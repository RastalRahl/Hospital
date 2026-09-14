# Perspective calibration V1 findings

Status: **NEEDS HUMAN VISUAL REVIEW**. These are reference-only repair candidates for three existing logical assets. Production PNGs, staging files, manifest records and approval states are unchanged.

## Result

V1 establishes a consistent rectangular-grid RPG-oblique construction for the repair program:

- depth moves straight upward;
- rear/top and front edges remain parallel;
- the default view has no broad right-side mass or rotated yaw;
- bottom-center feet match the existing 32 px placement contract;
- upper-left lighting and the warm clinical palette remain fixed;
- all sprite pixels use hard alpha and a controlled shared palette.

The candidates are intentionally cleaner and smaller than the approved sprites. Their current approved canvases include a lower three-quarter product-render angle, hundreds of near-duplicate colors and extensive partial alpha. V1 rebuilds the forms at native resolution rather than transforming or downscaling those pixels.

| Logical ID | Approved canvas / opaque colors / partial-alpha pixels | Candidate canvas / opaque colors / partial-alpha pixels | Perspective correction |
|---|---|---|---|
| `reception_counter_straight_01` | 73x41 / 789 / 2,284 | 72x38 / 10 / 0 | Removes the right end face; makes the two-tile top/front modular and parallel. |
| `bedside_cabinet_01` | 35x43 / 619 / 1,047 | 32x36 / 8 / 0 | Removes the turned cabinet side; reduces it against the bed/adult while retaining drawer and cupboard. |
| `medical_cart_base_01` | 39x50 / 893 / 1,261 | 36x42 / 7 / 0 | Removes the diagonal side mass; keeps the raised tray, three drawers and mobile silhouette. |

The generated edit concepts were used only to test massing. They remained high-resolution and smooth, so no generated pixels entered the candidates. `build_candidates.py` authors the final candidate pixels deterministically using the camera contract and controlled palette.

## Review evidence

- `perspective_calibration_review.png`: native approved/candidate sprites enlarged 5x with nearest-neighbor filtering.
- `perspective_calibration_godot.png`: Godot comparison beside the unchanged 26x46 adult, standard bed and waiting chair at integer 2x scale.
- `mapping.json`: exact approved/candidate paths, hashes, dimensions, alpha bounds, footprints and unchanged approval statement.
- `perspective_calibration_review.tscn`: separate practical scene; it does not alter F5 startup or the current hospital layout.

Godot review result:

```text
PERSPECTIVE_CALIBRATION_REVIEW_PASS: 3 candidates rendered with adult, bed and chair anchors; integer scale; matching feet
```

Rebuild and rerun from the repository root:

```powershell
python demo/hospital_integration/repair_candidates/perspective_calibration_v1/build_candidates.py
& 'C:\Godot\Godot_v4.7.1-stable_win64_console.exe' --headless --editor --path 'demo/hospital_integration' --quit
& 'C:\Godot\Godot_v4.7.1-stable_win64_console.exe' --path 'demo/hospital_integration' --scene 'res://perspective_calibration_review.tscn' --log-file '.qa/perspective_calibration_runtime.log' --quit-after 300 -- --perspective-calibration-review
```

## Codex assessment

The three candidates now share one usable camera and physical scale. The counter is a good modular baseline, the bedside cabinet no longer competes with the bed, and the cart remains distinguishable without relying on a turned side face. This is the correct direction for R1–R9. Human acceptance of this calibration is still required before applying it to the remaining 141 perspective repairs or changing production approval state.
