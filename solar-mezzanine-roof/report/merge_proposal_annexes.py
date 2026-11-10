"""Append annexes to the NSP proposal and stamp an 'ANNEX n' tag + footer on each annex page.
Usage: python3 merge_proposal_annexes.py <annex_dir>
annex_dir holds 1.Single_Line_Diagram.pdf ... 5.PV_Stuctrural_Drawing.pdf; Annex 6 = Kampala_Marriott_PV_Quotation.pdf.
"""
import io, os, sys
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

HERE = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1]
annexes = [("1", "Single-line diagram", "1.Single_Line_Diagram.pdf"), ("2", "Solar PV layout", "2.Solar_PV_Layout.pdf"),
           ("3", "Inverter data sheet", "3.Data_Sheet_of_Inverter.pdf"), ("4", "Solar module data sheet", "4.Data_Sheet_of_Solar_Module.pdf"),
           ("5", "PV structural drawing", "5.PV_Stuctrural_Drawing.pdf"), ("6", "Quotation", os.path.join(HERE, "Kampala_Marriott_PV_Quotation.pdf")),
           ("7", "PVsyst simulation report", os.path.join(HERE, "PVsyst_Report_Kampala_Marriott_Hotel_185kWp_VC0.pdf"))]

def stamp(w, h, label, pg):
    buf = io.BytesIO(); c = canvas.Canvas(buf, pagesize=(w, h))
    c.setFillColor(HexColor("#1f3f8f")); tw = c.stringWidth(label, "Helvetica-Bold", 8) + 16
    c.roundRect(w - tw - 14, h - 22, tw, 14, 3, fill=1, stroke=0)
    c.setFillColor(HexColor("#ffffff")); c.setFont("Helvetica-Bold", 8); c.drawString(w - tw - 6, h - 18, label)
    c.setFillColor(HexColor("#6b7480")); c.setFont("Helvetica", 6.5)
    c.drawRightString(w - 14, 6, f"185.4 kWp Rooftop Solar PV – Kampala Marriott Hotel | NileSun Power Ltd  ·  Page {pg}")
    c.save(); buf.seek(0); return PdfReader(buf).pages[0]

out = PdfWriter()
main = PdfReader(os.path.join(HERE, "Kampala_Marriott_PV_Proposal_NSP.pdf"))
for p in main.pages: out.add_page(p)
pg = len(main.pages)
for n, title, f in annexes:
    r = PdfReader(f if os.path.isabs(f) else os.path.join(src, f))
    for k, p in enumerate(r.pages):
        pg += 1
        w, h = float(p.mediabox.width), float(p.mediabox.height)
        label = f"ANNEX {n} – {title.upper()}" + (f" ({k+1}/{len(r.pages)})" if len(r.pages) > 1 else "")
        p.merge_page(stamp(w, h, label, pg)); out.add_page(p)
out.add_metadata({"/Title": "Technical & Commercial Proposal – 185.4 kWp Rooftop Solar PV – Kampala Marriott Hotel", "/Author": "NileSun Power Ltd"})
dst = os.path.join(HERE, "Kampala_Marriott_PV_Proposal_with_Annexes.pdf")
with open(dst, "wb") as fh: out.write(fh)
print(dst, pg, "pages")
