# D2 geometry revision v2 — proposed cutaway return

Contract: PROPOSED_FOR_HUMAN_GEOMETRY_REVIEW. Computed conformance: PASS. Human geometry review remains pending; no final appearance readiness or approval.

V1's shallow strip began at D1's baseline without a visible upper transition. V2 explicitly proposes a glazed north return and a stylized cutaway into the shallow side. This is not a new global camera or equal-height rail projection.

Canonical requirements remain 32 px grid, 8 px NS strip, axis-aligned ground, shallow orientation-aware side and 8x source scale. Measured canonical side is 20x32; D1 is 32x28. The 12 px side band, 2 px rails and cutaway arrangement are NEW proposed presentation choices, replacing v1's 14 px width ratio. Half-open rectangles are used throughout.

Main/repeat: 12x32 native, 96x256 source; origin [12,0] relative to cell, cell anchor [16,16], image anchor [4,16]. Corner-main/repeat: 12x56 native, 96x448 source; origin [12,-24], image anchor [4,40]. The carrier contains the declared north return, with no arbitrary padding/trim. All export pixels are exact 8x blocks. Footprint is 1x1 independently of carrier dimensions.

D1 cell [64,44] maps to render [64,36]. Its ground centerline is y60; baseline edge is y64. D2 cell [48,60] has north center [64,60]; its cap occupies y60..64 and meets the distinct D1 base edge. The corner image starts at [60,36], derived from D1's 28 px image height and 4 px center-to-base offset, not an unanchored upward shift.

The D2 upper cap [0,0,8,4), outer frame [0,0,2,28), glazed reveal [2,4,4,24) and shallow cap [0,24,12,28) explicitly form the transition. The return is a side-facing cheek beside D1's original post, not an added column or cover. Its 2 px glass reveal and abrupt cutaway are visual review risks. Main pane [2,4,10,28) has alpha150, frame255; all undeclared corner pixels are alpha0. Corner and straight views are mutually exclusive parts of one future logical asset. No D1 assembly mask is used.

Measured D1 top y36, side cap y60: deliberate 24 px cutaway. Draw order is background, D2, unchanged D1. Actual opaque overlap: 48 px, confined to [64,36,68,40) and [64,60,72,64). Translucent overlap: 0; hidden glass: 0; unexpected overlap: 0. Required upper contact, glazed reveal and continuous return-frame checks pass independently of base/topology checks. D1 pixels remain exact in the finished composition.

The v1 4x8 topology mask mixed baseline registration error with elbow ownership. With centerline registration, the missing quadrant is 16 px (4x4). D2 owns a half-strip cap [12,-4,20,0) within its corner ground region [12,-4,20,32); this fills that quadrant with 0 missing pixels remaining. It is separately shown as ground ownership, never rendered over the artwork or counted as an asset.

One/two/four-cell runs use 32 px depth stride, north-owned 4 px supports and a terminal south support. Geometry, contact continuity and separate light/dark/colored/object transmission pass. Original and relocated unchanged Batch 11 wall/floor contexts pass. The side/wall width step remains a presentation review item, not a general junction repair.

Negative controls (each has a passing valid control):

- repeat_displacement_1px: intended check `origins`, rejection proven True.
- broken_contact: intended check `frame`, rejection proven True.
- opaque_glass: intended check `pane`, rejection proven True.
- pane_hole: intended check `pane`, rejection proven True.
- doubled_support: intended check `support_spans`, rejection proven True.
- stacked_glass: intended check `single_glass_layer`, rejection proven True.
- anchor_mismatch_1px: intended check `render_origin`, rejection proven True.
- missing_corner_return: intended check `upper_contact`, rejection proven True.
- corner_displacement_1px: intended check `overlap_ownership`, rejection proven True.

Protected files: 1435; changed []; missing []. Counts before/after: {'manifest': 220, 'approved': 220, 'needs_human_review': 0} / {'manifest': 220, 'approved': 220, 'needs_human_review': 0}. Entire D2 v1 and D0/D1 history remain unchanged. Only D2 v2 reference additions are authorized; existing hashes remain locked.

Reproduce: `python tools/validate_architecture_d2_v2.py`. Full suite: `python -m pytest -q`; previous baseline 94.

Captured complete suite: 124 passed; exit 0.

No human approval, final appearance, production ingestion, Batch 13 or D3. Review the explicit cutaway before any appearance task.
