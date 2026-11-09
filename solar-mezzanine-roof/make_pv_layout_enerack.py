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
BUILD = P(0, 4002)[1]                           # tower / building face below the roof
# existing roof ducts/vents read off the satellite image (approximate - verify on site)
DUCTS = [(3000, -41600, 8100, -44600), (12500, -41600, 16400, -44600), (18800, -41600, 23600, -44600)]
INV1_MODULES = 152                              # INV-01: 8 strings x 19; INV-02 gets the rest (147)

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
"PV-OBSTRUCTION": 6, "PV-TEXT": 7, "PV-DIM": 2,
"PV-EQUIPMENT": 1, "PV-EXISTING": 8,
"PV-CABLE-TRAY": 8, "PV-CABLE-DC-STRING": 10, "PV-CABLE-DC-HOMERUN": 1, "PV-CABLE-AC-C1-C2": 5,
"PV-CABLE-AC-C3": 6, "PV-CABLE-EARTH": 3, "PV-CABLE-COMMS": 30, "PV-CABLE-TAGS": 7}
for n, col in LAY.items(): doc.layers.add(n, color=col)
doc.layers.get("PV-SETBACK").dxf.linetype = "DASHED"
for _ln, _lt in (("PV-CABLE-EARTH", "DASHDOT"), ("PV-CABLE-COMMS", "DASHED"), ("PV-CABLE-DC-STRING", "DOT")):
    doc.layers.get(_ln).dxf.linetype = _lt
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
mod_no = [0]
row_no = [0]
mod_centres = []                                 # (x, y, table index) in string order
table_mid = []
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
    for r in reversed(range(t["rows"])):          # top row first; snake order so rows join at the same end
        yb = ys(r * (MOD_L + GAP))
        row_no[0] += 1
        for col in (range(N_COLS) if row_no[0] % 2 else reversed(range(N_COLS))):
            x = SET_W + col * (MOD_W + GAP)
            msp.add_blockref("PV_MOD_620W", (x, yb), dxfattribs={"layer": lm})
            mod_no[0] += 1
            mod_centres.append((x + MOD_W / 2, yb + hm / 2, idx))
            svg_items.append(("rect", ("mod" if mod_no[0] <= INV1_MODULES else "mod2") + sfx, (x, yb, x + MOD_W, yb + hm)))
    for s in t["rails"]:
        line(xr, ys(s), xr + RAIL_LEN, ys(s), lr, "rail" + sfx)
    yf1 = ys(t["front_off"]); yf2 = yf1 + t["foot_span"]
    for k in range(N_FRAMES):
        xf = xr + FRAME_FIRST + k * FRAME_PITCH
        line(xf, yf1, xf, yf2, lf, "frame" + sfx)
        for yy in (yf1, yf2):
            rect(xf - 150, yy - 150, xf + 150, yy + 150, lo, "foot" + sfx)
    table_mid.append(yt - t["depth"] / 2)
    label = f"T{idx} {ty}x23"
    msp.add_text(label, height=300, dxfattribs={"layer": "PV-TEXT"}).set_placement(
        (xr + RAIL_LEN + 200, yt - t["depth"] / 2), align=TextEntityAlignment.MIDDLE_LEFT)
    svg_items.append(("text", "tlab", (ROOF_W + 500, yt - t["depth"] / 2, label + (" (optional)" if opt else ""))))

# roof, setbacks, obstructions
rect(0, 0, ROOF_W, UPPER_BOT, "PV-ROOF-REF", "roof")
rect(0, LOWER_TOP, ROOF_W, BUILD, "PV-ROOF-REF", "roof")
line(0, LOWER_LIMIT, ROOF_W, LOWER_LIMIT, "PV-ROOF-REF", "zlim")
svg_items.append(("text", "zlab", (300, LOWER_LIMIT - 450, "Architect's PV zone limit")))
svg_items.append(("text", "zlab", (300, BUILD + 450, "Tower / building face – cable riser to LV room (location TBC)")))
for (x1, y1, x2, y2) in DUCTS:
    rect(x1, y1, x2, y2, "PV-EXISTING", "duct")
