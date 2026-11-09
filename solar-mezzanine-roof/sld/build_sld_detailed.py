"""Detailed string-level SLD (contractor style): every string with DC SPD + DC isolator, inverters, AC combiner,
MLVS, UEDCL supply, zero-export metering, earthing, general notes/specs and title block.
Run: python3 build_sld_detailed.py && node sld_detailed_pdf.js  -> PV_SLD_Detailed.svg / .pdf / .png
Equipment per supplied data sheets: Astronergy ASTRO N7 CHSM66RN(DG)/F-BH 620 W; Sigenergy Sigen PV 80M1.
"""
import os
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1680, 1188
g = []
add = g.append
RED, BLU, YEL, BLK, GRN, GRY = "#d62020", "#1f4fd6", "#c99a00", "#111", "#1c9a35", "#666"

def T(x, y, t, size=9, anchor="start", weight="normal", rot=0, color="#000", italic=False):
    tr = f' transform="rotate({rot} {x} {y})"' if rot else ""
    st = ' font-style="italic"' if italic else ""
    add(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{color}"{st}{tr}>{escape(t)}</text>')
def L(x1, y1, x2, y2, c=BLK, w=1.3, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}"{d}/>')
def PL(pts, c=BLK, w=1.3, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<polyline points="{" ".join(f"{x},{y}" for x, y in pts)}" fill="none" stroke="{c}" stroke-width="{w}"{d}/>')
def R(x, y, w, h, c=BLK, sw=1.2, fill="none", rx=0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{c}" stroke-width="{sw}"{d}/>')

def panel(x, y):                      # PV module symbol (square with triangle), 26 x 20
    R(x, y - 10, 26, 20, BLU, 1.2, "#fff")
    PL([(x + 19, y - 7), (x + 7, y), (x + 19, y + 7)], BLU, 1.2)

def spd_dc(x, y1, y2):                # DC SPD box spanning + and - lines, earth tail
    R(x, y1 - 6, 26, y2 - y1 + 12, BLK, 1.2, "#fff")
    for k in range(3):
        xx = x + 5 + k * 8
        R(xx, y1 - 1, 4, y2 - y1 + 2, BLK, 0.8)
    L(x + 13, y2 + 6, x + 13, y2 + 16, GRN, 1.2)

def isolator(x, y1, y2):              # 2-pole DC isolator
    R(x, y1 - 6, 22, y2 - y1 + 12, BLK, 1.1, "#fff")
    for yy in (y1, y2):
        L(x + 4, yy + 3, x + 16, yy - 4, BLK, 1.1); L(x + 2, yy, x + 5, yy, BLK, 1); L(x + 17, yy, x + 20, yy, BLK, 1)

def mccb4(x, y0, gap=7, vertical=False, label=None, lab_side=1):
    """4-pole MCCB across 4 parallel lines (horizontal lines at y0..y0+3*gap, or vertical lines at x..x+3*gap)."""
    if not vertical:
        R(x - 9, y0 - 7, 18, 3 * gap + 14, BLK, 1.1, "#fff")
        for k in range(4):
            yy = y0 + k * gap; L(x - 7, yy, x - 3, yy); L(x - 3, yy, x + 4, yy - 4); L(x + 4, yy, x + 7, yy)
        L(x - 1, y0 - 3, x - 1, y0 + 3 * gap + 1, BLK, 0.7, "2 2")
        if label: T(x, y0 - 12, label, 8.5, "middle", "bold")
    else:
        R(x - 7, y0 - 9, 3 * gap + 14, 18, BLK, 1.1, "#fff")
        for k in range(4):
            xx = x + k * gap; L(xx, y0 - 7, xx, y0 - 3); L(xx, y0 - 3, xx - 4, y0 + 4); L(xx, y0 + 4, xx, y0 + 7)
        if label: T(x + 3 * gap + 14, y0 + 3, label, 8.5, "start", "bold")

def ac4(pts_x, y0, gap=7):            # 4 horizontal AC conductors L1 L2 L3 N
    for k, c in enumerate((RED, YEL, BLU, BLK)):
        L(pts_x[0], y0 + k * gap, pts_x[1], y0 + k * gap, c, 1.4)
def ac4v(x0, y1, y2, gap=7):
    for k, c in enumerate((RED, YEL, BLU, BLK)):
        L(x0 + k * gap, y1, x0 + k * gap, y2, c, 1.4)

def earth(x, y):
    L(x, y, x, y + 8, GRN, 1.4)
    for k, w in enumerate((14, 9, 4)): L(x - w / 2, y + 8 + k * 4, x + w / 2, y + 8 + k * 4, GRN, 1.4)

# ------------------------------------------------------------------ frames
R(10, 10, W - 20, H - 20, BLK, 2.2, "#fff")
R(30, 30, W - 60, H - 60, BLK, 1.2)
T(50, 58, "SINGLE LINE DIAGRAM – 185.4 kWp GRID-TIED ROOFTOP SOLAR PV SYSTEM (ZERO EXPORT)", 15, weight="bold")
T(50, 76, "Kampala Marriott Hotel – mezzanine roof  ·  299 × 620 Wp (Astronergy ASTRO N7)  ·  2 × 80 kW (Sigenergy Sigen PV 80M1)  ·  400 V 3N~ 50 Hz", 10, color="#333")

# ------------------------------------------------------------------ PV arrays + DC side
INV = [dict(name="Inverter - 01", n=152, kwp="94.24", strings=[19] * 8, top=100),
       dict(name="Inverter - 02", n=147, kwp="91.14", strings=[19, 19, 19, 18, 18, 18, 18, 18], top=590)]
AX, SPDX, ISOX, IX, IW = 48, 330, 390, 540, 120
for inv in INV:
    top = inv["top"]; ns = len(inv["strings"]); pitch = 50
    box_h = 70 + ns * pitch
    R(AX - 8, top, 280, box_h, BLK, 1.2)
    T(AX + 132, top + 16, inv["name"], 10, "middle", "bold")
    T(AX + 132, top + 30, f"Total number of panels – {inv['n']}  ·  Number of strings – {ns}", 8.5, "middle")
    T(AX + 132, top + 43, f"Solar PV capacity – {inv['kwp']} kWp", 8.5, "middle")
    iy0, iy1 = top + 50, top + box_h - 10
    R(IX, iy0, IW, iy1 - iy0, BLK, 1.6, "#fff")
    L(IX, iy1, IX + IW, iy0, BLK, 1.1)
    T(IX + 26, iy0 + (iy1 - iy0) * .38, "DC", 12, "middle", "bold"); T(IX + IW - 26, iy0 + (iy1 - iy0) * .7, "AC", 12, "middle", "bold")
    T(IX + IW / 2, iy0 - 26, "Sigenergy Sigen PV 80M1 – 80 kW", 8.5, "middle", "bold")
    T(IX + IW / 2, iy0 - 15, "1100 V DC · 2 strings / MPPT · integral Type II SPD", 7.5, "middle")
    T(IX + IW / 2, iy0 - 5, inv["name"], 8, "middle")
    for i, nm in enumerate(inv["strings"]):
        y = top + 66 + i * pitch; yp, yn = y, y + 14
        T(AX, y - 8, f"PV String {i+1} ({nm} × 620 Wp photovoltaic panels)", 8)
        for k, px in enumerate((AX, AX + 70, AX + 190)):
            panel(px, y + 7)
        T(AX + 145, y + 11, "· · ·", 10, "middle")
        L(AX + 26, y + 7, AX + 70, y + 7, BLU, 1.1); L(AX + 96, y + 7, AX + 125, y + 7, BLU, 1.1); L(AX + 165, y + 7, AX + 190, y + 7, BLU, 1.1)
        L(AX + 216, yp, SPDX, yp, RED, 1.4); L(AX - 4, y + 7, AX - 4, yn, BLU, 1.1)
        PL([(AX, y + 7), (AX - 4, y + 7), (AX - 4, yn + 4), (AX + 216, yn + 4)], BLU, 1.1); L(AX + 216, yn + 4, SPDX, yn, BLU, 1.4)
        L(AX + 216, y + 7, AX + 216, yp, RED, 1.1)
        spd_dc(SPDX, yp, yn); isolator(ISOX, yp, yn)
        if i == 0:
            T(SPDX + 13, yp - 10, "DC SPD", 7.5, "middle", "bold"); T(ISOX + 11, yp - 10, "DC Isolator", 7.5, "middle", "bold")
        L(SPDX + 26, yp, ISOX, yp, RED, 1.4); L(SPDX + 26, yn, ISOX, yn, BLU, 1.4)
        # route to inverter DC input
        ty = iy0 + 14 + i * ((iy1 - iy0 - 28) / max(ns - 1, 1))
        jx = 470 + (i % 4) * 14
        PL([(ISOX + 22, yp), (jx, yp), (jx, ty - 3), (IX, ty - 3)], RED, 1.3)
        PL([(ISOX + 22, yn), (jx + 6, yn), (jx + 6, ty + 3), (IX, ty + 3)], BLU, 1.3)
        L(SPDX + 13, yn + 16, SPDX + 13, yn + 20, GRN, 1); L(SPDX + 13, yn + 20, 438, yn + 20, GRN, 0.9)
    L(438, top + 60, 438, top + box_h, GRN, 1.2)          # DC SPD earth riser
    T(IX - 16, top + box_h - 2, "1C × 6 mm² H1Z2Z2-K DC cable (red +, blue −)", 7.5, "end")
    inv["iy"] = (iy0 + iy1) / 2
    inv["iy0"], inv["iy1"] = iy0, iy1

# ------------------------------------------------------------------ AC: inverters -> ACCP
ACX0 = IX + IW
CX = 860                                    # ACCP enclosure x
R(CX, 210, 210, 760, BLK, 1.3, dash="7 4")
T(CX + 105, 228, "AC COMBINER PANEL (ACCP) – ROOF", 9, "middle", "bold")
T(CX + 105, 241, "400 V 3N~ · busbar 400 A · IP65", 8, "middle")
BUS = CX + 150                              # vertical busbar (4 bars)
ac4v(BUS, 270, 930, 6)
T(BUS + 30, 935, "400 A Busbar", 8.5, "start", "bold", -90)
for k, inv in enumerate(INV):
    y0 = inv["iy"] - 10
    ac4((ACX0, CX + 40), y0)
    mccb4(ACX0 + 70, y0, label="MCCB 4P / 160 A / 25 kA")
    T(ACX0 + 70, y0 + 40, "Ir set 140 A", 7.5, "middle")
    T(ACX0 + 125, y0 + 38, f"C{k+1}: AC cable 4C × 50 mm² Cu XLPE ≈ 4 m", 8, "start", "bold")
    mccb4(CX + 60, y0, label=f"Q{k+1} MCCB 4P 160 A")
    PL([(CX + 69, y0), (BUS - 30, y0)], RED, 1.4)
    for j, c in enumerate((RED, YEL, BLU, BLK)):
        L(CX + 69, y0 + j * 7, BUS - 30 + j * 2, y0 + j * 7, c, 1.4)
        L(BUS - 30 + j * 2, y0 + j * 7, BUS + j * 6, y0 + j * 7, c, 1.4)
    T(ACX0 + 125, y0 + 50, "Inverter max. AC output 133.7 A @ 400 V", 7.5, "start", color="#444")
# AC SPD on busbar
ys = 560
for j, c in enumerate((RED, YEL, BLU, BLK)): L(BUS + j * 6, ys + j * 6, CX + 40, ys + j * 6, c, 1.2)
R(CX + 14, ys - 8, 26, 40, BLK, 1.2, "#fff")
for k in range(4): R(CX + 18 + k * 5, ys - 4, 3, 32, BLK, 0.7)
T(CX + 27, ys + 46, "AC SPD Type 2", 8, "middle", "bold"); T(CX + 27, ys + 57, "4P, Uc 320 Vac, 40 kA", 7.5, "middle")
earth(CX + 27, ys + 62)
# outgoing
YO = 400
for j, c in enumerate((RED, YEL, BLU, BLK)): L(BUS + j * 6, YO + j * 7, CX + 210, YO + j * 7, c, 1.4)
mccb4(BUS + 60, YO, label="Q3 MCCB 4P 400 A")
T(BUS + 60, YO + 42, "25 kA · Ir 280 A", 7.5, "middle")
# earth bar
R(CX + 20, 900, 110, 10, GRN, 1.2, "#e8f6ea"); T(CX + 75, 925, "Earth bar (ACCP)", 8, "middle", color=GRN)

# ------------------------------------------------------------------ C3 -> MLVS
MX = 1150
ac4((CX + 210, MX + 40), YO)
T((CX + 210 + MX) / 2, YO + 70, "C3: AC cable 4C × 120 mm² Cu", 8, "middle", "bold"); T((CX + 210 + MX) / 2, YO + 81, "XLPE/SWA ≈ 80 m (via riser)", 8, "middle", "bold")
R(MX, 120, 230, 850, BLK, 1.3, dash="7 4")
T(MX + 8, 138, "MAIN LV SWITCHBOARD (MLVS)", 9, "start", "bold")
T(MX + 8, 151, "LV room · existing · 400 V 3N~", 8, "start")
MB = MX + 125                                   # main busbar
ac4v(MB, 300, 900, 6)
T(MB + 34, 905, "Main busbar ≥ 1000 A (existing)", 8.5, "start", "bold", -90)
mccb4(MX + 62, YO, label="Q5 MCCB 4P 400 A")
T(MX + 62, YO + 42, "new way · 25 kA · Ir 280 A", 7.5, "middle")
for j, c in enumerate((RED, YEL, BLU, BLK)):
    L(MX + 40, YO + j * 7, MX + 71, YO + j * 7, c, 1.4); L(MX + 71, YO + j * 7, MB + j * 6, YO + j * 7, c, 1.4)
# incomer from UEDCL
ac4v(MB, 60 + 120, 300, 6)
mccb4(MB, 290, 6, vertical=True)
T(MB - 14, 288, "Q0 ACB 4P 1000 A", 8, "end", "bold"); T(MB - 14, 299, "Masterpact NW10 H1 (existing)", 7.5, "end")
R(MB - 10, 190, 38, 30, BLK, 1.2, "#fff"); T(MB + 9, 210, "kWh", 9, "middle", "bold")
T(MB - 16, 208, "UEDCL meter", 8, "end")
ac4v(MB, 90, 190, 6)
add(f'<circle cx="{MB+9}" cy="82" r="10" fill="#fff" stroke="#000" stroke-width="1.2"/>'); T(MB + 9, 86, "~", 11, "middle")
T(MB - 8, 78, "UEDCL utility supply", 9, "end", "bold"); T(MB - 8, 90, "11 kV / 400 V transformer (existing)", 7.5, "end")
# CTs + zero-export meter
for j in range(3):
    add(f'<circle cx="{MB + j*6}" cy="240" r="5" fill="none" stroke="{GRY}" stroke-width="1"/>')
R(MX + 6, 226, 60, 28, "#7b4fa0", 1.3, "#f4eefa"); T(MX + 36, 244, "Smart meter", 7.5, "middle", "bold", color="#7b4fa0")
L(MX + 66, 240, MB - 6, 240, "#7b4fa0", 1, "4 3")
T(MX + 36, 268, "CTs 3 × 1500/5 A on incomer", 7.5, "middle", color="#7b4fa0")
T(MX + 36, 279, "(zero-export control)", 7.5, "middle", color="#7b4fa0")
# existing feeders
for k, yy in enumerate((560, 640, 720, 800)):
    for j, c in enumerate((RED, YEL, BLU, BLK)): L(MB + j * 6, yy + j * 5, MX + 230, yy + j * 5, GRY, 1)
    R(MB + 40, yy - 6, 14, 26, GRY, 1, "#fff"); L(MB + 42, yy + 12, MB + 52, yy, GRY, 1)
T(MB + 30, 538, "Existing feeders", 8, "start", color=GRY); T(MB + 30, 549, "to hotel loads", 8, "start", color=GRY)

# communication (EMS / logger)
R(CX + 30, 1000, 150, 40, "#7b4fa0", 1.3, "#f4eefa")
T(CX + 105, 1016, "Sigen data logger / EMS", 8.5, "middle", "bold", color="#7b4fa0")
T(CX + 105, 1030, "export limit = 0 kW, monitoring", 7.5, "middle", color="#7b4fa0")
PL([(MX + 44, 254), (MX + 100, 254), (MX + 100, 1020), (CX + 180, 1020)], "#7b4fa0", 1, "4 3")
PL([(CX + 30, 1020), (IX + IW / 2, 1020), (IX + IW / 2, INV[1]["iy1"])], "#7b4fa0", 1, "4 3")
PL([(IX + IW + 12, 1020), (IX + IW + 12, INV[0]["iy1"] - 30), (IX + IW, INV[0]["iy1"] - 30)], "#7b4fa0", 1, "4 3")
T(IX + IW + 18, 1012, "RS485 / Ethernet (STP 2 × 2 × 0.5 mm²)", 7.5, "start", color="#7b4fa0")

# ------------------------------------------------------------------ earthing
EY = 1110
L(60, EY, MX + 160, EY, GRN, 1.8)
earth(90, EY); T(90, EY + 38, "Earthing point (array)", 8, "middle")
earth(MX + 160, EY); T(MX + 160, EY + 38, "Main earth terminal (MET)", 8, "middle")
L(438, 1100, 438, EY, GRN, 1.2); L(438, INV[0]["top"] + 600 - 500 + 60, 438, 1100, GRN, 1.2)
L(IX + IW / 2, INV[1]["iy1"], IX + IW / 2, INV[1]["iy1"] + 6, GRN, 1)
PL([(IX + 10, INV[0]["iy1"]), (IX + 10, INV[0]["iy1"] + 20), (500, INV[0]["iy1"] + 20)], GRN, 1.1)
PL([(IX + 10, INV[1]["iy1"]), (IX + 10, EY)], GRN, 1.1)
PL([(CX + 75, 910), (CX + 75, EY)], GRN, 1.4)
T(270, EY - 6, "1C × 16 mm² Cu (G/Y) – frame & structure bonding", 8, "middle", color=GRN)
T(IX + 90, EY - 6, "1C × 25 mm² Cu (G/Y) – inverter earth", 8, "start", color=GRN)
T(CX + 230, EY - 6, "1C × 70 mm² Cu (G/Y) – ACCP to MET", 8, "start", color=GRN)

# ------------------------------------------------------------------ general notes / specifications
NX, NW = 1400, 250
R(NX, 40, NW, 760, BLK, 1.4, "#fff", 10)
T(NX + NW / 2, 60, "General Notes", 12, "middle", "bold")
L(NX + 10, 68, NX + NW - 10, 68)
notes = [
 ("", "This diagram shows the electrical schematic of the 185.4 kWp grid-tied solar PV system (zero export, no battery)."),
 ("1. PV modules", "Astronergy ASTRO N7 CHSM66RN(DG)/F-BH, 620 Wp bifacial; Voc 49.04 V, Isc 16.11 A, Vmp 41.56 V, Imp 14.92 A"),
 ("2. Strings", "INV-01: 8 × 19 = 152 (94.24 kWp); INV-02: 3 × 19 + 5 × 18 = 147 (91.14 kWp). Max string Voc ≈ 955 V (15 °C) < 1100 V"),
 ("3. Inverters", "2 × Sigenergy Sigen PV 80M1, 80 kW, 400 V 3N~; max AC current 133.7 A; 2 strings per MPPT (max 40 A/MPPT)"),
 ("4. DC cables", "1C × 6 mm² Cu H1Z2Z2-K, 1.5 kV DC, IEC 62930 / EN 50618, UV resistant"),
 ("5. AC cables", "C1, C2: 4C × 50 mm² Cu XLPE; C3: 4C × 120 mm² Cu XLPE/SWA, 0.6/1 kV, IEC 60502-1; VD < 2 %"),
 ("6. Earthing cables", "16 / 25 / 70 mm² Cu G/Y, 450/750 V, IEC 60364-5-54"),
 ("7. DC SPD (per string)", "Type 2, Ucpv 1100 V DC, In 20 kA, Imax 40 kA, Up ≤ 4.0 kV, IEC 61643-31"),
 ("8. DC isolator (per string)", "2-pole, 1200 V DC, 32 A, DC-PV2, IEC 60947-3, IP66 enclosure"),
 ("9. AC SPD (ACCP)", "Type 2, 4P (3P+N), Uc 320 Vac, In 20 kA, Imax 40 kA, Up ≤ 1.5 kV, IEC 61643-11"),
 ("10. AC protection", "Inverter MCCB 4P 160 A (Ir 140 A) 25 kA; ACCP Q1/Q2 MCCB 4P 160 A; Q3 & Q5 MCCB 4P 400 A (Ir 280 A) 25 kA"),
 ("11. Zero export", "Smart meter + 3 CTs on MLVS incomer → Sigen EMS limits inverter output to keep export = 0"),
 ("12. Solar system", "PV capacity 185.38 kWp DC; inverter capacity 2 × 80 kW = 160 kW AC; DC/AC 1.16"),
 ("13.", "Cable lengths indicative; confirm on site. Verify MLVS spare way, fault level and busbar rating before installation."),
]
y = 84
import textwrap
for head, body in notes:
    if head: T(NX + 10, y, head, 8.5, weight="bold"); y += 12
    for line in textwrap.wrap(body, 52):
        T(NX + (18 if head else 10), y, line, 8); y += 11
    y += 4

# legend
LY = y + 6
T(NX + 10, LY, "Legend", 9, weight="bold")
legend = [(RED, "DC + / L1"), (BLU, "DC − / L3"), (YEL, "L2"), (BLK, "N"), (GRN, "Earth (PE)"), ("#7b4fa0", "Comms / CT signal")]
for i, (c, t) in enumerate(legend):
    yy = LY + 14 + (i // 2) * 14; xx = NX + 10 + (i % 2) * 120
    L(xx, yy - 3, xx + 26, yy - 3, c, 2, "4 3" if c == "#7b4fa0" else None); T(xx + 32, yy, t, 8)

# title block
TY = 815
R(NX, TY, NW, 335, BLK, 1.4, "#fff", 10)
rows = [("Firm name & address", "NileSun Power Ltd, Kampala, Uganda", 46),
        ("Project name & address", "185.4 kWp Rooftop Solar PV – Kampala Marriott Hotel, mezzanine roof, Kampala", 58),
        ("Client", "Kampala Marriott Hotel", 34),
        ("Drawing title", "Single line diagram – PV system & grid connection", 46)]
yy = TY
for lab, val, hh in rows:
    L(NX, yy, NX + NW, yy); T(NX + 8, yy + 13, lab, 7.5, color="#555")
    for k, line in enumerate(textwrap.wrap(val, 44)): T(NX + 8, yy + 27 + k * 11, line, 8.5, weight="bold", color="#1f3f8f" if lab.startswith("Firm") else "#000")
    yy += hh
cells = [("Drawn by", "Mahil Fernando"), ("Drawing No", "PV-SLD-D18102-005"), ("Revision", "A"), ("Issue date", "09/11/2026"), ("Scale / size", "NTS / A3")]
for lab, val in cells:
    L(NX, yy, NX + NW, yy); L(NX + 90, yy, NX + 90, yy + 22)
    T(NX + 8, yy + 15, lab, 8); T(NX + 98, yy + 15, val, 8.5, weight="bold"); yy += 22
L(NX, yy, NX + NW, yy)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Arial, Helvetica, sans-serif">'
       f'<rect width="{W}" height="{H}" fill="#fff"/>' + "".join(g) + "</svg>")
open(os.path.join(HERE, "PV_SLD_Detailed.svg"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n' + svg)
open(os.path.join(HERE, "PV_SLD_Detailed.html"), "w").write(
    "<!doctype html><html><head><meta charset='utf-8'><title>PV SLD Detailed</title><style>@page{size:A3 landscape;margin:0}"
    "html,body{margin:0}svg{width:420mm;height:297mm;display:block}</style></head><body>" + svg + "</body></html>")
print("ok")
