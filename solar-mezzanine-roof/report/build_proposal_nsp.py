"""Marriott proposal in the NileSun 'Option A' house style (cover + numbered sections + one-page quotation + annexes).
Run: python3 build_proposal_nsp.py && node proposal_nsp_pdf.js  -> Kampala_Marriott_PV_Proposal_NSP.pdf
"""
import os, json, base64

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
fin = json.load(open(os.path.join(HERE, "proposal_fin_v6.json")))   # PVsyst P50 + UEDCL bill Oct 2026 tariffs
mon = json.load(open(os.path.join(HERE, "monthly.json")))
tou = json.load(open(os.path.join(HERE, "tou.json")))

NAVY, GRN, ORG, ORG2, INK, MUT, CARD, LINE = "#1f3f8f", "#3c9a46", "#f4a522", "#f6c560", "#222", "#6b7480", "#eef2f8", "#cfd6e0"
REF, DATE, VALID = "NSP-261105-KMH", "05-Nov-2026", "05-Dec-2026"
TITLE = "185.4 kWp Grid-Tied Rooftop Solar PV System"
FOOT = "185.4 kWp Rooftop Solar PV – Kampala Marriott Hotel  |  NileSun Power Ltd"

def b64(p):
    ext = p.rsplit(".", 1)[1].lower().replace("jpg", "jpeg")
    return f"data:image/{ext};base64," + base64.b64encode(open(p, "rb").read()).decode()
LOGO = b64(os.path.join(HERE, "nilesun_logo.png"))
HOTEL = b64(os.path.join(HERE, "hotel.jpg"))
SITE = b64(os.path.join(ROOT, "visual", "Marriott_roof_PV_overlay_zoom.png"))
PLAN = b64(os.path.join(HERE, "layout_plan_crop.png"))
LAYOUT = b64(os.path.join(HERE, "layout_revB.png"))
SLD = b64(os.path.join(ROOT, "sld", "PV_SLD_Engineering.png"))

usd = lambda v, d=0: f"USD {v:,.{d}f}"
capex, y1, npv, irr, pb, lcoe, tar = fin["capex"], fin["cf"][1], fin["npv"], fin["irr"], fin["pb"], fin["lcoe"], fin["tar"]
net25, sav25, gen1, cum = fin["net25"], fin["sav25"], fin["gen"][0], fin["cum"]
TOTAL_PAGES = 9
pages = []

def stripes(cls="stripe"):
    return f'<div class="{cls}"><i style="background:{NAVY}"></i><i style="background:{GRN}"></i><i style="background:{ORG}"></i></div>'

def page(n, label, body):
    pages.append(f'''<section class="page">
<div class="hdr"><img src="{LOGO}"/><div class="co"><b>NILESUN POWER LTD</b><span>Solar Power Systems | Design | Installation | Maintenance</span>
<span>Tel: +256 708669574 &nbsp;|&nbsp; Email: sales@nilesunpower.com</span></div>
<div class="ref"><b>{label}</b><span>Ref: {REF}</span><span>Date: {DATE}</span></div></div>{stripes()}
<div class="content">{body}</div>
<div class="ftr"><span>{FOOT}</span><span>Page {n} of {TOTAL_PAGES}</span></div></section>''')

