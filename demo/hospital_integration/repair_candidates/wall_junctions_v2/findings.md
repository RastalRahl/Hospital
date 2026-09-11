# Junction V2 — visual refinement, reference only

[V1/V2 Godot comparison](junction_refinement_review.png). Production promotion remains on hold. The user authorized this refinement after Codex identified framed north returns and abrupt front-cap transitions in V1. The complete V1 workspace remains unchanged.

## Visual result

- **Three north returns:** continue the back wall's ivory face across the upper 52px. Exterior corners retain one outline and a restrained edge shade; the internal branch has continuous plaster. The side cap meets the back base within a short six-row contact instead of running up the full face. This removes the tall-post appearance while keeping the filled corner and shallow side-wall convention.
- **Two front corners:** a four-row slate end closes each side cap before the ivory front cap. The previous slate protrusion into the ivory face is removed. The side/front materials remain different; the end is now explicitly drawn.
- **Lower internal divider:** PNG byte-identical to V1. Its existing joined cap, face and base are retained.

Codex inspected fresh furnished Godot overviews and all six unobstructed close-up pairs. V2 gives the back wall a continuous surface, keeps the connected corners, and makes the cap endpoints legible. The improvement at the front is deliberately small (45 changed native RGB pixels per corner); the north change is the dominant improvement. The return is a low side-wall connection at the back base, not a full-height side wall. This remains a subjective art choice for human review.

## Scope and geometry

This is an RGB-only refinement of five V1 views, with the sixth retained unchanged. It adds no logical assets. All six canvases, alpha maps, logical footprints, anchors, replacement selectors, sort baselines and the three V1 collision additions are identical. The first native side cell beneath each north return is byte-identical at the pixel level; front edits stay in the cap endpoint. Left and right use their own source profiles, without rotation, mirroring, interpolation, blur or new palette colors.

`junctions.json` carries the V1 geometry contract and source hashes plus per-view V1/V2 hashes, changed-pixel counts and measured half-open RGB diff bounds. Six reference views still replace seven source sprites exclusively at six scene contacts. `runtime_manifest.json`, production artwork and approvals are unchanged: **224 manifest / 220 approved / 4 pending**, catalog **224**.

| View | Changed RGB pixels | Alpha changes |
| --- | ---: | ---: |
| north_left | 798 | 0 |
| north_right | 798 | 0 |
| north_branch | 821 | 0 |
| south_left | 45 | 0 |
| south_right | 45 | 0 |
| divider_east | 0 | 0 |

## Review and checks

- J enables the latest junction prototype; K compares V1/V2 using the same sprites and transforms. J off restores original junctions; V exits junction mode. Startup stays approved walls/original junctions.
- `-JunctionReview` now saves fresh V1/V2 captures in this folder and reports **WALL_JUNCTION_REVIEW_PASS**. It checks unchanged original transforms/contacts, the existing three gap contacts, figure Y-sort and restoration of original visibility.
- `-JunctionSmoke` checks K switches both directions, restores V2, then runs the existing full walkthrough: **HOSPITAL_SMOKE_PASS**. Door crossing/collision, furniture contacts, glass transmission/sorting and room access remain functional.
- Focused demo tests: **10 passed**. The new regression checks V1/V2 geometry/alpha/source preservation, palette membership, continuous upper plaster, unobstructed front-cap material and the unchanged lower divider.
- `review_checks.json`: **0 changed Godot pixels outside the five measured native RGB change regions and HUD**. Furnished captures retain all props; close-ups hide props only for inspection. No scene layout changes.
- Full suite, run once: **378 passed in 55.81s**, recorded in `test_results.txt`. All **1,073 protected files remain byte-identical**, recorded in `verification.json`: prior repair workspaces including V1, production assets/staging/metadata, runtime manifest and all five user-owned files.

The six existing scene contacts remain the supported scope. No arbitrary L/T/cross system, new topology, new collision rules or production connector migration was implemented. Certificate/editor-settings/cache sandbox warnings did not block the explicit Godot pass markers.

## Reproduce

From repository root:

```powershell
python demo/hospital_integration/repair_candidates/wall_junctions_v2/build_refinement.py
& ./demo/hospital_integration/launch.ps1 -Godot 'C:\Godot\Godot_v4.7.1-stable_win64_console.exe' -JunctionReview
python demo/hospital_integration/repair_candidates/wall_junctions_v2/build_review.py
& ./demo/hospital_integration/launch.ps1 -Godot 'C:\Godot\Godot_v4.7.1-stable_win64_console.exe' -JunctionSmoke
```

The builder reads V1 but only writes this V2 folder. It reuses V1 metadata and the existing family palette; it is not a new validation framework. Tests/engine logs remain under the demo's disposable `.qa/`; completed evidence is recorded here.
