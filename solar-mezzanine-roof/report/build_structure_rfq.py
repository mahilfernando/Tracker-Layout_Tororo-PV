"""Build the short (2-page) mounting-structure RFQ PDF for the supplier.

Run:  python3 build_structure_rfq.py && node to_pdf_rfq.js
"""
import base64, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
def b64(name, mime):
    return f"data:{mime};base64," + base64.b64encode(open(os.path.join(HERE, name), "rb").read()).decode()

DOC = "PV-RFQ-STR-001"; REV = "A"; DATE = "3 November 2026"

# ---- geometry ----
L, W, T, M = 2382, 1134, 30, 33.0       # module mm, kg
TILT = 10; GAP = 20; AISLE = 800; FRONT = 300
slope = 2 * L + GAP
D2 = slope * math.cos(math.radians(TILT)); D1 = L * math.cos(math.radians(TILT))
REAR2 = FRONT + slope * math.sin(math.radians(TILT)); REAR1 = FRONT + L * math.sin(math.radians(TILT))
ROW = 23 * W + 22 * GAP
A_MOD = L * W / 1e6
mods_2p = 46; mods_1p = 23
area_2p = mods_2p * A_MOD
foot_2p = ROW / 1000 * D2 / 1000
dl_mod = M / A_MOD                       # kg/m2 of module area
STRUCT = 4.5                             # kg/m2 module area, aluminium allowance
total_mod_kg = 299 * M
total_str_kg = 299 * A_MOD * STRUCT

# ---- wind (EN 1991-1-4, preliminary) ----
vb = 25.0; rho = 1.25; z = 10.0; z0 = 0.3; kr = 0.215
cr = kr * math.log(z / z0); Iv = 1 / math.log(z / z0)
ce = cr**2 * (1 + 7 * Iv)
qb = 0.5 * rho * vb**2 / 1000; qp = qb * ce

# ---- section drawing (SVG), scale 1 px = 12 mm ----
s = 1 / 12.0
ox, oy = 40, 190
def X(mm): return ox + mm * s
def Y(mm): return oy - mm * s
c, si = math.cos(math.radians(TILT)), math.sin(math.radians(TILT))
def table_svg(x0, rows, label):
    sl = rows * L + (rows - 1) * GAP
    x1, y1 = x0, FRONT
    x2, y2 = x0 + sl * c, FRONT + sl * si
    g = f'<line x1="{X(x1):.1f}" y1="{Y(y1):.1f}" x2="{X(x2):.1f}" y2="{Y(y2):.1f}" class="mod"/>'
    if rows == 2:
        xm, ym = x0 + L * c, FRONT + L * si
        g += f'<line x1="{X(xm):.1f}" y1="{Y(ym)-5:.1f}" x2="{X(xm):.1f}" y2="{Y(ym)+5:.1f}" class="thin"/>'
    # legs: front, (mid), rear
    for f in ([0, 0.5, 1] if rows == 2 else [0, 1]):
        lx = x0 + 150 * c + f * (sl - 300) * c; ly = FRONT + (150 + f * (sl - 300)) * si
        g += f'<line x1="{X(lx):.1f}" y1="{Y(ly):.1f}" x2="{X(lx):.1f}" y2="{Y(0):.1f}" class="leg"/>'
        g += f'<rect x="{X(lx)-9:.1f}" y="{Y(0):.1f}" width="18" height="5" class="pad"/>'
    g += f'<text x="{X(x0 + sl*c/2):.1f}" y="{Y(y2)-14:.1f}" class="lab" text-anchor="middle">{label}</text>'
    return g, x2, y2
t1, a_end, a_top = table_svg(0, 2, "2P table (2 × 2382 mm, portrait)")
t2, b_end, b_top = table_svg(D2 + AISLE, 2, "next 2P table")
dim = lambda x1, x2, y, txt: (f'<line x1="{X(x1):.1f}" y1="{y}" x2="{X(x2):.1f}" y2="{y}" class="dim"/>'
    f'<line x1="{X(x1):.1f}" y1="{y-4}" x2="{X(x1):.1f}" y2="{y+4}" class="dim"/><line x1="{X(x2):.1f}" y1="{y-4}" x2="{X(x2):.1f}" y2="{y+4}" class="dim"/>'
    f'<text x="{(X(x1)+X(x2))/2:.1f}" y="{y+13}" class="dt" text-anchor="middle">{txt}</text>')
