# Hospital integration demo

Latest glass review: `hospital_glass_review.tscn` (F6) uses the actual hospital, Foundation walls and a lighter glass enclosure. O compares glass; H compares walls. See `repair_candidates/glass_enclosure_refresh_v1/candidate_godot.png`, `mapping.json` and `findings.md`. Glazing alpha/frame regions are revised only in this reference candidate; support masks, placements, openings and collision remain fixed. Production contracts/approval are unchanged.

Latest actual-hospital architecture review: open `hospital_foundation_review.tscn` and press F6. H compares original walls with the coherent full-height Foundation candidate; the existing furnished hospital, doors/glass and movement remain active. See `repair_candidates/hospital_foundation_integration_v1/candidate_godot.png` and `findings.md`. The near-front view exposes significant figure occlusion, so production promotion remains on hold. Normal F5 startup is unchanged.

Latest material review: `foundation_reference_rooms.tscn` (F6) compares plain and Foundation-finished connected rooms at identical geometry/poses. Existing V2 cap/plaster/base pixels supply the finish. See `repair_candidates/foundation_connected_finish_v1/corridor_godot.png` and `findings.md`. Production approval and the full-front versus low-front camera decision remain pending.

Latest connected-room review: `connected_reference_rooms.tscn` (F6). Two furnished rooms and a deeper connecting corridor exercise L/T/cross caps, two room doorways and a front exit under the same full-height convention. See `repair_candidates/connected_reference_rooms_v1/corridor_crossing_godot.png` and `findings.md`. WASD/F/G/R controls remain; this is a separate reference scene, not production integration.

Latest single-reference baseline: open `reference_room.tscn` and press F6. This small room follows the complete visible wall convention of SmallBurg's supplied `cosy_house.png`, including a full front face. All walls use one 44px height; mixed-height reveals are inactive. See `repair_candidates/single_reference_room_v1/room_godot.png` and `findings.md`. This tests a coherent alternative and its front-wall occlusion tradeoff; the production low-front policy is unchanged.

Latest practical wall review: `wall_logic_refined.tscn` (F6), with lower side returns connected through the cut face to the upper wall border, shaded doorway jambs, existing bed/cabinet and the 26x46 figure. WASD moves; F toggles furniture; G shows the grid; R resets. See `repair_candidates/wall_logic_reference_v3/findings.md` and `front_godot.png`. V3 corrects V2's mid-face cap tips; earlier evidence is preserved. This is reference-only and leaves the hospital startup unchanged.

Reference-led empty wall test: open `wall_logic_test.tscn` and press F6. It compares continuous 44px walls with the same network using a 12px front cutaway; G toggles the ground grid. See `repair_candidates/wall_logic_reference_v1/findings.md` for capture instructions and limits. This separate review scene leaves the hospital startup unchanged and has no production approval.

Godot **4.7.1.stable.official.a13da4feb**, Compatibility/OpenGL 3.3; tested on NVIDIA RTX 3050 Laptop. Independent project; no Gloam dependency. Runtime requires only this directory and Godot 4.7.1. No engine installation or asset generation occurs.

From the repository root in PowerShell:

```powershell
& ./demo/hospital_integration/launch.ps1 -Godot 'C:\Godot\Godot_v4.7.1-stable_win64_console.exe'
```

Or import `project.godot` into Godot and press F6 on `main.tscn` / F5. For an extracted ZIP, run `./launch.ps1 -Godot '<path to Godot executable>'` from its project directory. The launcher puts logs in `.qa` to avoid the restricted user-data log directory encountered on this host. The engine can still warn about unavailable shader caching/certificates in the sandbox; this offline demo does not require either.

Controls: WASD/arrows move; E switches the patient-room door instantly (global debug control); G toggles grid, cyan anchors and orange floor contacts; R resets position; 1/2/3 select integer zoom. Zoom 2 shows the complete floor; zoom 3 follows the figure. Closing is refused while the figure occupies the doorway. The outlined 26x46 figure is a debug reference, not an inventory asset.

`overview_before.png` preserves the original overview byte-for-byte. `overview.png` is the improved 2x Godot overview; `captures/layout_glass_behind.png`, `captures/layout_glass_front.png` and `captures/layout_door_open.png` show the three requested figure poses. The floor is now 21x10 tiles (previously 24x11), with the same 20 prop types. Reception/check-in and waiting are grouped; all six examination props are inside the bay; bedside equipment surrounds the bed with a clear southern approach. `FINDINGS.md` records limitations and executed checks. `runtime_manifest.json` is the complete source/asset mapping: 39 byte-identical PNGs, logical IDs, source paths, status, SHA-256, native sizes, logical footprints, anchors, placements and demo-only collision rectangles. Its source paths are provenance only; runtime loads local `art/` files, except for the explicitly labelled open-door candidate described below. There are 20 prop types, Foundation floor/back/left/right/front modules, two sliding-door states plus two additive open-state leaves, and all four pending glass parents (ten selected exclusive views).

