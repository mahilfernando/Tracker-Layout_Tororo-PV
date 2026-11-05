// Word document with the engineering SLD on an A4 landscape page
const fs = require("fs"), path = require("path");
const { Document, Packer, Paragraph, TextRun, ImageRun, AlignmentType, PageOrientation } = require("docx");
const png = fs.readFileSync(path.join(__dirname, "PV_SLD_Engineering.png"));
const W = 960, H = Math.round(960 * 1188 / 1680);
const doc = new Document({
  styles: { default: { document: { run: { font: "Arial", size: 20 } } } },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838, orientation: PageOrientation.LANDSCAPE },
                          margin: { top: 567, bottom: 567, left: 567, right: 567 } } },
    children: [
      new Paragraph({ alignment: AlignmentType.CENTER, children: [new ImageRun({ type: "png", data: png,
        transformation: { width: W, height: H },
        altText: { title: "Single-line diagram", description: "PV system single-line diagram PV-SLD-D18102-004", name: "SLD" } })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60 }, children: [new TextRun({
        text: "Figure – Single-line diagram, 185.4 kWp rooftop PV (drawing PV-SLD-D18102-004 Rev A)", italics: true, size: 16, color: "5B6673" })] }),
    ],
  }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(path.join(__dirname, "PV_SLD_Engineering.docx"), b); console.log("docx ok"); });
