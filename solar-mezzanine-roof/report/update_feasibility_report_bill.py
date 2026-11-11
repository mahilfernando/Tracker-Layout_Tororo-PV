"""Feasibility report: energy demand and tariffs from the UEDCL bill (Oct 2026) and all financials re-run.
Usage: python3 update_feasibility_report_bill.py <in.docx> <out.docx>"""
import sys, os, json
import docx
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
F = json.load(open(os.path.join(HERE, "proposal_fin_v6.json")))
d = docx.Document(sys.argv[1])
B, T, tar = F["bill"], F["tou_rows"], F["tar"]
capex, gen, cf, cum = F["capex"], F["gen"], F["cf"], F["cum"]
y1, pb, irr, npv, lcoe, sav25 = cf[1], F["pb"], F["irr"], F["npv"], F["lcoe"], F["sav25"]
g1 = gen[0]; share = g1 / B["annual"]; usd = lambda v: f"USD {v:,.0f}"

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
def replace_in_par(p, old, new):
    if old not in p.text: return False
    runs = p.runs; full = "".join(r.text for r in runs); i = full.index(old); j = i + len(old); pos = 0; first = None
    for r in runs:
        a, b = pos, pos + len(r.text); pos = b
        if b <= i or a >= j: continue
        if first is None: first = r; r.text = r.text[:i - a] + new + (r.text[j - a:] if b > j else "")
        else: r.text = r.text[j - a:] if b > j else ""
    return True
def rep(old, new):
    pars = list(d.paragraphs) + [p for t in d.tables for row in t.rows for c in row.cells for p in c.paragraphs]
    if not any(replace_in_par(p, old, new) for p in pars): print("NOT FOUND", old)

# exec summary box
rep("4.9 yrs", f"{pb:.1f} yrs")
# key findings
for row in table_with("Item").rows:
    k = row.cells[0].text.strip()
    v = {"Hotel consumption": f"{B['month']:,.0f} kWh/month (UEDCL bill, Oct 2026)",
         "Year-1 generation": f"{g1/1000:.0f} MWh ({share*100:.1f}% of annual consumption) – PVsyst P50",
         "Avoided tariff": f"USD {tar+1e-9:.4f}/kWh (UGX 357/kWh shoulder tariff, as billed)",
         "Year-1 savings": usd(y1), "Simple payback": f"{pb:.1f} years", "Project IRR": f"{irr*100:.1f}%",
         "NPV (25 years at 10%)": usd(npv), "Cost of solar energy (LCOE)": f"{lcoe:.3f} USD/kWh"}.get(k)
    if v: set_cell(row.cells[1], v)
# site table
for row in table_with("Facility").rows:
    k = row.cells[0].text.strip()
    v = {"Annual electricity consumption": f"{B['annual']:,.0f} kWh (October 2026 bill × 12)",
         "Average monthly energy consumption": f"{B['month']:,.0f} kWh (UEDCL bill, 01/10–01/11/2026)",
         "Average / daytime demand": f"≈ {B['avg_sh']:,.0f} kW average in the shoulder band; maximum demand {B['maxkw']:,} kW"}.get(k)
    if v: set_cell(row.cells[1], v)
# generation bullet
set_par(par_starting("share of hotel uses"), f"share of hotel uses          100 %, {share*100:.1f} % of annual consumption")
# Table 2 – tariffs
t = table_with("Tariff period")
set_cell(t.rows[0].cells[2], "Tariff UGX/kWh → USD/kWh (UGX 4,100/USD)")
for row in t.rows[1:]:
    k = row.cells[0].text.strip()
    g = {"Off-peak": B["rate_op"], "Shoulder": B["rate_sh"], "Peak": B["rate_pk"]}[k]
    set_cell(row.cells[2], f"{g:.1f} → {g/B['fx']+1e-9:.4f}")
for p in d.paragraphs:
    if p.text.strip().startswith("Table 2"):
        set_par(p, "Table 2: UEDCL tariff 30.2 Large Consumers (bill Oct 2026), tariffs as billed excl. VAT, at UGX 4,100/USD")
# Table 3
for row in table_with("Period").rows[1:]:
    k = row.cells[0].text.strip()
    if k not in T: continue
    r = T[k]
    vals = [f"{r[1]:,.0f}", f"{r[2]:.1f}", f"{r[3]*100:.1f}%", f"{r[4]:,.0f}", f"{r[5]*100:.2f}%", f"{r[6]:,.0f}", f"{r[7]:,.0f}", f"{r[8]:,.0f}"]
    for c, v in zip(row.cells[1:], vals): set_cell(c, v)
