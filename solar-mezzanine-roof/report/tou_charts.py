"""Charts for the TOU section: (A) average-day PV by hour over tariff bands, (B) grid-energy reduction by band."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
t = json.load(open(os.path.join(HERE, "tou.json")))
STYLE = ('<style>.c .grid{stroke:#e3e7ec;stroke-width:1}.c .base{stroke:#8c96a1;stroke-width:1}'
         '.c .ax{font:10px Inter,Arial,sans-serif;fill:#5b6673}.c .val{font:600 10.5px Inter,Arial,sans-serif;fill:#1b2430}'
         '.c .bandt{font:600 10.5px Inter,Arial,sans-serif;fill:#3d4752}.c .bandv{font:10px Inter,Arial,sans-serif;fill:#5b6673}'
         '.c .pv{fill:#eda100}.c .red{fill:#2a78d6}.c .lab{font:10.5px Inter,Arial,sans-serif;fill:#1b2430}</style>')

# ---- A: hourly PV, average day ----
W, H, L, R, T, B = 720, 300, 52, 16, 46, 40
YMAX = 120
pw, ph = W - L - R, H - T - B
sx = lambda h: L + pw * h / 24
sy = lambda v: T + ph * (1 - v / YMAX)
g = []
fills = {"Off-peak": "#eef1f5", "Shoulder": "#ffffff", "Peak": "#f6efe4"}
for b in t["bands"]:
    a, z = int(b["hours"][:2]), int(b["hours"][6:8])
    g.append(f'<rect x="{sx(a):.1f}" y="{T}" width="{sx(z)-sx(a):.1f}" height="{ph}" fill="{fills[b["band"]]}"/>')
    g.append(f'<text x="{(sx(a)+sx(z))/2:.1f}" y="{T-24}" class="bandt" text-anchor="middle">{b["band"].upper()} {b["hours"]}</text>')
    g.append(f'<text x="{(sx(a)+sx(z))/2:.1f}" y="{T-10}" class="bandv" text-anchor="middle">{b["pv_share"]*100:.1f} % of solar energy</text>')
for v in range(0, YMAX + 1, 20):
    g.append(f'<line x1="{L}" x2="{W-R}" y1="{sy(v):.1f}" y2="{sy(v):.1f}" class="{"base" if v == 0 else "grid"}"/>')
    g.append(f'<text x="{L-8}" y="{sy(v)+3.5:.1f}" class="ax" text-anchor="end">{v}</text>')
g.append(f'<text x="14" y="{T+ph/2:.1f}" class="ax" text-anchor="middle" transform="rotate(-90 14 {T+ph/2:.1f})">kWh in each hour</text>')
bw = pw / 24 * 0.7
for h, v in enumerate(t["pv_h"]):
    x = sx(h) + (pw / 24 - bw) / 2
    if v > 0.05:
        y = sy(v); rr = min(3, (sy(0) - y) / 2)
        g.append(f'<path class="pv" d="M{x:.1f},{sy(0):.1f} V{y+rr:.1f} Q{x:.1f},{y:.1f} {x+rr:.1f},{y:.1f} H{x+bw-rr:.1f} Q{x+bw:.1f},{y:.1f} {x+bw:.1f},{y+rr:.1f} V{sy(0):.1f} Z"/>')
    if h % 3 == 0:
        g.append(f'<text x="{sx(h):.1f}" y="{H-B+16}" class="ax" text-anchor="middle">{h:02d}:00</text>')
g.append(f'<text x="{sx(24):.1f}" y="{H-B+16}" class="ax" text-anchor="end">24:00</text>')
pk = max(range(24), key=lambda h: t["pv_h"][h])
g.append(f'<text x="{sx(pk+0.5):.1f}" y="{sy(t["pv_h"][pk])-6:.1f}" class="val" text-anchor="middle">{t["pv_h"][pk]:.0f}</text>')
svgA = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" class="c touA" role="img" '
        f'aria-label="Average-day solar generation by hour and tariff period">{STYLE}{"".join(g)}</svg>')

# ---- B: reduction of grid energy by band ----
W2, H2, L2, R2 = 720, 170, 150, 90
rows = t["bands"]
XMAX = 0.05
g = []
bh = 26
sx2 = lambda v: L2 + (W2 - L2 - R2) * v / XMAX
for v in (0, 0.01, 0.02, 0.03, 0.04, 0.05):
    g.append(f'<line x1="{sx2(v):.1f}" x2="{sx2(v):.1f}" y1="14" y2="{14+len(rows)*44-10}" class="{"base" if v == 0 else "grid"}"/>')
    g.append(f'<text x="{sx2(v):.1f}" y="{14+len(rows)*44+6}" class="ax" text-anchor="middle">{v*100:.0f} %</text>')
for i, r in enumerate(rows):
    y = 20 + i * 44
    g.append(f'<text x="{L2-10}" y="{y+bh/2+4}" class="lab" text-anchor="end">{r["band"]} ({r["hours"]})</text>')
    w = sx2(r["red"]) - sx2(0)
    if w > 0.5:
        rr = min(3, w / 2)
        g.append(f'<path class="red" d="M{sx2(0):.1f},{y} H{sx2(0)+w-rr:.1f} Q{sx2(0)+w:.1f},{y} {sx2(0)+w:.1f},{y+rr} V{y+bh-rr} Q{sx2(0)+w:.1f},{y+bh} {sx2(0)+w-rr:.1f},{y+bh} H{sx2(0):.1f} Z"/>')
    g.append(f'<text x="{sx2(0)+max(w,0)+6:.1f}" y="{y+bh/2+4}" class="val">{r["red"]*100:.2f} %  ({r["pv"]/1000:,.1f} MWh/yr)</text>')
svgB = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W2} {H2}" class="c touB" role="img" '
        f'aria-label="Reduction of grid energy by tariff period">{STYLE}{"".join(g)}</svg>')
open(os.path.join(HERE, "tou_chartA.svg"), "w").write(svgA)
open(os.path.join(HERE, "tou_chartB.svg"), "w").write(svgB)
print("ok")
