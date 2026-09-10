# D1 independent reference validation

Result: **PASS**. Reference-only; no production approval or ingestion.

The saved main and repeat PNGs are two mutually exclusive implementation views of one proposed logical asset. Package reports and build tools were read as supporting context; no supplied tool was executed and no preview was used as artwork.

Authority: committed D0 contract at `9ed992f57585d77448f3e396b8f4dc6f25aa5987`. All rectangles use `[left, top, right, bottom)`. JSON separates expected/observed checks, derived placement information, and visual findings.

## File and pixel checks

| Check | Independently observed | Pass |
| --- | --- | --- |
| main_mode | `RGBA` | True |
| main_dimensions | `[32, 28]` | True |
| repeat_mode | `RGBA` | True |
| repeat_dimensions | `[32, 28]` | True |
| main_8x_mode | `RGBA` | True |
| main_8x_dimensions | `[256, 224]` | True |
| repeat_8x_mode | `RGBA` | True |
| repeat_8x_dimensions | `[256, 224]` | True |
| main_8x_blocks | `0` | True |
| main_roundtrip | `0` | True |
| repeat_8x_blocks | `0` | True |
| repeat_roundtrip | `0` | True |
| main_alpha_lock | `0` | True |
| main_rgb_changes | `796` | True |
| main_alpha_histogram | `{'150': 421, '210': 11, '255': 464}` | True |
| left_post | `{'alpha_min': 255, 'alpha_max': 255, 'violations': 0, 'sample_count': 112}` | True |
| right_post | `{'alpha_min': 255, 'alpha_max': 255, 'violations': 0, 'sample_count': 112}` | True |
| top_rail | `{'alpha_min': 255, 'alpha_max': 255, 'violations': 0, 'sample_count': 120}` | True |
| bottom_rail | `{'alpha_min': 255, 'alpha_max': 255, 'violations': 0, 'sample_count': 120}` | True |
| pane_locked_alpha_values | `[150, 210]` | True |
| visual_envelope | `[0, 0, 32, 28]` | True |
| repeat_column_extension | `0` | True |
| repeat_outside_extension | `0` | True |

Frame regions: left [0,0,4,28), right [28,0,32,28), top [4,0,28,5), bottom [4,23,28,28). Required alpha 255; pane [4,5,28,23) retains alpha 150/210 pixel-for-pixel. No zero-alpha pane holes or opaque fake glass. The intentional full-canvas frame contacts are not treated as generic prop clipping.

## Repetition and transmission

| Panels | Run checks | Separate-background checks |
| --- | --- | --- |
| 1 | True | True |
| 2 | True | True |
| 4 | True | True |

Runs are assembled from the supplied native files at 32 px stride. RGB checks use the D1 candidate, not canonical colors. Shared posts remain 4 px, the closing post remains present, pane widths are 28 px for nonterminal views and 24 px for the terminal view. Layer counts and output alpha are measured independently.

Light, dark, colored and colored-with-object backgrounds are separate PNGs. Source-over equations, all-pane background response, frame invariance and object-toggle response are checked from actual pixels.

## Anchors and context

Cell anchor [16,20], image anchor [16,28], render origin [0,-8]; architecture_grid_preserving normalization. Unchanged approved Batch 11 walls/floors surround the supplied four-panel run. Original and relocated contexts test relative anchors, shared baselines, adjacency, actual frame contacts and compositing.

- original: pass=True; placements/baseline `{'wall_origins': [[32, 32], [192, 32]], 'glass_origin': [64, 56], 'logical_cell_origin': [64, 64], 'shared_baseline': 84}`.
- relocated: pass=True; placements/baseline `{'wall_origins': [[64, 64], [224, 64]], 'glass_origin': [96, 88], 'logical_cell_origin': [96, 96], 'shared_baseline': 116}`.

No L/T/cross appearance validation or repairs were performed. Their D0 presentation limitations remain.

## Negative controls

| Fixture | Intended failing check | Failure proven with passing valid control |
| --- | --- | --- |
| placement_drift_1px | placements | True |
| broken_base_contact | base_0 | True |
| opaque_glass | glass_0 | True |
| zero_alpha_glass | glass_0 | True |
| doubled_post | post_runs | True |
| overlapping_glass | single_layer_alpha | True |

## Preservation and test safeguard

The original ZIP and every extracted package member are preserved under sources/. New diagnostics and reports are outside sources/. Exact member bytes and initial SHA-256 hashes are checked on every validation run.

Task counts before/after: `{'manifest': 220, 'approved': 220, 'needs_human_review': 0}` / `{'manifest': 220, 'approved': 220, 'needs_human_review': 0}`. Protected existing files: 1284. Missing: []; changed: [].

D0's historical snapshot and reports are unchanged. Its safeguard compares every historical path/hash and permits only additions beneath the explicitly authorized D1 workspace. Existing files are never exempted, even if they are under an allowed prefix. Temporary-fixture tests reject modification, deletion, count changes, unrelated additions and prefix lookalikes.

Full automated suite evidence is in test_results.json and test_results.txt; baseline was 39 passed. Reproduce validation with `python tools/validate_architecture_d1.py`; run tests with `python -m pytest -q`.

## Review limits

User reports ChatGPT appearance review passed for proceeding to technical validation; this is not final human production approval. Technical transmission proves live background response, not semantic absence of a painted scene. Direct visual inspection of the actual supplied candidate is recorded separately in visual_review.json.

Blockers: none.

Review montage: artifacts/d1_review_montage.png. Production remains unchanged; no Batch 13, no manifest/catalog entry, no D2.

Complete test suite: **PASS**, 67 passed; baseline 39.
