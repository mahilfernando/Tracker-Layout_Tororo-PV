"""Compare the PVsyst V8.1.8 simulation (VC0, 09/11/26) with the initial desktop generation estimate.
Output: PVsyst_vs_Initial_Generation.xlsx (formulas + charts)."""
import os, json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, LineChart, Reference

HERE = os.path.dirname(os.path.abspath(__file__))
mon = json.load(open(os.path.join(HERE, "monthly.json")))["rows"]
fin = json.load(open(os.path.join(HERE, "proposal_fin_v2.json")))
# PVsyst monthly table (page 4): GlobHor, GlobInc, E_Grid, PR
PV = [("Jan", 163.9, 174.4, 27523, 0.851), ("Feb", 155.8, 161.5, 25387, 0.848), ("Mar", 170.3, 170.2, 26942, 0.854),
      ("Apr", 146.6, 141.3, 22443, 0.857), ("May", 152.4, 142.3, 22628, 0.858), ("Jun", 147.4, 135.0, 21387, 0.855),
      ("Jul", 158.5, 145.4, 23038, 0.855), ("Aug", 160.2, 152.1, 24154, 0.857), ("Sep", 159.5, 157.0, 24885, 0.855),
      ("Oct", 155.5, 158.1, 24993, 0.853), ("Nov", 138.1, 144.3, 22933, 0.857), ("Dec", 146.8, 156.1, 24738, 0.855)]

NAVY, BAND, YEL = "14365D", "EEF2F6", "FFF2CC"
thin = Side(style="thin", color="9AA4AE"); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
def F(**k): return Font(name="Arial", **({"size": 10} | k))
def hdr(ws, r, vals):
    for c, v in enumerate(vals, 1):
        x = ws.cell(r, c, v); x.font = F(bold=True, color="FFFFFF"); x.fill = PatternFill("solid", fgColor=NAVY)
        x.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True); x.border = BOX
def cellv(ws, r, c, v, fmt=None, bold=False, fill=None, color=None):
    x = ws.cell(r, c, v); x.border = BOX; x.font = F(bold=bold, color=color) if color else F(bold=bold)
    if fmt: x.number_format = fmt
    if fill: x.fill = PatternFill("solid", fgColor=fill)
    return x

wb = Workbook()
# ---------------- Sheet 1: monthly comparison ----------------
ws = wb.active; ws.title = "Monthly comparison"
ws["A1"] = "PVsyst simulation vs initial generation estimate – Kampala Marriott 185.4 kWp"; ws["A1"].font = F(bold=True, size=13, color=NAVY)
ws["A2"] = "PVsyst V8.1.8 (trial) · Meteonorm 9.0 · tilt 10°, azimuth 0° · 299 × CHSM66RN(DG)/F-BH-620 · 2 × 80M1 · no shading · simulated 09/11/2026"
ws["A2"].font = F(italic=True, size=9, color="5B6673")
hdr(ws, 4, ["Month", "GHI – initial (kWh/m²)", "GHI – PVsyst (kWh/m²)", "Plane irradiation – PVsyst (kWh/m²)",
            "Generation – initial estimate (kWh)", "Generation – PVsyst E_Grid (kWh)", "Difference (kWh)", "Difference (%)", "PR – PVsyst"])
ws.row_dimensions[4].height = 45
for i, (m, pv) in enumerate(zip(mon, PV)):
    r = 5 + i
    cellv(ws, r, 1, m["m"]); cellv(ws, r, 2, f"={m['ghi']}*{m['days']}", "0.0")
    cellv(ws, r, 3, pv[1], "0.0", fill=YEL); cellv(ws, r, 4, pv[2], "0.0", fill=YEL)
    cellv(ws, r, 5, round(m["kwh"]), "#,##0"); cellv(ws, r, 6, pv[3], "#,##0", fill=YEL)
    cellv(ws, r, 7, f"=F{r}-E{r}", '#,##0;[Red]-#,##0'); cellv(ws, r, 8, f"=F{r}/E{r}-1", '0.0%;[Red]-0.0%'); cellv(ws, r, 9, pv[4], "0.0%", fill=YEL)
r = 17
cellv(ws, r, 1, "Year", bold=True, fill=BAND)
for c, col in ((2, "B"), (3, "C"), (4, "D"), (5, "E"), (6, "F"), (7, "G")):
    cellv(ws, r, c, f"=SUM({col}5:{col}16)", "#,##0" if c >= 5 else "#,##0.0", bold=True, fill=BAND)
