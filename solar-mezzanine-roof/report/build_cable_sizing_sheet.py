"""Adds/rebuilds the 'AC Cable Sizing' sheet in the workings: ACCP -> MLVS feeder, Cu vs Al, per-inverter vs combined."""
import sys
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment
from openpyxl.formatting.rule import FormulaRule

path = sys.argv[1] if len(sys.argv) > 1 else "Kampala_Marriott_PV_Workings_P50_PVsyst.xlsx"
wb = load_workbook(path)
if "AC Cable Sizing" in wb.sheetnames: del wb["AC Cable Sizing"]
ws = wb.create_sheet("AC Cable Sizing", wb.sheetnames.index("DC & AC Earthing System") + 1)

FN = "Times New Roman"; NAVY = "FF14365D"
f = lambda **k: Font(name=FN, size=k.pop("size", 11), **k)
INP = PatternFill("solid", fgColor="FF92D050"); TOT = PatternFill("solid", fgColor="FFEEF2F6"); HDR = PatternFill("solid", fgColor=NAVY)
thin = Side(style="thin", color="FFBFC7D1"); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
BLUE = f(color="FF0000FF"); BLK = f(); GRN = f(color="FF008000")
def cell(a, v, font=BLK, fill=None, fmt=None, al=None, box=True):
    c = ws[a]; c.value = v; c.font = font
    if fill: c.fill = fill
    if fmt: c.number_format = fmt
    if al: c.alignment = al
    if box: c.border = BOX
    return c
def header(row, labels, col0=1):
    for i, t in enumerate(labels):
        c = ws.cell(row, col0 + i, t); c.font = f(b=True, color="FFFFFFFF"); c.fill = HDR; c.border = BOX
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[row].height = 45

ws["A1"] = "AC Cable Sizing – ACCP (roof) → MLVS, indoor duct"; ws["A1"].font = f(b=True, size=13, color=NAVY)
ws["A2"] = ("Checks current rating (IEC 60364-5-52, Method B2: multicore cable in conduit/trunking) and voltage drop for Cu and Al options. "
            "Green cells are inputs; everything else is calculated.")
ws["A2"].font = f(color="FF5B6673", size=10)

# ---------- 1. inputs ----------
ws["A4"] = "1. Design inputs"; ws["A4"].font = f(b=True, color=NAVY)
header(5, ["Parameter", "Value", "Unit", "Source / note"])
inputs = [
    ("Number of inverters", 2, "nos", "Sigen PV 80M1 × 2", "0"),
    ("Inverter nominal current @ 400 V", 115.9, "A", "Inverter datasheet (Annex 3): nominal output current @400 Vac", "0.0"),
    ("Inverter maximum current", 133.7, "A", "Inverter datasheet (Annex 3): max. output current @380/400 Vac (88 kVA)", "0.0"),
    ("Line voltage", 400, "V", "LV grid, 3-phase", "0"),
    ("Power factor (cos φ)", 1, "", "Inverters run at unity PF; reactance term neglected", "0.00"),
    ("Route length ACCP → MLVS (one way)", 300, "m", "Indoor duct route – user, Nov 2026", "0"),
    ("Voltage-drop limit", 0.03, "%", "Design target; keeps inverter voltage rise within trip margin", "0.0%"),
    ("Ambient temperature factor", 1.0, "", "Indoor duct ≈ 30 °C (IEC 60364-5-52 Table B.52.14). Use 0.91 for 40 °C", "0.00"),
    ("Grouping factor – 2 cables in one duct", 0.8, "", "IEC 60364-5-52 Table B.52.17, 2 circuits bunched", "0.00"),
    ("Per-inverter protection (MCCB)", 160, "A", "Next standard rating ≥ 133.7 A", "0"),
    ("Combined protection (MCCB)", 320, "A", "Next standard rating ≥ 2 × 133.7 = 267.4 A", "0"),
    ("Max. conductor temperature (XLPE)", 90, "°C", "Resistance corrected from 20 °C to 90 °C (conservative)", "0"),
]
for i, (p, v, u, n, fm) in enumerate(inputs):
    r = 6 + i
    cell(f"A{r}", p); cell(f"B{r}", v, BLUE, INP, fm, Alignment(horizontal="center")); cell(f"C{r}", u, al=Alignment(horizontal="center"))
    cell(f"D{r}", n, f(size=10, color="FF5B6673"))
