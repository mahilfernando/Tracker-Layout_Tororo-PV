"""One-page commercial quotation (A4) for the Kampala Marriott rooftop PV - no cost breakdown.
Figures from Kampala_Marriott_PV_Workings.xlsx (client's version, Total Project Value USD 121,115).
Run: python3 build_quotation.py  -> Kampala_Marriott_PV_Quotation.xlsx (then convert to PDF).
"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

HERE = os.path.dirname(os.path.abspath(__file__))
F = "Arial"
NAVY, BAND, ACC, YEL = "14365D", "EEF2F6", "C27A00", "FFF2CC"
def font(**k): return Font(name=F, **k)
thin = Side(style="thin", color="9AA4AE"); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
wb = Workbook(); ws = wb.active; ws.title = "Quotation"
widths = {"A": 6, "B": 30, "C": 26, "D": 9, "E": 16, "F": 22}
for k, v in widths.items(): ws.column_dimensions[k].width = v
r = 1

def merge(row, c1, c2, value=None, f=None, fill=None, al=None, h=None, border=True):
    ws.merge_cells(f"{c1}{row}:{c2}{row}")
    cell = ws[f"{c1}{row}"]
    if value is not None: cell.value = value
    if f: cell.font = f
    if fill: cell.fill = PatternFill("solid", fgColor=fill)
    cell.alignment = al or Alignment(vertical="center", wrap_text=True)
    if h: ws.row_dimensions[row].height = h
    if border:
        cols = "ABCDEF"; i1, i2 = cols.index(c1), cols.index(c2)
        for c in cols[i1:i2 + 1]: ws[f"{c}{row}"].border = BOX
    return cell

def section(title):
    global r
    merge(r, "A", "F", title, font(bold=True, color="FFFFFF", size=11), NAVY, Alignment(vertical="center", indent=1), 20)
    r += 1

def kv(label, value, label2=None, value2=None, bold_value=False, h=16, fill_value=None):
    """Two key/value pairs per row: A:B label, C value | D:E label, F value (or one pair spanning C:F)."""
    global r
    merge(r, "A", "B", label, font(bold=True, size=9))
    if label2 is None:
        merge(r, "C", "F", value, font(size=9, bold=bold_value), fill_value)
    else:
        merge(r, "C", "C", value, font(size=9, bold=bold_value), fill_value)
        merge(r, "D", "E", label2, font(bold=True, size=9))
        merge(r, "F", "F", value2, font(size=9, bold=bold_value), fill_value)
    ws.row_dimensions[r].height = h
    r += 1

# ---------------- header ----------------
from openpyxl.drawing.image import Image as XLImage
logo = XLImage(os.path.join(HERE, "nilesun_logo.png")); logo.width, logo.height = 74, 75
ws.add_image(logo, "A1")
merge(r, "C", "F", "Nile Sun Power Limited\nKampala, Uganda", font(bold=True, size=11, color=NAVY), None,
      Alignment(horizontal="right", vertical="center", wrap_text=True), 60, border=False); r += 1
merge(r, "A", "F", "Commercial Proposal & Quotation – Rooftop Solar PV System", font(bold=True, size=16, color=NAVY),
      None, Alignment(horizontal="center", vertical="center"), 34); r += 1
merge(r, "A", "F", "Turnkey EPC supply, installation and commissioning · 185.4 kWp grid-tied · zero export · no battery",
      font(italic=True, size=9, color="5B6673"), None, Alignment(horizontal="center", vertical="center"), 16, border=False); r += 1
kv("Quotation No.:", "Q-KMH-PV-2026-001", "Date:", "05-11-2026")
kv("Revision:", "A", "Valid until:", "05-12-2026 (30 days)")

# ---------------- 1. project ----------------
section("1. Project Details")
kv("Project name:", "Kampala Marriott Hotel – 185.4 kWp Rooftop Solar PV (mezzanine roof)")
kv("System:", "Grid-tied solar PV, self-consumption, zero-export control, no battery storage")
kv("Location:", "Kampala, Uganda · 0°18'11.34\"N, 32°35'13.76\"E · Ref. drawing D18102-DD-A-104")

# ---------------- 2. client / supplier ----------------
section("2. Client & Supplier Details")
kv("Client:", "Kampala Marriott Hotel", "Supplier:", "Nile Sun Power Limited", h=26)
kv("Address:", "Kampala, Uganda", "Address:", "Kampala, Uganda", h=18)
kv("Contact:", "", "Contact:", "Mr. Mahil", fill_value=None)
kv("Mobile / Email:", "", "Mobile / Email:", "+94 773 55 96 82 · mahil@windforce.lk", h=28)
for rr in (r - 2, r - 1): ws[f"C{rr}"].fill = PatternFill("solid", fgColor=YEL)

# ---------------- 3. quotation ----------------
section("3. Quotation (Turnkey EPC)")
for col, h in zip("ABCDEF", ["No.", "Scope of supply & works", "", "Qty", "Unit", "Total Price (USD)"]):
    c = ws[f"{col}{r}"]; c.value = h if h else None
    c.font = font(bold=True, size=9, color=NAVY); c.fill = PatternFill("solid", fgColor=BAND); c.border = BOX
    c.alignment = Alignment(horizontal="center", vertical="center")
ws.merge_cells(f"B{r}:C{r}"); ws.row_dimensions[r].height = 18; r += 1
items = [("PV modules – 620 Wp bifacial N-type TOPCon (Tier-1)", "299", "nos"),
         ("String inverters – 80 kW, 1100 V, multi-MPPT", "2", "nos"),
         ("Ballasted aluminium mounting structure, 10° tilt", "1", "lot"),
         ("DC system – PV cable, connectors, string isolators, cable tray", "1", "lot"),
         ("AC system – AC combiner panel, MCCBs, cabling to main LV switchboard", "1", "lot"),
         ("Smart data logger, remote monitoring & zero-export control", "1", "set"),
         ("Earthing & lightning protection integration", "1", "lot"),
         ("Installation, testing & commissioning", "1", "lot"),
         ("Transport, logistics & customs clearing to site", "1", "lot")]
first = r
for i, (d, q, u) in enumerate(items, start=1):
    ws[f"A{r}"] = i; ws[f"B{r}"] = d; ws[f"D{r}"] = q; ws[f"E{r}"] = u
    ws.merge_cells(f"B{r}:C{r}")
    for c in "ABCDE":
        ws[f"{c}{r}"].border = BOX; ws[f"{c}{r}"].font = font(size=9)
        ws[f"{c}{r}"].alignment = Alignment(horizontal="center" if c in "ADE" else "left", vertical="center", wrap_text=True)
    ws.row_dimensions[r].height = 16
    r += 1
ws.merge_cells(f"F{first}:F{r-1}")
c = ws[f"F{first}"]; c.value = 121115; c.number_format = '"USD "#,##0'
c.font = font(bold=True, size=16, color=ACC); c.alignment = Alignment(horizontal="center", vertical="center")
for rr in range(first, r): ws[f"F{rr}"].border = BOX
merge(r, "A", "E", "TOTAL TURNKEY EPC PRICE (excluding VAT and other applicable taxes)", font(bold=True, size=10),
      BAND, Alignment(horizontal="right", vertical="center", indent=1), 20)
ws[f"F{r}"] = 121115; ws[f"F{r}"].number_format = '"USD "#,##0'; ws[f"F{r}"].font = font(bold=True, size=11, color=NAVY)
ws[f"F{r}"].fill = PatternFill("solid", fgColor=BAND); ws[f"F{r}"].border = BOX; ws[f"F{r}"].alignment = Alignment(horizontal="center", vertical="center")
r += 1
merge(r, "A", "F", "Equivalent to USD 0.65 per Wp · Amount in words: One hundred twenty-one thousand one hundred fifteen US Dollars only.",
      font(italic=True, size=8.5, color="5B6673"), None, None, 15); r += 1

# ---------------- 5. commercial terms ----------------
section("4. Payment & Commercial Terms")
kv("Price basis:", "Turnkey EPC, delivered, installed and commissioned at site, Kampala. Currency: USD.")
kv("Payment terms:", "30 % advance with purchase order · 60 % on delivery of main equipment to site · 10 % on commissioning", h=26)
kv("Taxes:", "Prices exclude VAT, withholding tax and any other statutory levies, which shall be charged as applicable.", h=26)

# ---------------- 6. delivery ----------------
section("5. Delivery & Project Schedule")
kv("Programme:", "Equipment delivery 8–10 weeks from PO and advance payment; installation and commissioning ≈ 4 weeks after delivery (≈ 12–14 weeks in total).", h=26)

# ---------------- 7. warranties ----------------
section("6. Warranties")
kv("PV modules:", "12-yr product · 30-yr linear power", "Inverters:", "5 years (extendable)")
kv("Mounting structure:", "10 years", "Workmanship:", "2 years from commissioning")

# ---------------- 8. notes ----------------
section("7. Notes & Exclusions")
notes = ["1. Final quantities are subject to detailed engineering and site survey; price will be adjusted for any change in scope.",
         "2. Excluded: roof structural strengthening or waterproofing works, battery storage, utility/permit fees, and works not listed above.",
         "3. Client to provide roof access, a spare 250 A way on the main LV switchboard, and power/water during installation.",
         "4. Energy and savings estimates are given in the accompanying proposal and are indicative only."]
for n in notes:
    merge(r, "A", "F", n, font(size=8.5), None, Alignment(vertical="center", wrap_text=True), 18); r += 1

# ---------------- signatures ----------------
r += 1
merge(r, "A", "C", "For Nile Sun Power Limited", font(bold=True, size=9), None, None, 16, border=False)
merge(r, "D", "F", "Accepted by Client (Kampala Marriott Hotel)", font(bold=True, size=9), None, None, 16, border=False); r += 1
merge(r, "A", "C", "\n\nSignature / Name / Date: ____________________", font(size=9), None, Alignment(vertical="bottom", wrap_text=True), 40, border=False)
merge(r, "D", "F", "\n\nSignature / Name / Date: ____________________", font(size=9), None, Alignment(vertical="bottom", wrap_text=True), 40, border=False)

ws.page_setup.paperSize = ws.PAPERSIZE_A4; ws.page_setup.orientation = "portrait"
ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 1; ws.sheet_properties.pageSetUpPr.fitToPage = True
ws.page_margins.left = ws.page_margins.right = 0.4; ws.page_margins.top = ws.page_margins.bottom = 0.4
ws.print_area = f"A1:F{r}"
ws.sheet_view.showGridLines = False
out = os.path.join(HERE, "Kampala_Marriott_PV_Quotation.xlsx"); wb.save(out); print(out, "rows", r)
