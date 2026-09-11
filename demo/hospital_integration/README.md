# Hospital integration demo

Godot **4.7.1.stable.official.a13da4feb**, Compatibility/OpenGL 3.3; tested on NVIDIA RTX 3050 Laptop. Independent project; no Gloam dependency. Runtime requires only this directory and Godot 4.7.1. No engine installation or asset generation occurs.

From the repository root in PowerShell:

```powershell
& ./demo/hospital_integration/launch.ps1 -Godot 'C:\Godot\Godot_v4.7.1-stable_win64_console.exe'
```

Or import `project.godot` into Godot and press F6 on `main.tscn` / F5. For an extracted ZIP, run `./launch.ps1 -Godot '<path to Godot executable>'` from its project directory. The launcher puts logs in `.qa` to avoid the restricted user-data log directory encountered on this host. The engine can still warn about unavailable shader caching/certificates in the sandbox; this offline demo does not require either.

Controls: WASD/arrows move; E switches the patient-room door instantly (global debug control); G toggles grid, cyan anchors and orange floor contacts; R resets position; 1/2/3 select integer zoom. Zoom 2 shows the complete floor; zoom 3 follows the figure. Closing is refused while the figure occupies the doorway. The outlined 26x46 figure is a debug reference, not an inventory asset.

`overview_before.png` preserves the original overview byte-for-byte. `overview.png` is the improved 2x Godot overview; `captures/layout_glass_behind.png`, `captures/layout_glass_front.png` and `captures/layout_door_open.png` show the three requested figure poses. The floor is now 21x10 tiles (previously 24x11), with the same 20 prop types. Reception/check-in and waiting are grouped; all six examination props are inside the bay; bedside equipment surrounds the bed with a clear southern approach. `FINDINGS.md` records limitations and executed checks. `runtime_manifest.json` is the complete source/asset mapping: 39 byte-identical PNGs, logical IDs, source paths, status, SHA-256, native sizes, logical footprints, anchors, placements and demo-only collision rectangles. Its source paths are provenance only; runtime loads local `art/` files. There are 20 prop types, Foundation floor/back/left/right/front modules, two sliding-door states plus two additive open-state leaves, and all four pending glass parents (ten selected exclusive views).

The optional `build_demo.py` regenerates the small mapping and copies from this repository's current production files; it is not required to play the extracted project. It uses `views.resolve` and never falls back to historical source art. Approved assets and Batch 13 are untouched. Floor and solid-wall placement follows the Batch 11 reconstruction convention. Glass uses the Batch 13 enclosure helper's north/south centerline geometry; first side returns sort before D1, and D4 sorts after the side terminals. Sprites use native dimensions, nearest filtering, and pixel snapping; no per-asset transforms, opacity overrides or masks.

For the engine smoke run:

```powershell
& ./demo/hospital_integration/launch.ps1 -Godot 'C:\Godot\Godot_v4.7.1-stable_win64_console.exe' -Smoke
```

This runs the layout walkthrough, collision and viewport-pixel assertions, updates `overview.png` and the three named `captures/` images, and puts the disposable debug overlay in `.qa/`. It never overwrites `overview_before.png`. Look for `HOSPITAL_SMOKE_PASS`; a zero exit alone is insufficient because the timeout can end a failed assertion run. Repository tests: `python -m pytest -q`.
