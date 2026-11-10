"""Switch the feasibility report (Rev B docx) from the desktop generation estimate to the PVsyst P50 figures
and add the PVsyst report to the annex list.
Usage: python3 update_feasibility_report_p50.py <in.docx> <out.docx>
"""
import sys, os, json, io, copy
import docx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
F = json.load(open(os.path.join(HERE, "proposal_fin_v3.json")))
d = docx.Document(sys.argv[1])

def replace_in_par(p, old, new):
    if old not in p.text: return False
    runs = p.runs; full = "".join(r.text for r in runs); i = full.index(old); j = i + len(old); pos = 0; first = None
    for r in runs:
        a, b = pos, pos + len(r.text); pos = b
        if b <= i or a >= j: continue
        if first is None: first = r; r.text = r.text[:i - a] + new + (r.text[j - a:] if b > j else "")
        else: r.text = r.text[j - a:] if b > j else ""
    return True
def all_pars():
    yield from d.paragraphs
    for t in d.tables:
        for row in t.rows:
            for c in row.cells: yield from c.paragraphs
def rep(old, new):
    n = sum(replace_in_par(p, old, new) for p in all_pars())
    if n == 0: print("NOT FOUND:", old)
def set_cell(cell, text):
    ps = cell.paragraphs
    if ps[0].runs:
        ps[0].runs[0].text = text
        for r in ps[0].runs[1:]: r.text = ""
    else: ps[0].add_run(text)
def par_starting(s):
    for p in d.paragraphs:
        if p.text.strip().startswith(s): return p
    print("NOT FOUND par:", s)
def set_par(p, text):
    p.runs[0].text = text
    for r in p.runs[1:]: r.text = ""
def add_par_after(p, text):
    new = copy.deepcopy(p._p); p._p.addnext(new)
    q = docx.text.paragraph.Paragraph(new, p._parent); set_par(q, text); return q
def table_with(first_cell):
    for t in d.tables:
        if t.rows[0].cells[0].text.strip().startswith(first_cell): return t
    print("NOT FOUND table:", first_cell)

usd = lambda v: f"USD {v:,.0f}"
capex, gen, cf, cum = F["capex"], F["gen"], F["cf"], F["cum"]
y1, pb, irr, npv, lcoe, sav25 = cf[1], F["pb"], F["irr"], F["npv"], F["lcoe"], F["sav25"]
g1 = gen[0]; share = g1 / 12_000_000; T = F["tou_rows"]

# ---- executive summary boxes + key findings ----
rep("274 MWh", f"{g1/1000:.0f} MWh")
rep("5.2 yrs", f"{pb:.1f} yrs")
t = table_with("Item")
for row in t.rows:
    k = row.cells[0].text.strip()
    v = {"Year-1 generation": f"{g1/1000:.0f} MWh ({share*100:.1f}% of annual consumption) – PVsyst P50",
         "Year-1 savings": usd(T["Total"][8]), "Simple payback": f"{pb:.1f} years", "Project IRR": f"{irr*100:.1f}%",
         "NPV (25 years at 10%)": usd(npv), "Cost of solar energy (LCOE)": f"{lcoe:.3f} USD/kWh"}.get(k)
    if v: set_cell(row.cells[1], v)
# ---- generation section ----
set_par(par_starting("Year-1 generation"), f"Year-1 generation\t{g1:,.0f} kWh, on average {g1/12:,.0f} kWh/month and {g1/365:,.0f} kWh/day")
set_par(par_starting("25-year generation"), f"25-year generation\t{F['gen25']/1000:,.0f} MWh*")
set_par(par_starting("share of hotel uses"), f"share of hotel uses          100 %, {share*100:.1f} % of annual consumption")
mm = F["pvsyst_monthly"]
set_par(par_starting("Note: Output is highest"), f"Source: PVsyst V8.1.8 simulation (P50, Meteonorm 9.0 weather, performance ratio 85.4 %, specific yield {g1/185.38:,.0f} kWh/kWp) – Annex 7. Output is highest from January to March and lowest in June.")
set_par(par_starting("The difference between the best"), f"The best month is about {round((max(mm)/min(mm)-1)*100)} % above the lowest. The hotel load is higher than the PV output in every hour, so all this energy is used on site. Figures are P50 as simulated, before shading and soiling losses (P90 ≈ 8 % lower).")
# monthly chart (png + svg)
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
def chart(fmt, w_in, h_in, dpi):
    fig, ax = plt.subplots(figsize=(w_in, h_in), dpi=dpi)
    v = [x / 1000 for x in mm]; bars = ax.bar(months, v, color="#17375e", width=0.65)
    for b_, x in zip(bars, v): ax.text(b_.get_x() + b_.get_width() / 2, x + 0.6, f"{x:.1f}", ha="center", fontsize=9)
    ax.set_ylim(0, 30); ax.set_yticks(range(0, 31, 5)); ax.set_yticklabels([f"{t:.1f}" for t in range(0, 31, 5)], fontsize=9)
    ax.set_ylabel("MWh per month", fontsize=9, fontweight="bold"); ax.tick_params(axis="x", labelsize=9)
    ax.set_title("Monthly PV Generation – Year 1, PVsyst P50 (185.4 kWp)", fontsize=13, fontweight="bold")
    ax.grid(axis="y", color="#b0b0b0", lw=0.6); ax.set_axisbelow(True)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    fig.tight_layout(); b = io.BytesIO(); fig.savefig(b, format=fmt, dpi=dpi); plt.close(fig); return b.getvalue()
