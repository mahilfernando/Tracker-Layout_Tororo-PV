// Small summary table to sit under the block diagram in a Word document
const fs = require("fs"), path = require("path");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun, WidthType, ShadingType,
        BorderStyle, AlignmentType, PageOrientation } = require("docx");
const rows = [
  ["Component", "Description", "Size / Quantity"],
  ["Solar panels", "Generate DC electricity from sunlight on the roof", "299 × 620 W = 185.4 kWp"],
  ["Inverters", "Convert DC power to AC power for the hotel", "2 × 80 kW"],
  ["AC combiner panel", "Joins both inverter outputs on the roof", "1 panel, 250 A"],
  ["Main switchboard", "Where solar and grid power meet (hotel LV room)", "Existing, 1000 A"],
  ["Zero-export controller", "Keeps solar below hotel use – no export to the grid", "1 unit with monitoring"],
  ["Utility grid (UEDCL)", "Supplies the rest of the hotel's electricity", "Existing supply"],
  ["Expected generation", "Solar energy used by the hotel each year", "≈ 274,000 kWh/yr (≈ 22,900 kWh/month)"],
];
const W = [2600, 4300, 2738];                    // twips, sum 9638 (A4 portrait text width)
const b = { style: BorderStyle.SINGLE, size: 4, color: "C9D0D8" };
const borders = { top: b, bottom: b, left: b, right: b };
const table = new Table({
  width: { size: 9638, type: WidthType.DXA }, columnWidths: W,
  rows: rows.map((r, i) => new TableRow({ tableHeader: i === 0, children: r.map((t, j) => new TableCell({
    borders, width: { size: W[j], type: WidthType.DXA }, margins: { top: 60, bottom: 60, left: 110, right: 110 },
    shading: i === 0 ? { fill: "14365D", type: ShadingType.CLEAR, color: "auto" } : (i % 2 === 0 ? { fill: "EEF2F6", type: ShadingType.CLEAR, color: "auto" } : undefined),
    children: [new Paragraph({ children: [new TextRun({ text: t, bold: i === 0 || j === 0, color: i === 0 ? "FFFFFF" : "1B2430", size: 19 })] })],
  })) })),
});
const img = fs.readFileSync(path.join(__dirname, "PV_Block_Diagram.png"));
const doc = new Document({
  styles: { default: { document: { run: { font: "Arial", size: 20 } } } },
  sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    children: [
      new Paragraph({ alignment: AlignmentType.CENTER, children: [new ImageRun({ type: "png", data: img, transformation: { width: 640, height: 256 },
        altText: { title: "Block diagram", description: "Rooftop solar PV block diagram", name: "Block diagram" } })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 }, children: [new TextRun({ text: "Figure – Rooftop solar PV system block diagram", italics: true, size: 16, color: "5B6673" })] }),
      table,
    ] }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(path.join(__dirname, "PV_Block_Diagram_with_Table.docx"), buf); console.log("ok"); });
