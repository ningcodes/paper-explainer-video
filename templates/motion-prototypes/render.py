"""Deterministic frame renderer: render.py <html> <outdir> [--fps 30] [--workers 4] [--times t1,t2,...] [--cues out.json]"""
import sys, os, json, argparse, multiprocessing as mp
from playwright.sync_api import sync_playwright

def work(args):
    html, outdir, frames, fps = args
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--disable-gpu", "--font-render-hinting=none"])
        pg = b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        pg.goto("file://" + os.path.abspath(html))
        pg.evaluate("window.READY")
        for i, t in frames:
            pg.evaluate(f"seek({t})")
            pg.screenshot(path=os.path.join(outdir, f"f_{i:05d}.png"), type="png")
        b.close()
    return len(frames)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("html"); ap.add_argument("outdir")
    ap.add_argument("--fps", type=float, default=30); ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--times", default=None); ap.add_argument("--cues", default=None)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1920, "height": 1080})
        pg.goto("file://" + os.path.abspath(a.html)); pg.evaluate("window.READY")
        dur = pg.evaluate("window.DURATION"); cues = pg.evaluate("window.CUES"); b.close()
    if a.cues: json.dump({"duration": dur, "cues": cues}, open(a.cues, "w"))
    if a.times:
        ts = [float(x) for x in a.times.split(",")]
        frames = [(int(round(t * 1000)), t) for t in ts]
    else:
        n = int(round(dur * a.fps)); frames = [(i, i / a.fps) for i in range(n)]
    chunks = [frames[k::a.workers] for k in range(a.workers)]
    with mp.Pool(a.workers) as pool:
        tot = sum(pool.map(work, [(a.html, a.outdir, c, a.fps) for c in chunks if c]))
    print("rendered", tot, "frames; duration", dur)
