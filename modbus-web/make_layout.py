"""Generate static/layout.json - the Tororo PV plant map used by layout.html.

    python make_layout.py

Edit BLOCK_TRACKERS below when the real tracker count of each block is known,
then run this again. The geometry follows the plant layout drawing: four
bands of trackers (two tracker rows per band) separated by internal roads,
skewed like the drawing.

Coordinates are "plan" units: x 0..1000 west -> east, y 0..620 north -> south.
layout.html maps them to the drawing's slanted view.

DBox numbering (ASSUMPTION - confirm with PVH): inside each block, DBoxes are
numbered segment by segment in the order listed in SEGMENTS, each segment
top tracker row first, west to east, then the bottom row west to east.
"""

import json
from pathlib import Path

# Trackers per block. Total must be 442. Split by area until the real
# numbers come from the commissioning team.
BLOCK_TRACKERS = {1: 103, 2: 102, 3: 111, 4: 126}

ROW_H = 64          # tracker length (one tracker row)
ROW_GAP = 6         # gap between the two tracker rows of a band
ROAD = 28           # internal road between bands
BAND_TOPS = [0, 162, 324, 486]   # y of each band's top row

# (band index 0-3, block, x0, x1) in plan units, in DBox numbering order
SEGMENTS = [
    (0, 2, 0, 410), (0, 1, 410, 1000),
    (1, 2, 0, 382), (1, 4, 382, 528), (1, 1, 528, 736), (1, 4, 736, 868),
    (2, 3, 0, 444), (2, 4, 444, 806),
    (3, 3, 0, 417), (3, 4, 417, 764),
]

# Inverter stations, from the drawing (image px) -> converted to plan units below
INVERTERS_IMG = {
    "B1-1": (1052, 127), "B1-2": (1022, 127), "B1-3": (968, 140), "B1-4": (938, 140),
    "B1-5": (882, 145), "B1-6": (850, 158), "B1-7": (783, 172), "B1-8": (756, 172),
    "B1-9": (703, 183), "B1-10": (775, 357), "B1-11": (850, 338),
    "B2-1": (673, 183), "B2-2": (631, 197), "B2-3": (602, 198), "B2-4": (541, 213),
    "B2-5": (490, 219), "B2-6": (458, 224), "B2-7": (414, 231), "B2-8": (388, 418),
    "B2-9": (443, 410), "B2-10": (528, 397), "B2-11": (603, 382),
    "B3-1": (416, 416), "B3-2": (494, 404), "B3-3": (575, 386), "B3-4": (653, 378),
    "B3-5": (398, 605), "B3-6": (425, 600), "B3-7": (472, 591), "B3-8": (497, 588),
    "B3-9": (572, 576), "B3-10": (618, 566), "B3-11": (653, 561),
    "B4-1": (682, 372), "B4-2": (725, 365), "B4-3": (805, 355), "B4-4": (881, 336),
    "B4-5": (955, 322), "B4-6": (896, 520), "B4-7": (868, 524), "B4-8": (827, 532),
    "B4-9": (800, 536), "B4-10": (722, 550), "B4-11": (686, 555),
}
SCADA_IMG = (955, 280)
BLOCK_LABELS_IMG = {1: (985, 190), 2: (640, 262), 3: (470, 462), 4: (880, 392)}

# plan -> drawing transform (must match layout.html): ix = 365 + 0.72 px,
# iy = 150 + 0.89 py - 0.1152 px
SX, SY, SK, OX, OY = 0.72, 0.89, 0.1152, 365, 150


def img_to_plan(ix, iy):
    px = (ix - OX) / SX
    py = (iy - OY + SK * px) / SY
    return round(px, 1), round(py, 1)


def split_counts(total, lengths):
    """Share `total` trackers over sub-rows in proportion to their length."""
    s = sum(lengths)
    raw = [total * L / s for L in lengths]
    counts = [int(r) for r in raw]
    for i in sorted(range(len(raw)), key=lambda i: raw[i] - counts[i], reverse=True)[: total - sum(counts)]:
        counts[i] += 1
    return counts


def main():
    assert sum(BLOCK_TRACKERS.values()) == 442, "BLOCK_TRACKERS must add up to 442"
    # every segment has two tracker rows
    rows = []
    for band, block, x0, x1 in SEGMENTS:
        top = BAND_TOPS[band]
        rows.append((block, x0, x1, top))
        rows.append((block, x0, x1, top + ROW_H + ROW_GAP))

    trackers, next_dbox, segs_out = [], {b: 1 for b in BLOCK_TRACKERS}, []
    for block, total in BLOCK_TRACKERS.items():
        mine = [r for r in rows if r[0] == block]
        for (blk, x0, x1, y), n in zip(mine, split_counts(total, [r[2] - r[1] for r in mine])):
            segs_out.append({"block": blk, "x0": x0, "x1": x1, "y": y, "h": ROW_H, "count": n})
    # number in SEGMENTS order (rows list order), not grouped by the loop above
    order = {(s["block"], s["x0"], s["y"]): s for s in segs_out}
    for block, x0, x1, y in rows:
        s = order[(block, x0, y)]
        pitch = (x1 - x0) / s["count"]
        for i in range(s["count"]):
            trackers.append({"block": block, "dbox": next_dbox[block],
                             "x": round(x0 + i * pitch + pitch * 0.15, 2), "y": y,
                             "w": round(pitch * 0.7, 2), "h": ROW_H})
            next_dbox[block] += 1

    roads = [{"y": BAND_TOPS[i] + 2 * ROW_H + ROW_GAP, "h": ROAD} for i in range(3)]
    layout = {
        "name": "Tororo PV",
        "transform": {"sx": SX, "sy": SY, "sk": SK, "ox": OX, "oy": OY},
        "plan": {"w": 1000, "h": BAND_TOPS[-1] + 2 * ROW_H + ROW_GAP},
        "blocks": {str(b): n for b, n in BLOCK_TRACKERS.items()},
        "roads": roads,
        "inverters": [{"name": k, "x": p[0], "y": p[1]} for k, p in
                      ((k, img_to_plan(*v)) for k, v in INVERTERS_IMG.items())],
        "scada": dict(zip(("x", "y"), img_to_plan(*SCADA_IMG))),
        "block_labels": {str(b): dict(zip(("x", "y"), img_to_plan(*p))) for b, p in BLOCK_LABELS_IMG.items()},
        "trackers": trackers,
    }
    out = Path(__file__).parent / "static" / "layout.json"
    out.write_text(json.dumps(layout, separators=(",", ":")))
    print(f"wrote {out}: {len(trackers)} trackers, "
          + ", ".join(f"block {b}: {n}" for b, n in BLOCK_TRACKERS.items()))


if __name__ == "__main__":
    main()
