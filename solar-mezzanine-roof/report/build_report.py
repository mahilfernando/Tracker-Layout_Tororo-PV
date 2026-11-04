"""Build the rooftop PV design & cost report (HTML -> PDF via Playwright/Chromium).

Run:  python3 calc.py && python3 build_report.py && node to_pdf.js
"""
import base64, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "calc.json")))

def b64(name, mime):
    return f"data:{mime};base64," + base64.b64encode(open(os.path.join(HERE, name), "rb").read()).decode()

def usd(x):
    return f"{x:,.0f}"

DOC_NO = "PV-RPT-D18102-001"
REV = "A"
DATE = "3 November 2026"

# ---------- cumulative cash-flow chart (inline SVG, single series) ----------
cum = d["cum"]
W, H, L, R, T, B = 640, 250, 64, 16, 16, 34
lo, hi = min(cum), max(cum)
lo = -150000 if lo > -150000 else lo
hi = 1000000 if hi < 1000000 else hi
def sx(i): return L + (W - L - R) * i / 25
def sy(v): return T + (H - T - B) * (hi - v) / (hi - lo)
grid = ""
for v in range(-200000, int(hi) + 1, 200000):
    if v < lo: continue
    grid += f'<line x1="{L}" x2="{W-R}" y1="{sy(v):.1f}" y2="{sy(v):.1f}" class="g"/>'
    grid += f'<text x="{L-6}" y="{sy(v)+3.5:.1f}" class="ax" text-anchor="end">{v/1000:,.0f}k</text>'
for i in range(0, 26, 5):
    grid += f'<text x="{sx(i):.1f}" y="{H-B+16}" class="ax" text-anchor="middle">{i}</text>'
pts = " ".join(f"{sx(i):.1f},{sy(v):.1f}" for i, v in enumerate(cum))
pb = d["payback"]
chart = f'''<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="Cumulative cash flow">
{grid}
<line x1="{L}" x2="{W-R}" y1="{sy(0):.1f}" y2="{sy(0):.1f}" class="zero"/>
<polyline points="{pts}" class="line"/>
<line x1="{sx(pb):.1f}" x2="{sx(pb):.1f}" y1="{T}" y2="{H-B}" class="pb"/>
<text x="{sx(pb)+5:.1f}" y="{T+12}" class="ann">Payback ≈ {pb:.1f} yrs</text>
<text x="{sx(25)-4:.1f}" y="{sy(cum[-1])-8:.1f}" class="ann" text-anchor="end">USD {cum[-1]/1000:,.0f}k at year 25</text>
<text x="{(L+W-R)/2:.1f}" y="{H-2}" class="ax" text-anchor="middle">Year of operation</text>
</svg>'''

boq_rows = "".join(
    f"<tr><td class='c'>{i+1}</td><td>{b[0]}</td><td class='c'>{b[1]}</td><td class='r'>{b[2]}</td><td class='r'>{usd(b[3])}</td></tr>"
    for i, b in enumerate(d["boq"]))

cf_rows = "".join(
    f"<tr><td class='c'>{r[0]}</td><td class='r'>{r[1]/1000:,.1f}</td><td class='r'>{r[2]:.3f}</td><td class='r'>{usd(r[3])}</td>"
    f"<td class='r'>{usd(r[4])}</td><td class='r'>{usd(r[5]) if r[5] else '–'}</td><td class='r'>{usd(r[6])}</td><td class='r {'neg' if r[7] < 0 else ''}'>{usd(r[7])}</td></tr>"
    for r in d["rows"] if r[0] in (1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25))

sens_rows = "".join(
    f"<tr{' class=hl' if abs(s[0]-d['TARIFF'])<1e-9 else ''}><td class='c'>{s[0]:.2f}</td><td class='r'>{s[1]:.1f}</td><td class='r'>{s[2]*100:.0f}%</td><td class='r'>{usd(s[3])}</td></tr>"
    for s in d["sens"])

KWP = d["KWP"]
y1 = d["y1_gen"]

