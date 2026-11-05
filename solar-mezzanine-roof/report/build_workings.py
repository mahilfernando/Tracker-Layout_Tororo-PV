"""Kampala Marriott rooftop PV - complete calculation workbook (all formulas, editable inputs).

Sheets: Summary, Inputs, Layout, Electrical, Structure, Generation, TOU Impact, BOQ, Financial, Sensitivity.
Run: python3 build_workings.py  then recalc with the xlsx skill's recalc.py.
"""
import os
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as CL

HERE = os.path.dirname(os.path.abspath(__file__))
F = "Arial"
def font(**k): return Font(name=F, **k)
BLUE, BLK, GRN, BOLD = font(color="0000FF"), font(), font(color="008000"), font(bold=True)
HEAD, TITLE = font(bold=True, color="FFFFFF"), font(bold=True, size=14, color="14365D")
SUB, NOTE = font(bold=True, size=11, color="14365D"), font(italic=True, size=9, color="5B6673")
HFILL, BAND, YEL = PatternFill("solid", fgColor="14365D"), PatternFill("solid", fgColor="EEF2F6"), PatternFill("solid", fgColor="FFFF00")
OKF, BADF = PatternFill("solid", fgColor="E3F4E8"), PatternFill("solid", fgColor="FBE3E3")
thin = Side(style="thin", color="C9D0D8"); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)

wb = Workbook()
N = {}                      # name -> absolute reference, e.g. "Inputs!$B$7"

def ref(ws, cell):
    sh = ws.title
    q = f"'{sh}'" if " " in sh else sh
    col = "".join(c for c in cell if c.isalpha()); row = "".join(c for c in cell if c.isdigit())
    return f"{q}!${col}${row}"

def title(ws, t, sub=None):
    ws["A1"] = t; ws["A1"].font = TITLE
    if sub: ws["A2"] = sub; ws["A2"].font = NOTE

def header(ws, row, cols, start=1, height=None):
    for j, h in enumerate(cols):
        c = ws.cell(row=row, column=start + j, value=h); c.font = HEAD; c.fill = HFILL
        c.alignment = Alignment(wrap_text=True, horizontal="center", vertical="center"); c.border = BOX
    if height: ws.row_dimensions[row].height = height

def kv(ws, row, label, value, unit="", note="", name=None, fmt=None, kind=None):
    """label | value | unit | note. kind: 'in' (input), 'link' (other sheet), None (formula)."""
    ws[f"A{row}"] = label; ws[f"B{row}"] = value; ws[f"C{row}"] = unit; ws[f"D{row}"] = note
    if kind is None:
        kind = "in" if not (isinstance(value, str) and value.startswith("=")) else ("link" if "!" in value else "f")
    ws[f"B{row}"].font = {"in": BLUE, "link": GRN, "f": BLK}[kind]
    if kind == "in": ws[f"B{row}"].fill = YEL
    if fmt: ws[f"B{row}"].number_format = fmt
    for c in "ABCD":
        ws[f"{c}{row}"].border = BOX
        if c != "B": ws[f"{c}{row}"].font = font(color="5B6673") if c == "D" else font()
    if name: N[name] = ref(ws, f"B{row}")
    return row + 1

def section(ws, row, text):
    ws[f"A{row}"] = text; ws[f"A{row}"].font = SUB
    return row + 1

def widths(ws, ws_w):
    for i, w in enumerate(ws_w, start=1): ws.column_dimensions[CL(i)].width = w

def landscape(ws):
    ws.page_setup.orientation = "landscape"; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True

# =====================================================================================
# INPUTS
# =====================================================================================
I = wb.active; I.title = "Inputs"
title(I, "Inputs & Assumptions – Kampala Marriott Rooftop PV",
      "Yellow cells with blue text are inputs. Black = formula, green = link to another sheet. Change inputs here; all sheets update.")
