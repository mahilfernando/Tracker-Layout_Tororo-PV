// Technical & commercial proposal (Word) for the Kampala Marriott rooftop PV.
// Run: python3 proposal_charts.py && node build_proposal.js
const fs = require("fs"), path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun, Header, Footer, AlignmentType,
  WidthType, ShadingType, BorderStyle, HeadingLevel, PageBreak, PageNumber, LevelFormat, TabStopType, VerticalAlign,
} = require("docx");

const D = JSON.parse(fs.readFileSync(path.join(__dirname, "proposal_fin.json")));
const M = JSON.parse(fs.readFileSync(path.join(__dirname, "monthly.json")));
const R = (...p) => path.join(__dirname, ...p);
const usd = (x) => Math.round(x).toLocaleString("en-US");
const NAVY = "14365D", BAND = "EEF2F6", RULE = "C9D0D8", MUTED = "5B6673", ACC = "C27A00";
const FONT = "Arial", REF = "P-KMH-PV-2026-001", DATE = "5 November 2026";
const PAGE_W = 11906, MARGIN = 1134, TW = PAGE_W - 2 * MARGIN;   // A4, 20 mm margins -> 9638

const bd = { style: BorderStyle.SINGLE, size: 4, color: RULE };
const borders = { top: bd, bottom: bd, left: bd, right: bd };
const T = (t, o = {}) => new TextRun({ text: t, ...o });
const B = (t) => new TextRun({ text: t, bold: true });
const P = (runs, o = {}) => new Paragraph({ children: Array.isArray(runs) ? runs : [T(runs)], spacing: { after: 120 }, ...o });
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [T(t)],
  border: { bottom: { style: BorderStyle.SINGLE, size: 10, color: NAVY, space: 4 } } });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [T(t)] });
const bullet = (runs) => new Paragraph({ numbering: { reference: "bul", level: 0 }, spacing: { after: 60 },
  children: Array.isArray(runs) ? runs : [T(runs)] });
const note = (t) => P([T(t, { size: 16, color: MUTED, italics: true })]);
const gap = () => new Paragraph({ children: [], spacing: { after: 80 } });
const pageBreak = () => new Paragraph({ children: [new PageBreak()] });
const caption = (t) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60, after: 200 },
  children: [T(t, { size: 16, color: MUTED, italics: true })] });
function img(file, type, wPx, hPx, maxW) {
  const w = Math.min(maxW, wPx), h = Math.round(hPx * w / wPx);
  return new Paragraph({ alignment: AlignmentType.CENTER, children: [new ImageRun({ type, data: fs.readFileSync(file),
    transformation: { width: w, height: h }, altText: { title: path.basename(file), description: path.basename(file), name: path.basename(file) } })] });
}
function cell(v, w, o = {}) {
  const runs = (Array.isArray(v) ? v : [v]).map((x) => typeof x === "string"
    ? new TextRun({ text: x, bold: o.bold, color: o.color, size: o.size || 18 }) : x);
  return new TableCell({ borders, width: { size: w, type: WidthType.DXA },
    shading: o.fill ? { fill: o.fill, type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 }, verticalAlign: VerticalAlign.CENTER,
    columnSpan: o.span, rowSpan: o.rowSpan,
    children: [new Paragraph({ alignment: o.align || AlignmentType.LEFT, children: runs })] });
}
function table(widths, rows, { header = true, aligns = [], totals = [], kv = false } = {}) {
  const al = (i) => ({ r: AlignmentType.RIGHT, c: AlignmentType.CENTER }[aligns[i]] || AlignmentType.LEFT);
  return new Table({ width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: widths,
    rows: rows.map((r, ri) => new TableRow({ tableHeader: header && ri === 0, cantSplit: true,
      children: r.map((c, ci) => {
        const head = header && ri === 0, tot = totals.includes(ri), key = kv && ci === 0;
        return cell(c, widths[ci], { bold: head || tot || key, color: head ? "FFFFFF" : (key ? NAVY : undefined),
          fill: head ? NAVY : (tot || key ? BAND : undefined), align: head ? AlignmentType.LEFT : al(ci) });
      }) })) });
}
const fin = { y1gen: D.gen[0], y1sav: D.cf[1], pb: D.pb, irr: D.irr, npv: D.npv, lcoe: D.lcoe, net25: D.net25, capex: D.capex };

