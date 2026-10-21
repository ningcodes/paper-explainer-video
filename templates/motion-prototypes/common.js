// shared helpers for the deterministic prototype renderer
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, t) => a + (b - a) * t;
const eio = t => { t = clamp(t); return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
const eout = t => { t = clamp(t); return 1 - Math.pow(1 - t, 3); };
const back = (t, s = 1.3) => { t = clamp(t); const c3 = s + 1; return 1 + c3 * Math.pow(t - 1, 3) + s * Math.pow(t - 1, 2); };
const P = (t, a, d) => clamp((t - a) / d);
function mulberry32(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const $ = id => document.getElementById(id);

// camera: keys[0] = start state; later keys = moves {t,d,cx,cy,z,r,dip}
function camAt(keys, t) {
  let s = { cx: keys[0].cx, cy: keys[0].cy, z: keys[0].z, r: keys[0].r || 0 };
  for (let i = 1; i < keys.length; i++) {
    const k = keys[i];
    if (t <= k.t) break;
    const p = eio((t - k.t) / k.d);
    const tgt = { cx: k.cx, cy: k.cy, z: k.z, r: k.r || 0 };
    if (p < 1) {
      const dip = k.dip ? (1 - k.dip * Math.sin(Math.PI * p)) : 1;
      return { cx: lerp(s.cx, tgt.cx, p), cy: lerp(s.cy, tgt.cy, p), z: Math.exp(lerp(Math.log(s.z), Math.log(tgt.z), p)) * dip, r: lerp(s.r, tgt.r, p) };
    }
    s = tgt;
  }
  return s;
}
function camCSS(c) { return `translate(960px,540px) rotate(${c.r}deg) scale(${c.z}) translate(${-c.cx}px,${-c.cy}px)`; }
// screen position of world point under camera
function toScreen(c, x, y) {
  const a = c.r * Math.PI / 180, dx = (x - c.cx) * c.z, dy = (y - c.cy) * c.z;
  return [960 + dx * Math.cos(a) - dy * Math.sin(a), 540 + dx * Math.sin(a) + dy * Math.cos(a)];
}
// directional motion blur from camera velocity
function motionBlur(keys, t, el, blurEl) {
  const c0 = camAt(keys, t), c1 = camAt(keys, t - 1 / 30);
  // where does the world point now at screen centre sit one frame earlier
  const [x, y] = toScreen(c1, c0.cx, c0.cy);
  const dx = Math.abs(x - 960), dy = Math.abs(y - 540);
  const k = 0.11 / Math.max(1, c0.z), sx = Math.min(dx * k, 10), sy = Math.min(dy * k, 10);
  if (sx < 0.4 && sy < 0.4) { el.style.filter = 'none'; }
  else { blurEl.setAttribute('stdDeviation', `${sx.toFixed(2)} ${sy.toFixed(2)}`); el.style.filter = 'url(#mb)'; }
}
// captions [[t0,t1,text]]
function caption(caps, t, el, txt) {
  let cur = null;
  for (const c of caps) if (t >= c[0] - 0.05 && t < c[1] + 0.25) cur = c;
  if (!cur) { el.style.opacity = 0; return; }
  if (txt.textContent !== cur[2]) txt.textContent = cur[2];
  const a = Math.min(P(t, cur[0] - 0.05, 0.12), 1 - P(t, cur[1] + 0.13, 0.12));
  el.style.opacity = a;
}
// greeked paper text lines (decorative stand-in for unreadable body text)
function greek(container, rnd, x, y0, w, lines, pitch = 16.8, h = 7, col = '#d8d4cc', paraEvery = 0) {
  let y = y0, html = '';
  for (let i = 0; i < lines; i++) {
    const last = paraEvery && ((i + 1) % paraEvery === 0);
    const ww = last ? w * (0.35 + rnd() * 0.4) : w * (0.93 + rnd() * 0.07);
    html += `<div style="position:absolute;left:${x}px;top:${y}px;width:${ww}px;height:${h}px;background:${col};border-radius:2px"></div>`;
    y += pitch; if (last) y += pitch * 0.6;
  }
  container.insertAdjacentHTML('beforeend', html);
  return y;
}
const LOCK_SVG = (s = 44, c = '#8a857c') => `<svg width="${s}" height="${s}" viewBox="0 0 44 44"><path d="M13 20 v-6 a9 9 0 0 1 18 0 v6" fill="none" stroke="${c}" stroke-width="3.5" stroke-linecap="round"/><rect x="8" y="20" width="28" height="20" rx="4" fill="none" stroke="${c}" stroke-width="3.5"/><circle cx="22" cy="30" r="2.6" fill="${c}"/></svg>`;
const PAPER_TEX = `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' seed='7'/><feColorMatrix values='0 0 0 0 0.45  0 0 0 0 0.38  0 0 0 0 0.28  0 0 0 0.10 0'/></filter><rect width='300' height='300' filter='url(%23n)'/></svg>")`;
