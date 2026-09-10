# Architecture D0 technical report

Technical result: **PASS**. READY FOR D1 APPEARANCE.

Reference-only geometry and diagnostics. No D1 appearance, Batch 13, D2, or production ingestion.

Both attached audit files were extracted verbatim under sources/. User approval supersedes their historical proposal-status labels; it does not authorize production.

Rectangles: `[left, top, right, bottom)`. Expected/spec, observed/computed, derived, and human visual fields are distinct. Geometry measurements read PNG pixels and placement metadata.

Canonical glass: 32x28 native, source scale 8 = 256x224. Pane [4,5,28,23); posts [0,0,4,28) and [28,0,32,28); rails [4,0,28,5) and [4,23,28,28). Base contact [0,23,32,28). Ground topology strip [0,12,32,20).

Derived anchor: logical cell (16,20), image (16,28), render origin relative to cell (0,-8). At 8x: image anchor (128,224), origin (0,-64). Contact baseline matches existing full back carrier; no 32x52 glass carrier.

Frame alpha is exactly 255. Pane alpha is 1..254; canonical has 421 pixels at 150 and 11 at 210. Zero is an accidental hole for this unbroken pane. A fully clear region requires explicit contract revision. Background/object layers stay separate.

Repeat: preserve 32 px stride. Nonterminal cells extend the last interior column through their right post region; next cell owns the shared 4 px post. Terminal cell keeps its right post. No overlapping glass, trim, padding, or canonical edit.

D1 context joins unchanged solid wall carriers at baseline y=84 (wall origin y=32, glass origin y=56). Both five-pixel contact strips and lateral adjacency are measured; the intentional 24 px height difference is retained.

| Run | Geometry/alpha | Background transmission |
| --- | --- | --- |
| 1 panels | True | True |
| 2 panels | True | True |
| 4 panels | True | True |

## Integration

| Scene | Computed technical pass | Wall overlap pixels |
| --- | --- | --- |
| connected_rooms | True | 0 |
| l_junction | True | 400 |
| t_junction | True | 400 |
| cross_junction | True | 1040 |

Connected rooms: BFS proves connectivity through the separately defined C8 opening in the level layout. The unchanged C8 PNG remains an opaque static recess. L/T/cross use canonical topology and unchanged approved carriers; overlaps are exposed, not silently passed as visual continuity. New human visual approval is not claimed.

## Negative evidence

| Broken fixture | Intended failing check | Valid control passes / failure proven |
| --- | --- | --- |
| join_shift_1px | placements | True / True |
| contact_pixel_removed | base_0 | True / True |
| fake_opaque_glass | glass_0 | True / True |
| pane_alpha_hole | glass_0 | True / True |
| double_seam | post_runs | True / True |
| overlap_darkening | single_layer_alpha | True / True |
| component_offset_1px | origin | True / True |

## Scope findings

- Canonical standalone glass duplicates its 4 px posts to 8 px when tiled unchanged. Shared-edge implementation required; canonical remains unchanged.
- L/T/cross topology is valid, but full approved render carriers overlap. Topology success alone cannot approve cap/occlusion appearance or prove a new adapter is necessary.
- Cross north-arm carrier is fully hidden by the central full-height back-wall face in the tested draw order; cross and T render similarly. Future multi-direction junction presentation/occlusion policy is unresolved; technical topology masks do not fix visible art.
- D1 numeric baseline anchor is a documented derivation; PNG dimensions do not encode a logical footprint.
- Batch 11 alternate floors contain partial alpha despite historical opaque-box wording; diagnostics deliberately use approved opaque plain floors. No artwork altered.

No new visible adapter is proven necessary; resolve junction cap/occlusion review before claiming all-direction visual coverage. This does not block straight D1 appearance under the explicit shared-edge contract.

Production: {'manifest': 220, 'approved': 220, 'needs_human_review': 0}; 1225 protected file hashes unchanged. Baseline: `sources/production_before.json`.

Batch 12 Markdown repaired from existing approved JSON; original duplicate report retained as sources/batch_12_qa_before.md. Repeated approval rendering is idempotent and preserves the recorded timestamp. JSON decisions, artworks, components and historical bundles remain untouched.

Reproduce: `python tools/validate_architecture_d0.py`. Full test evidence: `test_results.json` / `test_results.txt`. Baseline suite: 17 passed.

Review: `artifacts/chatgpt_review_montage.png`; geometry: `d1_geometry_alpha_contract.json`; native/source scaffolds and separate glass/background/scene PNGs: `artifacts/`.

Stop after D0. No new human-approved artwork or manifest record was created.

Complete automated suite: **PASS**; 39 passed (baseline 17, added 22). Command and captured output are recorded in test_results.json and test_results.txt.
