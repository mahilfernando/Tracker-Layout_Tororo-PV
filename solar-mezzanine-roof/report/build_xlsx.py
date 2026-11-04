"""Excel workbook of the estimated PV generation (inputs, monthly split + chart, 25-year profile + chart)."""
import os
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.comments import Comment
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

HERE = os.path.dirname(os.path.abspath(__file__))
F = "Arial"
BLUE = Font(name=F, color="0000FF"); BLK = Font(name=F); BOLD = Font(name=F, bold=True)
HEAD = Font(name=F, bold=True, color="FFFFFF"); TITLE = Font(name=F, bold=True, size=14, color="14365D")
NOTE = Font(name=F, italic=True, size=9, color="5B6673")
HFILL = PatternFill("solid", fgColor="14365D"); BAND = PatternFill("solid", fgColor="EEF2F6")
YEL = PatternFill("solid", fgColor="FFFF00")
thin = Side(style="thin", color="C9D0D8"); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)

wb = Workbook()
# ---------------- Inputs ----------------
ws = wb.active; ws.title = "Inputs"
ws["A1"] = "Rooftop Solar PV – Estimated Generation Inputs"; ws["A1"].font = TITLE
ws["A2"] = "Kampala Marriott Hotel – mezzanine roof · 0°18'11.34\"N, 32°35'13.76\"E"; ws["A2"].font = NOTE
rows = [
    ("Number of modules", 299, "nos", "0", "Layout PV-LAY-D18102-002 (13 rows × 23)"),
    ("Module rating", 620, "Wp", "0", "620 Wp bifacial TOPCon, 2382 × 1134 mm"),
    ("Plant capacity", "=B4*B5/1000", "kWp", "0.0", "Formula"),
    ("Specific yield (year 1)", 1480, "kWh/kWp/yr", "#,##0", "Desktop estimate incl. ≈0.80 performance ratio; confirm with PVsyst"),
    ("Year-1 generation", "=B6*B7", "kWh", "#,##0", "Formula"),
    ("Degradation, year 1", 0.01, "", "0.0%", "Typical TOPCon warranty"),
    ("Degradation, year 2 onward", 0.004, "per year", "0.0%", "Typical TOPCon warranty"),
    ("Hotel consumption", 12000000, "kWh/yr", "#,##0", "≈1,000,000 kWh/month (client)"),
    ("Share of hotel consumption", "=B8/B11", "", "0.0%", "Formula"),
]
for c, h in zip("ABCD", ["Parameter", "Value", "Unit", "Source / note"]):
    ws[f"{c}3"] = h; ws[f"{c}3"].font = HEAD; ws[f"{c}3"].fill = HFILL
for i, (p, v, u, fmt, src) in enumerate(rows, start=4):
    ws[f"A{i}"] = p; ws[f"B{i}"] = v; ws[f"C{i}"] = u; ws[f"D{i}"] = src
    ws[f"B{i}"].number_format = fmt
    is_input = not (isinstance(v, str) and v.startswith("="))
    ws[f"B{i}"].font = BLUE if is_input else BLK
    if is_input: ws[f"B{i}"].fill = YEL
    for c in "ABCD":
        ws[f"{c}{i}"].border = BOX
        if c != "B": ws[f"{c}{i}"].font = Font(name=F)
ws["A15"] = "Legend: yellow cells with blue text are inputs you can change; black values are formulas."; ws["A15"].font = NOTE
for col, w in zip("ABCD", [30, 14, 13, 62]): ws.column_dimensions[col].width = w

# ---------------- Monthly ----------------
m = wb.create_sheet("Monthly Generation")
m["A1"] = "Estimated Monthly PV Generation – Year 1"; m["A1"].font = TITLE
m["A2"] = ("Monthly shape from typical Kampala global horizontal irradiation (long-term climatology, approx.); "
           "annual total from Inputs!B8. PVGIS/NASA data could not be fetched – replace column C with PVGIS/PVsyst values when available."); m["A2"].font = NOTE
hdr = ["Month", "Days", "GHI (kWh/m²/day)", "Weight (GHI × days)", "Share of year", "Generation (kWh)", "Generation (MWh)", "Average (kWh/day)"]
for j, h in enumerate(hdr):
    c = m.cell(row=4, column=j + 1, value=h); c.font = HEAD; c.fill = HFILL
    c.alignment = Alignment(wrap_text=True, horizontal="center", vertical="center")
m.row_dimensions[4].height = 32
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
ghi = [5.4, 5.6, 5.4, 5.0, 4.7, 4.6, 4.5, 4.8, 5.1, 5.0, 4.9, 5.1]
for i, (mo, dd, g) in enumerate(zip(months, days, ghi)):
    r = 5 + i
    m[f"A{r}"] = mo; m[f"B{r}"] = dd; m[f"C{r}"] = g
    m[f"D{r}"] = f"=B{r}*C{r}"
    m[f"E{r}"] = f"=D{r}/$D$17"
    m[f"F{r}"] = f"=Inputs!$B$8*E{r}"
    m[f"G{r}"] = f"=F{r}/1000"
    m[f"H{r}"] = f"=F{r}/B{r}"
    m[f"C{r}"].font = BLUE; m[f"C{r}"].fill = YEL
    for col in "ABDEFGH": m[f"{col}{r}"].font = Font(name=F)
    m[f"F{r}"].font = Font(name=F, color="000000")
