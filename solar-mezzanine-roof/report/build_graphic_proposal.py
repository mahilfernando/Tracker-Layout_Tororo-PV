"""16-page graphic proposal (A4) for Kampala Marriott rooftop PV - same sections as the Canva design.
Run: python3 build_graphic_proposal.py && node graphic_to_pdf.js  -> Kampala_Marriott_PV_Graphic_Proposal.pdf
"""
import os, json, base64

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
fin = json.load(open(os.path.join(HERE, "proposal_fin.json")))
mon = json.load(open(os.path.join(HERE, "monthly.json")))
tou = json.load(open(os.path.join(HERE, "tou.json")))

NAVY, ORG, GRN, INK, MUT, BG = "#12438d", "#f39a1e", "#2e8b3a", "#1d2733", "#5b6673", "#f3f6fa"

def img(path):
    ext = path.rsplit(".", 1)[1].lower().replace("jpg", "jpeg")
    return f"data:image/{ext};base64," + base64.b64encode(open(path, "rb").read()).decode()

LOGO = img(os.path.join(HERE, "nilesun_logo.png"))
HOTEL = img(os.path.join(HERE, "hotel.jpg"))
OVERLAY = img(os.path.join(ROOT, "visual", "Marriott_roof_PV_overlay_zoom.png"))
BLOCK = img(os.path.join(ROOT, "sld", "PV_Block_Diagram.png"))
LAYOUT = img(os.path.join(HERE, "layout.png"))

def usd(v, d=0): return f"USD {v:,.{d}f}"
capex, y1, npv, irr, pb, lcoe = fin["capex"], fin["cf"][1], fin["npv"], fin["irr"], fin["pb"], fin["lcoe"]
net25, sav25, tar = fin["net25"], fin["sav25"], fin["tar"]
gen1 = fin["gen"][0]
savings = [fin["gen"][i] * tar * 1.02 ** i for i in range(25)]   # gross annual savings
roi = (net25 - capex) / capex   # 370 % (net gain over investment)
pages = []

def page(n, title, body, cls=""):
    head = (f'<div class="hdr"><div class="brand"><img src="{LOGO}"/>Nile Sun Power Ltd</div>'
            f'<div>Kampala Marriott Hotel &nbsp;|&nbsp; Solar PV Proposal</div></div>'
            f'<div class="bar"><i style="background:{NAVY}"></i><i style="background:{ORG}"></i><i style="background:{GRN}"></i></div>')
    t = f'<h1>{title}</h1><div class="uline"></div>' if title else ""
    foot = (f'<div class="ftr"><span>Clean Energy <b style="color:{ORG}">✦</b> <span style="color:#8fdc9a">Brighter Tomorrow</span></span>'
            f'<span class="pn">{n:02d}</span></div>')
    pages.append(f'<section class="page {cls}">{head}{t}<div class="body">{body}</div>{foot}</section>')

def tile(icon, big, small, color=NAVY):
    return (f'<div class="tile" style="border-color:{color}"><div class="ic" style="background:{color}">{icon}</div>'
            f'<div class="big" style="color:{color}">{big}</div><div class="small">{small}</div></div>')

# ---------- SVG chart helpers ----------
def bar_chart(vals, labels, w=700, h=300, color=NAVY, fmt=lambda v: f"{v:,.0f}", ymax=None, show_every=1, label_vals=True, colors=None):
    pl, pr, pt, pb_ = 60, 10, 20, 34
    ymax = ymax or max(vals) * 1.15
    cw = (w - pl - pr) / len(vals); s = []
    for k in range(5):
        y = pt + (h - pt - pb_) * k / 4; v = ymax * (1 - k / 4)
        s.append(f'<line x1="{pl}" y1="{y}" x2="{w-pr}" y2="{y}" stroke="#e1e6ec"/>'
                 f'<text x="{pl-6}" y="{y+4}" text-anchor="end" class="ax">{fmt(v)}</text>')
    for i, v in enumerate(vals):
        bh = (h - pt - pb_) * v / ymax; x = pl + i * cw + cw * 0.15
        c = colors[i] if colors else color
        s.append(f'<rect x="{x}" y="{h-pb_-bh}" width="{cw*0.7}" height="{bh}" rx="3" fill="{c}"/>')
        if label_vals: s.append(f'<text x="{x+cw*0.35}" y="{h-pb_-bh-5}" text-anchor="middle" class="vl">{fmt(v)}</text>')
        if i % show_every == 0 or i == len(vals) - 1:
            s.append(f'<text x="{x+cw*0.35}" y="{h-pb_+16}" text-anchor="middle" class="ax">{labels[i]}</text>')
    return f'<svg viewBox="0 0 {w} {h}" class="chart">{"".join(s)}</svg>'