header(I, 3, ["Parameter", "Value", "Unit", "Source / note"])
r = 4
r = section(I, r, "Site")
r = kv(I, r, "Project", "Kampala Marriott Hotel – mezzanine roof", "", "Client: Tororo PV Power Company Limited", kind="in")
r = kv(I, r, "Latitude", 0.30315, "° N", "0°18'11.34\"N", "lat", "0.00000")
r = kv(I, r, "Longitude", 32.58716, "° E", "32°35'13.76\"E", "lon", "0.00000")
r = kv(I, r, "Time zone", 3, "UTC +h", "East Africa Time", "tz", "0")
r = kv(I, r, "Day length", 12.1, "h", "Near-constant at the equator", "daylen", "0.0")
r = section(I, r, "PV module (620 Wp bifacial TOPCon – confirm with selected datasheet)")
r = kv(I, r, "Module power", 620, "Wp", "", "pmod", "0")
r = kv(I, r, "Module length", 2382, "mm", "", "mL", "0")
r = kv(I, r, "Module width", 1134, "mm", "", "mW", "0")
r = kv(I, r, "Module weight", 33, "kg", "Dual glass", "mkg", "0.0")
r = kv(I, r, "Voc (STC)", 48.6, "V", "Typical", "voc", "0.0")
r = kv(I, r, "Vmp (STC)", 40.6, "V", "Typical", "vmp", "0.0")
r = kv(I, r, "Isc (STC)", 16.1, "A", "Typical", "isc", "0.0")
r = kv(I, r, "Imp (STC)", 15.3, "A", "Typical", "imp", "0.0")
r = kv(I, r, "Temp. coefficient Voc", -0.0025, "/°C", "-0.25 %/°C", "kvoc", "0.00%")
r = kv(I, r, "Temp. coefficient Vmp", -0.0027, "/°C", "-0.27 %/°C", "kvmp", "0.00%")
r = kv(I, r, "Bifacial / irradiance current factor", 1.25, "×", "IEC 62548 string current factor", "kbif", "0.00")
r = kv(I, r, "Minimum cell temperature", 12, "°C", "Kampala cool morning", "tmin", "0")
r = kv(I, r, "Maximum cell temperature", 65, "°C", "Hot roof, low tilt", "tmax", "0")
r = section(I, r, "Roof & layout (drawing D18102-DD-A-104, architect's solar zone only)")
r = kv(I, r, "Roof inner width", 29264, "mm", "Traced from drawing (29,390 dim.)", "roofW", "#,##0")
r = kv(I, r, "Upper block inner depth", 15717, "mm", "Traced from drawing (15,805 dim.)", "upD", "#,##0")
r = kv(I, r, "Lower block PV-zone depth", 22754, "mm", "Joint to architect's PV limit", "loD", "#,##0")
r = kv(I, r, "Tilt", 10, "°", "", "tilt", "0")
r = kv(I, r, "Module clamp gap", 20, "mm", "", "gap", "0")
r = kv(I, r, "Aisle between tables", 800, "mm", "Shading + maintenance walkway", "aisle", "0")
r = kv(I, r, "Edge setback (west / north / south)", 1000, "mm", "", "setW", "0")
r = kv(I, r, "Edge setback (east)", 1742, "mm", "Clear of roof opening", "setE", "0")
r = section(I, r, "Inverters & stringing")
r = kv(I, r, "Inverter AC rating", 80, "kW", "Available sizes: 50/60/80/100/110/125 kW", "pinv", "0")
r = kv(I, r, "Number of inverters", 2, "nos", "", "ninv", "0")
r = kv(I, r, "Inverter max. DC voltage", 1100, "V", "", "vdcmax", "0")
r = kv(I, r, "Inverter MPPT minimum voltage", 200, "V", "", "vmpptmin", "0")
r = kv(I, r, "AC voltage (line-line)", 400, "V", "", "vac", "0")
r = kv(I, r, "Power factor", 1.0, "", "", "pf", "0.00")
r = kv(I, r, "INV-01: strings (group A)", 8, "nos", "", "i1na", "0")
r = kv(I, r, "INV-01: modules per string (group A)", 19, "nos", "", "i1la", "0")
r = kv(I, r, "INV-01: strings (group B)", 0, "nos", "", "i1nb", "0")
r = kv(I, r, "INV-01: modules per string (group B)", 18, "nos", "", "i1lb", "0")
r = kv(I, r, "INV-02: strings (group A)", 3, "nos", "", "i2na", "0")
r = kv(I, r, "INV-02: modules per string (group A)", 19, "nos", "", "i2la", "0")
r = kv(I, r, "INV-02: strings (group B)", 5, "nos", "", "i2nb", "0")
r = kv(I, r, "INV-02: modules per string (group B)", 18, "nos", "", "i2lb", "0")
r = section(I, r, "Cables & protection")
r = kv(I, r, "DC string cable length (one way, avg.)", 40, "m", "6 mm² Cu PV cable", "ldc", "0")
r = kv(I, r, "DC cable resistance (6 mm², 90 °C)", 3.95, "Ω/km", "", "rdc", "0.000")
r = kv(I, r, "Inverter → ACCP cable length", 30, "m", "4C × 50 mm² Cu XLPE", "lac1", "0")
r = kv(I, r, "Resistance 50 mm² Cu (90 °C)", 0.494, "Ω/km", "", "rac1", "0.000")
r = kv(I, r, "ACCP → MLVS cable length", 80, "m", "4C × 120 mm² Cu XLPE/SWA (confirm route)", "lac2", "0")
r = kv(I, r, "Resistance 120 mm² Cu (90 °C)", 0.196, "Ω/km", "", "rac2", "0.000")
r = kv(I, r, "Reactance (AC cables)", 0.08, "Ω/km", "", "xac", "0.000")
r = kv(I, r, "Inverter outgoing MCCB rating", 125, "A", "In ACCP", "cb1", "0")
r = kv(I, r, "PV feeder MCCB rating", 250, "A", "ACCP outgoing & MLVS PV way", "cb2", "0")
r = kv(I, r, "Main incomer (existing)", 1000, "A", "Schneider Masterpact NW10 H1, 65 kA", "incA", "0")
r = kv(I, r, "Switchboard fault level", 65, "kA", "Masterpact NW10 H1 Icu", "fault", "0")
r = kv(I, r, "PV MCCB breaking capacity Icu", 70, "kA", "e.g. NSX250 H", "icu", "0")
r = section(I, r, "Energy & load")
r = kv(I, r, "Specific yield, year 1 (incl. losses)", 1480, "kWh/kWp/yr", "Desktop estimate, PR ≈ 0.80 – confirm with PVsyst", "sy", "#,##0")
r = kv(I, r, "Degradation, year 1", 0.01, "", "", "deg1", "0.0%")
r = kv(I, r, "Degradation, year 2 onward", 0.004, "per yr", "", "deg", "0.0%")
r = kv(I, r, "Hotel consumption", 1000000, "kWh/month", "Client", "loadm", "#,##0")
r = section(I, r, "Time-of-use tariff (Uganda ERA structure – replace with the bill's values)")
r = kv(I, r, "Off-peak start / end", 0, "h", "00:00", "op_s", "0")
r = kv(I, r, "Shoulder start", 6, "h", "06:00", "sh_s", "0")
r = kv(I, r, "Peak start", 18, "h", "18:00 – 24:00", "pk_s", "0")
r = kv(I, r, "Off-peak rate", 0.07, "USD/kWh", "Indicative", "r_op", "0.000")
r = kv(I, r, "Shoulder rate", 0.12, "USD/kWh", "Indicative", "r_sh", "0.000")
r = kv(I, r, "Peak rate", 0.15, "USD/kWh", "Indicative", "r_pk", "0.000")
r = section(I, r, "Financial")
r = kv(I, r, "Avoided tariff used in cash flow (year 1)", 0.12, "USD/kWh", "Flat rate; TOU value per kWh shown on TOU sheet", "tar", "0.000")
r = kv(I, r, "Tariff escalation", 0.02, "per yr", "", "esc", "0.0%")
r = kv(I, r, "Discount rate", 0.10, "", "", "disc", "0.0%")
r = kv(I, r, "O&M cost (% of capex, year 1)", 0.012, "", "Cleaning, inspection, monitoring", "omp", "0.0%")
r = kv(I, r, "O&M escalation", 0.03, "per yr", "", "omesc", "0.0%")
r = kv(I, r, "Inverter replacement year", 12, "year", "", "repy", "0")
r = kv(I, r, "Contingency", 0.07, "", "", "cont", "0.0%")
r = section(I, r, "EPC unit rates (2026 East Africa, ±15 %)")
r = kv(I, r, "PV modules (landed, cleared)", 0.150, "USD/Wp", "", "c_mod", "0.000")
r = kv(I, r, "String inverter", 4800, "USD each", "80 kW, incl. comms", "c_inv", "#,##0")
r = kv(I, r, "Mounting structure (incl. ballast, pads)", 0.090, "USD/Wp", "Enerack quote within this allowance", "c_mnt", "0.000")
r = kv(I, r, "DC system", 0.040, "USD/Wp", "Cable, MC4, isolators, SPD", "c_dc", "0.000")
r = kv(I, r, "AC system (ACCP, MCCBs, 120 mm² cable, tray)", 9500, "USD", "Lump sum", "c_ac", "#,##0")
r = kv(I, r, "Zero-export controller & monitoring", 3500, "USD", "Lump sum", "c_zx", "#,##0")
r = kv(I, r, "Earthing & lightning protection", 3000, "USD", "Lump sum", "c_earth", "#,##0")
r = kv(I, r, "Walkways, lifeline, water point", 3500, "USD", "Lump sum", "c_walk", "#,##0")
r = kv(I, r, "Installation, testing & commissioning", 0.060, "USD/Wp", "", "c_inst", "0.000")
r = kv(I, r, "Engineering & structural check", 4000, "USD", "Lump sum", "c_eng", "#,##0")
r = kv(I, r, "Approvals & utility interface", 2000, "USD", "Lump sum", "c_appr", "#,##0")
r = kv(I, r, "Transport, logistics & customs clearing", 4000, "USD", "Lump sum", "c_trans", "#,##0")
widths(I, [44, 16, 12, 58]); landscape(I)

