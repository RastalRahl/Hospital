# Connected wall construction study — reference only

User requested implementation of the reference-led empty junction test. This is an original deterministic geometry study, not production artwork or an approval change. No third-party image is loaded by the scene or included in these outputs.

## Construction and visual review

`../../wall_logic_test.gd` unions axis-aligned wall strips on the existing 32px grid, using the centered 8px connection region. Each occupied ground pixel has a declared height and is projected to `(x, y-height)`. Columns draw back-to-front; shared intersections are emitted once. This avoids placement-specific connector patches and duplicate internal outlines.

The two layouts have identical footprints: outside L corners, a central north T, an internal cross, two 32px internal doorways, and a front entrance. A uses a consistent 44px height. B changes only the front strip to 12px. Wall-top width comes from the 8px footprint; back faces are tall and side boundaries appear shallow in the axis-aligned projection.

Codex inspected `godot_review.png`: A's caps visibly connect through the north branch and central cross, and the wall faces terminate consistently at openings. B exposes three tall end faces where the full-height side/divider strips meet the low front. These are real height steps in this construction, not missing pixels. This clarifies the remaining visual choice instead of hiding it with connector art. Recommend A's shared construction logic; B's terminal appearance still needs human review under the required cutaway camera policy.

This is deliberately plain geometry. It does not yet reproduce the human-approved Foundation surface treatment, replace hospital sprites, define collision gameplay, or prove all possible networks. The scene is a separate F6 review scene inside the existing Godot integration project. Production remains 224 manifest / 220 approved / 4 pending.

## Reproduce

From repository root:

```powershell
& C:/Godot/Godot_v4.7.1-stable_win64_console.exe --path demo/hospital_integration --log-file .qa/wall_logic_run.log res://wall_logic_test.tscn --quit-after 120 -- --wall-logic-review
```

Expect `WALL_LOGIC_REVIEW_PASS`. This executes ground-contact/opening and rendered-cap assertions and saves both native layouts plus the Godot viewport. Omit the review argument and timeout for interactive viewing; G toggles the ground grid. Existing main scene and user-owned project settings remain unchanged.

Reference principles: LimeZu's separate wall-top and face construction; SmallBurg's empty connected-room example; Penzilla's thin interior boundaries. Local source paths and license notes are in `docs/CODEX_PROJECT_STATE.md`. No source pixels were copied.

## Verification

- Godot 4.7.1 Compatibility render: `WALL_LOGIC_REVIEW_PASS`, including rendered junction pixels and doorway checks; viewport visually inspected.
- Focused integration tests: 10 passed. Reference-audit tests after the bounded adjustment: 64 passed.
- First full suite: 368 passed / 10 failed, all because 2,528 user-downloaded reference files were classified as unauthorized additions; no historical hashes changed. The existing live audit now permits additions only under `references/itch.io/`, without exempting any baseline hash. A regression test checks both this boundary and historical-file protection.
- Final full suite: **379 passed in 60.33s**. The repeat was required by the audit fix.
- SHA-256 comparison: **3,521 protected files unchanged**, including production, metadata, downloaded packs and the five pre-existing user-owned demo files. `git diff --check` passed. Only this task's scene, evidence, documentation and audit changes are delivered.
