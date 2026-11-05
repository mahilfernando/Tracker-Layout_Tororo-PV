"""A3 drawing sheet for the Enerack-based PV layout: plan + sections + schedule + title block.
Run after make_pv_layout_enerack.py, then: node layout_sheet_pdf.js
"""
import math, os
HERE = os.path.dirname(os.path.abspath(__file__))
plan = open(os.path.join(HERE, "PV_Layout_Enerack_10deg.svg")).read()
TILT = 10; c, s = math.cos(math.radians(TILT)), math.sin(math.radians(TILT))

def section(rows, front_off, span, front_h, rails, label):
    L, G = 2382, 20
    sl = rows * L + (rows - 1) * G
    k = 0.07                                         # px/mm
    ox, base = 30, 150
    X = lambda mm: ox + mm * k; Y = lambda mm: base - mm * k
    # module low edge at (0, h0); front post at slope front_off
    h0 = front_h - front_off * s
    x0 = 0
    g = f'<line class="slab" x1="{X(-200)}" y1="{Y(0)}" x2="{X(sl*c+300)}" y2="{Y(0)}"/>'
    g += f'<line class="smod" x1="{X(x0):.1f}" y1="{Y(h0):.1f}" x2="{X(x0+sl*c):.1f}" y2="{Y(h0+sl*s):.1f}"/>'
    xf, xr_ = front_off * c, front_off * c + span
    hr = h0 + (front_off * c + span) / c * s
    for xx, hh in ((xf, front_h), (xr_, hr)):
        g += f'<line class="spost" x1="{X(xx):.1f}" y1="{Y(0):.1f}" x2="{X(xx):.1f}" y2="{Y(hh):.1f}"/>'
        g += f'<rect class="sblk" x="{X(xx)-10:.1f}" y="{Y(0)-1:.1f}" width="20" height="8"/>'
    if rows == 2:
        g += f'<line class="spost" x1="{X(xf):.1f}" y1="{Y(0):.1f}" x2="{X(xr_):.1f}" y2="{Y(hr*0.55):.1f}"/>'
    for r in rails:
        g += f'<circle class="srail" cx="{X(r*c):.1f}" cy="{Y(h0+r*s)-4:.1f}" r="3"/>'
    dims = [(0, sl * c, 172, f"{sl*c:,.0f} plan depth"), (xf, xr_, 194, f"{span:,} feet span")]
    for a, b, yy, t in dims:
        g += (f'<line class="sd" x1="{X(a):.1f}" y1="{yy}" x2="{X(b):.1f}" y2="{yy}"/>'
              f'<line class="sd" x1="{X(a):.1f}" y1="{yy-3}" x2="{X(a):.1f}" y2="{yy+3}"/><line class="sd" x1="{X(b):.1f}" y1="{yy-3}" x2="{X(b):.1f}" y2="{yy+3}"/>'
              f'<text class="st" x="{(X(a)+X(b))/2:.1f}" y="{yy-3}" text-anchor="middle">{t}</text>')
    g += f'<text class="st" x="{X(xf)-14:.1f}" y="{Y(front_h/2)+4:.1f}" text-anchor="end">{front_h}</text>'
    g += f'<text class="st" x="{X(xr_)+4:.1f}" y="{Y(hr/2):.1f}">{hr:,.0f} rear post</text>'
    g += f'<text class="st" x="{X(sl*c)+4:.1f}" y="{Y(h0+sl*s)+3:.1f}">top edge ≈{h0+sl*s:,.0f}</text>'
    g += f'<text class="st" x="{X(sl*c*0.35):.1f}" y="{Y(h0+sl*0.35*s)-12:.1f}">{TILT}°</text>'
    g += f'<text class="sh" x="{X(-200)}" y="20">{label}</text>'
    return f'<svg viewBox="0 0 {X(4711+1300):.0f} 200" class="secsvg">{g}</svg>'

sec2 = section(2, 300, 3402, 595, [491, 1891, 2893, 4293], "SECTION A – 2P TABLE (2 × 23 modules)")
sec1 = section(1, 200, 1136, 200, [491, 1891], "SECTION B – 1P TABLE (1 × 23 modules)")

