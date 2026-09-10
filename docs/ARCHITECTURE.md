# Architecture System

Architecture is deterministic rather than freeform AI art. The authority is `references/architecture/rastalr_architecture_v2/architecture_v2_spec.json`, together with the camera reference.

| Constraint | Standard |
| --- | --- |
| Logical grid | 32 px |
| Wall topology strip | 8 px, centered |
| Connection region | pixels 12–19 |
| Physical wall | ~44 px visible height, 8 px cap |
| Projection | rectangular-grid RPG oblique |

Generate exact N/E/S/W, ends, corners, T junctions, crosses, and openings from topology. Presentation is orientation-aware: north walls receive a full face, side walls a shallow boundary, and south walls a low cutaway. Doors, windows, and glass inherit those anchors. Decoration is usually a separate overlay.

The extracted reference sprites are retained under `references/architecture/rastalr_architecture_v2/`; use them for validation, not as permission to alter the underlying topology.
