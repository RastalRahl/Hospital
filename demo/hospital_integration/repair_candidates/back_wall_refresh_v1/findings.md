# Back-wall RGB prototype — reference only

**READY FOR HUMAN WALL-PROTOTYPE REVIEW. Not approved; do not propagate yet.**

Source: `assets/architecture/hospital_wall_back_straight_01.png`. The attachment supplied visual direction only; its dimensions and smooth rendering were ignored.

1. **Exact source dimensions:** 32x52 RGBA, fully opaque. Canvas, `wall_center` anchor, 1x1 logical footprint, 32px grid and `[-16,-52]` demo image offset are unchanged. Source bands remain: cap rows0–7, separator8, ivory9–44, lower separator45, teal46–50, bottom outline51. No baseline or connection geometry changes.
2. **Alpha changed pixels: 0.**
3. **RGB changed pixels: 1,607.** All34 candidate colors are sampled from the approved source. The candidate was authored directly on the native raster with discrete clusters; only review previews use nearest-neighbor enlargement. No blur, antialiasing or high-resolution repaint.
4. **4x/8x repetition:** exact32px stride, zero gaps/overlaps and identical opposite edges on all52 rows. Boundary-neighborhood mean RGB difference (30→31,31→0,0→1) falls from94.774 to0. This catches similarly dark edge pairs that a last-versus-first comparison alone would miss. Cap/face/base continuity passes; texture periodicity remains visible.
5. **Godot placement:** all21 perimeter and4 internal copies retain transforms, offsets and draw anchors. Same1664x1088 viewport, camera, 2x zoom, furniture and open-door state. Excluding the HUD label, zero changed screenshot pixels lie outside target wall rectangles.
6. **Visual improvement:** the long wall reads as continuous architecture. Cap/base bands flow between cells. Horizontal navy outlines, the upper highlight and stepped material tones retain crisp depth. The source palette remains compatible with existing doors and glass.
7. **Drawbacks:** the face is calmer and less textured; stepped shading repeats at close zoom, as do subtle base clusters. Unchanged door framing and side/front walls now look more heavily framed. No exposed-end treatment was introduced: this is one repeat-module prototype, not a complete wall family.
8. **Propagation recommendation:** ready for human assessment of the continuous-wall direction, **not recommended for automatic family-wide propagation yet**. Confirm acceptable face texture/depth and exposed-end treatment first. No02/03/04 or other-family edits.

## Evidence and reproduction

`wall_review_montage.png` combines unscaled Godot crops. `godot_before.png` / `godot_after.png` are full viewport captures; `godot_8cell_before.png` / `godot_8cell_after.png` are tight eight-cell crops saved by Godot. `repeat_comparison.png` shows1/4/8 copies at4x display zoom. `candidate_8x.png`, `rgb_change_mask.png`, `rgb_absolute_diff.png` and `rgb_diff_diagnostic.png` support pixel inspection. White mask pixels mean RGB changed. `checks.json` records hashes and measurements.

In the existing demo press **V** to compare; startup uses the approved original. Alternatively run `launch.ps1 -Godot '<installed executable>' -WallReview`. No production path or runtime-manifest replacement occurs. The small review ZIP contains only14 prototype-evidence files, without engine caches.

**Verification:** 5 focused tests passed. Full repository suite ran once: **372 passed in96.19s**. Completion Godot smoke ran once: **HOSPITAL_SMOKE_PASS**. Dedicated wall comparison: **WALL_PROTOTYPE_REVIEW_PASS**, Godot4.7.1, Compatibility renderer, NVIDIA RTX3050 Laptop. Existing sandbox certificate/cache warnings did not prevent rendering.

Inventory remains **224 manifest / 220 approved / 4 needs_human_review**. Batch13 stays pending. Approved source bytes, layout and unrelated user changes remain unchanged. No approval, propagation or D5 work.
