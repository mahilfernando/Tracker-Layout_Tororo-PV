"""Separate technical note: justification of 18–19 module strings vs the usual 16–17 for the Sigen PV 80M1.
Run: python3 build_string_justification.py && node string_note_pdf.js -> String_Sizing_Justification.pdf"""
import os, base64
HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = "data:image/png;base64," + base64.b64encode(open(os.path.join(HERE, "nilesun_logo.png"), "rb").read()).decode()

# module: Astronergy ASTRO N7 CHSM66RN(DG)/F-BH 620 W (datasheet, Annex 4)
VOC, VMP, ISC, IMP = 49.04, 41.56, 16.11, 14.92
K_VOC, K_VMP, K_ISC = -0.0025, -0.0027, 0.00043      # Vmp coefficient assumed ≈ Pmax coeff (−0.29 %/°C) minus current share
T_MIN, T_MAX, BIF = 10, 70, 1.10                      # cell temperatures (°C), bifacial current gain
# inverter: Sigenergy Sigen PV 80M1 (datasheet, Annex 3)
VDC_MAX, MPPT_LO, MPPT_HI, V_NOM, V_START = 1100, 160, 1000, 600, 180
N_MPPT, STR_PER_MPPT, I_MPPT, ISC_MPPT = 6, 2, 40, 60

voc_c = VOC * (1 + K_VOC * (T_MIN - 25)); vmp_c = VMP * (1 + K_VMP * (T_MIN - 25)); vmp_h = VMP * (1 + K_VMP * (T_MAX - 25))
isc_h = ISC * (1 + K_ISC * (T_MAX - 25))
ok = lambda b: '<b class="ok">✔</b>' if b else '<b class="no">✘</b>'
rows = []
for n in (16, 17, 18, 19):
    a, b, c, e = n * voc_c, n * vmp_c, n * VMP, n * vmp_h
    rows.append(f"<tr{' class=hl' if n >= 18 else ''}><td>{n}</td><td>{a:,.0f} {ok(a <= VDC_MAX)}</td><td>{(1-a/VDC_MAX)*100:.0f} %</td>"
                f"<td>{b:,.0f} {ok(b <= MPPT_HI)}</td><td>{c:,.0f}</td><td>{e:,.0f} {ok(e >= MPPT_LO and e >= V_START)}</td><td>{c/V_NOM:.2f}</td></tr>")
