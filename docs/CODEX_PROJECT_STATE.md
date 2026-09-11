# Codex project state

Verified 2026-09-11. Operational handoff for future Codex sessions; read with `AGENTS.md`. Codex owns planning, implementation, review preparation, QA, Godot integration and Git delivery. Human visual/production decisions stay with the user, directly in Codex.

## Canonical product roadmap and current backlog

- The user explicitly requested target revision and inclusion of every existing asset. [ASSET_ROADMAP.md](ASSET_ROADMAP.md) revision 2 supersedes the original 400-asset category plan preserved at `2ae8aa1`.
- New working target: **373 logical assets = all 224 existing + 149 named additions**. Includes **352 clean environment/interaction assets and 21 abandoned-condition assets**. All four existing pending glass parents remain included, parked and unapproved; no new glass/windows are planned.
- [ASSET_COVERAGE_STATUS.md](ASSET_COVERAGE_STATUS.md) contains all 18 reconciled categories, scopes, practical room proofs, all 149 proposed IDs, and a complete retained register of all 224 current IDs. Current status remains **220 approved / 4 pending**. No negative category gaps or unnamed filler budget.
- After cleanup, next five families: **architecture 12; bathrooms/utility 18; signage/decor/safety 22; staff/admin 14; combined clinical completion 11**. Then exterior 17, food service 14, morgue 8, inventory/UI 13 and abandoned 20. This is planning, not new production authorization.
- Main revision: prioritize usable building/support spaces over further specialist equipment and excessive damaged variants. Retain every existing asset regardless of overlap; share counters, chairs, carts, sinks and autoclave across rooms instead of counting duplicates.
- Revision 2 begins at `2ae8aa1`; documentation checks and **379 tests passed in 104.75s**, recorded in the coverage file. No artwork, approvals, manifest categories or demo behavior change.

## Inventory and approval boundary

- Verified manifest: **224 logical assets / 220 approved / 4 needs_human_review**. Catalog: **224 rows**.
- Batches 01–12 are approved; Architecture Foundation (11) has 20 logical assets and Doors & Openings (12) has 8.
- Batch 13 glass: back, side_left, side_right and front_cutaway (`hospital_glass_partition_<orientation>_01`) remain formally pending. Its 12 exclusive views represent four logical assets. User runtime visual acceptance is recorded in the supplied handoff and current request; production approval metadata has not been changed.
- Bootstrap was documentation-only. The user subsequently authorized a reference-only junction prototype ("Do it"); it is now implemented. Production artwork, staging and approvals remain unchanged. No D5 or new asset generation before cleanup is resolved.

## Active repairs and practical review

- Open sliding door: `demo/hospital_integration/repair_candidates/sliding_door_open_alpha_v1/repair.json`. Candidate visually accepted by the user per handoff/current request, not promoted. Passage `[7,14,59,48)` has 1,768 alpha changes; RGB and parked leaves unchanged. Revise the existing logical asset and preserve the previous approved version/provenance.
- Foundation walls: [family findings](../demo/hospital_integration/repair_candidates/foundation_wall_refresh_family_v1/findings.md) and [review montage](../demo/hospital_integration/repair_candidates/foundation_wall_refresh_family_v1/wall_family_review_montage.png). Twelve reference-only repairs: four back, two left, two right, four front. Status: **READY FOR WALL-FAMILY REPAIR STAGING**. V2 visual language is human-approved; final propagated-family production approval is outstanding.
- Bootstrap visual inspection: continuous cap/base and quiet ivory surfaces remove the dominant repeated panel borders in the committed Godot and mixed-run montage. Subsequent user review accepts the surface improvement but flags incorrect perpendicular wall intersections. **Production promotion is on hold pending junction repair/review**; the earlier recommendation to promote with limitations is withdrawn.
- Follow-up inspection of full-resolution `godot_refreshed.png` and both refreshed north-corner crops confirms disconnected cap/face transitions. In `build_demo.py`, the north wall occupies y=44..95 while the outer side walls begin at y=96, outside its x span: their painted regions only meet at a diagonal corner. The internal side divider similarly begins at the north wall's base, and its lower end abuts the left edge of the full-height patient-room wall without a joining cap/face treatment. South corners also lack a coherent turn between the side and front band profiles. This is a perpendicular-junction representation problem; straight-run seam checks do not validate it.
- Geometry/alpha are preserved for all twelve; committed evidence covers 40 same/cross-variant joins. Repairs add no logical assets.
- Junction V1 is preserved at `demo/hospital_integration/repair_candidates/wall_junctions_v1/`. Its connections worked, but Codex withdrew the production recommendation because the north returns looked like tall framed posts and front caps ended abruptly. The user authorized a focused visual refinement.
- Latest junction **V2**: [findings](../demo/hospital_integration/repair_candidates/wall_junctions_v2/findings.md), [comparison](../demo/hospital_integration/repair_candidates/wall_junctions_v2/junction_refinement_review.png). Continuous upper plaster replaces the three framed north returns; short slate ends close the two front caps before the ivory face. The lower divider PNG, all alpha/geometry/anchors and collision contacts are unchanged from V1. Six views replace seven sprites at six contacts. J enables V2; K compares V1/V2. Codex inspected fresh furnished/unobstructed Godot views and prefers V2; **awaiting human visual review**, no production approval.

