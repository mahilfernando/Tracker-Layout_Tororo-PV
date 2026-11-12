"""proposal_fin_v8.json: v7 energy/tariff data with capex and BOQ from the final workings (contingency 7 %, AC cable priced)."""
import json
from openpyxl import load_workbook
F = json.load(open("proposal_fin_v7.json"))
wb = load_workbook("Kampala_Marriott_PV_Workings_P50_PVsyst.xlsx", data_only=True); b = wb["BOQ"]
capex = b["F14"].value
F["boq"] = {str(r): b[f"F{r}"].value for r in range(4, 18)}
F["epc"], F["margin"] = b["H14"].value, b["H15"].value
gen, tar, r = F["gen"], F["tar"], 0.10
def cfs(t): return [-capex] + [g * t * 1.02 ** (y) for y, g in enumerate(gen)]
def npv(c, k=r): return sum(v / (1 + k) ** i for i, v in enumerate(c))
def irr(c):
    lo, hi = -0.5, 2.0
    for _ in range(200):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if npv(c, m) > 0 else (lo, m)
    return m
def payback(c):
    s = 0
    for i, v in enumerate(c):
        if s + v >= 0 and i: return i - 1 + (-s) / v
        s += v
cf = cfs(tar); cum = []; s = 0
for v in cf: s += v; cum.append(s)
assert abs(cf[1] - F["cf"][1]) < 1e-6 and abs(cf[2] - F["cf"][2]) < 1e-6
dgen = sum(g / (1 + r) ** (i + 1) for i, g in enumerate(gen))
F.update(capex=capex, cf=cf, cum=cum, npv=npv(cf), irr=irr(cf), pb=payback(cf), lcoe=capex / dgen,
         sav25=sum(cf[1:]), net25=sum(cf[1:]))
F["sens"] = [[t, cfs(t)[1], payback(cfs(t)), irr(cfs(t)), npv(cfs(t))] for t, *_ in F["sens"]]
F["breakeven"] = tar * capex / (npv(cf) + capex)
json.dump(F, open("proposal_fin_v8.json", "w"))
print({k: F[k] for k in ["capex", "pb", "irr", "npv", "lcoe", "sav25", "breakeven", "epc", "margin"]}, cum[25])
for s_ in F["sens"]: print([round(x, 4) for x in s_])
