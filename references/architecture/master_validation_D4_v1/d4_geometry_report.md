# D4 front cutaway geometry proposal

**READY FOR HUMAN GEOMETRY REVIEW**. Computed conformance PASS to `PROPOSED_FOR_HUMAN_GEOMETRY_REVIEW`; no human approval.

Canonical:32px grid,8px centered ground strip, axis-aligned oblique camera, shallow foreground cutaway and integer8x export. Canonical solid front wall measures32x20 (8px trim +12px face). This is context, not D4 canvas authority.

Proposed D4:32x12 RGBA /256x96 source; main and repeat are mutually exclusive views of one future asset. Native envelope[0,0,32,12), footprint1x1, cell anchor[16,16], image anchor[16,4], relative origin[0,12], stride[32,0]. Frame255, pane150, undeclared exterior0 (no exterior pixels within this tight carrier). No trim, padding, rotated artwork or masks.

Corner-first derivation: side south center S is its terminal support exclusive edge; terminal support spans[S-4,S). D4 trim occupies that same4px band. The proposed8px front face below S contains6px pane and2px lower rail. Thus image top S-4, ground center S, strip bottom S+4, image base S+8 are distinct. The12px carrier is a proposed foreground cutaway, not a change to installed physical height. Side north returns retain their existing24px drop.

Ownership: each horizontal cell owns its left4px post; only main owns the right closing4px post. Repeat declares pane through x32. Side final main views retain their12x4 terminal support. D4 trim intersects each inward8x4 section; side outer4px shoulders remain visible. D4 draws over those opaque contacts only; no side glass is erased. Technical8x4 ground half-strip caps complete NE/NW elbow topology without visible components.

Each reconstruction uses actual saved D4 files, validated D1 main/repeat, validated D2/D3 corner_repeat then main (or corner_main for depth1), unchanged approved floor and separate object. Layers: floor, object, D2, D3, D1, D4. No entry opening is implied.

original size [4, 2]: conformance True; object samples/responses {'object_pane_samples': 72, 'object_responses': 72}.
- southwest: observed {'side_base_exclusive': 124, 'front_top': 120, 'front_base_exclusive': 132}; overlap {'intentional_opaque': 32, 'unexpected_opaque': 0, 'unexpected_overlap': 0, 'missing_contact': 0, 'stacked_glass': 0, 'hidden_glass': 0}.
- southeast: observed {'side_base_exclusive': 124, 'front_top': 120, 'front_base_exclusive': 132}; overlap {'intentional_opaque': 32, 'unexpected_opaque': 0, 'unexpected_overlap': 0, 'missing_contact': 0, 'stacked_glass': 0, 'hidden_glass': 0}.
- northwest retained: {'opaque_overlap_pixels': 48, 'stacked_glass_pixels': 0, 'hidden_glass_pixels': 0, 'unexpected_overlap_pixels': 0, 'top_y': 36, 'base_y': 64, 'cap_y': 60, 'origin': [60, 36], 'cell': [48, 60]}.
- northeast retained: {'opaque_overlap_pixels': 48, 'stacked_glass_pixels': 0, 'hidden_glass_pixels': 0, 'unexpected_overlap_pixels': 0, 'top_y': 36, 'base_y': 64, 'cap_y': 60, 'origin': [184, 36], 'cell': [176, 60]}.
relocated size [4, 2]: conformance True; object samples/responses {'object_pane_samples': 72, 'object_responses': 72}.
- southwest: observed {'side_base_exclusive': 156, 'front_top': 152, 'front_base_exclusive': 164}; overlap {'intentional_opaque': 32, 'unexpected_opaque': 0, 'unexpected_overlap': 0, 'missing_contact': 0, 'stacked_glass': 0, 'hidden_glass': 0}.
- southeast: observed {'side_base_exclusive': 156, 'front_top': 152, 'front_base_exclusive': 164}; overlap {'intentional_opaque': 32, 'unexpected_opaque': 0, 'unexpected_overlap': 0, 'missing_contact': 0, 'stacked_glass': 0, 'hidden_glass': 0}.
- northwest retained: {'opaque_overlap_pixels': 48, 'stacked_glass_pixels': 0, 'hidden_glass_pixels': 0, 'unexpected_overlap_pixels': 0, 'top_y': 68, 'base_y': 96, 'cap_y': 92, 'origin': [92, 68], 'cell': [80, 92]}.
- northeast retained: {'opaque_overlap_pixels': 48, 'stacked_glass_pixels': 0, 'hidden_glass_pixels': 0, 'unexpected_overlap_pixels': 0, 'top_y': 68, 'base_y': 96, 'cap_y': 92, 'origin': [216, 68], 'cell': [208, 92]}.
additional_size size [3, 3]: conformance True; object samples/responses {'object_pane_samples': 72, 'object_responses': 72}.
- southwest: observed {'side_base_exclusive': 156, 'front_top': 152, 'front_base_exclusive': 164}; overlap {'intentional_opaque': 32, 'unexpected_opaque': 0, 'unexpected_overlap': 0, 'missing_contact': 0, 'stacked_glass': 0, 'hidden_glass': 0}.
- southeast: observed {'side_base_exclusive': 156, 'front_top': 152, 'front_base_exclusive': 164}; overlap {'intentional_opaque': 32, 'unexpected_opaque': 0, 'unexpected_overlap': 0, 'missing_contact': 0, 'stacked_glass': 0, 'hidden_glass': 0}.
- northwest retained: {'opaque_overlap_pixels': 48, 'stacked_glass_pixels': 0, 'hidden_glass_pixels': 0, 'unexpected_overlap_pixels': 0, 'top_y': 36, 'base_y': 64, 'cap_y': 60, 'origin': [60, 36], 'cell': [48, 60]}.
- northeast retained: {'opaque_overlap_pixels': 48, 'stacked_glass_pixels': 0, 'hidden_glass_pixels': 0, 'unexpected_overlap_pixels': 0, 'top_y': 36, 'base_y': 64, 'cap_y': 60, 'origin': [152, 36], 'cell': [144, 60]}.