## Demo and verification

- Current foreground candidate: `foreground_visibility_review.tscn`; C compares a **12 px opaque outer front cutaway** with the preceding full-height wall. Godot **FOREGROUND_VISIBILITY_PASS** proves head/torso visibility at five boundary positions, retained collision, door passage, hospital route and C/H toggles. Focused integration **10 passed**, full suite **379 passed in 100.47s**; **5,687 existing non-task files unchanged**. Evidence: `repair_candidates/foreground_visibility_v1/findings.md`. Only eight foreground rendering rows change; production/approvals remain untouched. Internal patient-room wall/header occlusion remains full height and still needs assessment in the final architecture review.

- Current solid-only review: **379 passed in 59.82s**, focused integration **10 passed**; Godot **SOLID_WALL_REVIEW_PASS** verifies removed glass collision, retained props, wall comparison, door and hospital walkthrough. All **3,533 protected files unchanged**. Evidence: `solid_wall_review_v1/findings.md`. Production artwork and approval states unchanged.

- Latest actual-hospital glass refresh: **379 passed in 58.56s**, focused integration 10 passed; **HOSPITAL_GLASS_REVIEW_PASS** plus candidate/default **HOSPITAL_SMOKE_PASS**. Support masks/transforms preserved at 22 placements; opaque frame samples reduced 59.2%; exact candidate pane transmission and figure sorting pass. Existing 3,533-file preservation baseline unchanged. Evidence: `glass_enclosure_refresh_v1/findings.md` and `mapping.json`.

- Latest actual-hospital integration: **379 passed in 59.38s**, focused integration 10 passed; Godot **HOSPITAL_FOUNDATION_REVIEW_PASS** and **HOSPITAL_SMOKE_PASS** with candidate walls. Four added connection contacts, H restore and near-front occlusion checked; existing full walkthrough and door/glass pixel checks pass. Existing 3,533-file preservation baseline unchanged. Evidence: `hospital_foundation_integration_v1/findings.md`. Full-front usability is still unresolved despite technical passes.

- Latest Foundation connected finish: **379 passed in 56.88s**, focused integration 10 passed; Godot `FOUNDATION_CONNECTED_FINISH_PASS` confirms source-band mapping, wall-only pixel changes, walkthrough and occlusion. Connected-room regression passes with unchanged tracked captures. Existing 3,533-file preservation baseline unchanged. See `foundation_connected_finish_v1/findings.md` and `source_hashes.json`.

- Latest connected-room proof: **379 passed in 58.89s**, focused integration 10 passed; Godot `CONNECTED_REFERENCE_ROOMS_PASS` checks L/T/cross cap regions, walkthrough through both rooms/corridor/exit and collision/occlusion. Single-room regression also passes with byte-identical tracked images. Existing 3,533-file preservation baseline unchanged. See `connected_reference_rooms_v1/findings.md`.

- Latest single-reference room: **379 passed in 63.05s**, focused integration 10 passed; Godot `SINGLE_REFERENCE_ROOM_PASS` covers one-height geometry, four corners, doorway traversal, bed/wall contacts and front-wall occlusion. Previously protected 3,533 files unchanged; earlier candidate scenes/evidence untouched. See `single_reference_room_v1/findings.md` for the full-front visibility tradeoff and reference scope.

