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

# ---------------- TOU impact ----------------
import json
tou = json.load(open(os.path.join(HERE, "tou.json")))
pv_frac = [v / sum(tou["pv_h"]) for v in tou["pv_h"]]
load_frac = [v / sum(tou["load_h"]) for v in tou["load_h"]]
t = wb.create_sheet("TOU Impact")
t["A1"] = "Solar Impact on Time-of-Use Tariff – Average Day"; t["A1"].font = TITLE
t["A2"] = ("Bands per Uganda ERA TOU structure; rates indicative (USD/kWh) – replace with the hotel's bill. "
           "Hourly shares: solar from site sun times (sunrise ≈06:50, sunset ≈18:56); load from an assumed hotel profile."); t["A2"].font = NOTE
for j, h in enumerate(["Tariff period", "Start hour", "End hour", "Rate (USD/kWh)"]):
    c = t.cell(row=4, column=j + 1, value=h); c.font = HEAD; c.fill = HFILL
for i, (n, a, b, r) in enumerate([("Off-peak", 0, 6, 0.07), ("Shoulder", 6, 18, 0.12), ("Peak", 18, 24, 0.15)]):
    rr = 5 + i
    t[f"A{rr}"] = n; t[f"B{rr}"] = a; t[f"C{rr}"] = b; t[f"D{rr}"] = r
    for col in "BCD": t[f"{col}{rr}"].font = BLUE; t[f"{col}{rr}"].fill = YEL
    t[f"A{rr}"].font = Font(name=F); t[f"D{rr}"].number_format = "0.000"
    for col in "ABCD": t[f"{col}{rr}"].border = BOX
# hourly table
hh = ["Hour", "Period", "Solar share of day", "Load share of day", "Solar (kWh/day)", "Hotel load (kWh/day)", "Grid after solar (kWh/day)", "Rate (USD/kWh)"]
for j, h in enumerate(hh):
    c = t.cell(row=10, column=j + 1, value=h); c.font = HEAD; c.fill = HFILL; c.alignment = Alignment(wrap_text=True, horizontal="center")
t.row_dimensions[10].height = 32
for h in range(24):
    r = 11 + h
    t[f"A{r}"] = f"{h:02d}:00"
    t[f"B{r}"] = f'=IF({h}<$C$5,$A$5,IF({h}<$C$6,$A$6,$A$7))'
    t[f"C{r}"] = round(pv_frac[h], 6); t[f"D{r}"] = round(load_frac[h], 6)
    t[f"E{r}"] = f"=Inputs!$B$8/365*C{r}"
    t[f"F{r}"] = f"=Inputs!$B$11/365*D{r}"
    t[f"G{r}"] = f"=F{r}-E{r}"
    t[f"H{r}"] = f"=INDEX($D$5:$D$7,MATCH(B{r},$A$5:$A$7,0))"
    for col, f in zip("CDEFGH", ["0.00%", "0.00%", "#,##0.0", "#,##0", "#,##0", "0.000"]): t[f"{col}{r}"].number_format = f
    for col in "ABCDEFGH": t[f"{col}{r}"].border = BOX; t[f"{col}{r}"].font = Font(name=F)
t["A35"] = "Day total"; t["C35"] = "=SUM(C11:C34)"; t["D35"] = "=SUM(D11:D34)"
for col in "EFG": t[f"{col}35"] = f"=SUM({col}11:{col}34)"
for col in "ABCDEFGH": t[f"{col}35"].font = BOLD; t[f"{col}35"].fill = BAND; t[f"{col}35"].border = BOX
for col, f in zip("CDEFG", ["0.0%", "0.0%", "#,##0", "#,##0", "#,##0"]): t[f"{col}35"].number_format = f
# summary by period (annual)
sh = ["Period", "Hotel use (MWh/yr)", "Solar (MWh/yr)", "Share of solar", "Grid after solar (MWh/yr)", "Reduction", "Cost before (USD/yr)", "Cost after (USD/yr)", "Saving (USD/yr)"]
for j, h in enumerate(sh):
    c = t.cell(row=37, column=j + 1, value=h); c.font = HEAD; c.fill = HFILL; c.alignment = Alignment(wrap_text=True, horizontal="center")
