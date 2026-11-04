"""Generate the rooftop PV layout (10 deg tilt) for drawing D18102-DD-A-104 (Mezzanine).

Geometry was measured from the PDF plot and calibrated on the 29,390 and 15,805
dimensions (~15.5 mm per 600-dpi pixel). Origin (0,0) = inner face of the
north-west corner of the upper PV roof block; +X = right, +Y = up (as plotted).
All units mm.
"""
import math
import ezdxf
from ezdxf.enums import TextEntityAlignment

# ---------------- design inputs ----------------
MOD_L, MOD_W = 2382, 1134          # 210R TOPCon bifacial, 615-620 W
MOD_P = 620                        # W
TILT = 10                          # deg
GAP = 20                           # clamp gap between modules
AISLE = 800                        # aisle between tables
SET_W, SET_E = 1000, 1742          # edge setbacks (east kept clear of roof opening)
SET_EDGE = 1000                    # north / south setback
N_COLS = 23

PX = 15.5                          # mm per pixel of the 600-dpi raster
X0, Y0 = 5796, 324                 # origin pixel (inner wall faces)
def P(px, py):                     # raster pixel -> drawing mm
    return ((px - X0) * PX, -(py - Y0) * PX)

ROOF_W = (7684 - X0) * PX                          # 29,264 inner
UPPER_TOP, UPPER_BOT = 0.0, P(0, 1338)[1]          # upper block, +6.80 SSL
LOWER_TOP = P(0, 1350)[1]                          # lower block below joint
LOWER_LIMIT = P(0, 2818)[1]                        # architect's PV zone limit
OPT_LIMIT = P(0, 3416)[1]                          # grid/dimension line, clear of lift core

D2 = (2 * MOD_L + GAP) * math.cos(math.radians(TILT))   # 2P table depth on plan
D1 = MOD_L * math.cos(math.radians(TILT))               # 1P table depth on plan
ROW_LEN = N_COLS * MOD_W + (N_COLS - 1) * GAP

doc = ezdxf.new("R2010", setup=True)
doc.units = ezdxf.units.MM
msp = doc.modelspace()
for name, col in [("PV-ROOF-REF", 8), ("PV-SETBACK", 1), ("PV-MODULE", 5),
                  ("PV-TABLE", 3), ("PV-MODULE-OPTIONAL", 30), ("PV-TABLE-OPTIONAL", 30),
                  ("PV-OBSTRUCTION", 6), ("PV-TEXT", 7), ("PV-DIM", 2)]:
    doc.layers.add(name, color=col)
doc.layers.get("PV-SETBACK").dxf.linetype = "DASHED"

def rect(x1, y1, x2, y2, layer, **kw):
    msp.add_lwpolyline([(x1, y1), (x2, y1), (x2, y2), (x1, y2)], close=True,
                       dxfattribs={"layer": layer, **kw})

# module block (plan projection at 10 deg)
blk = doc.blocks.new("PV_MOD_620W")
blk.add_lwpolyline([(0, 0), (MOD_W, 0), (MOD_W, MOD_L * math.cos(math.radians(TILT))),
                    (0, MOD_L * math.cos(math.radians(TILT)))], close=True)
blk.add_line((0, 0), (MOD_W, MOD_L * math.cos(math.radians(TILT))))

counts = {}
def table(y_top, rows, optional=False):
    """Draw a table of `rows` portrait modules high, top edge at y_top. Returns bottom y."""
    lay_m = "PV-MODULE-OPTIONAL" if optional else "PV-MODULE"
    lay_t = "PV-TABLE-OPTIONAL" if optional else "PV-TABLE"
    depth = D2 if rows == 2 else D1
    x = SET_W
    rect(x, y_top, x + ROW_LEN, y_top - depth, lay_t)
    hm = MOD_L * math.cos(math.radians(TILT))
    gp = GAP * math.cos(math.radians(TILT))
    for r in range(rows):
        yb = y_top - (r + 1) * hm - r * gp
        for c in range(N_COLS):
            msp.add_blockref("PV_MOD_620W", (x + c * (MOD_W + GAP), yb), dxfattribs={"layer": lay_m})
    counts[lay_m] = counts.get(lay_m, 0) + rows * N_COLS
    return y_top - depth

