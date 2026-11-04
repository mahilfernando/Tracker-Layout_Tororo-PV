// Word version of the rooftop PV design & cost report. Run: python3 calc.py && node build_docx.js
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun, Header, Footer,
  AlignmentType, WidthType, ShadingType, BorderStyle, HeadingLevel, PageBreak, PageNumber,
  LevelFormat, TableOfContents, TabStopType, VerticalAlign,
} = require("docx");

const D = JSON.parse(fs.readFileSync(path.join(__dirname, "calc.json")));
const img = (f) => fs.readFileSync(path.join(__dirname, f));
const usd = (x) => Math.round(x).toLocaleString("en-US");
const f1 = (x) => x.toFixed(1);

const NAVY = "14365D", BAND = "EEF2F6", RULE = "C9D0D8", MUTED = "5B6673";
const FONT = "Arial";
const DOC_NO = "PV-RPT-D18102-001", REV = "B", DATE = "4 November 2026";
const PAGE_W = 11906, MARGIN = 1134;            // A4, 20 mm margins
const TW = PAGE_W - 2 * MARGIN;                 // 9638 DXA text width

const border = { style: BorderStyle.SINGLE, size: 4, color: RULE };
const borders = { top: border, bottom: border, left: border, right: border };

function P(text, opts = {}) {
  const runs = Array.isArray(text) ? text : [new TextRun({ text, ...(opts.run || {}) })];
  return new Paragraph({ children: runs, spacing: { after: 120 }, ...opts.para });
}
const B = (t) => new TextRun({ text: t, bold: true });
const T = (t) => new TextRun({ text: t });
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)],
  border: { bottom: { style: BorderStyle.SINGLE, size: 10, color: NAVY, space: 4 } } });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] });
const bullet = (runs) => new Paragraph({ numbering: { reference: "bul", level: 0 }, children: Array.isArray(runs) ? runs : [T(runs)], spacing: { after: 60 } });
const num = (ref, runs) => new Paragraph({ numbering: { reference: ref, level: 0 }, children: Array.isArray(runs) ? runs : [T(runs)], spacing: { after: 60 } });
const note = (t) => P(t, { run: { size: 16, color: MUTED } });
const pageBreak = () => new Paragraph({ children: [new PageBreak()] });

function cell(text, w, o = {}) {
  const runs = (Array.isArray(text) ? text : [text]).map((t) =>
    typeof t === "string" ? new TextRun({ text: t, bold: o.bold, color: o.color, size: o.size || 18 }) : t);
  return new TableCell({
    borders, width: { size: w, type: WidthType.DXA },
    shading: o.fill ? { fill: o.fill, type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({ alignment: o.align || AlignmentType.LEFT, children: runs })],
  });
}
// rows: array of arrays; first row header if header=true; aligns: array of 'l'|'r'|'c'
function table(widths, rows, { header = true, aligns = [], totalRows = [], kv = false } = {}) {
  const al = (i) => ({ r: AlignmentType.RIGHT, c: AlignmentType.CENTER }[aligns[i]] || AlignmentType.LEFT);
  return new Table({
    width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    columnWidths: widths,
    rows: rows.map((r, ri) => new TableRow({
      tableHeader: header && ri === 0,
      cantSplit: true,
      children: r.map((c, ci) => {
        const isHead = header && ri === 0;
        const isTot = totalRows.includes(ri);
        const isKey = kv && ci === 0;
        return cell(c, widths[ci], {
          bold: isHead || isTot, color: isHead ? NAVY : (isKey ? MUTED : undefined),
          fill: isHead || isTot || isKey ? BAND : undefined, align: isHead ? AlignmentType.LEFT : al(ci),
        });
      }),
    })),
  });
}
const gap = () => new Paragraph({ children: [], spacing: { after: 120 } });
const caption = (t) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60, after: 200 },
  children: [new TextRun({ text: t, size: 16, color: MUTED, italics: true })] });
function picture(file, type, wPx, hPx, maxW) {
  const w = Math.min(maxW, wPx), h = Math.round(hPx * w / wPx);
  return new Paragraph({ alignment: AlignmentType.CENTER, children: [new ImageRun({ type, data: img(file),
    transformation: { width: w, height: h }, altText: { title: file, description: file, name: file } })] });
}

const KWP = D.KWP, Y1 = D.y1_gen;

