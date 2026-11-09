"""Engineering-style single-line diagram (IEC 60617 symbols, A3 frame, title block).

Outputs (this folder):
  PV_SLD_Engineering.svg   standalone SVG (insert into Word 365 - stays sharp)
  PV_SLD_Engineering.html  wrapper used to print the PDF / PNG (node sld_iec_export.js)
"""
import os
from html import escape as esc

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1680, 1188                      # A3 landscape proportions (1:1.414)
g = []
def add(s): g.append(s)
def L(x1, y1, x2, y2, c="ln"): add(f'<line class="{c}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
def PL(pts, c="ln"): add(f'<polyline class="{c}" points="{" ".join(f"{x},{y}" for x, y in pts)}"/>')
def R(x, y, w, h, c="box"): add(f'<rect class="{c}" x="{x}" y="{y}" width="{w}" height="{h}"/>')
def C(x, y, r, c="ln"): add(f'<circle class="{c}" cx="{x}" cy="{y}" r="{r}"/>')
def T(x, y, s, c="t", a="start", rot=None):
    tr = f' transform="rotate({rot} {x} {y})"' if rot else ""
    add(f'<text class="{c}" x="{x}" y="{y}" text-anchor="{a}"{tr}>{esc(s)}</text>')

# ------------------------------------------------------------------ IEC 60617 symbols
def pv_array(x, y, w=70, h=46):
    """PV generator: rectangle with diagonal and incident-light arrows."""
    R(x, y, w, h, "boxh"); L(x, y + h, x + w, y, "ln")
    for k in (0, 14):
        L(x + 10 + k, y - 22, x + 20 + k, y - 8, "thin")
        PL([(x + 15 + k, y - 9), (x + 20 + k, y - 8), (x + 20 + k, y - 13)], "thin")
def breaker_h(x, y, label=None, sub=None, existing=False):
    """Circuit breaker (07-13-05) on a horizontal conductor from x to x+40: blade + cross at fixed contact."""
    c = "lnx" if existing else "lnh"
    L(x, y, x + 8, y, c); L(x + 8, y, x + 30, y - 12, c); L(x + 30, y, x + 40, y, c)
    L(x + 26, y - 4, x + 34, y + 4, c); L(x + 26, y + 4, x + 34, y - 4, c)
    if label: T(x + 20, y - 20, label, "ts", "middle")
    if sub: T(x + 20, y + 18, sub, "ts", "middle")
def breaker_v(x, y, label=None, sub=None, existing=False):
    """Circuit breaker on a vertical conductor from y to y+40."""
    c = "lnx" if existing else "lnh"
    L(x, y, x, y + 8, c); L(x, y + 8, x + 12, y + 30, c); L(x, y + 30, x, y + 40, c)
    L(x - 4, y + 26, x + 4, y + 34, c); L(x - 4, y + 34, x + 4, y + 26, c)
    if label: T(x - 10, y + 18, label, "ts", "end")
    if sub: T(x - 10, y + 31, sub, "ts", "end")
def switch_disconnector_h(x, y, label=None, sub=None):
    """Switch-disconnector (07-13-08): blade + isolating bar + load-break circle at fixed contact."""
    L(x, y, x + 8, y, "lnh"); L(x + 8, y, x + 30, y - 12, "lnh"); L(x + 30, y, x + 40, y, "lnh")
    L(x + 30, y - 6, x + 30, y + 6, "lnh"); C(x + 30, y - 9, 3, "lnh")
    if label: T(x + 20, y - 22, label, "ts", "middle")
    if sub: T(x + 20, y + 18, sub, "ts", "middle")
def dc_switch_h(x, y):
    L(x, y, x + 8, y, "lnh"); L(x + 8, y, x + 30, y - 12, "lnh"); L(x + 30, y, x + 40, y, "lnh")
    L(x + 30, y - 6, x + 30, y + 6, "lnh"); C(x + 30, y - 9, 3, "lnh")
def earth(x, y):
    L(x, y, x, y + 8, "ln"); L(x - 11, y + 8, x + 11, y + 8, "ln"); L(x - 7, y + 12, x + 7, y + 12, "ln"); L(x - 3, y + 16, x + 3, y + 16, "ln")
def spd_v(x, y, label="SPD T2"):
    """Surge arrester: rectangle with arrow, connected to earth below."""
    L(x, y, x, y + 14, "lnh"); R(x - 8, y + 14, 16, 26, "boxh"); L(x, y + 18, x, y + 34, "thin")
    PL([(x - 3, y + 30), (x, y + 35), (x + 3, y + 30)], "thin"); L(x, y + 40, x, y + 48, "lnh"); earth(x, y + 48)
    T(x - 14, y + 31, label, "ts", "end")
def ct_v(x, y, label):
    """Current transformer on a vertical conductor: circle around the conductor + secondary lead."""
    C(x, y, 9, "lnx")
    T(x - 16, y + 4, label, "ts", "end")
def transformer_v(x, y):
    C(x, y, 14, "lnx"); C(x, y + 20, 14, "lnx")
def meter(x, y, txt="kWh"):
    R(x - 18, y - 12, 36, 24, "box"); T(x, y + 4, txt, "ts", "middle")
def strokes(x, y, n, label=None, below=False):
    """Conductor-count marks on a horizontal line."""
    for i in range(n):
        xx = x + i * 5
        L(xx - 4, y + 6, xx + 4, y - 6, "thin")
    if label: T(x + n * 2.5, y + (18 if below else -12), label, "ts", "middle")
def tag(x, y, t, pe=False):
    add(f'<rect class="tag" x="{x-15}" y="{y-9}" width="30" height="18" rx="9"/>'); T(x, y + 4, t, "tagt", "middle")

# ------------------------------------------------------------------ frame, grid, title block
M = 20
R(M, M, W - 2 * M, H - 2 * M, "frame")
R(M + 20, M + 20, W - 2 * M - 40, H - 2 * M - 40, "frame2")
cols, rows = 8, 6
for i in range(cols):
    x = M + 20 + (W - 2 * M - 40) * (i + 0.5) / cols
    T(x, M + 14, str(i + 1), "grid", "middle"); T(x, H - M - 6, str(i + 1), "grid", "middle")
    if i: xx = M + 20 + (W - 2 * M - 40) * i / cols; L(xx, M, xx, M + 20, "thin"); L(xx, H - M - 20, xx, H - M, "thin")
for j in range(rows):
    y = M + 20 + (H - 2 * M - 40) * (j + 0.5) / rows
    T(M + 10, y + 4, "ABCDEF"[j], "grid", "middle"); T(W - M - 10, y + 4, "ABCDEF"[j], "grid", "middle")
    if j: yy = M + 20 + (H - 2 * M - 40) * j / rows; L(M, yy, M + 20, yy, "thin"); L(W - M - 20, yy, W - M, yy, "thin")

X0, X1 = M + 20, W - M - 20          # inner frame 40 .. 1640
Y1 = H - M - 20                      # 1148
BAND = 880                           # top of the bottom information band
L(X0, BAND, X1, BAND, "frame2")

# ------------------------------------------------------------------ enclosures (dash-dot)
R(70, 95, 590, 735, "encl"); T(80, 112, "ROOF – PV ARRAY & INVERTER STATION (NEW)", "enc")
R(700, 95, 300, 735, "encl"); T(710, 112, "=ACCP  AC COMBINER PANEL, ROOF (NEW)", "enc")
R(1170, 95, 450, 735, "enclx"); T(1180, 112, "=MLVS  MAIN LV SWITCHBOARD, LV ROOM (EXISTING)", "enc")

# ------------------------------------------------------------------ PV arrays, DC, inverters
def inverter_chain(y, inv, arr, strings, kwp, mods):
    pv_array(95, y - 23)
    T(95, y + 52, f"PV ARRAY {arr}", "tb"); T(95, y + 66, f"{mods} × 620 Wp = {kwp} kWp", "ts"); T(95, y + 80, strings, "ts")
    L(165, y, 230, y, "dc"); strokes(196, y, 2, "8 × (2 × 6 mm²)")
    dc_switch_h(230, y); L(270, y, 330, y, "dc"); spd_v(300, y, "")
    T(262, y - 55, "8 × DC switch-disc. 1200 V 32 A", "ts", "middle"); T(262, y - 42, "8 × DC SPD T2, Ucpv 1100 V", "ts", "middle")
    T(262, y - 29, "(1 each per string)", "ts", "middle")
    # inverter (DC/AC)
    R(330, y - 45, 100, 90, "boxh"); L(330, y + 45, 430, y - 45, "ln")
    T(345, y - 20, "=", "sym"); T(405, y + 32, "~", "sym")
    T(380, y - 55, f"={inv}", "tb", "middle")
    T(380, y + 62, "Sigen PV 80M1, 80 kW 3N~", "ts", "middle"); T(380, y + 75, "1100 V DC, 2 strings/MPPT", "ts", "middle")
    T(380, y + 88, "integral DC switch + SPD T2", "ts", "middle")
    return y

Y_I1, Y_I2 = 260, 600
inverter_chain(Y_I1, "INV-01", "PV-1", "8 strings × 19", "94.24", 152)
inverter_chain(Y_I2, "INV-02", "PV-2", "3 × 19 + 5 × 18", "91.14", 147)

# AC: inverters -> ACCP incomers
BX = 880                                    # ACCP busbar x
for y, c, e in ((Y_I1, "C1", "E1"), (Y_I2, "C2", "E2")):
    L(430, y, 760, y, "lnh"); strokes(520, y, 4, "3N~")
    tag(600, y, c); T(445, y + 19, "4C × 50 mm² Cu XLPE ≈ 4 m", "ts")
    breaker_h(760, y, "Q1" if c == "C1" else "Q2", "MCCB 4P 160 A, Ir 140 A")
    L(800, y, BX, y, "lnh")
    # PE
    L(430, y + 30, 455, y + 30, "pe"); L(455, y + 30, 690, y + 30, "pe"); T(470, y + 44, f"{e}: 25 mm² Cu PE", "tspe")
L(690, Y_I1 + 30, 690, 790, "pe"); L(690, Y_I2 + 30, 690, 790, "pe")

# ACCP busbar + SPD + outgoing
L(BX, 200, BX, 680, "bus"); T(BX + 8, 196, "400 V 3N~ 400 A", "ts")
L(BX, 500, 830, 500, "lnh"); spd_v(830, 500, "F1 AC SPD T2 4P")
YO = 400
L(BX, YO, 930, YO, "lnh"); switch_disconnector_h(930, YO, "Q3", "4P 400 A roof isolator")
L(970, YO, 1220, YO, "lnh"); strokes(1090, YO, 4, None)
tag(1140, YO - 30, "C3"); T(1140, YO + 26, "4C × 120 mm² Cu", "ts", "middle"); T(1140, YO + 39, "XLPE/SWA ≈ 80 m", "ts", "middle")
# ACCP earth bar
L(720, 790, 980, 790, "pebar"); T(850, 782, "ACCP EARTH BAR", "tspe", "middle")

# ------------------------------------------------------------------ MLVS (existing)
MB = 1480
transformer_v(MB, 60 + 6)
T(MB - 22, 64, "EXISTING TRANSFORMER / UEDCL SUPPLY", "tsx", "end")
L(MB, 100, MB, 160, "lnx")
L(MB, 179, MB, 210, "lnx")
meter(MB + 70, 195); L(MB + 9, 170, MB + 52, 190, "thin"); T(MB + 70, 222, "P1 UEDCL kWh METER", "tsx", "middle")
breaker_v(MB, 210, "Q0 MAIN INCOMER", "(existing, grid)", existing=True)
L(MB, 250, MB, 270, "lnx")
L(MB, 270, MB, 760, "busx"); T(MB - 8, 745, "MAIN BUSBAR 400 V 3N~ (≥ 1000 A, confirm)", "tsx", "end")
# new PV way (heavy)
L(1220, YO, 1300, YO, "lnh"); breaker_h(1300, YO, "Q5 ACB 1000 A", "Masterpact NW10 H1"); L(1340, YO, MB, YO, "lnh")
T(1320, YO + 32, "EXISTING – SOLAR INCOMER", "tb", "middle"); T(1320, YO + 46, "400 A rating plug, Ir 280 A", "ts", "middle")
# existing outgoing feeders (light)
for i, yy in enumerate((520, 590, 660)):
    L(MB, yy, 1540, yy, "lnx"); breaker_h(1540, yy, existing=True); L(1580, yy, 1600, yy, "lnx")
    T(1600, yy + 18, "EXISTING HOTEL LOAD", "tsx", "end")
# MET + E3
L(1200, 790, 1300, 790, "pebar"); T(1250, 782, "MET", "tspe", "middle"); earth(1250, 790)
L(980, 790, 1200, 790, "pe"); tag(1090, 790, "E3"); T(1090, 815, "E3: 70 mm² Cu PE ≈ 80 m", "tspe", "middle")


# ------------------------------------------------------------------ bottom band: legend | schedule | notes + title block
# symbol legend
R(X0, BAND, 420, Y1 - BAND, "frame2"); T(X0 + 10, BAND + 18, "SYMBOLS (IEC 60617)", "tb")
ly = BAND + 42
def leg(sym, text):
    global ly
    sym(X0 + 20, ly); T(X0 + 110, ly + 4, text, "ts"); ly += 26
leg(lambda x, y: (R(x, y - 10, 40, 22, "boxh"), L(x, y + 12, x + 40, y - 10, "ln")), "PV array / PV generator")
leg(lambda x, y: (R(x + 6, y - 11, 28, 24, "boxh"), L(x + 6, y + 13, x + 34, y - 11, "ln")), "Inverter DC/AC")
leg(lambda x, y: breaker_h(x, y), "Circuit breaker (MCCB / ACB)")
leg(lambda x, y: switch_disconnector_h(x, y), "Switch-disconnector (isolator)")
leg(lambda x, y: (L(x, y - 10, x, y + 12, "lnh"), R(x + 12, y - 10, 12, 20, "boxh"), L(x + 18, y - 6, x + 18, y + 6, "thin")), "Surge protective device (SPD)")
leg(lambda x, y: earth(x + 20, y - 10), "Earth / main earthing terminal")
leg(lambda x, y: (L(x, y, x + 40, y, "lnh"), strokes(x + 12, y, 4)), "Heavy = new, light = existing; strokes = conductors")
leg(lambda x, y: (L(x, y - 4, x + 40, y - 4, "dc"), L(x, y + 8, x + 40, y + 8, "pe")), "DC conductor   ·   PE conductor")

# cable schedule
SX = X0 + 420
R(SX, BAND, 600, Y1 - BAND, "frame2"); T(SX + 10, BAND + 18, "CABLE SCHEDULE", "tb")
hdr = [("TAG", 0), ("FROM → TO", 52), ("CABLE", 230), ("LENGTH", 400), ("PROTECTION", 470)]
yh = BAND + 30
R(SX + 6, yh, 588, 18, "thead")
for h, dx in hdr: T(SX + 12 + dx, yh + 13, h, "th")
rows_ = [("S1–S16", "PV strings → inverters", "2 × 6 mm² Cu H1Z2Z2-K", "≈ 40 m", "DC isolator 32 A + DC SPD T2"),
         ("C1, C2", "INV-01/02 → ACCP Q1/Q2", "4C × 50 mm² Cu XLPE", "≈ 4 m", "MCCB 160 A (Ir 140 A)"),
         ("C3", "ACCP Q3 → MLVS Q5", "4C × 120 mm² Cu XLPE/SWA", "≈ 80 m", "ACB NW10 H1, Ir 280 A"),
         ("E1, E2", "INV-01/02 → ACCP earth bar", "25 mm² Cu (G/Y)", "≈ 4 m", "–"),
         ("E3", "ACCP earth bar → MET", "70 mm² Cu (G/Y)", "≈ 80 m", "–"),
         ("–", "Array bonding / spine", "16 mm² / 35 mm² Cu (G/Y)", "≈ 280 m", "–")]
for i, row in enumerate(rows_):
    yy = yh + 18 + i * 22
    R(SX + 6, yy, 588, 22, "trow")
    for (h, dx), v in zip(hdr, row): T(SX + 12 + dx, yy + 15, v, "tdb" if h == "TAG" else "td")
T(SX + 10, Y1 - 10, "Lengths indicative – confirm on site. Sizes per IEC 60364-5-52 / 5-54 (see design report).", "note")

# notes + title block
TX = SX + 600
R(TX, BAND, X1 - TX, Y1 - BAND, "frame2")
T(TX + 10, BAND + 18, "NOTES", "tb")
notes = ["1. 299 × 620 Wp = 185.4 kWp DC; 2 × 80 kW = 160 kW AC; DC/AC 1.16.",
         "2. Grid-tied, no battery. DC SPD T2 + DC isolator on every string.",
         "3. Q5 = existing NW10 H1: 400 A plug, Ir 280 A (else C3 4C × 185 mm²).",
         "4. Final ratings to equipment datasheets and detailed design."]
for i, n in enumerate(notes): T(TX + 10, BAND + 38 + i * 15, n, "ts")
tb_y = BAND + 104
L(TX, tb_y, X1, tb_y, "frame2")
cells = [("CLIENT", "Kampala Marriott Hotel", TX, tb_y, 300, 34),
         ("PROJECT", "Kampala Marriott – Rooftop PV 185.4 kWp", TX + 300, tb_y, X1 - TX - 300, 34),
         ("TITLE", "SINGLE-LINE DIAGRAM – PV SYSTEM & GRID CONNECTION", TX, tb_y + 34, X1 - TX, 40),
         ("DRAWING No.", "PV-SLD-D18102-004", TX, tb_y + 74, 200, 34), ("REV", "B", TX + 200, tb_y + 74, 60, 34),
         ("SCALE / SIZE", "NTS / A3", TX + 260, tb_y + 74, 120, 34), ("DATE", "09.11.2026", TX + 380, tb_y + 74, X1 - TX - 380, 34),
         ("DRAWN", "", TX, tb_y + 108, 200, Y1 - tb_y - 108), ("CHECKED", "", TX + 200, tb_y + 108, 180, Y1 - tb_y - 108),
         ("APPROVED", "", TX + 380, tb_y + 108, X1 - TX - 380, Y1 - tb_y - 108)]
for lab, val, x, y, w, h in cells:
    R(x, y, w, h, "cell"); T(x + 5, y + 11, lab, "lbl")
    if val: T(x + 5, y + h - 9, val, "big" if lab == "TITLE" else "val")

CSS = """
.sld text { font-family: Arial, Helvetica, sans-serif; fill: #000; }
.sld .frame { fill: #fff; stroke: #000; stroke-width: 2.2; }
.sld .frame2 { fill: none; stroke: #000; stroke-width: 1.2; }
.sld .grid { font-size: 11px; }
.sld .ln { fill: none; stroke: #000; stroke-width: 1.2; }
.sld .lnh { fill: none; stroke: #000; stroke-width: 2.2; }
.sld .lnx { fill: none; stroke: #555; stroke-width: 1; }
.sld .thin { fill: none; stroke: #000; stroke-width: 0.8; }
.sld .dc { fill: none; stroke: #000; stroke-width: 2.2; }
.sld .bus { stroke: #000; stroke-width: 6; }
.sld .busx { stroke: #555; stroke-width: 4; }
.sld .pe { fill: none; stroke: #000; stroke-width: 1; stroke-dasharray: 10 3 2 3; }
.sld .pebar { stroke: #000; stroke-width: 4; }
.sld .comm { fill: none; stroke: #000; stroke-width: 1; stroke-dasharray: 6 4; }
.sld .box { fill: #fff; stroke: #000; stroke-width: 1.2; }
.sld .boxh { fill: #fff; stroke: #000; stroke-width: 2; }
.sld .encl { fill: none; stroke: #000; stroke-width: 1; stroke-dasharray: 14 4 2 4; }
.sld .enclx { fill: none; stroke: #555; stroke-width: 1; stroke-dasharray: 14 4 2 4; }
.sld .tag { fill: #fff; stroke: #000; stroke-width: 1.2; }
.sld .tagt { font-size: 10px; font-weight: 700; }
.sld .t, .sld .ts { font-size: 10.5px; }
.sld .tsx { font-size: 10px; fill: #444 !important; }
.sld .tspe { font-size: 10px; font-style: italic; }
.sld .tb { font-size: 11.5px; font-weight: 700; }
.sld .enc { font-size: 11px; font-weight: 700; letter-spacing: .03em; }
.sld .sym { font-size: 24px; font-weight: 700; }
.sld .thead { fill: #000; }
.sld .th { font-size: 9.5px; font-weight: 700; fill: #fff !important; }
.sld .trow { fill: #fff; stroke: #000; stroke-width: 0.5; }
.sld .td { font-size: 9.5px; }
.sld .tdb { font-size: 9.5px; font-weight: 700; }
.sld .note { font-size: 9px; font-style: italic; }
.sld .cell { fill: #fff; stroke: #000; stroke-width: 1; }
.sld .lbl { font-size: 8px; fill: #444 !important; }
.sld .val { font-size: 12px; font-weight: 700; }
.sld .big { font-size: 15px; font-weight: 700; }
"""
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" class="sld">'
       f'<style>{CSS}</style><rect width="{W}" height="{H}" fill="#fff"/>' + "".join(g) + "</svg>")
open(os.path.join(HERE, "PV_SLD_Engineering.svg"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n' + svg)
open(os.path.join(HERE, "PV_SLD_Engineering.html"), "w").write(
    "<!doctype html><html><head><meta charset='utf-8'><title>SLD</title><style>@page{size:A3 landscape;margin:6mm}"
    "html,body{margin:0;background:#fff}svg{height:283mm;width:auto;display:block;margin:0 auto}</style></head><body>" + svg + "</body></html>")
print("ok")
