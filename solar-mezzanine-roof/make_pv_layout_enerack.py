"""Rooftop PV layout redrawn with the Enerack ballast structure (drawing EPJ-26110401 V1.0).

Outputs (next to this file):
  PV_Layout_Enerack_10deg.dxf   - CAD layout: modules, rails, frames, feet, setbacks, dims
  PV_Layout_Enerack_10deg.svg   - same layout as a drawing sheet (used for the PDF)

Origin (0,0) = inner face of the NW corner of the upper PV roof block; +X right, +Y up.
Roof geometry as in make_pv_layout.py (traced from D18102-DD-A-104). Units mm.
"""
import math, os
import ezdxf
from ezdxf.enums import TextEntityAlignment

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------- module & Enerack structure ----------------
MOD_L, MOD_W, MOD_P = 2382, 1134, 620
TILT = 10
GAP = 20
N_COLS = 23
RAIL_LEN = 8 * 3000 + 2630                    # 26,630
RAIL_OH_START = 50                            # rail start -> first module edge
FRAME_FIRST, FRAME_PITCH, N_FRAMES = 315, 2600, 11
c = math.cos(math.radians(TILT))

TYPES = {
    # slope offsets measured from the module LOW edge
    "2P": dict(rows=2, front_off=300, foot_span=3402, rails=[491, 1891, 2402 + 491, 2402 + 1891],
               front_h=595, frame="ERK-W45-3800"),
    "1P": dict(rows=1, front_off=200, foot_span=1136, rails=[491, 1891],
               front_h=200, frame="ERK-W45-1400"),
}
for t in TYPES.values():
    sl = t["rows"] * MOD_L + (t["rows"] - 1) * GAP
    t["slope"] = sl
    t["depth"] = sl * c
    t["rear_h"] = t["front_h"] + sl * math.sin(math.radians(TILT))

AISLE = 800
SET_W, SET_E, SET_EDGE = 1000, 1742, 1000      # setbacks to the MODULE edge
ROW_LEN = N_COLS * MOD_W + (N_COLS - 1) * GAP  # 26,522

# ---------------- roof (from make_pv_layout.py) ----------------
PX = 15.5; X0, Y0 = 5796, 324
def P(px, py): return ((px - X0) * PX, -(py - Y0) * PX)
ROOF_W = (7684 - X0) * PX
UPPER_BOT = P(0, 1338)[1]
LOWER_TOP = P(0, 1350)[1]
LOWER_LIMIT = P(0, 2818)[1]
OPT_LIMIT = P(0, 3416)[1]
OBS = [(P(7614, 801), P(7676, 1273), "OPENING"), (P(6100, 3520), P(6474, 3710), "LIFT CORE")]

# ---------------- build table list ----------------
tables = []   # (name, type, y_top, optional)
def stack(y, seq, optional=False, start=1):
    for i, ty in enumerate(seq):
        if i: y -= AISLE
        tables.append((ty, y, optional))
        y -= TYPES[ty]["depth"]
    return y
y = stack(-SET_EDGE, ["2P", "2P", "1P"])
assert y >= UPPER_BOT + SET_EDGE - 1
y = stack(LOWER_TOP - SET_EDGE, ["2P"] * 4)
assert y >= LOWER_LIMIT - 1

# ---------------- DXF ----------------
doc = ezdxf.new("R2010", setup=True); doc.units = ezdxf.units.MM
msp = doc.modelspace()
LAY = {"PV-ROOF-REF": 8, "PV-SETBACK": 1, "PV-MODULE": 5, "PV-RAIL": 4, "PV-FRAME": 3, "PV-FOOT": 6,
"PV-OBSTRUCTION": 6, "PV-TEXT": 7, "PV-DIM": 2}
for n, col in LAY.items(): doc.layers.add(n, color=col)
doc.layers.get("PV-SETBACK").dxf.linetype = "DASHED"
hm = MOD_L * c
blk = doc.blocks.new("PV_MOD_620W")
blk.add_lwpolyline([(0, 0), (MOD_W, 0), (MOD_W, hm), (0, hm)], close=True)
blk.add_line((0, 0), (MOD_W, hm))

svg_items = []   # (kind, layer, data)
def rect(x1, y1, x2, y2, layer, svg_cls=None):
    msp.add_lwpolyline([(x1, y1), (x2, y1), (x2, y2), (x1, y2)], close=True, dxfattribs={"layer": layer})
    if svg_cls: svg_items.append(("rect", svg_cls, (x1, y1, x2, y2)))
def line(x1, y1, x2, y2, layer, svg_cls=None):
    msp.add_line((x1, y1), (x2, y2), dxfattribs={"layer": layer})
    if svg_cls: svg_items.append(("line", svg_cls, (x1, y1, x2, y2)))

