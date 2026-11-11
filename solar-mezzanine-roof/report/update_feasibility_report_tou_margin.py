"""Feasibility report: all solar counted in the shoulder band (no peak-hour solar) and profit margin built into
modules + installation (no margin rows shown). Usage: python3 update_feasibility_report_tou_margin.py <in.docx> <out.docx>"""
import sys, os, json
import docx
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from openpyxl import load_workbook

HERE = os.path.dirname(os.path.abspath(__file__))
F = json.load(open(os.path.join(HERE, "proposal_fin_v3.json"))); T = F["tou_rows"]
B = load_workbook(os.path.join(HERE, "Kampala_Marriott_PV_Workings_P50_PVsyst.xlsx"), data_only=True)["BOQ"]
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
# key findings
for row in table_with("Item").rows:
    if row.cells[0].text.strip() == "Year-1 savings": set_cell(row.cells[1], f"USD {T['Total'][8]:,.0f}")
# TOU table 3
for row in table_with("Period").rows[1:]:
    k = row.cells[0].text.strip()
    if k not in T: continue
    r = T[k]
    vals = [f"{r[1]:,.0f}", f"{r[2]:.1f}", f"{r[3]*100:.1f}%", f"{r[4]:,.0f}", f"{r[5]*100:.2f}%", f"{r[6]:,.0f}", f"{r[7]:,.0f}", f"{r[8]:,.0f}"]
    for c, v in zip(row.cells[1:], vals): set_cell(c, v)
# note under table 3
for p in d.paragraphs:
    if p.text.strip().startswith("*Forecasted Energy demand"):
        p.runs[-1].text = p.runs[-1].text + "  All solar output (including the small output just after 18:00) is counted in the shoulder period."
        break
# BOQ table 7
t = table_with("No.")
amt = {r: B.cell(r, 6).value for r in range(4, 18)}
for row in list(t.rows):
    k = row.cells[1].text.strip()
    if k.startswith("Supply of PV modules"):
        set_cell(row.cells[3], f"{amt[4]/185380:.3f}"); set_cell(row.cells[4], f"{amt[4]:,.0f}")
    elif k.startswith("Installation, testing"):
        set_cell(row.cells[4], f"{amt[10]:,.0f}")
    elif k == "Sub-total":
        set_cell(row.cells[4], f"{amt[12]:,.0f}")
    elif k in ("Total budget EPC cost (excluding taxes)", "Profit margin"):
        t._tbl.remove(row._tr)
    elif k.startswith("Total Project Value"):
        set_cell(row.cells[4], f"{amt[14]:,.0f}")
st = d.settings.element; uf = st.find(qn("w:updateFields"))
if uf is None: uf = OxmlElement("w:updateFields"); st.append(uf)
uf.set(qn("w:val"), "true")
d.save(sys.argv[2]); print("saved", sys.argv[2])
