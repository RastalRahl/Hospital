# Findings — bounded hospital integration

Reviewed Godot viewport captures at actual 2x gameplay zoom, 2026-09-11. This is an integration review, not human production approval. Inventory remains **224 / 220 approved / 4 needs_human_review**. Batch 13 remains pending. No D5 work.

## Blocking

- **Production gate:** the four glass parents remain intentionally unapproved. This demo explicitly includes their pending native files; it does not authorize production use.
- **Environment:** direct startup initially crashed when Godot could not create its sandboxed user-data log directory. The provided launcher supplies a writable local log path and rendered startup succeeds. Shader-cache and certificate-store warnings remain environmental limitations, not art failures.

## Noticeable

- **Asset: opaque open doorway.** The additive parked leaves render correctly and the central collision clears immediately. The unchanged recessed opening is opaque: the figure's body disappears while behind it and becomes visible after crossing the ground anchor. This is not a transparent passage or animation. No alpha patch was applied.
- **Asset: module/style differences.** Repeated Foundation cells show strong dark vertical divisions and segmented caps; floors tile without empty seams but have visible tonal repetition/fine texture. Some props (bench, brochure rack, plant) have finer/noisier clusters than the smooth glass frames. Small detached pixels are visible by the plant/rack. Native bytes were retained, not cleaned.
- **Asset/layout support:** only available authored orientations are used. No arbitrary glass L/T/cross junctions, solid-wall internal corner adapters or rotated doors are claimed. Solid divider joins remain visibly butt-joined. The glass entrance is a gap between two straight terminal runs, not a new door asset. The seven-cell bay extends the documented straight-run method; it is not a claim of a newly approved enclosure size.
- **Demo approximation:** furniture contacts are hand-selected small base rectangles (explicitly separate from manifest footprints); they do not model every wheel/leg. Shallow side partitions sort per cell, not per pixel. No universal occlusion solution is claimed for untested positions or new layouts.

## Acceptable

- Twenty existing prop types furnish reception/waiting, an examination bay, patient room and a southern connecting corridor. Scale is broadly usable against the 26x46 figure; benches appear more compact than individual patient chairs. Nothing was resized to equalize them.
- The 64px examination entrance and open sliding passage are traversable. Flood-fill clearance checks reach counter, waiting chairs, examination table/stool and bedside/visitor approaches. Beds and counters cannot be walked through at floor contact.
- Glass keeps its supplied alpha and replaces alternate views once per placement. Godot front/behind captures show transmission through the pane, opaque frames, and the figure on top when in front. Corrected corner placement uses the helper's distinct side centerline and D1 baseline; north returns and south shoulders remain visible. No doubled panes, masking or opacity multiplication.
- Sorting uses floor anchors, a Y-sorted object layer and the authored glass corner tie order. The floor is separate. Closed/open door components switch as a group; permanent jamb contacts remain. Reset, overlay and integer zoom controls passed engine assertions.

## Executed checks

- Installed executable version query; baseline HEAD verification; manifest inventory query.
- Godot headless editor import completed; no GDScript parse or missing-texture errors. Sandbox editor-settings/user-data warnings were observed.
- Godot Compatibility renderer startup and scripted movement/collision smoke passed on the GPU. Captured overview, grid/contact overlay, glass behind/front, and open-door occlusion directly from the Godot viewport. Inspected those 2x captures; this was scripted runtime review, not a prolonged manual play session.
- Three focused Python tests check copied bytes/status/footprints, exclusive/additive selection, and walking reachability. Complete repository suite run once: **370 passed in 68.28s**. Focused tests rerun after the corner-placement correction; all three pass, including 48px north / 32px south opaque contacts without stacked glass.
- Early implementation issues corrected: overly strict float equality in a smoke assertion; debug drawing hidden below floor sprites; glass side cells initially aligned to D1 cells instead of the helper's separate centerline coordinates. Source artwork was never changed.

- Extracted the cache-free ZIP into an isolated directory and ran its launcher with `-Smoke`: fresh import, GPU startup and `HOSPITAL_SMOKE_PASS` succeeded without repository asset paths.