# ---- roof reference outline (inner faces) ----
rect(0, UPPER_TOP, ROOF_W, UPPER_BOT, "PV-ROOF-REF")
rect(0, LOWER_TOP, ROOF_W, LOWER_LIMIT, "PV-ROOF-REF")
msp.add_line((0, LOWER_LIMIT), (ROOF_W, LOWER_LIMIT), dxfattribs={"layer": "PV-ROOF-REF", "linetype": "DASHDOT"})
# obstructions
ox1, oy1 = P(7614, 801); ox2, oy2 = P(7676, 1273)
rect(ox1, oy1, ox2, oy2, "PV-OBSTRUCTION")                    # X-box opening, upper block
lx1, ly1 = P(6100, 3520); lx2, ly2 = P(6474, 3710)
rect(lx1, ly1, lx2, ly2, "PV-OBSTRUCTION")                    # new lift core
# setback lines
rect(SET_W, UPPER_TOP - SET_EDGE, ROOF_W - SET_E, UPPER_BOT + SET_EDGE, "PV-SETBACK")
rect(SET_W, LOWER_TOP - SET_EDGE, ROOF_W - SET_E, LOWER_LIMIT, "PV-SETBACK")

# ---- upper block: 2P, 2P, 1P ----
y = UPPER_TOP - SET_EDGE
y = table(y, 2); y = table(y - AISLE, 2); y = table(y - AISLE, 1)
assert y >= UPPER_BOT + SET_EDGE - 1, ("upper overflow", y, UPPER_BOT + SET_EDGE)
# ---- lower block: 4 x 2P inside architect's PV zone ----
y = LOWER_TOP - SET_EDGE
for i in range(4):
    y = table(y if i == 0 else y - AISLE, 2)
assert y >= LOWER_LIMIT - 1, ("lower overflow", y, LOWER_LIMIT)

base = counts["PV-MODULE"]; opt = counts.get("PV-MODULE-OPTIONAL", 0)
kwp = lambda n: n * MOD_P / 1000

# dimensions
dim = dict(dimstyle="EZDXF", dxfattribs={"layer": "PV-DIM"})
msp.add_linear_dim(base=(0, 2500), p1=(0, 0), p2=(ROOF_W, 0), **dim).render()
msp.add_linear_dim(base=(SET_W, 1200), p1=(SET_W, 0), p2=(SET_W + ROW_LEN, 0), **dim).render()
msp.add_linear_dim(base=(-2500, 0), p1=(0, UPPER_TOP), p2=(0, UPPER_BOT), angle=90, **dim).render()
yt = UPPER_TOP - SET_EDGE
msp.add_linear_dim(base=(-1200, 0), p1=(SET_W, yt), p2=(SET_W, yt - D2), angle=90, **dim).render()
msp.add_linear_dim(base=(-1200, 0), p1=(SET_W, yt - D2), p2=(SET_W, yt - D2 - AISLE), angle=90, **dim).render()

notes = [
    "ROOFTOP PV LAYOUT - D18102-DD-A-104 MEZZANINE",
    f"MODULE: 2382 x 1134 x 30 mm, {MOD_P} Wp bifacial TOPCon, portrait, 2 high (2P)",
    f"TILT {TILT} deg, plan depth 2P table = {D2:.0f} mm, 1P table = {D1:.0f} mm",
    f"CLAMP GAP {GAP} mm, AISLE {AISLE} mm, EDGE SETBACK {SET_EDGE} mm (east {SET_E} mm for roof opening)",
    f"{N_COLS} modules per row, row length {ROW_LEN:.0f} mm",
    f"BASE (architect PV zone incl. hatched +4.85 strip): {base} modules = {kwp(base):.1f} kWp",
    "Origin 0,0 = inner face NW corner of upper PV roof. Geometry traced from PDF plot; verify vs DWG.",
]
for i, t in enumerate(notes):
    msp.add_text(t, height=350 if i else 500, dxfattribs={"layer": "PV-TEXT"}).set_placement(
        (ROOF_W + 2500, -1000 - i * 800), align=TextEntityAlignment.LEFT)
msp.add_text("REF 0,0", height=300, dxfattribs={"layer": "PV-TEXT"}).set_placement((150, -450))
msp.add_circle((0, 0), 250, dxfattribs={"layer": "PV-TEXT"})

doc.saveas(__file__.replace("make_pv_layout.py", "PV_Layout_10deg_Mezzanine_Roof.dxf"))
print(f"D2={D2:.0f} D1={D1:.0f} row={ROW_LEN:.0f} roofW={ROOF_W:.0f} upper={-UPPER_BOT:.0f} lowerZone={LOWER_TOP-LOWER_LIMIT:.0f} opt={LOWER_LIMIT-OPT_LIMIT:.0f}")
print(f"base {base} mods {kwp(base):.1f} kWp, optional {opt} mods {kwp(opt):.1f} kWp, total {base+opt} = {kwp(base+opt):.1f} kWp")
