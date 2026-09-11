# One complete wall convention — SmallBurg study

The user authorized a small room based on one reference's complete wall convention after Codex acknowledged that the mixed-height fixes were not demonstrated by those references.

## Reference and interpretation

Inspected the supplied `references/itch.io/SmallBurg_village_pack_v3.18_free/examples/cosy_house.png`: narrow connected top borders, full horizontal wall faces, narrow vertical boundaries and a full front face. This complete assembled scene is the sole architectural reference for this study. Its visible construction is the evidence; its implementation, collision and camera math are not supplied by the PNG and are not claimed to be reproduced.

Original RastalR geometry uses 32px cells, an 8px centered wall strip and one 44px height for every wall. Wall-center spans are 8 by 5 cells. The room has four corners and one 32px front doorway. RastalR palette and approved bed/cabinet are retained; no SmallBurg pixels are copied. The reference's fully drawn front is an explicit study alternative to the project's production low-front policy, not a silent change to that policy.

## Implementation and review

`reference_room.gd` reuses the existing deterministic column renderer, furniture loading, figure and movement. Its single-height footprint never activates the mixed-height reveal code. `reference_room.tscn` is an independent F6 scene inside the current Godot demo; it does not change hospital startup.

Codex inspected empty/furnished `room_godot.png` and `behind_front_native.png`. The full perimeter is coherent without special junction strips. Behind the full front wall the figure is mostly hidden, with the head remaining visible in the tested rear pose. This is expected depth ordering and a real gameplay visibility tradeoff, not a rendering defect to patch away with another local height rule. `doorway_godot.png` tests the clear opening separately.

This establishes a consistent single-room baseline. It does not demonstrate internal T/cross arrangements, production shallow-side compatibility, finished Foundation surfaces, or a low-front variant. Those should be evaluated from this baseline rather than assumed solved. Production assets/approvals remain unchanged: **224 manifest / 220 approved / 4 pending**.

## Reproduce

Open `../../reference_room.tscn`, press F6. WASD moves, F toggles furniture/figure, G shows grid lines, R resets. Figure canvas is 26x46; foot contact is 18x8. Bed and cabinet have explicit demo-only contacts.

```powershell
& C:/Godot/Godot_v4.7.1-stable_win64_console.exe --path demo/hospital_integration --log-file .qa/single_room_run.log res://reference_room.tscn --quit-after 180 -- --single-room-review
```

Expect `SINGLE_REFERENCE_ROOM_PASS`: every occupied pixel has the same height, all four corner-center cap pixels are continuous, wall/furniture contacts block, every pixel step through the doorway is clear, and rear/doorway figure visibility is checked. Saves empty, furnished, rear and doorway native views plus three Godot captures.

## Verification

Godot 4.7.1 Compatibility: **SINGLE_REFERENCE_ROOM_PASS**; fresh furnished, rear and doorway images inspected. Focused integration tests: **10 passed in 0.33s**. Full suite once: **379 passed in 63.05s**. Existing preservation baseline: **3,533 files unchanged**, including production, metadata, downloaded references and five user-owned demo files. Git inspection confirms earlier scene scripts and candidate evidence are untouched. `git diff --check` passed.