H = lambda t: f'<h2><i></i>{t}</h2>'
def tbl(rows, head=True, cls="", widths=None):
    cg = "".join(f'<col style="width:{w}%"/>' for w in widths) if widths else ""
    out = []
    for i, r in enumerate(rows):
        tag = "th" if head and i == 0 else "td"
        out.append("<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in r) + "</tr>")
    return f'<table class="t {cls}"><colgroup>{cg}</colgroup>{"".join(out)}</table>'
def cards(items):
    cols = [ORG, "#2f5fc4", GRN, NAVY]
    return '<div class="cards">' + "".join(
        f'<div class="card" style="border-top-color:{cols[i % 4]}"><b>{v}</b><span>{l}</span></div>' for i, (v, l) in enumerate(items)) + "</div>"

def bars(vals, labels, w=680, h=250, fmt=lambda v: f"{v:,.0f}", ylab="", colors=None, ymax=None, neg=False):
    pl, pr, pt, pb_ = 52, 8, 16, 26
    lo = min(0, min(vals)) if neg else 0
    hi = ymax or max(vals) * 1.18
    if neg: lo = lo * 1.25
    Y = lambda v: pt + (h - pt - pb_) * (hi - v) / (hi - lo)
    cw = (w - pl - pr) / len(vals); s = []
    for k in range(6):
        v = lo + (hi - lo) * k / 5
        s.append(f'<line x1="{pl}" y1="{Y(v):.1f}" x2="{w-pr}" y2="{Y(v):.1f}" stroke="#e3e7ed"/><text x="{pl-6}" y="{Y(v)+3:.1f}" class="ax" text-anchor="end">{fmt(v)}</text>')
    if neg: s.append(f'<line x1="{pl}" y1="{Y(0):.1f}" x2="{w-pr}" y2="{Y(0):.1f}" stroke="#8a929c"/>')
    for i, v in enumerate(vals):
        x = pl + i * cw + cw * .14; y0, y1_ = sorted((Y(v), Y(0)))
        c = colors[i] if colors else (ORG if i % 2 == 0 else ORG2)
        s.append(f'<rect x="{x:.1f}" y="{y0:.1f}" width="{cw*.72:.1f}" height="{y1_-y0:.1f}" fill="{c}"/>')
        if labels[i] is not None:
            s.append(f'<text x="{x+cw*.36:.1f}" y="{h-pb_+15}" class="ax" text-anchor="middle">{labels[i]}</text>')
    if ylab: s.append(f'<text transform="translate(12,{(h-pb_)/2+20}) rotate(-90)" class="ax" text-anchor="middle">{ylab}</text>')
    return s, Y, pl, cw

# ---------------- cover ----------------
pages.append(f'''<section class="page cover">{stripes("stripe big")}
<div class="cv-logo"><img src="{LOGO}"/></div>
<div class="cv-photo" style="background-image:url({HOTEL})"></div>
<div class="cv-kicker">TECHNICAL &amp; COMMERCIAL PROPOSAL</div>
<div class="cv-title">185.4 kWp Rooftop<br/>Solar PV System</div>
<div class="cv-sub">299 × 620 Wp solar panels &nbsp;|&nbsp; 2 × 80 kW grid-tied inverters</div>
<div class="cv-box"><div><span>PREPARED FOR</span><b>Kampala Marriott Hotel</b><p>Mezzanine roof, Kampala, Uganda</p></div>
<div><span>PREPARED BY</span><b>NileSun Power Ltd</b><p>Contact: Mahil Fernando<br/>Tel: +256 708669574 &nbsp;|&nbsp; +94 773 55 96 82<br/>Email: sales@nilesunpower.com<br/>Ref: {REF} &nbsp;|&nbsp; {DATE}</p></div></div>
<div class="cv-valid">Valid until {VALID} &nbsp;|&nbsp; Clean Energy - Brighter Tomorrow</div>
{stripes("stripe big bottom")}</section>''')

# ---------------- page 2: summary ----------------
page(2, "TECHNICAL &amp; COMMERCIAL PROPOSAL", f'''
<h1>{TITLE}</h1>
{H("Quote &amp; Client Details")}
{tbl([["Quote No.", REF, "Date", DATE, "Valid Until", VALID],
      ["Client Name", "Kampala Marriott Hotel", "Contact No.", "Mr. Jagath<br/>+256 791 811805", "Client Email", ""],
      ["Site Address", "Kampala Marriott Hotel, mezzanine roof, Kampala", "Supply Type", "Three-phase 400 V, UEDCL, main LV switchboard", "VAT TIN No.", ""]],
     head=False, cls="kv6", widths=[12, 22, 11, 22, 11, 22])}
{cards([("185.4 kWp", "Solar array capacity"), ("160 kW", "Inverters (2 × 80 kW)"), ("299 nos", "620 Wp solar panels"), (usd(capex), "Turnkey price excl. VAT"),
        (f"{gen1/365:,.0f} kWh", "Avg. daily generation"), (f"{gen1/1000:,.1f} MWh", "Est. annual generation"), (usd(y1), "Savings in year 1"), (f"{pb:.1f} years", "Payback period")])}
{H("1. Executive Summary")}
<p>NileSun Power Ltd is pleased to submit this proposal for the design, supply, installation and commissioning of a
<b>185.4 kWp grid-tied rooftop solar PV system</b> on the mezzanine roof of the <b>Kampala Marriott Hotel</b>:
<b>299 × 620 W N-type bifacial solar panels</b> on a ballasted aluminium structure at 10° tilt, with
<b>two 80 kW three-phase string inverters</b> connected to the hotel's main LV switchboard.</p>
<p>The array generates about <b>{gen1:,.0f} kWh per year</b> (approx. {gen1/365:,.0f} kWh/day). The hotel used 981,901 kWh
in October 2026 (UEDCL bill), so every solar kWh is used on site and directly reduces grid purchases. At the UEDCL shoulder
tariff of UGX 357/kWh (≈ USD {tar+1e-9:.4f}/kWh at UGX 4,100/USD) this saves about
<b>{usd(y1)} in the first year</b>. The turnkey price is <b>{usd(capex)}</b> (excl. VAT), paid back in about <b>{pb:.1f} years</b>, with an IRR of
<b>{irr*100:.1f} %</b> (Sections 12 and 14).</p>
{H("Key Benefits")}
<ul class="dots"><li>Lower bills: solar energy covers part of the hotel's daytime load at USD {lcoe:.3f}/kWh versus USD {tar:.3f}/kWh from the grid.</li>
<li>Fast payback ({pb:.1f} years) and {usd(sav25)} savings over 25 years.</li>
<li>Long life: Astronergy N-type bifacial panels (15-year product, 30-year power warranty); remote monitoring of generation and savings.</li></ul>''')

# ---------------- page 3: equipment, array, generation ----------------
mk = fin["pvsyst_monthly"]   # PVsyst E_Grid, P50
s, Y, pl, cw = bars(mk, [r["m"] for r in mon["rows"]], h=108, ymax=30000, ylab="kWh / month")
for i, v in enumerate(mk):
    s.append(f'<text x="{pl+i*cw+cw*.5:.1f}" y="{Y(v)-5:.1f}" class="vl" text-anchor="middle">{v/1000:.1f}k</text>')
genchart = f'<svg viewBox="0 0 680 108" class="chart">{"".join(s)}</svg>'
page(3, "SYSTEM DESIGN", f'''
{H("2. Equipment Schedule (Bill of Materials)")}
{tbl([["#", "Item", "Specification", "Qty", "UoM"],
      ["1", "Solar panels", "Astronergy ASTRO N7 CHSM66RN(DG)/F-BH 620 Wp N-type TOPCon bifacial, 2382 × 1134 × 30 mm (Annex 4)", "299", "pcs"],
      ["2", "String inverters", "Sigenergy Sigen PV 80M1, 80 kW three-phase, 1100 V DC, with monitoring (Annex 3)", "2", "pcs"],
      ["3", "Mounting structure", "Enerack ballasted aluminium system, 10° tilt, 6 × 2P + 1 × 1P tables, no roof penetration (Annex 5)", "1", "system"],
      ["4", "DC protection", "DC isolator units (2-pole 1000 V 32 A) + DC SPD Type II – 1 each per string", "16+16", "pcs"],
      ["5", "AC combiner panel", "MCCBs 2 × 160 A (inverter incomers), 400 A roof isolator, AC SPD Type II", "1", "set"],
      ["6", "Grid connection", "Connection to the existing Masterpact NW10 H1 solar incomer on the main LV switchboard", "1", "set"],
      ["7", "Cabling", "Solar cable 4 mm², AC 4C × 50 mm² and 4C × 240 mm² Cu XLPE/SWA, cable tray", "1", "lot"],
      ["8", "Monitoring & control", "Smart data logger, energy meter, remote monitoring", "1", "set"],
      ["9", "Earthing", "Array bonding, connection to building earth and lightning protection", "1", "set"]],
     widths=[4, 18, 62, 7, 9])}
{H("3. Solar Array &amp; Inverters")}
<div class="two">{tbl([["Solar array", "Value"], ["Panels", "299 × 620 W = 185.4 kWp"], ["Arrangement", "7 tables: 6 × 2P×23, 1 × 1P×23 (portrait)"],
                       ["DC / AC ratio", "185.4 kWp / 160 kW = 1.16"], ["Location / tilt", "Flat concrete mezzanine roof, 10°"], ["Panel area", "approx. 808 m² (299 panels)"]], widths=[42, 58])}
{tbl([["Inverters", "Value"], ["INV-01", "152 panels = 94.2 kWp, 8 strings × 19"], ["INV-02", "147 panels = 91.1 kWp, 3 × 19 + 5 × 18"],
      ["AC output", "2 × 80 kW, 400 V 3N~"], ["Connection", "AC combiner → MLVS via riser"]], widths=[38, 62])}</div>
{H("4. Estimated Energy Generation")}
<p class="small">PVsyst V8.1.8 simulation (P50, Meteonorm 9.0, PR 85.4 %, Annex 7). Annual total <b>{gen1:,.0f} kWh</b> (≈ {gen1/185.38:,.0f} kWh/kWp).</p>{genchart}''')

# ---------------- page 4: plan + site ----------------
page(4, "PLAN VIEWS", f'''
{H("5. Design Solar Top Installation (Roof Plan)")}
<p class="small">The 299 panels are placed on the mezzanine roof on 7 Enerack
ballast tables at 10° tilt with 800 mm service aisles. INV-01 feeds tables T1–T4 (part), INV-02 feeds T4 (part)–T7. The inverter station and AC
combiner panel sit at the south-east corner; the AC cable runs to the main LV switchboard via the building riser.</p>
<div class="fig"><img src="{PLAN}" style="max-height:178mm"/><div class="cap">Proposed solar installation – Kampala Marriott Hotel, mezzanine roof (0°18'11.34"N, 32°35'13.76"E). Full drawing in Annex 2.</div></div>''')

# ---------------- page 5: energy use / TOU ----------------
tr = fin["tou_rows"]; ph = fin["hourly"]
bands = [dict(band=k, hours=h, load=tr[k][1]*1000, pv=tr[k][2]*1000, pv_share=tr[k][3], red=tr[k][5]) for k, h in (("Off-peak", "00:00–06:00"), ("Shoulder", "06:00–18:00"), ("Peak", "18:00–24:00"))]
s, Y, pl, cw = bars(ph, [f"{h:02d}" if h % 2 == 0 else None for h in range(24)], h=210, ylab="kW (average)",
                    colors=[NAVY if (h < 6 or h >= 19) else (ORG if h % 2 == 0 else ORG2) for h in range(24)], fmt=lambda v: f"{v:.0f}")
hourly = f'<svg viewBox="0 0 680 210" class="chart">{"".join(s)}</svg>'
share = gen1 / fin["bill"]["annual"]
page(5, "LOAD ASSESSMENT", f'''
{H("7. Hotel Load &amp; Solar Contribution")}
<p class="small">The hotel used <b>981,901 kWh in October 2026</b> (UEDCL bill; ≈ 11.8 GWh per year), with an average daytime demand of about
{fin["bill"]["avg_sh"]:,.0f} kW and a maximum demand of 1,836 kW. The solar system supplies about
<b>{share*100:.1f} %</b> of this, so all solar output is consumed on site even on low-occupancy days – no export and no battery are needed.</p>
{tbl([["Item", "Value", "Check", "Result"],
      ["Hotel annual consumption", f"{fin['bill']['annual']:,.0f} kWh", "Solar share of consumption", f"{share*100:.1f} %"],
      ["Solar generation, year 1", f"{gen1:,.0f} kWh", "Peak solar output", f"≈ {max(ph):.0f} kW (midday average)"],
      ["Hotel daytime demand", "far above solar output", "Energy exported", "0 kWh (all used on site)"],
      ["Grid tariff (avoided)", f"USD {tar+1e-9:.4f}/kWh (UGX 357), +2 %/yr", "Every solar kWh used?", "Yes – offsets grid purchase"]], widths=[27, 23, 27, 23])}
{H("8. Solar Generation by Time-of-Use Band")}
<p class="small">Average daily solar output by hour. All solar generation is counted in the shoulder period (06:00–18:00), when the hotel's
air-conditioning, kitchen and laundry loads are high; no solar energy is assigned to the peak band.</p>{hourly}
{tbl([["TOU band", "Hours", "Hotel consumption (kWh/yr)", "Solar energy (kWh/yr)", "Share of solar", "Reduction of band purchase"]] +
     [[b["band"], b["hours"], f"{b['load']:,.0f}", f"{b['pv']:,.0f}", f"{b['pv_share']*100:.1f} %", f"{b['red']*100:.1f} %"] for b in bands] +
     [["<b>Total</b>", "", f"<b>{tr['Total'][1]*1000:,.0f}</b>", f"<b>{tr['Total'][2]*1000:,.0f}</b>", "<b>100 %</b>", f"<b>{share*100:.1f} %</b>"]],
     widths=[14, 15, 20, 18, 14, 19])}
<p class="small">*Consumption and tariffs from the UEDCL bill for October 2026 (tariff 30.2 Large Consumers); annual = October × 12. Rates are as billed
(peak 428.8, shoulder 357.0, off-peak 286.5 UGX/kWh) at UGX 4,100/USD, excluding VAT; solar does not reduce the maximum-demand charge.</p>''')

# ---------------- page 6: connection diagram, schedule, warranty ----------------
def blk(x, y, w, h, t, s_, c):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{c}"/>'
            f'<text x="{x+w/2}" y="{y+h/2-2}" class="bt" text-anchor="middle">{t}</text><text x="{x+w/2}" y="{y+h/2+11}" class="bs" text-anchor="middle">{s_}</text>')
