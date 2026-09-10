# Independent D3 appearance validation

**PASS**. Reference-only. Historical contract remains `PROPOSED_FOR_HUMAN_GEOMETRY_REVIEW`. No human production approval.

Actual saved RGBA inputs were checked without conversion or repairs. Package scripts were not executed; local PASS claims are not repository observations.

| View | Native | Source | Alpha changes | RGB changes | Invisible RGBA changes |
| --- | --- | --- | ---: | ---: | ---: |
| main | [12, 32] | [96, 256] | 0 | 384 | 0 |
| repeat | [12, 32] | [96, 256] | 0 | 384 | 0 |
| corner_main | [12, 56] | [96, 448] | 0 | 496 | 0 |
| corner_repeat | [12, 56] | [96, 448] | 0 | 496 | 0 |

Original ZIP and 81 members preserved; 12 packaged source PNGs compared to committed bytes. Pinned contract Git SHA-1 verified; exact checkout hash protected (LF/CRLF normalization is used only for pinned text comparison). Package integrity: True.

View relationships and metadata mapping: True. Main/repeat origin[8,0], image anchor[8,16]; corner origin[8,-24], image anchor[8,40]; cell anchor[16,16]. Four mutually exclusive views are one future logical asset. Body and upper-return RGBA match exactly; repeat extends only row27 within [2,28,10,32).

- straight_1: geometry True, view selection True, transmission True.
- corner_1: geometry True, view selection True, transmission True.
- straight_2: geometry True, view selection True, transmission True.
- corner_2: geometry True, view selection True, transmission True.
- straight_4: geometry True, view selection True, transmission True.
- corner_4: geometry True, view selection True, transmission True.

northeast_original NE measured: {'opaque_overlap_pixels': 48, 'stacked_glass_pixels': 0, 'hidden_glass_pixels': 0, 'unexpected_overlap_pixels': 0, 'top_y': 36, 'base_y': 64, 'cap_y': 60, 'origin': [88, 36], 'cell': [80, 60]}.

northeast_relocated NE measured: {'opaque_overlap_pixels': 48, 'stacked_glass_pixels': 0, 'hidden_glass_pixels': 0, 'unexpected_overlap_pixels': 0, 'top_y': 68, 'base_y': 96, 'cap_y': 92, 'origin': [120, 68], 'cell': [112, 92]}.

enclosure_original NE measured: {'opaque_overlap_pixels': 48, 'stacked_glass_pixels': 0, 'hidden_glass_pixels': 0, 'unexpected_overlap_pixels': 0, 'top_y': 36, 'base_y': 64, 'cap_y': 60, 'origin': [184, 36], 'cell': [176, 60]}.
enclosure_original NW measured separately: {'opaque_overlap_pixels': 48, 'stacked_glass_pixels': 0, 'hidden_glass_pixels': 0, 'unexpected_overlap_pixels': 0, 'top_y': 36, 'base_y': 64, 'cap_y': 60, 'origin': [60, 36], 'cell': [48, 60]}.

enclosure_relocated NE measured: {'opaque_overlap_pixels': 48, 'stacked_glass_pixels': 0, 'hidden_glass_pixels': 0, 'unexpected_overlap_pixels': 0, 'top_y': 68, 'base_y': 96, 'cap_y': 92, 'origin': [216, 68], 'cell': [208, 92]}.
enclosure_relocated NW measured separately: {'opaque_overlap_pixels': 48, 'stacked_glass_pixels': 0, 'hidden_glass_pixels': 0, 'unexpected_overlap_pixels': 0, 'top_y': 68, 'base_y': 96, 'cap_y': 92, 'origin': [92, 68], 'cell': [80, 92]}.

The source-over check samples every pane pixel, including the narrow glazed return, on separate light/dark/colored/object backgrounds. Frame alpha255 is invariant; glass alpha150 responds; exterior alpha0 stays separate. Exact 8x blocks and native roundtrips pass.

Draw order: separate background, D2 when present, D3, unchanged D1. Each back corner has its own overlap measurement; ground center and baseline remain distinct and the cutaway is24px. D1 final composited pixels and D2 layer remain exact. Independently relocated corner/enclosure structures match after a32px translation. Right-wall contexts use unchanged approved wall/floor files. No front partition.

## Negative controls

- wrong_left_origin: valid True; intended failure proven True (anchor).
- anchor_1px: valid True; intended failure proven True (anchor).
- missing_return: valid True; intended failure proven True (upper_contact).
- displaced_return: valid True; intended failure proven True (upper_contact).
- D1_wrong_terminal: valid True; intended failure proven True (D1_terminal_post).
- repeat_drift_1px: valid True; intended failure proven True (origins).
- broken_contact: valid True; intended failure proven True (frame).
- pane_hole: valid True; intended failure proven True (pane).
- opaque_glass: valid True; intended failure proven True (pane).
- doubled_support: valid True; intended failure proven True (support_spans).
- D3_wrong_terminal: valid True; intended failure proven True (support_spans).
- stacked_glass: valid True; intended failure proven True (single_glass_layer).
- source_subpixel: valid True; intended failure proven True (source_subpixel).
- invisible_rgb: valid True; intended failure proven True (invisible_rgb).
- broken_repeat: valid True; intended failure proven True (repeat_outside).
- broken_corner_body: valid True; intended failure proven True (corner_body_main).

Protected files 1810; changed []; missing []. Counts before/after {'manifest': 220, 'approved': 220, 'needs_human_review': 0} / {'manifest': 220, 'approved': 220, 'needs_human_review': 0}. Historical sources, reports, proposed contracts, snapshots, approved artwork and inventory bytes remain unchanged.

Only the explicitly named new appearance workspace is allowed by addition safeguards. Existing-file hashes remain mandatory, including inside allowed prefixes. Reused helpers accept an explicit output directory/reference path; defaults and historical evidence are unchanged.

Reproduce: `python tools/validate_architecture_d3_appearance.py`. Complete suite: `python -m pytest -q`. Actual starting suite198 passed.

Captured complete suite 237 passed; exit 0.

Blockers: []

No candidate edits, human approval, production ingestion, Batch13, D4 or unrelated junction repairs.
