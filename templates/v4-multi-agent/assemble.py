"""assemble.py [parts...]  — render parts in order (prev.png chaining), concat, global audio mix, mux.
   python3 assemble.py render ch01 ch02 ...   # render the listed parts (frames → v.mp4, cues.json, last.png)
   python3 assemble.py mix                    # concat all parts + global audio → out/harness2_v4.mp4
"""
import sys, os, json, subprocess, shutil
# R = project work dir: R/kit (shared files), R/<part>/scene.html, R/out (outputs). Override with env WORK.
R = os.environ.get('WORK', os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))); K = R + '/kit'
TL = json.load(open(K + '/timeline.json'))
CH = {c['id']: c for c in TL['chapters']}
PARTS = [('ch01', '01', 0, None), ('ch02', '02', 0, None), ('ch03', '03', 0, None), ('ch04a', '04', 0, 78.5),
         ('ch04b', '04', 78.5, None), ('ch05', '05', 0, None), ('ch06', '06', 0, None), ('ch07', '07', 0, None), ('ch08', '08', 0, None)]
def info(p):
    for name, cid, off, ln in PARTS:
        if name == p:
            c = CH[cid]; L = ln if ln is not None else c['duration'] - off
            return dict(start=c['start'] + off, dur=L, frames=int(round(L * 30)))
def sh(*a, **k): print('+', ' '.join(a)); subprocess.run(a, check=True, **k)

def render(p):
    D = f'{R}/{p}'; i = [x[0] for x in PARTS].index(p)
    if i > 0 and PARTS[i][2] == 0:   # chapter start → page flip uses previous part's last frame
        prev = f'{R}/{PARTS[i-1][0]}/last.png'
        if os.path.exists(prev): shutil.copy(prev, f'{D}/prev.png')
        else: print('WARN no prev for', p)
    shutil.rmtree(f'{D}/fr', ignore_errors=True)
    sh('python3', K + '/render.py', 'scene.html', 'fr', '--workers', os.environ.get('W', '2'), '--cues', 'cues.json', cwd=D)
    n = len(os.listdir(f'{D}/fr')); exp = info(p)['frames']
    print(p, 'frames', n, 'expected', exp)
    sh('ffmpeg', '-y', '-loglevel', 'error', '-framerate', '30', '-i', 'fr/f_%05d.png', '-frames:v', str(exp), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', 'v.mp4', cwd=D)
    lt = round(info(p)['dur'] - 1 / 30, 4)
    shutil.rmtree(f'{D}/lastfr', ignore_errors=True)
    sh('python3', K + '/render.py', 'scene.html?nochrome=1', 'lastfr', '--workers', '1', '--times', str(lt), cwd=D)
    f = os.listdir(f'{D}/lastfr')[0]; shutil.move(f'{D}/lastfr/{f}', f'{D}/last.png'); shutil.rmtree(f'{D}/lastfr')
    # contact sheet every 1s
    os.makedirs(f'{D}/sh', exist_ok=True)
    for f in os.listdir(f'{D}/sh'): os.remove(f'{D}/sh/{f}')
    for k in range(0, n, 30): shutil.copy(f'{D}/fr/f_{k:05d}.png', f'{D}/sh/f_{k:05d}.png')
    fs = sorted(os.listdir(f'{D}/sh'))
    sh('python3', K + '/sheet.py', 'full_sheet.png', '8', '240', '--fps=30', *[f'sh/{x}' for x in fs], cwd=D)
    shutil.rmtree(f'{D}/fr', ignore_errors=True)

def mix():
    O = R + '/out'; os.makedirs(O, exist_ok=True)
    with open(O + '/list.txt', 'w') as f:
        for p, *_ in PARTS: f.write(f"file '{R}/{p}/v.mp4'\n")
    sh('ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', O + '/list.txt', '-c', 'copy', O + '/video.mp4')
    cues = []
    for p, *_ in PARTS:
        c = json.load(open(f'{R}/{p}/cues.json'))['cues']; s = info(p)['start']
        for q in c: q = dict(q); q['t'] = round(q['t'] + s, 4); cues.append(q)
    json.dump({'duration': TL['total'], 'cues': cues}, open(O + '/cues.json', 'w'))
    sh('python3', K + '/audio.py', O + '/cues.json', R + '/voice/voice_full.wav', '0', str(TL['total']), O + '/mix.wav', '1')
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', O + '/mix.wav', '-af', 'loudnorm=I=-16:TP=-1.8:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
    j = json.loads(r[r.rindex('{'):r.rindex('}') + 1])
    af = f"loudnorm=I=-16:TP=-1.8:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,aresample=48000"
    sh('ffmpeg', '-y', '-loglevel', 'error', '-i', O + '/mix.wav', '-af', af, '-ar', '48000', O + '/norm.wav')
    sh('ffmpeg', '-y', '-loglevel', 'error', '-i', O + '/video.mp4', '-i', O + '/norm.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', O + '/harness2_v4.mp4')
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', O + '/harness2_v4.mp4', '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    print('\n'.join(l for l in r.splitlines()[-14:]))

if __name__ == '__main__':
    if sys.argv[1] == 'render':
        for p in sys.argv[2:]: render(p)
    elif sys.argv[1] == 'mix': mix()

def patch(p, n0, n1):
    """re-render frames [n0,n1) of part p and splice into v.mp4"""
    D = f'{R}/{p}'; T = f'{D}/patch'; shutil.rmtree(T, ignore_errors=True)
    ts = ','.join(str(round(k / 30, 5)) for k in range(n0, n1))
    sh('python3', K + '/render.py', 'scene.html', T, '--workers', '2', '--times', ts, cwd=D)
    fs = sorted(os.listdir(T), key=lambda f: int(f[2:-4]))
    for k, f in enumerate(fs): os.rename(f'{T}/{f}', f'{T}/p_{k:05d}.png')
    sh('ffmpeg', '-y', '-loglevel', 'error', '-i', 'v.mp4', '-framerate', '30', '-i', 'patch/p_%05d.png', '-filter_complex',
       f"[0:v]trim=end_frame={n0},setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS,format=yuv420p[b];[0:v]trim=start_frame={n1},setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1[o]",
       '-map', '[o]', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', 'v2.mp4', cwd=D)
    n = int(subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v', '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', f'{D}/v2.mp4'], capture_output=True, text=True).stdout)
    print('patched', p, 'frames', n, 'expected', info(p)['frames'])
    if n == info(p)['frames']: os.replace(f'{D}/v2.mp4', f'{D}/v.mp4')
    shutil.rmtree(T, ignore_errors=True)

if __name__ == '__main__' and sys.argv[1] == 'patch':
    patch(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