// ---------------- COVER ----------------
const cover = [
  picture("hotel.jpg", "jpg", 1080, 718, 642),
  new Paragraph({ spacing: { before: 0, after: 400 }, border: { bottom: { style: BorderStyle.SINGLE, size: 24, color: NAVY, space: 1 } }, children: [] }),
  new Paragraph({ spacing: { before: 200, after: 80 }, children: [new TextRun({ text: "TECHNICAL REPORT · RENEWABLE ENERGY", size: 18, color: MUTED, characterSpacing: 40 })] }),
  new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: "Rooftop Solar PV System", size: 52, bold: true, color: NAVY, font: FONT })] }),
  new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: "Design Basis & Cost Estimate", size: 52, bold: true, color: NAVY, font: FONT })] }),
  new Paragraph({ spacing: { after: 480 }, children: [new TextRun({ text: "Marriott Hotel – Mezzanine Roof (Drawing D18102-DD-A-104)", size: 26 })] }),
  table([2600, 4400], [
    ["Document No.", DOC_NO], ["Revision", `${REV} – Issued for review`], ["Date", DATE],
    ["Client", "Tororo PV Power Company Limited"],
    ["System capacity", `${f1(KWP)} kWp DC / ${D.AC.toFixed(0)} kW AC, grid-tied, no battery`],
  ], { header: false, kv: true }),
];

// ---------------- DOC CONTROL ----------------
const control = [
  H1("Document Control"),
  table([900, 1700, 2638, 1450, 1450, 1500], [
    ["Rev", "Date", "Description", "Prepared", "Checked", "Approved"],
    ["A", "3 November 2026", "Issued for review", "", "", ""],
    ["B", DATE, "Inverters 2 × 80 kW; solar zone limited to architect's drawing", "", "", ""],
  ], { aligns: ["c"] }),
  H2("Reference documents"),
  table([3400, 6238], [
    ["Reference", "Title"],
    ["D18102-DD-A-104", "Mezzanine floor plan incl. roof PV zones (architect)"],
    ["PV-LAY-D18102-002", "PV layout with Enerack ballast structure, 10° tilt"],
    ["EPJ-26110401 V1.0", "Enerack mounting structure drawings (2P and 1P tables)"],
  ]),
  H2("Contents"),
  new TableOfContents("Contents", { hyperlink: true, headingStyleRange: "1-1" }),
  note("Right-click the table of contents and choose Update Field if page numbers are not shown."),
];

// ---------------- 1 EXEC SUMMARY ----------------
const kpi = table([2409, 2410, 2410, 2409], [
  [[new TextRun({ text: `${f1(KWP)} kWp`, bold: true, size: 30, color: NAVY })],
   [new TextRun({ text: `${usd(Y1 / 1000)} MWh`, bold: true, size: 30, color: NAVY })],
   [new TextRun({ text: `USD ${usd(D.capex / 1000)}k`, bold: true, size: 30, color: NAVY })],
   [new TextRun({ text: `${f1(D.payback)} yrs`, bold: true, size: 30, color: NAVY })]],
  [`DC capacity (${D.N} × ${D.P} Wp)`, "Year-1 generation", `Budget EPC cost (${D.usd_wp.toFixed(2)} USD/Wp)`, "Simple payback"],
], { header: false, aligns: ["c", "c", "c", "c"] });

