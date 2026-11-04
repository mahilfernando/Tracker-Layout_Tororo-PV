"""Monthly generation bar chart (single series) as inline SVG -> gen_chart.svg."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
m = json.load(open(os.path.join(HERE, "monthly.json")))
rows = m["rows"]
W, H, L, R, T, B = 720, 300, 52, 16, 22, 40
YMAX = 30000
pw, ph = W - L - R, H - T - B
bw = pw / 12 * 0.56
sy = lambda v: T + ph * (1 - v / YMAX)
g = []
for v in range(0, YMAX + 1, 5000):
    g.append(f'<line x1="{L}" x2="{W-R}" y1="{sy(v):.1f}" y2="{sy(v):.1f}" class="{"base" if v==0 else "grid"}"/>')
    g.append(f'<text x="{L-8}" y="{sy(v)+3.5:.1f}" class="ax" text-anchor="end">{v//1000}</text>')
g.append(f'<text x="14" y="{T+ph/2:.1f}" class="ax" text-anchor="middle" transform="rotate(-90 14 {T+ph/2:.1f})">MWh per month</text>')
hi = max(r["kwh"] for r in rows); lo = min(r["kwh"] for r in rows)
for i, r in enumerate(rows):
    cx = L + pw / 12 * (i + 0.5); x = cx - bw / 2; y = sy(r["kwh"]); h = sy(0) - y; rr = 4
    g.append(f'<path class="bar" d="M{x:.1f},{sy(0):.1f} V{y+rr:.1f} Q{x:.1f},{y:.1f} {x+rr:.1f},{y:.1f} H{x+bw-rr:.1f} Q{x+bw:.1f},{y:.1f} {x+bw:.1f},{y+rr:.1f} V{sy(0):.1f} Z"/>')
    g.append(f'<text x="{cx:.1f}" y="{H-B+16}" class="ax" text-anchor="middle">{r["m"]}</text>')
    if r["kwh"] in (hi, lo) and not (r["kwh"] == hi and i == 2):
        g.append(f'<text x="{cx:.1f}" y="{y-6:.1f}" class="val" text-anchor="middle">{r["kwh"]/1000:.1f}</text>')
avg = m["avg_month"]
g.append(f'<line x1="{L}" x2="{W-R}" y1="{sy(avg):.1f}" y2="{sy(avg):.1f}" class="avg"/>')
g.append(f'<text x="{W-R-2}" y="{sy(26600):.1f}" class="avgt" text-anchor="end">-- -- Average {avg/1000:.1f} MWh/month</text>')
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" class="genchart" role="img" '
       f'aria-label="Estimated monthly PV generation, year 1">'
       '<style>.genchart .grid{stroke:#e3e7ec;stroke-width:1}.genchart .base{stroke:#8c96a1;stroke-width:1}'
       '.genchart .bar{fill:#14365d}.genchart .ax{font:10px Inter,Arial,sans-serif;fill:#5b6673}'
       '.genchart .val{font:600 10.5px Inter,Arial,sans-serif;fill:#1b2430}'
       '.genchart .avg{stroke:#8c96a1;stroke-width:1.2;stroke-dasharray:5 4}'
       '.genchart .avgt{font:600 10px Inter,Arial,sans-serif;fill:#5b6673}</style>'
       + "".join(g) + "</svg>")
open(os.path.join(HERE, "gen_chart.svg"), "w").write(svg)
print("ok")
