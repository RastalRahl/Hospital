# Bedside cabinet V4 art-pilot findings

Status: **NEEDS HUMAN VISUAL REVIEW**. V4 is a reference-only candidate. The approved `bedside_cabinet_01` production PNG, staging files, manifest record and approval state are unchanged.

## Corrections after V3

V3 remained too generic: its top read as stacked slabs, the drawer dominated the front, and the plain rectangular body lacked a purposeful lower silhouette. V4 is a fresh native-pixel redraw:

- one continuous molded work surface with stepped manufactured corners;
- body tucked directly beneath the surface instead of a separate front slab;
- smaller muted-steel drawer and compact handle;
- broad warm-ivory cupboard surface with sparse material clusters;
- one restrained teal latch rather than decorative micro-detail;
- clipped lower corners, narrow undercarriage and compact hospital casters;
- exterior-weighted navy silhouette with lighter slate internal construction;
- 32x36 canvas, 28x32 opaque bounds, 12 opaque colors and no partial alpha;
- one-tile logical footprint, `bottom_center` anchor and upper-left lighting.

ImageGen was used for a form exploration. Its high-resolution result retained a baked checkerboard and excessive smooth shading, so it contributed no pixels. The exploration supported only the caster direction. `build_cabinet_v4.py` plots the final clusters at native resolution and locks both the approved and V3 input hashes.

## Evidence

- `bedside_cabinet_v4_review.png`: approved / rejected V3 / V4 at nearest-neighbor 8x.
- `bedside_cabinet_v4_godot.png`: those states beside the adult, standard bed and waiting chair at integer 3x.
- `mapping.json`: locked input hashes, candidate hash, dimensions, alpha bounds, palette size and unchanged approval statement.
- `bedside_cabinet_v4_review.tscn`: isolated practical review scene; normal integration startup is unchanged.

Executed results:

```text
BEDSIDE_CABINET_V4_BUILD_PASS: 32x36 native sprite; 12 opaque colors; hard alpha; inputs locked
BEDSIDE_CABINET_V4_REVIEW_PASS: V4 rendered beside approved, V3, adult, bed and chair at integer scale
```

## Codex assessment

V4 resolves the named V3 defects. Its top reads as one molded component, the cupboard owns the front hierarchy, and the caster silhouette gives the object a specific hospital-furniture identity. The material clusters stay readable at native scale and its proportions remain credible beside the adult and bed. This is suitable for human acceptance as the calibration art direction. Do not promote production or propagate the style to the counter and cart until the user accepts it.
