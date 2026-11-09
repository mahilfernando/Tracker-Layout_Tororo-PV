"""Update the client's feasibility report (docx) with the new workings (Total Project Value USD 102,789).
Usage: python3 update_feasibility_report.py <in.docx> <out.docx>
Edits text in place (keeps the original formatting), rebuilds the BOQ / finance / sensitivity / cash-flow tables,
fixes section numbering and sets Word to refresh the table of contents on open.
"""
import sys, json, os, copy
import docx
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
F = json.load(open(os.path.join(HERE, "proposal_fin_v2.json")))
src, dst = sys.argv[1], sys.argv[2]
d = docx.Document(src)

def replace_in_par(p, old, new):
    """Replace text that may span several runs; keeps the formatting of the first run of the match."""
    if old not in p.text: return False
    runs = p.runs; full = "".join(r.text for r in runs); i = full.index(old); j = i + len(old)
    pos = 0; first = None
    for r in runs:
        a, b = pos, pos + len(r.text); pos = b
        if b <= i or a >= j:
            continue
        if first is None:
            first = r; r.text = r.text[:i - a] + new + (r.text[j - a:] if b > j else "")
        else:
            r.text = r.text[j - a:] if b > j else ""
    return True

def all_pars():
    for p in d.paragraphs: yield p
    for t in d.tables:
        for row in t.rows:
            for c in row.cells:
                for p in c.paragraphs: yield p

def rep(old, new, must=True):
    n = sum(replace_in_par(p, old, new) for p in all_pars())
    if must and n == 0: print("NOT FOUND:", old)
    return n

def set_cell(cell, text):
    ps = cell.paragraphs
    if ps[0].runs:
        ps[0].runs[0].text = text
        for r in ps[0].runs[1:]: r.text = ""
    else:
        ps[0].add_run(text)
    for p in ps[1:]:
        for r in p.runs: r.text = ""

def set_row(row, vals):
    for c, v in zip(row.cells, vals): set_cell(c, v)

def clone_row(table, src_row, after_row):
    new = copy.deepcopy(src_row._tr); after_row._tr.addnext(new)
    return table.rows[[r._tr for r in table.rows].index(new)]

def del_row(table, row):
    table._tbl.remove(row._tr)

usd = lambda v: f"USD {v:,.0f}"
capex, y1, pb, irr, npv, lcoe = F["capex"], F["cf"][1], F["pb"], F["irr"], F["npv"], F["lcoe"]
sav25, cum = F["sav25"], F["cum"]

# ---------- cover / document control ----------
rep("A – Issued for review", "B – Updated costing and financials")
rep("4 November 2026", "9 November 2026")
t = d.tables[1]
r = clone_row(t, t.rows[1], t.rows[-1])
set_row(r, ["B", "9/11/2026", "Updated costing & financials", "Mahil Fernando", "Prasanna Dissanayake", "Manjula Perera"])
# ---------- executive summary ----------
rep("grid-tiled", "grid-tied")
rep("USD 117k", f"USD {capex/1000:.0f}k")
rep("5.9 yrs", f"{pb:.1f} yrs")
rep("(0.59 USD/Wp)", f"({capex/185380:.2f} USD/Wp)")
rep("Budget EPC cost", "Total project cost")
t = d.tables[4]
for row in t.rows:
    k = row.cells[0].text.strip()
    v = {"Total project cost": usd(capex), "Simple payback": f"{pb:.1f} years", "Project IRR": f"{irr*100:.1f}%",
         "NPV (25 years at 10%)": usd(npv), "Cost of solar energy (LCOE)": f"{lcoe:.3f} USD/kWh"}.get(k)
    if v: set_cell(row.cells[1], v)
