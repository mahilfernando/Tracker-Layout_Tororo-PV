"""Build the mounting-structure RFQ / structural design brief PDF for the supplier.

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
@page {{ size:A4; margin:20mm 18mm 18mm 18mm; }}
:root {{ --ink:#1b2430; --muted:#5b6673; --rule:#c9d0d8; --navy:#14365d; --band:#eef2f6; }}
html,body {{ margin:0; background:#fff; color:var(--ink); font-family:Inter,"DejaVu Sans",Arial,sans-serif; font-size:9.4pt; line-height:1.45; }}
h1 {{ font-size:18pt; color:var(--navy); margin:0 0 2px; }}
h2 {{ font-size:12pt; color:var(--navy); border-bottom:1.4px solid var(--navy); padding-bottom:3px; margin:16px 0 8px; break-after:avoid; }}
p {{ margin:0 0 7px; }}
table {{ width:100%; border-collapse:collapse; margin:3px 0 8px; }}
th,td {{ border:0.6pt solid var(--rule); padding:3.5px 6px; vertical-align:top; }}
th {{ background:var(--band); color:var(--navy); text-align:left; font-weight:600; }}
tr {{ break-inside:avoid; }}
td.r {{ text-align:right; white-space:nowrap; font-variant-numeric:tabular-nums; }}
.kv td:first-child {{ width:40%; color:var(--muted); }}
.head {{ border-bottom:3px solid var(--navy); padding-bottom:8px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:flex-end; }}
.head .sub {{ font-size:10.5pt; }}
.meta {{ font-size:8.4pt; color:var(--muted); text-align:right; line-height:1.5; }}
.note {{ font-size:8.3pt; color:var(--muted); }}
.fig {{ text-align:center; break-inside:avoid; margin:4px 0; }}
.fig img {{ max-width:100%; border:0.6pt solid var(--rule); }}
.cap {{ font-size:8.2pt; color:var(--muted); text-align:center; margin:2px 0 8px; }}
ol,ul {{ margin:0 0 6px; padding-left:18px; }} li {{ margin-bottom:2px; }}
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
.two {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
</style></head><body>

<div class="head">
  <div><h1>PV Mounting Structure</h1><div class="sub">Request for Quotation &amp; Structural Design Brief<br>185.4 kWp rooftop PV – Marriott Hotel, mezzanine roof</div></div>
  <div class="meta">Doc. {DOC} Rev {REV}<br>{DATE}<br>Ref. drawing D18102-DD-A-104</div>
</div>

<p>We invite your quotation for the design, supply and delivery of the PV mounting structure described below. The design must be
carried out by a qualified structural engineer, and the calculations submitted for approval by the building's structural engineer.</p>

<h2>1. Project summary</h2>
<table class="kv">
<tr><td>Location</td><td>Uganda (equatorial, ≈0–1° N). Site address to be given at award.</td></tr>
<tr><td>Roof</td><td>Flat reinforced-concrete slab with perimeter parapet, single level; waterproofed. Usable area ≈29.4 × 39 m.</td></tr>
<tr><td>Roof height</td><td>About 7 m above ground (mezzanine podium). <b>Two hotel towers stand next to the roof</b>; consider wind acceleration and downwash.</td></tr>
<tr><td>PV system</td><td>299 modules × 620 Wp = 185.4 kWp</td></tr>
<tr><td>Module</td><td>Bifacial TOPCon, {L} × {W} × {T} mm, ≈{M:.0f} kg (dual glass); datasheet to follow</td></tr>
<tr><td>Design life</td><td>25 years minimum</td></tr>
</table>

<h2>2. Array configuration</h2>
<table>
<tr><th>Item</th><th>Value</th></tr>
<tr><td>Tilt / orientation</td><td>{TILT}° fixed; modules portrait, rows running along the 29.4 m roof width</td></tr>
<tr><td>Table type</td><td>2P = 2 modules high in portrait × 23 wide; 1P = 1 module high × 23 wide</td></tr>
<tr><td>Quantities</td><td><b>6 tables of 2P × 23 (46 modules each) + 1 table of 1P × 23 (23 modules) = 299 modules</b></td></tr>
<tr><td>Table length</td><td>{ROW:,} mm (23 modules + 20 mm gaps)</td></tr>
<tr><td>Table depth on plan</td><td>{D2:,.0f} mm (2P); {D1:,.0f} mm (1P)</td></tr>
<tr><td>Front edge height (min.)</td><td>{FRONT} mm above slab (cleaning access, water flow, bifacial gain)</td></tr>
<tr><td>Rear edge height</td><td>≈{REAR2:,.0f} mm (2P); ≈{REAR1:,.0f} mm (1P)</td></tr>
<tr><td>Gaps</td><td>20 mm between modules; {AISLE} mm aisle between tables; ≥1,000 mm from parapet</td></tr>
</table>
<div class="fig">{svg}</div>
<div class="cap">Figure 1 – Typical section through two 2P tables</div>

<div class="pb"></div>
<h2>3. Layout</h2>
<div class="fig"><img src="{b64('layout.png','image/png')}" style="max-height:118mm"></div>
<div class="cap">Figure 2 – PV layout on the mezzanine roof (CAD file DWG/DXF supplied with this RFQ)</div>

<h2>4. Structural design basis</h2>
<table>
<tr><th style="width:34%">Item</th><th>Requirement / preliminary value</th></tr>
<tr><td>Design codes</td><td>EN 1990, EN 1991-1-4 (wind), EN 1999 (aluminium), EN 1993 (steel), or ASCE 7 equivalent. Seismic per Uganda code US 319.</td></tr>
<tr><td>Basic wind speed</td><td>v<sub>b</sub> = {vb:.0f} m/s (10-min mean, 10 m, preliminary). <b>Supplier to confirm for the site.</b></td></tr>
<tr><td>Peak velocity pressure</td><td>q<sub>p</sub> ≈ {qp:.2f} kN/m² (terrain cat. III, z = {z:.0f} m, c<sub>e</sub> ≈ {ce:.2f}); check tower effects</td></tr>
<tr><td>Wind pressure coefficients</td><td>From supplier's wind-tunnel data for {TILT}° arrays, with edge and corner zones next to the parapet</td></tr>
<tr><td>Module dead load</td><td>≈{dl_mod:.1f} kg/m² of module area ({M:.0f} kg per module)</td></tr>
<tr><td>Structure dead load (allowance)</td><td>≈{STRUCT} kg/m² of module area; supplier to state actual</td></tr>
<tr><td>Snow load</td><td>None</td></tr>
<tr><td>Maintenance load</td><td>Structure not walkable; aisles carry roof live load (by others)</td></tr>
<tr><td>Temperature range</td><td>10 °C to 70 °C (structure); expansion breaks in rails at ≤ 12 m</td></tr>
<tr><td>Deflection limit</td><td>Rails L/200; must meet the module manufacturer's limits</td></tr>
<tr><td>Corrosion</td><td>Category C3. Aluminium 6005-T6 / 6063-T6 (anodised or mill finish); fasteners stainless A2-70 / A4-70; no galvanic contact with steel</td></tr>
<tr><td>Module clamping</td><td>Long-side clamping within the zones of the module installation manual (dual-glass bifacial); clamp loads to rated test loads (5400 Pa down / 2400 Pa up)</td></tr>
</table>

<h2>5. Roof interface</h2>
<ul>
<li><b>Option A – Anchored (preferred):</b> feet fixed to concrete plinths or chemical anchors into the slab, with full waterproofing detail. Suits the wind exposure near the towers.</li>
<li><b>Option B – Ballasted:</b> no penetrations; concrete ballast blocks with wind deflectors. Must state ballast per table and the resulting load in kg/m².</li>
<li>EPDM or rubber protection pads under every foot; do not block roof drainage paths or outlets.</li>
<li><b>Allowable roof load to be confirmed by the building's structural engineer.</b> The supplier must give the uniform load (kg/m²) and maximum point load (kN) at each foot.</li>
</ul>
<p class="note">Indicative weights: modules {total_mod_kg/1000:.1f} t + structure ≈{total_str_kg/1000:.1f} t (excluding ballast) over ≈{6*foot_2p+ROW/1000*D1/1000:,.0f} m² of table footprint, i.e. ≈{(total_mod_kg+total_str_kg)/(6*foot_2p+ROW/1000*D1/1000):.0f} kg/m² before ballast.</p>

<h2>6. Scope of supply</h2>
<div class="two"><ul>
<li>Rails, rafters, legs, bracing for 7 tables</li>
<li>End and mid clamps, bonding/earthing clips</li>
<li>All fasteners (stainless steel)</li>
<li>Feet, anchors or ballast trays, protection pads</li></ul><ul>
<li>Optional: roof walkway between tables</li>
<li>Optional: cable trays fixed to the structure</li>
<li>Optional: installation supervision</li></ul></div>

<h2>7. Information required with the quotation</h2>
<ol>
<li>Price per Wp and total price, in USD; state delivered to site or ex-works, and lead time.</li>
<li>Structural calculation report: wind zones, loads per foot (kN), ballast or anchor details, slab load (kg/m²).</li>
<li>General arrangement and detail drawings, with a bill of materials.</li>
<li>Material grades, corrosion protection and certificates.</li>
<li>Warranty period (structure 10 years minimum; materials 20 years minimum) and installation manual.</li>
</ol>
<p class="note">Contact: [Name / Company / Phone / Email]</p>
</body></html>"""
open(os.path.join(HERE, "Structure_RFQ.html"), "w").write(html)
print(f"D2 {D2:.0f} rear {REAR2:.0f} qp {qp:.2f} ce {ce:.2f} dl {dl_mod:.1f} mods {total_mod_kg} str {total_str_kg:.0f}")
