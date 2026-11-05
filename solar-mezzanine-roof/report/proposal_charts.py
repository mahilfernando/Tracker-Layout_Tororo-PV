"""Cumulative cash-flow chart for the proposal (from proposal_fin.json) -> cashflow_chart.svg"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "proposal_fin.json")))
cum = d["cum"]
W, H, L, R, T, B = 720, 300, 64, 16, 20, 40
lo, hi = -150000, 500000
pw, ph = W - L - R, H - T - B
sx = lambda i: L + pw * (i + 0.5) / 26
sy = lambda v: T + ph * (hi - v) / (hi - lo)
g = []
for v in range(-100000, hi + 1, 100000):
    g.append(f'<line x1="{L}" x2="{W-R}" y1="{sy(v):.1f}" y2="{sy(v):.1f}" class="{"base" if v == 0 else "grid"}"/>')
    g.append(f'<text x="{L-8}" y="{sy(v)+3.5:.1f}" class="ax" text-anchor="end">{v/1000:,.0f}k</text>')
g.append(f'<line x1="{L}" x2="{W-R}" y1="{sy(0):.1f}" y2="{sy(0):.1f}" class="base"/>')
bw = pw / 26 * 0.62
for i, v in enumerate(cum):
    x = sx(i) - bw / 2; y0, y1 = sorted((sy(0), sy(v)))
    g.append(f'<rect x="{x:.1f}" y="{y0:.1f}" width="{bw:.1f}" height="{max(y1-y0,0.5):.1f}" class="{"neg" if v < 0 else "pos"}"/>')
    if i % 5 == 0: g.append(f'<text x="{sx(i):.1f}" y="{H-B+16}" class="ax" text-anchor="middle">{i}</text>')
g.append(f'<text x="{(L+W-R)/2:.1f}" y="{H-4}" class="ax" text-anchor="middle">Year</text>')
pb = d["pb"]; xp = L + pw * (pb + 0.5) / 26
g.append(f'<line x1="{xp:.1f}" x2="{xp:.1f}" y1="{T}" y2="{H-B}" class="pbl"/>')
g.append(f'<text x="{xp+6:.1f}" y="{T+12}" class="ann">Payback ≈ {pb:.1f} years</text>')
g.append(f'<text x="{sx(25):.1f}" y="{sy(cum[-1])-8:.1f}" class="ann" text-anchor="end">USD {cum[-1]/1000:,.0f}k after 25 years</text>')
g.append(f'<text x="{sx(0)+12:.1f}" y="{sy(cum[0])+14:.1f}" class="ann">Investment USD {-cum[0]/1000:,.0f}k</text>')
css = ('<style>.c text{font-family:Arial,Helvetica,sans-serif}.c .grid{stroke:#e3e7ec}.c .base{stroke:#8c96a1}'
       '.c .ax{font-size:10px;fill:#5b6673}.c .pos{fill:#14365d}.c .neg{fill:#c0392b}.c .pbl{stroke:#8c96a1;stroke-dasharray:4 3}'
       '.c .ann{font-size:10.5px;font-weight:700;fill:#1b2430}</style>')
open(os.path.join(HERE, "cashflow_chart.svg"), "w").write(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" class="c">{css}<rect width="{W}" height="{H}" fill="#fff"/>' + "".join(g) + "</svg>")
print("ok")
