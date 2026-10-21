"""sheet.py <out.png> <cols> <thumbW> files... (labels from filename: f_<ms>.png -> seconds, or pass --fps for frame index)"""
import sys, os, re
from PIL import Image, ImageDraw, ImageFont
out, cols, tw = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
fps = None; files = sys.argv[4:]
if files and files[0].startswith("--fps="): fps = float(files[0][6:]); files = files[1:]
th = int(tw * 9 / 16); rows = (len(files) + cols - 1) // cols
S = Image.new("RGB", (cols * tw, rows * th), "white"); d = ImageDraw.Draw(S)
try: F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", max(14, tw // 14))
except Exception: F = None
for k, f in enumerate(files):
    im = Image.open(f).convert("RGB").resize((tw, th), Image.LANCZOS)
    x, y = (k % cols) * tw, (k // cols) * th; S.paste(im, (x, y))
    n = int(re.findall(r"(\d+)", os.path.basename(f))[-1]); t = n / fps if fps else n / 1000
    lab = f"{t:.1f}s"; d.rectangle([x, y, x + len(lab) * tw // 22 + 8, y + tw // 12], fill="black"); d.text((x + 4, y + 2), lab, fill="yellow", font=F)
    d.rectangle([x, y, x + tw - 1, y + th - 1], outline="#999")
S.save(out); print(out, S.size)