const exec = [
  H1("1. Executive Summary"),
  P("This report sets out the design basis, layout, energy yield and budget cost for a grid-tied rooftop solar photovoltaic (PV) system on the mezzanine-level roof of the Marriott Hotel, as shown on architectural drawing D18102-DD-A-104. The system has no battery storage and supplies the hotel's own load behind the utility meter."),
  kpi, gap(),
  H2("Key findings"),
  bullet([B("Capacity. "), T(`The solar zones on the architect's drawing (≈1,150 m² gross) accommodate ${D.N} modules of ${D.P} Wp in 13 rows of 23, giving ${f1(KWP)} kWp at 10° tilt with 800 mm maintenance aisles and 1.0 m edge setbacks.`)]),
  bullet([B("Self-consumption. "), T("The hotel uses about 1,000,000 kWh per month (average demand ≈1.37 MW). The PV peak output (≈160 kW AC) is about one-tenth of the daytime load, so 100 % of the solar energy is used on site. No energy is exported and no battery is needed.")]),
  bullet([B("Energy and savings. "), T(`Year-1 generation is about ${usd(Y1 / 1000)} MWh (${(D.share * 100).toFixed(1)} % of annual consumption). At an avoided tariff of USD ${D.TARIFF.toFixed(2)}/kWh this saves about USD ${usd(D.y1_sav)} in year 1.`)]),
  bullet([B("Cost and return. "), T(`The budget turnkey (EPC) cost is USD ${usd(D.capex)} excluding taxes, including 7 % contingency. Simple payback is ${f1(D.payback)} years, project IRR ${(D.irr * 100).toFixed(0)} % and 25-year NPV (10 %) USD ${usd(D.npv)}. The levelised cost of solar energy is about USD ${D.lcoe.toFixed(3)}/kWh.`)]),
  bullet([B("Path to 500 kWp. "), T("The architect's solar zone limits this roof to 185.4 kWp. The balance of ≈315 kWp would need other roof areas or car-park canopies (Section 8).")]),
  H2("Recommendation"),
  P(`Proceed with the ${f1(KWP)} kWp mezzanine roof system as Phase 1, subject to (i) a structural check of the slab for the ballasted structure (dead load, ballast and wind uplift), and (ii) confirmation of the avoided tariff from recent utility bills. In parallel, survey other roof areas and the car park for Phase 2.`),
];

// ---------------- 2 SITE & BASIS ----------------
const basis = [
  H1("2. Site and Design Basis"),
  H2("2.1 Site and load"),
  table([3400, 6238], [
    ["Facility", "Marriott Hotel – twin towers with podium; PV on the mezzanine-level roof"],
    ["Location", "Uganda, equatorial (≈0–1° N); irradiation basis to be confirmed with site coordinates"],
    ["Roof", "Flat reinforced-concrete slab, single level, with parapet; architect's two PV zones (29.39 m wide)"],
    ["Annual electricity consumption", "≈12,000,000 kWh (≈1,000,000 kWh/month)"],
    ["Average / daytime demand", "≈1,370 kW / ≈1,700 kW (hotel load profile assumed)"],
    ["Grid connection", "Behind-the-meter, LV main switchboard; zero-export control"],
    ["Energy storage", "None"],
  ], { header: false, kv: true }),
  H2("2.2 Design criteria"),
  table([2900, 3638, 3100], [
    ["Parameter", "Value", "Basis"],
    ["Module", "620 Wp bifacial TOPCon, 2382 × 1134 × 30 mm, ≈33 kg", "Current Tier-1 mainstream size"],
    ["Orientation / mounting", "Portrait, 2 modules high (2P) per table", "Matches roof depth"],
    ["Tilt", "10°", "Low wind load, self-cleaning by rain"],
    ["Table depth on plan", "4,711 mm (2P); 2,346 mm (1P)", "2 × 2382 + 20 mm, × cos 10°"],
    ["Module clamp gap", "20 mm", "Mid-clamp"],
    ["Aisle between tables", "800 mm", "No inter-row shading 09:00–15:00 all year; walkway for cleaning"],
    ["Edge setback", "1,000 mm (east side 1,742 mm)", "Wind edge zone, safe access; clear of roof opening"],
    ["Inverter DC voltage", "1,100 V max", "Standard C&I string inverter"],
    ["Design standards", "IEC 62548, IEC 60364-7-712, IEC 61215/61730, IEC 62109, IEC 62305", "PV array, wiring, modules, inverters, lightning"],
  ]),
];

// ---------------- 3 LAYOUT ----------------
const layout = [
  H1("3. PV Array Layout"),
  P("The array occupies only the solar zones shown on drawing D18102-DD-A-104. Each row holds 23 modules on Enerack R80 rails 26,630 mm long, supported by 11 frames per table at 2,600 mm centres. The upper block carries two 2P tables and one 1P table; the lower block carries four 2P tables."),
  picture("layout.png", "png", 1386, 1790, 400),
  caption("Figure 1 – PV module layout on the mezzanine roof"),
  table([4238, 2000, 1000, 1200, 1200], [
    ["Zone", "Tables", "Rows", "Modules", "kWp"],
    ["Upper block", "2 × 2P + 1 × 1P", "5", "115", "71.3"],
    ["Lower block", "4 × 2P", "8", "184", "114.1"],
    ["Total", "7 tables", "13", String(D.N), f1(KWP)],
  ], { aligns: ["l", "l", "r", "r", "r"], totalRows: [3] }),
  note("Mounting structure: Enerack ballast system, drawing EPJ-26110401 V1.0 – 66 frames for 2P tables and 11 frames for 1P tables, 26 rail lines. Module area 807 m²."),
];