vdim = lambda x, h, txt, anchor="end", dx=-6: (f'<line x1="{X(x)}" y1="{Y(0):.1f}" x2="{X(x)}" y2="{Y(h):.1f}" class="dim"/>'
    f'<text x="{X(x)+dx}" y="{(Y(0)+Y(h))/2+3:.1f}" class="dt" text-anchor="{anchor}">{txt}</text>')
right = D2 + AISLE + D2
svg = f'''<svg viewBox="-10 50 {X(right)+70:.0f} 200" class="sec">
<line x1="{X(-300):.1f}" y1="{Y(0):.1f}" x2="{X(right+300):.1f}" y2="{Y(0):.1f}" class="slab"/>
<text x="{X(right+300):.1f}" y="{Y(0)+20:.1f}" class="dt" text-anchor="end">RC roof slab + waterproofing</text>
{t1}{t2}
{dim(0, D2, 218, f"{D2:,.0f} (plan depth)")}
{dim(D2, D2+AISLE, 236, f"{AISLE} aisle")}
{vdim(0, FRONT, f"{FRONT}", "end", -6)}
{vdim(D2, REAR2, f"{REAR2:,.0f}", "start", 6)}
<text x="{X(1500):.1f}" y="{Y(150):.1f}" class="lab">{TILT}° tilt</text>
<text x="{X(-300):.1f}" y="246" class="dt">Dimensions in mm</text>
</svg>'''

