# Refined cutaway and furnished-room test

Reference only; original architecture rendering, no production replacement or approval change. User authorized the refinements after review of V1. The existing V1 scene and evidence remain unchanged.

## Result

- The front rooms now share a 12px display cut plane across their side/divider returns and front boundary. Full 44px walls remain across the back and internal horizontal run. This removes the three isolated tall front terminal faces. The low side caps enter the bottom of the full internal wall face; they do not pretend to share its elevated cap plane.
- Darker slate caps and a warm neutral floor separate the wall footprint from walkable space. Door openings have two-pixel shaded jamb edges, with different light/dark treatments by facing. Doorway width and ground connectivity are unchanged.
- One upper room uses the existing approved hospital bed and bedside cabinet at native size and bottom-center anchors. An original 26x46 debug figure moves through the right doorway. Images composite back-to-front by ground row, so walls naturally cover a figure behind them and the figure covers walls behind its feet.
- Codex inspected the full Godot comparison, doorway native view and rear occlusion view. The cutaway ends are clearer than V1 and the furnished room makes the intended camera/scale legible. This is a plain geometry candidate, not finished Foundation artwork. Thin jamb shading is restrained; no lintel or door leaf is included. Applying this policy to the full hospital and its existing shallow side sprites is still a separate integration step.

## Review and controls

Open `../../wall_logic_refined.tscn` and press F6. WASD moves at 64 native pixels/second, including normalized diagonals; F toggles furniture/figure; G toggles ground grid; R resets. The 18x8 foot contact blocks against occupied wall footprints and two explicitly declared demo-only furniture contacts. Production physics/metadata are not changed.

```powershell
& C:/Godot/Godot_v4.7.1-stable_win64_console.exe --path demo/hospital_integration --log-file .qa/wall_refined_run.log res://wall_logic_refined.tscn --quit-after 180 -- --wall-refined-review
```

Expect `WALL_REFINED_REVIEW_PASS`. This verifies rendered T/cross/front cap pixels, lowered return heights, solid-wall/bed collision, every one-pixel step through the doorway, and visible/hidden figure pixels. It saves empty, rear, doorway and foreground native images plus three Godot viewport captures. `front_godot.png` is the principal review image. The scene inherits the V1 footprint function rather than defining a second topology system; no third-party pixels are loaded.

## Executed verification

- Godot 4.7.1 Compatibility: `WALL_REFINED_REVIEW_PASS`; fresh native and viewport renders inspected. This offline run retains the host's root-certificate warning.
- Focused integration tests: **10 passed in 0.33s**.
- Full suite, once after completing the batch: **379 passed in 61.70s**.
- SHA-256 preservation check: **3,525 files unchanged**, covering production, staging, source, metadata, downloaded packs, reference V1 evidence and all five pre-existing user-owned demo files. `git diff --check` passed.
- Production inventory remains **224 / 220 approved / 4 pending**. The new review outputs are not logical inventory assets and have not entered the approval path.