set_par(par_starting("*Forecasted Energy demand"), f"*Annual energy demand = UEDCL bill for October 2026 ({B['month']:,.0f} kWh) × 12, split by tariff band as billed. All solar output (including the small output just after 18:00) is counted in the shoulder period. The demand charge (UGX 11,096/kW) is not reduced by solar.")
# finance
set_par(par_starting("The solar system needs"), f"The solar system needs a total investment of {usd(capex)} (total project value, excluding taxes). At the avoided shoulder tariff of USD {tar+1e-9:.4f}/kWh (UGX 357/kWh as billed, excl. VAT, at UGX 4,100/USD), rising 2% a year, it saves about USD {y1/1000:,.1f}k in its first year (PVsyst P50 generation).")
set_par(par_starting("The investment pays back"), f"The investment pays back in about {pb:.1f} years. Over 25 years the project gives an IRR of {irr*100:.1f}% and an NPV of {usd(npv)} at a 10% discount rate, with total savings of about USD {sav25/1000:,.0f},000.")
for row in table_with("Total investment").rows:
    k = row.cells[0].text.strip()
    v = {"Avoided grid tariff (year 1) / escalation": f"USD {tar+1e-9:.4f}/kWh (shoulder) / 2 % per year", "Year-1 savings": usd(y1),
         "Simple payback": f"{pb:.1f} years", "Project IRR (25 years, unlevered)": f"{irr*100:.1f} %", "NPV at 10 % discount rate": usd(npv),
         "Levelized cost of energy (LCOE)": f"USD {lcoe:.3f}/kWh", "25-year cumulative savings": usd(sav25)}.get(k)
    if v: set_cell(row.cells[1], v)
sens = {round(s[0], 4): s for s in F["sens"]}
st = F["scen"]; s07 = sens[0.07]; s10 = sens[0.1]
set_par(par_starting("The project remains viable"), f"The base case uses the shoulder tariff from the October 2026 bill, UGX 357/kWh (USD {tar+1e-9:.4f}/kWh at UGX 4,100/USD). If the 40 % energy rebate shown on the bill is applied to the saved energy, the avoided cost falls to USD {st['rebate']:.4f}/kWh; if VAT on electricity cannot be recovered it rises to USD {st['novat']:.4f}/kWh. Each USD 0.01/kWh change in the avoided tariff moves the NPV by about USD {(s10[4]-s07[4])/3/1000:,.1f}k. The break-even tariff (NPV = 0 at 10 %) is about USD {F['breakeven']:.3f}/kWh, roughly {round((1-F['breakeven']/tar)*100)} % below the current shoulder tariff.")
t = table_with("Avoided tariff")
cases = [(st["rebate"], "with 40 % rebate"), (0.07, ""), (tar, "base – bill tariff"), (0.10, ""), (st["novat"], "VAT not recoverable")]
for row, (tv, lab) in zip(t.rows[1:], cases):
    s = min(F["sens"], key=lambda x: abs(x[0] - tv))
    for c, v in zip(row.cells, [f"{tv+1e-9:.4f}" + (f" ({lab})" if lab else ""), f"{s[2]:.1f}", f"{s[3]*100:.1f}%", f"{s[4]:,.0f}"]): set_cell(c, v)
set_par(par_starting("For an investment of"), f"For an investment of {usd(capex)}, the system saves about USD {y1/1000:,.1f}k in its first year, rising with the tariff*. The investment is recovered in about {pb:.1f} years, and over 25 years the hotel's cumulative net cash flow reaches {usd(cum[25])}.")
for row in table_with("Year").rows[1:]:
    y = row.cells[0].text.strip()
    if not y.isdigit(): continue
    y = int(y); c = cum[y]
    if y > 0:
        set_cell(row.cells[2], f"{tar*1.02**(y-1):.3f}"); set_cell(row.cells[3], f"{cf[y]:,.0f}"); set_cell(row.cells[4], f"{cf[y]:,.0f}")
    set_cell(row.cells[5], f"({-c:,.0f})" if c < 0 else f"{c:,.0f}")
set_par(par_starting("*Grid price saved"), f"*Grid price saved for each kWh of solar. Starts at USD {tar+1e-9:.3f} (UGX 357/kWh shoulder tariff) and rises 2% a year to about USD {tar*1.02**24:.3f} by year 25.")
for row in table_with("Option").rows:
    if row.cells[0].text.startswith("Indicative total"): set_cell(row.cells[4], f"{(g1 + 370000)/B['annual']*100:.1f} % of hotel consumption")
set_par(par_starting("The hotel load is about"), f"The hotel used {B['month']:,.0f} kWh in October 2026 (UEDCL bill) with an average daytime demand of about {B['avg_sh']:,.0f} kW – far above the 160 kW PV output.")
set_par(par_starting("The avoided tariff is"), f"The avoided tariff is the UEDCL shoulder tariff as billed, UGX 357/kWh ≈ USD {tar+1e-9:.4f}/kWh at UGX 4,100/USD (excl. VAT), escalating 2 %/yr. The bill also shows a 40 % energy rebate; if it is applied to the solar savings the value is USD {st['rebate']:.4f}/kWh.")
stg = d.settings.element; uf = stg.find(qn("w:updateFields"))
if uf is None: uf = OxmlElement("w:updateFields"); stg.append(uf)
uf.set(qn("w:val"), "true")
d.save(sys.argv[2]); print("saved", sys.argv[2])