for rel in d.part.rels.values():
    if not rel.reltype.endswith("/image"): continue
    if rel.target_ref.endswith("image3.png"): rel.target_part._blob = chart("png", 1444 / 192, 682 / 192, 192)
    if rel.target_ref.endswith("image4.svg"): rel.target_part._blob = chart("svg", 722 / 96, 341 / 96, 96)
# ---- TOU table 3 ----
t = table_with("Period")
for row in t.rows[1:]:
    k = row.cells[0].text.strip()
    if k not in T: continue
    r = T[k]
    set_cell(row.cells[1], f"{r[1]:,.0f}"); set_cell(row.cells[2], f"{r[2]:.1f}"); set_cell(row.cells[3], f"{r[3]*100:.1f}%")
    set_cell(row.cells[4], f"{r[4]:,.0f}"); set_cell(row.cells[5], f"{r[5]*100:.2f}%")
    set_cell(row.cells[6], f"{r[6]:,.0f}"); set_cell(row.cells[7], f"{r[7]:,.0f}"); set_cell(row.cells[8], f"{r[8]:,.0f}")
# ---- electrical component table ----
rep("274,000 kWh/yr", f"{round(g1, -3):,.0f} kWh/yr"); rep("(22,900 kWh/month)", f"({round(g1/12, -1):,.0f} kWh/month)")
# ---- financial ----
set_par(par_starting("The solar system needs"), f"The solar system needs a total investment of {usd(capex)} (total project value, excluding taxes). At an avoided grid tariff of USD 0.07/kWh, rising 2% a year, it saves about USD {y1/1000:,.1f}k in its first year (PVsyst P50 generation).")
set_par(par_starting("The investment pays back"), f"The investment pays back in about {pb:.1f} years. Over 25 years the project gives an IRR of {irr*100:.1f}% and an NPV of {usd(npv)} at a 10% discount rate, with total savings of about USD {sav25/1000:,.0f},000.")
set_par(par_starting("Solar energy costs about"), f"Solar energy costs about USD {lcoe:.3f}/kWh, below the grid tariff, so every unit generated reduces the hotel’s electricity cost. No O&M or inverter-replacement cost is included in the cash flow.")
t = table_with("Total investment")
for row in t.rows:
    k = row.cells[0].text.strip()
    v = {"Year-1 savings": usd(y1), "Simple payback": f"{pb:.1f} years", "Project IRR (25 years, unlevered)": f"{irr*100:.1f} %",
         "NPV at 10 % discount rate": usd(npv), "Levelized cost of energy (LCOE)": f"USD {lcoe:.3f}/kWh", "25-year cumulative savings": usd(sav25)}.get(k)
    if v: set_cell(row.cells[1], v)
sens = {round(s[0], 2): s for s in F["sens"]}
set_par(par_starting("The project remains viable"), f"The project remains viable across a wide tariff range. Each USD 0.01/kWh change in the avoided tariff moves the NPV by about USD {(sens[0.08][4]-sens[0.07][4])/1000:,.1f}k and the payback by about 0.6 years. The break-even tariff (NPV = 0 at a 10 % discount rate) is about USD {F['breakeven']:.3f}/kWh, roughly {round((1-F['breakeven']/0.07)*100)} % below the current USD 0.07/kWh, so the investment stays profitable even if the effective tariff falls significantly.")
t = table_with("Avoided tariff")
for row, tv in zip(t.rows[1:], (0.07, 0.08, 0.09, 0.10, 0.12)):
    s = sens[tv]
    for c, v in zip(row.cells, [f"{tv:.3f}", f"{s[2]:.1f}", f"{s[3]*100:.1f}%", f"{s[4]:,.0f}"]): set_cell(c, v)
set_par(par_starting("For an investment of"), f"For an investment of {usd(capex)}, the system saves about USD {y1/1000:,.1f}k in its first year, rising with the tariff*. The investment is recovered in about {pb:.1f} years, and over 25 years the hotel's cumulative net cash flow reaches {usd(cum[25])}.")
t = table_with("Year")
for row in t.rows[1:]:
    y = row.cells[0].text.strip()
    if not y.isdigit(): continue
    y = int(y); c = cum[y]
    if y > 0:
        g = gen[y - 1]
        set_cell(row.cells[1], f"{g:,.0f}"); set_cell(row.cells[3], f"{cf[y]:,.0f}"); set_cell(row.cells[4], f"{cf[y]:,.0f}")
    set_cell(row.cells[5], f"({-c:,.0f})" if c < 0 else f"{c:,.0f}")
# ---- expansion ----
t = table_with("Option")
for row in t.rows:
    a = row.cells[0].text
    if a.startswith("Phase 1"): set_cell(row.cells[2], f"{g1/1000:.0f} MWh")
    if a.startswith("Indicative total"):
        set_cell(row.cells[2], f"{g1/1000 + 370:.0f} MWh"); set_cell(row.cells[4], f"{(g1 + 370000)/12e6*100:.1f} % of hotel consumption")
# ---- assumptions + annexes ----
p = par_starting("Prices are 2026 East African")
add_par_after(p, f"Energy yield from the PVsyst V8.1.8 simulation, P50 as simulated ({g1:,.0f} kWh/yr); shading and soiling are not yet modelled and a P90 year is about 8 % lower.")
p = par_starting("6.Quotation")
add_par_after(p, "7.PVsyst Simulation Report")
# refresh TOC on open
st = d.settings.element; uf = st.find(qn("w:updateFields"))
if uf is None: uf = OxmlElement("w:updateFields"); st.append(uf)
uf.set(qn("w:val"), "true")
d.save(sys.argv[2]); print("saved", sys.argv[2])
