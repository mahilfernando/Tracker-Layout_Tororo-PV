"""Generate the 5-page technical & commercial proposal for a
20 kW / 80 kWh hybrid solar system (Tororo PV Power Company Limited).

Run:  python3 proposals/make_proposal_20kW_80kWh.py
Output: proposals/Proposal_20kW_80kWh_2026.10.26.pdf
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle

# ---------------------------------------------------------------- inputs
COMPANY = "TORORO PV POWER COMPANY LIMITED"
COMPANY_NAME = "Tororo PV Power Company Limited"
COMPANY_TAG = "Solar Power Systems | Design | Installation | Maintenance"
COMPANY_CONTACT = "Tororo, Uganda  |  Tel: ____________  |  Email: ____________"
QUOTE_NO = "TPV-261026-001"
DATE = "26-Oct-2026"
VALID = "25-Nov-2026"

SYSTEM_KW = 20                 # inverter rating
PRICE_PER_KW_USD = 250         # as instructed
FX_UGX_PER_USD = 3880          # same rate as the 22-Oct-2026 reference quote
MATERIAL_SHARE = 0.8607        # material / total split from the reference quote

N_MOD, MOD_W = 33, 620         # Jinko JKM620N-66HL4M-BDV
STRINGS, PER_STRING = 3, 11
N_BAT, BAT_KWH = 16, 5.12      # Dyness DL5.0C
DOD = 0.90
PR = 0.80                      # performance ratio
TARIFF_UGX = 800               # indicative grid tariff, UGX/kWh
SELF_USE = 0.90                # share of PV energy used on site

# indicative monthly GHI for Tororo, kWh/m2/day
GHI = [5.7, 5.9, 5.6, 5.2, 5.0, 5.0, 4.8, 5.0, 5.4, 5.3, 5.1, 5.4]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

# ---------------------------------------------------------------- derived
KWP = N_MOD * MOD_W / 1000
BAT_NOMINAL = 80               # kWh, as requested (16 x 5.12 = 81.92 kWh installed)
BAT_TOTAL = N_BAT * BAT_KWH
BAT_USABLE = BAT_TOTAL * DOD
TOTAL_USD = SYSTEM_KW * PRICE_PER_KW_USD
TOTAL_UGX = TOTAL_USD * FX_UGX_PER_USD
MAT_UGX = round(TOTAL_UGX * MATERIAL_SHARE, -2)
ADD_UGX = TOTAL_UGX - MAT_UGX
MONTHLY = [KWP * g * PR * d for g, d in zip(GHI, DAYS)]
ANNUAL = sum(MONTHLY)
DAILY = ANNUAL / 365
SAVE_UGX = ANNUAL * SELF_USE * TARIFF_UGX
PAYBACK = TOTAL_UGX / SAVE_UGX
CO2_T = ANNUAL * 0.55 / 1000   # t CO2 avoided vs diesel/grid mix

# ---------------------------------------------------------------- style
NAVY = colors.HexColor("#1F2A5C")
BLUE = colors.HexColor("#2F4FA8")
GREEN = colors.HexColor("#2E9E5B")
AMBER = colors.HexColor("#F2A900")
LIGHT = colors.HexColor("#EEF2FA")
GREY = colors.HexColor("#6B7280")
LINE = colors.HexColor("#C9D1E3")
PV = colors.HexColor("#22357A")
W, H = A4
M = 18 * mm

body = ParagraphStyle("b", fontName="Helvetica", fontSize=9.2, leading=13,
                      textColor=colors.HexColor("#222222"))
small = ParagraphStyle("s", parent=body, fontSize=8, leading=10.5)
cell = ParagraphStyle("c", parent=body, fontSize=8.3, leading=10.5)
cellb = ParagraphStyle("cb", parent=cell, fontName="Helvetica-Bold")


def ugx(v):
    return f"{v:,.0f}"


def usd(v):
    return f"{v:,.2f}"


def header(c, page, title):
    c.setFillColor(NAVY)
    c.rect(0, H - 30 * mm, W, 30 * mm, fill=1, stroke=0)
    c.setFillColor(AMBER)
    c.rect(0, H - 31.5 * mm, W, 1.5 * mm, fill=1, stroke=0)
    sun(c, M + 7 * mm, H - 15 * mm, 6.5 * mm)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(M + 17 * mm, H - 13 * mm, COMPANY)
    c.setFont("Helvetica", 8.5)
    c.drawString(M + 17 * mm, H - 18.5 * mm, COMPANY_TAG)
    c.drawString(M + 17 * mm, H - 23 * mm, COMPANY_CONTACT)
    c.setFont("Helvetica-Bold", 8.2)
    c.drawRightString(W - M, H - 13 * mm, title)
    c.setFont("Helvetica", 8)
    c.drawRightString(W - M, H - 18.5 * mm, f"Ref: {QUOTE_NO}")
    c.drawRightString(W - M, H - 23 * mm, f"Date: {DATE}")
    # footer
    c.setStrokeColor(LINE)
    c.line(M, 14 * mm, W - M, 14 * mm)
    c.setFillColor(GREY)
    c.setFont("Helvetica", 7.5)
    c.drawString(M, 9.5 * mm, f"{SYSTEM_KW} kW / {BAT_NOMINAL} kWh Hybrid Solar "
                 f"System Proposal  |  {COMPANY_NAME}")
    c.drawRightString(W - M, 9.5 * mm, f"Page {page} of 5")


def sun(c, x, y, r):
    c.setFillColor(AMBER)
    c.circle(x, y, r * 0.55, fill=1, stroke=0)
    c.setStrokeColor(AMBER)
    c.setLineWidth(1.4)
    import math
    for i in range(12):
        a = i * math.pi / 6
        c.line(x + r * 0.7 * math.cos(a), y + r * 0.7 * math.sin(a),
               x + r * math.cos(a), y + r * math.sin(a))
    c.setLineWidth(1)


def section(c, y, text):
    y -= 5 * mm
    c.setFillColor(GREEN)
    c.rect(M, y - 1.2 * mm, 2.2 * mm, 6 * mm, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 11.5)
    c.drawString(M + 4.5 * mm, y, text)
    return y - 5.5 * mm


def para(c, text, x, y, w, style=body):
    p = Paragraph(text, style)
    _, h = p.wrap(w, 500)
    p.drawOn(c, x, y - h)
    return y - h


def table(c, data, x, y, widths, head=True, zebra=True, extra=None):
    rows = [[Paragraph(str(v), cellb if (head and i == 0) else cell)
             if not isinstance(v, Paragraph) else v for v in r]
            for i, r in enumerate(data)]
    t = Table(rows, colWidths=widths)
    st = [("GRID", (0, 0), (-1, -1), 0.4, LINE),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("TOPPADDING", (0, 0), (-1, -1), 2.6),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6)]
    if head:
        st += [("BACKGROUND", (0, 0), (-1, 0), LIGHT)]
    if zebra:
        for i in range(2 if head else 1, len(rows), 2):
            st.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F8FAFD")))
    st += extra or []
    t.setStyle(TableStyle(st))
    _, h = t.wrap(0, 0)
    t.drawOn(c, x, y - h)
    return y - h


def tile(c, x, y, w, h, value, label, col):
    c.setFillColor(LIGHT)
    c.roundRect(x, y, w, h, 2 * mm, fill=1, stroke=0)
    c.setFillColor(col)
    c.rect(x, y + h - 1.6 * mm, w, 1.6 * mm, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(x + w / 2, y + h * 0.45, value)
    c.setFillColor(GREY)
    c.setFont("Helvetica", 7.6)
    c.drawCentredString(x + w / 2, y + 3 * mm, label)


# ================================================================ page 1
def page1(c):
    header(c, 1, "TECHNICAL & COMMERCIAL PROPOSAL")
    y = H - 44 * mm
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(M, y, f"{SYSTEM_KW} kW / {BAT_NOMINAL} kWh Hybrid Solar Power System")
    c.setFont("Helvetica", 10.5)
    c.setFillColor(GREY)
    c.drawString(M, y - 7 * mm, f"{KWP:.2f} kWp PV array  |  {SYSTEM_KW} kW three-phase hybrid "
                 f"inverter  |  {BAT_TOTAL:.2f} kWh LiFePO4 storage")
    y -= 16 * mm

    y = section(c, y, "Quote & Client Details")
    y = table(c, [
        ["Quote No.", QUOTE_NO, "Date", DATE, "Valid Until", VALID],
        ["Client Name", "", "Contact No.", "", "Client Email", ""],
        ["Site Address", "", "Supply Type", "Three-phase 415 V", "VAT TIN No.", "__________"],
    ], M, y, [24 * mm, 36 * mm, 22 * mm, 30 * mm, 23 * mm, 39 * mm], head=False, zebra=False,
        extra=[("BACKGROUND", (0, 0), (0, -1), LIGHT), ("BACKGROUND", (2, 0), (2, -1), LIGHT),
               ("BACKGROUND", (4, 0), (4, -1), LIGHT),
               ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold")])
    y -= 8 * mm

    tw = (W - 2 * M - 3 * 4 * mm) / 4
    th = 20 * mm
    vals = [(f"{KWP:.2f} kWp", "PV array capacity", AMBER),
            (f"{SYSTEM_KW} kW", "Inverter output (3-phase)", BLUE),
            (f"{BAT_TOTAL:.1f} kWh", "Battery storage", GREEN),
            (f"USD {TOTAL_USD:,.0f}", "Total system cost", NAVY)]
    for i, (v, l, col) in enumerate(vals):
        tile(c, M + i * (tw + 4 * mm), y - th, tw, th, v, l, col)
    y -= th + 4 * mm
    vals = [(f"{DAILY:.0f} kWh", "Avg. daily generation", AMBER),
            (f"{ANNUAL/1000:,.1f} MWh", "Est. annual generation", BLUE),
            (f"{BAT_USABLE:.0f} kWh", f"Usable storage ({DOD:.0%} DoD)", GREEN),
            (f"{CO2_T:.0f} t", "CO2 avoided per year", NAVY)]
    for i, (v, l, col) in enumerate(vals):
        tile(c, M + i * (tw + 4 * mm), y - th, tw, th, v, l, col)
    y -= th + 3 * mm

    y = section(c, y, "1. Executive Summary")
    txt = (
        f"{COMPANY_NAME} is pleased to submit this proposal for the design, supply, "
        f"installation and commissioning of a <b>{SYSTEM_KW} kW / {BAT_NOMINAL} kWh hybrid "
        f"solar power system</b> for the client's residence. The system combines a "
        f"<b>{KWP:.2f} kWp</b> rooftop array of {N_MOD} Jinko 620 W N-type bifacial modules, a "
        f"Deye {SYSTEM_KW} kW three-phase hybrid inverter and {N_BAT} Dyness 5.12 kWh LiFePO4 "
        f"battery modules, giving the house clean daytime power and up to "
        f"<b>{BAT_USABLE:.0f} kWh</b> of usable night-time and back-up energy.")
    y = para(c, txt, M, y, W - 2 * M)
    y -= 2.5 * mm
    txt = (
        f"The array is expected to generate about <b>{ANNUAL:,.0f} kWh per year</b> "
        f"(approx. {DAILY:.0f} kWh/day). At an indicative grid tariff of UGX {TARIFF_UGX}/kWh this "
        f"is worth about <b>UGX {SAVE_UGX/1e6:,.1f} million per year</b> in avoided electricity "
        f"costs. The turnkey price is <b>USD {TOTAL_USD:,.0f}</b> (UGX {ugx(TOTAL_UGX)}), "
        f"based on USD {PRICE_PER_KW_USD} per kW of system capacity, including equipment, "
        f"mounting, balance of system, logistics, installation and commissioning.")
    y = para(c, txt, M, y, W - 2 * M)
    y -= 0.5 * mm

    y = section(c, y, "Key Benefits")
    bl = [
        "Uninterrupted power: automatic switch-over to solar + battery in under 10 ms during grid outages.",
        "Lower bills: most daytime load and much of the evening load supplied from the sun.",
        "Long life: Tier-1 N-type modules (30-year output warranty) and 6,000+ cycle LiFePO4 batteries.",
        "Remote monitoring: inverter Wi-Fi logger with mobile app for live generation, load and battery data.",
        "Scalable: the inverter and battery bank can be expanded or paralleled later.",
    ]
    for b in bl:
        c.setFillColor(GREEN)
        c.circle(M + 1.6 * mm, y - 1.4 * mm, 0.9 * mm, fill=1, stroke=0)
        y = para(c, b, M + 4.5 * mm, y + 1.2 * mm, W - 2 * M - 5 * mm) - 1.3 * mm


# ================================================================ page 2
def page2(c):
    header(c, 2, "SYSTEM DESIGN")
    y = H - 42 * mm
    y = section(c, y, "2. Equipment Schedule (Bill of Materials)")
    y = table(c, [
        ["#", "Item", "Specification", "Qty", "UoM"],
        ["1", "Hybrid inverter", f"Deye SUN-20K-SG05LP3-EU, {SYSTEM_KW} kW, 3-phase 400 V, 48 V battery, "
         "2 MPPT, Wi-Fi logger", "1", "pcs"],
        ["2", "Battery modules", f"Dyness DL5.0C, 5.12 kWh, 51.2 V 100 Ah LiFePO4 "
         f"(total {BAT_TOTAL:.2f} kWh)", str(N_BAT), "pcs"],
        ["3", "Battery racks", "19-inch cabinet racks, 8 modules each, with busbars & comms cables", "2", "pcs"],
        ["4", "Solar PV modules", f"Jinko JKM620N-66HL4M-BDV, 620 W N-type bifacial "
         f"(total {KWP:.2f} kWp)", str(N_MOD), "pcs"],
        ["5", "Mounting structure", "Anodised aluminium rails, mid/end clamps, roof hooks / L-feet", "1", "system"],
        ["6", "DC protection", "PV combiner with DC isolators, 1000 V fuses & Type II SPD; "
         "battery DC breaker/fuse", "1", "set"],
        ["7", "AC protection", "AC distribution board, MCBs, RCD, Type II AC SPD, change-over switch", "1", "set"],
        ["8", "Cabling", "6 mm² PV solar cable, 70 mm² battery cable, AC cable, MC4 connectors, conduit & trunking", "1", "lot"],
        ["9", "Earthing", "Copper earth rods, earth cable and bonding of array frame and enclosures", "1", "set"],
    ], M, y, [8 * mm, 32 * mm, 106 * mm, 12 * mm, 16 * mm])
    y -= 2 * mm

    y = section(c, y, "3. PV Array & String Design")
    half = (W - 2 * M - 6 * mm) / 2
    y2 = table(c, [
        ["Parameter", "Value"],
        ["Modules", f"{N_MOD} x {MOD_W} W = {KWP:.2f} kWp"],
        ["String configuration", f"{STRINGS} strings x {PER_STRING} modules"],
        ["MPPT 1 / MPPT 2", "2 strings / 1 string"],
        ["String Voc (STC)", f"approx. {PER_STRING*50.1:.0f} V"],
        ["String Vmp (STC)", f"approx. {PER_STRING*42.0:.0f} V"],
        ["DC/AC ratio", f"{KWP/SYSTEM_KW:.2f}"],
        ["Roof area used", "approx. 95 m²"],
    ], M, y, [half * 0.5, half * 0.5])
    yb = table(c, [
        ["Battery parameter", "Value"],
        ["Modules", f"{N_BAT} x {BAT_KWH} kWh (all in parallel)"],
        ["Nominal voltage", "51.2 V DC"],
        ["Total / usable energy", f"{BAT_TOTAL:.2f} / {BAT_USABLE:.1f} kWh"],
        ["Chemistry", "LiFePO4, BMS with CAN comms"],
        ["Design cycle life", "6,000+ cycles @ 90% DoD"],
        ["Back-up @ 3 kW load", f"approx. {BAT_USABLE/3:.0f} hours"],
        ["Back-up @ 5 kW load", f"approx. {BAT_USABLE/5:.0f} hours"],
    ], M + half + 6 * mm, y, [half * 0.5, half * 0.5])
    y = min(y2, yb) - 2 * mm

    y = section(c, y, "4. Estimated Energy Generation")
    y = para(c, f"Estimate based on long-term average irradiation for Tororo (lat. 0.69° N) and a "
                f"performance ratio of {PR:.0%}. Annual total: <b>{ANNUAL:,.0f} kWh</b>.",
             M, y, W - 2 * M, small)
    y -= 4 * mm
    # bar chart
    ch_h = 52 * mm
    x0, y0 = M + 12 * mm, y - ch_h
    cw = W - 2 * M - 14 * mm
    vmax = 3500
    c.setFont("Helvetica", 7)
    for v in range(0, vmax + 1, 500):
        yy = y0 + ch_h * v / vmax
        c.setStrokeColor(colors.HexColor("#E3E8F2"))
        c.line(x0, yy, x0 + cw, yy)
        c.setFillColor(GREY)
        c.drawRightString(x0 - 2 * mm, yy - 2, f"{v:,}")
    c.saveState()
    c.translate(M, y0 + ch_h / 2)
    c.rotate(90)
    c.drawCentredString(0, 0, "kWh / month")
    c.restoreState()
    bw = cw / 12
    for i, v in enumerate(MONTHLY):
        bh = ch_h * v / vmax
        c.setFillColor(AMBER if i % 2 == 0 else colors.HexColor("#F6C343"))
        c.rect(x0 + i * bw + bw * 0.18, y0, bw * 0.64, bh, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 6.8)
        c.drawCentredString(x0 + i * bw + bw / 2, y0 + bh + 1.2 * mm, f"{v:,.0f}")
        c.setFillColor(GREY)
        c.setFont("Helvetica", 7.5)
        c.drawCentredString(x0 + i * bw + bw / 2, y0 - 4 * mm, MONTHS[i])
    c.setStrokeColor(GREY)
    c.line(x0, y0, x0 + cw, y0)


# ================================================================ page 3
def page3(c):
    header(c, 3, "PLAN VIEWS")
    y = H - 42 * mm
    y = section(c, y, "5. Roof Plan - PV Array Layout")
    y = para(c, "Indicative layout on a typical 20 m x 12 m pitched-roof bungalow. Final layout "
                "will be confirmed after the site survey (roof orientation, shading and structure).",
             M, y, W - 2 * M, small)
    y -= 3 * mm

    # ---- roof plan (scale)
    s = 6.6 * mm                       # 1 m = s
    hx, hy = M + 20 * mm, y - 12.6 * s - 6 * mm
    hw, hd = 20, 12
    ov = 0.6
    c.setStrokeColor(NAVY)
    c.setFillColor(colors.HexColor("#E8E3DA"))
    c.rect(hx - ov * s, hy - ov * s, (hw + 2 * ov) * s, (hd + 2 * ov) * s, fill=1, stroke=1)
    # ridge
    c.setDash(4, 2)
    c.line(hx - ov * s, hy + hd / 2 * s, hx + (hw + ov) * s, hy + hd / 2 * s)
    c.setDash()
    c.setFont("Helvetica", 6.5)
    c.setFillColor(GREY)
    c.drawString(hx + (hw - 2.2) * s, hy + hd / 2 * s + 1 * mm, "RIDGE")
    # modules portrait 1.134 x 2.382 m
    mw, mh, g = 1.134, 2.382, 0.03
    cols = colors.HexColor("#22357A"), colors.HexColor("#2C5AA0"), colors.HexColor("#2E7D6B")
    arr_w = PER_STRING * mw + (PER_STRING - 1) * g
    ax = hx + (hw - arr_w) / 2 * s
    rows = [(hy + (hd / 2 + 0.6) * s, 0), (hy + (hd / 2 + 0.6 + mh + 0.15) * s, 1),
            (hy + (hd / 2 - 0.6 - mh) * s, 2)]
    for ry, si in rows:
        for k in range(PER_STRING):
            x = ax + k * (mw + g) * s
            c.setFillColor(cols[si])
            c.setStrokeColor(colors.white)
            c.setLineWidth(0.4)
            c.rect(x, ry, mw * s, mh * s, fill=1, stroke=1)
            c.setStrokeColor(colors.HexColor("#8FA6D8"))
            c.setLineWidth(0.2)
            for q in range(1, 4):
                c.line(x + mw * s * q / 4, ry, x + mw * s * q / 4, ry + mh * s)
        c.setFillColor(NAVY)
        c.roundRect(ax + arr_w * s / 2 - 19 * mm, ry + mh * s / 2 - 2.4 * mm, 38 * mm, 4.8 * mm,
                    1 * mm, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(ax + arr_w * s / 2, ry + mh * s / 2 - 2.4, f"STRING {si+1}  ({PER_STRING} x {MOD_W} W)")
    c.setLineWidth(1)
    # labels / dims
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(hx + hw * s * 0.5, hy + (hd + ov) * s + 2.5 * mm, "ROOF FACE A (NORTH)")
    c.drawCentredString(hx + hw * s * 0.5, hy - ov * s - 5 * mm, "ROOF FACE B (SOUTH)")
    dim(c, hx, hy - ov * s - 9 * mm, hx + hw * s, "20.0 m")
    vdim(c, hx - ov * s - 6 * mm, hy, hy + hd * s, "12.0 m")
    # combiner + cable drop
    cbx, cby = hx + (hw - 1.6) * s, hy + 1.0 * s
    c.setFillColor(AMBER)
    c.rect(cbx, cby, 1.2 * s, 0.8 * s, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica", 6.3)
    c.drawRightString(cbx - 1 * mm, cby + 1.5 * mm, "DC combiner / cable drop")
    # north arrow + legend
    na_x, na_y = W - M - 8 * mm, y - 8 * mm
    c.setFillColor(NAVY)
    p = c.beginPath()
    p.moveTo(na_x, na_y)
    p.lineTo(na_x - 2.5 * mm, na_y - 8 * mm)
    p.lineTo(na_x + 2.5 * mm, na_y - 8 * mm)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(na_x, na_y + 1.5 * mm, "N")
    ly = hy - 20 * mm
    for i, (col, t) in enumerate(zip(cols, ["String 1 -> MPPT 1", "String 2 -> MPPT 1",
                                             "String 3 -> MPPT 2"])):
        lx = M + i * 46 * mm
        c.setFillColor(col)
        c.rect(lx, ly, 5 * mm, 3 * mm, fill=1, stroke=0)
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 7.5)
        c.drawString(lx + 6.5 * mm, ly + 0.6 * mm, t)
    c.setFillColor(AMBER)
    c.rect(M + 138 * mm, ly, 5 * mm, 3 * mm, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.drawString(M + 144.5 * mm, ly + 0.6 * mm, "DC combiner")

    # ---- floor plan
    y = ly - 4 * mm
    y = section(c, y, "6. Ground Floor Plan - Equipment Location & Cable Routes")
    s = 5.6 * mm
    fx, fy = M + 24 * mm, y - 12 * s - 6 * mm
    rooms = [  # x, y, w, h, name
        (0, 6, 7, 6, "LIVING ROOM"), (7, 6, 5, 6, "DINING"), (12, 8, 4, 4, "KITCHEN"),
        (16, 8, 4, 4, "PLANT ROOM"), (12, 6, 8, 2, "CORRIDOR"),
        (0, 0, 5, 6, "BEDROOM 1"), (5, 0, 5, 6, "BEDROOM 2"), (10, 0, 3, 3, "BATH"),
        (10, 3, 3, 3, "STORE"), (13, 0, 7, 6, "MASTER BEDROOM"),
    ]
    c.setLineWidth(1.6)
    c.setStrokeColor(colors.HexColor("#333333"))
    for rx, ry, rw, rh, nm in rooms:
        c.setFillColor(colors.HexColor("#FFF6DD") if nm == "PLANT ROOM" else colors.white)
        c.rect(fx + rx * s, fy + ry * s, rw * s, rh * s, fill=1, stroke=1)
        c.setFillColor(GREY)
        c.setFont("Helvetica", 6.3)
        c.drawCentredString(fx + (rx + rw / 2) * s, fy + (ry + rh - 0.6) * s, nm)
    c.setLineWidth(1)
    # equipment in plant room
    def box(x, y_, w, h, col, label):
        c.setFillColor(col)
        c.rect(fx + x * s, fy + y_ * s, w * s, h * s, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 5.6)
        c.drawCentredString(fx + (x + w / 2) * s, fy + (y_ + h / 2) * s - 2, label)
    box(16.3, 8.3, 1.5, 0.9, BLUE, "INV")
    box(18.1, 8.3, 0.8, 2.0, GREEN, "B1")
    box(19.0, 8.3, 0.8, 2.0, GREEN, "B2")
    box(16.3, 9.6, 1.3, 0.6, colors.HexColor("#7A3E9D"), "ACDB")
    box(12.3, 6.3, 1.0, 0.6, GREY, "MDB")
    # cable routes
    c.setStrokeColor(AMBER)
    c.setLineWidth(1.4)
    c.setDash(3, 2)
    c.line(fx + 19.6 * s, fy + 12.6 * s, fx + 19.6 * s, fy + 11.2 * s)
    c.line(fx + 19.6 * s, fy + 11.2 * s, fx + 17.9 * s, fy + 11.2 * s)
    c.line(fx + 17.9 * s, fy + 11.2 * s, fx + 17.9 * s, fy + 9.2 * s)
    c.setStrokeColor(colors.HexColor("#7A3E9D"))
    c.line(fx + 16.3 * s, fy + 8.75 * s, fx + 13.3 * s, fy + 6.6 * s)
    c.setDash()
    c.setLineWidth(1)
    # meter & earth pit outside
    c.setFillColor(colors.HexColor("#555555"))
    c.rect(fx + 20.3 * s, fy + 6.5 * s, 0.8 * s, 0.8 * s, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 6.3)
    c.drawString(fx + 21.3 * s, fy + 6.7 * s, "Utility meter")
    c.setStrokeColor(GREEN)
    c.circle(fx + 21 * s, fy + 9.5 * s, 0.4 * s, stroke=1, fill=0)
    c.line(fx + 20.7 * s, fy + 9.5 * s, fx + 21.3 * s, fy + 9.5 * s)
    c.drawString(fx + 21.6 * s, fy + 9.3 * s, "Earth pit")
    c.drawString(fx + 21.3 * s, fy + 11.9 * s, "PV DC cables")
    c.drawString(fx + 21.3 * s, fy + 11.3 * s, "from roof")
    dim(c, fx, fy - 4 * mm, fx + 20 * s, "20.0 m")
    vdim(c, fx - 5 * mm, fy, fy + 12 * s, "12.0 m")
    # key
    kx, ky = M, fy + 12 * s - 2 * mm
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(NAVY)
    c.drawString(kx, ky + 4 * mm, "KEY")
    for i, (col, t) in enumerate([(BLUE, "INV"), (GREEN, "BAT"), (colors.HexColor("#7A3E9D"), "ACDB"),
                                  (GREY, "MDB")]):
        c.setFillColor(col)
        c.rect(kx, ky - i * 5 * mm, 3 * mm, 3 * mm, fill=1, stroke=0)
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 6.5)
        c.drawString(kx + 4 * mm, ky - i * 5 * mm + 0.7 * mm, t)


def dim(c, x1, y, x2, label):
    c.setStrokeColor(GREY)
    c.setLineWidth(0.5)
    c.line(x1, y, x2, y)
    c.line(x1, y - 1.2 * mm, x1, y + 1.2 * mm)
    c.line(x2, y - 1.2 * mm, x2, y + 1.2 * mm)
    c.setFillColor(colors.white)
    c.rect((x1 + x2) / 2 - 7 * mm, y - 1.6 * mm, 14 * mm, 3.2 * mm, fill=1, stroke=0)
    c.setFillColor(GREY)
    c.setFont("Helvetica", 7)
    c.drawCentredString((x1 + x2) / 2, y - 1.1 * mm, label)
    c.setLineWidth(1)


def vdim(c, x, y1, y2, label):
    c.setStrokeColor(GREY)
    c.setLineWidth(0.5)
    c.line(x, y1, x, y2)
    c.line(x - 1.2 * mm, y1, x + 1.2 * mm, y1)
    c.line(x - 1.2 * mm, y2, x + 1.2 * mm, y2)
    c.saveState()
    c.translate(x, (y1 + y2) / 2)
    c.rotate(90)
    c.setFillColor(colors.white)
    c.rect(-7 * mm, -1.6 * mm, 14 * mm, 3.2 * mm, fill=1, stroke=0)
    c.setFillColor(GREY)
    c.setFont("Helvetica", 7)
    c.drawCentredString(0, -1.1 * mm, label)
    c.restoreState()
    c.setLineWidth(1)


# ================================================================ page 4
def page4(c):
    header(c, 4, "ELECTRICAL DESIGN & IMPLEMENTATION")
    y = H - 42 * mm
    y = section(c, y, "7. Single-Line Diagram")
    top = y - 2 * mm
    dh = 80 * mm
    c.setStrokeColor(LINE)
    c.roundRect(M, top - dh, W - 2 * M, dh, 2 * mm, fill=0, stroke=1)

    def blk(x, y_, w, h, col, title, sub=""):
        c.setFillColor(col)
        c.roundRect(x, y_, w, h, 1.5 * mm, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 7.6)
        c.drawCentredString(x + w / 2, y_ + h / 2 + (1 if sub else -2.5), title)
        if sub:
            c.setFont("Helvetica", 6.4)
            c.drawCentredString(x + w / 2, y_ + h / 2 - 7, sub)

    def wire(pts, col=NAVY, wdt=1.2):
        c.setStrokeColor(col)
        c.setLineWidth(wdt)
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            c.line(x1, y1, x2, y2)
        c.setLineWidth(1)

    bw, bh = 34 * mm, 12 * mm
    # PV strings
    px = M + 5 * mm
    sy = [top - 14 * mm, top - 30 * mm, top - 46 * mm]
    for i, yy in enumerate(sy):
        blk(px, yy, bw, bh, PV, f"PV STRING {i+1}", f"{PER_STRING} x {MOD_W} W = {PER_STRING*MOD_W/1000:.2f} kWp")
    cx = px + bw + 14 * mm
    blk(cx, top - 46 * mm, 30 * mm, 44 * mm, colors.HexColor("#B07D00"), "DC COMBINER",
        "isolators | fuses | SPD")
    for yy in sy:
        wire([(px + bw, yy + bh / 2), (cx, yy + bh / 2)], AMBER)
    ix = cx + 30 * mm + 14 * mm
    iy = top - 46 * mm
    blk(ix, iy, 36 * mm, 44 * mm, BLUE, "HYBRID INVERTER", f"Deye {SYSTEM_KW} kW 3-ph")
    wire([(cx + 30 * mm, sy[0] + bh / 2), (ix, sy[0] + bh / 2)], AMBER)
    wire([(cx + 30 * mm, sy[2] + bh / 2), (ix, sy[2] + bh / 2)], AMBER)
    c.setFont("Helvetica", 6.3)
    c.setFillColor(GREY)
    c.drawCentredString((cx + 30 * mm + ix) / 2, sy[0] + bh / 2 + 1.5 * mm, "MPPT 1")
    c.drawCentredString((cx + 30 * mm + ix) / 2, sy[2] + bh / 2 + 1.5 * mm, "MPPT 2")
    # battery
    bx = ix
    by = top - dh + 5 * mm
    blk(bx, by, 36 * mm, 15 * mm, GREEN, "BATTERY BANK", f"{N_BAT} x {BAT_KWH} kWh | 51.2 V")
    wire([(bx + 18 * mm, by + 15 * mm), (bx + 18 * mm, iy)], colors.HexColor("#C0392B"), 1.6)
    c.setFillColor(GREY)
    c.drawString(bx + 20 * mm, by + 17 * mm, "DC breaker + fuse")
    c.drawString(bx + 20 * mm, by + 21 * mm, "BMS CAN comms")
    # AC side
    gx = W - M - 5 * mm - 30 * mm
    blk(gx, top - 16 * mm, 30 * mm, 12 * mm, colors.HexColor("#555555"), "UTILITY GRID", "3-ph 415 V + meter")
    blk(gx, top - 36 * mm, 30 * mm, 12 * mm, colors.HexColor("#7A3E9D"), "MAIN DB", "non-essential loads")
    blk(gx, top - 58 * mm, 30 * mm, 12 * mm, colors.HexColor("#7A3E9D"), "BACKED-UP DB", "essential loads")
    wire([(gx + 15 * mm, top - 16 * mm), (gx + 15 * mm, top - 24 * mm)])
    mid = ix + 36 * mm
    wire([(gx, top - 30 * mm), (mid + 8 * mm, top - 30 * mm), (mid + 8 * mm, iy + 34 * mm), (mid, iy + 34 * mm)])
    wire([(mid, iy + 10 * mm), (mid + 8 * mm, iy + 10 * mm), (mid + 8 * mm, top - 52 * mm), (gx, top - 52 * mm)])
    c.setFillColor(GREY)
    c.setFont("Helvetica", 6.3)
    c.drawString(mid + 1 * mm, iy + 30 * mm, "GRID")
    c.drawString(mid + 1 * mm, iy + 6 * mm, "LOAD")
    c.drawRightString(W - M - 4 * mm, top - dh + 8 * mm, "AC SPD, MCBs & RCD on all AC circuits")
    c.drawString(M + 5 * mm, top - dh + 8 * mm, "All metal frames bonded to common earth (< 10 ohm)")
    y = top - dh - 2 * mm

    y = section(c, y, "8. Implementation Schedule")
    y = table(c, [
        ["Phase", "Activity", "Duration"],
        ["1. Site survey", "Roof inspection, load audit, shading & supply check, design confirmation", "1-2 days"],
        ["2. Procurement", "Equipment ordering, delivery to site, pre-installation checks", "1-2 weeks"],
        ["3. Installation", "Mounting structure, modules, inverter, batteries, cabling, earthing & protection", "4-5 days"],
        ["4. Commissioning", "Insulation & polarity tests, settings, monitoring app set-up, handover", "1 day"],
        ["5. Training", "Client training on operation, app monitoring and basic care", "2 hours"],
    ], M, y, [32 * mm, 116 * mm, 26 * mm])
    y -= 2 * mm

    y = section(c, y, "9. Standards, Warranty & After-Sales Support")
    half = (W - 2 * M - 6 * mm) / 2
    y1 = table(c, [
        ["Component", "Warranty"],
        ["PV modules", "12 yrs product / 30 yrs power"],
        ["Hybrid inverter", "5 years (manufacturer)"],
        ["LiFePO4 batteries", "10 years (manufacturer)"],
        ["Installation workmanship", "2 years"],
    ], M, y, [half * 0.5, half * 0.5])
    p = Paragraph(
        "Installation follows IEC 62548 (PV array design), IEC 60364-7-712 and the Uganda Electricity "
        "Regulatory Authority wiring requirements. After handover we provide remote monitoring "
        "support, a free 6-month check-up visit and optional annual maintenance (module cleaning, "
        "torque checks, firmware updates, battery health report).", small)
    _, ph = p.wrap(half, 200)
    p.drawOn(c, M + half + 6 * mm, y - ph)


# ================================================================ page 5
def page5(c):
    header(c, 5, "QUOTATION")
    y = H - 42 * mm
    y = section(c, y, "10. Commercial Offer")
    rate = PRICE_PER_KW_USD
    rows = [
        ["Item", "Qty", "UoM", "Cost (UGX)"],
        [f"Deye {SYSTEM_KW} kW 3-phase hybrid inverter (SUN-20K-SG05LP3-EU)", "1", "pcs", "Included"],
        ["Dyness 5.12 kWh 51.2 V 100 Ah LiFePO4 (DL5.0C)", str(N_BAT), "pcs", "Included"],
        ["Jinko 620 W N-Type bifacial (JKM620N-66HL4M-BDV)", str(N_MOD), "pcs", "Included"],
        ["Mounting structure", "1", "system", "Included"],
        ["Balance of system (protection, cabling, earthing, racks)", "1", "system", "Included"],
        ["<b>Total Material Cost</b>", "", "", f"<b>{ugx(MAT_UGX)}</b>"],
        ["Logistics & transport", "", "", "Included"],
        ["Commercials", "", "", "Included"],
        ["Installation labour, testing & commissioning", "", "", "Included"],
        ["<b>Total Additional Costs</b>", "", "", f"<b>{ugx(ADD_UGX)}</b>"],
        ["Subtotal (excl. VAT)", "", "", ugx(TOTAL_UGX)],
        ["Less discount (not applied)", "", "", "0"],
        ["VAT (not applicable)", "", "", "0"],
        ["<b>TOTAL SYSTEM COST (UGX)</b>", "", "", f"<b>{ugx(TOTAL_UGX)}</b>"],
        ["<b>TOTAL SYSTEM COST (USD)</b>", "", "", f"<b>{usd(TOTAL_USD)}</b>"],
    ]
    rows = [[Paragraph(v, cellb if i == 0 else cell) for v in r] for i, r in enumerate(rows)]
    n = len(rows)
    y = table(c, rows, M, y, [108 * mm, 16 * mm, 18 * mm, 32 * mm], zebra=False, extra=[
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("BACKGROUND", (0, 6), (-1, 6), LIGHT), ("BACKGROUND", (0, 10), (-1, 10), LIGHT),
        ("BACKGROUND", (0, n - 2), (-1, n - 1), colors.HexColor("#E6F4EC")),
    ])
    y = para(c, f"Pricing basis: {SYSTEM_KW} kW x USD {rate}/kW = USD {TOTAL_USD:,.0f}; "
                f"exchange rate UGX {FX_UGX_PER_USD:,}/USD. Prices valid until {VALID}.",
             M, y - 1.5 * mm, W - 2 * M, small)
    y -= 1.5 * mm

    y = section(c, y, "11. Financial Summary (indicative)")
    y = table(c, [
        ["Indicator", "Value", "Indicator", "Value"],
        ["Annual generation", f"{ANNUAL:,.0f} kWh", "Annual savings", f"UGX {ugx(SAVE_UGX)}"],
        ["Self-consumed share", f"{SELF_USE:.0%}", "Simple payback", f"approx. {PAYBACK*12:.0f} months"],
        ["Tariff assumed", f"UGX {TARIFF_UGX}/kWh", "25-year savings (no escalation)", f"UGX {SAVE_UGX*25/1e6:,.0f} M"],
    ], M, y, [36 * mm, 36 * mm, 52 * mm, 50 * mm])
    y -= 1.5 * mm

    y = section(c, y, "12. Payment Details & Terms")
    y = table(c, [
        ["Payment Method", "Account Number", "Bank / Branch", "Account Name"],
        ["Bank Transfer", "____________", "____________", COMPANY_NAME],
        ["Mobile Money", "____________", "____________", COMPANY_NAME],
    ], M, y, [36 * mm, 40 * mm, 44 * mm, 54 * mm])
    y -= 2.5 * mm
    terms = [
        "Deposit to commence: 100% of total material cost + 50% of additional costs (commercials, labour & "
        "logistics); remaining 50% of additional costs due on completion.",
        "Installation warranty: 2 years on workmanship; manufacturer warranties apply to equipment.",
        "Site inspection required before final quotation confirmation; a three-phase supply is assumed.",
        "Additional costs may apply for non-standard installations, roof reinforcement or site conditions.",
    ]
    for t in terms:
        c.setFillColor(GREEN)
        c.circle(M + 1.6 * mm, y - 1.3 * mm, 0.8 * mm, fill=1, stroke=0)
        y = para(c, t, M + 4.5 * mm, y + 1.2 * mm, W - 2 * M - 5 * mm, small) - 1 * mm
    y -= 4 * mm

    y = section(c, y, "13. Acceptance & Authorization")
    y = para(c, "By signing below, the client acknowledges acceptance of this proposal and the terms "
                "outlined above.", M, y, W - 2 * M, small)
    y -= 5 * mm
    colw = (W - 2 * M - 10 * mm) / 2
    for i, (who, rows_) in enumerate([("CLIENT", ["Name:", "Signature:", "Date:"]),
                                      ("FOR " + COMPANY, ["Name:", "Signature:", f"Date:  {DATE}"])]):
        x = M + i * (colw + 10 * mm)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(x, y, who)
        for j, r in enumerate(rows_):
            yy = y - 8 * mm - j * 7 * mm
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 8.5)
            c.drawString(x, yy, r)
            c.setStrokeColor(GREY)
            c.setLineWidth(0.4)
            c.line(x + max(20 * mm, c.stringWidth(r, "Helvetica", 8.5) + 2 * mm), yy - 1, x + colw, yy - 1)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Oblique", 8.5)
    c.drawCentredString(W / 2, 17.5 * mm,
                        f"Thank you for considering {COMPANY_NAME} for your solar energy needs.")


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "Proposal_20kW_80kWh_2026.10.26.pdf")
    c = canvas.Canvas(out, pagesize=A4)
    c.setTitle("20 kW / 80 kWh Hybrid Solar System Proposal")
    c.setAuthor(COMPANY_NAME)
    for fn in (page1, page2, page3, page4, page5):
        fn(c)
        c.showPage()
    c.save()
    print(out)


if __name__ == "__main__":
    main()