html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>PV Mounting Structure – RFQ</title>
<style>
@page {{ size:A4; margin:16mm 16mm 16mm 16mm; }}
:root {{ --ink:#1b2430; --muted:#5b6673; --rule:#c9d0d8; --navy:#14365d; --band:#eef2f6; }}
html,body {{ margin:0; background:#fff; color:var(--ink); font-family:Inter,"DejaVu Sans",Arial,sans-serif; font-size:9.6pt; line-height:1.42; }}
h1 {{ font-size:17pt; color:var(--navy); margin:0 0 2px; }}
h2 {{ font-size:11.5pt; color:var(--navy); border-bottom:1.4px solid var(--navy); padding-bottom:3px; margin:12px 0 6px; break-after:avoid; }}
p {{ margin:0 0 6px; }}
table {{ width:100%; border-collapse:collapse; margin:2px 0 6px; }}
th,td {{ border:0.6pt solid var(--rule); padding:3.5px 7px; vertical-align:top; }}
tr {{ break-inside:avoid; }}
.kv td:first-child {{ width:36%; color:var(--muted); background:var(--band); }}
.head {{ border-bottom:3px solid var(--navy); padding-bottom:7px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:flex-end; }}
.meta {{ font-size:8.4pt; color:var(--muted); text-align:right; line-height:1.5; }}
.note {{ font-size:8.3pt; color:var(--muted); }}
.fig {{ text-align:center; break-inside:avoid; margin:4px 0; }}
.fig img {{ max-width:100%; border:0.6pt solid var(--rule); }}
.cap {{ font-size:8.2pt; color:var(--muted); text-align:center; margin:2px 0 6px; }}
ol,ul {{ margin:0 0 4px; padding-left:18px; }} li {{ margin-bottom:2px; }}
.sec {{ width:100%; height:auto; }}
.sec .slab {{ stroke:#1b2430; stroke-width:3; }}
.sec .mod {{ stroke:#14365d; stroke-width:5; }}
.sec .thin {{ stroke:#fff; stroke-width:2; }}
.sec .leg {{ stroke:#5b6673; stroke-width:2; }}
.sec .pad {{ fill:#5b6673; }}
.sec .dim {{ stroke:#8c96a1; stroke-width:0.8; }}
.sec .dt {{ font-size:15px; fill:#5b6673; }}
.sec .lab {{ font-size:16px; fill:#1b2430; }}
.pb {{ break-before:page; }}
</style></head><body>

<div class="head">
  <div><h1>PV Mounting Structure – Request for Quotation</h1><div>185.4 kWp rooftop PV · Marriott Hotel, mezzanine roof · Uganda</div></div>
  <div class="meta">Doc. {DOC} Rev {REV}<br>{DATE}</div>
</div>
<p>Please quote for the design and supply of the PV mounting structure below, including the structural calculation.</p>

<h2>1. System and module</h2>
<table class="kv">
<tr><td>Solar capacity</td><td><b>185.4 kWp</b></td></tr>
<tr><td>Number of modules</td><td><b>299 modules × 620 Wp</b></td></tr>
<tr><td>Module size / weight</td><td><b>{L} × {W} × {T} mm</b>, ≈{M:.0f} kg each (bifacial, dual glass)</td></tr>
<tr><td>Total module weight</td><td>≈{total_mod_kg/1000:.1f} t (≈{dl_mod:.1f} kg/m² of module area)</td></tr>
</table>

<h2>2. Structure configuration</h2>
<table class="kv">
<tr><td>Tilt</td><td><b>{TILT}°</b> fixed</td></tr>
<tr><td>Module orientation</td><td>Portrait, 2 modules high per table (2P)</td></tr>
<tr><td>Number of tables</td><td><b>6 tables of 2P × 23 modules (46 each) + 1 table of 1P × 23 modules</b></td></tr>
<tr><td>Table length</td><td>{ROW:,} mm</td></tr>
<tr><td>Table depth on plan</td><td>{D2:,.0f} mm (2P) / {D1:,.0f} mm (1P)</td></tr>
<tr><td>Front / rear edge height</td><td>{FRONT} mm / ≈{REAR2:,.0f} mm above roof (2P)</td></tr>
<tr><td>Spacing</td><td>20 mm between modules · {AISLE} mm aisle between tables · 1,000 mm from parapet</td></tr>
</table>
<div class="fig">{svg}</div>
<div class="cap">Typical section through two 2P tables</div>

<h2>3. Wind load and structural design</h2>
<table class="kv">
<tr><td>Basic wind speed</td><td><b>{vb:.0f} m/s</b> (10-min mean at 10 m; preliminary, supplier to confirm for the site)</td></tr>
<tr><td>Peak wind pressure</td><td><b>q<sub>p</sub> ≈ {qp:.2f} kN/m²</b> (EN 1991-1-4, terrain cat. III, roof height ≈7–10 m)</td></tr>
<tr><td>Site exposure</td><td>Two hotel towers stand next to the roof: allow for wind acceleration and edge/corner zones at the parapet</td></tr>
<tr><td>Design codes</td><td>EN 1991-1-4, EN 1999 (aluminium) or ASCE 7 equivalent; design life 25 years</td></tr>
<tr><td>Materials</td><td>Aluminium 6005-T6 / 6063-T6; stainless-steel fasteners A2-70; corrosion category C3</td></tr>
<tr><td>Module clamping</td><td>To the module installation manual (rated test loads 5,400 Pa down / 2,400 Pa up)</td></tr>
</table>

<div class="pb"></div>
<h2>4. Roof and fixing</h2>
<table class="kv">
<tr><td>Roof</td><td>Flat reinforced-concrete slab, single level, waterproofed, with parapet. Usable area ≈29.4 × 39 m.</td></tr>
<tr><td>Fixing (please quote both)</td><td><b>A – Anchored (preferred):</b> chemical anchors or concrete plinths, with waterproofing detail<br>
<b>B – Ballasted:</b> concrete ballast with wind deflectors; state ballast weight per table</td></tr>
<tr><td>Roof protection</td><td>EPDM pads under every foot; keep drainage paths clear</td></tr>
<tr><td>Roof load</td><td>State the uniform load (kg/m²) and the point load per foot (kN), for approval by the building's structural engineer</td></tr>
</table>

<h2>5. Layout</h2>
<div class="fig"><img src="{b64('layout.png','image/png')}" style="max-height:120mm"></div>
<div class="cap">PV layout on the mezzanine roof (DWG/DXF attached)</div>

<h2>6. Quotation to include</h2>
<ol>
<li>Price (USD per Wp and total), delivery terms and lead time</li>
<li>Structural calculation: wind loads, loads per foot, anchor or ballast design</li>
<li>General arrangement drawings and bill of materials</li>
<li>Warranty (structure 10 years minimum) and installation manual</li>
</ol>
<p class="note">Contact: [Name / Company / Phone / Email]</p>
</body></html>"""
open(os.path.join(HERE, "Structure_RFQ.html"), "w").write(html)
print("ok")