d = [blk(40, 20, 130, 44, "PV ARRAY 1", "152 × 620 W = 94.2 kWp", NAVY), blk(40, 150, 130, 44, "PV ARRAY 2", "147 × 620 W = 91.1 kWp", "#2c7a6b"),
     blk(240, 20, 130, 44, "INVERTER 1", "80 kW three-phase", "#2f5fc4"), blk(240, 150, 130, 44, "INVERTER 2", "80 kW three-phase", "#2f5fc4"),
     blk(430, 78, 120, 58, "AC COMBINER", "MCCBs, SPD, isolator", "#555"), blk(600, 78, 120, 58, "MAIN LV SWITCHBOARD", "NW10 H1 solar incomer", "#555"),
     blk(600, 6, 120, 44, "UEDCL GRID", "three-phase + meter", "#555"), blk(600, 170, 120, 44, "HOTEL LOADS", "≈ 1 GWh / month", GRN),
     blk(430, 170, 120, 44, "ENERGY MONITORING", "data logger + meter", "#7b4fa0")]
for yy in (42, 172):
    d.append(f'<line x1="170" y1="{yy}" x2="240" y2="{yy}" stroke="{ORG}" stroke-width="2.5"/><rect x="198" y="{yy-7}" width="14" height="14" fill="#b07a10"/>')
