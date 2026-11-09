"""Simple (non-technical) block diagram of the rooftop PV system -> PV_Block_Diagram.svg / .html."""
import os
from html import escape as esc

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1600, 640
g = []
def box(x, y, w, h, title, lines, fill, stroke, icon=None):
    g.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{stroke}" stroke-width="2.5"/>')
    if icon: g.append(icon(x + w / 2, y + 48))
    g.append(f'<text x="{x+w/2}" y="{y+110}" class="bt" text-anchor="middle">{esc(title)}</text>')
    for i, t in enumerate(lines):
        g.append(f'<text x="{x+w/2}" y="{y+136+i*22}" class="bs" text-anchor="middle">{esc(t)}</text>')
def arrow(x1, y1, x2, y2, label=None, dashed=False, lx=None, ly=None):
    cls = "arrd" if dashed else "arr"
    g.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{cls}" marker-end="url(#{"hd" if dashed else "h"})"/>')
    if label:
        g.append(f'<text x="{lx if lx is not None else (x1+x2)/2}" y="{ly if ly is not None else (y1+y2)/2-12}" class="al" text-anchor="middle">{esc(label)}</text>')

# simple icons
def sun_panel(cx, cy):
    s = f'<circle cx="{cx-34}" cy="{cy-18}" r="10" fill="#eda100"/>'
    s += f'<rect x="{cx-22}" y="{cy-16}" width="56" height="34" fill="#1f4fb5" stroke="#14365d" stroke-width="2" transform="skewX(-12)"/>'
    for k in (1, 2): s += f'<line x1="{cx-22+k*18.7}" y1="{cy-16}" x2="{cx-22+k*18.7}" y2="{cy+18}" stroke="#9fb7e6" stroke-width="1.5" transform="skewX(-12)"/>'
    s += f'<line x1="{cx-22}" y1="{cy+1}" x2="{cx+34}" y2="{cy+1}" stroke="#9fb7e6" stroke-width="1.5" transform="skewX(-12)"/>'
    return s
def inverter(cx, cy):
    return (f'<rect x="{cx-26}" y="{cy-24}" width="52" height="46" rx="5" fill="#fff" stroke="#14365d" stroke-width="2.5"/>'
            f'<line x1="{cx-26}" y1="{cy+22}" x2="{cx+26}" y2="{cy-24}" stroke="#14365d" stroke-width="1.5"/>'
            f'<text x="{cx-15}" y="{cy-6}" class="ic">=</text><text x="{cx+5}" y="{cy+17}" class="ic">~</text>')
def panel(cx, cy):
    s = f'<rect x="{cx-22}" y="{cy-26}" width="44" height="50" rx="4" fill="#fff" stroke="#14365d" stroke-width="2.5"/>'
    for k in range(3): s += f'<rect x="{cx-14}" y="{cy-18+k*14}" width="28" height="8" rx="2" fill="#c9d0d8"/>'
    return s
def building(cx, cy):
    s = f'<rect x="{cx-30}" y="{cy-22}" width="60" height="46" fill="#fff" stroke="#14365d" stroke-width="2.5"/>'
    s += f'<polygon points="{cx-36},{cy-22} {cx},{cy-42} {cx+36},{cy-22}" fill="#14365d"/>'
    for i in range(3):
        for j in range(2): s += f'<rect x="{cx-22+i*16}" y="{cy-14+j*16}" width="10" height="9" fill="#eda100"/>'
    return s
def pylon(cx, cy):
    return (f'<polyline points="{cx-18},{cy+24} {cx},{cy-30} {cx+18},{cy+24}" fill="none" stroke="#14365d" stroke-width="2.5"/>'
            f'<line x1="{cx-24}" y1="{cy-14}" x2="{cx+24}" y2="{cy-14}" stroke="#14365d" stroke-width="2.5"/>'
            f'<line x1="{cx-14}" y1="{cy+2}" x2="{cx+14}" y2="{cy+2}" stroke="#14365d" stroke-width="2.5"/>')
def controller(cx, cy):
    return (f'<rect x="{cx-24}" y="{cy-20}" width="48" height="38" rx="5" fill="#fff" stroke="#c27a00" stroke-width="2.5"/>'
            f'<polyline points="{cx-16},{cy+6} {cx-6},{cy-6} {cx+4},{cy+2} {cx+16},{cy-10}" fill="none" stroke="#c27a00" stroke-width="2.5"/>')

g.append(f'<text x="40" y="52" class="h">Rooftop Solar PV System – Kampala Marriott Hotel</text>')
g.append(f'<text x="40" y="80" class="sub">185.4 kWp grid-tied system · all solar energy used by the hotel · no battery</text>')

Y, BH, BW = 130, 210, 230
xs = [40, 360, 680, 1000, 1320]
BLUE, BS = "#eef2f6", "#14365d"
box(xs[0], Y, BW, BH, "Solar Panels", ["299 panels × 620 W", "185.4 kWp on the roof"], "#eef4ff", "#1f4fb5", sun_panel)
box(xs[1], Y, BW, BH, "2 Inverters", ["2 × 80 kW", "convert DC to AC power"], BLUE, BS, inverter)
box(xs[2], Y, BW, BH, "AC Combiner Panel", ["on the roof", "joins both inverters"], BLUE, BS, panel)
box(xs[3], Y, BW, BH, "Main Switchboard", ["hotel LV room", "solar + grid meet here"], BLUE, BS, panel)
box(xs[4], Y, BW, BH, "Hotel Loads", ["≈ 1,000,000 kWh/month", "rooms, kitchen, A/C, lifts"], "#fff6e5", "#c27a00", building)
my = Y + BH / 2
arrow(xs[0] + BW, my, xs[1] - 6, my, "DC power")
arrow(xs[1] + BW, my, xs[2] - 6, my, "AC power")
arrow(xs[2] + BW, my, xs[3] - 6, my, "AC power")
arrow(xs[3] + BW, my, xs[4] - 6, my, "Electricity")

# grid below main switchboard
box(xs[3], 420, BW, 180, "Utility Grid (UEDCL)", ["supplies the rest", "of the hotel's power"], "#f4f6f9", "#5b6673", pylon)
arrow(xs[3] + BW / 2, 420, xs[3] + BW / 2, Y + BH + 6, "Grid power", lx=xs[3] + BW / 2 + 70, ly=395)
# energy monitoring (data logger + meter) – monitoring only, no export control
box(xs[1], 420, BW + 320, 180, "Energy Monitoring", ["data logger + energy meter", "remote monitoring of solar output and savings"], "#fff6e5", "#c27a00", controller)
arrow(xs[1] + 80, Y + BH + 6, xs[1] + 80, 420, "monitors", dashed=True, lx=xs[1] + 128, ly=395)
CSS = """
.blk text { font-family: Arial, Helvetica, sans-serif; fill: #1b2430; }
.blk .h { font-size: 28px; font-weight: 700; fill: #14365d; }
.blk .sub { font-size: 17px; fill: #5b6673; }
.blk .bt { font-size: 21px; font-weight: 700; fill: #14365d; }
.blk .bs { font-size: 15.5px; fill: #3d4752; }
.blk .al { font-size: 15px; font-weight: 700; fill: #5b6673; }
.blk .ic { font-size: 20px; font-weight: 700; fill: #14365d; }
.blk .arr { stroke: #14365d; stroke-width: 4; }
.blk .arrd { stroke: #c27a00; stroke-width: 3; stroke-dasharray: 9 6; }
"""
defs = ('<defs><marker id="h" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
        '<path d="M0,0 L10,5 L0,10 z" fill="#14365d"/></marker>'
        '<marker id="hd" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M0,0 L10,5 L0,10 z" fill="#c27a00"/></marker></defs>')
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" class="blk">'
       f'<style>{CSS}</style>{defs}<rect width="{W}" height="{H}" fill="#fff"/>' + "".join(g) + "</svg>")
open(os.path.join(HERE, "PV_Block_Diagram.svg"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n' + svg)
open(os.path.join(HERE, "PV_Block_Diagram.html"), "w").write(
    "<!doctype html><html><head><meta charset='utf-8'><style>@page{size:A4 landscape;margin:10mm}html,body{margin:0;background:#fff}"
    "svg{width:277mm;height:auto;display:block}</style></head><body>" + svg + "</body></html>")
print("ok")
