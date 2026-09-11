# Back-wall refresh v2 — reference only

**READY FOR FAMILY PROPAGATION** is the visual recommendation, not production approval or authorization to propagate in this task. V1's direction is human-approved; both candidate PNGs remain reference-only. Only `hospital_wall_back_straight_01` was prototyped. No production or approval changes.

- Exact source, v1 and v2: **32x52 RGBA**. Alpha changed: **0** against both v1 and approved. RGB changed: **1,108 vs v1; 1,589 vs approved**. Source/candidate SHA-256 and row-band geometry are in `checks.json`.
- Canvas, wall_center anchor, 1x1 footprint, 32px stride, demo offset [-16,-52], baseline and band boundaries remain fixed. Cap rows 0–7, separator 8, face 9–44, base separator 45, teal 46–50, bottom outline 51. Existing upper-left cap highlight and vertical material shading remain; no horizontal lighting gradient restarts per tile.
- Six columns at each edge are uniform within each row. All seven boundaries in the eight-cell run have **0 edge RGB MAE and 0 three-transition neighborhood MAE**. Exact 32px stride gives no gaps or overlaps. Cap/base rows are continuous across their full width.
- Face variation consists of 18 pixels in four small hard-edged warm/cool clusters, well inside the edge keepout. These are near-isoluminant plaster color details, not dithering, antialiasing or a lighting ramp. Two restrained near-ivory colors supplement the existing v1 base color; alpha is untouched. The face is not a three-rectangle flood fill.

## Seam and periodicity review

Luminance uses Rec.709 coefficients on 0–255 RGB. Diagnostic covers the complete eight-cell run, not only matching outermost pixels. See `checks.json` for each boundary and cap/face/base measurements.

| Metric | Approved | V1 | V2 |
| --- | ---: | ---: | ---: |
| Face column-mean luminance range | 187.58092 | 1.44467 | 0.00013333 |
| Face 32px Fourier amplitude | 23.89738 | 0.46330 | 0.00001043 |
| Base column-mean luminance range | 88.54968 | 4.02912 | 0 |
| Cap column-mean luminance range | 80.60838 | 0.723925 | 0 |

Identical tiles necessarily repeat their chromatic details every 32px; this is not a claim of aperiodic texture. At actual 2x gameplay zoom, the broad stepped ivory rhythm and base variation visible in v1 are absent. No visible 32px luminance pattern remains. The crisp cap, separators and teal base retain depth and the hospital material palette. Door and glass compatibility remains visually consistent.

The tradeoff is a quieter, plainer plaster face: its small color details are barely visible at gameplay zoom, clearer in the nearest-neighbor 8x preview. This is preferable to the broad repeated shading, but should remain visible in human family review. Existing side/front-wall segmentation and junction defects remain exposed and outside scope.

## Engine comparison and verification

Godot **4.7.1.stable.official.a13da4feb**, Compatibility/OpenGL, rendered `godot_approved.png`, `godot_v1.png` and `godot_v2.png` from the same scene, fixed camera and integer zoom 2. `wall_three_way_review.png` uses unscaled Godot crops of the long eight-cell run and internal doorway. No fake backdrop or altered scene art. All 25 back-wall transforms/draw anchors were asserted unchanged. Pixel differences outside back-wall rectangles and the version HUD are **0** for both candidates.

Press **V** to cycle approved / v1 / v2. Approved remains the startup default. Run the existing launcher with `-WallReview` to reproduce all three captures; run `build_review.py` to compose the montage. Prior v1 evidence remains intact.

Focused demo checks: **6 passed**. Complete repository suite run once: **373 passed in 56.09s**. Engine import and three-way capture: **WALL_PROTOTYPE_REVIEW_PASS**. Completion smoke: **HOSPITAL_SMOKE_PASS**, covering movement/access, closed/open collision, crossing, furniture contacts and glass sorting. Sandbox certificate/cache/editor-settings warnings did not prevent import or rendering.

Inventory remains **224 total / 220 approved / 4 needs_human_review**. Production artwork, metadata/catalog, runtime placement manifest and prior v1 evidence are unchanged. Existing user project.godot, export_presets.cfg and three layout import sidecars were verified byte-identical. No propagation, batch, approval or D5 work.