d += [f'<polyline points="370,42 400,42 400,98 430,98" fill="none" stroke="{NAVY}" stroke-width="2"/>',
      f'<polyline points="370,172 400,172 400,116 430,116" fill="none" stroke="{NAVY}" stroke-width="2"/>',
      f'<line x1="550" y1="107" x2="600" y2="107" stroke="{NAVY}" stroke-width="2"/>',
      f'<line x1="660" y1="50" x2="660" y2="78" stroke="{NAVY}" stroke-width="2"/>', f'<line x1="660" y1="136" x2="660" y2="170" stroke="{NAVY}" stroke-width="2"/>',
      f'<polyline points="600,192 550,192" fill="none" stroke="#7b4fa0" stroke-width="1.6" stroke-dasharray="5 4"/>',
      f'<polyline points="490,170 490,150 300,150 300,194" fill="none" stroke="#7b4fa0" stroke-width="1.6" stroke-dasharray="5 4"/>',
      '<text x="205" y="80" class="bs2" text-anchor="middle">DC isolator + SPD</text><text x="575" y="101" class="bs2" text-anchor="middle">C3</text>']
diag = f'<div class="diag"><svg viewBox="0 0 740 220">{"".join(d)}</svg></div>'
page(6, "ELECTRICAL DESIGN", f'''
{H("9. System Connection Diagram")}{diag}
{H("10. Implementation Schedule")}
{tbl([["Phase", "Activity", "Duration"],
      ["1. Site survey &amp; design", "Roof and LV switchboard survey, detailed design, approvals", "Weeks 1–3"],
      ["2. Procurement", "Ordering, shipping (Mombasa), customs clearing, delivery to site", "Weeks 2–10"],
      ["3. Installation", "Ballast structure, panels, inverters, AC combiner, cabling &amp; earthing", "Weeks 10–13"],
      ["4. Commissioning", "Testing, monitoring set-up, grid synchronisation", "Weeks 13–14"],
      ["5. Training &amp; handover", "Operator training, as-built drawings and O&amp;M manual", "Week 14"]], widths=[24, 60, 16])}
{H("11. Warranty &amp; After-Sales Support")}
<div class="two">{tbl([["Component", "Warranty"], ["Solar panels", "15 yrs product / 30 yrs linear power"], ["Inverters", "5 years (extendable)"],
                       ["Mounting structure", "10 years"], ["Installation workmanship", "2 years"]], widths=[48, 52])}<div></div></div>
<p class="small">Installed to IEC solar installation standards and Uganda Electricity Regulatory Authority requirements. After handover we provide
remote monitoring support, a free 6-month check-up visit and optional annual maintenance (panel cleaning, connection checks, inverter
software updates, performance report).</p>''')

