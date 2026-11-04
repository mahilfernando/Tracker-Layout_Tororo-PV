"""Monthly split of the year-1 PV generation for the report chart.

PVGIS / NASA POWER were not reachable from this session, so the monthly SHAPE uses typical
Kampala global horizontal irradiation (kWh/m2/day, long-term climatology, approx.) and the
annual TOTAL is the report's year-1 figure (185.4 kWp x 1,480 kWh/kWp). Confirm with PVsyst.
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "calc.json")))
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
GHI = [5.4, 5.6, 5.4, 5.0, 4.7, 4.6, 4.5, 4.8, 5.1, 5.0, 4.9, 5.1]
w = [g * n for g, n in zip(GHI, DAYS)]
tot = d["y1_gen"]
kwh = [tot * x / sum(w) for x in w]
rows = [dict(m=m, days=n, ghi=g, kwh=round(k), per_day=round(k / n), share=k / tot)
        for m, n, g, k in zip(MONTHS, DAYS, GHI, kwh)]
out = dict(rows=rows, total=round(tot), avg_month=round(tot / 12), avg_day=round(tot / 365),
           max=max(rows, key=lambda r: r["kwh"])["m"], min=min(rows, key=lambda r: r["kwh"])["m"])
json.dump(out, open(os.path.join(HERE, "monthly.json"), "w"), indent=1)
for r in rows: print(r)
print(out["total"], out["avg_month"], out["avg_day"], out["max"], out["min"])