// ---------------- 4 ELECTRICAL ----------------
const elec = [
  H1("4. Electrical Design"),
  H2("4.1 Configuration"),
  table([2638, 2400, 2800, 1800], [
    ["Item", "Inverter INV-01", "Inverter INV-02", "Total"],
    ["Rated AC power", "80 kW", "80 kW", "160 kW"],
    ["Strings", "8 × 19 modules", "3 × 19 + 5 × 18 modules", "16 strings"],
    ["Modules", "152", "147", String(D.N)],
    ["DC capacity", "94.2 kWp", "91.1 kWp", `${f1(KWP)} kWp`],
    ["DC/AC ratio", "1.18", "1.14", "1.16"],
  ]),
  H2("4.2 String voltage check"),
  table([4438, 1300, 2200, 1700], [
    ["Check", "Value", "Limit", "Result"],
    ["Max. open-circuit voltage, 19 modules at 12 °C (Voc ≈ 50.2 V)", "954 V", "≤ 1,100 V", "OK"],
    ["Min. MPP voltage, 18 modules at 65 °C (Vmp ≈ 36.2 V)", "652 V", "≥ MPPT minimum (≈200 V)", "OK"],
    ["String current (Isc ≈ 16.1 A, × 1.25 bifacial)", "≈20 A", "MPPT input rating", "OK, max. 2 strings per MPPT"],
  ], { aligns: ["l", "r"] }),
  note("Module electrical values are typical for 620 Wp TOPCon modules. Re-check against the selected module and inverter datasheets."),
  H2("4.3 Single-line arrangement"),
  num("sld", "PV strings → 6 mm² double-insulated PV cable in UV-resistant trunking → inverters on the roof in a shaded, ventilated location."),
  num("sld", "Inverters (400 V, 3-phase) → AC combiner panel with outgoing 250 A MCCB, Type II SPD and roof isolator."),
  num("sld", "AC combiner panel → 4C × 120 mm² Cu XLPE/SWA (≈80 m, confirm route) → dedicated 250 A way on the main LV switchboard."),
  num("sld", "Zero-export controller with CTs on the incomer limits PV output so the site never exports."),
  num("sld", "Earthing: array frames bonded to the building earth and integrated with the lightning protection system (IEC 62305)."),
];

// ---------------- 5 YIELD ----------------
const yieldS = [
  H1("5. Energy Yield"),
  table([3800, 5838], [
    ["Specific yield (year 1, incl. losses)", `${D.SY.toLocaleString("en-US")} kWh/kWp/yr`],
    ["Performance ratio assumed", "≈ 0.80 (temperature, soiling, cabling, inverter, availability)"],
    ["Year-1 generation", `${usd(Y1)} kWh (≈ ${usd(Y1 / 12)} kWh per month)`],
    ["Degradation", "1.0 % in year 1, then 0.4 %/yr"],
    ["25-year generation", `${usd(D.gen25 / 1000)} MWh`],
    ["Self-consumption", "100 % (PV peak ≈160 kW vs. daytime load ≈1,700 kW)"],
    ["Share of hotel consumption", `${(D.share * 100).toFixed(1)} %`],
  ], { header: false, kv: true }),
  gap(),
  P("At the equator, day length is nearly constant, so monthly output is fairly even. It is lowest in the main rainy seasons (March–May and October–November). Because the hotel load exceeds the PV output in every hour, cloudy days reduce savings but never cause curtailment."),
  note("The yield figure is a desktop estimate. A PVsyst simulation with the exact site coordinates is recommended at detailed design."),
];

