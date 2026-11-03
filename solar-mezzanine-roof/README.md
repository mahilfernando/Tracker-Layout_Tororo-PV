# Rooftop PV layout – D18102-DD-A-104 (Mezzanine)

`PV_Layout_10deg_Mezzanine_Roof.dxf` – PV layout at real scale in mm, ready to paste into the DWG.
`make_pv_layout.py` – regenerates the DXF (change tilt, module or spacing at the top).
`preview_overlay.png` – the layout drawn over the architect's PDF to check the fit.

## Design basis
| Item | Value |
|---|---|
| Module | 2382 × 1134 × 30 mm, 620 Wp bifacial TOPCon, portrait, 2 high (2P) |
| Tilt | 10° → 2P table depth on plan 4,711 mm; 1P table 2,346 mm |
| Clamp gap | 20 mm |
| Aisle between tables | 800 mm (no row-to-row shading 09:00–15:00 all year at Tororo) |
| Edge setback | 1,000 mm (east side 1,742 mm to keep clear of the roof opening ⊠) |
| Modules per row | 23 (row length 26,522 mm) |

## Result
| Zone | Tables | Modules | kWp |
|---|---|---|---|
| Upper block (+6.80, incl. hatched +4.85 strip) | 2 × 2P + 1 × 1P | 115 | 71.3 |
| Lower block (architect's PV zone) | 4 × 2P | 184 | 114.1 |
| **Base total** | | **299** | **185.4** |
| Optional strip below the PV zone (orange layer, confirm it is open roof) | 1 × 2P + 1 × 1P | 69 | 42.8 |
| **Total with optional** | | **368** | **228.2** |

## Layers
`PV-MODULE`, `PV-TABLE`, `PV-MODULE-OPTIONAL`, `PV-TABLE-OPTIONAL`, `PV-SETBACK`,
`PV-OBSTRUCTION`, `PV-ROOF-REF`, `PV-DIM`, `PV-TEXT`. Modules are block `PV_MOD_620W`.

## Inserting into the DWG
The roof outline was traced from the PDF plot (accurate to about ±50 mm) and calibrated on the
29,390 and 15,805 dimensions. The DXF origin (0,0) is the **inner face of the top-left (NW) corner
of the upper PV roof**.
1. Open the DXF, select everything, then run `COPYBASE` with base point 0,0.
2. In the DWG, `PASTECLIP` and pick the same inner corner.
3. If the model space is rotated relative to the plot, `ROTATE` about that corner.
4. Check that the `PV-ROOF-REF` outline sits on the walls, then freeze or delete that layer.