# ---------- section numbering ----------
for old, new in (("3.PV Array Layout", "5. PV Array Layout"), ("4. Electrical Design", "6. Electrical Design"),
                 ("4.1 Configuration", "6.1 Configuration"), ("4.3 Single-line arrangement", "6.2 Single-line arrangement"),
                 ("5 Cost Estimate (Bill of Quantities)", "7. Cost Estimate (Bill of Quantities)"),
                 ("6. Financial Analysis", "8. Financial Analysis"), ("8. Expansion Options", "9. Expansion Options"),
                 ("9. Assumptions, Exclusions and Next Steps", "10. Assumptions, Exclusions and Next Steps"),
                 ("3.Estimation PV Solar Generation", "3. Estimation of PV Solar Generation")):
    for p in d.paragraphs:
        if p.style.name.startswith("Heading") and p.text.strip().startswith(old): replace_in_par(p, old, new)
# ---------- electrical ----------
pars = d.paragraphs
def par_starting(s):
    for p in d.paragraphs:
        if p.text.strip().startswith(s): return p
def set_par(p, text):
    p.runs[0].text = text
    for r in p.runs[1:]: r.text = ""
set_par(par_starting("PV strings 6 mm²"), "PV strings: 6 mm² double-insulated PV cable through the cable trays, via a DC isolator and a Type II DC SPD for every string, to the inverters on the roof in a shaded, ventilated location.")
set_par(par_starting("Inverters (400 V, 3-phase)"), "Inverters (400 V, 3-phase) → AC combiner panel with 2 × 160 A MCCB incomers, Type II AC SPD and 400 A roof isolator.")
set_par(par_starting("AC combiner panel 4C"), "AC combiner panel → 4C × 240 mm² Cu XLPE/SWA → existing Masterpact NW10 H1 (1000 A) solar incomer on the main LV switchboard.")
set_par(par_starting("Earthing: array frames"), "Earthing: panel-to-panel bonding of the module frames, connected to the building earth and integrated with the lightning protection system.")
rep("1 panel, 250 A", "1 panel, 400 A")
# ---------- BOQ (table 11) ----------
t = d.tables[11]
items = [("1", "Supply of PV modules, 620 Wp (299 Nos Modules)", "185.4 kWp", "0.13", "24,099"),
         ("2", "Supply of String inverters, 80 kW", "2 nos", "4,000", "8,000"),
         ("3", "Supply of Mounting structure per Wp", "185.4 kWp", "0.095", "17,634"),
         ("4", "Supply of DC system", "Lot", "USD 0.029/Wp", "5,376"),
         ("5", "Supply of AC system", "Lot", "Lump sum", "6,245"),
         ("6", "Earthing, equipotential bonding & lightning protection integration", "Lot", "Lump sum", "1,847"),
         ("7", "Installation, testing & commissioning", "Lot", "Lump sum", "5,000"),
         ("8", "Transport, logistics & customs clearing", "Lot", "Lump sum", "8,650")]
for row, vals in zip(t.rows[1:9], items): set_row(row, vals)
summary = [("", "Sub-total", "", "", "76,851"), ("", "Contingency", "", "7 %", "5,380"),
           ("", "Total budget EPC cost (excluding taxes)", "", "", "82,231"), ("", "Profit margin", "", "25 %", "20,558"),
           ("", "Total Project Value (excluding taxes)", "", "", f"{capex:,.0f}"), ("", "Specific cost", "", "", f"{capex/185380:.3f} USD/Wp")]
rows = t.rows
set_row(rows[9], summary[0]); set_row(rows[10], summary[1]); set_row(rows[11], summary[5])
last = rows[10]
for vals in summary[2:5]:
    last = clone_row(t, rows[10], last); set_row(last, vals)
