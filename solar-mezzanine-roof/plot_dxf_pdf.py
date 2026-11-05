"""Plot PV_Layout_Enerack_10deg.dxf to PDF (A3 landscape) with the CAD layer colours.

Page 1: whole drawing (array, structure, equipment, all cable layers).
Page 2: cable layout only - modules/structure greyed out, cable layers in colour, with a layer legend.
Run: python3 plot_dxf_pdf.py
"""
import os
import ezdxf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy, ColorPolicy
from ezdxf import colors

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "PV_Layout_Enerack_10deg.dxf")
OUT = os.path.join(HERE, "PV_Layout_Enerack_10deg_CAD.pdf")
A3 = (16.54, 11.69)

CABLE_LAYERS = ["PV-CABLE-TRAY", "PV-CABLE-DC-STRING", "PV-CABLE-DC-HOMERUN", "PV-CABLE-AC-C1-C2",
                "PV-CABLE-AC-C3", "PV-CABLE-EARTH", "PV-CABLE-COMMS", "PV-CABLE-TAGS"]
GREY_LAYERS = ["PV-MODULE", "PV-RAIL", "PV-FRAME", "PV-FOOT", "PV-SETBACK", "PV-DIM"]

def plot(doc, title, cables_only=False):
    fig = plt.figure(figsize=A3)
    ax = fig.add_axes([0.02, 0.06, 0.96, 0.86])
    ax.set_axis_off()
    # plot-only overrides (the DXF file itself is not changed)
    doc.styles.get("Standard").dxf.font = "DejaVuSans.ttf"
    for name, aci in (("PV-TEXT", 250), ("PV-CABLE-TAGS", 250), ("PV-DIM", 8)):
        doc.layers.get(name).dxf.color = aci
    dark = ezdxf.colors.rgb2int((45, 50, 58))
    for e in doc.modelspace():                       # texts render with explicit colour only
        if e.dxftype() in ("TEXT", "MTEXT"): e.dxf.true_color = dark
    for blk in doc.blocks:                           # dimension geometry/text (anonymous *D blocks)
        if blk.name.upper().startswith("*D"):
            for e in blk: e.dxf.true_color = ezdxf.colors.rgb2int((110, 118, 128))
    if cables_only:
        for name in GREY_LAYERS:
            if doc.layers.has_entry(name): doc.layers.get(name).dxf.color = 253
    ctx = RenderContext(doc)
    cfg = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.COLOR_SWAP_BW,
                        lineweight_scaling=0.6, min_lineweight=0.12)
    Frontend(ctx, MatplotlibBackend(ax, adjust_figure=False), config=cfg).draw_layout(doc.modelspace(), finalize=False)
    ax.set_aspect("equal", adjustable="datalim")
    x0, x1, y0, y1 = (-4000, 46000, -59000, 4500) if cables_only else (-4000, 86000, -59000, 4500)
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
    fig.text(0.02, 0.965, title, fontsize=13, fontweight="bold", color="#14365d")
    fig.text(0.02, 0.945, "Kampala Marriott Hotel – mezzanine roof · 185.4 kWp · plotted from PV_Layout_Enerack_10deg.dxf "
             "(units mm, origin = inner NW corner of upper roof) · NTS", fontsize=8.5, color="#5b6673")
    if cables_only:
        handles = []
        for name in CABLE_LAYERS:
            aci = doc.layers.get(name).dxf.color
            rgb = colors.aci2rgb(aci) if aci not in (7, 250) else (60, 60, 60)
            ls = {"CONTINUOUS": "-", "DASHED": "--", "DASHDOT": "-.", "DOT": ":"}.get(doc.layers.get(name).dxf.linetype.upper(), "-")
            handles.append(Line2D([0], [0], color=[v / 255 for v in rgb], lw=2, ls=ls, label=name))
        fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=8, frameon=False, bbox_to_anchor=(0.5, 0.005))
    else:
        fig.text(0.02, 0.02, "Layers: PV-MODULE, PV-RAIL, PV-FRAME, PV-FOOT, PV-EQUIPMENT, PV-EXISTING, PV-OBSTRUCTION, "
                 + ", ".join(CABLE_LAYERS) + ".", fontsize=7.5, color="#5b6673", wrap=True)
    return fig

doc = ezdxf.readfile(SRC)
with PdfPages(OUT) as pdf:
    pdf.savefig(plot(doc, "ROOFTOP PV LAYOUT – CAD PLOT (all layers)"))
    plt.close("all")
    doc2 = ezdxf.readfile(SRC)
    pdf.savefig(plot(doc2, "CABLE LAYOUT – CAD PLOT (cable layers highlighted)", cables_only=True))
    plt.close("all")
print(OUT)
