"""Render bar frames with Playwright.
usage:
  python3 render_bar.py test  <variant> <out.png> t1 t2 ...     -> stacked test strip
  python3 render_bar.py frames <variant> <outdir>                -> 900 frames for the 30s preview
  python3 render_bar.py still <variant> <out.png> <t>
"""
import sys, os, pathlib, tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
TOTAL = 311.77
FAST = 18.0
RATE = TOTAL / FAST
EXC_START = 86.0
FPS = 30


def mapping(f):
    t = f / FPS
    if t < FAST:
        return t * RATE, {"animScale": RATE, "teaser": False}
    return EXC_START + (t - FAST), {"animScale": 1, "teaser": True}


def page_for(p, variant):
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1920, "height": 64}, device_scale_factor=1)
    pg.goto(f"file://{HERE}/progress-bar.html?variant={variant}")
    pg.evaluate("window.barReady")
    return b, pg


def shot(pg, t, opts, path):
    pg.evaluate("([t,o])=>window.seek(t,o)", [t, opts])
    pg.locator("#bar").screenshot(path=path)


def main():
    mode, variant = sys.argv[1], sys.argv[2]
    with sync_playwright() as p:
        b, pg = page_for(p, variant)
        if mode == "frames":
            out = pathlib.Path(sys.argv[3]); out.mkdir(parents=True, exist_ok=True)
            for f in range(int(30 * FPS)):
                t, o = mapping(f)
                shot(pg, t, o, str(out / f"{f:05d}.png"))
        elif mode == "still":
            shot(pg, float(sys.argv[4]), {"animScale": 1, "teaser": True}, sys.argv[3])
        elif mode == "test":
            from PIL import Image
            ts = [float(x) for x in sys.argv[4:]]
            ims = []
            for i, t in enumerate(ts):
                pth = str(Path(tempfile.gettempdir()) / f"_bar_t{i}.png")
                shot(pg, t, {"animScale": 1, "teaser": True}, pth)
                ims.append(Image.open(pth).convert("RGB"))
                os.remove(pth)
            st = Image.new("RGB", (1920, 72 * len(ims)), (200, 60, 200))
            for i, im in enumerate(ims):
                st.paste(im, (0, 72 * i))
            st.save(sys.argv[3])
        b.close()


if __name__ == "__main__":
    main()
