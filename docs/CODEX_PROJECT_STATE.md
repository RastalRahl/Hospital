# Codex project state

Verified 2026-09-11. Operational handoff for future Codex sessions; read with `AGENTS.md`. Codex owns planning, implementation, review preparation, QA, Godot integration and Git delivery. Human visual/production decisions stay with the user, directly in Codex.

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

1. Review the Foundation material adaptation: `demo/hospital_integration/repair_candidates/foundation_connected_finish_v1/corridor_godot.png`, via `foundation_reference_rooms.tscn` (F6). Existing human-approved V2 material pixels supply the blue-slate cap, warm ivory plaster and teal base on the fixed connected-room geometry. Left/right panels have identical furniture/figure poses. Geometry, full wall heights, openings and collisions remain unchanged; only projected wall pixels differ. Codex inspected cap/junction/base/doorway continuity. Human visual review and full hospital integration remain outstanding, including the explicit full-front versus production low-front camera decision. No production promotion.
2. After visual acceptance and production authorization, consolidate glass approval, the door alpha repair, wall RGB revisions and formal junction-view integration using existing conventions. Preserve old versions/provenance, declare any required placement-specific views explicitly, and record approval accurately; do not silently promote the reference-only junction files.
3. Point the stable demo at promoted production assets; use existing contracts/scripts, targeted preflight, one full suite, one Godot smoke and one final integration capture. Expected inventory: **224 / 224 approved / 0 pending**.
4. Then address targeted bench proportions and brochure-rack/plant noisy pixels. Floor repetition and generalized terminal/corner/junction art are lower priority; do not reopen the architecture system routinely.

Use cost-conscious iteration: existing scripts/contracts, targeted checks, full suite once per completed batch, Godot as primary practical test. No bespoke validator framework for ordinary assets or bulk generation without instruction. Work toward approximately 400 meaningful assets only after cleanup and authorization.

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