// ------------------------------------------------------------------ cover
const cover = [
  new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { after: 120 }, children: [new ImageRun({ type: "png", data: fs.readFileSync(R("nilesun_logo.png")),
    transformation: { width: 120, height: 122 }, altText: { title: "Nile Sun Power logo", description: "Nile Sun Power Ltd logo", name: "logo" } })] }),
  img(R("hotel.jpg"), "jpg", 1080, 718, 600),
  new Paragraph({ spacing: { after: 360 }, border: { bottom: { style: BorderStyle.SINGLE, size: 24, color: NAVY, space: 1 } }, children: [] }),
  P([T("TECHNICAL & COMMERCIAL PROPOSAL", { size: 18, color: MUTED, characterSpacing: 40 })], { spacing: { before: 200, after: 80 } }),
  P([T("185.4 kWp Rooftop Solar PV System", { size: 48, bold: true, color: NAVY })], { spacing: { after: 60 } }),
  P([T("Kampala Marriott Hotel – Mezzanine Roof", { size: 28, color: "1B2430" })], { spacing: { after: 480 } }),
  table([2600, 4400], [
    ["Prepared for", "Kampala Marriott Hotel, Kampala, Uganda"],
    ["Prepared by", "Nile Sun Power Limited"],
    ["Proposal ref.", REF],
    ["Date", DATE],
    ["Validity", "30 days"],
  ], { header: false, kv: true }),
];

// ------------------------------------------------------------------ 1 executive summary
const kpi = (v, l) => [new TextRun({ text: v, bold: true, size: 28, color: NAVY }), new TextRun({ text: "", break: 1 }), new TextRun({ text: l, size: 15, color: MUTED })];
const exec = [
  H1("1. Executive Summary"),
  P("Nile Sun Power Limited is pleased to propose a turnkey 185.4 kWp grid-tied solar PV system on the mezzanine roof of the Kampala Marriott Hotel. The system generates clean electricity during the day that is used entirely by the hotel, reducing purchases from the grid. It operates with zero export and needs no battery storage."),
  new Table({ width: { size: TW, type: WidthType.DXA }, columnWidths: [2409, 2410, 2410, 2409], rows: [
    new TableRow({ children: [
      cell(kpi("185.4 kWp", "Solar capacity"), 2409, { align: AlignmentType.CENTER }),
      cell(kpi(`${usd(fin.y1gen)} kWh`, "Year-1 generation"), 2410, { align: AlignmentType.CENTER }),
      cell(kpi(`USD ${usd(fin.y1sav)}`, "Year-1 savings"), 2410, { align: AlignmentType.CENTER }),
      cell(kpi(`${fin.pb.toFixed(1)} years`, "Simple payback"), 2409, { align: AlignmentType.CENTER }) ] }),
    new TableRow({ children: [
      cell(kpi(`USD ${usd(fin.capex)}`, "Turnkey investment"), 2409, { align: AlignmentType.CENTER }),
      cell(kpi(`${(fin.irr * 100).toFixed(1)} %`, "Project IRR (25 yrs)"), 2410, { align: AlignmentType.CENTER }),
      cell(kpi(`USD ${usd(fin.npv)}`, "NPV @ 10 %"), 2410, { align: AlignmentType.CENTER }),
      cell(kpi(`USD ${usd(fin.net25)}`, "25-year net savings"), 2409, { align: AlignmentType.CENTER }) ] }),
  ] }),
  gap(),
  H2("Why this project makes sense"),
  bullet([B("Fast payback: "), T(`the investment is recovered in about ${fin.pb.toFixed(1)} years, and the system then keeps saving for more than 18 more years.`)]),
  bullet([B("Low-cost energy: "), T(`solar electricity costs about USD ${fin.lcoe.toFixed(3)}/kWh over the system life, below the grid tariff of about USD 0.070/kWh – and grid tariffs are expected to rise.`)]),
  bullet([B("Every unit is used: "), T("the hotel's daytime demand is far above the solar output, so 100 % of the energy offsets grid purchases. No export, no battery.")]),
  bullet([B("Sustainability: "), T("about 6.5 GWh of clean energy over 25 years, supporting the hotel's environmental commitments.")]),
  bullet([B("Turnkey delivery: "), T("design, supply, installation, commissioning and handover by a single contractor, in about 12–14 weeks.")]),
];