// ---------------- 6 BOQ ----------------
const boqRows = [["No.", "Description", "Qty", "Rate", "Amount (USD)"]];
D.boq.forEach((b, i) => boqRows.push([String(i + 1), b[0], b[1], b[2], usd(b[3])]));
const nB = boqRows.length;
boqRows.push(["", "Sub-total", "", "", usd(D.sub)]);
boqRows.push(["", "Contingency (7 %)", "", "", usd(D.cont)]);
boqRows.push(["", "Total budget EPC cost (excluding taxes)", "", "", usd(D.capex)]);
boqRows.push(["", "Specific cost", "", "", `${D.usd_wp.toFixed(3)} USD/Wp`]);
const boq = [
  H1("6. Cost Estimate (Bill of Quantities)"),
  P("Budget turnkey (EPC) estimate in US dollars, based on 2026 East African market prices for commercial rooftop systems. Accuracy ±15 %."),
  table([600, 4838, 1300, 1500, 1400], boqRows, { aligns: ["c", "l", "c", "r", "r"], totalRows: [nB, nB + 2] }),
  note(`Excludes VAT, withholding tax and import duties (solar equipment is generally zero-rated or exempt in Uganda; confirm with URA), roof waterproofing upgrades, structural strengthening if required, and utility charges. Annual O&M is estimated at USD ${usd(D.om0)}/yr (≈1.2 % of capex), escalating at 3 %/yr. The Enerack structure quote (≈USD 9,500 CIF Mombasa for 299 modules) falls within item 3, which also covers ballast blocks, transport and pads.`),
];

// ---------------- 7 FINANCIAL ----------------
const sensRows = [["Avoided tariff (USD/kWh)", "Payback (yrs)", "IRR", "NPV @ 10 % (USD)"]];
D.sens.forEach((s) => sensRows.push([s[0].toFixed(2), f1(s[1]), `${(s[2] * 100).toFixed(0)} %`, usd(s[3])]));
const cfRows = [["Year", "Generation (MWh)", "Tariff (USD/kWh)", "Savings", "O&M", "Replacement", "Net cash flow", "Cumulative"]];
cfRows.push(["0", "", "", "", "", "", usd(-D.capex), usd(-D.capex)]);
D.rows.filter((r) => [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25].includes(r[0])).forEach((r) =>
  cfRows.push([String(r[0]), f1(r[1] / 1000), r[2].toFixed(3), usd(r[3]), usd(r[4]), r[5] ? usd(r[5]) : "–", usd(r[6]), usd(r[7])]));
const fin = [
  H1("7. Financial Analysis"),
  table([4400, 5238], [
    ["Investment (EPC, excluding taxes)", `USD ${usd(D.capex)}`],
    ["Avoided grid tariff (year 1) / escalation", `USD ${D.TARIFF.toFixed(2)}/kWh / ${(D.ESC * 100).toFixed(0)} % per year`],
    ["Year-1 savings", `USD ${usd(D.y1_sav)}`],
    ["Inverter replacement (year 12)", "USD 9,600"],
    ["Simple payback", `${f1(D.payback)} years`],
    ["Project IRR (25 years, unlevered)", `${(D.irr * 100).toFixed(1)} %`],
    ["NPV at 10 % discount rate", `USD ${usd(D.npv)}`],
    ["Levelised cost of energy (LCOE)", `USD ${D.lcoe.toFixed(3)}/kWh`],
    ["25-year cumulative savings, net of O&M", `USD ${usd(D.cum[D.cum.length - 1] + D.capex)}`],
  ], { header: false, kv: true }),
  gap(),
  picture("chart.png", "png", 1920, 753, 600),
  caption("Figure 2 – Cumulative net cash flow (USD)"),
  H2("Tariff sensitivity"),
  table([2800, 2200, 2000, 2638], sensRows, { aligns: ["c", "r", "r", "r"], totalRows: [3] }),
  H2("Annual cash flow (selected years, USD)"),
  table([700, 1300, 1200, 1200, 1000, 1338, 1400, 1500], cfRows, { aligns: ["c", "r", "r", "r", "r", "r", "r", "r"] }),
];

// ---------------- 8 EXPANSION ----------------
const exp = [
  H1("8. Expansion Options"),
  P("The target of about 500 kWp exceeds what the architect's solar zone on the mezzanine roof can hold. Because the hotel load is around ten times the PV output, every additional kWp would also be fully self-consumed, so expansion can be added in stages without a battery."),
  table([2900, 1300, 1400, 1700, 2338], [
    ["Option", "Capacity", "Year-1 energy", "Budget cost (USD)", "Remarks"],
    ["Phase 1 – mezzanine roof (this report)", "185.4 kWp", "274 MWh", usd(D.capex), "Ready for detailed design"],
    ["Other roofs (left podium roof ≈370 m², lobby roof)", "≈ 65–120 kWp", "≈ 95–180 MWh", "≈ 38,000–68,000", "Survey and structural check required"],
    ["Car-park solar canopies", "≈ 150–250 kWp", "≈ 220–370 MWh", "≈ 0.75–0.85 USD/Wp", "Adds shaded parking; steel canopy cost"],
    ["Indicative total", "≈ 400–555 kWp", "≈ 590–825 MWh", "", "≈ 5–7 % of hotel consumption"],
  ], { aligns: ["l", "r", "r", "r", "l"], totalRows: [4] }),
];