N, INOM, IMAX, V, PF, L, VDL, KA, KG, INP1, INPC, TMAX = (f"$B${6+i}" for i in range(12))

r = 19; ws[f"A{r}"] = "Design currents"; ws[f"A{r}"].font = f(b=True, color=NAVY)
header(20, ["Circuit", "Nominal Ib (A)", "Maximum Ib (A)", "Protection In (A)"])
cell("A21", "Per inverter (one cable each)"); cell("B21", f"={INOM}", fmt="0.0"); cell("C21", f"={IMAX}", fmt="0.0"); cell("D21", f"={INP1}", fmt="0")
cell("A22", "Combined (one cable for both)"); cell("B22", f"={N}*{INOM}", fmt="0.0"); cell("C22", f"={N}*{IMAX}", fmt="0.0"); cell("D22", f"={INPC}", fmt="0")

# ---------- 2. cable library ----------
ws["A24"] = "2. Cable data (4-core XLPE/SWA)"; ws["A24"].font = f(b=True, color=NAVY)
header(25, ["Cable", "Material", "Size (mm²)", "R at 20 °C (Ω/km)", "α (1/°C)", "R at 90 °C (Ω/km)", "Iz Method B2 (A)", "Price (USD/m)"])
lib = [("Cu 95", "Cu", 95, 0.193, 210, None), ("Cu 120", "Cu", 120, 0.153, 240, None), ("Cu 150", "Cu", 150, 0.124, 270, 106),
       ("Cu 185", "Cu", 185, 0.0991, 300, None), ("Cu 240", "Cu", 240, 0.0754, 350, None),
       ("Al 150", "Al", 150, 0.206, 215, None), ("Al 185", "Al", 185, 0.164, 230, None), ("Al 240", "Al", 240, 0.125, 275, 146),
       ("Al 300", "Al", 300, 0.100, 310, None), ("Al 400", "Al", 400, 0.0778, 370, None)]
L0 = 26
for i, (k, m, s, r20, iz, pr) in enumerate(lib):
    r = L0 + i
    cell(f"A{r}", k, f(b=True)); cell(f"B{r}", m, al=Alignment(horizontal="center")); cell(f"C{r}", s, al=Alignment(horizontal="center"))
    cell(f"D{r}", r20, BLUE, INP, "0.0000"); cell(f"E{r}", f'=IF(B{r}="Cu",0.00393,0.00403)', fmt="0.00000")
    cell(f"F{r}", f"=D{r}*(1+E{r}*({TMAX}-20))", fmt="0.0000"); cell(f"G{r}", iz, BLUE, INP, "0")
    cell(f"H{r}", pr, BLUE, INP, "#,##0.00")
L1 = L0 + len(lib) - 1
ws[f"A{L1+1}"] = ("R20: IEC 60228 class 2 conductors. α: IEC 60228 temperature coefficients. Iz: approximate IEC 60364-5-52 Table B.52.5 (Cu) / B.52.5-Al, "
                 "XLPE, 3 loaded conductors, 30 °C – confirm with the cable maker's datasheet. Prices: Cu 150 and Al 240 from supplier notes; fill in the others.")
ws[f"A{L1+1}"].font = f(size=9, i=True, color="FF5B6673")
ws.merge_cells(f"A{L1+1}:M{L1+1}"); ws[f"A{L1+1}"].alignment = Alignment(wrap_text=True, vertical="top"); ws.row_dimensions[L1+1].height = 30

# ---------- 3. options ----------
O = L1 + 3
ws[f"A{O}"] = "3. Cable options – current rating and voltage drop"; ws[f"A{O}"].font = f(b=True, color=NAVY)
heads = ["Option", "Cable", "Circuits (runs)", "Length per run (m)", "Ib nominal (A)", "Ib max (A)", "Protection In (A)",
         "Iz table (A)", "Grouping factor", "Iz derated (A)", "Current check (Iz ≥ In ≥ Ib max)", "R 90 °C (Ω/km)",
         "Voltage drop (V)", "Voltage drop (%)", "VD check", "Power loss at nominal (kW)", "Total cable (m)", "Cable cost (USD)", "Result"]
header(O + 1, heads)
opts = [("Per inverter", k, 2) for k in ["Cu 95", "Cu 120", "Cu 150", "Al 185", "Al 240"]] + \
       [("Combined", k, 1) for k in ["Cu 150", "Cu 185", "Cu 240", "Al 240", "Al 300", "Al 400"]]
