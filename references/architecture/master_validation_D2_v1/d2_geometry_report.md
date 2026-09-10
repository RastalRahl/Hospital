# D2 geometry proposal and scaffold

**READY FOR HUMAN GEOMETRY REVIEW**. Technical conformance: PASS. Contract remains `PROPOSED_FOR_HUMAN_GEOMETRY_REVIEW`.

## Authority and proposal

Canonical: 32 px logical grid, centered 8 px NS ground strip [12,0,20,32), scale 8, axis-aligned camera and shallow left-side presentation. Canonical side PNG measures 20x32; canonical back canvas 32x60 with measured visible envelope [0,0,32,52); D1 32x28. Approved back carriers are 32x52. No committed low-glass side geometry is specified. Sources and SHA-256 are listed in the contract.

Proposed native carrier **32x32**, source **256x256**. Visible envelope **[12,0,26,32)** = 14x32. Explicit presentation heuristic: retain 8 px topology reference width and scale the 12 px additional solid-side band by 28/52: round(12*28/52)=6; total 14. This heuristic is not a measured camera/height law. The cell carrier is declared registration space, not safety padding. No D1 sprite was rotated or transposed.

The side view represents the same nominal 28 px installed partition through a narrower shallow band, not an independently proven elevation projection. This is a design choice for human review, especially at the corner.

Anchor: logical cell [16,16], image [16,16], render origin [0,0]. Ground-to-image is identity in the full-cell carrier. North endpoint [16,0], south [16,32]; source coordinates are multiplied by 8. Room interior faces east/right; depth recedes toward negative y.

## Regions and repeat ownership

Opaque rails: [12,0,14,32), [24,0,26,32). North support: [14,0,24,4); terminal south support: [14,28,24,32). Pane [14,4,24,28) alpha 150. Exterior [0,0,12,32) and [26,0,32,32) alpha 0. Rail width 2 and support depth 4 are proposed choices. Frame alpha is 255; no highlights or appearance polish.

For a nonterminal cell, the pane extends to y=32 within x=14..24. Every cell owns its north support; only the last owns a south support. Two mutually exclusive views belong to one future logical asset. Stride [0,32]; no overlap or shortened spacing.

| Cells | Geometry conformance | Background transmission |
| --- | --- | --- |
| 1 | True | True |
| 2 | True | True |
| 4 | True | True |

## Context and local north-west corner

Original context conformance: True; relocated: True. Both use unchanged approved Batch 11 floors and left-side wall PNGs. Anchor, depth endpoint and opaque contact evidence is in JSON. The proposed 6 px visible-width reduction remains for human review.

D1 actual validated main/repeat files remain unchanged. D1 render origin [64, 36], D2 cell/render origin [48, 64]; computed base endpoints [64, 64] and [64, 64]. Rendered opaque edge pairs: 10; rendered overlaps: 0; glass overlaps: 0. Draw order: floor, D1, D2; no deliberate opaque occlusion or extra visible support.

**Corner remains unresolved at the upper rail.** Measured D1 post top y=36; shallow D2 north support y=64; transition 28 px. A base/topology PASS is not a visual-connection PASS. No column, decorative cover or extra wall conceals this. Straight-run readiness is separate from corner appearance feasibility.

The ground strips alone omit 32 pixels of the canonical SE elbow (east/south arms at a room NW corner). Missing-region bbox [60, 56, 64, 64] is shown as a separate topology-only component; remaining missing pixels after completion: 0. It does not solve the visible head-rail transition and is not production inventory.

## Negative controls

| Broken fixture | Intended failing check | Passing control / rejection proven |
| --- | --- | --- |
| repeat_displacement_1px | origins | True / True |
| broken_contact | frame | True / True |
| opaque_glass | pane | True / True |
| pane_hole | pane | True / True |
| doubled_support | support_spans | True / True |
| overlapping_glass | single_translucent_layer | True / True |
| anchor_mismatch_1px | relative_origin | True / True |

## Preservation and handoff

Counts before/after: {'manifest': 220, 'approved': 220, 'needs_human_review': 0} / {'manifest': 220, 'approved': 220, 'needs_human_review': 0}. Protected historical files: 1370; changed []; missing [].

D0/D1 sources, artwork, reports and snapshots are unchanged. Only the explicit D2 workspace is added to the authorized-reference safeguard; existing protected hashes are never exempted or refreshed.

Reproduce with `python tools/validate_architecture_d2.py`; complete suite command `python -m pytest -q`. Baseline: 67 passed. Captured results: test_results.json / test_results.txt.

Review ZIP: d2_geometry_review_bundle.zip. Montage: artifacts/d2_geometry_review_montage.png. Standalone native/source main and repeat scaffolds are beside the proposed contract. No production ingestion, D1/D2 approval, Batch 13, D3 or general junction repairs.

Complete suite: 94 passed; exit 0.
