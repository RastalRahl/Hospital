# Solid architecture review — glass removed

User confirmed removing the central glass enclosure from the wall-review scene after clarifying that it was not needed. `solid_wall_review.tscn` is the current review entry point. It extends the actual-hospital Foundation candidate, hides all 22 glass placements, and rebuilds active collision/debug anchors from non-glass placements only. Examination furniture stays at its existing positions; no substitute windows or partitions are added.

Glass source files, pending records and prior candidates are preserved separately. Their redesign/promotion is parked. Normal project startup and production artwork are unchanged. Inventory remains 224 / 220 approved / 4 pending; the four glass parents are not promoted as part of solid-wall cleanup.

Codex inspected `overview_godot.png`: the central examination area is open and the solid perimeter/patient-room walls can be judged without the enclosure. Foreground full-wall visibility remains the next architectural issue. This is an asset/architecture review layout, not a final clinical floor plan.

Open `../../solid_wall_review.tscn` and press F6; existing movement, E door and H wall comparison remain. For repeatable capture/checks:

```powershell
& C:/Godot/Godot_v4.7.1-stable_win64_console.exe --path demo/hospital_integration --log-file .qa/solid_wall_run.log res://solid_wall_review.tscn --quit-after 240 -- --solid-wall-review
```

Require `SOLID_WALL_REVIEW_PASS`: glass hidden even after H comparisons, all furniture visible, former glass contacts clear, movement across former north/side boundaries, door collision/open crossing, retained table collision and the existing full hospital route. The initial eastward test endpoint touched the unchanged solid divider; shortening that route to stop before the divider confirmed the removed glass is traversable without weakening solid collision.

Verification: focused integration **10 passed**; completed full suite **379 passed in 59.82s**; Godot **SOLID_WALL_REVIEW_PASS**. All **3,533 protected files unchanged**, including production/staging metadata and unrelated user files.