# =====================================================================================
# LAYOUT
# =====================================================================================
L = wb.create_sheet("Layout")
title(L, "Layout & Row-Spacing Working", "Tables are 2 modules high in portrait (2P) or 1 module high (1P).")
header(L, 3, ["Item", "Value", "Unit", "Working"])
r = 4
r = section(L, r, "Table geometry")
r = kv(L, r, "2P slope length", f"=2*{N['mL']}+{N['gap']}", "mm", "2 × module length + gap", "sl2", "#,##0")
r = kv(L, r, "2P table depth on plan", f"={N['sl2']}*COS(RADIANS({N['tilt']}))", "mm", "slope × cos(tilt)", "d2", "#,##0")
r = kv(L, r, "2P rise (rear above front)", f"={N['sl2']}*SIN(RADIANS({N['tilt']}))", "mm", "slope × sin(tilt)", "h2", "#,##0")
r = kv(L, r, "1P table depth on plan", f"={N['mL']}*COS(RADIANS({N['tilt']}))", "mm", "", "d1", "#,##0")
r = kv(L, r, "1P rise", f"={N['mL']}*SIN(RADIANS({N['tilt']}))", "mm", "", "h1", "#,##0")
r = kv(L, r, "Modules per row", f"=INT(({N['roofW']}-{N['setW']}-{N['setE']}+{N['gap']})/({N['mW']}+{N['gap']}))", "nos", "fits between setbacks", "ncol", "0")
r = kv(L, r, "Row length (modules)", f"={N['ncol']}*{N['mW']}+({N['ncol']}-1)*{N['gap']}", "mm", "", "rowlen", "#,##0")
r = section(L, r, "Upper block")
r = kv(L, r, "Available depth", f"={N['upD']}-2*{N['setW']}", "mm", "depth − 2 setbacks", "upA", "#,##0")
r = kv(L, r, "2P tables", f"=INT(({N['upA']}+{N['aisle']})/({N['d2']}+{N['aisle']}))", "nos", "", "up2", "0")
r = kv(L, r, "Depth left after 2P tables", f"={N['upA']}-({N['up2']}*{N['d2']}+MAX({N['up2']}-1,0)*{N['aisle']})", "mm", "", "upRem", "#,##0")
r = kv(L, r, "1P tables", f"=IF({N['upRem']}>={N['aisle']}+{N['d1']},1,0)", "nos", "one 1P row if it fits", "up1", "0")
r = kv(L, r, "Modules", f"=({N['up2']}*2+{N['up1']})*{N['ncol']}", "nos", "", "upM", "0")
r = section(L, r, "Lower block (to architect's PV limit)")
r = kv(L, r, "Available depth", f"={N['loD']}-{N['setW']}", "mm", "setback at top only", "loA", "#,##0")
r = kv(L, r, "2P tables", f"=INT(({N['loA']}+{N['aisle']})/({N['d2']}+{N['aisle']}))", "nos", "", "lo2", "0")
r = kv(L, r, "Depth left after 2P tables", f"={N['loA']}-({N['lo2']}*{N['d2']}+MAX({N['lo2']}-1,0)*{N['aisle']})", "mm", "", "loRem", "#,##0")
r = kv(L, r, "1P tables", f"=IF({N['loRem']}>={N['aisle']}+{N['d1']},1,0)", "nos", "", "lo1", "0")
r = kv(L, r, "Modules", f"=({N['lo2']}*2+{N['lo1']})*{N['ncol']}", "nos", "", "loM", "0")
r = section(L, r, "Totals")
r = kv(L, r, "2P tables (total)", f"={N['up2']}+{N['lo2']}", "nos", "", "t2", "0")
r = kv(L, r, "1P tables (total)", f"={N['up1']}+{N['lo1']}", "nos", "", "t1", "0")
r = kv(L, r, "Total modules", f"={N['upM']}+{N['loM']}", "nos", "", "nmod", "0")
r = kv(L, r, "Plant capacity (DC)", f"={N['nmod']}*{N['pmod']}/1000", "kWp", "", "kwp", "0.00")
r = kv(L, r, "Module area", f"={N['nmod']}*{N['mL']}*{N['mW']}/1000000", "m²", "", "marea", "#,##0")
r = kv(L, r, "Module weight (total)", f"={N['nmod']}*{N['mkg']}/1000", "t", "", "mt", "0.0")
r = section(L, r, "Row-to-row shading check (panels facing the equator, no shading 09:00–15:00 all year)")
header(L, r, ["Sun position", "Declination (°)", "Hour angle (°)", "Elevation (°)", "N-S component", "Shadow gap needed (mm)"]); r += 1
cases = [("21 Dec, 09:00 / 15:00", -23.45, 45), ("21 Dec, 12:00", -23.45, 0), ("21 Jun, 09:00 / 15:00", 23.45, 45), ("21 Jun, 12:00", 23.45, 0)]
first = r
for lab, dec, ha in cases:
    L[f"A{r}"] = lab; L[f"B{r}"] = dec; L[f"C{r}"] = ha
    L[f"D{r}"] = (f"=DEGREES(ASIN(SIN(RADIANS({N['lat']}))*SIN(RADIANS(B{r}))+COS(RADIANS({N['lat']}))*COS(RADIANS(B{r}))*COS(RADIANS(C{r}))))")
    L[f"E{r}"] = (f"=-(COS(RADIANS({N['lat']}))*SIN(RADIANS(B{r}))-SIN(RADIANS({N['lat']}))*COS(RADIANS(B{r}))*COS(RADIANS(C{r})))")
    L[f"F{r}"] = f"=IF(E{r}>0,{N['h2']}*E{r}/SIN(RADIANS(D{r})),0)"
    for c, f in zip("BCDEF", ["0.00", "0", "0.0", "0.000", "#,##0"]): L[f"{c}{r}"].number_format = f
    for c in "BC": L[f"{c}{r}"].font = BLUE; L[f"{c}{r}"].fill = YEL
    for c in "ADEF": L[f"{c}{r}"].font = font()
    for c in "ABCDEF": L[f"{c}{r}"].border = BOX
    r += 1
r = kv(L, r, "Largest shadow gap needed", f"=MAX(F{first}:F{r-1})", "mm", "worst case of the rows above", "gapneed", "#,##0")
r = kv(L, r, "Aisle provided", f"={N['aisle']}", "mm", "", None, "#,##0")
L[f"A{r}"] = "Shading check"; L[f"B{r}"] = f'=IF({N["aisle"]}>={N["gapneed"]},"OK","INCREASE AISLE")'; L[f"B{r}"].font = BOLD
for c in "ABCD": L[f"{c}{r}"].border = BOX
r += 1
widths(L, [36, 16, 14, 16, 14, 20]); landscape(L)

# =====================================================================================
# ELECTRICAL
# =====================================================================================
E = wb.create_sheet("Electrical")
title(E, "Electrical Working – Strings, Inverters, Cables, Protection")
header(E, 3, ["Item", "Value", "Unit", "Working"])
r = 4
r = section(E, r, "Module voltages at temperature extremes")
r = kv(E, r, "Voc at minimum cell temperature", f"={N['voc']}*(1+{N['kvoc']}*({N['tmin']}-25))", "V", "Voc × (1 + k × (Tmin − 25))", "voccold", "0.00")
r = kv(E, r, "Vmp at maximum cell temperature", f"={N['vmp']}*(1+{N['kvmp']}*({N['tmax']}-25))", "V", "Vmp × (1 + k × (Tmax − 25))", "vmphot", "0.00")
r = kv(E, r, "Max. modules per string", f"=INT({N['vdcmax']}/{N['voccold']})", "nos", "inverter max DC ÷ Voc cold", "smax", "0")
r = kv(E, r, "Min. modules per string", f"=ROUNDUP({N['vmpptmin']}/{N['vmphot']},0)", "nos", "MPPT min ÷ Vmp hot", "smin", "0")
r = kv(E, r, "Design string current", f"={N['isc']}*{N['kbif']}", "A", "Isc × factor", "istr", "0.0")
r = section(E, r, "Inverter configuration")
header(E, r, ["", "INV-01", "INV-02", "Total"]); r += 1
rows = [
    ("Strings", f"={N['i1na']}+{N['i1nb']}", f"={N['i2na']}+{N['i2nb']}", "=B{r}+C{r}", "0"),
    ("Modules", f"={N['i1na']}*{N['i1la']}+{N['i1nb']}*{N['i1lb']}", f"={N['i2na']}*{N['i2la']}+{N['i2nb']}*{N['i2lb']}", "=B{r}+C{r}", "0"),
    ("DC capacity (kWp)", "=B{p}*" + N['pmod'] + "/1000", "=C{p}*" + N['pmod'] + "/1000", "=B{r}+C{r}", "0.00"),
    ("AC rating (kW)", f"={N['pinv']}", f"={N['pinv']}", "=B{r}+C{r}", "0"),
    ("DC/AC ratio", "=B{p}/B{r1}", "=C{p}/C{r1}", "=D{p}/D{r1}", "0.00"),
    ("Longest string Voc cold (V)", f"=MAX(IF({N['i1na']}>0,{N['i1la']},0),IF({N['i1nb']}>0,{N['i1lb']},0))*{N['voccold']}",
     f"=MAX(IF({N['i2na']}>0,{N['i2la']},0),IF({N['i2nb']}>0,{N['i2lb']},0))*{N['voccold']}", "=MAX(B{r},C{r})", "0"),
    ("Shortest string Vmp hot (V)", f"=MIN(IF({N['i1na']}>0,{N['i1la']},999),IF({N['i1nb']}>0,{N['i1lb']},999))*{N['vmphot']}",
     f"=MIN(IF({N['i2na']}>0,{N['i2la']},999),IF({N['i2nb']}>0,{N['i2lb']},999))*{N['vmphot']}", "=MIN(B{r},C{r})", "0"),
    ("AC current at rated output (A)", f"={N['pinv']}*1000/(SQRT(3)*{N['vac']}*{N['pf']})", f"={N['pinv']}*1000/(SQRT(3)*{N['vac']}*{N['pf']})", "=B{r}+C{r}", "0.0"),
]
start = r
for i, (lab, b, c, d, fmt) in enumerate(rows):
    p = r - 1; r1 = r - 1
    if lab == "DC/AC ratio": p, r1 = start + 2, start + 3
    if lab == "DC capacity (kWp)": p = start + 1
    E[f"A{r}"] = lab
    E[f"B{r}"] = b.format(r=r, p=p, r1=r1); E[f"C{r}"] = c.format(r=r, p=p, r1=r1); E[f"D{r}"] = d.format(r=r, p=p, r1=r1)
    for col in "BCD": E[f"{col}{r}"].number_format = fmt; E[f"{col}{r}"].font = font()
    for col in "ABCD": E[f"{col}{r}"].border = BOX
    E[f"A{r}"].font = font()
    if lab == "Modules": N["modsInv"] = ref(E, f"D{r}")
    if lab == "DC capacity (kWp)": N["kwpInv"] = ref(E, f"D{r}")
    if lab == "AC rating (kW)": N["acTot"] = ref(E, f"D{r}")
    if lab == "DC/AC ratio": N["dcac"] = ref(E, f"D{r}")
    if lab.startswith("Longest"): N["vocmaxStr"] = ref(E, f"D{r}")
    if lab.startswith("Shortest"): N["vmpminStr"] = ref(E, f"D{r}")
    if lab.startswith("AC current"): N["iac1"] = ref(E, f"B{r}"); N["iacT"] = ref(E, f"D{r}")
    r += 1