html = f"""<!doctype html><html><head><meta charset="utf-8"><title>PV Layout – Enerack</title>
<style>
@page {{ size: A3 landscape; margin: 8mm; }}
html,body {{ margin:0; background:#fff; color:#1b2430; font-family:Inter,"DejaVu Sans",Arial,sans-serif; }}
.sheet {{ width:404mm; height:280mm; overflow:hidden; border:0.8mm solid #1b2430; display:grid; grid-template-columns: 1fr 112mm; box-sizing:border-box; }}
.left {{ padding:4mm; border-right:0.5mm solid #1b2430; display:flex; flex-direction:column; }}
.left h3 {{ margin:0 0 2mm; font-size:11pt; color:#14365d; }}
.plan {{ width:100%; height:auto; max-height:262mm; }}
.right {{ display:flex; flex-direction:column; font-size:8pt; }}
.box {{ border-bottom:0.4mm solid #1b2430; padding:2.2mm 3mm; }}
.box h4 {{ margin:0 0 1.5mm; font-size:8.5pt; color:#14365d; }}
table {{ width:100%; border-collapse:collapse; }}
td,th {{ border:0.25mm solid #9aa4ae; padding:1mm 1.5mm; text-align:left; }}
th {{ background:#eef2f6; }}
td.r {{ text-align:right; }}
.secsvg {{ width:100%; height:auto; max-height:44mm; }}
.grow {{ flex:1; }}
.tb td {{ border:0.25mm solid #1b2430; }}
.tb .big {{ font-size:12pt; font-weight:700; color:#14365d; }}
.legend span {{ display:inline-block; width:9mm; height:0; border-top:0.7mm solid; vertical-align:middle; margin-right:2mm; }}
/* plan classes */
.plan .mod {{ fill:#dfe7f5; stroke:#1f4fb5; stroke-width:0.5; }}
.plan .mod2 {{ fill:#dcf2e8; stroke:#1b8f63; stroke-width:0.5; }}
.plan .inv {{ fill:#14365d; stroke:#14365d; }}
.plan .acc {{ fill:#c27a00; stroke:#c27a00; }}
.plan .canopy {{ fill:none; stroke:#14365d; stroke-width:0.8; stroke-dasharray:4 2; }}
.plan .clear {{ fill:#eef2f6; stroke:#9aa4ae; stroke-width:0.5; stroke-dasharray:2 2; }}
.plan .tray {{ stroke:#c0392b; stroke-width:1.6; stroke-dasharray:6 3; }}
.plan .c3 {{ stroke:#1b2430; stroke-width:1.8; stroke-dasharray:8 3 2 3; }}
.plan .duct {{ fill:#f3e8f3; stroke:#a100a1; stroke-width:0.6; stroke-dasharray:3 2; }}
.plan .zlim {{ stroke:#6b7682; stroke-width:0.8; stroke-dasharray:10 3 2 3; }}
.plan .zlab, .plan .dlab {{ font-size:7px; fill:#5b6673; font-style:italic; }}
.plan .elab {{ font-size:7.5px; font-weight:700; fill:#14365d; }}
.plan .elab2 {{ font-size:7px; fill:#14365d; }}
.plan .trlab {{ font-size:7px; fill:#c0392b; }}
.plan .c3lab {{ font-size:7px; fill:#1b2430; }}
.plan .leader {{ stroke:#14365d; stroke-width:0.6; }}
.plan .dframe {{ fill:#ffffff; stroke:#14365d; stroke-width:0.9; }}
.plan .dtitle {{ font-size:7.5px; font-weight:700; fill:#14365d; }}
.plan .dlabel {{ font-size:7px; font-weight:700; fill:#1b2430; }}
.plan .dsmall, .plan .dsmallr {{ font-size:6px; fill:#4a5561; }}
.plan .mod-opt {{ fill:#fdebd6; stroke:#d97a00; stroke-width:0.5; }}
.plan .rail {{ stroke:#00a3b4; stroke-width:0.6; }}
.plan .rail-opt {{ stroke:#e0a050; stroke-width:0.6; }}
.plan .frame {{ stroke:#1f8a3a; stroke-width:0.9; }}
.plan .frame-opt {{ stroke:#d97a00; stroke-width:0.9; }}
.plan .foot {{ fill:#555; stroke:none; }}
.plan .foot-opt {{ fill:#d97a00; stroke:none; }}
.plan .roof {{ fill:none; stroke:#1b2430; stroke-width:1.6; }}
.plan .set {{ fill:none; stroke:#d0202a; stroke-width:0.7; stroke-dasharray:5 3; }}
.plan .obs {{ fill:none; stroke:#a100a1; stroke-width:1; }}
.plan .olab {{ font-size:7px; fill:#a100a1; }}
.plan .tlab {{ font-size:8px; fill:#1b2430; }}
.plan .dim {{ stroke:#6b7682; stroke-width:0.6; }}
.plan .dt {{ font-size:7.5px; fill:#4a5561; }}
.secsvg .slab {{ stroke:#1b2430; stroke-width:2; }}
.secsvg .smod {{ stroke:#1f4fb5; stroke-width:4; }}
.secsvg .spost {{ stroke:#1f8a3a; stroke-width:1.6; }}
.secsvg .sblk {{ fill:#555; }}
.secsvg .srail {{ fill:#00a3b4; }}
.secsvg .sd {{ stroke:#6b7682; stroke-width:0.6; }}
.secsvg .st {{ font-size:13px; fill:#4a5561; }}
.secsvg .sh {{ font-size:15px; font-weight:700; fill:#14365d; }}
</style></head><body><div class="sheet">
<div class="left"><h3>PLAN – PV LAYOUT, INVERTERS &amp; ACCP ON MEZZANINE ROOF (ENERACK BALLAST, 10° TILT)</h3>{plan}</div>
<div class="right">
 <div class="box">{sec2}</div>
 <div class="box">{sec1}</div>
 <div class="box"><h4>TABLE SCHEDULE</h4>
  <table><tr><th>Table</th><th>Type</th><th class="r">Modules</th><th>Inverter</th></tr>
  <tr><td>T1, T2</td><td>2P × 23</td><td class="r">92</td><td>INV-01</td></tr>
  <tr><td>T3</td><td>1P × 23</td><td class="r">23</td><td>INV-01</td></tr>
  <tr><td>T4</td><td>2P × 23</td><td class="r">46</td><td>INV-01: 37 · INV-02: 9</td></tr>
  <tr><td>T5–T7</td><td>2P × 23</td><td class="r">138</td><td>INV-02</td></tr>
  <tr><th colspan="2">TOTAL (77 frames, 26 rail lines)</th><th class="r">299</th><th>INV-01 152 · INV-02 147</th></tr>
</table>
 </div>
 <div class="box"><h4>DESIGN DATA</h4>
  <table>
  <tr><td>Module</td><td>620 Wp bifacial TOPCon, 2382 × 1134 × 30 mm</td></tr>
  <tr><td>Structure</td><td>Enerack ballast, dwg EPJ-26110401 V1.0</td></tr>
  <tr><td>Tilt / wind / snow</td><td>10° / 35 m/s / 0 kN/m²</td></tr>
  <tr><td>Rails</td><td>R80, 8 × 3000 + 2630 = 26,630 mm per line</td></tr>
  <tr><td>Frames</td><td>11 per table: first at 315, then 10 × 2,600</td></tr>
  <tr><td>Spacing</td><td>20 mm module gap · 800 mm aisle · ≥ 950 mm rail to wall</td></tr>
  </table>
 </div>
 <div class="box legend"><h4>LEGEND</h4>
  <div><span style="border-color:#1f4fb5;width:4mm"></span>INV-01 modules &nbsp; <span style="border-color:#1b8f63;width:4mm"></span>INV-02 modules &nbsp; <b style="color:#14365d">■</b> Inverter &nbsp; <b style="color:#c27a00">■</b> ACCP</div>
  <div><span style="border-color:#c0392b;border-top-style:dashed"></span>DC cable tray &nbsp; <span style="border-color:#1b2430;border-top-style:dashed"></span>C3 + E3 to LV room &nbsp; <span style="border-color:#a100a1;border-top-style:dotted"></span>Existing ducts</div>
  <div><span style="border-color:#00a3b4"></span>Rail &nbsp; <span style="border-color:#1f8a3a"></span>Frame / post &nbsp; ■ Foot block (300 × 300 indicative)</div>
  <div><span style="border-color:#d0202a;border-top-style:dashed"></span>Setback line &nbsp; <span style="border-color:#a100a1"></span>Obstruction</div>
 </div>
 <div class="box grow" style="font-size:7.5pt;color:#4a5561">NOTES: 1. Dimensions in mm. 2. Roof outline traced from D18102-DD-A-104; verify on site.
 3. Foot block size and ballast weight per Enerack calculation; roof load to be approved by the building structural engineer. 4. All tables lie within the architect's solar zone. 5. Inverter station and duct positions indicative – confirm on site with the hotel; C3 riser route and LV room location TBC.</div>
 <div class="tb"><table>
  <tr><td colspan="2" class="big">ROOFTOP SOLAR PV LAYOUT</td></tr>
  <tr><td>Project</td><td>Marriott Hotel – Mezzanine Roof</td></tr>
  <tr><td>Client</td><td>Kampala Marriott Hotel</td></tr>
  <tr><td>Drawing No.</td><td>PV-LAY-D18102-002 &nbsp; Rev B</td></tr>
  <tr><td>Date / Scale</td><td>4 November 2026 · NTS (A3)</td></tr>
 </table></div>
</div></div></body></html>"""
open(os.path.join(HERE, "PV_Layout_Enerack_10deg.html"), "w").write(html)
print("ok")