The optional `build_demo.py` regenerates the small mapping and copies from this repository's current production files; it is not required to play the extracted project. It uses `views.resolve` and never falls back to historical source art. Approved assets and Batch 13 are untouched. Floor and solid-wall placement follows the Batch 11 reconstruction convention. Glass uses the Batch 13 enclosure helper's north/south centerline geometry; first side returns sort before D1, and D4 sorts after the side terminals. Sprites use native dimensions, nearest filtering, and pixel snapping; no per-asset transforms, runtime opacity overrides or shaders.

For the engine smoke run:

```powershell
& ./demo/hospital_integration/launch.ps1 -Godot 'C:\Godot\Godot_v4.7.1-stable_win64_console.exe' -Smoke
```

This runs the layout walkthrough, collision and viewport-pixel assertions and saves disposable captures in `.qa/`. Previous layout and glass review captures are preserved. Look for `HOSPITAL_SMOKE_PASS`; a zero exit alone is insufficient because the timeout can end a failed assertion run. Repository tests: `python -m pytest -q`.


The open state now uses **one unapproved alpha-only repair candidate**, identified in the HUD. The approved original remains in `art/hospital_sliding_clinical_doors_open_01__main.png`; the two parked leaves and all placements are unchanged. `runtime_manifest.json` continues to describe the original source copies. The separate candidate mapping, mask and geometry justification are in `repair_candidates/sliding_door_open_alpha_v1/repair.json`. Its mask `[7,14,59,48)` changes 1,768 alpha values to zero, preserving every RGB value, jamb/header pixel and threshold row.

To capture and test the door comparison:

```powershell
& ./demo/hospital_integration/launch.ps1 -Godot 'C:\Godot\Godot_v4.7.1-stable_win64_console.exe' -DoorReview
```

Look for `DOOR_ALPHA_REVIEW_PASS`. `captures/door_alpha_repair/` contains closed approach, approved before, candidate behind/crossing/front and the compact `door_and_glass_review.png`. The last image combines unscaled crops from Godot captures, including the preserved Batch 13 glass-behind/front views. `build_door_review_image.py` rebuilds that review image after capture (Pillow and Windows Arial); it is not needed to run the demo. `build_door_alpha_candidate.py` reproduces the exact candidate from the repository's approved source and requires no engine or production write.


A separate **reference-only back-wall RGB prototype** is preserved for historical comparison with `-WallReview` (approved original is the startup default). It overrides only `hospital_wall_back_straight_01` at its existing 25 placements. Nothing is propagated to production. For deterministic approved/v1/v2 captures, use `launch.ps1 -Godot '<Godot executable>' -WallReview`; look for `WALL_PROTOTYPE_REVIEW_PASS`. Captures, native candidate, diff/repeat diagnostics and findings are in `repair_candidates/back_wall_refresh_v1/`. The small `wall_prototype_review.zip` there contains only this prototype's evidence. Existing door/glass controls and repairs are unchanged.

V2 evidence and the three-way engine montage are in `repair_candidates/back_wall_refresh_v2/`. V1 evidence remains preserved. Human approval of the v1 direction does not approve either candidate or propagate artwork. V2 removes per-cell luminance shading and retains small interior chromatic pixel clusters.

The **V** key now switches the complete Foundation wall family between approved originals and reference-only refreshed candidates. All twelve IDs are mapped; the unchanged hospital uses 73 placements of back 01, left 01, right 01 and front 01. Other variants are covered by native mixed-run/pair checks and loaded by Godot without adding furniture or wall placements. `launch.ps1 -Godot '<Godot executable>' -FamilyReview` captures the two overviews and seven region pairs at identical 2x zoom; expect `WALL_FAMILY_REVIEW_PASS`. Evidence, mapping, findings and the compact montage are in `repair_candidates/foundation_wall_refresh_family_v1/`. The human-approved V2 visual language is propagated only to these reference candidates; no production approval is implied.

**J** toggles the reference-only junction prototype (now V2) and enables the refreshed wall family. **K** compares preserved V1 and refined V2 while junctions are enabled. Six explicit junction views replace seven side-wall sprites at the existing ground positions: northwest/northeast, the internal north branch, both south corners, and the divider's east-going full-height return. The north views extend 52 native pixels above the first side cell; the divider end spans its final two cells with a declared 16px visual extension. V2 continues back-wall plaster and base across the north returns, removing the tall framed-post appearance; short slate end caps terminate before the ivory front cap. The lower divider image, all alpha maps, footprints, anchors and contacts are unchanged from V1. Three missing 8px-wide collision contacts are active only with J, drawn magenta with G. Existing collision rectangles, furniture/layout and `runtime_manifest.json` remain unchanged. Turning J off restores the original side sprites; V also exits junction mode. Startup remains approved walls with original junctions.

Use `launch.ps1 -Godot '<Godot executable>' -JunctionReview` for fresh V1/V2 captures, contact and figure-sort assertions (`WALL_JUNCTION_REVIEW_PASS`). `-JunctionSmoke` checks K comparison and runs the existing walkthrough/smoke with V2 enabled (`HOSPITAL_SMOKE_PASS`). The six close-up pairs temporarily hide props so the joins can be seen; furnished overviews keep all props. Latest views, explicit footprints/anchors, scripts and montage are in `repair_candidates/wall_junctions_v2/`; the complete V1 workspace is preserved unchanged. This prototype covers only the six current scene junctions, not arbitrary L/T/cross arrangements. Production promotion remains on hold for human review.
