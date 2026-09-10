# Architecture System

Architecture is deterministic rather than freeform AI art. The authority is `references/architecture/rastalr_architecture_v2/architecture_v2_spec.json`, together with the camera reference.

| Constraint | Standard |
| --- | --- |
| Logical grid | 32 px |
| Wall topology strip | 8 px, centered |
| Connection region | pixels 12–19 |
| Physical wall | ~44 px visible height, 8 px cap |
| Projection | rectangular-grid RPG oblique |

Generate exact N/E/S/W, ends, corners, T junctions, crosses, and openings from topology. Presentation is orientation-aware: north walls receive a full face, side walls a shallow boundary, and south walls a low cutaway. Doors, windows, and glass inherit those anchors. Decoration is usually a separate overlay.

The extracted reference sprites are retained under `references/architecture/rastalr_architecture_v2/`; use them for validation, not as permission to alter the underlying topology.

## Geometry evidence contract (D0)

New validators use Pillow-style **half-open rectangles `[left, top, right, bottom)`**: width is right minus left; height is bottom minus top. This is a coordinate convention, unrelated to a half-open door state. The canonical inclusive connection range 12–19 is `[12,20)`; do not change the canonical specification. Pillow crop/paste accepts these bounds; ImageDraw.rectangle includes its last pixel, so draw `(left,top,right-1,bottom-1)` when filling such a region.

Reports distinguish:

- `expected`: specification/contract values, declared geometry and requirements.
- `observed`: values actually read from PNG pixels, dimensions or placement metadata, with the method named. A placement record proves where a carrier was drawn, not where a painted feature lies inside it.
- `derived`: calculations from named inputs, such as source dimensions = native dimensions × integer scale or an anchor derived from a baseline.
- `human_visual_review`: explicit reviewer findings; pending until a human reviews. Automated technical checks cannot supply human approval.

Use `tools/rastalr_pipeline/geometry.py` for reusable evidence records, half-open region alpha checks, joins and anchored component checks. Each pass value compares actual observations against a requirement and has deliberately failing test coverage. The helpers are opt-in; historical validator and production API behavior remains backward-compatible. The existing generic full-coverage architecture QA is insufficient for glass and must be paired with an explicit material-region contract before any future D1 ingestion.

### Historical evidence limitations

C1/C2/C4/C5/C6/C7/C8 include literal structural coordinates, zero-deviation values and continuity/clipping conclusions in their reports. Those are declared or previously assessed values, not independent runtime feature measurements. C3 v1's `OBSERVED_*` landmarks are manually encoded observations; arithmetic differences are computed, but the landmarks are not detected from pixels by that script. C3 locked v2 and C8 compute actual changed-pixel/bounding-box evidence; this proves the stated edit-region restriction, not every other literal geometry conclusion. Alpha counts, component counts and image dimensions read at runtime remain computed evidence within their stated scope.

Batch 11's zero cumulative drift is an assembly-coordinate assertion; its alpha minimum is over the complete image, despite the edge-oriented field name. Some alternate floor tiles contain partial alpha; no-zero-alpha is not the same as fully opaque. Batch 12 reconstruction headline checks also include assertions rather than individual measured predicates. Existing reports, approvals, PNGs and provenance are retained; this note limits interpretation rather than rewriting history.

### D1 reference contract

See `references/architecture/master_validation_D0_v1/d1_geometry_alpha_contract.json` and the D0 technical report. Canonical D1 is 32×28, not a 32×52 back wall. Its 4 px side posts and 5 px rails surround the 24×18 pane. The ground topology strip and visible base rail have different roles: the 8 px strip is collision/connection topology; the 5 px rail is measured visible contact geometry.

D0 derives a numeric baseline mapping: logical-cell anchor `(16,20)` meets image anchor `(16,28)`, giving render origin `(0,-8)` relative to the cell. This documents previously unspecified numeric placement; it is not metadata recovered from a PNG. Frame alpha is 255; this unbroken pane requires alpha 1–254 and has no declared alpha-zero holes. The level/background stays separate.

Unchanged single panels produce doubled 8 px seam posts at a 32 px stride. The D0 reference assembler extends the last interior column through each nonterminal right-post strip; the following cell owns the 4 px shared post. This is a future adjacency-aware representation requirement, not a canonical edit, new logical asset or final appearance. L/T/cross diagnostics distinguish canonical topology contacts from unresolved visible carrier occlusion. No new visible adapter is assumed merely because a topology connector exists.

Reproduce reference evidence with `python tools/validate_architecture_d0.py`; run all tests with `python -m pytest -q`. D0 outputs stay outside production staging, manifest and catalog. Batch 12's approval Markdown renderer is idempotent; its pre-cleanup report is preserved in the D0 sources directory.