lk = lambda col, r: f"INDEX(${col}${L0}:${col}${L1},MATCH($B{r},$A${L0}:$A${L1},0))"
for i, (opt, k, n) in enumerate(opts):
    r = O + 2 + i; per = opt == "Per inverter"
    vals = [opt, k, n, f"={L}",
            "=$B$21" if per else "=$B$22", "=$C$21" if per else "=$C$22", "=$D$21" if per else "=$D$22",
            f"={lk('G', r)}", f"=IF(C{r}>1,{KG},1)", f"=H{r}*I{r}*{KA}",
            f'=IF(AND(J{r}>=G{r},G{r}>=F{r}),"OK","FAIL")', f"={lk('F', r)}",
            f"=SQRT(3)*E{r}*D{r}/1000*L{r}*{PF}", f"=M{r}/{V}", f'=IF(N{r}<={VDL},"OK","FAIL")',
            f"=C{r}*3*E{r}^2*L{r}*D{r}/1000/1000", f"=C{r}*D{r}", f'=IF({lk("H", r)}="","price needed",Q{r}*{lk("H", r)})',
            f'=IF(AND(K{r}="OK",O{r}="OK"),"SUITABLE","NOT SUITABLE")']
    fmts = [None, None, "0", "0", "0.0", "0.0", "0", "0", "0.00", "0", None, "0.0000", "0.0", "0.0%", None, "0.00", "#,##0", "#,##0", None]
    for j, (v, fm) in enumerate(zip(vals, fmts)):
        c = ws.cell(r, j + 1, v); c.font = BLUE if j in (0, 1, 2) else BLK; c.border = BOX
        if j in (0, 1, 2): c.fill = INP
        if fm: c.number_format = fm
        c.alignment = Alignment(horizontal="left" if j == 0 else "center")
    ws.cell(r, 19).font = f(b=True)
R0, R1 = O + 2, O + 1 + len(opts)
red = PatternFill("solid", fgColor="FFF8D7DA"); grn = PatternFill("solid", fgColor="FFD4EDDA")
for col in "KOS":
    rng = f"{col}{R0}:{col}{R1}"
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f'ISNUMBER(SEARCH("NOT",{col}{R0}))'], fill=red))
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f'ISNUMBER(SEARCH("FAIL",{col}{R0}))'], fill=red))
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f'OR({col}{R0}="OK",{col}{R0}="SUITABLE")'], fill=grn))

n0 = R1 + 2
notes = ["Formulas:",
         "  Current check: Iz derated = Iz table × grouping factor × ambient factor; must satisfy Ib max ≤ In ≤ Iz derated (IEC 60364-4-43).",
         "  Voltage drop (V) = √3 × Ib nominal × L (km) × R90 × cos φ  (3-phase, reactance neglected at cos φ = 1); % = V ÷ line voltage.",
         "  Power loss (kW) = runs × 3 × Ib² × R90 × L (km) ÷ 1000 – at full nominal output; annual energy loss is roughly 40 % of this × full-load hours.",
         "  R90 = R20 × (1 + α × (90 − 20)) – conservative; real conductor temperature is lower, so actual drop is a little smaller.",
         "Recommendation (300 m): 2 × 4C × 120 mm² Cu (one per inverter) or 2 × 4C × 240 mm² Al; single-cable option only 4C × 240 mm² Cu.",
         "Armour (SWA) used as protective earth – bond at both ends; verify fault-loop impedance / disconnection time for the final length.",
         "Aluminium: bimetallic (Al–Cu) lugs with contact grease at copper busbars; re-torque after one month."]
for i, t in enumerate(notes):
    c = ws[f"A{n0+i}"]; c.value = t; c.font = f(size=10, b=(i in (0, 5)), color=NAVY if i == 5 else "FF333333")

widths = {"A": 34, "B": 12, "C": 11, "D": 13, "E": 11, "F": 11, "G": 12, "H": 11, "I": 10, "J": 11, "K": 15, "L": 11, "M": 11, "N": 11, "O": 10, "P": 12, "Q": 11, "R": 13, "S": 15}
for k, w in widths.items(): ws.column_dimensions[k].width = w
ws.column_dimensions["D"].width = 13
for r in range(6, 18): ws.row_dimensions[r].height = 16
ws.freeze_panes = "A4"
ws.sheet_view.zoomScale = 90
wb.save(path); print("saved", path, "options rows", R0, R1)
