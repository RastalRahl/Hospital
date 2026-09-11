# Independent D4 appearance validation

**PASS**. Reference-only; historical contract remains `PROPOSED_FOR_HUMAN_GEOMETRY_REVIEW`. No human production approval.

Actual supplied saved RGBA files were read without conversion or repair. Package builder inspected but never executed; local PASS claims were not copied.

| View | Native | Source | RGB changes | Alpha changes | Histogram |
| --- | --- | --- | ---: | ---: | --- |
| main | [32, 12] | [256, 96] | 384 | 0 | {'255': 240, '150': 144} |
| repeat | [32, 12] | [256, 96] | 384 | 0 | {'255': 216, '150': 168} |

Original archive plus 93 members preserved; all 15 reference copies compared to pinned Git bytes. Contract blob SHA1 checked exactly; no newline normalization needed.

Every8x8 block and native roundtrip checked. Alpha255 frame and150 glass match the contract. Tight carriers have no internal exterior pixels. Cell anchor[16,16], image anchor[16,4], origin[0,12], stride[32,0], normalization architecture_grid_preserving. These mappings are contract/metadata; rendered anchors are checked separately.

View relationships pass: True. Only24 continuation pixels differ, each copied from actual main column27; upper trim/lower rail unchanged. Two mutually exclusive views are ONE future logical asset.

- Run1: geometry True, selected actual RGBA True, transmission True; responding pane pixels 144, object response 10, frame response errors 0.
- Run2: geometry True, selected actual RGBA True, transmission True; responding pane pixels 312, object response 10, frame response errors 0.
- Run4: geometry True, selected actual RGBA True, transmission True; responding pane pixels 648, object response 10, frame response errors 0.

local: {'size_cells': [2, 1], 'west': 64, 'east': 128, 'north_centerline': 60, 'south_centerline': 92, 'D1_origin': [64, 36], 'D2_origin': [60, 36], 'D3_origin': [120, 36], 'D4_cell': [64, 76], 'D4_origin': [64, 88]}. Assembly pass True.
- southwest: {'side_base_exclusive': 92, 'front_top': 88, 'front_base_exclusive': 100}; independently measured overlap {'intentional_opaque': 32, 'unexpected_opaque': 0, 'unexpected_overlap': 0, 'missing_contact': 0, 'stacked_glass': 0, 'hidden_glass': 0}.
- southeast: {'side_base_exclusive': 92, 'front_top': 88, 'front_base_exclusive': 100}; independently measured overlap {'intentional_opaque': 32, 'unexpected_opaque': 0, 'unexpected_overlap': 0, 'missing_contact': 0, 'stacked_glass': 0, 'hidden_glass': 0}.
- northwest retained: {'opaque_overlap_pixels': 48, 'stacked_glass_pixels': 0, 'hidden_glass_pixels': 0, 'unexpected_overlap_pixels': 0, 'top_y': 36, 'base_y': 64, 'cap_y': 60, 'origin': [60, 36], 'cell': [48, 60]}.
- northeast retained: {'opaque_overlap_pixels': 48, 'stacked_glass_pixels': 0, 'hidden_glass_pixels': 0, 'unexpected_overlap_pixels': 0, 'top_y': 36, 'base_y': 64, 'cap_y': 60, 'origin': [120, 36], 'cell': [112, 60]}.
Changed scene pixels {'changed_scene_pixels': 768}; off-D4 violations 0. D1/D2/D3 saved input-layer bytes unchanged.

original: {'size_cells': [4, 2], 'west': 64, 'east': 192, 'north_centerline': 60, 'south_centerline': 124, 'D1_origin': [64, 36], 'D2_origin': [60, 36], 'D3_origin': [184, 36], 'D4_cell': [64, 108], 'D4_origin': [64, 120]}. Assembly pass True.
- southwest: {'side_base_exclusive': 124, 'front_top': 120, 'front_base_exclusive': 132}; independently measured overlap {'intentional_opaque': 32, 'unexpected_opaque': 0, 'unexpected_overlap': 0, 'missing_contact': 0, 'stacked_glass': 0, 'hidden_glass': 0}.
- southeast: {'side_base_exclusive': 124, 'front_top': 120, 'front_base_exclusive': 132}; independently measured overlap {'intentional_opaque': 32, 'unexpected_opaque': 0, 'unexpected_overlap': 0, 'missing_contact': 0, 'stacked_glass': 0, 'hidden_glass': 0}.
- northwest retained: {'opaque_overlap_pixels': 48, 'stacked_glass_pixels': 0, 'hidden_glass_pixels': 0, 'unexpected_overlap_pixels': 0, 'top_y': 36, 'base_y': 64, 'cap_y': 60, 'origin': [60, 36], 'cell': [48, 60]}.
- northeast retained: {'opaque_overlap_pixels': 48, 'stacked_glass_pixels': 0, 'hidden_glass_pixels': 0, 'unexpected_overlap_pixels': 0, 'top_y': 36, 'base_y': 64, 'cap_y': 60, 'origin': [184, 36], 'cell': [176, 60]}.
Changed scene pixels {'changed_scene_pixels': 1536}; off-D4 violations 0. D1/D2/D3 saved input-layer bytes unchanged.