svg_items.append(("text", "dlab", (3000, -45300, "Existing ducts (approx., verify)")))
# ---------------- inverter station: DC isolator units, DC SPD units, inverters, ACCP ----------------
EQ_Y = -40100                                   # front (north) face of equipment
INV_W, INV_D, ACCP_W, ACCP_D = 1050, 400, 800, 300
DCU_W, DCU_D, GAPU = 500, 250, 150              # DC isolator unit / DC SPD unit (wall boxes on the frame)
STATION_E = 28400
x_acc = STATION_E - ACCP_W
x_inv2 = x_acc - 450 - INV_W
x_dcs2 = x_inv2 - GAPU - DCU_W
x_dci2 = x_dcs2 - GAPU - DCU_W
x_inv1 = x_dci2 - 300 - INV_W
x_dcs1 = x_inv1 - GAPU - DCU_W
x_dci1 = x_dcs1 - GAPU - DCU_W
x0 = x_inv1
eq = [("DCI-01", x_dci1, DCU_W, DCU_D, "dci"), ("DCS-01", x_dcs1, DCU_W, DCU_D, "dcs"), ("INV-01", x_inv1, INV_W, INV_D, "inv"),
      ("DCI-02", x_dci2, DCU_W, DCU_D, "dci"), ("DCS-02", x_dcs2, DCU_W, DCU_D, "dcs"), ("INV-02", x_inv2, INV_W, INV_D, "inv"),
      ("ACCP", x_acc, ACCP_W, ACCP_D, "acc")]
rect(x_dci1 - 300, EQ_Y + 300, STATION_E + 300, EQ_Y - INV_D - 600, "PV-EQUIPMENT", "canopy")
rect(x_dci1 - 300, EQ_Y + 1300, STATION_E + 300, EQ_Y + 300, "PV-EQUIPMENT", "clear")
for name, x, w, dpt, cls in eq:
    rect(x, EQ_Y, x + w, EQ_Y - dpt, "PV-EQUIPMENT", cls)
    msp.add_text(name, height=160, dxfattribs={"layer": "PV-TEXT"}).set_placement((x + w / 2, EQ_Y - dpt - 250), align=TextEntityAlignment.MIDDLE_CENTER)
    svg_items.append(("text", "eqtag", (x + w / 2, EQ_Y - dpt - 150, name)))
# callout to the right of the roof
line(STATION_E + 300, EQ_Y - 300, ROOF_W + 400, EQ_Y - 300, "PV-TEXT", "leader")
svg_items.append(("text", "elab", (ROOF_W + 500, EQ_Y + 300, "INVERTER STATION (steel frame + canopy)")))
svg_items.append(("text", "elab2", (ROOF_W + 500, EQ_Y - 900, "DCI-01/02 DC isolator units (8 × 2P 1200 V 32 A each)")))
svg_items.append(("text", "elab2", (ROOF_W + 500, EQ_Y - 2000, "DCS-01/02 DC SPD units (8 × Type 2, 1100 V each)")))
svg_items.append(("text", "elab2", (ROOF_W + 500, EQ_Y - 3100, "INV-01/02 Sigen PV 80M1 80 kW · ACCP 400 A")))
# DC cable tray: east corridor between rail ends and the east wall, stubs to each table, run along the station
TRAY_X = 27900
TRAY_Y = EQ_Y + 800
line(TRAY_X, -1000 - 600, TRAY_X, TRAY_Y, "PV-CABLE-TRAY", "tray")
line(TRAY_X, TRAY_Y, x_dci1 + DCU_W / 2, TRAY_Y, "PV-CABLE-TRAY", "tray")
for xx in (x_dci1 + DCU_W / 2, x_dci2 + DCU_W / 2):
    line(xx, TRAY_Y, xx, EQ_Y, "PV-CABLE-TRAY", "tray")
for ym in table_mid:
    line(xr + RAIL_LEN, ym, TRAY_X, ym, "PV-CABLE-TRAY", "tray")