html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Rooftop Solar PV – Design &amp; Cost Report</title>
<style>
@page {{ size: A4; margin: 22mm 18mm 20mm 18mm; }}
@page :first {{ margin: 0; }}
:root {{ --ink:#1b2430; --muted:#5b6673; --rule:#c9d0d8; --navy:#14365d; --band:#eef2f6; }}
* {{ box-sizing:border-box; }}
html,body {{ margin:0; background:#fff; color:var(--ink); font-family:Inter, "DejaVu Sans", Arial, sans-serif; font-size:9.6pt; line-height:1.45; }}
h1,h2,h3 {{ color:var(--navy); margin:0; }}
h2 {{ font-size:14pt; border-bottom:1.5px solid var(--navy); padding-bottom:4px; margin:0 0 10px; break-after:avoid; }}
h3 {{ font-size:10.5pt; margin:14px 0 6px; break-after:avoid; }}
p {{ margin:0 0 8px; }}
table {{ width:100%; border-collapse:collapse; margin:4px 0 10px; break-inside:auto; }}
th,td {{ border:0.6pt solid var(--rule); padding:4px 6px; vertical-align:top; }}
th {{ background:var(--band); text-align:left; font-weight:600; color:var(--navy); }}
tr {{ break-inside:avoid; }}
td.r,th.r {{ text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }}
td.c,th.c {{ text-align:center; }}
tr.tot td {{ font-weight:700; background:var(--band); }}
tr.hl td {{ font-weight:700; }}
td.neg {{ color:#8a1c1c; }}
.kv td:first-child {{ width:42%; color:var(--muted); }}
.section {{ break-before:page; }}
.note {{ font-size:8.4pt; color:var(--muted); }}
.fig {{ text-align:center; margin:6px 0 4px; break-inside:avoid; }}
.fig img {{ max-width:100%; border:0.6pt solid var(--rule); }}
.cap {{ font-size:8.4pt; color:var(--muted); text-align:center; margin-bottom:10px; }}
.kpis {{ display:grid; grid-template-columns:repeat(4,1fr); gap:0; border:0.6pt solid var(--rule); margin:8px 0 12px; }}
.kpi {{ padding:8px 10px; border-right:0.6pt solid var(--rule); }}
.kpi:last-child {{ border-right:0; }}
.kpi b {{ display:block; font-size:15pt; color:var(--navy); font-variant-numeric:tabular-nums; }}
.kpi span {{ font-size:8pt; color:var(--muted); }}
ul,ol {{ margin:0 0 8px 0; padding-left:18px; }} li {{ margin-bottom:3px; }}
.chart {{ width:100%; height:auto; }}
.chart .g {{ stroke:#e3e7ec; stroke-width:1; }}
.chart .zero {{ stroke:#8c96a1; stroke-width:1; }}
.chart .line {{ fill:none; stroke:var(--navy); stroke-width:2.2; }}
.chart .pb {{ stroke:#8c96a1; stroke-width:1; stroke-dasharray:4 3; }}
.chart .ax {{ font-size:9px; fill:var(--muted); }}
.chart .ann {{ font-size:9.5px; fill:var(--ink); font-weight:600; }}
/* cover */
.cover {{ height:297mm; width:210mm; position:relative; display:flex; flex-direction:column; }}
.cover .hero {{ height:150mm; background:url('{b64("hotel.jpg","image/jpeg")}') center 35%/cover no-repeat; }}
.cover .band {{ height:3mm; background:var(--navy); }}
.cover .body {{ padding:16mm 18mm 0; flex:1; }}
.cover .eyebrow {{ font-size:9pt; letter-spacing:.14em; text-transform:uppercase; color:var(--muted); margin-bottom:6px; }}
.cover h1 {{ font-size:25pt; line-height:1.15; margin-bottom:6px; }}
.cover .sub {{ font-size:12.5pt; color:var(--ink); margin-bottom:14mm; }}
.cover table {{ width:62%; font-size:9pt; }}
.cover .foot {{ position:absolute; bottom:12mm; left:18mm; right:18mm; font-size:8pt; color:var(--muted); border-top:0.6pt solid var(--rule); padding-top:4px; display:flex; justify-content:space-between; }}
.toc td {{ border:0; border-bottom:0.6pt dotted var(--rule); padding:5px 2px; }}
.sig td {{ height:28px; }}
</style></head><body>

<!-- ===================== COVER ===================== -->
<div class="cover">
  <div class="hero"></div><div class="band"></div>
  <div class="body">
    <div class="eyebrow">Technical Report · Renewable Energy</div>
    <h1>Rooftop Solar PV System<br>Design Basis &amp; Cost Estimate</h1>
    <div class="sub">Marriott Hotel – Mezzanine Roof (Drawing D18102-DD-A-104)</div>
    <table class="kv">
      <tr><td>Document No.</td><td>{DOC_NO}</td></tr>
      <tr><td>Revision</td><td>{REV} – Issued for review</td></tr>
      <tr><td>Date</td><td>{DATE}</td></tr>
      <tr><td>System capacity</td><td>{KWP:.1f} kWp DC / {d['AC']:.0f} kW AC, grid-tied, no battery</td></tr>
    </table>
  </div>
  <div class="foot"><span>Rooftop Solar PV – Design Basis &amp; Cost Estimate</span><span>{DOC_NO} Rev {REV}</span></div>
</div>

<!-- ===================== DOC CONTROL ===================== -->
<div class="section">
<h2>Document Control</h2>
<table>
<tr><th style="width:12%">Rev</th><th style="width:20%">Date</th><th>Description</th><th style="width:16%">Prepared</th><th style="width:16%">Checked</th><th style="width:16%">Approved</th></tr>
<tr class="sig"><td class="c">{REV}</td><td>{DATE}</td><td>Issued for review</td><td></td><td></td><td></td></tr>
<tr class="sig"><td></td><td></td><td></td><td></td><td></td><td></td></tr>
</table>
<h3>Reference documents</h3>
<table>
<tr><th style="width:28%">Reference</th><th>Title</th></tr>
<tr><td>D18102-DD-A-104</td><td>Mezzanine floor plan incl. roof PV zones (architect)</td></tr>
<tr><td>D18102-DD-A-104 Layout1</td><td>Mezzanine plan with PV module layout, 10° tilt (this design)</td></tr>
<tr><td>PV_Layout_10deg_Mezzanine_Roof.dxf</td><td>PV layout CAD file – modules, tables, setbacks, dimensions</td></tr>
</table>
<h3>Contents</h3>
<table class="toc">
<tr><td>1. Executive Summary</td></tr><tr><td>2. Site and Design Basis</td></tr>
<tr><td>3. PV Array Layout</td></tr><tr><td>4. Electrical Design</td></tr>
<tr><td>5. Energy Yield</td></tr><tr><td>6. Cost Estimate (Bill of Quantities)</td></tr>
<tr><td>7. Financial Analysis</td></tr><tr><td>8. Expansion Options</td></tr>
<tr><td>9. Assumptions, Exclusions and Next Steps</td></tr>
</table>
</div>

<!-- ===================== 1 EXEC SUMMARY ===================== -->
<div class="section">
<h2>1. Executive Summary</h2>
<p>This report sets out the design basis, layout, energy yield and budget cost for a grid-tied rooftop solar
photovoltaic (PV) system on the mezzanine-level roof of the Marriott Hotel, as shown on architectural drawing
D18102-DD-A-104. The system has no battery storage and supplies the hotel's own load behind the utility meter.</p>
<div class="kpis">
  <div class="kpi"><b>{KWP:.1f} kWp</b><span>DC capacity ({d['N']} × {d['P']} Wp)</span></div>
  <div class="kpi"><b>{y1/1000:,.0f} MWh</b><span>Year-1 generation</span></div>
  <div class="kpi"><b>USD {d['capex']/1000:,.0f}k</b><span>Budget EPC cost ({d['usd_wp']:.2f} USD/Wp)</span></div>
  <div class="kpi"><b>{d['payback']:.1f} yrs</b><span>Simple payback</span></div>
</div>
<h3>Key findings</h3>
<ul>
<li><b>Capacity.</b> The two roof zones allocated for PV by the architect (≈1,150 m² gross, including the hatched
+4.85 m slab strip) accommodate <b>{d['N']} modules of {d['P']} Wp in 13 rows of 23</b>, giving <b>{KWP:.1f} kWp</b>
at 10° tilt with 800 mm maintenance aisles and 1.0 m edge setbacks.</li>
<li><b>Self-consumption.</b> The hotel consumes approximately <b>1,000,000 kWh per month</b> (average demand ≈1.37 MW).
The PV peak output (≈160 kW AC) is around one-tenth of the daytime load, so <b>100 % of the solar energy is consumed on site</b>.
No energy is exported and no battery is required.</li>
<li><b>Energy and savings.</b> Year-1 generation is about <b>{y1/1000:,.0f} MWh</b>, or {d['share']*100:.1f} % of the annual consumption.
At an avoided tariff of USD {d['TARIFF']:.2f}/kWh this saves about <b>USD {d['y1_sav']:,.0f} in year 1</b>.</li>
<li><b>Cost and return.</b> The budget turnkey (EPC) cost is <b>USD {usd(d['capex'])}</b> excluding taxes, including 7 % contingency.
Simple payback is <b>{d['payback']:.1f} years</b>, project IRR {d['irr']*100:.0f} % and 25-year NPV (10 %) USD {usd(d['npv'])}.
The levelised cost of solar energy is about <b>USD {d['lcoe']:.3f}/kWh</b>, below the grid tariff.</li>
<li><b>Path to 500 kWp.</b> The architect's solar zone limits this roof to 185.4 kWp. The balance of ≈315 kWp would need other roof areas or car-park canopies (Section 8).</li>
</ul>
<h3>Recommendation</h3>
<p>Proceed with the {KWP:.1f} kWp mezzanine roof system as Phase 1, subject to (i) a structural check of both slabs
for an added dead load of about 20–25 kg/m² (including ballast) and wind uplift, and (ii) confirmation of the avoided
tariff from recent utility bills. In parallel, survey other roof areas and the car park for Phase 2.</p>
</div>

<!-- ===================== 2 SITE & BASIS ===================== -->
<div class="section">
<h2>2. Site and Design Basis</h2>
<h3>2.1 Site and load</h3>
<table class="kv">
<tr><td>Facility</td><td>Marriott Hotel – twin towers with podium; PV on the mezzanine-level roof</td></tr>
<tr><td>Location</td><td>Uganda, equatorial (≈0–1° N); irradiation basis to be confirmed with site coordinates</td></tr>
<tr><td>Roof zones used</td><td>Upper block (+6.80 m SSL, 29.39 × 15.81 m) incl. hatched +4.85 m strip; lower block (architect's PV zone)</td></tr>
<tr><td>Annual electricity consumption</td><td>≈12,000,000 kWh (≈1,000,000 kWh/month)</td></tr>
<tr><td>Average / daytime demand</td><td>≈1,370 kW / ≈1,700 kW (hotel load profile assumed)</td></tr>
<tr><td>Grid connection</td><td>Behind-the-meter, LV main switchboard; zero-export control</td></tr>
<tr><td>Energy storage</td><td>None</td></tr>
</table>
<h3>2.2 Design criteria</h3>
<table>
<tr><th style="width:42%">Parameter</th><th>Value</th><th>Basis</th></tr>
<tr><td>Module</td><td>620 Wp bifacial TOPCon, 2382 × 1134 × 30 mm, ≈33 kg</td><td>Current Tier-1 mainstream size</td></tr>
<tr><td>Orientation / mounting</td><td>Portrait, 2 modules high (2P) per table</td><td>Matches roof depth</td></tr>
<tr><td>Tilt</td><td>10°</td><td>Low wind load, self-cleaning by rain</td></tr>
<tr><td>Table depth on plan</td><td>4,711 mm (2P); 2,346 mm (1P)</td><td>2 × 2382 + 20 mm, × cos 10°</td></tr>
<tr><td>Module clamp gap</td><td>20 mm</td><td>Mid-clamp</td></tr>
<tr><td>Aisle between tables</td><td>800 mm</td><td>No inter-row shading 09:00–15:00 all year (≥523 mm required); walkway for cleaning</td></tr>
<tr><td>Edge setback</td><td>1,000 mm (east side 1,742 mm)</td><td>Wind edge zone, safe access; clear of roof opening</td></tr>
<tr><td>Inverter DC voltage</td><td>1,100 V max</td><td>Standard C&amp;I string inverter</td></tr>
<tr><td>Design standards</td><td>IEC 62548, IEC 60364-7-712, IEC 61215/61730, IEC 62109, IEC 62305</td><td>PV array, wiring, modules, inverters, lightning</td></tr>
</table>
</div>

<!-- ===================== 3 LAYOUT ===================== -->
<div class="section">
<h2>3. PV Array Layout</h2>
<p>The array occupies the two roof zones allocated for PV on drawing D18102-DD-A-104. Each row holds 23 modules
(row length 26,522 mm). The upper block carries two 2P tables and one 1P table; the lower block carries four 2P tables.</p>
<div class="fig"><img src="{b64('layout.png','image/png')}" style="max-height:150mm"></div>
<div class="cap">Figure 1 – PV module layout on the mezzanine roof (extract from D18102-DD-A-104 Layout1). Upper block at top, lower block below.</div>
<table>
<tr><th>Zone</th><th>Tables</th><th class="r">Rows</th><th class="r">Modules</th><th class="r">kWp</th></tr>
<tr><td>Upper block (+6.80 m, incl. hatched +4.85 m strip)</td><td>2 × 2P + 1 × 1P</td><td class="r">5</td><td class="r">115</td><td class="r">71.3</td></tr>
<tr><td>Lower block (architect's PV zone)</td><td>4 × 2P</td><td class="r">8</td><td class="r">184</td><td class="r">114.1</td></tr>
<tr class="tot"><td>Total</td><td></td><td class="r">13</td><td class="r">{d['N']}</td><td class="r">{KWP:.1f}</td></tr>
</table>
<p class="note">Module area 807 m²; gross roof ≈1,150 m². Indicative added dead load ≈14 kg/m² for modules and structure, plus ballast to suit the wind design.</p>
</div>

<!-- ===================== 4 ELECTRICAL ===================== -->
<div class="section">
<h2>4. Electrical Design</h2>
<h3>4.1 Configuration</h3>
<table>
<tr><th>Item</th><th>Inverter INV-01</th><th>Inverter INV-02</th><th>Total</th></tr>
<tr><td>Rated AC power</td><td>80 kW</td><td>80 kW</td><td>160 kW</td></tr>
<tr><td>Strings</td><td>8 × 19 modules</td><td>3 × 19 + 5 × 18 modules</td><td>16 strings</td></tr>
<tr><td>Modules</td><td>152</td><td>147</td><td>{d['N']}</td></tr>
<tr><td>DC capacity</td><td>94.2 kWp</td><td>91.1 kWp</td><td>{KWP:.1f} kWp</td></tr>
<tr><td>DC/AC ratio</td><td>1.18</td><td>1.14</td><td>1.16</td></tr>
</table>
<h3>4.2 String voltage check</h3>
<table>
<tr><th style="width:46%">Check</th><th>Value</th><th>Limit</th><th>Result</th></tr>
<tr><td>Max. open-circuit voltage, 19 modules at 12 °C cell temperature (Voc ≈ 50.2 V)</td><td>954 V</td><td>≤ 1,100 V</td><td>OK</td></tr>
<tr><td>Min. MPP voltage, 18 modules at 65 °C cell temperature (Vmp ≈ 36.2 V)</td><td>652 V</td><td>≥ MPPT minimum (≈200 V)</td><td>OK</td></tr>
<tr><td>String current (Isc ≈ 16.1 A, ×1.25 for bifacial gain)</td><td>≈20 A</td><td>MPPT input rating</td><td>OK, max. 2 strings per MPPT</td></tr>
</table>
<p class="note">Module electrical values are typical for 620 Wp TOPCon modules. Re-check against the datasheet of the selected module and inverter.</p>
<h3>4.3 Single-line arrangement</h3>
<ol>
<li>PV strings → 6 mm² double-insulated PV cable in UV-resistant trunking → inverters mounted on the roof in a shaded, ventilated location.</li>
<li>Inverters (400 V, 3-phase) → AC combiner panel with outgoing 250 A MCCB, Type II SPD and an isolator at the roof.</li>
<li>AC combiner panel → 4C × 120 mm² Cu XLPE/SWA (≈80 m, confirm route) → dedicated 250 A outgoing way on the main LV switchboard.</li>
<li>Zero-export controller with CTs on the incomer limits PV output so the site never exports, satisfying utility interface requirements.</li>
<li>Earthing: array frames bonded and connected to the building earth; integrated with the existing lightning protection system (IEC 62305).</li>
</ol>
</div>

<!-- ===================== 5 YIELD ===================== -->
<div class="section">
<h2>5. Energy Yield</h2>
<table class="kv">
<tr><td>Specific yield (year 1, incl. losses)</td><td>{d['SY']:,} kWh/kWp/yr</td></tr>
<tr><td>Performance ratio assumed</td><td>≈ 0.80 (temperature, soiling, cabling, inverter, availability)</td></tr>
<tr><td>Year-1 generation</td><td>{y1:,.0f} kWh (≈ {y1/12:,.0f} kWh per month)</td></tr>
<tr><td>Degradation</td><td>1.0 % in year 1, then 0.4 %/yr</td></tr>
<tr><td>25-year generation</td><td>{d['gen25']/1000:,.0f} MWh</td></tr>
<tr><td>Self-consumption</td><td>100 % (PV peak ≈160 kW vs. daytime load ≈1,700 kW)</td></tr>
<tr><td>Share of hotel consumption</td><td>{d['share']*100:.1f} %</td></tr>
</table>
<p>At the equator the sun crosses close to overhead and day length is nearly constant, so monthly output is fairly even.
It is lowest in the main rainy seasons (March–May and October–November). Because the hotel load exceeds the PV output in
every hour, cloudy days reduce savings but never cause curtailment.</p>
<p class="note">The yield figure is a desktop estimate for an equatorial Ugandan site. A PVsyst simulation using the exact site coordinates
and Meteonorm/PVGIS data is recommended at detailed design.</p>
</div>

<!-- ===================== 6 BOQ ===================== -->
<div class="section">
<h2>6. Cost Estimate (Bill of Quantities)</h2>
<p>Budget turnkey (EPC) estimate in US dollars, based on 2026 East African market prices for commercial rooftop
systems. Accuracy class ±15 %.</p>
<table>
<tr><th class="c" style="width:5%">No.</th><th>Description</th><th class="c" style="width:12%">Qty</th><th class="r" style="width:15%">Rate</th><th class="r" style="width:13%">Amount (USD)</th></tr>
{boq_rows}
<tr class="tot"><td></td><td colspan="3">Sub-total</td><td class="r">{usd(d['sub'])}</td></tr>
<tr><td></td><td colspan="3">Contingency (7 %)</td><td class="r">{usd(d['cont'])}</td></tr>
<tr class="tot"><td></td><td colspan="3">Total budget EPC cost (excluding taxes)</td><td class="r">{usd(d['capex'])}</td></tr>
<tr><td></td><td colspan="3">Specific cost</td><td class="r">{d['usd_wp']:.3f} USD/Wp</td></tr>
</table>
<p class="note">Excludes VAT, withholding tax and import duties (solar equipment is generally zero-rated or exempt in Uganda; confirm with URA),
roof waterproofing upgrades, structural strengthening if required, and any utility charges. Annual O&amp;M (cleaning, inspection, monitoring)
is estimated at USD {usd(d['om0'])}/yr (≈1.2 % of capex), escalating at 3 %/yr.</p>
</div>

<!-- ===================== 7 FINANCIAL ===================== -->
<div class="section">
<h2>7. Financial Analysis</h2>
<table class="kv">
<tr><td>Investment (EPC, excluding taxes)</td><td>USD {usd(d['capex'])}</td></tr>
<tr><td>Avoided grid tariff (year 1) / escalation</td><td>USD {d['TARIFF']:.2f}/kWh / {d['ESC']*100:.0f} % per year</td></tr>
<tr><td>Year-1 savings</td><td>USD {usd(d['y1_sav'])}</td></tr>
<tr><td>Inverter replacement (year 12)</td><td>USD 9,600</td></tr>
<tr><td>Simple payback</td><td>{d['payback']:.1f} years</td></tr>
<tr><td>Project IRR (25 years, unlevered)</td><td>{d['irr']*100:.1f} %</td></tr>
<tr><td>NPV at 10 % discount rate</td><td>USD {usd(d['npv'])}</td></tr>
<tr><td>Levelised cost of energy (LCOE)</td><td>USD {d['lcoe']:.3f}/kWh</td></tr>
<tr><td>25-year cumulative savings, net of O&amp;M</td><td>USD {usd(d['cum'][-1] + d['capex'])}</td></tr>
</table>
<div class="fig" style="border:0">{chart}</div>
<div class="cap">Figure 2 – Cumulative net cash flow (USD)</div>
<h3>Tariff sensitivity</h3>
<table>
<tr><th class="c">Avoided tariff (USD/kWh)</th><th class="r">Payback (yrs)</th><th class="r">IRR</th><th class="r">NPV @10 % (USD)</th></tr>
{sens_rows}
</table>
</div>

<div class="section">
<h3 style="margin-top:0">Annual cash flow (selected years, USD)</h3>
<table>
<tr><th class="c">Year</th><th class="r">Generation (MWh)</th><th class="r">Tariff (USD/kWh)</th><th class="r">Savings</th><th class="r">O&amp;M</th><th class="r">Replacement</th><th class="r">Net cash flow</th><th class="r">Cumulative</th></tr>
<tr><td class="c">0</td><td></td><td></td><td></td><td></td><td></td><td class="r">{usd(-d['capex'])}</td><td class="r neg">{usd(-d['capex'])}</td></tr>
{cf_rows}
</table>

<!-- ===================== 8 EXPANSION ===================== -->
<h2 style="margin-top:18px">8. Expansion Options</h2>
<p>The target of about 500 kWp exceeds what the mezzanine roof can hold. Because the hotel load is around ten times the PV output,
every additional kWp would also be fully self-consumed. Expansion can be added in stages without a battery.</p>
<table>
<tr><th>Option</th><th class="r">Capacity</th><th class="r">Year-1 energy</th><th class="r">Budget cost (USD)</th><th>Remarks</th></tr>
<tr><td>Phase 1 – mezzanine roof (this report)</td><td class="r">185.4 kWp</td><td class="r">274 MWh</td><td class="r">{usd(d['capex'])}</td><td>Ready for detailed design</td></tr>
<tr><td>Other roofs (left podium roof ≈370 m², lobby roof)</td><td class="r">≈ 65–120 kWp</td><td class="r">≈ 95–180 MWh</td><td class="r">≈ 38,000–68,000</td><td>Survey and structural check required</td></tr>
<tr><td>Car-park solar canopies</td><td class="r">≈ 150–250 kWp</td><td class="r">≈ 220–370 MWh</td><td class="r">≈ 0.75–0.85 USD/Wp</td><td>Adds shaded parking; steel canopy cost</td></tr>
<tr class="tot"><td>Indicative total</td><td class="r">≈ 400–555 kWp</td><td class="r">≈ 590–825 MWh</td><td class="r"></td><td>≈ 5–7 % of hotel consumption</td></tr>
</table>
</div>

<!-- ===================== 9 ASSUMPTIONS ===================== -->
<div class="section">
<h2>9. Assumptions, Exclusions and Next Steps</h2>
<h3>9.1 Key assumptions</h3>
<ul>
<li>Roof geometry is taken from drawing D18102-DD-A-104; the hatched +4.85 m slab strip is available for PV, as confirmed by the client.</li>
<li>Both roof slabs can carry the PV dead load and wind loads without strengthening, subject to verification by the structural engineer.</li>
<li>The hotel load is about 1,000,000 kWh per month with a continuous daytime demand well above 160 kW.</li>
<li>The avoided tariff is USD {d['TARIFF']:.2f}/kWh escalating at {d['ESC']*100:.0f} %/yr, to be confirmed from the latest utility bills (energy plus demand components).</li>
<li>Prices are 2026 East African market levels in USD, excluding taxes. The exchange rate is not considered.</li>
</ul>
<h3>9.2 Exclusions</h3>
<ul>
<li>Battery storage, diesel-generator synchronisation and export metering.</li>
<li>Roof waterproofing renewal, structural strengthening, and civil works to the LV room.</li>
<li>Utility network upgrades, permit fees and financing costs.</li>
</ul>
<h3>9.3 Recommended next steps</h3>
<ol>
<li>Obtain 12 months of utility bills or interval-meter data and confirm the tariff structure.</li>
<li>Commission a structural assessment of both slabs (dead load, ballast, wind uplift) and agree the roof fixing method with the architect.</li>
<li>Confirm the inverter location, AC cable route and spare way on the main LV switchboard.</li>
<li>Run a PVsyst simulation with site coordinates and the selected module and inverter datasheets.</li>
<li>Issue the tender package (layout, single-line diagram, specification, BOQ) to at least three qualified EPC contractors.</li>
<li>Start the Phase 2 survey of other roofs and the car park to move towards the 500 kWp target.</li>
</ol>
</div>

</body></html>"""
open(os.path.join(HERE, "Rooftop_PV_Report.html"), "w").write(html)
print("ok")