cellv(ws, r, 8, "=F17/E17-1", "0.0%", bold=True, fill=BAND); cellv(ws, r, 9, 0.8544, "0.0%", bold=True, fill=BAND)
rows = [("Specific yield (kWh/kWp/yr)", "=E17/185.38", "=F17/185.38", "#,##0"),
        ("Average per month (kWh)", "=E17/12", "=F17/12", "#,##0"),
        ("Average per day (kWh)", "=E17/365", "=F17/365", "#,##0"),
        ("Performance ratio (yield ÷ plane irradiation)", "=E17/185.38/D17", "=I17", "0.0%"),
        ("Best month ÷ worst month", "=MAX(E5:E16)/MIN(E5:E16)", "=MAX(F5:F16)/MIN(F5:F16)", "0.00")]
hdr(ws, 19, ["Indicator", "", "", "", "Initial estimate", "PVsyst", "Difference", "", ""])
for i, (lab, a, b, fmt) in enumerate(rows):
    rr = 20 + i
    cellv(ws, rr, 1, lab); ws.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=4)
    cellv(ws, rr, 5, a, fmt); cellv(ws, rr, 6, b, fmt)
    cellv(ws, rr, 7, f"=F{rr}-E{rr}" if fmt != "0.0%" else f"=F{rr}-E{rr}", fmt)
for col, w in zip("ABCDEFGHI", (10, 14, 14, 16, 18, 18, 14, 12, 11)): ws.column_dimensions[col].width = w
ch = BarChart(); ch.type = "col"; ch.title = "Monthly generation – initial estimate vs PVsyst (kWh)"; ch.y_axis.title = "kWh"
ch.add_data(Reference(ws, min_col=5, max_col=6, min_row=4, max_row=16), titles_from_data=True)
ch.set_categories(Reference(ws, min_col=1, min_row=5, max_row=16)); ch.height = 8.5; ch.width = 22
ch.y_axis.majorGridlines = None; ch.y_axis.delete = False; ch.x_axis.delete = False
ws.add_chart(ch, "K4")
ln = LineChart(); ln.title = "Global horizontal irradiation (kWh/m²/month)"
ln.add_data(Reference(ws, min_col=2, max_col=3, min_row=4, max_row=16), titles_from_data=True)
ln.set_categories(Reference(ws, min_col=1, min_row=5, max_row=16)); ln.height = 7.5; ln.width = 22
ln.y_axis.delete = False; ln.x_axis.delete = False
ws.add_chart(ln, "K22")

# ---------------- Sheet 2: assumptions / losses ----------------
w2 = wb.create_sheet("Assumptions & losses")
w2["A1"] = "Why the two estimates differ"; w2["A1"].font = F(bold=True, size=13, color=NAVY)
hdr(w2, 3, ["Item", "Initial estimate (Excel)", "PVsyst VC0", "Comment"])
items = [
    ("Weather data", "Typical Kampala GHI (desktop), 1,827 kWh/m²/yr", "Meteonorm 9.0 synthetic, 1,855 kWh/m²/yr", "PVsyst GHI 1.5 % higher"),
    ("Method", "kWp × specific yield 1,480 kWh/kWp", "Hourly simulation (Perez transposition)", ""),
    ("Performance ratio", "≈ 0.80 (assumed, all losses)", "0.854 (simulated)", "Main reason for the 6 % difference"),
    ("Shading (row-to-row, parapet, tower)", "included in PR 0.80", "Not modelled – 'no 3D scene, no shadings'", "Tower and parapet shading will reduce PVsyst output"),
    ("Soiling (dust)", "included in PR 0.80", "Not modelled (0 %)", "Typically 2–3 % in Kampala (dry seasons, urban dust)"),
    ("Thermal model", "included in PR 0.80", "Uc = 20 W/m²K → −6.7 % temperature loss", "Conservative for an open ballast structure (Uc 29 typical)"),
    ("Module quality / LID", "included in PR 0.80", "+0.75 % quality gain, no LID", "Optimistic – use 0 % quality gain"),
    ("Bifacial rear gain", "not included", "not included (front-side only)", "Could add ≈ 2–4 % on a light roof"),
    ("String layout", "16 strings: 8 × 19 + 3 × 19 + 5 × 18", "23 strings × 13 modules", "Update PVsyst to the design stringing (19/18 in series)"),
    ("AC losses (ACCP → MLVS cable)", "included in PR 0.80", "Not modelled (output at inverter)", "≈ 1–2 % with the long C3 run"),
    ("Availability / downtime", "included in PR 0.80", "Not modelled", "≈ 1 % typical"),
    ("Degradation", "1 % year 1, then 0.4 %/yr", "Year-1 nominal (no degradation)", "Compare year-1 figures only"),
    ("Software licence", "–", "PVsyst TRIAL / evaluation mode", "Run with a licensed copy for the issued report"),
]
for i, row in enumerate(items):
    for c, v in enumerate(row, 1):
        x = cellv(w2, 4 + i, c, v); x.alignment = Alignment(wrap_text=True, vertical="center")