# ---------- financial text ----------
set_par(par_starting("The solar system needs an investment"), f"The solar system needs a total investment of {usd(capex)} (total project value, excluding taxes). At an avoided grid tariff of USD 0.07/kWh, rising 2% a year, it saves about USD 19,200 in its first year.")
set_par(par_starting("The investment pays back"), f"The investment pays back in about {pb:.1f} years. Over 25 years the project gives an IRR of {irr*100:.1f}% and an NPV of {usd(npv)} at a 10% discount rate, with total savings of about USD {sav25/1000:,.0f},000.")
p = par_starting("maintenance."); set_par(p, "")
set_par(par_starting("Solar energy costs about"), f"Solar energy costs about USD {lcoe:.3f}/kWh, below the grid tariff, so every unit generated reduces the hotel’s electricity cost. No O&M or inverter-replacement cost is included in the cash flow.")
t = d.tables[12]
for row in list(t.rows):
    k = row.cells[0].text.strip()
    if k.startswith("Inverter replacement"): del_row(t, row); continue
    v = {"Investment (EPC, excluding taxes)": usd(capex), "Year-1 savings": usd(y1), "Simple payback": f"{pb:.1f} years",
         "Project IRR (25 years, unlevered)": f"{irr*100:.1f} %", "NPV at 10 % discount rate": usd(npv),
         "Levelized cost of energy (LCOE)": f"USD {lcoe:.3f}/kWh", "25-year cumulative savings, net of O&M": usd(sav25)}.get(k)
    if k.startswith("Investment (EPC"): set_cell(row.cells[0], "Total investment (excluding taxes)")
    if k.startswith("25-year cumulative savings"): set_cell(row.cells[0], "25-year cumulative savings")
    if v: set_cell(row.cells[1], v)
# ---------- sensitivity ----------
sens = {round(s[0], 2): s for s in F["sens"]}
step_npv = sens[0.08][4] - sens[0.07][4]
set_par(par_starting("The project remains viable"), f"The project remains viable across a wide tariff range. Each USD 0.01/kWh change in the avoided tariff moves the NPV by about USD {step_npv/1000:,.1f}k and the payback by about 0.6 years. The break-even tariff (NPV = 0 at a 10 % discount rate) is about USD {F['breakeven']:.3f}/kWh, roughly {round((1-F['breakeven']/0.07)*100)} % below the current USD 0.07/kWh, so the investment stays profitable even if the effective tariff falls significantly.")
t = d.tables[13]
for row, tv in zip(t.rows[1:], (0.07, 0.08, 0.09, 0.10, 0.12)):
    s = sens[tv]; set_row(row, [f"{tv:.3f}", f"{s[2]:.1f}", f"{s[3]*100:.1f}%", f"{s[4]:,.0f}"])
# ---------- cash flow ----------
set_par(par_starting("For an investment of"), f"For an investment of {usd(capex)}, the system saves about USD 19,200 in its first year, rising with the tariff*. The investment is recovered in about {pb:.1f} years, and over 25 years the hotel's cumulative net cash flow reaches {usd(cum[25])}.")
t = d.tables[14]
for row in t.rows[1:]:
    y = row.cells[0].text.strip()
    if not y.isdigit(): continue
    y = int(y); c = cum[y]
    set_cell(row.cells[5], f"({-c:,.0f})" if c < 0 else f"{c:,.0f}")
    if y == 0: set_cell(row.cells[4], f"({capex:,.0f})")
# ---------- expansion ----------
t = d.tables[15]
for row in t.rows:
    if row.cells[0].text.startswith("Phase 1"): set_cell(row.cells[3], f"{capex:,.0f}")
    if row.cells[0].text.startswith("Indicative total"): set_cell(row.cells[3], f"{capex + 187500:,.0f}")
# ---------- block diagram picture (Figure 5): replace the zero-export version ----------
import io
from PIL import Image
_im = Image.open(os.path.join(HERE, "..", "sld", "PV_Block_Diagram.png")).convert("RGB")
for rel in d.part.rels.values():
    if rel.reltype.endswith("/image") and rel.target_ref.endswith("image8.png"):
        old = Image.open(io.BytesIO(rel.target_part.blob))
        b = io.BytesIO(); _im.resize(old.size, Image.LANCZOS).save(b, "PNG", dpi=old.info.get("dpi", (220, 220)))
        rel.target_part._blob = b.getvalue()
# ---------- refresh TOC on open ----------
st = d.settings.element
uf = st.find(qn("w:updateFields"))
if uf is None:
    uf = OxmlElement("w:updateFields"); st.append(uf)
uf.set(qn("w:val"), "true")
d.save(dst); print("saved", dst)