r += 1
r = section(E, r, "Checks")
checks = [
    ("Modules in strings = modules on roof", f'=IF({N["modsInv"]}={N["nmod"]},"OK","MISMATCH")'),
    ("String Voc cold ≤ inverter max DC", f'=IF({N["vocmaxStr"]}<={N["vdcmax"]},"OK","TOO HIGH")'),
    ("String Vmp hot ≥ MPPT minimum", f'=IF({N["vmpminStr"]}>={N["vmpptmin"]},"OK","TOO LOW")'),
    ("DC/AC ratio between 1.0 and 1.35", f'=IF(AND({N["dcac"]}>=1,{N["dcac"]}<=1.35),"OK","CHECK")'),
    ("Inverter MCCB ≥ inverter current", f'=IF({N["cb1"]}>={N["iac1"]},"OK","UNDERSIZED")'),
    ("PV feeder MCCB ≥ total PV current", f'=IF({N["cb2"]}>={N["iacT"]},"OK","UNDERSIZED")'),
    ("PV MCCB Icu ≥ switchboard fault level", f'=IF({N["icu"]}>={N["fault"]},"OK","UPGRADE")'),
    ("PV current ≤ 25 % of main incomer", f'=IF({N["iacT"]}<=0.25*{N["incA"]},"OK","CHECK BUSBAR")'),
]
for lab, f in checks:
    E[f"A{r}"] = lab; E[f"B{r}"] = f; E[f"B{r}"].font = BOLD
    for c in "AB": E[f"{c}{r}"].border = BOX
    r += 1
r += 1
r = section(E, r, "Voltage drop")
r = kv(E, r, "DC string voltage (19 modules at Vmp STC)", f"={N['i1la']}*{N['vmp']}", "V", "", "vstr", "0")
r = kv(E, r, "DC voltage drop", f"=2*{N['ldc']}*{N['imp']}*{N['rdc']}/1000", "V", "2 × L × Imp × R", "vddc", "0.00")
r = kv(E, r, "DC voltage drop", f"={N['vddc']}/{N['vstr']}", "%", "target ≤ 1.5 %", "vddcp", "0.00%")
r = kv(E, r, "AC drop inverter → ACCP", f"=SQRT(3)*{N['iac1']}*{N['lac1']}*({N['rac1']}*{N['pf']}+{N['xac']}*SIN(ACOS({N['pf']})))/1000/{N['vac']}", "%", "√3·I·L·(R cosφ + X sinφ) / V", "vdac1", "0.00%")
r = kv(E, r, "AC drop ACCP → MLVS", f"=SQRT(3)*{N['iacT']}*{N['lac2']}*({N['rac2']}*{N['pf']}+{N['xac']}*SIN(ACOS({N['pf']})))/1000/{N['vac']}", "%", "", "vdac2", "0.00%")
r = kv(E, r, "Total AC voltage drop", f"={N['vdac1']}+{N['vdac2']}", "%", "target ≤ 3 %", "vdacT", "0.00%")
E[f"A{r}"] = "Voltage-drop check"; E[f"B{r}"] = f'=IF(AND({N["vddcp"]}<=0.015,{N["vdacT"]}<=0.03),"OK","CHECK CABLES")'; E[f"B{r}"].font = BOLD
for c in "AB": E[f"{c}{r}"].border = BOX
widths(E, [44, 16, 16, 30]); landscape(E)

# =====================================================================================
# STRUCTURE
# =====================================================================================
S = wb.create_sheet("Structure")
title(S, "Mounting Structure – Enerack Ballast System (supplier quote as issued)",
      "Xiamen Enerack Technology Co., Ltd. · Invoice/quote ERKI20261104TP dated 2026-11-04 · Drawing EPJ-26110401 V1.0 · Panel 2382×1134×30 mm")
header(S, 4, ["Item No.", "Description", "Qty", "Unit", "Unit price EXW (USD)", "Amount EXW (USD)"], height=30)
QUOTE = [("ERK-R80-3000", "R80 Rail L=3000", 256, 16.64, 4258.56), ("ERK-R80-2630", "R80 Rail L=2630", 32, 14.58, 466.67),
         ("ERK-SFR-R80", "Rail connect", 256, 1.19, 304.64), ("ERK-GRC", "Rail clamp", 795, 0.22, 178.59),
         ("ERK-FEC-30", "30 mm end clamp", 65, 0.30, 19.47), ("ERK-AIC", "Adjustable (30-40 mm) inner clamp", 707, 0.30, 212.10),
         ("ERK-W45-3800", "Pre-assembly L=3800 (2P frame)", 77, 40.40, 3110.80), ("ERK-W45-1400", "Pre-assembly L=1400 (1P frame)", 22, 20.64, 454.08),
         ("ERK-35JL-2725", "Cross L=2725", 140, 6.85, 958.77), ("ERK-M8X70", "M8×70 bolt", 155, 0.20, 31.00),
         ("ERK-ELG-03", "Earthing lug", 33, 0.28, 9.24)]
r = 5
for code, d, q, u, amt in QUOTE:
    S[f"A{r}"] = code; S[f"B{r}"] = d; S[f"C{r}"] = q; S[f"D{r}"] = "kits"; S[f"E{r}"] = u; S[f"F{r}"] = amt
    for c in "CEF": S[f"{c}{r}"].font = BLUE
    S[f"C{r}"].number_format = "#,##0"; S[f"E{r}"].number_format = "#,##0.00"; S[f"F{r}"].number_format = "#,##0.00"
    for c in "ABD": S[f"{c}{r}"].font = font()
    for c in "ABCDEF": S[f"{c}{r}"].border = BOX
    r += 1
q0, q1 = 5, r - 1
S[f"B{r}"] = "Sub-total EXW"; S[f"C{r}"] = f"=SUM(C{q0}:C{q1})"; S[f"F{r}"] = f"=SUM(F{q0}:F{q1})"; sub_r = r; r += 1
S[f"B{r}"] = "Freight cost to Mombasa Port, Kenya"; S[f"F{r}"] = 1300; S[f"F{r}"].font = BLUE; r += 1
S[f"B{r}"] = "Total CIF Mombasa"; S[f"F{r}"] = f"=F{sub_r}+F{r-1}"; N["strCIF"] = ref(S, f"F{r}"); cif_r = r
for rr in range(sub_r, r + 1):
    for c in "ABCDEF": S[f"{c}{rr}"].border = BOX; S[f"{c}{rr}"].fill = BAND
    S[f"B{rr}"].font = BOLD; S[f"F{rr}"].number_format = "#,##0.00"
    if rr != sub_r + 1: S[f"F{rr}"].font = BOLD
