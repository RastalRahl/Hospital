# Bedside cabinet V2 art-pilot findings

Status: **REJECTED AS A RELEASE ART BASELINE; RETAINED AS ITERATION EVIDENCE**. Human follow-up found the top rim too heavy, the silhouette too diagram-like, the internal outlines too dominant and the cupboard detail too noisy. The approved `bedside_cabinet_01` production PNG, staging files, manifest record and approval state are unchanged.

## Why V2 exists

The user found the V1 calibration more perspective-consistent but ugly. That assessment is recorded as an art-direction rejection: V1 remains useful for geometry, scale and anchor reasoning, but it must not become the visual standard for R1–R9.

The first V2 Godot pass restored construction detail but remained too tall beside the 26x46 adult. The final candidate compresses the body to V1's 36 px canvas height while retaining the richer art.

## Final candidate

- 34x36 canvas; 28x32 opaque bounds; one-tile logical footprint; `bottom_center` anchor.
- Rectangular-grid RPG-oblique projection with depth moving straight upward.
- Parallel top/front edges and no broad right-side face or default rotated yaw.
- Thirteen opaque colors, zero partial-alpha pixels and no downscaling.
- Upper-left highlight and right-edge value falloff without inventing a side plane.
- Constructed top rim, recessed steel drawer, lit metal pull, raised cupboard panel, latch, hinges, corner posts, base rail, feet and small contact shadow.
- Large quiet ivory clusters keep the cabinet readable at native scale; small teal/steel clusters provide clinical identity.

ImageGen was used for one richer form exploration with the approved cabinet, V1 geometry, canonical camera and local Modern Interiors sheet as references. Its output remained a smooth high-resolution concept with a baked checkerboard treatment, so none of those pixels entered V2. `build_cabinet_v2.py` plots the final native pixels deterministically.

## Evidence

- `bedside_cabinet_art_review.png`: approved / rejected V1 geometry / V2 art at nearest-neighbor 8x.
- `bedside_cabinet_art_godot.png`: all three cabinets beside the unchanged adult, standard bed and waiting chair at integer 3x.
- `mapping.json`: exact source and candidate hashes, dimensions, alpha bounds and unchanged approval statement.
- `bedside_cabinet_art_review.tscn`: separate review scene; normal startup and production integration remain unchanged.

Executed results:

```text
BEDSIDE_CABINET_V2_BUILD_PASS: native art pilot; 13 opaque colors; hard alpha; approved and V1 hashes locked
BEDSIDE_CABINET_ART_REVIEW_PASS: approved, V1 and V2 share feet; V2 rendered beside adult, bed and chair at integer scale
```

## Superseded assessment

V2 improved material identity over V1, but it did not meet the release art bar. Its geometry remains useful for comparing the successive corrections. V3 replaces it as the active human-review candidate.