counts = {"2P": [0, 0], "1P": [0, 0]}   # [base, optional]
xr = SET_W - RAIL_OH_START              # rail start x
for idx, (ty, yt, opt) in enumerate(tables, 1):
    t = TYPES[ty]; counts[ty][1 if opt else 0] += 1
    lm = "PV-OPTIONAL" if opt else "PV-MODULE"
    lr = "PV-OPTIONAL" if opt else "PV-RAIL"
    lf = "PV-OPTIONAL" if opt else "PV-FRAME"
    lo = "PV-OPTIONAL" if opt else "PV-FOOT"
    sfx = "-opt" if opt else ""
    # y of a point at slope distance s from the LOW (front) edge; front edge = table bottom (south)
    ybot = yt - t["depth"]
    ys = lambda s: ybot + s * c
    for r in range(t["rows"]):
        yb = ys(r * (MOD_L + GAP))
        for col in range(N_COLS):
            x = SET_W + col * (MOD_W + GAP)
            msp.add_blockref("PV_MOD_620W", (x, yb), dxfattribs={"layer": lm})
            svg_items.append(("rect", "mod" + sfx, (x, yb, x + MOD_W, yb + hm)))
    for s in t["rails"]:
        line(xr, ys(s), xr + RAIL_LEN, ys(s), lr, "rail" + sfx)
    yf1 = ys(t["front_off"]); yf2 = yf1 + t["foot_span"]
    for k in range(N_FRAMES):
        xf = xr + FRAME_FIRST + k * FRAME_PITCH
        line(xf, yf1, xf, yf2, lf, "frame" + sfx)
        for yy in (yf1, yf2):
            rect(xf - 150, yy - 150, xf + 150, yy + 150, lo, "foot" + sfx)
    label = f"T{idx} {ty}x23"
    msp.add_text(label, height=300, dxfattribs={"layer": "PV-TEXT"}).set_placement(
        (xr + RAIL_LEN + 200, yt - t["depth"] / 2), align=TextEntityAlignment.MIDDLE_LEFT)
    svg_items.append(("text", "tlab", (ROOF_W + 500, yt - t["depth"] / 2, label + (" (optional)" if opt else ""))))

# roof, setbacks, obstructions
rect(0, 0, ROOF_W, UPPER_BOT, "PV-ROOF-REF", "roof")
rect(0, LOWER_TOP, ROOF_W, LOWER_LIMIT - SET_EDGE, "PV-ROOF-REF", "roof")
rect(SET_W, -SET_EDGE, ROOF_W - SET_E, UPPER_BOT + SET_EDGE, "PV-SETBACK", "set")
rect(SET_W, LOWER_TOP - SET_EDGE, ROOF_W - SET_E, LOWER_LIMIT, "PV-SETBACK", "set")
for (a, b, name) in OBS:
    rect(a[0], a[1], b[0], b[1], "PV-OBSTRUCTION", "obs")
    line(a[0], a[1], b[0], b[1], "PV-OBSTRUCTION", "obs")
    line(a[0], b[1], b[0], a[1], "PV-OBSTRUCTION", "obs")

dim = dict(dimstyle="EZDXF", dxfattribs={"layer": "PV-DIM"})
msp.add_linear_dim(base=(0, 2500), p1=(0, 0), p2=(ROOF_W, 0), **dim).render()
msp.add_linear_dim(base=(0, 1300), p1=(xr, 0), p2=(xr + RAIL_LEN, 0), **dim).render()
msp.add_linear_dim(base=(-2500, 0), p1=(0, 0), p2=(0, UPPER_BOT), angle=90, **dim).render()
t0 = TYPES["2P"]
msp.add_linear_dim(base=(-1200, 0), p1=(SET_W, -SET_EDGE), p2=(SET_W, -SET_EDGE - t0["depth"]), angle=90, **dim).render()
msp.add_linear_dim(base=(-1200, 0), p1=(SET_W, -SET_EDGE - t0["depth"]), p2=(SET_W, -SET_EDGE - t0["depth"] - AISLE), angle=90, **dim).render()

nb = counts["2P"][0] * 46 + counts["1P"][0] * 23
no = counts["2P"][1] * 46 + counts["1P"][1] * 23
kw = lambda n: n * MOD_P / 1000
frames = {ty: [v * N_FRAMES for v in counts[ty]] for ty in counts}
rails_lines = [counts["2P"][i] * 4 + counts["1P"][i] * 2 for i in (0, 1)]
notes = [
    "ROOFTOP PV LAYOUT - ENERACK BALLAST STRUCTURE (EPJ-26110401 V1.0)",
    f"MODULE {MOD_L}x{MOD_W}x30 mm, {MOD_P} Wp, portrait, TILT {TILT} deg, wind 35 m/s",
    f"2P TABLE: 2x23 modules, rails 4 x {RAIL_LEN} mm, 11 frames @2600, feet span 3402, front post 595",
    f"1P TABLE: 1x23 modules, rails 2 x {RAIL_LEN} mm, 11 frames @2600, feet span 1136, front post 200",
    f"BASE: {counts['2P'][0]} x 2P + {counts['1P'][0]} x 1P = {nb} modules = {kw(nb):.1f} kWp",
    "All tables within the architect's solar zone on D18102-DD-A-104.",
    "Foot blocks drawn 300x300 indicative - size/weight by Enerack. Origin 0,0 = inner NW corner of upper roof.",
]
for i, tx in enumerate(notes):
    msp.add_text(tx, height=450 if i == 0 else 330, dxfattribs={"layer": "PV-TEXT"}).set_placement(
        (ROOF_W + 6500, -1000 - i * 750), align=TextEntityAlignment.LEFT)