t.row_dimensions[37].height = 32
for i in range(3):
    r = 38 + i; src = 5 + i
    t[f"A{r}"] = f"=A{src}"
    t[f"B{r}"] = f"=SUMIF($B$11:$B$34,A{r},$F$11:$F$34)*365/1000"
    t[f"C{r}"] = f"=SUMIF($B$11:$B$34,A{r},$E$11:$E$34)*365/1000"
    t[f"D{r}"] = f"=IF($C$41=0,0,C{r}/$C$41)"
    t[f"E{r}"] = f"=B{r}-C{r}"
    t[f"F{r}"] = f"=IF(B{r}=0,0,C{r}/B{r})"
    t[f"G{r}"] = f"=B{r}*1000*D{src}"
    t[f"H{r}"] = f"=E{r}*1000*D{src}"
    t[f"I{r}"] = f"=G{r}-H{r}"
t["A41"] = "Total"
for col in "BCEGHI": t[f"{col}41"] = f"=SUM({col}38:{col}40)"
t["D41"] = "=SUM(D38:D40)"; t["F41"] = "=IF(B41=0,0,C41/B41)"
t["A42"] = "Bill reduction"; t["I42"] = "=IF(G41=0,0,I41/G41)"
t["A43"] = "Value per solar kWh (USD)"; t["I43"] = "=IF(C41=0,0,I41/(C41*1000))"
for r in range(38, 44):
    for col, f in zip("BCDEFGHI", ["#,##0", "#,##0.0", "0.0%", "#,##0", "0.00%", "#,##0", "#,##0", "#,##0"]):
        t[f"{col}{r}"].number_format = f
    for col in "ABCDEFGHI":
        t[f"{col}{r}"].border = BOX
        t[f"{col}{r}"].font = BOLD if r >= 41 else Font(name=F)
        if r >= 41: t[f"{col}{r}"].fill = BAND
t["I42"].number_format = "0.00%"; t["I43"].number_format = "0.000"
for col, w in zip("ABCDEFGHI", [16, 14, 13, 13, 14, 16, 16, 15, 14]): t.column_dimensions[col].width = w
c1 = BarChart(); c1.type = "col"; c1.title = "Average-Day Solar Generation by Hour (kWh)"
c1.add_data(Reference(t, min_col=5, min_row=10, max_row=34), titles_from_data=True)
c1.set_categories(Reference(t, min_col=1, min_row=11, max_row=34))
c1.legend = None; c1.gapWidth = 40; c1.height = 8; c1.width = 20; c1.y_axis.title = "kWh in each hour"
c1.y_axis.delete = False; c1.x_axis.delete = False; c1.y_axis.scaling.min = 0
c1.series[0].graphicalProperties.solidFill = "EDA100"; c1.series[0].graphicalProperties.line.solidFill = "EDA100"
t.add_chart(c1, "K4")
c2 = BarChart(); c2.type = "bar"; c2.title = "Reduction of Grid Energy by Tariff Period"
c2.add_data(Reference(t, min_col=6, min_row=37, max_row=40), titles_from_data=True)
c2.set_categories(Reference(t, min_col=1, min_row=38, max_row=40))
c2.legend = None; c2.height = 6; c2.width = 20; c2.x_axis.delete = False; c2.y_axis.delete = False
c2.y_axis.scaling.min = 0; c2.y_axis.number_format = "0%"
c2.series[0].graphicalProperties.solidFill = "2A78D6"; c2.series[0].graphicalProperties.line.solidFill = "2A78D6"
c2.series[0].dLbls = DataLabelList(); c2.series[0].dLbls.showVal = True; c2.series[0].dLbls.numFmt = "0.00%"
c2.series[0].dLbls.showSerName = c2.series[0].dLbls.showCatName = c2.series[0].dLbls.showLegendKey = False
c2.x_axis.scaling.orientation = "maxMin"
t.add_chart(c2, "K22")
t.page_setup.orientation = "landscape"; t.page_setup.fitToWidth = 1; t.page_setup.fitToHeight = 1
t.sheet_properties.pageSetUpPr.fitToPage = True

out = os.path.join(HERE, "PV_Generation_Estimate.xlsx")
wb.save(out); print(out)