m["C5"].comment = Comment("Typical Kampala GHI, kWh/m²/day (approx. long-term climatology). Edit to PVGIS / PVsyst monthly values.", "PV design")
r = 17
m[f"A{r}"] = "Year"; m[f"B{r}"] = "=SUM(B5:B16)"; m[f"C{r}"] = "=SUMPRODUCT(B5:B16,C5:C16)/B17"
m[f"D{r}"] = "=SUM(D5:D16)"; m[f"E{r}"] = "=SUM(E5:E16)"; m[f"F{r}"] = "=SUM(F5:F16)"
m[f"G{r}"] = "=SUM(G5:G16)"; m[f"H{r}"] = "=F17/B17"
m["A18"] = "Monthly average"; m["F18"] = "=F17/12"; m["G18"] = "=G17/12"
for rr in (17, 18):
    for col in "ABCDEFGH":
        m[f"{col}{rr}"].font = BOLD; m[f"{col}{rr}"].fill = BAND
fmts = {"B": "0", "C": "0.00", "D": "0.0", "E": "0.0%", "F": "#,##0", "G": "0.0", "H": "#,##0"}
for rr in range(5, 19):
    for col, f in fmts.items(): m[f"{col}{rr}"].number_format = f
    for col in "ABCDEFGH": m[f"{col}{rr}"].border = BOX
for col, w in zip("ABCDEFGH", [16, 8, 14, 14, 12, 16, 14, 14]): m.column_dimensions[col].width = w

ch = BarChart(); ch.type = "col"; ch.style = 10
ch.title = "Estimated Monthly PV Generation – Year 1 (185.4 kWp)"
ch.y_axis.title = "MWh per month"; ch.x_axis.title = None
ch.add_data(Reference(m, min_col=7, min_row=4, max_row=16), titles_from_data=True)
ch.set_categories(Reference(m, min_col=1, min_row=5, max_row=16))
ch.legend = None; ch.gapWidth = 60; ch.height = 9; ch.width = 20
ch.y_axis.scaling.min = 0; ch.y_axis.majorGridlines = ch.y_axis.majorGridlines
ch.y_axis.delete = False; ch.x_axis.delete = False
s = ch.series[0]; s.graphicalProperties.solidFill = "14365D"; s.graphicalProperties.line.solidFill = "14365D"
s.dLbls = DataLabelList(); s.dLbls.showVal = True; s.dLbls.numFmt = "0.0"
s.dLbls.showSerName = s.dLbls.showCatName = s.dLbls.showLegendKey = False
m.add_chart(ch, "J4")

# ---------------- 25-year ----------------
y = wb.create_sheet("25-Year Generation")
y["A1"] = "Estimated Annual PV Generation – 25 Years"; y["A1"].font = TITLE
for j, h in enumerate(["Year", "Generation (kWh)", "Generation (MWh)", "Cumulative (MWh)"]):
    c = y.cell(row=3, column=j + 1, value=h); c.font = HEAD; c.fill = HFILL; c.alignment = Alignment(horizontal="center", wrap_text=True)
for k in range(1, 26):
    r = 3 + k
    y[f"A{r}"] = str(k)
    y[f"B{r}"] = "=Inputs!$B$8" if k == 1 else f"=Inputs!$B$8*(1-Inputs!$B$9)*(1-Inputs!$B$10)^(A{r}-1)"
    y[f"C{r}"] = f"=B{r}/1000"
    y[f"D{r}"] = f"=C{r}" if k == 1 else f"=D{r-1}+C{r}"
    y[f"A{r}"].alignment = Alignment(horizontal="center")
    for col, f in zip("BCD", ["#,##0", "0.0", "#,##0"]): y[f"{col}{r}"].number_format = f
    for col in "ABCD": y[f"{col}{r}"].border = BOX; y[f"{col}{r}"].font = Font(name=F)
y["A29"] = "Total"; y["B29"] = "=SUM(B4:B28)"; y["C29"] = "=SUM(C4:C28)"
for col in "ABCD": y[f"{col}29"].font = BOLD; y[f"{col}29"].fill = BAND; y[f"{col}29"].border = BOX
y["B29"].number_format = "#,##0"; y["C29"].number_format = "#,##0"
y["A30"] = "Year 1 uses Inputs!B8; later years apply the year-1 loss plus the yearly rate (same basis as the report)."; y["A30"].font = NOTE
for col, w in zip("ABCD", [8, 18, 16, 16]): y.column_dimensions[col].width = w
lc = LineChart(); lc.title = "Annual PV Generation (MWh)"; lc.y_axis.title = "MWh per year"; lc.x_axis.title = "Year"
lc.add_data(Reference(y, min_col=3, min_row=3, max_row=28), titles_from_data=True)
lc.set_categories(Reference(y, min_col=1, min_row=4, max_row=28))
lc.legend = None; lc.height = 9; lc.width = 20; lc.y_axis.delete = False; lc.x_axis.delete = False
lc.series[0].graphicalProperties.line.solidFill = "14365D"; lc.series[0].graphicalProperties.line.width = 28000
lc.series[0].smooth = False
lc.y_axis.scaling.min = 0; lc.y_axis.scaling.max = 300
y.add_chart(lc, "F3")
for sh in wb.worksheets:
    sh.page_setup.orientation = "landscape"; sh.page_setup.fitToWidth = 1; sh.page_setup.fitToHeight = 1
    sh.sheet_properties.pageSetUpPr.fitToPage = True

out = os.path.join(HERE, "PV_Generation_Estimate.xlsx")
wb.save(out); print(out)