# ---------- 1 cover ----------
pages.append(f'''<section class="page cover">
<div class="cv-top"><img src="{LOGO}" class="cv-logo"/><div><b>Nile Sun Power Limited</b><br/>Solar EPC · Kampala, Uganda</div></div>
<div class="cv-img" style="background-image:url({HOTEL})"></div>
<div class="cv-band">
  <div class="kicker">COMMERCIAL PROPOSAL</div>
  <div class="cv-title">Rooftop Solar PV System</div>
  <div class="cv-sub">Kampala Marriott Hotel · Mezzanine Roof</div>
  <div class="cv-chips"><span>185.4 kWp</span><span>299 × 620 Wp</span><span>2 × 80 kW inverters</span><span>Zero export</span></div>
</div>
<div class="cv-foot"><div><small>Prepared for</small><br/><b>Kampala Marriott Hotel</b><br/>Kampala, Uganda</div>
<div><small>Prepared by</small><br/><b>Nile Sun Power Limited</b><br/>Ref. Q-KMH-PV-2026-001 · 05 November 2026</div></div>
<div class="bar thick"><i style="background:{NAVY}"></i><i style="background:{ORG}"></i><i style="background:{GRN}"></i></div>
</section>''')

# ---------- 2 contents ----------
toc = ["Executive Summary", "About Nile Sun Power", "The Site", "Proposed System", "Energy Generation",
       "Solar Energy Profile", "Savings", "Return on Investment", "Financial Analysis", "Cash Flow",
       "Tariff Sensitivity", "What’s Included & Warranties", "Commercial Quotation", "Timeline & Contact"]
rows = "".join(f'<div class="toc-r"><span class="toc-n">{i+3:02d}</span><span class="toc-t">{t}</span><span class="toc-d"></span><span class="toc-p">{i+3}</span></div>' for i, t in enumerate(toc))
page(2, "Contents", f'<div class="toc">{rows}</div>')

# ---------- 3 executive summary ----------
page(3, "Executive Summary", f'''
<p class="lead">Nile Sun Power Limited proposes a <b>185.4 kWp grid-tied rooftop solar PV system</b> on the mezzanine roof of
Kampala Marriott Hotel. All solar energy is used on site (zero export, no battery), directly reducing the hotel's
daytime electricity purchases from the grid.</p>
<div class="grid3">
{tile("☀", "185.4 kWp", "solar capacity<br/>299 × 620 Wp panels")}
{tile("⚡", f"{gen1:,.0f}", "kWh generated<br/>in year 1", ORG)}
{tile("$", usd(y1), "savings in year 1", GRN)}
{tile("⟳", f"{pb:.1f} yrs", "simple payback")}
{tile("%", f"{irr*100:.1f} %", "project IRR", ORG)}
{tile("▲", usd(npv), "NPV at 10 %", GRN)}
</div>
<div class="callout"><b>Investment:</b> {usd(capex)} turnkey EPC (excl. VAT) &nbsp;·&nbsp; <b>25-year net savings:</b> {usd(net25)}
&nbsp;·&nbsp; <b>Cost of solar energy:</b> USD {lcoe:.3f}/kWh vs grid USD {tar:.3f}/kWh</div>
<ul class="ticks">
<li>Panels placed strictly within the architect's designated solar zone (drawing D18102-DD-A-104).</li>
<li>Ballasted aluminium structure at 10° tilt – no roof penetrations.</li>
<li>Zero-export control keeps all solar power inside the hotel.</li>
<li>Smart monitoring of generation and savings from day one.</li></ul>''')

# ---------- 4 about ----------
page(4, "About Nile Sun Power", f'''
<div class="about"><img src="{LOGO}"/><p class="lead">Nile Sun Power Limited is a solar energy company based in Kampala, Uganda,
delivering turnkey solar PV systems for commercial and industrial customers – from site assessment and engineering
through supply, installation, commissioning and after-sales support.</p></div>
<div class="grid3">
{tile("✎", "Engineering", "site survey, layout,<br/>electrical design")}
{tile("▦", "Supply", "Tier-1 panels, inverters<br/>& structures", ORG)}
{tile("⚒", "Installation", "certified team,<br/>safe rooftop works", GRN)}
{tile("✔", "Commissioning", "testing & grid<br/>synchronisation")}
{tile("◉", "Monitoring", "online performance<br/>tracking", ORG)}
{tile("☎", "Support", "warranty & after-<br/>sales service", GRN)}
</div>
<div class="callout"><b>Our promise:</b> a reliable, bankable solar system that lowers your energy costs and carbon footprint for 25+ years.</div>''')