for col, w in zip("ABCD", (34, 38, 40, 50)): w2.column_dimensions[col].width = w

r0 = 4 + len(items) + 2
w2.cell(r0, 1, "Adjusted PVsyst estimate (adding the losses PVsyst left out)").font = F(bold=True, size=11, color=NAVY)
hdr(w2, r0 + 1, ["Step", "Factor", "Energy (kWh/yr)", "Note"])
adj = [("PVsyst E_Grid (as simulated)", None, "='Monthly comparison'!F17", "page 4 of the report"),
       ("Soiling", 0.02, None, "edit"), ("Near shading (tower / parapet / rows)", 0.02, None, "edit – confirm with a 3D scene"),
       ("AC cable losses to MLVS", 0.01, None, "edit"), ("Availability", 0.01, None, "edit"),
       ("Remove module quality gain", 0.0075, None, "PVsyst +0.75 %")]
for i, (lab, f_, val, note) in enumerate(adj):
    r = r0 + 2 + i
    cellv(w2, r, 1, lab)
    if f_ is None:
        cellv(w2, r, 3, val, "#,##0")
    else:
        cellv(w2, r, 2, f_, "0.0%", fill=YEL); cellv(w2, r, 3, f"=C{r-1}*(1-B{r})", "#,##0")
    cellv(w2, r, 4, note)
rl = r0 + 2 + len(adj) - 1
cellv(w2, rl + 1, 1, "Adjusted PVsyst year-1 generation", bold=True, fill=BAND); cellv(w2, rl + 1, 3, f"=C{rl}", "#,##0", bold=True, fill=BAND)
cellv(w2, rl + 2, 1, "Initial estimate (proposal / workings)", bold=True, fill=BAND); cellv(w2, rl + 2, 3, "='Monthly comparison'!E17", "#,##0", bold=True, fill=BAND)
cellv(w2, rl + 3, 1, "Adjusted PVsyst vs initial", bold=True, fill=BAND); cellv(w2, rl + 3, 3, f"=C{rl+1}/C{rl+2}-1", "0.0%", bold=True, fill=BAND)

# ---------------- Sheet 3: financial impact ----------------
w3 = wb.create_sheet("Financial impact")
w3["A1"] = "Year-1 financial effect of the generation basis (tariff USD 0.07/kWh, Total Project Value USD 102,789)"
w3["A1"].font = F(bold=True, size=12, color=NAVY)
hdr(w3, 3, ["Case", "Year-1 generation (kWh)", "Year-1 savings (USD)", "Simple payback (yrs, approx.)", "Specific yield (kWh/kWp)"])
cases = [("Initial estimate (used in proposal)", "='Monthly comparison'!E17"),
         ("PVsyst as simulated", "='Monthly comparison'!F17"),
         ("PVsyst adjusted (soiling, shading, AC, availability)", f"='Assumptions & losses'!C{rl+1}")]
w3["H3"] = "Tariff (USD/kWh)"; w3["I3"] = fin["tar"]; w3["H4"] = "Investment (USD)"; w3["I4"] = round(fin["capex"], 2)
w3["H5"] = "Escalation"; w3["I5"] = 0.02
for c in ("I3", "I4", "I5"): w3[c].fill = PatternFill("solid", fgColor=YEL)
for i, (lab, g) in enumerate(cases):
    r = 4 + i
    cellv(w3, r, 1, lab); cellv(w3, r, 2, g, "#,##0"); cellv(w3, r, 3, f"=B{r}*$I$3", "#,##0")
    cellv(w3, r, 4, f"=LN(1+$I$4*$I$5/C{r})/LN(1+$I$5)", "0.0"); cellv(w3, r, 5, f"=B{r}/185.38", "#,##0")
w3.cell(8, 1, "Payback = years for savings rising 2 %/yr to repay the investment (degradation ignored, so ≈ 0.1 yr shorter than the full 25-year model in the workings).").font = F(italic=True, size=9, color="5B6673")
for col, w in zip("ABCDEFGHI", (48, 20, 18, 20, 18, 4, 4, 18, 12)): w3.column_dimensions[col].width = w

out = os.path.join(HERE, "PVsyst_vs_Initial_Generation.xlsx"); wb.save(out); print(out)