// ------------------------------------------------------------------ 2 site
const site = [
  H1("2. Site & Energy Profile"),
  table([3400, 6238], [
    ["Location", "Kampala Marriott Hotel, Kampala, Uganda (0°18'11.34\"N, 32°35'13.76\"E)"],
    ["Installation area", "Mezzanine-level flat concrete roof – architect's solar zone (drawing D18102-DD-A-104)"],
    ["Hotel consumption", "≈ 1,000,000 kWh per month (≈ 12 GWh per year)"],
    ["Grid supply", "UEDCL, time-of-use tariff; main LV switchboard with 1000 A incomer"],
    ["Solar resource", "Equatorial site – stable output all year, ≈ 1,480 kWh per kWp per year"],
  ], { header: false, kv: true }),
  gap(),
  img(R("..", "visual", "Marriott_roof_PV_overlay_zoom.png"), "png", 1052, 894, 430),
  caption("Figure 1 – Proposed PV array on the mezzanine roof (indicative visual)"),
];

// ------------------------------------------------------------------ 3 solution
const sol = [
  H1("3. Proposed Solution"),
  P("The system is a grid-tied rooftop PV plant feeding the hotel's main LV switchboard. Solar power is always used first; the grid supplies the balance. A zero-export controller measures the hotel's grid import and limits solar output so that no power flows back to the utility."),
  img(R("..", "sld", "PV_Block_Diagram.png"), "png", 4800, 1920, 620),
  caption("Figure 2 – System block diagram"),
  table([2600, 4300, 2738], [
    ["Component", "Description", "Size / Quantity"],
    ["Solar panels", "620 Wp bifacial N-type TOPCon, Tier-1, portrait, 10° tilt", "299 nos = 185.4 kWp"],
    ["Inverters", "Three-phase string inverters, 1100 V, multi-MPPT", "2 × 80 kW = 160 kW AC"],
    ["Mounting structure", "Ballasted aluminium system, no roof penetration", "7 tables (6 × 2P, 1 × 1P)"],
    ["AC combiner panel", "Joins both inverters; MCCBs, surge protection, roof isolator", "1 panel, 250 A"],
    ["Grid connection", "New 250 A way on the existing main LV switchboard", "1 feeder"],
    ["Monitoring & control", "Smart data logger, remote monitoring, zero-export control", "1 set"],
    ["Earthing & protection", "Array bonding, connection to building earth and lightning protection", "1 lot"],
  ]),
];

// ------------------------------------------------------------------ 4 energy
const energy = [
  H1("4. Energy Generation"),
  P(`The system is expected to generate about ${usd(fin.y1gen)} kWh in its first year – about 22,900 kWh per month or 750 kWh per day. Because Kampala lies on the equator, output is stable through the year: the best months (January–March) are only about 20 % above the lowest (June–July).`),
  img(R("gen_chart.png"), "png", 2160, 900, 600),
  caption("Figure 3 – Estimated monthly generation, year 1 (MWh)"),
  table([1100, 1200, 1300, 1600, 1500, 2938], [
    ["Month", "GHI (kWh/m²/day)", "Days", "Generation (kWh)", "kWh per day", "Share of year"],
    ...M.rows.map((r) => [r.m, r.ghi.toFixed(1), String(r.days), usd(r.kwh), usd(r.per_day), `${(r.share * 100).toFixed(1)} %`]),
    ["Total", "", "365", usd(M.rows.reduce((a, r) => a + r.kwh, 0)), usd(M.rows.reduce((a, r) => a + r.kwh, 0) / 365), "100 %"],
  ], { aligns: ["c", "r", "r", "r", "r", "r"], totals: [13] }),
  gap(),
  P("Almost all generation (≈ 98.6 %) falls in the shoulder tariff period (06:00–18:00), when the hotel's demand is high, so every kWh directly reduces grid purchases. Panel output degrades slowly (about 0.4 % per year); total generation over 25 years is about 6,477 MWh."),
];