# ---------- 5 site ----------
page(5, "The Site", f'''
<div class="grid4">
{tile("⌖", "Kampala", "Uganda<br/>0°18'11.34\"N, 32°35'13.76\"E")}
{tile("▤", "Mezzanine", "roof – architect's<br/>solar zone only", ORG)}
{tile("⚡", "≈ 1,000,000", "kWh per month<br/>hotel consumption")}
{tile("☀", "Equatorial", "sun gives stable<br/>output all year", GRN)}
</div>
<div class="imgbox"><img src="{OVERLAY}"/><div class="cap">Proposed PV array on the hotel's mezzanine roof (indicative visual)</div></div>''')

# ---------- 6 proposed system ----------
page(6, "Proposed System", f'''
<div class="grid4">
{tile("▦", "299", "solar panels ×<br/>620 W bifacial TOPCon", ORG)}
{tile("⇄", "2 × 80 kW", "string inverters")}
{tile("◢", "10° tilt", "ballasted aluminium<br/>(no roof penetration)", GRN)}
{tile("✕", "No battery", "zero-export control<br/>& smart monitoring")}
</div>
<div class="imgbox white"><img src="{BLOCK}"/><div class="cap">How the system connects – solar panels → inverters → AC combiner → main switchboard → hotel loads</div></div>
<table class="tbl"><tr><th>Item</th><th>Specification</th></tr>
<tr><td>DC capacity</td><td>185.4 kWp (299 × 620 Wp, 2382 × 1134 × 30 mm)</td></tr>
<tr><td>AC capacity</td><td>160 kW (2 × 80 kW, 1100 V, multi-MPPT)</td></tr>
<tr><td>Connection</td><td>AC combiner panel on roof → spare 250 A way on main LV switchboard</td></tr></table>''')

# ---------- 7 energy generation ----------
mk = [r["kwh"] for r in mon["rows"]]; ml = [r["m"] for r in mon["rows"]]
page(7, "Energy Generation", f'''
<div class="grid3">
{tile("⚡", f"{gen1:,.0f}", "kWh in year 1")}
{tile("≈", f"{gen1/365:,.0f}", "kWh per day (average)", ORG)}
{tile("★", "1,480", "kWh per kWp per year<br/>(specific yield)", GRN)}
</div>
<h3>Monthly generation – year 1 (kWh)</h3>
{bar_chart(mk, ml, colors=[ORG if v == max(mk) else NAVY for v in mk])}
<table class="tbl small"><tr><th>Month</th>{"".join(f"<th>{m}</th>" for m in ml)}</tr>
<tr><td>kWh</td>{"".join(f"<td>{v/1000:.1f}k</td>" for v in mk)}</tr>
<tr><td>GHI</td>{"".join(f"<td>{r['ghi']}</td>" for r in mon["rows"])}</tr></table>
<p class="note">GHI = global horizontal irradiation, kWh/m²/day (typical Kampala values). Output degrades about 0.4 % per year;
25-year total ≈ {sum(fin["gen"])/1e6:.2f} GWh.</p>''')

# ---------- 8 solar energy profile ----------
ph = tou["pv_h"]
bands = tou["bands"]; share = gen1 / 12_000_000
hcol = [NAVY if (h < 6 or h >= 18) else ORG for h in range(24)]
page(8, "Solar Energy Profile", f'''
<p class="lead">Solar power is produced during daytime hours, exactly when the hotel's air-conditioning, kitchens and
laundry load is high. Almost all solar energy falls in the <b>shoulder period (06:00–18:00)</b>.</p>
<h3>Average daily solar output by hour (kW)</h3>
{bar_chart(ph, [f"{h:02d}" for h in range(24)], h=270, fmt=lambda v: f"{v:.0f}", show_every=2, label_vals=False, colors=hcol)}
<table class="tbl"><tr><th>TOU band</th><th>Hours</th><th>Solar energy (kWh/yr)</th><th>Share of solar</th></tr>
{"".join(f"<tr><td>{b['band']}</td><td>{b['hours']}</td><td>{b['pv']:,.0f}</td><td>{b['pv_share']*100:.1f} %</td></tr>" for b in bands)}
</table>
<div class="grid3">
{tile("☀", f"{bands[1]['pv_share']*100:.1f} %", "of solar energy used<br/>in the shoulder band", ORG)}
{tile("▣", f"{share*100:.1f} %", "of the hotel's annual<br/>consumption covered")}
{tile("⇤", "0 kWh", "exported to the grid<br/>(zero-export control)", GRN)}
</div>''')