# ---------------- page 7: financial analysis ----------------
s, Y, pl, cw = bars(cum, [str(i) if i % 5 == 0 or i == 6 else None for i in range(26)], h=190, neg=True, ymax=max(cum)*1.15,
                    colors=[("#c0392b" if v < 0 else GRN) for v in cum], fmt=lambda v: f"{v/1000:,.0f}k", ylab="USD")
for i in (0, 6, 12, 25):
    s.append(f'<text x="{pl+i*cw+cw*.5:.1f}" y="{(Y(cum[i])+13) if cum[i] < 0 else (Y(cum[i])-5):.1f}" class="vl" text-anchor="middle">{cum[i]/1000:+,.0f}k</text>')
cfchart = f'<svg viewBox="0 0 680 190" class="chart">{"".join(s)}</svg>'
yrs = [0, 1, 3, 5, 6, 7, 10, 12, 15, 20, 25]
cfrows = [["Year", "Generation (kWh)", "Tariff (USD/kWh)", "Savings (USD)", "Net cash flow (USD)", "Cumulative (USD)"]]
for y_ in yrs:
    if y_ == 0: cfrows.append(["0", "", "", "", f"({capex:,.0f})", f"({capex:,.0f})"]); continue
    g = fin["gen"][y_ - 1]; t = tar * 1.02 ** (y_ - 1); c = cum[y_]
    cfrows.append([str(y_), f"{g:,.0f}", f"{t:.3f}", f"{g*t:,.0f}", f"{fin['cf'][y_]:,.0f}", f"({-c:,.0f})" if c < 0 else f"{c:,.0f}"])