// ------------------------------------------------------------------ 5 financial
const sens = D.sens;
const cfYears = [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20, 25];
const fin5 = [
  H1("5. Financial Analysis"),
  H2("5.1 Key assumptions"),
  table([4400, 5238], [
    ["Turnkey investment (excl. VAT)", `USD ${usd(fin.capex)}`],
    ["Avoided grid tariff (year 1)", "USD 0.070/kWh, escalating 2 % per year"],
    ["Generation, year 1 / degradation", `${usd(fin.y1gen)} kWh / 1 % in year 1, then 0.4 % per year`],
    ["Inverter replacement", "USD 9,600 in year 12"],
    ["Discount rate / analysis period", "10 % / 25 years"],
  ], { header: false, kv: true }),
  H2("5.2 Results"),
  table([4400, 5238], [
    ["Year-1 savings", `USD ${usd(fin.y1sav)}`],
    ["Simple payback", `${fin.pb.toFixed(1)} years`],
    ["Project IRR (25 years)", `${(fin.irr * 100).toFixed(1)} %`],
    ["Net present value @ 10 %", `USD ${usd(fin.npv)}`],
    ["Levelised cost of solar energy", `USD ${fin.lcoe.toFixed(3)}/kWh`],
    ["25-year net savings (after inverter replacement)", `USD ${usd(fin.net25)}`],
    ["Net gain after recovering the investment", `USD ${usd(fin.net25 - fin.capex)}`],
    ["Return on investment (25 years) / year-1 return", `${Math.round((fin.net25 - fin.capex) / fin.capex * 100)} % (${(fin.net25 / fin.capex).toFixed(1)}× the investment) / ${(fin.y1sav / fin.capex * 100).toFixed(1)} %`],
  ], { header: false, kv: true }),
  gap(),
  img(R("cashflow_chart.png"), "png", 2160, 900, 600),
  caption("Figure 4 – Cumulative cash flow (USD)"),
  pageBreak(),
  H2("5.3 Cash flow (selected years, USD)"),
  table([900, 1700, 1500, 1500, 1500, 2538], [
    ["Year", "Generation (kWh)", "Tariff (USD/kWh)", "Savings", "Net cash flow", "Cumulative"],
    ["0", "", "", "", `(${usd(fin.capex)})`, `(${usd(fin.capex)})`],
    ...cfYears.map((y) => [String(y), usd(D.gen[y - 1]), (D.tar * Math.pow(1.02, y - 1)).toFixed(3),
      usd(D.gen[y - 1] * D.tar * Math.pow(1.02, y - 1)), usd(D.cf[y]),
      D.cum[y] < 0 ? `(${usd(-D.cum[y])})` : usd(D.cum[y])]),
  ], { aligns: ["c", "r", "r", "r", "r", "r"] }),
  note("Year 12 includes the USD 9,600 inverter replacement. Values in brackets are negative (investment not yet recovered)."),
  H2("5.4 Tariff sensitivity"),
  table([2400, 2000, 1800, 1438, 2000], [
    ["Avoided tariff (USD/kWh)", "Year-1 savings (USD)", "Payback (years)", "IRR", "NPV @ 10 % (USD)"],
    ...sens.map((s) => [s[0].toFixed(2), usd(s[1]), s[2].toFixed(1), `${(s[3] * 100).toFixed(1)} %`, usd(s[4])]),
  ], { aligns: ["c", "r", "r", "r", "r"], totals: [3] }),
  P(`The project remains attractive across a wide tariff range. The break-even tariff (NPV = 0 at 10 %) is about USD ${D.breakeven.toFixed(3)}/kWh – roughly ${Math.round((1 - D.breakeven / 0.07) * 100)} % below today's tariff – which gives a strong safety margin.`, { spacing: { before: 120 } }),
  note("Financial figures are indicative and exclude O&M costs, which can be offered separately (see Section 7)."),
];

// ------------------------------------------------------------------ 6 scope / schedule
const scope = [
  H1("6. Scope of Works & Project Schedule"),
  H2("6.1 Included"),
  bullet("Detailed engineering: layout, single-line diagram, string design, cable sizing and protection."),
  bullet("Supply of all equipment: PV modules, inverters, mounting structure, DC and AC systems, monitoring and zero-export control."),
  bullet("Transport, customs clearing and delivery to site in Kampala."),
  bullet("Installation, cabling, earthing and connection to the main LV switchboard."),
  bullet("Testing, commissioning, as-built documentation, operator training and handover."),
  H2("6.2 Client responsibilities & exclusions"),
  bullet("Roof access, secure storage area, and power and water during installation."),
  bullet("A spare 250 A way on the main LV switchboard and access to the LV room."),
  bullet("Excluded: roof structural strengthening or waterproofing, battery storage, utility or permit fees, VAT and statutory levies."),
  H2("6.3 Indicative schedule"),
  table([3800, 2400, 3438], [
    ["Phase", "Timing", "Key output"],
    ["Detailed design & approvals", "Weeks 1–3", "Approved drawings, structural sign-off"],
    ["Procurement & shipping", "Weeks 2–10", "Equipment delivered to site"],
    ["Installation", "Weeks 10–13", "Structure, modules, cabling, panels"],
    ["Testing & commissioning", "Weeks 13–14", "System energised, handover"],
  ]),
];