- Latest lower-return correction (reference V3): **379 passed in 67.19s**, focused integration tests 10 passed; Godot `WALL_REFINED_REVIEW_PASS` includes continuous lower-branch pixel paths and adjacent plaster checks. All four native comparisons change only 756 pixels within the three return joins. **3,533 protected files unchanged**. Evidence: `wall_logic_reference_v3/findings.md`.

- Latest refined furnished construction test: **379 passed in 61.70s**, focused integration tests 10 passed; Godot `WALL_REFINED_REVIEW_PASS` confirms doorway traversal, wall/bed contacts, continuous cap pixels and behind/inside/front figure sorting. **3,525 protected files unchanged**. See `wall_logic_reference_v2/findings.md`; this separate F6 review scene does not replace the hospital's production architecture.

- Latest reference-led construction test: **379 passed in 60.33s**; Godot `WALL_LOGIC_REVIEW_PASS`; 3,521 protected files unchanged. The live historical audit was updated to accept newly supplied local files only under `references/itch.io/`, preserving all baseline hashes. The first full run's 10 audit failures were solely these downloaded additions; the final run passes. See `wall_logic_reference_v1/findings.md` for visual limits and commands.

- Stable practical test bed: [hospital integration demo](../demo/hospital_integration/README.md), Godot 4.7.1.stable.official.a13da4feb. Preserve the compact reception/exam/patient-room/corridor layout and 26x46 debug figure. Startup uses approved walls; V toggles family candidates. The open door uses its labelled repair override; glass remains pending.
- Latest recorded completed full suite at `504c52c45e6409710a10afb8badbef427bcfdd18`: **374 passed in 77.60s**; engine comparison **WALL_FAMILY_REVIEW_PASS**; Godot smoke **HOSPITAL_SMOKE_PASS**. Source: family findings linked above. These are prior recorded results, not new bootstrap runs; smoke used default approved walls and comparison separately tested substitutions.
- Bootstrap targeted verification: `python -m pytest -q tests/test_hospital_integration_demo.py` — **7 passed in 0.25s**. Manifest/catalog counts read directly. Full suite and Godot were not rerun for this documentation-only step.
- Prior V1 verification: **377 passed in 79.27s**; Godot review/smoke passed; 1,040 protected files unchanged. The initial V1 full run found the bootstrap state document missing from the historical audit's allowed additions; an exact named allowance fixed this without exempting any baseline hash.
- Latest completed **V2 verification: 378 passed in 55.81s**, full suite run once; focused demo tests **10 passed**; **WALL_JUNCTION_REVIEW_PASS**; **HOSPITAL_SMOKE_PASS** with V2 and K comparison checked. **0 scene pixel changes outside five native RGB refinement bounds and HUD**. All **1,073 protected files unchanged**, including V1 and the five user-owned files. Results: `wall_junctions_v2/test_results.txt` and `verification.json` under the demo's repair candidates.

## Next priorities

1. Current review: `demo/hospital_integration/foreground_visibility_review.tscn` (F6), with evidence in `repair_candidates/foreground_visibility_v1/`. The outer foreground visibility fix is implemented and awaits human visual review. Next assess the complete wall family, including internal patient-room wall/header occlusion, endpoints and junctions. All 22 glass renderers/contacts remain excluded; furniture retained; glass parked. No new windows. Production promotion remains on hold.
2. After visual acceptance and production authorization, consolidate the door alpha repair, solid-wall revisions and formal junction-view integration using existing conventions. Preserve old versions/provenance and record approval accurately; do not silently promote reference-only files. Glass approval is a separate parked task.
3. Point the stable demo at authorized production assets; use existing contracts/scripts, targeted preflight, one full suite, one Godot smoke and one final integration capture. Inventory remains **224 / 220 approved / 4 pending** until separately authorized glass approval.
4. Then address targeted bench proportions and brochure-rack/plant noisy pixels. Floor repetition and generalized terminal/corner/junction art are lower priority; do not reopen the architecture system routinely.
5. Once cleanup is resolved and production authorized, execute the next five families in [ASSET_COVERAGE_STATUS.md](ASSET_COVERAGE_STATUS.md); maintain its concrete backlog against the manifest at every completed batch. Preserve the category budgets in [ASSET_ROADMAP.md](ASSET_ROADMAP.md).

