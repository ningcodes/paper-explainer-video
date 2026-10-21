"""audio.py <cues.json> <src.mp4> <start> <end> <out.wav> [seed]
Builds voice (cut from original) + synthesized music bed (ducked) + synthesized SFX, pre-loudnorm mix."""
import sys, json, subprocess, wave, re, os
import numpy as np
SR = 48000
cues_f, src, t0, t1, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
seed = int(sys.argv[6]) if len(sys.argv) > 6 else 1
rng = np.random.default_rng(seed)
C = json.load(open(cues_f)); DUR = C["duration"]; N = int(DUR * SR)
tmp = out + ".d"; os.makedirs(tmp, exist_ok=True)

def readwav(p):
    w = wave.open(p); x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return x.reshape(-1, w.getnchannels())
def writewav(p, x):
    x = np.clip(x, -1, 1); w = wave.open(p, "wb"); w.setnchannels(x.shape[1]); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close()
def lufs(p):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", p, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1])

# ---------- voice
vp = f"{tmp}/voice_raw.wav"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t0), "-to", str(t1), "-i", src, "-vn", "-ac", "2", "-ar", str(SR), vp], check=True)
v = readwav(vp); fade = int(0.012 * SR); v[:fade] *= np.linspace(0, 1, fade)[:, None]; v[-fade:] *= np.linspace(1, 0, fade)[:, None]
voice = np.zeros((N, 2), np.float32); voice[:min(N, len(v))] = v[:N]

# ---------- filters
def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); s = 0.0
    for i in range(len(x)): s = (1 - a) * x[i] + a * s; y[i] = s
    return y
def svf_bp(x, fc_arr, q=1.2):
    y = np.empty_like(x); lp = bp = 0.0
    f_arr = 2 * np.sin(np.pi * np.clip(fc_arr, 20, SR / 6) / SR)
    for i in range(len(x)):
        f = f_arr[i]; hp = x[i] - lp - bp / q; bp += f * hp; lp += f * bp; y[i] = bp
    return y

# ---------- SFX
def whoosh(d, soft=False):
    n = int(d * SR); t = np.linspace(0, 1, n)
    env = np.sin(np.pi * t ** 0.75) ** 2
    fc = (350 if soft else 450) + (1400 if soft else 2600) * np.sin(np.pi * t ** 0.8) ** 1.5
    x = svf_bp(rng.standard_normal(n).astype(np.float32), fc, 1.6) * env
    x2 = svf_bp(rng.standard_normal(n).astype(np.float32), fc * 1.03, 1.6) * env
    pan = np.linspace(-0.6, 0.6, n)
    return np.stack([x * (1 - pan) / 2 + x2 * .2, x2 * (1 + pan) / 2 + x * .2], 1)
def pop():
    n = int(0.12 * SR); t = np.arange(n) / SR
    f = 380 * (1 + 1.2 * np.exp(-t / 0.012)); ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t / 0.035) + 0.35 * np.sin(2 * ph) * np.exp(-t / 0.02)
    x[:int(.003 * SR)] *= np.linspace(0, 1, int(.003 * SR))
    return np.stack([x, x], 1)
def tick(key=False):
    n = int(0.05 * SR); t = np.arange(n) / SR
    if key:
        x = svf_bp(rng.standard_normal(n).astype(np.float32), np.full(n, 1800.0), 2.0) * np.exp(-t / 0.008)
    else:
        x = np.sin(2 * np.pi * 2600 * t) * np.exp(-t / 0.006) + 0.3 * rng.standard_normal(n) * np.exp(-t / 0.002)
    return np.stack([x, x], 1)
def scratch(d):
    n = int(d * SR); t = np.arange(n) / SR
    strokes = 0.55 + 0.45 * np.sin(2 * np.pi * 9 * t + 2 * np.sin(2 * np.pi * 2.3 * t))
    grain = onepole_lp(np.abs(rng.standard_normal(n)).astype(np.float32), 60) * 2
    env = np.minimum(1, t / 0.03) * np.minimum(1, (d - t) / 0.08)
    x = svf_bp(rng.standard_normal(n).astype(np.float32), 3600 + 900 * np.sin(2 * np.pi * 4.5 * t), 2.2) * strokes * grain * env
    return np.stack([x * .9, x], 1)
def paper():
    n = int(0.4 * SR); t = np.arange(n) / SR
    crack = (rng.random(n) < 0.004).astype(np.float32) * rng.standard_normal(n)
    crack = onepole_lp(crack.astype(np.float32), 5000) * 6
    hiss = svf_bp(rng.standard_normal(n).astype(np.float32), np.full(n, 2400.0), 0.9)
    env = np.sin(np.pi * np.clip(t / 0.4, 0, 1)) ** 0.7
    x = (hiss * 0.6 + crack) * env
    return np.stack([x, x * .95], 1)