// ------------------------------------------------------------------ 7 warranties
const warr = [
  H1("7. Warranties & After-Sales Support"),
  table([3800, 5838], [
    ["Item", "Warranty"],
    ["PV modules", "12-year product warranty; 30-year linear power warranty"],
    ["Inverters", "5 years (extendable)"],
    ["Mounting structure", "10 years"],
    ["Workmanship", "2 years from commissioning"],
  ]),
  gap(),
  P("Optional operation & maintenance (O&M) services – panel cleaning, periodic inspections, remote performance monitoring and reporting – can be provided under a separate annual agreement."),
];

// ------------------------------------------------------------------ 8 commercial offer (one page)
const q = [
  H1("8. Commercial Offer – Quotation"),
  table([2400, 2419, 2400, 2419], [
    ["Quotation No.", "Q-KMH-PV-2026-001", "Date", "05-11-2026"],
    ["Revision", "A", "Valid until", "05-12-2026 (30 days)"],
    ["Client", "Kampala Marriott Hotel", "Supplier", "Nile Sun Power Limited"],
    ["Address", "Kampala, Uganda", "Contact", "Mahil Fernando"],
    ["Project", "185.4 kWp rooftop PV, mezzanine roof", "Mobile / Email", "+94 773 55 96 82 · mahil@windforce.lk"],
  ], { header: false, kv: false }),
  gap(),
  new Table({ width: { size: TW, type: WidthType.DXA }, columnWidths: [600, 5200, 900, 900, 2038], rows: [
    new TableRow({ tableHeader: true, children: ["No.", "Scope of supply & works", "Qty", "Unit", "Total Price (USD)"].map((h, i) =>
      cell(h, [600, 5200, 900, 900, 2038][i], { bold: true, color: "FFFFFF", fill: NAVY, align: i === 1 ? AlignmentType.LEFT : AlignmentType.CENTER })) }),
    ...[["PV modules – 620 Wp bifacial N-type TOPCon (Tier-1)", "299", "nos"],
        ["String inverters – 80 kW, 1100 V, multi-MPPT", "2", "nos"],
        ["Ballasted aluminium mounting structure, 10° tilt", "1", "lot"],
        ["DC system – PV cable, connectors, string isolators, cable tray", "1", "lot"],
        ["AC system – combiner panel, MCCBs, cabling to main LV switchboard", "1", "lot"],
        ["Smart data logger, remote monitoring & zero-export control", "1", "set"],
        ["Earthing & lightning protection integration", "1", "lot"],
        ["Installation, testing & commissioning", "1", "lot"],
        ["Transport, logistics & customs clearing to site", "1", "lot"]].map((it, i) => new TableRow({ cantSplit: true, children: [
          cell(String(i + 1), 600, { align: AlignmentType.CENTER }), cell(it[0], 5200), cell(it[1], 900, { align: AlignmentType.CENTER }),
          cell(it[2], 900, { align: AlignmentType.CENTER }),
          ...(i === 0 ? [new TableCell({ borders, width: { size: 2038, type: WidthType.DXA }, rowSpan: 9, verticalAlign: VerticalAlign.CENTER,
            children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: `USD ${usd(fin.capex)}`, bold: true, size: 32, color: ACC })] })] })] : []),
        ] })),
    new TableRow({ children: [
      cell("TOTAL TURNKEY EPC PRICE (excluding VAT and other applicable taxes)", 7600, { bold: true, fill: BAND, span: 4, align: AlignmentType.RIGHT }),
      cell(`USD ${usd(fin.capex)}`, 2038, { bold: true, fill: BAND, color: NAVY, align: AlignmentType.CENTER, size: 20 }) ] }),
  ] }),
  note("Equivalent to USD 0.65 per Wp. Amount in words: One hundred twenty-one thousand one hundred fifteen US Dollars only."),
  table([2600, 7038], [
    ["Price basis", "Turnkey EPC – delivered, installed and commissioned at site, Kampala. Currency: USD."],
    ["Payment terms", "30 % advance with purchase order · 60 % on delivery of main equipment to site · 10 % on commissioning"],
    ["Taxes", "Prices exclude VAT, withholding tax and other statutory levies, charged as applicable."],
    ["Delivery", "Equipment 8–10 weeks from PO and advance; installation and commissioning ≈ 4 weeks after delivery."],
    ["Warranties", "Modules 12-yr product / 30-yr power · inverters 5 yrs · structure 10 yrs · workmanship 2 yrs"],
    ["Notes", "Final quantities subject to detailed engineering and site survey. Exclusions as listed in Section 6.2."],
  ], { header: false, kv: true }),
  gap(),
  new Table({ width: { size: TW, type: WidthType.DXA }, columnWidths: [4819, 4819], rows: [new TableRow({ children: [
    new TableCell({ borders: { top: bd, bottom: bd, left: bd, right: bd }, width: { size: 4819, type: WidthType.DXA }, margins: { top: 100, bottom: 100, left: 120, right: 120 },
      children: [P([B("For Nile Sun Power Limited")]), P(" "), P(" "), P([T("Signature / Name / Date", { size: 16, color: MUTED })])] }),
    new TableCell({ borders: { top: bd, bottom: bd, left: bd, right: bd }, width: { size: 4819, type: WidthType.DXA }, margins: { top: 100, bottom: 100, left: 120, right: 120 },
      children: [P([B("Accepted by Kampala Marriott Hotel")]), P(" "), P(" "), P([T("Signature / Name / Date", { size: 16, color: MUTED })])] }),
  ] })] }),
];

