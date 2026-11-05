"""Mounting-structure BOQ (Enerack quote ERKI20261104TP as issued) -> Enerack_Structure_BOQ.xlsx."""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

HERE = os.path.dirname(os.path.abspath(__file__))
F = "Arial"
def font(**k): return Font(name=F, **k)
BLUE, BOLD = font(color="0000FF"), font(bold=True)
HEAD, TITLE, NOTE = font(bold=True, color="FFFFFF"), font(bold=True, size=14, color="14365D"), font(italic=True, size=9, color="5B6673")
SUB = font(bold=True, size=11, color="14365D")
HFILL, BAND = PatternFill("solid", fgColor="14365D"), PatternFill("solid", fgColor="EEF2F6")
thin = Side(style="thin", color="C9D0D8"); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)

wb = Workbook(); ws = wb.active; ws.title = "Structure BOQ"
ws["A1"] = "Bill of Quantities – PV Mounting Structure (Enerack Ballast System)"; ws["A1"].font = TITLE
ws["A2"] = "Kampala Marriott Hotel – mezzanine roof rooftop PV, 185.4 kWp · values exactly as quoted by the supplier"; ws["A2"].font = NOTE

info = [("Supplier", "Xiamen Enerack Technology Co., Ltd., Xiamen, China"),
        ("Quote / invoice No.", "ERKI20261104TP"), ("Date", "2026-11-04"),
        ("To", "Tororo PV Power Company Limited, Kampala, Uganda"),
        ("Drawing", "EPJ-26110401 V1.0 (2P and 1P tables, 10° tilt, wind 35 m/s)"),
        ("Module", "2382 × 1134 × 30 mm"), ("Incoterm", "EXW unit prices; freight to Mombasa quoted separately (CIF Mombasa)")]
r = 4
for k, v in info:
    ws[f"A{r}"] = k; ws[f"B{r}"] = v; ws[f"A{r}"].font = font(color="5B6673"); ws[f"B{r}"].font = font()
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=7)
    for c in "AB": ws[f"{c}{r}"].border = BOX
    r += 1
r += 1
hdr = ["No.", "Item No.", "Description", "Qty", "Unit", "Unit price EXW (USD)", "Amount (USD)"]
for j, h in enumerate(hdr):
    c = ws.cell(row=r, column=j + 1, value=h); c.font = HEAD; c.fill = HFILL; c.border = BOX
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
ws.row_dimensions[r].height = 30
QUOTE = [("ERK-R80-3000", "R80 Rail L=3000", 256, 16.64, 4258.56), ("ERK-R80-2630", "R80 Rail L=2630", 32, 14.58, 466.67),
         ("ERK-SFR-R80", "Rail connect", 256, 1.19, 304.64), ("ERK-GRC", "Rail clamp", 795, 0.22, 178.59),
         ("ERK-FEC-30", "30 mm end clamp", 65, 0.30, 19.47), ("ERK-AIC", "Adjustable (30–40 mm) inner clamp", 707, 0.30, 212.10),
         ("ERK-W45-3800", "Pre-assembly L=3800 (2P frame)", 77, 40.40, 3110.80), ("ERK-W45-1400", "Pre-assembly L=1400 (1P frame)", 22, 20.64, 454.08),
         ("ERK-35JL-2725", "Cross L=2725", 140, 6.85, 958.77), ("ERK-M8X70", "M8×70 bolt", 155, 0.20, 31.00),
         ("ERK-ELG-03", "Earthing lug", 33, 0.28, 9.24)]
r += 1; q0 = r
for i, (code, d, q, u, amt) in enumerate(QUOTE, start=1):
    vals = [i, code, d, q, "kits", u, amt]
    for j, v in enumerate(vals):
        c = ws.cell(row=r, column=j + 1, value=v); c.border = BOX
        c.font = BLUE if j in (3, 5, 6) else font()
    ws[f"A{r}"].alignment = Alignment(horizontal="center")
    ws[f"D{r}"].number_format = "#,##0"; ws[f"F{r}"].number_format = "#,##0.00"; ws[f"G{r}"].number_format = "#,##0.00"
    r += 1
q1 = r - 1
tot = [("Sub-total EXW", f"=SUM(G{q0}:G{q1})", f"=SUM(D{q0}:D{q1})"),
       ("Freight cost to Mombasa Port, Kenya", 1300, None),
       ("Total CIF Mombasa", f"=G{r}+G{r+1}", None)]
for k, (lab, val, qty) in enumerate(tot):
    ws[f"C{r}"] = lab; ws[f"G{r}"] = val
    if qty: ws[f"D{r}"] = qty; ws[f"D{r}"].number_format = "#,##0"
    for c in "ABCDEFG": ws[f"{c}{r}"].border = BOX; ws[f"{c}{r}"].fill = BAND
    ws[f"C{r}"].font = BOLD; ws[f"D{r}"].font = BOLD
    ws[f"G{r}"].font = BLUE if k == 1 else BOLD; ws[f"G{r}"].number_format = "#,##0.00"
    r += 1
cif_r = r - 1
r += 1
ws[f"A{r}"] = "Quote terms"; ws[f"A{r}"].font = SUB; r += 1
for t in ["1. Payment: T/T 30 % deposit, balance paid before shipment.",
          "2. Port of destination: Mombasa Port, Kenya.",
          "3. Delivery: 10–15 days after receipt of deposit.",
          "4. CIF price excludes import customs clearance, customs duties and VAT.",
          "5. Line amounts are as printed on the supplier's quote (a few differ from qty × unit price by cents – supplier rounding)."]:
    ws[f"A{r}"] = t; ws[f"A{r}"].font = font(); r += 1
r += 1
ws[f"A{r}"] = "Scope note"; ws[f"A{r}"].font = SUB; r += 1
ws[f"A{r}"] = ("Quote quantities cover 7 × 2P + 2 × 1P tables (99 frames, 32 rail lines, 368 modules). The final layout uses 6 × 2P + 1 × 1P "
               "(77 frames, 26 rail lines, 299 modules, 185.4 kWp). Values kept as quoted – confirm final quantities with Enerack before ordering.")
ws[f"A{r}"].font = font(); ws[f"A{r}"].alignment = Alignment(wrap_text=True, vertical="top")
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7); ws.row_dimensions[r].height = 42
r += 2
ws[f"A{r}"] = "Cost per Wp (CIF, 185.4 kWp plant)"; ws[f"F{r}"] = 185380; ws[f"F{r}"].number_format = "#,##0"; ws[f"F{r}"].font = BLUE
ws[f"E{r}"] = "Wp"; ws[f"G{r}"] = f"=G{cif_r}/F{r}"; ws[f"G{r}"].number_format = "0.000"; ws[f"G{r}"].font = BOLD
ws[f"A{r}"].font = font()
r += 2
ws[f"A{r}"] = "Blue = value from the supplier's quote (edit if the quote is revised); black = formula."; ws[f"A{r}"].font = NOTE
for col, w in zip("ABCDEFG", [20, 16, 36, 10, 8, 18, 16]): ws.column_dimensions[col].width = w
ws.page_setup.orientation = "portrait"; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 1
ws.sheet_properties.pageSetUpPr.fitToPage = True
out = os.path.join(HERE, "Enerack_Structure_BOQ.xlsx"); wb.save(out); print(out)