S[f"C{sub_r}"].number_format = "#,##0"; S[f"C{sub_r}"].font = BOLD
r += 2
S[f"A{r}"] = "Quote terms: 30 % T/T deposit, balance before shipment · Port of destination Mombasa · Delivery 10–15 days after deposit · CIF excludes import clearance, customs duties and VAT."; S[f"A{r}"].font = NOTE; r += 1
S[f"A{r}"] = "Line amounts are as printed on the supplier's quote (some differ from qty × unit price by a few cents due to the supplier's rounding)."; S[f"A{r}"].font = NOTE; r += 2
r = section(S, r, "Quote scope vs. current layout")
header(S, r, ["", "Item", "Quoted", "Current layout", "Difference", ""]); r += 1
for lab, quoted, cur in [("2P frames (L=3800)", f"=C{q0+6}", f"={N['t2']}*11"), ("1P frames (L=1400)", f"=C{q0+7}", f"={N['t1']}*11"),
                         ("Rail lines (R80 L=2630, 1 per line)", f"=C{q0+1}", f"={N['t2']}*4+{N['t1']}*2"),
                         ("Modules supported", "=(C11/11*46)+(C12/11*23)", f"={N['nmod']}")]:
    S[f"B{r}"] = lab; S[f"C{r}"] = quoted; S[f"D{r}"] = cur; S[f"E{r}"] = f"=C{r}-D{r}"
    for c in "CDE": S[f"{c}{r}"].number_format = "#,##0"; S[f"{c}{r}"].font = font()
    S[f"B{r}"].font = font()
    for c in "BCDE": S[f"{c}{r}"].border = BOX
    r += 1
S[f"A{r}"] = "The quote covers 7 × 2P + 2 × 1P tables (368 modules); the current layout uses 6 × 2P + 1 × 1P (299 modules). Value kept as quoted – confirm final quantities with Enerack."; S[f"A{r}"].font = NOTE; r += 2
r = kv(S, r, "Structure cost per Wp of current plant (CIF)", f"=F{cif_r}/({N['kwp']}*1000)", "USD/Wp", "", None, "0.000")
S.merge_cells(start_row=r-1, start_column=4, end_row=r-1, end_column=6)
r = kv(S, r, "Roof load – modules + structure (excl. ballast)", f"=({N['mt']}*1000+{N['marea']}*4.5)/(({N['t2']}*{N['d2']}+{N['t1']}*{N['d1']})*{N['rowlen']}/1000000)", "kg/m²", "4.5 kg/m² structure allowance; ballast per Enerack calculation", None, "0.0")
widths(S, [44, 36, 12, 16, 18, 18]); landscape(S)

# =====================================================================================
# GENERATION (monthly + 25 years)
# =====================================================================================
G = wb.create_sheet("Generation")
title(G, "Estimated PV Solar Generation",
      "Monthly shape from typical Kampala irradiation (approx.); annual total = kWp × specific yield. Replace column C with PVGIS/PVsyst values when available.")
r = 4
r = kv(G, r, "Plant capacity", f"={N['kwp']}", "kWp", "", None, "0.00")
r = kv(G, r, "Year-1 generation", f"={N['kwp']}*{N['sy']}", "kWh", "kWp × specific yield", "y1", "#,##0")
r = kv(G, r, "Hotel consumption", f"={N['loadm']}*12", "kWh/yr", "", "loady", "#,##0")
r = kv(G, r, "Share of hotel consumption", f"={N['y1']}/{N['loady']}", "", "", "share", "0.00%")
r += 1
hr = r
header(G, hr, ["Month", "Days", "GHI (kWh/m²/day)", "Weight", "Share", "Generation (kWh)", "Generation (MWh)", "kWh/day"], height=30)
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
ghi = [5.4, 5.6, 5.4, 5.0, 4.7, 4.6, 4.5, 4.8, 5.1, 5.0, 4.9, 5.1]
m0 = hr + 1; mt = m0 + 12
for i in range(12):
    rr = m0 + i
    G[f"A{rr}"] = months[i]; G[f"B{rr}"] = days[i]; G[f"C{rr}"] = ghi[i]
    G[f"D{rr}"] = f"=B{rr}*C{rr}"; G[f"E{rr}"] = f"=D{rr}/$D${mt}"; G[f"F{rr}"] = f"={N['y1']}*E{rr}"
    G[f"G{rr}"] = f"=F{rr}/1000"; G[f"H{rr}"] = f"=F{rr}/B{rr}"
    G[f"C{rr}"].font = BLUE; G[f"C{rr}"].fill = YEL
for col, f in zip("BCDEFGH", ["0", "0.00", "0.0", "0.0%", "#,##0", "0.0", "#,##0"]):
    for rr in range(m0, mt + 2): G[f"{col}{rr}"].number_format = f
G[f"A{mt}"] = "Year"
for col in "BDEFG": G[f"{col}{mt}"] = f"=SUM({col}{m0}:{col}{mt-1})"
G[f"C{mt}"] = f"=SUMPRODUCT(B{m0}:B{mt-1},C{m0}:C{mt-1})/B{mt}"; G[f"H{mt}"] = f"=F{mt}/B{mt}"
G[f"A{mt+1}"] = "Monthly average"; G[f"F{mt+1}"] = f"=F{mt}/12"; G[f"G{mt+1}"] = f"=G{mt}/12"
for rr in range(m0, mt + 2):
    for col in "ABCDEFGH":
        G[f"{col}{rr}"].border = BOX
        if rr >= mt: G[f"{col}{rr}"].font = BOLD; G[f"{col}{rr}"].fill = BAND
        elif col != "C": G[f"{col}{rr}"].font = font()
ch = BarChart(); ch.type = "col"; ch.title = "Estimated Monthly PV Generation – Year 1 (MWh)"
ch.add_data(Reference(G, min_col=7, min_row=hr, max_row=mt - 1), titles_from_data=True)
ch.set_categories(Reference(G, min_col=1, min_row=m0, max_row=mt - 1))
ch.legend = None; ch.gapWidth = 60; ch.height = 8; ch.width = 18; ch.y_axis.title = "MWh per month"
ch.y_axis.delete = False; ch.x_axis.delete = False; ch.y_axis.scaling.min = 0
s0 = ch.series[0]; s0.graphicalProperties.solidFill = "14365D"; s0.graphicalProperties.line.solidFill = "14365D"
s0.dLbls = DataLabelList(); s0.dLbls.showVal = True; s0.dLbls.numFmt = "0.0"
s0.dLbls.showSerName = s0.dLbls.showCatName = s0.dLbls.showLegendKey = False
G.add_chart(ch, "J4")
widths(G, [18, 8, 14, 10, 10, 16, 14, 12]); landscape(G)

# =====================================================================================
# TOU IMPACT (hourly sine model in formulas)
# =====================================================================================
T = wb.create_sheet("TOU Impact")
title(T, "Solar Impact on Time-of-Use Tariff – Average Day",
      "Solar: sine profile between sunrise and sunset at the site (formula). Load: hotel hourly profile (edit column F).")
r = 4
r = kv(T, r, "Solar noon (EAT)", f"=12-({N['lon']}-15*{N['tz']})*4/60+0.05", "h", "longitude correction + equation-of-time avg", "noon", "0.00")
r = kv(T, r, "Sunrise", f"={N['noon']}-{N['daylen']}/2", "h", "", "sr", "0.00")
r = kv(T, r, "Sunset", f"={N['noon']}+{N['daylen']}/2", "h", "", "ss", "0.00")
r = kv(T, r, "Solar per average day", f"={N['y1']}/365", "kWh/day", "", "pvday", "#,##0")
r = kv(T, r, "Hotel load per average day", f"={N['loady']}/365", "kWh/day", "", "loadday", "#,##0")
r += 1
hr = r
header(T, hr, ["Hour", "Period", "Rate (USD/kWh)", "Sun-up from", "Sun-up to", "Load profile factor",
               "Solar share", "Solar (kWh)", "Hotel load (kWh)", "Grid after solar (kWh)"], height=30)
