"""Final workings (Nov 2026): BOQ (contingency 7 %, AC system incl. 4C×240 mm² Al cable at USD 146/m, transport +500),
total project value, C3/E3 cable description. Run after update_feasibility_report_bill.py.
Usage: python3 update_feasibility_report_final.py <in.docx> <out.docx>"""
import sys, os, json
import docx

HERE = os.path.dirname(os.path.abspath(__file__))
F = json.load(open(os.path.join(HERE, "proposal_fin_v8.json")))
capex, B = F["capex"], {int(k): v for k, v in F["boq"].items()}
d = docx.Document(sys.argv[1])

def set_cell(cell, text):
    ps = cell.paragraphs
    if ps[0].runs:
        ps[0].runs[0].text = text
        for r in ps[0].runs[1:]: r.text = ""
    else: ps[0].add_run(text)
def table_with(first):
    for t in d.tables:
        if t.rows[0].cells[0].text.strip().startswith(first): return t
    print("NOT FOUND table", first)
def par_starting(s):
    for p in d.paragraphs:
        if p.text.strip().startswith(s): return p
    print("NOT FOUND par", s)
def set_par(p, text):
    p.runs[0].text = text
    for r in p.runs[1:]: r.text = ""

wp = capex / 185380
# executive summary box (row 0 values, row 1 labels)
t = d.tables[3]
set_cell(t.rows[0].cells[2], f"USD {capex/1000:.0f}k")
for c in t.rows[1].cells:
    if "USD/Wp" in c.text:
        for p in c.paragraphs:
            for r in p.runs:
                if "USD/Wp" in r.text: r.text = r.text.split("(")[0] + f"({wp:.2f} USD/Wp)"
# key findings + finance table
for row in table_with("Item").rows:
    if row.cells[0].text.strip() == "Total project cost": set_cell(row.cells[1], f"USD {capex:,.0f}")
for row in table_with("Total investment").rows:
    if row.cells[0].text.strip().startswith("Total investment"): set_cell(row.cells[1], f"USD {capex:,.0f}")
# BOQ table 7
t = table_with("No.")
vals = {"Supply of PV modules": (f"{B[4]/185380:.3f}", B[4]), "Supply of DC system": (f"USD {B[7]/185380:.3f}/Wp", B[7]),
        "Supply of AC system": ("Lump sum", B[8]), "Earthing": ("Lump sum", B[9]), "Installation, testing": ("Lump sum", B[10]), "Transport, logistics": ("Lump sum", B[11])}
for row in t.rows:
    k = row.cells[1].text.strip()
    for key, (rate, amt) in vals.items():
        if k.startswith(key): set_cell(row.cells[3], rate); set_cell(row.cells[4], f"{amt:,.0f}")
    if k == "Sub-total": set_cell(row.cells[4], f"{B[12]:,.0f}")
    if k == "Contingency": set_cell(row.cells[3], "7 %"); set_cell(row.cells[4], f"{B[13]:,.0f}")
    if k.startswith("Total Project Value"): set_cell(row.cells[4], f"{capex:,.0f}")
    if k == "Specific cost": set_cell(row.cells[4], f"{wp:.3f} USD/Wp")
# electrical description
set_par(par_starting("AC combiner panel →"), "AC combiner panel → 4C × 240 mm² Al XLPE/SWA (≈ 200 m) → existing Masterpact NW10 H1 (1000 A) solar incomer on the main LV switchboard; the cable’s steel-wire armour serves as the protective earth (glands earthed).")
# cash-flow table, year 0
for row in table_with("Year").rows[1:]:
    if row.cells[0].text.strip() == "0": set_cell(row.cells[4], f"({capex:,.0f})")
# expansion
for row in table_with("Option").rows:
    a = row.cells[0].text
    if a.startswith("Phase 1"): set_cell(row.cells[3], f"{capex:,.0f}")
    if a.startswith("Phase 2"): set_cell(row.cells[3], "To be determined"); set_cell(row.cells[4], "Budget after canopy design and survey")
    if a.startswith("Indicative total"): set_cell(row.cells[3], "To be determined")
d.save(sys.argv[2]); print("saved", sys.argv[2])
