# Bedside cabinet V3 art-pilot findings

Status: **REJECTED AS A RELEASE ART BASELINE; RETAINED AS ITERATION EVIDENCE**. V3 corrected V2's excessive internal detail, but follow-up review found its top still slab-like, its body generic and its drawer too dominant. The approved `bedside_cabinet_01` production PNG, staging files, manifest record and approval state are unchanged.

## What changed after V2

V2 was rejected because its stacked crown, nested cupboard borders, heavy internal ink and small hardware marks made it read like a diagram. V3 redraws the native sprite rather than filtering or downscaling V2:

- one shallow top plane and one slim front edge;
- full navy outline concentrated on the exterior silhouette;
- slate internal separators instead of repeated navy frames;
- one quiet ivory cupboard plane with a single readable latch;
- one broad steel drawer with compact handle clusters;
- eleven controlled opaque colors, zero partial-alpha pixels;
- 32x36 canvas, 28x32 opaque bounds, one-tile footprint and `bottom_center` anchor;
- upper-left light, right-edge falloff and a small contact cluster;
- axis-aligned construction with depth receding straight upward and no broad rotated side face.

An ImageGen exploration was used only to test the simplified form direction. It produced smooth high-resolution rendering and did not supply pixels to the candidate. `build_cabinet_v3.py` deliberately plots the final native clusters and locks the hashes of the approved, V1 and V2 inputs.

## Evidence

- `bedside_cabinet_v3_review.png`: approved / V1 / rejected V2 / V3 at nearest-neighbor 7x.
- `bedside_cabinet_v3_godot.png`: the four cabinet states beside the adult, standard bed and waiting chair at integer 3x.
- `mapping.json`: input and candidate hashes, dimensions, alpha bounds, palette size and unchanged approval statement.
- `bedside_cabinet_v3_review.tscn`: isolated practical review scene; normal integration startup remains unchanged.

Executed results:

```text
BEDSIDE_CABINET_V3_BUILD_PASS: 32x36 native sprite; 11 opaque colors; hard alpha; prior hashes locked
BEDSIDE_CABINET_V3_REVIEW_PASS: four cabinet states rendered beside adult, bed and chair at integer scale
```

## Superseded assessment

V3 established the calmer outline and cluster direction, but it did not clear the release bar. V4 replaces it as the active human-review candidate.