shape = [.75, .72, .70, .70, .72, .80, .95, 1.10, 1.20, 1.25, 1.28, 1.30, 1.30, 1.30, 1.28, 1.25, 1.20, 1.20, 1.25, 1.20, 1.10, .98, .88, .80]
h0 = hr + 1; ht = h0 + 24
pi = "PI()"
for h in range(24):
    rr = h0 + h
    T[f"A{rr}"] = h; T[f"A{rr}"].number_format = '00":00"'
    T[f"B{rr}"] = f'=IF(A{rr}<{N["sh_s"]},"Off-peak",IF(A{rr}<{N["pk_s"]},"Shoulder","Peak"))'
    T[f"C{rr}"] = f'=IF(B{rr}="Off-peak",{N["r_op"]},IF(B{rr}="Shoulder",{N["r_sh"]},{N["r_pk"]}))'
    T[f"D{rr}"] = f"=MAX(A{rr},{N['sr']})"; T[f"E{rr}"] = f"=MIN(A{rr}+1,{N['ss']})"
    T[f"F{rr}"] = shape[h]; T[f"F{rr}"].font = BLUE; T[f"F{rr}"].fill = YEL
    T[f"G{rr}"] = (f"=IF(E{rr}>D{rr},(COS({pi}*(D{rr}-{N['sr']})/{N['daylen']})-COS({pi}*(E{rr}-{N['sr']})/{N['daylen']}))/2,0)")
    T[f"H{rr}"] = f"={N['pvday']}*G{rr}"
    T[f"I{rr}"] = f"={N['loadday']}*F{rr}/$F${ht}"
    T[f"J{rr}"] = f"=I{rr}-H{rr}"
    for col, f in zip("CDEFGHIJ", ["0.000", "0.00", "0.00", "0.00", "0.00%", "#,##0.0", "#,##0", "#,##0"]): T[f"{col}{rr}"].number_format = f
    for col in "ABCDEGHIJ": T[f"{col}{rr}"].font = font()
    for col in "ABCDEFGHIJ": T[f"{col}{rr}"].border = BOX
T[f"A{ht}"] = "Day total"
for col in "FGHIJ": T[f"{col}{ht}"] = f"=SUM({col}{h0}:{col}{ht-1})"
for col, f in zip("FGHIJ", ["0.00", "0.0%", "#,##0", "#,##0", "#,##0"]): T[f"{col}{ht}"].number_format = f
for col in "ABCDEFGHIJ": T[f"{col}{ht}"].font = BOLD; T[f"{col}{ht}"].fill = BAND; T[f"{col}{ht}"].border = BOX
r = ht + 2
sr0 = r
header(T, r, ["Period", "Rate (USD/kWh)", "Hotel use (MWh/yr)", "Solar (MWh/yr)", "Share of solar", "Grid after solar (MWh/yr)",
              "Reduction", "Cost before (USD/yr)", "Cost after (USD/yr)", "Saving (USD/yr)"], height=32)
r += 1
hrng = lambda c: f"${c}${h0}:${c}${ht-1}"
for name, rate in (("Off-peak", "r_op"), ("Shoulder", "r_sh"), ("Peak", "r_pk")):
    T[f"A{r}"] = name; T[f"B{r}"] = f"={N[rate]}"; T[f"B{r}"].font = GRN
    T[f"C{r}"] = f'=SUMIF({hrng("B")},A{r},{hrng("I")})*365/1000'
    T[f"D{r}"] = f'=SUMIF({hrng("B")},A{r},{hrng("H")})*365/1000'
    T[f"E{r}"] = f"=IF($D${sr0+4}=0,0,D{r}/$D${sr0+4})"
    T[f"F{r}"] = f"=C{r}-D{r}"; T[f"G{r}"] = f"=IF(C{r}=0,0,D{r}/C{r})"
    T[f"H{r}"] = f"=C{r}*1000*B{r}"; T[f"I{r}"] = f"=F{r}*1000*B{r}"; T[f"J{r}"] = f"=H{r}-I{r}"
    r += 1
T[f"A{r}"] = "Total"
for col in "CDFHIJ": T[f"{col}{r}"] = f"=SUM({col}{sr0+1}:{col}{r-1})"
T[f"E{r}"] = f"=SUM(E{sr0+1}:E{r-1})"; T[f"G{r}"] = f"=IF(C{r}=0,0,D{r}/C{r})"
N["touSave"] = ref(T, f"J{r}"); N["touCost0"] = ref(T, f"H{r}"); N["touPV"] = ref(T, f"D{r}")
tot_row = r
for rr in range(sr0 + 1, r + 1):
    for col, f in zip("BCDEFGHIJ", ["0.000", "#,##0", "#,##0.0", "0.0%", "#,##0", "0.00%", "#,##0", "#,##0", "#,##0"]):
        T[f"{col}{rr}"].number_format = f
    for col in "ABCDEFGHIJ":
        T[f"{col}{rr}"].border = BOX
        if rr == r: T[f"{col}{rr}"].font = BOLD; T[f"{col}{rr}"].fill = BAND
        elif col != "B": T[f"{col}{rr}"].font = font()
r += 1
T[f"A{r}"] = "Bill reduction"; T[f"J{r}"] = f"=IF(H{tot_row}=0,0,J{tot_row}/H{tot_row})"; T[f"J{r}"].number_format = "0.00%"; r += 1
T[f"A{r}"] = "Value per solar kWh (USD)"; T[f"J{r}"] = f"=IF(D{tot_row}=0,0,J{tot_row}/(D{tot_row}*1000))"; T[f"J{r}"].number_format = "0.000"
N["touVal"] = ref(T, f"J{r}")
for rr in (r - 1, r): T[f"A{rr}"].font = BOLD; T[f"J{rr}"].font = BOLD
c1 = BarChart(); c1.type = "col"; c1.title = "Average-Day Solar Generation by Hour (kWh)"
c1.add_data(Reference(T, min_col=8, min_row=hr, max_row=ht - 1), titles_from_data=True)
c1.set_categories(Reference(T, min_col=1, min_row=h0, max_row=ht - 1))
c1.legend = None; c1.gapWidth = 40; c1.height = 8; c1.width = 20; c1.y_axis.title = "kWh in each hour"
c1.y_axis.delete = False; c1.x_axis.delete = False; c1.y_axis.scaling.min = 0
c1.series[0].graphicalProperties.solidFill = "EDA100"; c1.series[0].graphicalProperties.line.solidFill = "EDA100"
T.add_chart(c1, "L4")
c2 = BarChart(); c2.type = "bar"; c2.title = "Reduction of Grid Energy by Tariff Period"
c2.add_data(Reference(T, min_col=7, min_row=sr0, max_row=sr0 + 3), titles_from_data=True)
c2.set_categories(Reference(T, min_col=1, min_row=sr0 + 1, max_row=sr0 + 3))
c2.legend = None; c2.height = 6; c2.width = 20; c2.x_axis.delete = False; c2.y_axis.delete = False
c2.y_axis.scaling.min = 0; c2.y_axis.number_format = "0%"; c2.x_axis.scaling.orientation = "maxMin"
c2.series[0].graphicalProperties.solidFill = "2A78D6"; c2.series[0].graphicalProperties.line.solidFill = "2A78D6"
c2.series[0].dLbls = DataLabelList(); c2.series[0].dLbls.showVal = True; c2.series[0].dLbls.numFmt = "0.00%"
c2.series[0].dLbls.showSerName = c2.series[0].dLbls.showCatName = c2.series[0].dLbls.showLegendKey = False
T.add_chart(c2, "L22")
widths(T, [16, 13, 12, 11, 11, 12, 12, 13, 14, 14]); landscape(T)

# =====================================================================================
# BOQ
# =====================================================================================
B = wb.create_sheet("BOQ")
title(B, "Cost Estimate – Bill of Quantities (USD, excluding taxes)")
header(B, 3, ["No.", "Description", "Quantity", "Unit", "Rate (USD)", "Amount (USD)"], height=22)
items = [
    ("PV modules, 620 Wp bifacial TOPCon (landed, cleared)", f"={N['kwp']}*1000", "Wp", "c_mod"),
    ("String inverters, 80 kW, 1,100 V, multi-MPPT", f"={N['ninv']}", "nos", "c_inv"),
    ("Mounting structure, 10° ballasted, incl. pads", f"={N['kwp']}*1000", "Wp", "c_mnt"),
    ("DC system: PV cable, MC4, isolators, SPD", f"={N['kwp']}*1000", "Wp", "c_dc"),
    ("AC system: ACCP, MCCBs, 4C×120 mm² cable, tray", 1, "lot", "c_ac"),
    ("Zero-export controller, CTs, data logger", 1, "set", "c_zx"),
    ("Earthing, bonding & lightning protection", 1, "lot", "c_earth"),
    ("Roof walkways, safety lifeline, water point", 1, "lot", "c_walk"),
    ("Installation, testing & commissioning", f"={N['kwp']}*1000", "Wp", "c_inst"),
    ("Engineering: design, structural check, PVsyst", 1, "lot", "c_eng"),
    ("Approvals & utility interface (ERA / UEDCL)", 1, "lot", "c_appr"),
    ("Transport, logistics & customs clearing", 1, "lot", "c_trans"),
]
r = 4
for i, (d, q, u, rate) in enumerate(items, start=1):
    B[f"A{r}"] = i; B[f"B{r}"] = d; B[f"C{r}"] = q; B[f"D{r}"] = u; B[f"E{r}"] = f"={N[rate]}"
    B[f"F{r}"] = f"=ROUND(C{r}*E{r},0)"
    B[f"C{r}"].number_format = "#,##0"; B[f"E{r}"].number_format = "#,##0.000" if u == "Wp" else "#,##0"
    B[f"F{r}"].number_format = "#,##0"; B[f"E{r}"].font = GRN
    if not isinstance(q, str): B[f"C{r}"].font = BLUE; B[f"C{r}"].fill = YEL
    for c in "ABCDEF":
        B[f"{c}{r}"].border = BOX
        if c not in "EC": B[f"{c}{r}"].font = font()
    r += 1
