# D3 right-side geometry proposal

**READY FOR HUMAN GEOMETRY REVIEW**. Computed conformance PASS to `PROPOSED_FOR_HUMAN_GEOMETRY_REVIEW`; no human approval.

Structural rectangles alone were reflected: cell [l,r) becomes [32-r,32-l); local image uses [12-r,12-l). No D1/D2 finished sprite or scene was flipped. Half-open edges and pixel indices remain distinct.

Main/repeat: native12x32, source96x256, envelope[0,0,12,32), origin[8,0], image anchor[8,16]. Corner-main/repeat: native12x56, source96x448, envelope[0,0,12,56), origin[8,-24], image anchor[8,40]. Cell anchor[16,16], logical footprint1x1, NS strip[12,0,20,32), depth stride[0,32]. Exact integer exports only.

Canonical right wall measures20x32; its cell envelope x0..20 is consistent with the narrower proposed D3 band x8..20. This retains D2 family proportions with no departure. Rectangles/dimensions are derived proposals, not measured canonical D3 geometry. All frame alpha255, pane150, undeclared exterior0. Four mutually exclusive views belong to one future logical asset.

NE actual computed evidence: {'opaque_overlap_pixels': 48, 'stacked_glass_pixels': 0, 'hidden_glass_pixels': 0, 'unexpected_overlap_pixels': 0, 'top_y': 36, 'base_y': 64, 'cap_y': 60, 'origin': [88, 36], 'cell': [80, 60]}. Ground center [96,60] differs from D1 baseline y64. D1 extends west from its existing terminal post. Upper and shallow contacts pass independently; the deliberate cutaway remains24px. Expected overlap derives from4x4 upper plus8x4 lower contacts; the observed opaque overlap is 48px, unexpected 0, stacked glass 0, hidden glass 0.

SW elbow missing pixels before north-cap ownership: 16; after: 0. Ground mask is technical evidence only and is never rendered over the artwork.

One/two/four straight and corner-starting runs pass saved RGBA selection, 32px placement, 4px shared support, closure and separate light/dark/colored/object transmission. Original and relocated approved right-wall/floor contexts pass.

The open-front enclosure uses four actual D1 panels (repeat,repeat,repeat,main), actual D2 corner_repeat/main down the left and D3 corner_repeat/main down the right. No alternative views are stacked. Both upper/base corner checks pass; D1 composited pixels and D2 layer pixels are unchanged. The independent +32,+32 enclosure has an identical translated structure. No front partition or all-direction junction claim.

## Negative controls

- wrong_left_origin: valid control True; intended `anchor` rejection proven True.
- anchor_1px: valid control True; intended `anchor` rejection proven True.
- missing_return: valid control True; intended `upper_contact` rejection proven True.
- displaced_return: valid control True; intended `upper_contact` rejection proven True.
- D1_wrong_terminal: valid control True; intended `D1_terminal_post` rejection proven True.
- repeat_drift_1px: valid control True; intended `origins` rejection proven True.
- broken_contact: valid control True; intended `frame` rejection proven True.
- pane_hole: valid control True; intended `pane` rejection proven True.
- opaque_glass: valid control True; intended `pane` rejection proven True.
- doubled_support: valid control True; intended `support_spans` rejection proven True.
- D3_wrong_terminal: valid control True; intended `support_spans` rejection proven True.
- stacked_glass: valid control True; intended `single_glass_layer` rejection proven True.

Protected historical files: 1688; changed []; missing []. Counts before/after: {'manifest': 220, 'approved': 220, 'needs_human_review': 0} / {'manifest': 220, 'approved': 220, 'needs_human_review': 0}. Manifest/catalog and all historical sources/reports/contracts/snapshots remain unchanged. Only new D3 files are allowed; old hashes remain mandatory.

Run `python tools/validate_architecture_d3.py`; complete suite `python -m pytest -q`. Actual starting suite:160 passed.

Captured suite: 198 passed; exit 0.

Blockers: []

Human review remains pending for right-side geometry and the two local corners. Flat D3 colors are intentional; future highlights must be authored for upper-left lighting. No approval, final appearance, ingestion, Batch13, D4 or unrelated junction repair.
