# Wall junction prototype — awaiting human visual review

User authorized this reference-only prototype after identifying disconnected perpendicular walls. No production replacement or approval is performed. Inventory remains **224 / 220 approved / 4 needs_human_review**.

Review [the before/after montage](junction_review_montage.png). The top row is the actual furnished Godot scene, at 1x presentation from integer 2x captures. The six close-up pairs are unscaled 2x Godot crops; only props and the debug figure were temporarily hidden to expose the contacts. Camera, furniture positions, original wall transforms and layout are unchanged.

## Changes and visual assessment

- **Northwest/northeast:** the first side cell owns a 52px north return. Its cap turns into the full-height back cap, replacing the previous diagonal-only painted contact. Left and right use their own source profiles and lighting; neither is a rotated/mirrored rendering.
- **Internal north branch:** a separate branch view lets the back wall's top cap continue across the joint while the vertical return branches down. It does not inherit the exterior corner's top-edge break.
- **Southwest/southeast:** the final side cell owns the turn into the front wall. The ivory face and teal base now reach the outside edge instead of ending against an uninterrupted vertical strip.
- **Internal side-to-full-height wall:** one two-cell view replaces the final two side sprites, joins the horizontal cap, and extends the face/base to the existing wall's baseline. This removes the exposed end above the floor.

Codex inspected all six unobstructed close-ups and the furnished overview: the cap/face connections read continuously, the exterior corners close, and the divider reads as connected architecture. The long narrow north returns are a deliberate cutaway representation, using the existing shallow side-wall profile. Human review should assess that appearance before production adoption.

## Explicit geometry and runtime ownership

`junctions.json` declares six native RGBA views, six placements, seven mutually exclusive source-sprite replacements, logical footprints, image anchors, source hashes and render-sort baselines. All original PNGs and `runtime_manifest.json` remain unchanged. These reference implementation views are **not new catalog assets**.

| View | Native canvas | Logical footprint | Image anchor | Demo use |
| --- | --- | --- | --- | --- |
| north_left | 20x84 | 1x1 | (20,68) | northwest |
| north_right | 20x84 | 1x1 | (0,68) | northeast |
| north_branch | 20x84 | 1x1 | (20,68) | internal north branch |
| south_left | 20x32 | 1x1 | (20,16) | southwest |
| south_right | 20x32 | 1x1 | (0,16) | southeast |
| divider_east | 20x80 | 1x2 | (20,64) | final two divider cells |

The native ground grid stays 32px. Position minus image anchor determines render origin; neither is inferred from PNG size. North return extent is 52px above the first side cell. The divider view owns a 64px two-cell run and a declared 16px southern visual extension. The sprites are tightly rectangular and fully opaque RGBA, without matte padding, filtering, arbitrary canvas trim or background pixels. All colors are sampled from the existing refreshed orientations; the topology is deterministic.

The reference toggle adds exactly three half-open collision rectangles expressed as `[x,y,width,height]`: `[24,88,8,8]`, `[704,88,8,8]`, `[504,320,8,16]`. They complete missing 8px strip contacts; all old collision rectangles are retained unchanged. The internal north and south perimeter contacts already connect and need no additions. J toggles the views and contacts together; turning it off restores the original sprites and contact behavior. G shows these new contacts in magenta. V exits junction mode.

## Verification and limits

- Focused demo tests: **9 passed**. Checks cover exact source hashes, native bodies, perpendicular edge profiles, palette/alpha, unique replacement selection, collision holes and access to all ten existing room destinations.
- Godot review: **WALL_JUNCTION_REVIEW_PASS**. Six views load, seven originals are replaced exclusively, original transforms/contacts remain unchanged, three added contacts block the former gaps, the figure sorts behind/in front of the divider return, and toggling off restores original visibility.
- Existing Godot smoke, run once with this prototype enabled: **HOSPITAL_SMOKE_PASS**. Door crossing/collision, furniture contacts, glass transmission/sorting and reception/exam/patient-room walkthrough pass.
- `review_checks.json`: actual before/after RGB comparison finds **0 changed pixels outside the six declared junction carriers and HUD**. This is a bounded scene comparison, not a universal junction guarantee.
- Full suite: **377 passed in 79.27s**, recorded in `test_results.txt`. Its initial run exposed the earlier operational state document as an unrecognized addition in the historical audit (366 passed, 10 audit failures). The exact `docs/CODEX_PROJECT_STATE.md` addition is now declared separately; no production hashes, snapshots, output ledgers or approval rules were relaxed. A regression test rejects lookalike paths and changes/deletions to any baseline file, including the allowed name if it was present in that baseline.
- A pre/post hash check covers 1,040 files: production assets/staging/metadata, prior repair evidence, runtime manifest and all five unrelated user-owned local files. See `verification.json` for the recorded result.

Only these six existing scene contacts are covered. Arbitrary orientations, generalized L/T/cross junctions and a production connector selection API are not implemented. This is a completed review prototype; production promotion remains on hold for the user's visual decision. Certificate/editor-settings/cache sandbox warnings did not prevent Godot rendering or the explicit pass markers.

## Reproduce

From repository root:

```powershell
python demo/hospital_integration/repair_candidates/wall_junctions_v1/build_junctions.py
& ./demo/hospital_integration/launch.ps1 -Godot 'C:\Godot\Godot_v4.7.1-stable_win64_console.exe' -JunctionReview
python demo/hospital_integration/repair_candidates/wall_junctions_v1/build_review.py
& ./demo/hospital_integration/launch.ps1 -Godot 'C:\Godot\Godot_v4.7.1-stable_win64_console.exe' -JunctionSmoke
```

Review captures and native views stay in this folder. Smoke captures/logs are disposable under the demo's `.qa/`. Do not rerun historical family capture commands merely to inspect this prototype.