# ---------- 9 savings ----------
page(9, "Savings", f'''
<div class="grid3">
{tile("1", usd(savings[0]), f"year-1 savings<br/>at USD {tar:.3f}/kWh")}
{tile("25", usd(savings[-1]), "year-25 savings<br/>tariff rising +2 %/yr", ORG)}
{tile("Σ", usd(sav25), "total savings<br/>over 25 years", GRN)}
</div>
<h3>Annual electricity savings (USD)</h3>
{bar_chart(savings, [str(i+1) for i in range(25)], h=420, fmt=lambda v: f"{v/1000:.0f}k", show_every=2, label_vals=False, colors=[GRN if i in (0, 24) else NAVY for i in range(25)])}
<p class="note">Savings = solar energy used on site × grid tariff (USD {tar:.5f}/kWh in year 1, escalating 2 % per year),
after 0.4 %/yr module degradation. No O&amp;M cost assumed; one inverter replacement (USD 9,600) in year 12.</p>''')

# ---------- 10 ROI ----------
page(10, "Return on Investment", f'''
<div class="roi"><div><div class="roi-big">{roi*100:.0f}%</div><div class="roi-s">ROI over 25 years</div>
<div class="roi-x">{net25/capex:.1f}× return</div><p class="note">Every USD 1 invested returns about USD {net25/capex:.1f} in savings over the system life.</p></div></div>
<div class="grid3">
{tile("1", f"{y1/capex*100:.1f} %", "year-1 return")}
{tile("⟳", f"{pb:.1f} years", "simple payback", ORG)}
{tile("%", f"{irr*100:.1f} %", "IRR (25 years)", GRN)}
</div>
<table class="tbl"><tr><th>Metric</th><th>Value</th></tr>
<tr><td>Total project investment</td><td>{usd(capex)}</td></tr>
<tr><td>Net savings over 25 years (after inverter replacement)</td><td>{usd(net25)}</td></tr>
<tr><td>Net gain after recovering the investment</td><td>{usd(net25-capex)}</td></tr>
<tr><td>Return on investment (net gain ÷ investment)</td><td>{roi*100:.0f} %</td></tr></table>''')

# ---------- 11 financial analysis ----------
page(11, "Financial Analysis", f'''
<div class="grid3">
{tile("$", usd(capex), "investment (excl. VAT)")}
{tile("▲", usd(npv), "NPV at 10 % discount", GRN)}
{tile("⚖", f"USD {lcoe:.3f}", f"per kWh solar cost<br/>vs USD {tar:.3f} grid", ORG)}
</div>
<table class="tbl"><tr><th>Parameter</th><th>Value</th></tr>
<tr><td>System size</td><td>185.4 kWp DC / 160 kW AC</td></tr>
<tr><td>Year-1 generation</td><td>{gen1:,.0f} kWh</td></tr>
<tr><td>Grid tariff (year 1) / escalation</td><td>USD {tar:.5f}/kWh / 2 % per year</td></tr>
<tr><td>Module degradation</td><td>≈ 0.4 % per year</td></tr>
<tr><td>Year-1 savings</td><td>{usd(y1)}</td></tr>
<tr><td>Simple payback</td><td>{pb:.1f} years</td></tr>
<tr><td>IRR (25 years)</td><td>{irr*100:.1f} %</td></tr>
<tr><td>NPV (10 % discount rate)</td><td>{usd(npv)}</td></tr>
<tr><td>Levelised cost of energy (LCOE)</td><td>USD {lcoe:.3f}/kWh</td></tr>
<tr><td>O&amp;M cost</td><td>Not included (none assumed)</td></tr>
<tr><td>Inverter replacement</td><td>USD 9,600 in year 12 (included)</td></tr>
<tr><td>25-year gross savings / net savings</td><td>{usd(sav25)} / {usd(net25)}</td></tr></table>''')

# ---------- 12 cash flow ----------
cum = fin["cum"]
W, H, pl, pt, pbm, pr = 700, 400, 70, 20, 36, 10
lo, hi = -150000, 500000
X = lambda i: pl + (W - pl - pr) * i / 25
Y = lambda v: pt + (H - pt - pbm) * (hi - v) / (hi - lo)
s = []
for v in range(-100000, 500001, 100000):
    s.append(f'<line x1="{pl}" y1="{Y(v)}" x2="{W-pr}" y2="{Y(v)}" stroke="{"#9aa4ae" if v == 0 else "#e1e6ec"}"/>'
             f'<text x="{pl-6}" y="{Y(v)+4}" text-anchor="end" class="ax">{v/1000:,.0f}k</text>')
for i, v in enumerate(cum):
    bw = (W - pl - pr) / 26 * 0.7
    y0, y1_ = (Y(v), Y(0)) if v >= 0 else (Y(0), Y(v))
    s.append(f'<rect x="{X(i)-bw/2+8}" y="{y0}" width="{bw}" height="{y1_-y0}" rx="2" fill="{GRN if v >= 0 else "#c0392b"}" opacity=".85"/>')
    if i % 5 == 0 or i == 7: s.append(f'<text x="{X(i)+8}" y="{H-pbm+16}" text-anchor="middle" class="ax">{i}</text>')