page(7, "FINANCIAL ANALYSIS", f'''
{H("12. Financial Analysis &amp; Cash Flow")}
<div class="two">{tbl([["Assumption", "Value"], ["Turnkey investment (excl. VAT)", usd(capex)], ["Avoided tariff, year 1", f"USD {tar+1e-9:.4f}/kWh (shoulder)"],
                       ["Tariff escalation", "2 % per year"], ["Degradation", "≈ 0.4 % per year"],
                       ["O&amp;M cost / discount rate", "none assumed / 10 %"]], widths=[56, 44])}
{tbl([["Result", "Value"], ["Year-1 savings", usd(y1)], ["Simple payback", f"{pb:.1f} years"], ["IRR (25 years)", f"{irr*100:.1f} %"],
      ["NPV @ 10 %", usd(npv)], ["LCOE (solar energy cost)", f"USD {lcoe:.3f}/kWh"], ["25-year savings", usd(sav25)]], widths=[56, 44])}</div>
<p class="small"><b>Cumulative cash flow (USD)</b> – the investment is recovered during year {int(pb)+1} ({pb:.1f} years).</p>{cfchart}
{tbl(cfrows, cls="num", widths=[8, 19, 16, 17, 20, 20])}
<p class="small">No O&amp;M or inverter-replacement cost is included. Values in brackets are negative (investment not yet recovered).</p>''')

# ---------------- page 8: quotation + financial summary ----------------
items = [("PV modules – Astronergy ASTRO N7 620 Wp bifacial N-type TOPCon", "299", "nos"), ("String inverters – Sigenergy Sigen PV 80M1, 80 kW, 1100 V", "2", "nos"),
         ("Ballasted aluminium mounting structure, 10° tilt", "1", "lot"), ("DC system – PV cable, connectors, string isolators, cable tray", "1", "lot"),
         ("AC system – AC combiner panel, MCCBs, cabling to main LV switchboard", "1", "lot"), ("Smart data logger, energy meter &amp; remote monitoring", "1", "set"),
         ("Earthing &amp; lightning protection integration", "1", "lot"), ("Installation, testing &amp; commissioning", "1", "lot"),
         ("Transport, logistics &amp; customs clearing to site", "1", "lot")]
qrows = "".join(f"<tr><td>{i}</td><td>{d_}</td><td>{q}</td><td>{u}</td>" + (f'<td rowspan="9" class="lump">{usd(capex)}</td>' if i == 1 else "") + "</tr>"
                for i, (d_, q, u) in enumerate(items, 1))
sens = fin["sens"]
page(8, "QUOTATION", f'''
{H("13. Quotation for 185.4 kWp Rooftop Solar PV – Turnkey EPC")}
{tbl([["Quote No.", REF, "Date", DATE, "Valid Until", VALID], ["Client", "Kampala Marriott Hotel", "Contact", "Mahil Fernando", "Currency", "USD"]],
     head=False, cls="kv6", widths=[12, 24, 10, 20, 12, 22])}
<table class="t q"><colgroup><col style="width:5%"/><col style="width:58%"/><col style="width:8%"/><col style="width:8%"/><col style="width:21%"/></colgroup>
<tr><th>#</th><th>Scope of supply &amp; works</th><th>Qty</th><th>Unit</th><th>Price (USD)</th></tr>{qrows}
<tr class="tot"><td></td><td>TOTAL TURNKEY EPC PRICE (excluding VAT and other applicable taxes)</td><td></td><td></td><td>{usd(capex)}</td></tr></table>
<p class="small">Equivalent to USD {capex/185400:.2f} per Wp. Amount in words: One hundred two thousand seven hundred eighty-nine US Dollars only.</p>
{tbl([["Payment terms", "75 % advance with PO · 25 % on commissioning"],
      ["Delivery", "Equipment 8–10 weeks from PO and advance; installation &amp; commissioning ≈ 4 weeks after delivery"],
      ["Taxes", "VAT, withholding tax and statutory levies excluded – charged as applicable"],
      ["Exclusions", "Roof strengthening / waterproofing, battery storage, utility and permit fees, works not listed above"],
      ["Client to provide", "Roof access, connection to the existing NW10 H1 solar incomer on the main LV switchboard, power &amp; water during installation"]], head=False, cls="kv", widths=[20, 80])}
''')