doc.saveas(os.path.join(HERE, "PV_Layout_Enerack_10deg.dxf"))

# ---------------- SVG drawing sheet (plan) ----------------
S = 0.0105                                     # px per mm
minx, maxx = -3200, ROOF_W + 9800
miny, maxy = LOWER_LIMIT - 2500, 3800
W, H = (maxx - minx) * S, (maxy - miny) * S
tx = lambda x: (x - minx) * S
ty_ = lambda y: (maxy - y) * S
out = []
for kind, cls, d in svg_items:
    if kind == "rect":
        x1, y1, x2, y2 = d
        out.append(f'<rect class="{cls}" x="{tx(min(x1,x2)):.2f}" y="{ty_(max(y1,y2)):.2f}" width="{abs(x2-x1)*S:.2f}" height="{abs(y2-y1)*S:.2f}"/>')
    elif kind == "line":
        x1, y1, x2, y2 = d
        out.append(f'<line class="{cls}" x1="{tx(x1):.2f}" y1="{ty_(y1):.2f}" x2="{tx(x2):.2f}" y2="{ty_(y2):.2f}"/>')
    else:
        x, y, s = d
        out.append(f'<text class="{cls}" x="{tx(x):.2f}" y="{ty_(y)+3:.2f}">{s}</text>')
def sdim_h(x1, x2, y, txt):
    return (f'<line class="dim" x1="{tx(x1):.1f}" y1="{ty_(y):.1f}" x2="{tx(x2):.1f}" y2="{ty_(y):.1f}"/>'
            f'<line class="dim" x1="{tx(x1):.1f}" y1="{ty_(y)-4:.1f}" x2="{tx(x1):.1f}" y2="{ty_(y)+4:.1f}"/>'
            f'<line class="dim" x1="{tx(x2):.1f}" y1="{ty_(y)-4:.1f}" x2="{tx(x2):.1f}" y2="{ty_(y)+4:.1f}"/>'
            f'<text class="dt" x="{(tx(x1)+tx(x2))/2:.1f}" y="{ty_(y)-4:.1f}" text-anchor="middle">{txt}</text>')
def sdim_v(x, y1, y2, txt):
    return (f'<line class="dim" x1="{tx(x):.1f}" y1="{ty_(y1):.1f}" x2="{tx(x):.1f}" y2="{ty_(y2):.1f}"/>'
            f'<line class="dim" x1="{tx(x)-4:.1f}" y1="{ty_(y1):.1f}" x2="{tx(x)+4:.1f}" y2="{ty_(y1):.1f}"/>'
            f'<line class="dim" x1="{tx(x)-4:.1f}" y1="{ty_(y2):.1f}" x2="{tx(x)+4:.1f}" y2="{ty_(y2):.1f}"/>'
            f'<text class="dt" transform="translate({tx(x)-5:.1f},{(ty_(y1)+ty_(y2))/2:.1f}) rotate(-90)" text-anchor="middle">{txt}</text>')
out.append(sdim_h(0, ROOF_W, 2600, f"{ROOF_W:,.0f} (inner)"))
out.append(sdim_h(xr, xr + RAIL_LEN, 1300, f"{RAIL_LEN:,} rail length"))
out.append(sdim_v(-2300, 0, UPPER_BOT, f"{-UPPER_BOT:,.0f}"))
out.append(sdim_v(-900, -SET_EDGE, -SET_EDGE - t0["depth"], f'{t0["depth"]:,.0f}'))
out.append(sdim_v(-900, -SET_EDGE - t0["depth"], -SET_EDGE - t0["depth"] - AISLE, f"{AISLE}"))
for (a, b, name) in OBS:
    cx, cy = tx((a[0]+b[0])/2), ty_((a[1]+b[1])/2)
    out.append(f'<text class="olab" transform="translate({cx-12 if name=="LIFT CORE" else cx+3:.1f},{cy:.1f}) rotate({0 if name=="LIFT CORE" else -90})" text-anchor="middle">{name}</text>')
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" class="plan">'
       + "".join(out) + "</svg>")
open(os.path.join(HERE, "PV_Layout_Enerack_10deg.svg"), "w").write(svg)

summary = dict(counts=counts, base=nb, opt=no, kwp_base=kw(nb), kwp_opt=kw(no), frames=frames,
               rail_lines=rails_lines, types={k: {kk: round(vv) if isinstance(vv, float) else vv
               for kk, vv in v.items() if kk != "rails"} for k, v in TYPES.items()})
print(summary)