for i in (0, 7, 15, 25):
    v = cum[i]; s.append(f'<text x="{X(i)+8}" y="{Y(v)+(14 if v < 0 else -6)}" text-anchor="middle" class="vl">{v:+,.0f}</text>')
cf_svg = f'<svg viewBox="0 0 {W} {H}" class="chart">{"".join(s)}</svg>'
page(12, "Cash Flow", f'''
<p class="lead">Cumulative cash flow over the 25-year project life (USD). The investment is fully recovered during year 7.</p>
{cf_svg}
<div class="grid3">
{tile("⟳", f"{pb:.1f} yrs", "payback – positive<br/>from year 7", ORG)}
{tile("▲", f"+{cum[25]:,.0f}", "cumulative cash<br/>at year 25 (USD)", GRN)}
{tile("25", "25 yrs", "project life")}
</div>
<table class="tbl small"><tr><th>Year</th>{"".join(f"<th>{i}</th>" for i in (0,1,3,5,6,7,10,12,15,20,25))}</tr>
<tr><td>Annual</td>{"".join(f"<td>{fin['cf'][i]/1000:+,.1f}k</td>" for i in (0,1,3,5,6,7,10,12,15,20,25))}</tr>
<tr><td>Cumulative</td>{"".join(f"<td>{cum[i]/1000:+,.1f}k</td>" for i in (0,1,3,5,6,7,10,12,15,20,25))}</tr></table>
<p class="note">Year 12 includes the inverter replacement (USD 9,600).</p>''')

# ---------- 13 tariff sensitivity ----------
sens = fin["sens"]
srows = "".join(f'<tr class="{"hl" if abs(t-0.07)<1e-9 else ""}"><td>USD {t:.2f}</td><td>{usd(s1)}</td><td>{p:.1f}</td><td>{i*100:.1f} %</td><td>{usd(n)}</td></tr>' for t, s1, p, i, n in sens)
page(13, "Tariff Sensitivity", f'''
<p class="lead">The higher the grid tariff, the better the returns. Even at USD 0.05/kWh the project still pays back and earns a positive NPV.</p>
<table class="tbl"><tr><th>Tariff (/kWh)</th><th>Year-1 savings</th><th>Payback (yrs)</th><th>IRR</th><th>NPV @10 %</th></tr>{srows}</table>
<div class="two">
<div><h3>Payback (years)</h3>{bar_chart([x[2] for x in sens], [f"{x[0]:.2f}" for x in sens], w=340, h=240, color=ORG, fmt=lambda v: f"{v:.1f}")}</div>
<div><h3>IRR (%)</h3>{bar_chart([x[3]*100 for x in sens], [f"{x[0]:.2f}" for x in sens], w=340, h=240, color=GRN, fmt=lambda v: f"{v:.1f}")}</div></div>
<div class="callout">Break-even tariff ≈ <b>USD {fin["breakeven"]:.4f}/kWh</b> – below this tariff the NPV at 10 % would turn negative.
Current tariff: USD {tar:.3f}/kWh.</div>''')

# ---------- 14 included & warranties ----------
inc = [("✎", "Engineering & design"), ("▦", "299 solar panels"), ("⇄", "2 inverters"), ("◢", "Mounting structure"),
       ("〰", "DC & AC cabling"), ("◉", "Monitoring & zero-export control"), ("⏚", "Earthing & lightning protection"),
       ("⚒", "Installation & commissioning"), ("⛟", "Transport & customs clearing")]
page(14, "What’s Included & Warranties", f'''
<div class="pill">WHAT’S INCLUDED</div>
<div class="grid3 inc">{"".join(f'<div class="incl"><span>{a}</span>{b}</div>' for a, b in inc)}</div>
<div class="pill" style="background:{GRN}">WARRANTIES</div>
<div class="grid4">
{tile("▦", "12 / 30 yrs", "panels – product /<br/>linear power", ORG)}
{tile("⇄", "5 yrs", "inverters<br/>(extendable)")}
{tile("◢", "10 yrs", "mounting<br/>structure", GRN)}
{tile("⚒", "2 yrs", "workmanship from<br/>commissioning")}
</div>
<div class="callout"><b>Excluded:</b> roof strengthening or waterproofing, battery storage, utility/permit fees, VAT and statutory levies,
and works not listed above.</div>''')

