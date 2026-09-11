# Foundation wall family — reference-only refresh

**READY FOR WALL-FAMILY REPAIR STAGING**. This recommends these appearance candidates for review staging, not production replacement or approval. Human approval covers the V2 visual language. Inventory stays 224 / 220 approved / 4 needs_human_review; Batch 13 remains pending.

## Visual findings

1. **Propagation:** the V2 continuous-surface treatment works across back, independently authored left/right shallow boundaries, and low front cutaways. The cap and base no longer restart at every tile. Back 01 is a byte-for-byte copy of the committed V2 candidate. The remaining variants use restrained interior chromatic clusters with seam-safe margins. Front/side transverse shading is sampled separately from each orientation's approved source, retaining its bands and highlights, rather than rotating or mirroring another candidate.
2. **Repeat seams:** none visible in the inspected same/mixed runs or 2x Godot wall crops. All 40 directed adjacency pairs (12 same-variant, 28 cross-variant) have zero RGB edge and three-transition neighborhood differences, with fully opaque joins. All four eight-cell mixed runs use exact 32px stride with no gaps/overlaps. Full-run 32px luminance amplitudes are below 0.000017 on the 0–255 scale. Small chromatic clusters still repeat mathematically; no broad periodic lighting rhythm is visible. The resulting plaster is deliberately quiet, with detail easiest to see enlarged.
3. **Variant compatibility:** no cap/base clash across any tested combination. Back and front variants share boundary profiles; side variants share their orientation's profile. All twelve output byte hashes are distinct. The original metadata assigns no distinct functional role to variants within an orientation: they are alternate sampled surface cells. They remain texture alternatives, not twelve distinct construction capabilities. No inventory changes or invented functional distinctions are warranted.
4. **Corners/terminations — existing representation limitation:** colors now agree, but the existing north/back-to-side junction still makes an abrupt height/cap-direction step, and the exposed internal side-wall end has no dedicated end-cap geometry. These are not fully resolved architectural corners. RGB-only repeated cells cannot provide both seamless internal joins and unique end caps without placement-specific terminal art. No connector art, geometry changes or concealing overlays were added. The northwest/northeast crops show this plainly; the unchanged bedside cabinet partly occludes the northeast junction.
5. **Doors/glass and staging decision:** the quieter wall remains visually compatible with the existing door frame and glass palette. Glass still has its authored frames; the open door remains the earlier unapproved repair. No candidate requires another RGB revision before *repair staging* on this evidence. Future production review must still assess corner/terminal representation separately; this task does not claim a finished connector family.

## Locked geometry and provenance

All alpha maps remain pixel-identical and fully opaque, as in these twelve approved wall sources. Canvas, orientation, wall_center anchor, 1x1 logical footprint and source band coordinates remain fixed. No scale/rotation/mirroring, alpha editing, blur, antialiasing, generated repaint or per-tile luminance gradient. Source and candidate SHA-256 values are recorded per ID in `checks.json`.

Back row bands: cap 0–7; separator 8; ivory 9–44; separator 45; base 46–50; bottom outline 51. Front: outer trim 0–2; shallow ivory face 3–10; separator 11; teal/base 12–18; bottom silhouette 19. Left transverse columns: outer edge 0; cap 1–6; separator 7–8; face 9–16; edge trim 17–18; silhouette 19. Right is independently sourced: silhouette 0; trim 1–2; face 3–10; separator 11–12; cap 13–18; silhouette 19. The original light/dark cross-section is retained for each side, not forced into symmetry. Removed transverse tile borders are internal repeat boundaries, not moved bands.

| Candidate (relative to this folder) | Native RGBA size | Alpha changes | RGB changes vs approved |
| --- | --- | ---: | ---: |
| [hospital_wall_back_straight_01_refresh_candidate.png](hospital_wall_back_straight_01_refresh_candidate.png) | 32×52 | 0 | 1589 |
| [hospital_wall_back_straight_02_refresh_candidate.png](hospital_wall_back_straight_02_refresh_candidate.png) | 32×52 | 0 | 1629 |
| [hospital_wall_back_straight_03_refresh_candidate.png](hospital_wall_back_straight_03_refresh_candidate.png) | 32×52 | 0 | 1629 |
| [hospital_wall_back_straight_04_refresh_candidate.png](hospital_wall_back_straight_04_refresh_candidate.png) | 32×52 | 0 | 1632 |
| [hospital_wall_side_left_01_refresh_candidate.png](hospital_wall_side_left_01_refresh_candidate.png) | 20×32 | 0 | 605 |
| [hospital_wall_side_left_02_refresh_candidate.png](hospital_wall_side_left_02_refresh_candidate.png) | 20×32 | 0 | 620 |
| [hospital_wall_side_right_01_refresh_candidate.png](hospital_wall_side_right_01_refresh_candidate.png) | 20×32 | 0 | 612 |
| [hospital_wall_side_right_02_refresh_candidate.png](hospital_wall_side_right_02_refresh_candidate.png) | 20×32 | 0 | 636 |
| [hospital_front_wall_cutaway_01_refresh_candidate.png](hospital_front_wall_cutaway_01_refresh_candidate.png) | 32×20 | 0 | 601 |
| [hospital_front_wall_cutaway_02_refresh_candidate.png](hospital_front_wall_cutaway_02_refresh_candidate.png) | 32×20 | 0 | 624 |
| [hospital_front_wall_cutaway_03_refresh_candidate.png](hospital_front_wall_cutaway_03_refresh_candidate.png) | 32×20 | 0 | 622 |
| [hospital_front_wall_cutaway_04_refresh_candidate.png](hospital_front_wall_cutaway_04_refresh_candidate.png) | 32×20 | 0 | 622 |

## Engine evidence and scope

Godot 4.7.1.stable.official.a13da4feb, Compatibility/OpenGL on RTX 3050 Laptop. `godot_approved.png` and `godot_refreshed.png` are actual engine captures at identical fixed camera and integer 2x zoom. Seven region pairs cover back, left, right, front, doorway and both north corners. `wall_family_review_montage.png` combines those unscaled crops with smaller 1x overviews and clearly labelled native mixed-run diagnostics. Labels remain outside artwork.

V toggles approved/reference family. All twelve candidate textures load in Godot. The unchanged hospital uses 73 placements of back 01, left 01, right 01 and front 01. Variants 02–04 are checked in the native same/cross/mixed-run evidence, not added as new room placements. All 73 transforms/anchors were asserted unchanged. Pixel differences outside wall rectangles and HUD: **0**. Furniture, floor, glass, door, collisions and layout remain unchanged. Old V1/V2 captures remain intact.

Reproduce candidates with `python build_family.py`, captures with the existing launcher `-FamilyReview`, and montage with `python build_review.py`. The scripts are bounded evidence helpers, not a placement or architecture framework.

Focused checks: **7 passed**. Complete repository suite run once at completion: **374 passed in 77.60s**. Engine import/capture: **WALL_FAMILY_REVIEW_PASS**. Completion Godot smoke, run once: **HOSPITAL_SMOKE_PASS**, including walkthrough/access, door collision/crossing, furniture contacts and glass sorting. Smoke uses the default approved-wall state; the family comparison separately tests only texture substitution and unchanged transforms. Certificate/cache/editor-settings sandbox warnings did not block rendering.

User project.godot, export_presets.cfg and three layout import sidecars are preserved byte-for-byte. Production PNGs, manifest/catalog, prior reference evidence and approval values are unchanged. No Batch 13 approval, door promotion, production repair batch or D5 work.