# ---------------- page 9: tariff sensitivity + annex index ----------------
page(9, "FINANCIAL SUMMARY", f'''
{H("14. Financial Summary &amp; Payback")}
{cards([(usd(capex), "Total investment (excl. VAT)"), (usd(y1), "Savings in year 1"), (f"{pb:.1f} years", "Payback period"), (f"{irr*100:.1f} %", "IRR (25 years)"),
        (usd(sav25), "25-year savings"), (usd(cum[25]), "25-year net gain after investment"), (f"{sav25/capex:.1f} x", "Savings / investment"), (usd(npv), "NPV @ 10 %")])}
{H("15. Tariff Sensitivity")}
{tbl([["Avoided tariff (USD/kWh)", "Year-1 savings (USD)", "Payback (years)", "IRR", "NPV @ 10 % (USD)"]] +
     [[(f"{t+1e-9:.4f} (base)" if abs(t-tar) < 1e-9 else f"{t:.4f}" if t not in (0.04, 0.06, 0.07, 0.10, 0.12) else f"{t:.2f}"), f"{s1:,.0f}", f"{p:.1f}", f"{i*100:.1f} %", f"{n:,.0f}"] for t, s1, p, i, n in sens], cls="num hl3 tight", widths=[24, 20, 18, 16, 22])}
<p class="small">The project remains attractive over a wide tariff range. The break-even tariff (NPV = 0 at 10 %) is about
<b>USD {fin['breakeven']:.4f}/kWh</b> – roughly {round((1-fin['breakeven']/tar)*100)} % below today's shoulder tariff. Other rows: with the 40 % energy rebate = USD {fin['scen']['rebate']:.4f}; VAT not recoverable = USD {fin['scen']['novat']:.4f}.</p>
{H("Annexes")}
{tbl([["Annex", "Title", "Page"],
      ["Annex 1", "Single-line diagram – PV system &amp; grid connection", "10"],
      ["Annex 2", "Solar PV layout – mezzanine roof", "11"],
      ["Annex 3", "Data sheet – Sigenergy Sigen PV inverter (80 kW)", "12–13"],
      ["Annex 4", "Data sheet – Astronergy ASTRO N7 620 W bifacial solar module", "14–15"],
      ["Annex 5", "PV structural drawing – Enerack ballast system", "16–17"],
      ["Annex 6", "Quotation – 185.4 kWp rooftop solar PV (one page)", "18"],
      ["Annex 7", "PVsyst simulation report – P50 energy yield (V8.1.8, VC0)", "19–25"]], cls="tight", widths=[14, 74, 12])}
{H("Next Steps")}
<ol class="steps"><li>Review of this proposal and clarification meeting with the hotel's engineering team.</li>
<li>Site survey: roof condition, LV switchboard, cable route and inverter location.</li>
<li>Confirmation of the tariff from recent utility bills and structural review of the roof.</li>
<li>Purchase order and advance payment – project start.</li></ol>
<p class="thanks">Thank you for considering NileSun Power Ltd. Contact: Mahil Fernando &nbsp;|&nbsp; +256 708669574 &nbsp;|&nbsp; sales@nilesunpower.com</p>''')