# ---------- 15 quotation ----------
items = [("PV modules – 620 Wp bifacial N-type TOPCon (Tier-1)", "299 nos"), ("String inverters – 80 kW, 1100 V, multi-MPPT", "2 nos"),
         ("Ballasted aluminium mounting structure, 10° tilt", "1 lot"), ("DC system – PV cable, connectors, string isolators, cable tray", "1 lot"),
         ("AC system – AC combiner panel, MCCBs, cabling to main LV switchboard", "1 lot"), ("Smart data logger, remote monitoring & zero-export control", "1 set"),
         ("Earthing & lightning protection integration", "1 lot"), ("Installation, testing & commissioning", "1 lot"),
         ("Transport, logistics & customs clearing to site", "1 lot")]
qrows = "".join(f"<tr><td>{i}</td><td>{d}</td><td>{q}</td></tr>" for i, (d, q) in enumerate(items, 1))
page(15, "Commercial Quotation", f'''
<table class="tbl meta"><tr><td><b>Quotation No.</b> Q-KMH-PV-2026-001</td><td><b>Date</b> 05-11-2026</td><td><b>Valid</b> 30 days (05-12-2026)</td></tr>
<tr><td><b>Client</b> Kampala Marriott Hotel</td><td colspan="2"><b>Supplier</b> Nile Sun Power Limited, Kampala, Uganda</td></tr></table>
<table class="tbl"><tr><th>#</th><th>Scope of supply &amp; works (turnkey EPC)</th><th>Qty</th></tr>{qrows}
<tr class="total"><td colspan="2">TOTAL TURNKEY EPC PRICE (excluding VAT)</td><td>{usd(capex)}</td></tr></table>
<p class="note">Equivalent to USD {capex/185400:.2f} per Wp · One hundred twenty-one thousand one hundred fifteen US Dollars only.</p>
<table class="tbl"><tr><th colspan="2">Commercial terms</th></tr>
<tr><td>Payment</td><td>30 % advance with PO · 60 % on delivery of main equipment · 10 % on commissioning</td></tr>
<tr><td>Delivery</td><td>Equipment 8–10 weeks from PO; installation &amp; commissioning ≈ 4 weeks (≈ 12–14 weeks total)</td></tr>
<tr><td>Taxes</td><td>VAT, withholding tax and statutory levies excluded – charged as applicable</td></tr>
<tr><td>Client scope</td><td>Roof access, spare 250 A way on the main LV switchboard, power &amp; water during installation</td></tr></table>
<div class="sign"><div>For Nile Sun Power Limited<br/><br/>____________________________<br/><small>Signature / Name / Date</small></div>
<div>Accepted by Kampala Marriott Hotel<br/><br/>____________________________<br/><small>Signature / Name / Date</small></div></div>''')

# ---------- 16 timeline & contact ----------
steps = [("1", "Design", "weeks 1–3", 0, 3), ("2", "Procurement", "weeks 2–10", 1, 10), ("3", "Installation", "weeks 10–13", 9, 13), ("4", "Commissioning", "weeks 13–14", 12, 14)]
cols = [NAVY, ORG, GRN, NAVY]
gantt = "".join(f'<div class="g-r"><div class="g-l"><span class="g-n" style="background:{cols[k]}">{n}</span>{t}<small>{w}</small></div>'
                f'<div class="g-t"><div class="g-b" style="left:{a/14*100}%;width:{(b-a)/14*100}%;background:{cols[k]}"></div></div></div>'
                for k, (n, t, w, a, b) in enumerate(steps))
page(16, "Timeline & Contact", f'''
<h3>Project timeline (≈ 14 weeks from purchase order)</h3>
<div class="gantt">{gantt}<div class="g-r"><div class="g-l"></div><div class="g-t axis">{"".join(f"<span>{i}</span>" for i in range(0, 15, 2))}</div></div></div>
<div class="thanks"><img src="{LOGO}"/><div><div class="ty">Thank you</div>
<p>We appreciate the opportunity to support Kampala Marriott Hotel with a clean, reliable and sustainable energy future.</p></div></div>
<div class="contact"><div><small>Company</small><b>Nile Sun Power Limited</b>Kampala, Uganda</div>
<div><small>Contact</small><b>Mahil Fernando</b>+94 773 55 96 82<br/>mahil@windforce.lk</div></div>''')

