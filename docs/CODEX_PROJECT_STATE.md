# Codex project state

Verified 2026-09-11. Operational handoff for future Codex sessions; read with `AGENTS.md`. Codex owns planning, implementation, review preparation, QA, Godot integration and Git delivery. Human visual/production decisions stay with the user, directly in Codex.

## Inventory and approval boundary

- Verified manifest: **224 logical assets / 220 approved / 4 needs_human_review**. Catalog: **224 rows**.
- Batches 01–12 are approved; Architecture Foundation (11) has 20 logical assets and Doors & Openings (12) has 8.
- Batch 13 glass: back, side_left, side_right and front_cutaway (`hospital_glass_partition_<orientation>_01`) remain formally pending. Its 12 exclusive views represent four logical assets. User runtime visual acceptance is recorded in the supplied handoff and current request; production approval metadata has not been changed.
- Bootstrap is documentation-only. No production artwork, staging or approval changes are authorized until the user confirms the next production action. No D5 or new generation before cleanup is resolved.

## Active repairs and practical review

- Open sliding door: `demo/hospital_integration/repair_candidates/sliding_door_open_alpha_v1/repair.json`. Candidate visually accepted by the user per handoff/current request, not promoted. Passage `[7,14,59,48)` has 1,768 alpha changes; RGB and parked leaves unchanged. Revise the existing logical asset and preserve the previous approved version/provenance.
- Foundation walls: [family findings](../demo/hospital_integration/repair_candidates/foundation_wall_refresh_family_v1/findings.md) and [review montage](../demo/hospital_integration/repair_candidates/foundation_wall_refresh_family_v1/wall_family_review_montage.png). Twelve reference-only repairs: four back, two left, two right, four front. Status: **READY FOR WALL-FAMILY REPAIR STAGING**. V2 visual language is human-approved; final propagated-family production approval is outstanding.
- Bootstrap visual inspection: continuous cap/base and quiet ivory surfaces remove the dominant repeated panel borders in the committed Godot and mixed-run montage. Subsequent user review accepts the surface improvement but flags incorrect perpendicular wall intersections. **Production promotion is on hold pending junction repair/review**; the earlier recommendation to promote with limitations is withdrawn.
- Follow-up inspection of full-resolution `godot_refreshed.png` and both refreshed north-corner crops confirms disconnected cap/face transitions. In `build_demo.py`, the north wall occupies y=44..95 while the outer side walls begin at y=96, outside its x span: their painted regions only meet at a diagonal corner. The internal side divider similarly begins at the north wall's base, and its lower end abuts the left edge of the full-height patient-room wall without a joining cap/face treatment. South corners also lack a coherent turn between the side and front band profiles. This is a perpendicular-junction representation problem; straight-run seam checks do not validate it.
- Geometry/alpha are preserved for all twelve; committed evidence covers 40 same/cross-variant joins. Repairs add no logical assets.

## Demo and verification

- Stable practical test bed: [hospital integration demo](../demo/hospital_integration/README.md), Godot 4.7.1.stable.official.a13da4feb. Preserve the compact reception/exam/patient-room/corridor layout and 26x46 debug figure. Startup uses approved walls; V toggles family candidates. The open door uses its labelled repair override; glass remains pending.
- Latest recorded completed full suite at `504c52c45e6409710a10afb8badbef427bcfdd18`: **374 passed in 77.60s**; engine comparison **WALL_FAMILY_REVIEW_PASS**; Godot smoke **HOSPITAL_SMOKE_PASS**. Source: family findings linked above. These are prior recorded results, not new bootstrap runs; smoke used default approved walls and comparison separately tested substitutions.
- Bootstrap targeted verification: `python -m pytest -q tests/test_hospital_integration_demo.py` — **7 passed in 0.25s**. Manifest/catalog counts read directly. Full suite and Godot were not rerun for this documentation-only step.

## Next priorities

1. Prepare a bounded reference-only junction repair for the existing demo: back-to-side outer corners, internal side-to-full-wall join, and side-to-front corners. Use deterministic geometry and existing grid anchors, then inspect in Godot before requesting production approval. The user has requested inspection; junction implementation is the proposed next action, not yet executed.
2. On confirmation, finalize four Batch 13 glass parents and all required views; promote the accepted door alpha repair and twelve wall RGB repairs as revisions, preserving prior approved artwork/provenance and recording approval accurately.
3. Point the stable demo at promoted production assets; use existing contracts/scripts, targeted preflight, one full suite, one Godot smoke and one final integration capture. Expected inventory: **224 / 224 approved / 0 pending**.
4. Then address targeted bench proportions and brochure-rack/plant noisy pixels. Floor repetition and generalized terminal/corner/junction art are lower priority; do not reopen the architecture system routinely.

Use cost-conscious iteration: existing scripts/contracts, targeted checks, full suite once per completed batch, Godot as primary practical test. No bespoke validator framework for ordinary assets or bulk generation without instruction. Work toward approximately 400 meaningful assets only after cleanup and authorization.

## Relevant history

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