Original/relocated structure comparison: {'checks': {'translated_structure': {'expected': 0, 'observed': 0, 'method': 'Compare independently rendered saved structures after removing +32,+32 translation', 'units': 'native_px', 'pass': True}}, 'pass': True}. Runs1/2/4 and separate light/dark/colored/toggled-object transmission all independently checked.

## Negative controls

- repeat_displacement: passing valid control True; intended `origins` failure proven True.
- broken_frame: passing valid control True; intended `frame` failure proven True.
- opaque_glass: passing valid control True; intended `pane` failure proven True.
- pane_hole: passing valid control True; intended `pane` failure proven True.
- doubled_support: passing valid control True; intended `support_spans` failure proven True.
- wrong_terminal: passing valid control True; intended `support_spans` failure proven True.
- stacked_glass: passing valid control True; intended `single_layer` failure proven True.
- anchor_1px: passing valid control True; intended `placement` failure proven True.
- baseline_confusion: passing valid control True; intended `centerline_registration` failure proven True.
- missing_contact: passing valid control True; intended `front_contact` failure proven True.
- wrong_side_terminal: passing valid control True; intended `side_support` failure proven True.
- source_subpixel: passing valid control True; intended `blocks` failure proven True.

Protected historical files 2022; changed []; missing []. Production before/after: {'manifest': 220, 'approved': 220, 'needs_human_review': 0} / {'manifest': 220, 'approved': 220, 'needs_human_review': 0}.

Safeguards permit only new D4 workspace files; existing hashes remain mandatory even within allowed directories. No historical baseline is refreshed.

Reproduce: `python tools/validate_architecture_d4.py`. Complete suite: `python -m pytest -q`; recorded prior baseline237.

Captured complete suite: {'command': 'python -m pytest -q', 'exit_code': 0, 'passed': 269, 'recorded_baseline': 237, 'duration_seconds': 96.39, 'summary': '269 passed in 94.52s (0:01:34)'}.

Blockers: []

Pending human geometry review:6px front-pane legibility, foreground height and exposed4px shoulders. This is a deliberately stylized cutaway, not final appearance or a continuous equal-height rail. No assets or approval records changed; no ingestion, Batch13, D5 or other junction work.