CSS = f"""
@page {{ size: A4; margin: 0 }}
* {{ box-sizing: border-box }}
body {{ margin:0; font-family: 'Inter','Segoe UI',Arial,sans-serif; color:{INK}; -webkit-print-color-adjust:exact; print-color-adjust:exact }}
.page {{ width:210mm; height:297mm; position:relative; overflow:hidden; page-break-after:always; padding:12mm 13mm 0; background:#fff }}
.hdr {{ display:flex; justify-content:space-between; align-items:center; font-size:8.5pt; font-weight:700; color:{NAVY}; text-transform:uppercase; letter-spacing:.3px }}
.brand {{ display:flex; align-items:center; gap:6px }} .brand img {{ height:22px }}
.bar {{ display:flex; height:4px; margin:5px 0 0 }} .bar i {{ flex:1 }} .bar.thick {{ height:10px; position:absolute; bottom:0; left:0; right:0; margin:0 }}
h1 {{ font-size:34pt; color:{NAVY}; margin:9mm 0 2mm; letter-spacing:-.5px; line-height:1.05 }}
.uline {{ width:60px; height:5px; background:{ORG}; border-radius:3px; margin-bottom:6mm }}
h3 {{ color:{NAVY}; font-size:12pt; margin:5mm 0 2mm }}
.lead {{ font-size:11pt; line-height:1.5; margin:0 0 5mm }}
.note {{ font-size:8.5pt; color:{MUT}; line-height:1.4 }}
.ftr {{ position:absolute; bottom:0; left:0; right:0; height:14mm; background:{NAVY}; color:#fff; display:flex; justify-content:center; align-items:center; font-size:10pt; font-weight:600 }}
.ftr .pn {{ position:absolute; right:13mm; background:#fff; color:{NAVY}; border-radius:6px; padding:3px 9px; font-weight:800 }}
.grid3,.grid4 {{ display:grid; gap:4mm; margin:3mm 0 5mm }} .grid3 {{ grid-template-columns:repeat(3,1fr) }} .grid4 {{ grid-template-columns:repeat(4,1fr) }}
.tile {{ border:1.6px solid; border-radius:10px; padding:4mm 3mm; text-align:center; background:{BG} }}
.tile .ic {{ width:34px; height:34px; border-radius:50%; color:#fff; margin:0 auto 2mm; display:flex; align-items:center; justify-content:center; font-size:15pt; font-weight:800 }}
.tile .big {{ font-size:15pt; font-weight:800; line-height:1.15 }} .tile .small {{ font-size:8.5pt; color:{MUT}; margin-top:1mm; line-height:1.3 }}
.grid4 .tile .big {{ font-size:13pt }}
.callout {{ background:#fff6e8; border-left:5px solid {ORG}; padding:3.5mm 4mm; font-size:10pt; border-radius:6px; margin:4mm 0; line-height:1.45 }}
ul.ticks {{ padding:0; list-style:none; font-size:10.5pt; line-height:1.6 }} ul.ticks li:before {{ content:'✔'; color:{GRN}; font-weight:800; margin-right:8px }}
.tbl {{ width:100%; border-collapse:collapse; font-size:9.5pt; margin:3mm 0 }}
.tbl th {{ background:{NAVY}; color:#fff; text-align:left; padding:2.2mm 2.5mm }} .tbl td {{ padding:2mm 2.5mm; border-bottom:1px solid #e1e6ec }}
.tbl tr:nth-child(even) td {{ background:{BG} }} .tbl.small {{ font-size:7.8pt }} .tbl.small th,.tbl.small td {{ padding:1.5mm 1mm; text-align:center }}
.tbl tr.hl td {{ background:#fff1d9; font-weight:700 }} .tbl tr.total td {{ background:{NAVY}; color:#fff; font-weight:800; font-size:11pt }}
.tbl.meta td {{ background:{BG}; font-size:9pt }}
.chart {{ width:100%; height:auto; display:block }} .ax {{ font-size:10px; fill:{MUT} }} .vl {{ font-size:10px; font-weight:700; fill:{INK} }}
.imgbox {{ border-radius:12px; overflow:hidden; border:1.5px solid #d5dce4 }} .imgbox img {{ width:100%; display:block }}
.imgbox.white img {{ padding:2mm }} .cap {{ font-size:8.5pt; color:{MUT}; padding:2mm 3mm; background:{BG} }}
.two {{ display:grid; grid-template-columns:1fr 1fr; gap:6mm }}
.cover {{ padding:0 }} .cv-top {{ display:flex; gap:4mm; align-items:center; padding:10mm 13mm 6mm; color:{NAVY}; font-size:10pt }} .cv-logo {{ height:22mm }}
.cv-img {{ height:120mm; background-size:cover; background-position:center }}
.cv-band {{ background:{NAVY}; color:#fff; padding:9mm 13mm 10mm }}
.kicker {{ color:{ORG}; font-weight:800; letter-spacing:3px; font-size:10pt }}
.cv-title {{ font-size:36pt; font-weight:800; line-height:1.05; margin:2mm 0 }} .cv-sub {{ font-size:15pt; opacity:.9 }}
.cv-chips {{ margin-top:6mm; display:flex; gap:3mm; flex-wrap:wrap }} .cv-chips span {{ background:{ORG}; padding:2mm 4mm; border-radius:20px; font-weight:700; font-size:10pt }}
.cv-chips span:nth-child(even) {{ background:{GRN} }}
.cv-foot {{ display:grid; grid-template-columns:1fr 1fr; gap:8mm; padding:9mm 13mm; font-size:10.5pt; line-height:1.5 }} .cv-foot small {{ color:{MUT}; text-transform:uppercase; letter-spacing:1px }}
.toc {{ margin-top:4mm }} .toc-r {{ display:flex; align-items:baseline; gap:4mm; padding:2.9mm 0; border-bottom:1px solid #e8ecf1; font-size:12.5pt }}
.toc-n {{ background:{NAVY}; color:#fff; border-radius:6px; padding:1mm 2.5mm; font-weight:800; font-size:10pt }} .toc-r:nth-child(3n+2) .toc-n {{ background:{ORG} }} .toc-r:nth-child(3n) .toc-n {{ background:{GRN} }}
.toc-t {{ font-weight:600 }} .toc-d {{ flex:1; border-bottom:2px dotted #c4ccd6 }} .toc-p {{ color:{NAVY}; font-weight:800 }}
.about {{ display:flex; gap:6mm; align-items:center }} .about img {{ height:38mm }}
.roi {{ background:{BG}; border-radius:14px; padding:6mm 8mm; margin-bottom:4mm; border:1.5px solid #dbe2ea }}
.roi-big {{ font-size:78pt; font-weight:900; color:{NAVY}; line-height:1 }} .roi-s {{ font-size:22pt; font-weight:800; color:{NAVY} }}
.roi-x {{ font-size:30pt; font-weight:900; color:{GRN}; margin-top:3mm; border-top:2px solid #c9d2dc; padding-top:3mm }}
.pill {{ display:inline-block; background:{NAVY}; color:#fff; font-weight:800; padding:2mm 5mm; border-radius:6px; font-size:10pt; letter-spacing:1px }}
.incl {{ display:flex; align-items:center; gap:3mm; border:1.4px solid #d5dce4; border-radius:10px; padding:3.5mm; font-weight:700; color:{NAVY}; font-size:10pt; background:{BG} }}
.incl span {{ width:30px; height:30px; flex:none; border-radius:50%; background:{ORG}; color:#fff; display:flex; align-items:center; justify-content:center; font-size:13pt }}
.sign {{ display:grid; grid-template-columns:1fr 1fr; gap:10mm; font-size:10pt; font-weight:700; margin-top:5mm }} .sign small {{ font-weight:400; color:{MUT} }}
.gantt {{ margin:2mm 0 8mm }} .g-r {{ display:flex; align-items:center; margin:2.5mm 0 }}
.g-l {{ width:72mm; display:flex; align-items:center; gap:3mm; font-weight:700; font-size:11pt }} .g-l small {{ color:{MUT}; font-weight:400; margin-left:auto; margin-right:4mm }}
.g-n {{ width:26px; height:26px; border-radius:50%; color:#fff; display:flex; align-items:center; justify-content:center }}
.g-t {{ flex:1; position:relative; height:9mm; background:{BG}; border-radius:5px }} .g-b {{ position:absolute; top:1.5mm; bottom:1.5mm; border-radius:4px }}
.g-t.axis {{ background:none; display:flex; justify-content:space-between; font-size:8.5pt; color:{MUT}; height:auto }}
.thanks {{ display:flex; gap:6mm; align-items:center; background:{NAVY}; color:#fff; border-radius:14px; padding:7mm }}
.thanks img {{ height:30mm; background:#fff; border-radius:10px; padding:2mm }} .ty {{ font-size:30pt; font-weight:900; color:{ORG} }} .thanks p {{ font-size:11.5pt; line-height:1.5; margin:2mm 0 0 }}
.contact {{ display:grid; grid-template-columns:1fr 1fr; gap:5mm; margin-top:6mm }}
.contact div {{ border:1.5px solid #d5dce4; border-radius:10px; padding:5mm; font-size:11pt; line-height:1.6; background:{BG} }}
.contact small {{ display:block; color:{MUT}; text-transform:uppercase; letter-spacing:1px; font-size:8pt }} .contact b {{ display:block; color:{NAVY}; font-size:13pt }}
"""
html = f"<!doctype html><html><head><meta charset='utf-8'><title>Kampala Marriott Solar PV Proposal</title><style>{CSS}</style></head><body>{''.join(pages)}</body></html>"
open(os.path.join(HERE, "Kampala_Marriott_PV_Graphic_Proposal.html"), "w").write(html)
print("pages", len(pages))