relocated: {'size_cells': [4, 2], 'west': 96, 'east': 224, 'north_centerline': 92, 'south_centerline': 156, 'D1_origin': [96, 68], 'D2_origin': [92, 68], 'D3_origin': [216, 68], 'D4_cell': [96, 140], 'D4_origin': [96, 152]}. Assembly pass True.
- southwest: {'side_base_exclusive': 156, 'front_top': 152, 'front_base_exclusive': 164}; independently measured overlap {'intentional_opaque': 32, 'unexpected_opaque': 0, 'unexpected_overlap': 0, 'missing_contact': 0, 'stacked_glass': 0, 'hidden_glass': 0}.
- southeast: {'side_base_exclusive': 156, 'front_top': 152, 'front_base_exclusive': 164}; independently measured overlap {'intentional_opaque': 32, 'unexpected_opaque': 0, 'unexpected_overlap': 0, 'missing_contact': 0, 'stacked_glass': 0, 'hidden_glass': 0}.
- northwest retained: {'opaque_overlap_pixels': 48, 'stacked_glass_pixels': 0, 'hidden_glass_pixels': 0, 'unexpected_overlap_pixels': 0, 'top_y': 68, 'base_y': 96, 'cap_y': 92, 'origin': [92, 68], 'cell': [80, 92]}.
- northeast retained: {'opaque_overlap_pixels': 48, 'stacked_glass_pixels': 0, 'hidden_glass_pixels': 0, 'unexpected_overlap_pixels': 0, 'top_y': 68, 'base_y': 96, 'cap_y': 92, 'origin': [216, 68], 'cell': [208, 92]}.
Changed scene pixels {'changed_scene_pixels': 1536}; off-D4 violations 0. D1/D2/D3 saved input-layer bytes unchanged.

additional_size: {'size_cells': [3, 3], 'west': 64, 'east': 160, 'north_centerline': 60, 'south_centerline': 156, 'D1_origin': [64, 36], 'D2_origin': [60, 36], 'D3_origin': [152, 36], 'D4_cell': [64, 140], 'D4_origin': [64, 152]}. Assembly pass True.
- southwest: {'side_base_exclusive': 156, 'front_top': 152, 'front_base_exclusive': 164}; independently measured overlap {'intentional_opaque': 32, 'unexpected_opaque': 0, 'unexpected_overlap': 0, 'missing_contact': 0, 'stacked_glass': 0, 'hidden_glass': 0}.
- southeast: {'side_base_exclusive': 156, 'front_top': 152, 'front_base_exclusive': 164}; independently measured overlap {'intentional_opaque': 32, 'unexpected_opaque': 0, 'unexpected_overlap': 0, 'missing_contact': 0, 'stacked_glass': 0, 'hidden_glass': 0}.
- northwest retained: {'opaque_overlap_pixels': 48, 'stacked_glass_pixels': 0, 'hidden_glass_pixels': 0, 'unexpected_overlap_pixels': 0, 'top_y': 36, 'base_y': 64, 'cap_y': 60, 'origin': [60, 36], 'cell': [48, 60]}.
- northeast retained: {'opaque_overlap_pixels': 48, 'stacked_glass_pixels': 0, 'hidden_glass_pixels': 0, 'unexpected_overlap_pixels': 0, 'top_y': 36, 'base_y': 64, 'cap_y': 60, 'origin': [152, 36], 'cell': [144, 60]}.
Changed scene pixels {'changed_scene_pixels': 1152}; off-D4 violations 0. D1/D2/D3 saved input-layer bytes unchanged.

Ground center S, side terminal/trim[S-4,S), pane[S,S+6), base S+8 and ground strip[S-4,S+4) remain distinct. D4 draws over only its declared opaque contacts. Side shoulders retained; no masking or source edits. Original4x2, independently relocated+32,+32 and3x3 tested. Both historical36x36 corner crops reproduced independently with the saved scaffold2x1 control.

## Negative controls

- repeat_displacement: valid True; intended `origins` failure proven True.
- broken_frame: valid True; intended `frame` failure proven True.
- opaque_glass: valid True; intended `pane` failure proven True.
- pane_hole: valid True; intended `pane` failure proven True.
- doubled_support: valid True; intended `support_spans` failure proven True.
- wrong_terminal: valid True; intended `support_spans` failure proven True.
- stacked_glass: valid True; intended `single_layer` failure proven True.
- anchor_1px: valid True; intended `placement` failure proven True.
- baseline_confusion: valid True; intended `centerline_registration` failure proven True.
- missing_contact: valid True; intended `front_contact` failure proven True.
- wrong_side_terminal: valid True; intended `side_support` failure proven True.
- source_subpixel: valid True; intended `blocks` failure proven True.
- repeat_rgb_outside: valid True; intended `outside` failure proven True.
- repeat_rgb_continuation: valid True; intended `extension` failure proven True.

Protected files 2145; changed []; missing []. Counts before/after {'manifest': 220, 'approved': 220, 'needs_human_review': 0} / {'manifest': 220, 'approved': 220, 'needs_human_review': 0}.

Only new files in this named workspace are allowed. Existing hashes, including inside allowed prefixes, remain mandatory. Historical reports, contracts, snapshots and production records remain unchanged.

Reproduce: `python tools/validate_architecture_d4_appearance.py`. Full suite: `python -m pytest -q`. Starting suite269 passed.

Captured suite: {'command': 'python -m pytest -q', 'exit_code': 0, 'passed': 305, 'verified_baseline': 269, 'duration_seconds': 36.22, 'summary': '305 passed in 35.61s'}.

Blockers: []

No repaint, geometry change, approval, ingestion, Batch13, D5 or unrelated junction repair.