// ---------------- 9 ASSUMPTIONS ----------------
const assum = [
  H1("9. Assumptions, Exclusions and Next Steps"),
  H2("9.1 Key assumptions"),
  bullet("Roof geometry is taken from drawing D18102-DD-A-104; PV is limited to the architect's solar zones."),
  bullet("The roof slab can carry the ballasted structure and wind loads without strengthening, subject to verification by the structural engineer."),
  bullet("The hotel load is about 1,000,000 kWh per month with a continuous daytime demand well above 160 kW."),
  bullet(`The avoided tariff is USD ${D.TARIFF.toFixed(2)}/kWh escalating at ${(D.ESC * 100).toFixed(0)} %/yr, to be confirmed from the latest utility bills.`),
  bullet("Prices are 2026 East African market levels in USD, excluding taxes."),
  H2("9.2 Exclusions"),
  bullet("Battery storage, diesel-generator synchronisation and export metering."),
  bullet("Roof waterproofing renewal, structural strengthening, and civil works to the LV room."),
  bullet("Utility network upgrades, permit fees and financing costs."),
  H2("9.3 Recommended next steps"),
  num("next", "Obtain 12 months of utility bills or interval-meter data and confirm the tariff structure."),
  num("next", "Obtain the Enerack structural calculation (loads per foot, ballast weights) and have the building structural engineer approve the roof load."),
  num("next", "Confirm the inverter location, AC cable route and spare way on the main LV switchboard."),
  num("next", "Run a PVsyst simulation with site coordinates and the selected module and inverter datasheets."),
  num("next", "Issue the tender package (layout, single-line diagram, specification, BOQ) to qualified EPC contractors."),
  num("next", "Start the Phase 2 survey of other roofs and the car park."),
];

const doc = new Document({
  features: { updateFields: true },
  creator: "Tororo PV Power Company Limited",
  title: "Rooftop Solar PV System – Design Basis & Cost Estimate",
  styles: {
    default: { document: { run: { font: FONT, size: 19 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 28, bold: true, color: NAVY },
        paragraph: { spacing: { before: 120, after: 200 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 22, bold: true, color: NAVY },
        paragraph: { spacing: { before: 240, after: 100 }, keepNext: true, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [
    { reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 400, hanging: 260 } } } }] },
    ...["sld", "next"].map((ref) => ({ reference: ref, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.",
      alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 300 } } } }] })),
  ] },
  sections: [
    { properties: { page: { size: { width: PAGE_W, height: 16838 }, margin: { top: 850, bottom: 850, left: MARGIN, right: MARGIN } } },
      children: cover },
    { properties: { page: { size: { width: PAGE_W, height: 16838 }, margin: { top: 1300, bottom: 1134, left: MARGIN, right: MARGIN, header: 600, footer: 600 } } },
      headers: { default: new Header({ children: [new Paragraph({
        tabStops: [{ type: TabStopType.RIGHT, position: TW }],
        border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: RULE, space: 4 } },
        children: [new TextRun({ text: "Marriott Hotel – Rooftop Solar PV", size: 15, color: MUTED }),
                   new TextRun({ text: `\t${DOC_NO} Rev ${REV}`, size: 15, color: MUTED })] })] }) },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
        children: [new TextRun({ children: ["Page ", PageNumber.CURRENT, " of ", PageNumber.TOTAL_PAGES], size: 15, color: MUTED })] })] }) },
      children: [
        ...control, pageBreak(), ...exec, pageBreak(), ...basis, pageBreak(), ...layout, pageBreak(),
        ...elec, pageBreak(), ...yieldS, pageBreak(), ...boq, pageBreak(), ...fin, pageBreak(), ...exp, gap(), ...assum,
      ] },
  ],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(path.join(__dirname, "Rooftop_PV_Report.docx"), buf);
  console.log("written");
});
