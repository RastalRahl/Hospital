# Foundation architecture in the actual hospital

User authorized a practical integration review of the coherent full-height geometry and Foundation finish in the existing furnished hospital. This is a separate F6 scene, `../../hospital_foundation_review.tscn`; production startup, artwork and approvals are unchanged.

## Integration

`hospital_foundation_review.gd` extends the existing hospital scene logic. The 73 original wall placements are hidden only while H review mode is enabled. Their declared collision rectangles supply the wall footprint, rather than inferring footprint from PNG dimensions. The original furniture, glass, doors, floor, camera, movement and state controls remain active at their existing positions.

Four explicit 8px-wide connection contacts close gaps: northwest `(24,88,8,8)`, northeast `(704,88,8,8)`, north divider `(504,88,8,8)`, and lower divider return `(504,320,8,16)`. They are active only with the candidate. Existing wall contacts are unchanged. The candidate uses one 44px height and the previously reviewed Foundation material functions, with no mixed-height reveal.

`hospital_wall_material.gd` produces 328 transparent ground-row textures at native pixel density. Each sorts at its ground baseline alongside the existing sprites, retaining door/glass/figure occlusion rather than drawing architecture as a foreground overlay. The full back wall aligns with the existing 52px rendered height (8px cap plus 44px face). The front now uses the same full-height convention as the reference study, explicitly for review.

H compares original/candidate. V/J/K historical wall controls are available after H restores the original walls, avoiding stacked wall modes. G includes the four extra contacts in magenta. Closing the review does not modify the saved project or production defaults.

## Visual result and remaining decision

Codex inspected the actual furnished overview, open-door view and near-front view. The north perimeter, internal north branch, lower patient-room return and door opening now have coherent connected boundaries and Foundation material bands. Furniture and glass remain at their established scale and positions; the existing sliding-door repair is retained.

The full front is a real usability concern: at `(112,400)` only the figure's head remains visible, while at `(112,368)` the body is visible. Viewport-pixel assertions confirm that difference. This is not solved by the passing tests. Recommend retaining the connected construction and finish, but resolving foreground visibility before production promotion. The production low-front camera contract has not been changed or accepted as replaced.

`candidate_godot.png` and `original_godot.png` are matching overview comparisons. `front_near_godot.png` and `front_clear_godot.png` expose the visibility tradeoff; `divider_godot.png` and `door_open_godot.png` cover the patient-room connection.

## Reproduce and checks

```powershell
& C:/Godot/Godot_v4.7.1-stable_win64_console.exe --path demo/hospital_integration --log-file .qa/hospital_foundation_run.log res://hospital_foundation_review.tscn --quit-after 600 -- --hospital-foundation-review
```

Require both `HOSPITAL_FOUNDATION_REVIEW_PASS` and `HOSPITAL_SMOKE_PASS`. The first covers row count, four connection contacts, front visibility and H restoration. The second runs the existing actual-hospital walkthrough, door collision/open crossing, examination entrance, furniture contact and exact glass transmission/sorting checks with candidate walls enabled. Disposable smoke images stay in `.qa/`. The host still emits certificate/shader-cache permission warnings; both pass markers were observed.

Inventory remains **224 manifest / 220 approved / 4 pending**. No new inventory assets are counted and no pending repair is promoted.

Final verification: both Godot pass markers above; focused integration tests **10 passed in 0.37s**; full suite once **379 passed in 59.38s**. Existing SHA-256 preservation baseline confirms **3,533 files unchanged**, including production, metadata, local downloads and the five user-owned demo files. Git inspection confirms existing runtime manifest, scene scripts and previous evidence unchanged. `git diff --check` passed.
