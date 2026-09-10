# Independent D2 appearance validation

**PASS** — reference-only technical validation. Historical contract stays `PROPOSED_FOR_HUMAN_GEOMETRY_REVIEW`. No production approval.

Actual saved candidate PNGs were read; no montage crops or package builders were used. Expected/spec, computed observations, derived placement and review evidence are separate in JSON.

| View | Native RGBA | Source RGBA | Alpha changed | RGB changed | Zero-alpha RGBA changed |
| --- | --- | --- | ---: | ---: | ---: |
| main | [12, 32] | [96, 256] | 0 | 384 | 0 |
| repeat | [12, 32] | [96, 256] | 0 | 384 | 0 |
| corner_main | [12, 56] | [96, 448] | 0 | 496 | 0 |
| corner_repeat | [12, 56] | [96, 448] | 0 | 496 | 0 |

Package integrity: True; 51 extracted members and original archive preserved. Packaged source copies match pinned Git sources. Exact nearest-neighbor 8x blocks, alpha regions, and native roundtrips were independently checked.

View relationships/anchors: True. Main/repeat image anchor [4,16], origin [12,0]; corner image anchor [4,40], origin [12,-24]; logical-cell anchor [16,16]. Four mutually exclusive implementation views belong to one future logical asset. Corner bodies equal corresponding straight candidates; repeat only extends candidate row27 within [2,28,10,32).

- straight_1: geometry True, candidate selection True, transmission True.
- corner_1: geometry True, candidate selection True, transmission True.
- straight_2: geometry True, candidate selection True, transmission True.
- corner_2: geometry True, candidate selection True, transmission True.
- straight_4: geometry True, candidate selection True, transmission True.
- corner_4: geometry True, candidate selection True, transmission True.

Corner original: {'D1_origin': [64, 36], 'D2_origin': [60, 36], 'D2_cell': [48, 60], 'intersection': [64, 60], 'D1_baseline_y': 64, 'D1_top_y': 36, 'D2_cap_y': 60, 'opaque_overlap': 48, 'stacked_glass': 0, 'hidden_glass': 0}. All declared corner checks pass: True.

Corner relocated: {'D1_origin': [96, 68], 'D2_origin': [92, 68], 'D2_cell': [80, 92], 'intersection': [96, 92], 'D1_baseline_y': 96, 'D1_top_y': 68, 'D2_cap_y': 92, 'opaque_overlap': 48, 'stacked_glass': 0, 'hidden_glass': 0}. All declared corner checks pass: True.

Draw order is separate background, D2, unchanged D1. Required top contact, glazed reveal and return frame are checked separately from the baseline. Straight/corner runs preserve 32px ground stride, single 4px supports and terminal closure. Glass alpha150 transmits separate light/dark/colored/object backgrounds; opaque frame alpha255 remains invariant. Approved Batch11 wall/floor contexts are rebuilt independently at original and relocated origins.

## Negative controls

- repeat_displacement_1px: valid control True; intended rejection proven True (origins).
- broken_contact: valid control True; intended rejection proven True (frame).
- opaque_glass: valid control True; intended rejection proven True (pane).
- pane_hole: valid control True; intended rejection proven True (pane).
- doubled_support: valid control True; intended rejection proven True (support_spans).
- stacked_glass: valid control True; intended rejection proven True (single_glass_layer).
- anchor_mismatch_1px: valid control True; intended rejection proven True (render_origin).
- missing_corner_return: valid control True; intended rejection proven True (upper_contact).
- corner_displacement_1px: valid control True; intended rejection proven True (overlap_ownership).
- source_subpixel: valid control True; intended rejection proven True (exact 8x blocks).

Protected files: 1537; changed []; missing []. Counts before/after: {'manifest': 220, 'approved': 220, 'needs_human_review': 0} / {'manifest': 220, 'approved': 220, 'needs_human_review': 0}. Historical contracts, reports, snapshots, D1 and approved artwork remain unchanged.

The only historical test adjustment permits additions in this named workspace; existing hashes remain mandatory, including within allowed directories. Package sources additionally have immutable archive/member hash checks.

Run `python tools/validate_architecture_d2_appearance.py`; full suite `python -m pytest -q`. Baseline verified: 124 passed.

Captured complete suite: 160 passed; exit 0.

Blockers: []

ChatGPT review is supporting appearance evidence. No final human production approval, ingestion, Batch13, D3 or all-direction junction coverage is claimed.