sfx = np.zeros((N, 2), np.float32)
GAIN = {"whoosh": 1.0, "pop": 0.55, "tick": 0.35, "scratch": 0.8, "paper": 0.7}
for c in C["cues"]:
    ty = c["type"]
    if ty == "whoosh": s = whoosh(c.get("d", .7), c.get("soft"))
    elif ty == "pop": s = pop()
    elif ty == "tick": s = tick(c.get("key"))
    elif ty == "scratch": s = scratch(c.get("d", .6))
    elif ty == "paper": s = paper()
    else: continue
    s = s / (np.max(np.abs(s)) + 1e-9) * GAIN[ty] * (0.6 if c.get("soft") else 1.0)
    i = int(c["t"] * SR); j = min(N, i + len(s)); sfx[i:j] += s[:j - i]

# ---------- music bed: warm pad + soft arpeggio + bass in F major, 84 bpm
bpm = 84; beat = 60 / bpm; bar = 4 * beat
def m2f(m): return 440 * 2 ** ((m - 69) / 12)
CH = [[53, 57, 60, 64], [50, 53, 57, 60], [46, 50, 53, 57], [48, 52, 55, 58]]  # Fmaj7 Dm7 Bbmaj7 C7
t = np.arange(N) / SR
pad = np.zeros(N, np.float32); arp = np.zeros(N, np.float32); bass = np.zeros(N, np.float32)
clen = 2 * bar; nch = int(DUR / clen) + 2
for k in range(nch):
    notes = CH[k % 4]; a, b = k * clen, (k + 1) * clen
    i0, i1 = int(max(0, a - 0.6) * SR), min(N, int((b + 1.2) * SR))
    if i0 >= N: break
    tt = t[i0:i1] - a
    env = np.clip((tt + 0.6) / 1.4, 0, 1) * np.clip((clen + 1.2 - tt) / 1.6, 0, 1)
    for m in notes:
        for det in (-0.0018, 0.0016):
            f = m2f(m) * (1 + det)
            pad[i0:i1] += env * sum(np.sin(2 * np.pi * f * h * tt + h) / h ** 1.6 for h in range(1, 5)) * 0.08
    fb = m2f(notes[0] - 12)
    bass[i0:i1] += env * np.sin(2 * np.pi * fb * tt) * 0.16
    # arpeggio, 8th notes, up an octave
    seq = [notes[0] + 12, notes[1] + 12, notes[2] + 12, notes[3] + 12, notes[2] + 12, notes[1] + 12, notes[2] + 12, notes[3] + 12]
    for q in range(int(clen / (beat / 2))):
        st = a + q * beat / 2
        j0 = int(st * SR)
        if j0 >= N: break
        n = min(int(0.9 * SR), N - j0); u = np.arange(n) / SR
        f = m2f(seq[q % 8]); vel = 0.75 + 0.25 * ((q % 4) == 0)
        arp[j0:j0 + n] += vel * (np.sin(2 * np.pi * f * u) + 0.25 * np.sin(4 * np.pi * f * u)) * np.exp(-u / 0.28) * np.minimum(1, u / 0.004) * 0.07
pad = onepole_lp(pad, 1600); arp = onepole_lp(arp, 3200)
# stereo with a simple dotted-8th echo on the arp
d = int(0.75 * beat * SR); arpL = arp.copy(); arpR = arp.copy()
arpR[d:] += 0.35 * arp[:-d]; arpL[2 * d:] += 0.2 * arp[:-2 * d]
music = np.stack([pad * 1.0 + arpL + bass, pad * 0.95 + arpR + bass], 1)
fi, fo = int(0.4 * SR), int(0.8 * SR)
music[:fi] *= np.linspace(0, 1, fi)[:, None]; music[-fo:] *= np.linspace(1, 0, fo)[:, None]

# ---------- ducking from voice envelope
vm = np.abs(voice).mean(1); hop = 480
rms = np.sqrt(np.convolve(vm ** 2, np.ones(hop) / hop, "same"))
act = (rms > 0.02).astype(np.float32)
g = np.empty(N, np.float32); s = 0.0
att, rel = np.exp(-1 / (0.06 * SR)), np.exp(-1 / (0.45 * SR))
for i in range(0, N, hop):  # block-rate smoothing
    a_ = act[i]; coef = att ** hop if a_ > s else rel ** hop
    s = a_ + (s - a_) * coef; g[i:i + hop] = s
duck = 10 ** (-7 * g / 20)
music *= duck[:, None]

# ---------- levels
writewav(f"{tmp}/voice.wav", voice); writewav(f"{tmp}/music.wav", music); writewav(f"{tmp}/sfx.wav", sfx)
Lv, Lm, Ls = lufs(f"{tmp}/voice.wav"), lufs(f"{tmp}/music.wav"), lufs(f"{tmp}/sfx.wav")
# targets relative to a -16 LUFS voice: music bed ~-28 LUFS (after ducking), SFX ~ -24 dB under voice
gv = 10 ** ((-16 - Lv) / 20); gm = 10 ** ((-28 - Lm) / 20); gs = 10 ** ((-16 - 24 - Ls) / 20)
mix = voice * gv + music * gm + sfx * gs
pk = np.max(np.abs(mix));
if pk > 0.98: mix *= 0.98 / pk
writewav(out, mix)
print(json.dumps({"voice_lufs": Lv, "music_lufs": Lm, "sfx_lufs": Ls, "gains_db": [20 * np.log10(gv), 20 * np.log10(gm), 20 * np.log10(gs)], "peak": float(pk)}))