nmax = int(VDC_MAX // voc_c); nmin = int(-(-max(MPPT_LO, V_START) // vmp_h))
i2 = STR_PER_MPPT * IMP; i2b = i2 * BIF; isc2 = STR_PER_MPPT * isc_h * BIF

html = f"""<!doctype html><html><head><meta charset="utf-8"><title>String Sizing Justification</title><style>
@page {{ size:A4; margin:0 }} * {{ box-sizing:border-box }}
body {{ margin:0; font-family:Arial,Helvetica,sans-serif; font-size:9pt; color:#222; -webkit-print-color-adjust:exact; print-color-adjust:exact }}
.page {{ width:210mm; height:297mm; overflow:hidden; padding:10mm 16mm 12mm; position:relative; page-break-after:always }}
.hdr {{ display:flex; align-items:center; gap:5mm; border-bottom:3px solid #1f3f8f; padding-bottom:3mm }} .hdr img {{ height:18mm }}
.hdr b {{ color:#1f3f8f; font-size:13pt }} .hdr span {{ color:#6b7480; font-size:8.5pt; display:block }}
h1 {{ color:#1f3f8f; font-size:16pt; margin:5mm 0 1mm }} .sub {{ color:#6b7480; margin-bottom:3mm }}
h2 {{ color:#1f3f8f; font-size:11pt; margin:3.5mm 0 1.5mm; border-left:2.4mm solid #f4a522; padding-left:2.5mm }}
table {{ width:100%; border-collapse:collapse; margin:1mm 0 2mm }} th,td {{ border:1px solid #cfd6e0; padding:1mm 1.8mm; text-align:left }}
th {{ background:#eef2f8 }} tr.hl td {{ background:#fff6e6; font-weight:700 }} .ok {{ color:#2e8b3a }} .no {{ color:#c0392b }}
p {{ line-height:1.45; margin:0 0 2mm }} .small {{ font-size:8.5pt; color:#555 }} ul {{ margin:0 0 2mm; padding-left:5mm; line-height:1.45 }}
.box {{ background:#eef7ee; border-left:4px solid #2e8b3a; padding:3mm 4mm; margin:3mm 0 }}
.ftr {{ position:absolute; bottom:6mm; left:16mm; right:16mm; border-top:1px solid #cfd6e0; padding-top:1.5mm; font-size:7.5pt; color:#6b7480; display:flex; justify-content:space-between }}
</style></head><body>
<section class="page">
<div class="hdr"><img src="{LOGO}"/><div><b>NILESUN POWER LTD</b><span>Internal technical note – not part of the client proposal</span></div></div>
<h1>String Sizing Justification – 18 / 19 Modules per String</h1>
<div class="sub">Kampala Marriott Hotel · 185.4 kWp · 299 × Astronergy ASTRO N7 620 W · 2 × Sigenergy Sigen PV 80M1 · Ref. NSP-261105-KMH</div>

<h2>1. Design question</h2>
<p>For 1,100 V C&amp;I string inverters, 16–17 modules per string is a common rule of thumb. This design uses
<b>19 modules (INV-01: 8 × 19; INV-02: 3 × 19)</b> and <b>18 modules (INV-02: 5 × 18)</b> – 16 strings in total. This note checks that 18–19
modules stay inside every inverter limit and explains why they are preferred here.</p>

<h2>2. Data used</h2>
<table><tr><th>Module (datasheet)</th><th>Value</th><th>Inverter Sigen PV 80M1 (datasheet)</th><th>Value</th></tr>
<tr><td>Voc / Vmp (STC)</td><td>{VOC} V / {VMP} V</td><td>Max. DC input voltage</td><td>{VDC_MAX:,} V</td></tr>
<tr><td>Isc / Imp (STC)</td><td>{ISC} A / {IMP} A</td><td>MPPT voltage range</td><td>{MPPT_LO} – {MPPT_HI:,} V</td></tr>
<tr><td>Temp. coeff. Voc / Isc</td><td>−0.25 %/°C / +0.043 %/°C</td><td>Nominal DC voltage / start-up</td><td>{V_NOM} V / {V_START} V</td></tr>
<tr><td>Temp. coeff. Vmp (assumed)</td><td>−0.27 %/°C</td><td>MPP trackers × strings per MPPT</td><td>{N_MPPT} × {STR_PER_MPPT}</td></tr>
<tr><td>Max. system voltage</td><td>1,500 V DC</td><td>Max. input / short-circuit current per MPPT</td><td>{I_MPPT} A / {ISC_MPPT} A</td></tr></table>
<p class="small">Site temperatures (Kampala, 1,180 m): minimum cell temperature {T_MIN} °C (cool clear dawn – record ambient minimum ≈ 10–12 °C);
maximum cell temperature {T_MAX} °C (hot roof, low tilt). Bifacial rear-side current gain taken as +10 %.</p>

<h2>3. Voltage check per string length</h2>
<table><tr><th>Modules in series</th><th>Voc at {T_MIN} °C (≤ {VDC_MAX:,} V)</th><th>Margin to 1,100 V</th><th>Vmp at {T_MIN} °C (≤ {MPPT_HI:,} V)</th>
<th>Vmp at STC</th><th>Vmp at {T_MAX} °C (≥ {max(MPPT_LO, V_START)} V)</th><th>Vmp STC ÷ 600 V nominal</th></tr>{"".join(rows)}</table>
<p>Limits for this module and inverter at Kampala temperatures: <b>maximum {nmax} modules</b> (Voc cold ≤ 1,100 V) and <b>minimum {nmin} modules</b>
(hot Vmp ≥ start-up voltage). <b>18 and 19 modules are well inside this range</b>: the coldest open-circuit voltage of a 19-module string is
{19*voc_c:,.0f} V – {(1-19*voc_c/VDC_MAX)*100:.0f} % below the 1,100 V limit – and the operating voltage stays inside the 160–1,000 V MPPT window at
all temperatures ({19*vmp_h:,.0f}–{19*vmp_c:,.0f} V for 19 modules, {18*vmp_h:,.0f}–{18*vmp_c:,.0f} V for 18 modules).</p>

<h2>4. Current check per MPPT (2 strings in parallel)</h2>
<table><tr><th>Check</th><th>Value</th><th>Limit</th><th>Result</th></tr>
<tr><td>Operating current, 2 × Imp</td><td>{i2:.1f} A ({i2b:.1f} A with +10 % bifacial gain)</td><td>{I_MPPT} A max. input</td><td>{ok(i2b <= I_MPPT)}</td></tr>
<tr><td>Short-circuit current, 2 × Isc at {T_MAX} °C × 1.10 bifacial</td><td>{isc2:.1f} A</td><td>{ISC_MPPT} A max. short-circuit</td><td>{ok(isc2 <= ISC_MPPT)}</td></tr>
<tr><td>Strings per inverter</td><td>8 (uses 4 of 6 MPPTs, 2 strings each)</td><td>{N_MPPT * STR_PER_MPPT} strings</td><td>{ok(True)}</td></tr></table>
<p class="small">String length does not change the current – the current check is the same for 16–19 modules.</p>
<div class="ftr"><span>NileSun Power Ltd · String sizing note · Kampala Marriott 185.4 kWp</span><span>Page 1 of 2</span></div>
</section>

<section class="page">
<div class="hdr"><img src="{LOGO}"/><div><b>NILESUN POWER LTD</b><span>Internal technical note – not part of the client proposal</span></div></div>
<h2>5. Comparison of stringing options for 299 modules</h2>
<table><tr><th>Item</th><th>Design: 19 / 18 modules</th><th>Alternative: 17 / 16 modules</th></tr>
<tr><td>Strings</td><td><b>16</b> (11 × 19 + 5 × 18)</td><td>18 (11 × 17 + 7 × 16)</td></tr>
<tr><td>Per inverter</td><td>8 + 8 strings → 4 MPPTs fully paired on each</td><td>9 + 9 strings → 5 MPPTs, one MPPT with a single string</td></tr>
<tr><td>DC isolators + DC SPDs</td><td>16 + 16</td><td>18 + 18 (+ 4 units)</td></tr>
<tr><td>String home-run cable pairs</td><td>16</td><td>18 (≈ 12 % more DC cable)</td></tr>
<tr><td>String operating voltage (STC)</td><td>748–790 V</td><td>665–707 V</td></tr>
<tr><td>DC ohmic loss (same power, same cable)</td><td>lower – ∝ 1/V²; ≈ 20 % less than 17/16</td><td>higher</td></tr>
<tr><td>Inverter efficiency (nearer 600 V nominal)</td><td>very slightly lower (typ. &lt; 0.2 %)</td><td>very slightly higher</td></tr>
<tr><td>Voc margin to 1,100 V at {T_MIN} °C</td><td>{(1-19*voc_c/VDC_MAX)*100:.0f} % (19 mod.)</td><td>{(1-17*voc_c/VDC_MAX)*100:.0f} % (17 mod.)</td></tr></table>

<h2>6. Why 16–17 is the usual rule – and why it does not limit this site</h2>
<ul><li>16–17 modules keep the cold open-circuit voltage far below 1,000–1,100 V in <b>cold climates</b> (design minimum −10 °C or lower), and keep the
operating voltage close to the inverter's 600 V nominal point.</li>
<li>Kampala is equatorial at 1,180 m – cell temperature does not fall much below 10 °C – so even 19 modules leave a 12 % voltage margin.</li>
<li>299 modules divide neatly into <b>16 strings of 19/18</b>, pairing exactly on 4 MPPTs per inverter. 16/17-module strings need 18 strings and leave
one MPPT on each inverter with a single string.</li>
<li>Fewer, higher-voltage strings mean fewer isolators and SPDs, less DC cable and lower DC losses, which outweighs the small efficiency
advantage of operating closer to 600 V.</li></ul>
<div class="box"><b>Conclusion:</b> 18- and 19-module strings are within the Sigen PV 80M1 limits at all Kampala temperatures (maximum {nmax} modules) and are
the better fit for 299 modules. The design is kept at 16 strings: INV-01 8 × 19; INV-02 3 × 19 + 5 × 18. A 17/16 layout is also technically possible
if a client specification requires it.</div>
<p class="small">Action: the PVsyst model currently uses 23 strings × 13 modules – update it to the design stringing above before the final simulation.
Vmp temperature coefficient assumed (−0.27 %/°C) – confirm with the module manufacturer's datasheet or PAN file.</p>
<div class="ftr"><span>NileSun Power Ltd · String sizing note · Kampala Marriott 185.4 kWp</span><span>Page 2 of 2</span></div>
</section></body></html>"""
open(os.path.join(HERE, "String_Sizing_Justification.html"), "w").write(html)
print("max", nmax, "min", nmin, "voc19", round(19 * voc_c), "vmp19 hot", round(19 * vmp_h), "i2b", round(i2b, 1), "isc2", round(isc2, 1))