B[f"B{r}"] = "Sub-total"; B[f"F{r}"] = f"=SUM(F4:F{r-1})"; N["sub"] = ref(B, f"F{r}"); r += 1
B[f"B{r}"] = "Contingency"; B[f"E{r}"] = f"={N['cont']}"; B[f"E{r}"].number_format = "0.0%"; B[f"E{r}"].font = GRN
B[f"F{r}"] = f"=ROUND({N['sub']}*{N['cont']},0)"; r += 1
B[f"B{r}"] = "Total budget EPC cost (excluding taxes)"; B[f"F{r}"] = f"={N['sub']}+F{r-1}"; N["capex"] = ref(B, f"F{r}"); r += 1
B[f"B{r}"] = "Specific cost"; B[f"D{r}"] = "USD/Wp"; B[f"F{r}"] = f"={N['capex']}/({N['kwp']}*1000)"; B[f"F{r}"].number_format = "0.000"; r += 1
B[f"B{r}"] = "Annual O&M, year 1"; B[f"F{r}"] = f"=ROUND({N['capex']}*{N['omp']},0)"; N["om0"] = ref(B, f"F{r}")
for rr in range(r - 4, r + 1):
    for c in "ABCDEF": B[f"{c}{rr}"].border = BOX; B[f"{c}{rr}"].fill = BAND
    B[f"B{rr}"].font = BOLD
    if B[f"F{rr}"].number_format != "0.000": B[f"F{rr}"].number_format = "#,##0"
    B[f"F{rr}"].font = BOLD
widths(B, [6, 52, 12, 8, 12, 16]); landscape(B)

# =====================================================================================
# FINANCIAL
# =====================================================================================
Fs = wb.create_sheet("Financial")
title(Fs, "Financial Analysis – 25-Year Cash Flow (USD)", "Savings use the flat avoided tariff on Inputs; see the TOU sheet for value by tariff period.")
header(Fs, 4, ["Year", "Generation (kWh)", "Tariff (USD/kWh)", "Savings", "O&M", "Inverter replacement", "Net cash flow",
               "Cumulative", "Discount factor", "Disc. cash flow", "Disc. generation", "Disc. costs (O&M + repl.)"], height=32)
y0 = 5
Fs[f"A{y0}"] = 0; Fs[f"G{y0}"] = f"=-{N['capex']}"; Fs[f"H{y0}"] = f"=G{y0}"; Fs[f"I{y0}"] = 1; Fs[f"J{y0}"] = f"=G{y0}"
for k in range(1, 26):
    rr = y0 + k
    Fs[f"A{rr}"] = k
    Fs[f"B{rr}"] = f"={N['y1']}" if k == 1 else f"={N['y1']}*(1-{N['deg1']})*(1-{N['deg']})^(A{rr}-1)"
    Fs[f"C{rr}"] = f"={N['tar']}*(1+{N['esc']})^(A{rr}-1)"
    Fs[f"D{rr}"] = f"=B{rr}*C{rr}"
    Fs[f"E{rr}"] = f"={N['om0']}*(1+{N['omesc']})^(A{rr}-1)"
    Fs[f"F{rr}"] = f"=IF(A{rr}={N['repy']},{N['c_inv']}*{N['ninv']},0)"
    Fs[f"G{rr}"] = f"=D{rr}-E{rr}-F{rr}"
    Fs[f"H{rr}"] = f"=H{rr-1}+G{rr}"
    Fs[f"I{rr}"] = f"=1/(1+{N['disc']})^A{rr}"
    Fs[f"J{rr}"] = f"=G{rr}*I{rr}"; Fs[f"K{rr}"] = f"=B{rr}*I{rr}"; Fs[f"L{rr}"] = f"=(E{rr}+F{rr})*I{rr}"
ye = y0 + 25
for rr in range(y0, ye + 1):
    for col, f in zip("ABCDEFGHIJKL", ["0", "#,##0", "0.000", "#,##0", "#,##0", "#,##0", "#,##0;(#,##0)", "#,##0;(#,##0)", "0.0000", "#,##0;(#,##0)", "#,##0", "#,##0"]):
        Fs[f"{col}{rr}"].number_format = f; Fs[f"{col}{rr}"].border = BOX; Fs[f"{col}{rr}"].font = font()
rr = ye + 1
Fs[f"A{rr}"] = "Total"
for col in "BDEFGJKL": Fs[f"{col}{rr}"] = f"=SUM({col}{y0}:{col}{ye})"
for col in "ABCDEFGHIJKL": Fs[f"{col}{rr}"].font = BOLD; Fs[f"{col}{rr}"].fill = BAND; Fs[f"{col}{rr}"].border = BOX
for col, f in zip("BDEFGJKL", ["#,##0", "#,##0", "#,##0", "#,##0", "#,##0;(#,##0)", "#,##0;(#,##0)", "#,##0", "#,##0"]): Fs[f"{col}{rr}"].number_format = f
tr = rr
r = tr + 2
r = section(Fs, r, "Results")
cfR, cumR = f"G{y0}:G{ye}", f"H{y0}:H{ye}"
res = [
    ("Investment (EPC)", f"={N['capex']}", "USD", "#,##0", "capex_r"),
    ("Year-1 savings", f"=D{y0+1}", "USD", "#,##0", "sav1"),
    ("Simple payback", f"=COUNTIF({cumR},\"<0\")-1+(-INDEX({cumR},COUNTIF({cumR},\"<0\")))/INDEX({cfR},COUNTIF({cumR},\"<0\")+1)", "years", "0.0", "pb"),
    ("Project IRR (25 years)", f"=IRR({cfR})", "", "0.0%", "irr"),
    ("NPV at discount rate", f"=G{y0}+NPV({N['disc']},G{y0+1}:G{ye})", "USD", "#,##0", "npv"),
    ("LCOE", f"=({N['capex']}+L{tr})/K{tr}", "USD/kWh", "0.000", "lcoe"),
    ("25-year generation", f"=B{tr}/1000", "MWh", "#,##0", "gen25"),
    ("25-year net savings (before capex)", f"=G{tr}-G{y0}", "USD", "#,##0", "net25"),
]
for lab, f, u, fmt, nm in res:
    r = kv(Fs, r, lab, f, u, "", nm, fmt)
Fs[f"A{r}"] = "LCOE = (capex + discounted O&M and replacement) ÷ discounted generation. Payback interpolated within the year it turns positive."; Fs[f"A{r}"].font = NOTE
lc = LineChart(); lc.title = "Cumulative Net Cash Flow (USD)"
lc.add_data(Reference(Fs, min_col=8, min_row=4, max_row=ye), titles_from_data=True)
lc.set_categories(Reference(Fs, min_col=1, min_row=y0, max_row=ye))
lc.legend = None; lc.height = 8; lc.width = 18; lc.y_axis.delete = False; lc.x_axis.delete = False
lc.y_axis.title = "USD"; lc.x_axis.title = "Year"; lc.y_axis.number_format = "#,##0"
lc.series[0].graphicalProperties.line.solidFill = "14365D"; lc.series[0].graphicalProperties.line.width = 28000; lc.series[0].smooth = False
Fs.add_chart(lc, "N4")
widths(Fs, [8, 14, 11, 11, 10, 12, 13, 13, 10, 13, 13, 14]); landscape(Fs)

