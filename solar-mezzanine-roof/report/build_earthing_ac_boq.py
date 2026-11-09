"""Revised Earthing BOQ (panel-to-panel bonding) and revised AC BOQ (C3 200 m, 240 mm²) -> Kampala_Marriott_Earthing_AC_BOQ.xlsx"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

HERE = os.path.dirname(os.path.abspath(__file__))
NAVY, BAND, YEL, GRN, BLUE = "14365D", "EEF2F6", "FFFF00", "92D050", "0000FF"
thin = Side(style="thin", color="9AA4AE"); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
F = lambda **k: Font(name="Arial", **({"size": 10} | k))

def sheet(ws, title, rows, allowance, note):
    ws["A1"] = title; ws["A1"].font = F(bold=True, size=13, color=NAVY)
    ws["A2"] = "Kampala Marriott Hotel – 185.4 kWp rooftop PV · NileSun Power Ltd · yellow = input, blue = estimated rate (confirm)"
    ws["A2"].font = F(italic=True, size=9, color="5B6673")
    hdr = ["No.", "Item", "Quantity", "Unit", "Rate (USD)", "Amount (USD)", "Quantity working"]
    for c, h in enumerate(hdr, 1):
        x = ws.cell(4, c, h); x.font = F(bold=True, color="FFFFFF"); x.fill = PatternFill("solid", fgColor=NAVY)
        x.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True); x.border = BOX
    r = 5
    for i, (item, q, u, rate, est, work) in enumerate(rows, 1):
        vals = [i, item, q, u, rate, f"=C{r}*E{r}", work]
        for c, v in enumerate(vals, 1):
            x = ws.cell(r, c, v); x.border = BOX; x.font = F()
            x.alignment = Alignment(vertical="center", wrap_text=c in (2, 7), horizontal="center" if c in (1, 4) else None)
        ws.cell(r, 3).fill = PatternFill("solid", fgColor=YEL); ws.cell(r, 5).fill = PatternFill("solid", fgColor=YEL)
        if est: ws.cell(r, 5).font = F(color=BLUE, bold=True)
        ws.cell(r, 3).number_format = "#,##0"; ws.cell(r, 5).number_format = "#,##0.00"; ws.cell(r, 6).number_format = "#,##0"
        ws.cell(r, 7).font = F(color="5B6673")
        r += 1
    first, last = 5, r - 1
    for lab, f, col in (("Total (bottom-up)", f"=SUM(F{first}:F{last})", None),
                        ("Current BOQ allowance (lump sum)", allowance, "008000"),
                        ("Difference (bottom-up − allowance)", f"=F{last+1}-F{last+2}", None)):
        ws.cell(r, 2, lab).font = F(bold=True)
        x = ws.cell(r, 6, f); x.number_format = '#,##0;(#,##0)'; x.font = F(bold=True, color=col) if col else F(bold=True)
        for c in range(1, 8):
            ws.cell(r, c).fill = PatternFill("solid", fgColor=BAND); ws.cell(r, c).border = BOX
        r += 1
    ws.cell(r + 1, 1, note).font = F(italic=True, size=9, color="5B6673")
    for col, w in zip("ABCDEFG", (6, 62, 10, 7, 11, 13, 62)): ws.column_dimensions[col].width = w
    ws.freeze_panes = "A5"
    ws.page_setup.orientation = "landscape"; ws.page_setup.fitToWidth = 1; ws.sheet_properties.pageSetUpPr.fitToPage = True

wb = Workbook()
ws = wb.active; ws.title = "Earthing BOQ"
sheet(ws, "Earthing & Bonding BOQ – panel-to-panel bonding (revised)", [
    ("Panel-to-panel bonding jumpers 6 mm² Cu, green/yellow, UV-resistant", 385, "m", 0.80, True, "13 rows × 22 jumpers × 1.3 m (286 nos) + 7 table-to-rail jumpers"),
    ("Row-end earth leads 16 mm² Cu, green/yellow", 60, "m", 2.50, False, "13 rows × 2 ends (26 nos), last panel → tray earth"),
    ("Tray earth conductor 35 mm² Cu (array → ACCP earth bar)", 45, "m", 5.00, False, "along east-corridor tray to inverter station"),
    ("Crimp lugs, tinned Cu, 6 mm² / M6", 590, "nos", 0.15, True, "2 per jumper"),
    ("Stainless M6 bolt + serrated (star) washer + nut", 600, "sets", 0.30, True, "1 per lug at panel earthing holes"),
    ("Bimetallic (Al–Cu) clamps on rails / tray earth", 40, "nos", 3.00, False, "7 tables × 2 + 26 row-end connections"),
    ("Inverter, DC SPD unit & ACCP earth bonding (16 mm² Cu + lugs)", 5, "sets", 25.00, False, "2 inverters + 2 DC SPD units + ACCP earth bar"),
    ("Air-termination rods 1 m with concrete bases (array perimeter)", 6, "nos", 80.00, False, "only if the array is outside the existing LPS protection zone"),
    ("Connection to existing LPS: clamps, test joints, separation-distance fittings", 1, "lot", 250.00, False, "IEC 62305 tie-in"),
    ("Earth pit: 1.5 m Cu-bonded rod", 1, "nos", 350.00, False, "only if the building earth is inadequate"),
    ("Earthing labels & warning signs", 1, "lot", 50.00, False, "lot"),
], 2500, "E3 (120 mm² Cu ≈ 200 m, ACCP earth bar → MET) is included in the AC BOQ sheet.")

ws2 = wb.create_sheet("AC BOQ")
sheet(ws2, "AC System BOQ – revised (C3 ≈ 200 m, 4C × 240 mm²)", [
    ("ACCP enclosure IP65, 400 A busbar, wiring, assembly", 1, "nos", 1000.00, True, "AC combiner panel on the roof"),
    ("MCCB 4P 160 A (Ir 140 A), Icu ≥ 25 kA – inverter incomers Q1/Q2", 2, "nos", 300.00, True, "1 per inverter (max AC 133.7 A)"),
    ("Switch-disconnector 4P 400 A – Q3 roof isolator", 1, "nos", 500.00, True, "replaces 250 A MCCB + 250 A switch"),
    ("AC SPD Type 2, 3P+N, Uc 320 Vac, 40 kA (ACCP)", 1, "nos", 250.00, False, ""),
    ("Cable 4C × 50 mm² Cu XLPE (C1, C2 inverter → ACCP)", 15, "m", 25.00, False, "layout: C1 4.5 m + C2 2.3 m + drops/terminations"),
    ("Earth cable 25 mm² Cu (E1, E2 inverter → ACCP)", 15, "m", 4.00, False, "same route"),
    ("Cable 4C × 240 mm² Cu XLPE/SWA (C3 ACCP → MLVS)", 200, "m", 110.00, True, "route length (confirm); VD ≈ 2.0 % at 232 A"),
    ("Earth cable 120 mm² Cu (E3 ACCP → MET)", 200, "m", 15.00, True, "same route"),
    ("Cable ladder/tray 300 mm HDG (roof section)", 20, "m", 18.00, False, "roof ≈ 17.4 m; LV room cable provision available"),
    ("Cable glands, lugs, terminations (240 mm²)", 1, "lot", 350.00, True, "lot"),
    ("MLVS solar incomer: existing Masterpact NW10 H1 (no new breaker)", 0, "nos", 900.00, False, "existing breaker used – Ir set 400 A"),
    ("MLVS busbar connection & NW10 H1 setting / test", 1, "lot", 300.00, False, ""),
    ("Inverter station frame & sun-shade canopy (incl. DC units)", 2, "nos", 300.00, False, "1 per inverter bay"),
], 13140, "Rates in blue are estimates for new / upsized items – confirm with suppliers.")
out = os.path.join(HERE, "Kampala_Marriott_Earthing_AC_BOQ.xlsx"); wb.save(out); print(out)
