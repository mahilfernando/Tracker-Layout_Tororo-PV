"""Overlay the 299-module PV layout (from PV_Layout_Enerack_10deg.dxf) on the satellite image.

Roof (mm, origin = inner NW corner of the upper PV block) is mapped to image pixels with a
homography fitted to four roof points read off the satellite image (crop of x380-580, y120-420, x4).
"""
import os
import numpy as np
import ezdxf
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
UP = 3                                            # output upscale

def crop2img(cx, cy):                             # crop coords (x4 of region 380,120) -> image px
    return (380 + cx / 4.0, 120 + cy / 4.0)

ROOF_W = 29264.0
src = [(0, 0), (ROOF_W, 0), (0, -52000), (ROOF_W, -52000)]
dst = [crop2img(183, 150), crop2img(677, 185), crop2img(117, 1000), crop2img(612, 1040)]

def homography(src, dst):
    A = []
    for (x, y), (u, v) in zip(src, dst):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y, -u], [0, 0, 0, x, y, 1, -v * x, -v * y, -v]]
    _, _, vt = np.linalg.svd(np.array(A))
    return vt[-1].reshape(3, 3) / vt[-1][-1]
Hm = homography(src, dst)
def tp(x, y):
    p = Hm @ np.array([x, y, 1.0]); return (p[0] / p[2] * UP, p[1] / p[2] * UP)

doc = ezdxf.readfile(os.path.join(HERE, "..", "PV_Layout_Enerack_10deg.dxf"))
mods = [e.dxf.insert for e in doc.modelspace().query("INSERT") if e.dxf.layer == "PV-MODULE"]
assert len(mods) == 299, len(mods)
W, Hh = 1134, 2382 * np.cos(np.radians(10))

base = Image.open(os.path.join(HERE, "satellite.png")).convert("RGB")
base = base.resize((base.width * UP, base.height * UP), Image.LANCZOS)
over = Image.new("RGBA", base.size, (0, 0, 0, 0))
d = ImageDraw.Draw(over)
for p in mods:
    x, y = p.x, p.y
    poly = [tp(x, y), tp(x + W, y), tp(x + W, y + Hh), tp(x, y + Hh)]
    d.polygon(poly, fill=(22, 42, 92, 235), outline=(150, 175, 215, 255))
    # cell line for a module look
    d.line([tp(x + W / 2, y), tp(x + W / 2, y + Hh)], fill=(60, 85, 140, 200), width=1)
out = Image.alpha_composite(base.convert("RGBA"), over).convert("RGB")

# label
dr = ImageDraw.Draw(out)
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 31)
    small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
except OSError:
    font = small = ImageFont.load_default()
lx, ly = tp(ROOF_W + 2500, -8000)
txt = ["PROPOSED ROOFTOP PV", "185.4 kWp · 299 × 620 Wp", "10° fixed tilt"]
bw = 520; bh = 130
lx = min(lx, out.width - bw - 25)
dr.rectangle([lx, ly, lx + bw, ly + bh], fill=(255, 255, 255), outline=(20, 54, 93), width=3)
dr.text((lx + 16, ly + 12), txt[0], font=font, fill=(20, 54, 93))
dr.text((lx + 16, ly + 56), txt[1], font=small, fill=(27, 36, 48))
dr.text((lx + 16, ly + 90), txt[2], font=small, fill=(27, 36, 48))
ax, ay = tp(ROOF_W - 2000, -9000)
dr.line([(lx, ly + bh / 2), (ax, ay)], fill=(20, 54, 93), width=3)

out.save(os.path.join(HERE, "Marriott_roof_PV_overlay.png"))
# zoomed view of the roof
x0, y0 = tp(-9000, 7000); x1, y1 = tp(ROOF_W + 33000, -60000); x1 = max(x1, lx + bw + 30)
out.crop((int(x0), int(y0), int(x1), int(y1))).save(os.path.join(HERE, "Marriott_roof_PV_overlay_zoom.png"))
print("ok", out.size)