CSS = f"""
@page {{ size:A4; margin:0 }} * {{ box-sizing:border-box }}
body {{ margin:0; font-family:Arial,Helvetica,sans-serif; color:{INK}; font-size:9.6pt; -webkit-print-color-adjust:exact; print-color-adjust:exact }}
.page {{ width:210mm; height:297mm; position:relative; overflow:hidden; page-break-after:always; background:#fff }}
.stripe {{ display:flex; height:3.2mm }} .stripe i {{ flex:1 }} .stripe.big {{ height:6.5mm }} .stripe.bottom {{ position:absolute; bottom:0; left:0; right:0 }}
.hdr {{ display:flex; align-items:center; padding:7mm 18mm 4mm; gap:6mm }} .hdr img {{ height:26mm }}
.co {{ flex:1; white-space:nowrap; display:flex; flex-direction:column; gap:1.5mm; color:{MUT}; font-size:8.6pt }} .co b {{ color:{NAVY}; font-size:13pt }}
.ref {{ text-align:right; display:flex; flex-direction:column; gap:1.5mm; color:{MUT}; font-size:8.6pt }} .ref b {{ color:{NAVY}; font-size:9pt }}
.content {{ padding:3mm 18mm 0 }}
.ftr {{ position:absolute; bottom:8mm; left:18mm; right:18mm; border-top:1px solid {LINE}; padding-top:2mm; display:flex; justify-content:space-between; color:{MUT}; font-size:7.6pt }}
h1 {{ color:{NAVY}; font-size:19pt; margin:3mm 0 1mm }} .sub {{ color:{MUT}; font-size:10.5pt; margin-bottom:2mm }}
h2 {{ color:{NAVY}; font-size:12.5pt; margin:4mm 0 2.5mm; display:flex; align-items:center; gap:3mm }} h2 i {{ width:2.4mm; height:6.5mm; background:{ORG} }}
p {{ line-height:1.45; margin:0 0 2.5mm }} p.small {{ font-size:8.8pt }}
.t {{ width:100%; border-collapse:collapse; table-layout:fixed; margin-bottom:2mm }} .t th,.t td {{ border:1px solid {LINE}; padding:1.2mm 2mm; vertical-align:middle; line-height:1.3 }}
.t th {{ background:{CARD}; color:#1a2a4a; text-align:left; font-weight:700 }}
.t.tight th,.t.tight td {{ padding:0.7mm 2mm; font-size:8.6pt }}
.t.kv6 td:nth-child(odd) {{ background:{CARD} }} .t.kv td:first-child {{ background:{CARD}; font-weight:700 }}
.t.num td {{ text-align:right }} .t.num td:first-child {{ text-align:center }} .t.hl3 tr:nth-child(4) td {{ background:#fff3dc; font-weight:700 }}
.t.q td:nth-child(1),.t.q td:nth-child(3),.t.q td:nth-child(4) {{ text-align:center }} .t.q td.lump {{ text-align:center; font-size:15pt; font-weight:800; color:{NAVY} }}
.t.q tr.tot td {{ background:#e6f2e6; font-weight:800 }} .t.q tr.tot td:last-child {{ text-align:center; color:{NAVY} }}
.cards {{ display:grid; grid-template-columns:repeat(4,1fr); gap:3.5mm; margin:3mm 0 }}
.card {{ background:{CARD}; border-top:2.2mm solid; border-radius:0 0 3mm 3mm; text-align:center; padding:3mm 2mm 2.6mm }}
.card b {{ display:block; color:{NAVY}; font-size:14.5pt }} .card span {{ display:block; color:{MUT}; font-size:8pt; margin-top:1.8mm }}
ul.dots {{ padding-left:0; list-style:none; margin:0 }} ul.dots li {{ position:relative; padding-left:5mm; margin-bottom:1.6mm; line-height:1.4 }}
ul.dots li:before {{ content:''; position:absolute; left:0; top:1.3mm; width:2.4mm; height:2.4mm; border-radius:50%; background:{GRN} }}
.two {{ display:grid; grid-template-columns:1fr 1fr; gap:5mm; align-items:start }}
.chart {{ width:100%; height:auto; display:block }} .ax {{ font-size:8.5px; fill:{MUT} }} .vl {{ font-size:8px; font-weight:700; fill:{NAVY} }}
.fig {{ text-align:center }} .fig img {{ max-width:100%; border:1px solid {LINE} }} .cap {{ font-size:8pt; color:{MUT}; font-style:italic; margin-top:1.5mm; text-align:center }}
.diag {{ border:1px solid {LINE}; border-radius:3mm; padding:3mm }} .diag svg {{ width:100%; display:block }}
.bt {{ font-size:9px; font-weight:700; fill:#fff }} .bs {{ font-size:7.5px; fill:#e8edf5 }} .bs2 {{ font-size:7.5px; fill:{MUT} }}
.sign {{ display:grid; grid-template-columns:1fr 1fr; gap:6mm; margin-top:3mm }} .sign div {{ border:1px solid {LINE}; height:22mm; padding:2.5mm 3mm; display:flex; flex-direction:column; justify-content:space-between }}
.sign span {{ color:{MUT}; font-size:8pt }}
ol.steps {{ margin:0; padding-left:5mm; line-height:1.4 }}
.thanks {{ margin-top:3mm; text-align:center; color:{NAVY}; font-style:italic; font-size:8.5pt }}
.cover {{ text-align:center }} .cv-logo img {{ height:40mm; margin-top:8mm }}
.cv-photo {{ height:92mm; margin:5mm 18mm 0; background-size:cover; background-position:center 35%; border-radius:3mm }}
.cv-kicker {{ color:{ORG}; font-weight:700; font-size:10.5pt; margin-top:7mm }}
.cv-title {{ color:{NAVY}; font-size:25pt; font-weight:800; line-height:1.2; margin-top:3mm }} .cv-sub {{ color:{MUT}; font-size:10pt; margin-top:3mm }}
.cv-box {{ position:absolute; left:15mm; right:15mm; bottom:24mm; background:{NAVY}; border-radius:3mm; color:#fff; display:grid; grid-template-columns:1fr 1fr; text-align:left; padding:7mm 9mm }}
.cv-box div + div {{ border-left:1px solid #5a74b4; padding-left:9mm }} .cv-box span {{ color:{ORG}; font-weight:700; font-size:8.5pt }}
.cv-box b {{ display:block; font-size:12pt; margin:2.5mm 0 }} .cv-box p {{ font-size:8.6pt; line-height:1.75; margin:0 }}
.cv-valid {{ position:absolute; left:0; right:0; bottom:12mm; color:{GRN}; font-style:italic; font-size:9pt }}
.annex .atag {{ position:absolute; top:8mm; right:12mm; background:{NAVY}; color:#fff; font-weight:700; font-size:8.5pt; padding:1.5mm 4mm; border-radius:1.5mm }}
.annex .rot {{ position:absolute; top:18mm; left:10mm; width:190mm; height:262mm; display:flex; align-items:center; justify-content:center }}
.annex .rot img {{ width:262mm; height:auto; max-height:190mm; transform:rotate(90deg) }}
"""
open(os.path.join(HERE, "Kampala_Marriott_PV_Proposal_NSP.html"), "w").write(
    f"<!doctype html><html><head><meta charset='utf-8'><title>Kampala Marriott – Rooftop Solar PV Proposal</title><style>{CSS}</style></head><body>{''.join(pages)}</body></html>")
print("pages", len(pages))