Use cost-conscious iteration: existing scripts/contracts, targeted checks, full suite once per completed batch, Godot as primary practical test. No bespoke validator framework for ordinary assets or bulk generation without instruction. Work toward the revision-2 target of 373 meaningful assets only after cleanup and authorization; see the canonical roadmap and current backlog.

## Local architecture references (2026-09-11)

User supplied three extracted packs under `references/itch.io/`. Inspected their actual PNGs, not just store previews. These are local study material; do not include third-party sprites in RastalR exports or commit the downloaded packs.

- Primary construction reference: `references/itch.io/Modern tiles_Free/Interiors_free/32x32/Room_Builder_free_32x32.png` ([LimeZu](https://limezu.itch.io/moderninteriors)). The top of the sheet supplies connected ceiling/wall-top shapes separately from repeated wall-face finishes below. Study the shared boundary, corner turns and face termination logic. The 32px export is not a reason to copy its proportions into our independent 32px footprint contract.
- Secondary assembled-room reference: `references/itch.io/Top-Down_Retro_Interior/TopDownHouse_FloorsAndWalls.png` ([Penzilla](https://penzilla.itch.io/top-down-retro-interior)). Compact connected rooms make the distinction between tall horizontal faces and thin vertical partitions visible. Compare its sibling `TopDownHouse_FloorsAndWalls_OpenDoors.png` when studying openings.
- Supporting modular reference: `references/itch.io/SmallBurg_village_pack_v3.18_free/assets/housing/house_interiors_assets.png` ([almostApixel](https://almostapixel.itch.io/small-burg-village-pack/devlog/337115/weekly-update-3-new-housing-system)). Local sheet contains separate wall/trim and furnishing pieces; the previously inspected author devlog provides the clearer empty multiroom construction example.

Implementation direction inferred from these references: determine connectivity first, produce one continuous wall-top region through L/T/cross contacts, then draw visible faces with consistent endpoint and occlusion rules. Do not outline shared internal edges as separate posts. Doorways interrupt both the relevant boundary and face, with explicit exposed ends. Adapt this to our existing centered 8px strip, anchors, full back faces, shallow sides and low front cutaways; the reference layouts do not themselves validate our mixed-height transitions.

Practical proof implemented after the user's "Do it": original RastalR empty layouts with L/T/cross intersections, doorways, and a full-wall-to-low-front comparison in the existing Godot demo. The procedural scene uses native pixels, declared heights and the existing grid contract, with no third-party textures or production overrides. Findings and native/Godot images are under `wall_logic_reference_v1`. Judge the exposed height-step ends before adding furniture or applying Foundation finishes. Existing demo tests and engine assertions are used; no new validation framework.

Local license notes: LimeZu's downloaded free license restricts commercial sprite use; SmallBurg prohibits asset redistribution/resale. This workflow studies construction and authors original RastalR geometry/art. The downloaded files remain untouched and untracked.

## Commit history

- `9740fae2fa9ad8042d4d85433fa5d36944080bfd` — junction V1, preserved as the visual refinement baseline.
- Verified bootstrap starting HEAD on `main`: `504c52c45e6409710a10afb8badbef427bcfdd18` — wall-family propagation and review.
- `1239ed8126ae7446d59a412ce2f2c85fea269ccd` — V2 wall prototype.
- `d1d500efb0c2f1342fa81803c8dadc023b5b40f6` — door alpha candidate.
- `ca7833878ab312f163054011aab2845d24728d39` — stable compact demo layout.
- `9a95eba055324f87a7f62ffcda859e1949b207eb` — Batch 13 staging.
- Canonical remote: `https://github.com/RastalRahl/Hospital.git`, branch `main`.

## Unrelated local work: preserve exactly

Present at bootstrap; exclude from task commits, never reset/clean merely to obtain a clean worktree:

- Modified `demo/hospital_integration/project.godot`.
- Untracked `demo/hospital_integration/export_presets.cfg`.
- Untracked `demo/hospital_integration/captures/layout_door_open.png.import`.
- Untracked `demo/hospital_integration/captures/layout_glass_behind.png.import`.
- Untracked `demo/hospital_integration/captures/layout_glass_front.png.import`.

Historical geometry reports contain asserted values that are not independent measurements; consult `docs/ARCHITECTURE.md` before interpreting them. Glass supports reviewed straight runs/rectangular enclosures, not arbitrary L/T/cross junctions. Technical QA never supplies human approval.
