"""Single-line diagram (SLD) for the 185.4 kWp rooftop PV system -> SLD.html (then node sld_pdf.js)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))

W, H = 1680, 1060
g = []
def L(x1, y1, x2, y2, cls="w"): g.append(f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
def PL(pts, cls="w"): g.append(f'<polyline class="{cls}" points="{" ".join(f"{x},{y}" for x, y in pts)}"/>')
def R(x, y, w, h, cls="box"): g.append(f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}"/>')
def T(x, y, s, cls="t", anchor="start"): g.append(f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}">{s}</text>')
def C(x, y, r, cls="w"): g.append(f'<circle class="{cls}" cx="{x}" cy="{y}" r="{r}"/>')

def pv_string(x, y, label):
    # PV module symbol: box with diagonal + sun arrows
    R(x, y, 46, 30, "pv"); L(x, y + 30, x + 46, y, "thin")
    T(x + 56, y + 10, label, "ts")
def breaker(x, y, label=None, horiz=True, right=True):
    # circuit breaker symbol on a horizontal line at (x,y): small arc + cross
    if horiz:
        g.append(f'<path class="w" d="M{x} {y} q 12 -16 24 0"/>')
        L(x + 9, y - 13, x + 15, y - 7, "w"); L(x + 15, y - 13, x + 9, y - 7, "w")
        if label: T(x + 12, y - 20, label, "ts", "middle")
def isolator(x, y, label=None):
    L(x, y, x + 6, y); L(x + 6, y, x + 24, y - 12); L(x + 24, y, x + 30, y)
    C(x + 6, y, 2.5, "dot")
    if label: T(x + 15, y - 18, label, "ts", "middle")
def spd(x, y, label="SPD Type II"):
    L(x, y, x, y + 26); R(x - 9, y + 26, 18, 26, "box"); L(x - 5, y + 32, x + 5, y + 46, "thin")
    L(x, y + 52, x, y + 64); earth(x, y + 64); T(x - 14, y + 44, label, "ts", "end")
def earth(x, y):
    L(x - 12, y, x + 12, y); L(x - 8, y + 5, x + 8, y + 5); L(x - 4, y + 10, x + 4, y + 10)
def ct(x, y, label="CT"):
    C(x, y, 9, "ctc")
    if label: T(x, y - 14, label, "ts", "middle")

# ---------------- title ----------------
T(30, 40, "SINGLE-LINE DIAGRAM – 185.4 kWp ROOFTOP SOLAR PV SYSTEM (GRID-TIED, ZERO EXPORT, NO BATTERY)", "h")
T(30, 64, "Kampala Marriott Hotel – mezzanine roof · 299 × 620 Wp modules · 2 × 80 kW string inverters", "sub")

# ---------------- zone frames ----------------
R(20, 90, 760, 760, "zone"); T(32, 112, "ROOF – PV ARRAY &amp; INVERTERS", "zt")
R(800, 90, 380, 760, "zone"); T(812, 112, "ROOF – AC COMBINER PANEL (ACCP)", "zt")
R(1240, 90, 420, 760, "zone"); T(1252, 112, "LV ROOM – MAIN LV SWITCHBOARD (MLVS)", "zt")

# ---------------- PV strings & inverters ----------------
def inverter_block(y0, name, strings, kwp):
    # strings column
    ys = [y0 + i * 38 for i in range(len(strings))]
    for yy, lab in zip(ys, strings):
        pv_string(50, yy, lab)
        PL([(96, yy + 15), (300, yy + 15)], "dc")
    # DC bus into inverter
    L(300, ys[0] + 15, 300, ys[-1] + 15, "dc")
    PL([(300, (ys[0] + ys[-1]) / 2 + 15), (360, (ys[0] + ys[-1]) / 2 + 15)], "dc")
    yc = (ys[0] + ys[-1]) / 2 + 15
    isolator(330, yc, None)
    T(345, yc - 34, "DC isolator", "ts", "middle"); T(345, yc - 21, "+ SPD (in inv.)", "ts", "middle")
    # inverter symbol
    R(380, yc - 50, 130, 100, "inv")
    L(380, yc + 50, 510, yc - 50, "thin")
    T(400, yc - 20, "=", "sym"); T(475, yc + 32, "~", "sym")
    T(445, yc + 72, name, "tb", "middle")
    T(445, yc + 90, f"80 kW · 400 V 3φ · {kwp}", "ts", "middle")
    T(445, yc - 60, "MPPT ≥ 8 · 1,100 V DC", "ts", "middle")
    # AC out to combiner
    PL([(510, yc), (900, yc)], "ac")
    T(700, yc - 10, "4C × 50 mm² Cu XLPE", "ts", "middle")
    return yc

strings1 = [f"S{i}: 19 × 620 Wp" for i in range(1, 9)]
strings2 = [f"S{i}: 19 × 620 Wp" for i in range(1, 4)] + [f"S{i}: 18 × 620 Wp" for i in range(4, 9)]
yc1 = inverter_block(140, "INV-01", strings1, "94.2 kWp (152 mod.)")
yc2 = inverter_block(490, "INV-02", strings2, "91.1 kWp (147 mod.)")
T(40, 470, "PV cable 6 mm² double-insulated, in UV-resistant trunking", "note")
T(40, 820, "PV cable 6 mm² double-insulated, in UV-resistant trunking", "note")

# ---------------- AC combiner panel ----------------
R(880, 150, 260, 620, "panel")
bx = 1060                                     # vertical busbar in ACCP
L(bx, 200, bx, 700, "bus"); T(bx + 8, 196, "400 V busbar", "ts")
for yc, n in ((yc1, "1"), (yc2, "2")):
    breaker(930, yc, f"MCCB 125 A")
    PL([(954, yc), (bx, yc)], "ac")
# SPD
PL([(bx, 520), (960, 520)], "ac"); spd(960, 520)
# outgoing
yo = 420
PL([(bx, yo), (1090, yo)], "ac"); breaker(1090, yo, "MCCB 250 A"); PL([(1114, yo), (1160, yo)], "ac")
isolator(1160, yo, None); T(1175, yo + 24, "Roof isolator", "ts", "middle"); T(1175, yo + 38, "250 A", "ts", "middle")
PL([(1190, yo), (1340, yo)], "ac")
T(1262, yo - 50, "4C × 120 mm²", "ts", "middle"); T(1262, yo - 36, "Cu XLPE/SWA", "ts", "middle"); T(1262, yo - 22, "≈ 80 m (confirm)", "ts", "middle")

# ---------------- main LV switchboard ----------------
R(1320, 150, 320, 620, "panel")
mb = 1560
L(mb, 180, mb, 720, "bus"); T(mb - 8, 740, "MLVS main busbar 400 V", "ts", "end")
breaker(1340, yo); T(1352, yo + 24, "250 A PV way", "ts", "middle"); PL([(1364, yo), (mb, yo)], "ac")
# utility incomer from top
T(mb, 128, "UEDCL supply / transformer", "tb", "middle")
L(mb, 136, mb, 150, "ac")
L(mb, 150, mb, 180, "ac")
ct(mb, 230, None); T(mb - 16, 234, "CTs (export control)", "ts", "end")
R(mb - 22, 255, 44, 30, "box"); T(mb, 275, "kWh", "ts", "middle"); T(mb - 30, 275, "Utility meter", "ts", "end")
g.append(f'<path class="w" d="M{mb} 300 q 16 12 0 24"/>'); T(mb - 12, 318, "Main incomer ACB", "ts", "end")
# existing hotel loads
for i, yy in enumerate((540, 600, 660)):
    PL([(mb, yy), (1480, yy)], "ac"); breaker(1456, yy); PL([(1456, yy), (1400, yy)], "ac")
    T(1392, yy + 4, "Hotel load", "ts", "end")

# ---------------- zero-export controller & monitoring ----------------
R(1320, 880, 300, 70, "ctrl"); T(1470, 908, "ZERO-EXPORT CONTROLLER", "tb", "middle")
T(1470, 928, "+ data logger / remote monitoring", "ts", "middle")
PL([(mb, 240), (1640, 240), (1640, 915), (1620, 915)], "comm")
T(1632, 600, "CT signals", "ts", "end")
PL([(1320, 915), (600, 915), (600, yc1 + 35), (510, yc1 + 35)], "comm")
PL([(600, yc2 + 35), (510, yc2 + 35)], "comm")
T(800, 908, "RS485 / Modbus – active power limit to INV-01 / INV-02", "ts", "middle")

# ---------------- earthing ----------------
R(30, 960, 560, 70, "earthbox")
T(44, 984, "EARTHING &amp; LIGHTNING PROTECTION", "tb")
T(44, 1004, "Array frames &amp; rails bonded (6/16 mm² Cu) → main earth bar → building earth", "ts")
T(44, 1020, "Integrated with existing lightning protection system (IEC 62305); SPDs on DC and AC sides", "ts")
earth(610, 1000)

# ---------------- legend ----------------
R(640, 960, 640, 70, "earthbox")
T(654, 984, "LEGEND", "tb")
L(654, 1004, 694, 1004, "dc"); T(700, 1008, "DC (PV)", "ts")
L(780, 1004, 820, 1004, "ac"); T(826, 1008, "AC 400 V", "ts")
L(900, 1004, 940, 1004, "comm"); T(946, 1008, "Control / comms", "ts")
breaker(1060, 1004); T(1090, 1008, "Circuit breaker", "ts")
isolator(1180, 1004); T(1214, 1008, "Isolator", "ts")
T(654, 1024, "Strings: INV-01 8 × 19 · INV-02 3 × 19 + 5 × 18 · DC/AC 1.16 · Indicative – confirm with final equipment datasheets", "ts")

svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" class="sld">{"".join(g)}</svg>'
css = """
@page { size: A3 landscape; margin: 8mm; }
html,body { margin:0; background:#fff; }
.sld { width: 404mm; height: auto; font-family: Inter, "DejaVu Sans", Arial, sans-serif; }
.sld .h { font-size: 20px; font-weight: 700; fill: #14365d; }
.sld .sub { font-size: 13px; fill: #4a5561; }
.sld .zt { font-size: 12px; font-weight: 700; fill: #14365d; letter-spacing: .04em; }
.sld .t, .sld .ts { font-size: 11px; fill: #1b2430; }
.sld .tb { font-size: 12.5px; font-weight: 700; fill: #1b2430; }
.sld .note { font-size: 10.5px; fill: #5b6673; font-style: italic; }
.sld .sym { font-size: 26px; fill: #14365d; font-weight: 700; }
.sld .zone { fill: #f7f9fb; stroke: #9aa4ae; stroke-width: 1; stroke-dasharray: 6 4; }
.sld .panel { fill: #fff; stroke: #1b2430; stroke-width: 1.6; }
.sld .box { fill: #fff; stroke: #1b2430; stroke-width: 1.2; }
.sld .pv { fill: #dfe7f5; stroke: #1f4fb5; stroke-width: 1.4; }
.sld .inv { fill: #eef2f6; stroke: #14365d; stroke-width: 2; }
.sld .ctrl { fill: #fff6e5; stroke: #c27a00; stroke-width: 1.6; }
.sld .earthbox { fill: #fff; stroke: #9aa4ae; stroke-width: 1; }
.sld .w { fill: none; stroke: #1b2430; stroke-width: 1.6; }
.sld .thin { stroke: #1b2430; stroke-width: 0.9; }
.sld .dc { fill: none; stroke: #c0392b; stroke-width: 1.8; }
.sld .ac { fill: none; stroke: #1b2430; stroke-width: 2.2; }
.sld .bus { stroke: #1b2430; stroke-width: 6; }
.sld .comm { fill: none; stroke: #c27a00; stroke-width: 1.4; stroke-dasharray: 7 4; }
.sld .ctc { fill: none; stroke: #c27a00; stroke-width: 2; }
.sld .dot { fill: #1b2430; }
"""
open(os.path.join(HERE, "SLD.html"), "w").write(f"<!doctype html><html><head><meta charset='utf-8'><title>Single-Line Diagram</title><style>{css}</style></head><body>{svg}</body></html>")
print("ok")