# =====================================================================================
# SENSITIVITY (tariff)
# =====================================================================================
Z = wb.create_sheet("Sensitivity")
title(Z, "Tariff Sensitivity", "Each column recomputes the 25-year cash flow at a different avoided tariff (year 1).")
tariffs = [0.09, 0.10, 0.12, 0.14, 0.16]
header(Z, 4, ["Avoided tariff (USD/kWh)"] + [""] * 0 + ["Payback (yrs)", "IRR", "NPV (USD)"])
cols = ["F", "G", "H", "I", "J"]
hb = 12
Z[f"E{hb}"] = "Year"; Z[f"E{hb}"].font = HEAD; Z[f"E{hb}"].fill = HFILL
for j, t in enumerate(tariffs):
    c = cols[j]
    Z[f"{c}{hb-1}"] = t; Z[f"{c}{hb-1}"].font = BLUE; Z[f"{c}{hb-1}"].fill = YEL; Z[f"{c}{hb-1}"].number_format = "0.000"
    Z[f"{c}{hb}"] = f"Cash flow @ {c}{hb-1}"; Z[f"{c}{hb}"].font = HEAD; Z[f"{c}{hb}"].fill = HFILL
    for k in range(0, 26):
        rr = hb + 1 + k; fr = y0 + k
        Z[f"E{rr}"] = k
        if k == 0: Z[f"{c}{rr}"] = f"=Financial!G{fr}"
        else: Z[f"{c}{rr}"] = f"=Financial!B{fr}*{c}${hb-1}*(1+{N['esc']})^(E{rr}-1)-Financial!E{fr}-Financial!F{fr}"
        Z[f"{c}{rr}"].number_format = "#,##0;(#,##0)"; Z[f"{c}{rr}"].font = GRN if k == 0 else font()
Z[f"E{hb-1}"] = "Tariff →"; Z[f"E{hb-1}"].font = BOLD
cumc = ["L", "M", "N", "O", "P"]
Z[f"K{hb}"] = "";
for j in range(5):
    c, cc = cols[j], cumc[j]
    Z[f"{cc}{hb}"] = f"Cumulative @ {c}{hb-1}"; Z[f"{cc}{hb}"].font = HEAD; Z[f"{cc}{hb}"].fill = HFILL
    for k in range(0, 26):
        rr = hb + 1 + k
        Z[f"{cc}{rr}"] = f"={c}{rr}" if k == 0 else f"={cc}{rr-1}+{c}{rr}"
        Z[f"{cc}{rr}"].number_format = "#,##0;(#,##0)"; Z[f"{cc}{rr}"].font = font()
last = hb + 26
for j in range(5):
    rr = 5 + j; c, cc = cols[j], cumc[j]
    cf, cu = f"{c}{hb+1}:{c}{last}", f"{cc}{hb+1}:{cc}{last}"
    Z[f"A{rr}"] = f"={c}{hb-1}"; Z[f"A{rr}"].number_format = "0.000"
    Z[f"B{rr}"] = f"=COUNTIF({cu},\"<0\")-1+(-INDEX({cu},COUNTIF({cu},\"<0\")))/INDEX({cf},COUNTIF({cu},\"<0\")+1)"
    Z[f"C{rr}"] = f"=IRR({cf})"; Z[f"D{rr}"] = f"={c}{hb+1}+NPV({N['disc']},{c}{hb+2}:{c}{last})"
    for col, f in zip("BCD", ["0.0", "0%", "#,##0"]): Z[f"{col}{rr}"].number_format = f
    for col in "ABCD": Z[f"{col}{rr}"].border = BOX; Z[f"{col}{rr}"].font = font()
widths(Z, [24, 14, 10, 14, 8, 14, 14, 14, 14, 14, 2, 15, 15, 15, 15, 15]); landscape(Z)

# =====================================================================================
# SUMMARY (first sheet)
# =====================================================================================
Su = wb.create_sheet("Summary", 0)
title(Su, "Kampala Marriott Hotel – Rooftop Solar PV: Summary of Workings",
      "185.4 kWp grid-tied, zero-export, no battery · Mezzanine roof (D18102-DD-A-104) · All values link to the working sheets.")
header(Su, 4, ["Item", "Value", "Unit", "Sheet"])
r = 5
summ = [
    ("System", None, None, None, None),
    ("Modules", N["nmod"], "nos", "Layout", "0"),
    ("Module rating", N["pmod"], "Wp", "Inputs", "0"),
    ("Plant capacity (DC)", N["kwp"], "kWp", "Layout", "0.0"),
    ("Inverters", f'{N["ninv"]}&" × "&{N["pinv"]}&" kW"', "", "Inputs", None),
    ("Inverter capacity (AC)", N["acTot"], "kW", "Electrical", "0"),
    ("DC/AC ratio", N["dcac"], "", "Electrical", "0.00"),
    ("Tilt", N["tilt"], "°", "Inputs", "0"),
    ("Tables (2P / 1P)", f'{N["t2"]}&" / "&{N["t1"]}', "", "Layout", None),
    ("Energy", None, None, None, None),
    ("Year-1 generation", N["y1"], "kWh", "Generation", "#,##0"),
    ("Average monthly generation", f"{N['y1']}/12", "kWh", "Generation", "#,##0"),
    ("Share of hotel consumption", N["share"], "", "Generation", "0.0%"),
    ("Solar in shoulder period", f"'TOU Impact'!$E${sr0+2}", "", "TOU Impact", "0.0%"),
    ("Solar in peak period", f"'TOU Impact'!$E${sr0+3}", "", "TOU Impact", "0.0%"),
    ("Bill reduction (TOU rates)", f"'TOU Impact'!$J${tot_row+1}", "", "TOU Impact", "0.00%"),
    ("Value per solar kWh (TOU)", N["touVal"], "USD/kWh", "TOU Impact", "0.000"),
    ("Cost & return", None, None, None, None),
    ("Budget EPC cost (excl. taxes)", N["capex"], "USD", "BOQ", "#,##0"),
    ("Specific cost", f"{N['capex']}/({N['kwp']}*1000)", "USD/Wp", "BOQ", "0.000"),
    ("Mounting structure (Enerack, CIF Mombasa)", N["strCIF"], "USD", "Structure", "#,##0"),
    ("Year-1 savings", N["sav1"], "USD", "Financial", "#,##0"),
    ("Simple payback", N["pb"], "years", "Financial", "0.0"),
    ("Project IRR", N["irr"], "", "Financial", "0.0%"),
    ("NPV (25 years)", N["npv"], "USD", "Financial", "#,##0"),
    ("LCOE", N["lcoe"], "USD/kWh", "Financial", "0.000"),
    ("Checks", None, None, None, None),
    ("Row shading", f"Layout!$B${[row for row in range(1, 80) if L[f'A{row}'].value == 'Shading check'][0]}", "", "Layout", None),
    ("String voltages", f'IF(AND({N["vocmaxStr"]}<={N["vdcmax"]},{N["vmpminStr"]}>={N["vmpptmin"]}),"OK","CHECK")', "", "Electrical", None),
    ("Modules in strings = modules on roof", f'IF({N["modsInv"]}={N["nmod"]},"OK","MISMATCH")', "", "Electrical", None),
]
for item in summ:
    lab = item[0]
    if item[1] is None:
        Su[f"A{r}"] = lab; Su[f"A{r}"].font = SUB; r += 1; continue
    _, f, u, sh, fmt = item
    Su[f"A{r}"] = lab; Su[f"B{r}"] = "=" + f; Su[f"C{r}"] = u; Su[f"D{r}"] = sh
    Su[f"B{r}"].font = GRN
    if fmt: Su[f"B{r}"].number_format = fmt
    Su[f"B{r}"].alignment = Alignment(horizontal="right")
    for c in "ABCD":
        Su[f"{c}{r}"].border = BOX
        if c != "B": Su[f"{c}{r}"].font = font(color="5B6673") if c == "D" else font()
    r += 1
r += 1
Su[f"A{r}"] = "Colour code: yellow + blue = input · black = formula · green = link to another sheet."; Su[f"A{r}"].font = NOTE
widths(Su, [44, 18, 12, 14]); landscape(Su)

out = os.path.join(HERE, "Kampala_Marriott_PV_Workings.xlsx")
wb.save(out); print(out)
