# South-going side returns — reference-led correction

The user correctly identified that V2's low side walls approached from below and started midway down the full horizontal wall face. That created three protruding tabs rather than readable connected architecture. V2's geometric height calculation did not provide the intended RPG cutaway representation.

Re-inspected the local LimeZu `Room_Builder_free_32x32.png`: its narrow vertical room boundaries connect into the continuous horizontal wall-top border. Applied that visual construction principle to our three mixed-height returns. The final full-height ground row now draws an 8px-wide cutaway edge through the face, from the upper cap to the low return. Shared horizontal outlines are removed inside this edge, and its sides retain the directional light/dark rails. Subsequent low rows use the existing renderer and ground-row occlusion order.

This is an explicit camera-aware cutaway convention, not a physical claim that the 44px and 12px caps occupy the same elevation. Footprints, logical wall heights, collision, doors and actor positions are unchanged. No third-party pixels are copied; the existing procedural scene and V1 connectivity are reused.

## Visual review and scope

Codex inspected `front_godot.png`: both outer lower returns and the central lower branch now connect to the upper wall-top border. The central cross has a continuous narrow vertical edge; there are no isolated low cap tips on plaster. The surrounding full wall faces retain their original shapes and surface colors.

Compared all four native views against preserved reference V2: **756 changed pixels per view**, all inside the three 8px-wide return strips at x `[44,52)`, `[204,212)`, `[332,340)` and y `[135,180)`. No pixels change elsewhere. V1 and V2 evidence remain untouched. The left full-height comparison is unchanged; only the right-hand mixed-height joins are revised (plus explanatory HUD text).

## Reproduce

Open `../../wall_logic_refined.tscn` with F6. Existing WASD/F/G/R controls remain.

```powershell
& C:/Godot/Godot_v4.7.1-stable_win64_console.exe --path demo/hospital_integration --log-file .qa/wall_refined_v3_run.log res://wall_logic_refined.tscn --quit-after 180 -- --wall-refined-review
```

Expect `WALL_REFINED_REVIEW_PASS`. Added assertions check every center pixel along all three connected cap paths and intact neighboring plaster. Existing doorway traversal, bed/wall contacts and figure occlusion checks still execute. First targeted engine iteration exposed a remaining horizontal outline at the connection; removing that shared outline made the continuity checks pass.

Production remains **224 manifest / 220 approved / 4 pending**. This fixes the review scene; production architecture is not replaced or approved.

Verification: Godot **WALL_REFINED_REVIEW_PASS**; focused integration tests **10 passed in 0.35s**; full suite once after the correction **379 passed in 67.19s**. SHA-256 comparison confirms **3,533 protected files unchanged**, including production, local reference downloads, V1/V2 evidence and all five pre-existing user-owned demo files. `git diff --check` passed.