// ------------------------------------------------------------------ 9 next steps
const nextS = [
  H1("9. Next Steps"),
  new Paragraph({ numbering: { reference: "num", level: 0 }, spacing: { after: 60 }, children: [T("Review of this proposal and clarification meeting with the hotel's engineering team.")] }),
  new Paragraph({ numbering: { reference: "num", level: 0 }, spacing: { after: 60 }, children: [T("Site survey: roof condition, LV switchboard, cable route and inverter location.")] }),
  new Paragraph({ numbering: { reference: "num", level: 0 }, spacing: { after: 60 }, children: [T("Confirmation of the tariff from recent utility bills and structural review of the roof.")] }),
  new Paragraph({ numbering: { reference: "num", level: 0 }, spacing: { after: 60 }, children: [T("Purchase order and advance payment – project start.")] }),
  gap(),
  P("We thank the Kampala Marriott Hotel for the opportunity and look forward to delivering this project together."),
  P([B("Contact: "), T("Mahil Fernando, Nile Sun Power Limited · +94 773 55 96 82 · mahil@windforce.lk")]),
];

const doc = new Document({
  creator: "Nile Sun Power Limited", title: "Technical & Commercial Proposal – 185.4 kWp Rooftop Solar PV",
  features: { updateFields: true },
  styles: {
    default: { document: { run: { font: FONT, size: 19 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 28, bold: true, color: NAVY }, paragraph: { spacing: { before: 120, after: 200 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 22, bold: true, color: NAVY }, paragraph: { spacing: { before: 220, after: 100 }, keepNext: true, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [
    { reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 260 } } } }] },
    { reference: "num", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 300 } } } }] },
  ] },
  sections: [
    { properties: { page: { size: { width: PAGE_W, height: 16838 }, margin: { top: 850, bottom: 850, left: MARGIN, right: MARGIN } } }, children: cover },
    { properties: { page: { size: { width: PAGE_W, height: 16838 }, margin: { top: 1300, bottom: 1134, left: MARGIN, right: MARGIN, header: 600, footer: 600 } } },
      headers: { default: new Header({ children: [new Paragraph({ tabStops: [{ type: TabStopType.RIGHT, position: TW }],
        border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: RULE, space: 4 } },
        children: [new ImageRun({ type: "png", data: fs.readFileSync(R("nilesun_logo.png")), transformation: { width: 34, height: 34 },
          altText: { title: "Nile Sun Power logo", description: "logo", name: "hlogo" } }),
          T("  Nile Sun Power Limited", { size: 16, bold: true, color: NAVY }), T(`\tKampala Marriott Hotel – Rooftop Solar PV · ${REF}`, { size: 15, color: MUTED })] })] }) },
      footers: { default: new Footer({ children: [new Paragraph({ tabStops: [{ type: TabStopType.RIGHT, position: TW }], children: [
        T("Nile Sun Power Limited · Confidential", { size: 15, color: MUTED }),
        new TextRun({ children: ["\tPage ", PageNumber.CURRENT, " of ", PageNumber.TOTAL_PAGES], size: 15, color: MUTED })] })] }) },
      children: [...exec, pageBreak(), ...site, pageBreak(), ...sol, pageBreak(), ...energy, pageBreak(), ...fin5, pageBreak(),
                 ...scope, gap(), ...warr, pageBreak(), ...q, pageBreak(), ...nextS] },
  ],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(R("Kampala_Marriott_PV_Proposal.docx"), b); console.log("written"); });