svg_items.append(("text", "trlab", (ROOF_W + 500, -15350, "DC cable tray (east corridor)")))
# C3 route from ACCP to the riser at the building face
cx3 = x_acc + ACCP_W / 2
svg_items.append(("line", "c3", (cx3, EQ_Y - ACCP_D, cx3, BUILD)))      # sheet only; DXF gets the real cables below
line(cx3, -50000, ROOF_W + 400, -50000, "PV-TEXT", "leader")
svg_items.append(("text", "c3lab", (ROOF_W + 500, -49700, "C3 4C×240 mm² + E3 120 mm²")))
svg_items.append(("text", "c3lab", (ROOF_W + 500, -50900, "to MLVS via riser")))
svg_items.append(("text", "c3lab", (ROOF_W + 500, -52100, "(≈ 200 m, route TBC)")))
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
    "INV-01 (80 kW): T1, T2, T3 + T4 top row + 14 modules = 152 modules, 8 strings x 19",
    "INV-02 (80 kW): rest of T4 + T5-T7 = 147 modules, 3 x 19 + 5 x 18",
    "DC isolator units, DC SPD units, inverters + ACCP on shaded steel frame (equipment strip, east end); DC tray along east corridor; C3 to riser TBC.",
    "Foot blocks drawn 300x300 indicative - size/weight by Enerack. Origin 0,0 = inner NW corner of upper roof.",
]
for i, tx in enumerate(notes):
    msp.add_text(tx, height=450 if i == 0 else 330, dxfattribs={"layer": "PV-TEXT"}).set_placement(
        (ROOF_W + 6500, -1000 - i * 750), align=TextEntityAlignment.LEFT)

# =====================================================================================
# CABLES (DXF only) – indicative routing, one entity per conductor group
# =====================================================================================
def pl(pts, layer, w=None):
    msp.add_lwpolyline(pts, dxfattribs={"layer": layer, **({"const_width": w} if w else {})})
def tagtxt(t, xy, h=220, rot=0):
    msp.add_text(t, height=h, rotation=rot, dxfattribs={"layer": "PV-CABLE-TAGS"}).set_placement(xy, align=TextEntityAlignment.MIDDLE_LEFT)

# cable tray outline (100 mm wide) along the east corridor and the stubs
pl([(TRAY_X - 50, -1600), (TRAY_X - 50, EQ_Y + 300), (TRAY_X + 50, EQ_Y + 300), (TRAY_X + 50, -1600), (TRAY_X - 50, -1600)], "PV-CABLE-TRAY")
tagtxt("CABLE TRAY 100 mm HDG + UV cover", (TRAY_X + 200, -30000), 220, 90)

