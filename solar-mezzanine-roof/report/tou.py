"""Time-of-use (TOU) impact of the PV system - average day, hour by hour.

Bands (Uganda ERA TOU structure - confirm on the hotel's bill):
  Off-peak 00:00-06:00, Shoulder 06:00-18:00, Peak 18:00-24:00.
PV: average day = year-1 generation / 365, sine profile between sunrise and sunset at the site
(Kampala, 32.59 E, UTC+3 -> solar noon ~12:50 EAT, day length ~12.1 h), 1-minute resolution.
Load: 1,000,000 kWh/month spread with a hotel hourly profile (assumed).
Tariff rates are indicative USD/kWh inputs - replace with the bill's rates.
"""
import json, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "calc.json")))

BANDS = [("Off-peak", 0, 6), ("Shoulder", 6, 18), ("Peak", 18, 24)]
RATES = {"Off-peak": 0.07, "Shoulder": 0.12, "Peak": 0.15}      # USD/kWh, indicative
LON, TZ = 32.587, 3
SOLAR_NOON = 12 - (LON - 15 * TZ) * 4 / 60 + 0.05                 # + ~3 min equation-of-time avg
DAYLEN = 12.1
SUNRISE, SUNSET = SOLAR_NOON - DAYLEN / 2, SOLAR_NOON + DAYLEN / 2

pv_day = d["y1_gen"] / 365
mins = [i / 60 for i in range(24 * 60)]
raw = [max(0.0, math.sin(math.pi * (t - SUNRISE) / DAYLEN)) if SUNRISE < t < SUNSET else 0.0 for t in mins]
k = pv_day / (sum(raw) / 60)
pv_h = [sum(raw[h * 60:(h + 1) * 60]) / 60 * k for h in range(24)]          # kWh in each hour
shape = [.75, .72, .70, .70, .72, .80, .95, 1.10, 1.20, 1.25, 1.28, 1.30, 1.30, 1.30, 1.28, 1.25, 1.20, 1.20, 1.25, 1.20, 1.10, .98, .88, .80]
load_day = 12_000_000 / 365
load_h = [load_day * x / sum(shape) for x in shape]
grid_h = [l - p for l, p in zip(load_h, pv_h)]
assert min(grid_h) > 0

def band_of(h):
    return next(n for n, a, b in BANDS if a <= h < b)
res = []
for n, a, b in BANDS:
    L = sum(load_h[a:b]) * 365; P = sum(pv_h[a:b]) * 365; G = L - P; r = RATES[n]
    res.append(dict(band=n, hours=f"{a:02d}:00–{b:02d}:00", rate=r, load=L, pv=P, grid=G,
                    cost0=L * r, cost1=G * r, saving=P * r, pv_share=P / (sum(pv_h) * 365), red=P / L))
tot = {k2: sum(x[k2] for x in res) for k2 in ("load", "pv", "grid", "cost0", "cost1", "saving")}
out = dict(bands=res, total=tot, rates=RATES, pv_h=pv_h, load_h=load_h, grid_h=grid_h,
           sunrise=SUNRISE, sunset=SUNSET, solar_noon=SOLAR_NOON, pv_peak_kw=max(raw) * k,
           pv_day=pv_day, load_day=load_day, blended=tot["saving"] / tot["pv"])
json.dump(out, open(os.path.join(HERE, "tou.json"), "w"), indent=1)
for x in res:
    print(f"{x['band']:9s} load {x['load']/1e6:6.2f} GWh pv {x['pv']/1e3:6.1f} MWh ({x['pv_share']*100:4.1f}%) "
          f"red {x['red']*100:4.2f}%  cost {x['cost0']:,.0f} -> {x['cost1']:,.0f}  save {x['saving']:,.0f}")
print("total save", round(tot["saving"]), "bill red", round(tot["saving"] / tot["cost0"] * 100, 2), "%",
      "blended", round(out["blended"], 4), "sunrise", round(SUNRISE, 2), "sunset", round(SUNSET, 2), "peak kW", round(out["pv_peak_kw"], 1))