# strings: sequences of modules in snake order
sizes = [19] * 8 + [19] * 3 + [18] * 5
inv_of = ["INV-01"] * 8 + ["INV-02"] * 8
assert sum(sizes) == len(mod_centres) == 299
inv_x = {"INV-01": x_dci1, "INV-02": x_dci2}
term_no = {"INV-01": 0, "INV-02": 0}
k = 0; hr_no = 0
for si, n in enumerate(sizes):
    seg = mod_centres[k:k + n]; k += n
    sname = f"S{si % 8 + 1}"; inv = inv_of[si]
    # string path through the modules (module-to-module leads)
    pl([(x, y) for x, y, _ in seg], "PV-CABLE-DC-STRING")
    mid = seg[len(seg) // 2]
    tagtxt(f"{inv} {sname} ({n} mod.)", (mid[0] - 900, mid[1] + 250), 180)
    # home runs (+ and −) from both string ends to the inverter DC inputs
    for end, pol in ((seg[0], "+"), (seg[-1], "−")):
        off = 30 + hr_no * 22; hr_no += 1
        tx_ = TRAY_X - 40 + (off % 80)
        xi = inv_x[inv] + 20 + term_no[inv] * 28; term_no[inv] += 1
        yrun = end[1] - 300 - (hr_no % 4) * 40           # along the rail under the modules
        pts = [(end[0], end[1]), (end[0], yrun), (tx_, yrun), (tx_, EQ_Y + 600 + (hr_no % 16) * 15),
               (xi, EQ_Y + 600 + (hr_no % 16) * 15), (xi, EQ_Y)]
        pl(pts, "PV-CABLE-DC-HOMERUN")
for xu, xi_ in ((x_dci1, x_inv1), (x_dci2, x_inv2)):
    pl([(xu + DCU_W, EQ_Y - 120), (x_dcs1 if xu == x_dci1 else x_dcs2, EQ_Y - 120)], "PV-CABLE-DC-HOMERUN")
    pl([((x_dcs1 if xu == x_dci1 else x_dcs2) + DCU_W, EQ_Y - 120), (xi_, EQ_Y - 120)], "PV-CABLE-DC-HOMERUN")
tagtxt("DC HOME RUNS: 16 strings × (+/−) 6 mm² Cu H1Z2Z2-K in tray", (TRAY_X + 400, -24000), 220, 90)

# AC: C1 / C2 inverter → ACCP (4C × 50 mm²)
xa = x_acc
for name, xi, ydrop, xin in (("C1", x_inv1 + INV_W / 2, EQ_Y - 700, xa + 200), ("C2", x_inv2 + INV_W / 2, EQ_Y - 850, xa + 350)):
    pl([(xi, EQ_Y - INV_D), (xi, ydrop), (xin, ydrop), (xin, EQ_Y - ACCP_D)], "PV-CABLE-AC-C1-C2", 40)
    tagtxt(f"{name} 4C×50 mm² Cu XLPE ≈4 m", (xi - 500, ydrop - 220), 160)
# AC: C3 ACCP → riser → MLVS (4C × 120 mm² XLPE/SWA)
c3x = xa + 550
pl([(c3x, EQ_Y - ACCP_D), (c3x, BUILD), (c3x, BUILD - 800)], "PV-CABLE-AC-C3", 60)
tagtxt("C3 4C×240 mm² Cu XLPE/SWA → riser → MLVS Q5 NW10 H1 solar incomer (≈200 m TBC)", (c3x + 250, -47000), 220, 90)

# EARTH: array bonding 16 mm² along each table, 35 mm² spine in tray, E1/E2 25 mm², E3 70 mm²
for ym in table_mid:
    pl([(xr, ym + 120), (xr + RAIL_LEN, ym + 120), (TRAY_X + 30, ym + 120)], "PV-CABLE-EARTH")
pl([(TRAY_X + 30, table_mid[0] + 120), (TRAY_X + 30, EQ_Y + 500), (xa + ACCP_W - 100, EQ_Y + 500), (xa + ACCP_W - 100, EQ_Y - ACCP_D)], "PV-CABLE-EARTH")
tagtxt("ARRAY BONDING 16 mm² Cu per table + 35 mm² spine to ACCP earth bar", (TRAY_X + 700, -24000), 200, 90)
for name, xi, ydrop, xin in (("E1", x_inv1 + INV_W / 2 + 120, EQ_Y - 760, xa + 260), ("E2", x_inv2 + INV_W / 2 + 120, EQ_Y - 910, xa + 410)):
    pl([(xi, EQ_Y - INV_D), (xi, ydrop), (xin, ydrop), (xin, EQ_Y - ACCP_D)], "PV-CABLE-EARTH")
    tagtxt(f"{name} 25 mm² Cu", (xi + 150, ydrop - 200), 140)
pl([(c3x + 120, EQ_Y - ACCP_D), (c3x + 120, BUILD), (c3x + 120, BUILD - 800)], "PV-CABLE-EARTH")
tagtxt("E3 120 mm² Cu → MET (LV room)", (c3x + 600, -47000), 200, 90)

doc.saveas(os.path.join(HERE, "PV_Layout_Enerack_10deg.dxf"))

# ---------------- SVG drawing sheet (plan) ----------------
S = 0.0105                                     # px per mm
minx, maxx = -3200, ROOF_W + 9800
miny, maxy = BUILD - 1500, 3800
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
        if cls == "eqtag":
            out.append(f'<text class="eqtag" transform="translate({tx(x)+1.6:.2f},{ty_(y):.2f}) rotate(-90)" style="text-anchor:end">{s}</text>'); continue
        anchor = ' text-anchor="end"' if cls.endswith("-end") else ""
        out.append(f'<text class="{cls.replace("-end", "")}" x="{tx(x):.2f}" y="{ty_(y)+3:.2f}"{anchor}>{s}</text>')
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
