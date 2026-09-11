# Batch13 glass partitions — NEEDS_HUMAN_REVIEW

Four logical assets; twelve mutually exclusive native views. No production approval has been granted.
Native PNGs are byte-identical copies of validated artwork. Working-source scale8 is provenance; never divide these native files by8 again.

Use `rastalr_pipeline.views.resolve(root, asset, index=..., count=..., back_corner=...)` or `views.run`. Missing or corrupt selected files fail; there is no reference-source fallback.
Horizontal runs select repeat until the last main. Side runs select repeat until the last main; at a reviewed north corner only the first cell uses corner_repeat, or corner_main for a one-cell run. Keep the final side support at D4.
These alternatives replace each other once per placement. They are distinct from Batch12 additive components, which remain additive.

All logical footprints are1x1 on a32px grid. Rectangles are half-open [left,top,right,bottom). Image origin = cell origin + cell anchor − image anchor. Add [32,0] per horizontal cell, [0,32] per side cell. The24px side return overhang does not change the logical footprint.

| Parent / view | Native size | Cell anchor | Image anchor | Relative origin | Native path |
|---|---|---|---|---|---|
| hospital_glass_partition_back_01 / main | [32, 28] | [16, 20] | [16, 28] | [0, -8] | `staging/pending/normalized/hospital_glass_partition_back_01.png` |
| hospital_glass_partition_back_01 / repeat | [32, 28] | [16, 20] | [16, 28] | [0, -8] | `staging/pending/normalized/views/hospital_glass_partition_back_01/repeat_01.png` |
| hospital_glass_partition_side_left_01 / main | [12, 32] | [16, 16] | [4, 16] | [12, 0] | `staging/pending/normalized/hospital_glass_partition_side_left_01.png` |
| hospital_glass_partition_side_left_01 / repeat | [12, 32] | [16, 16] | [4, 16] | [12, 0] | `staging/pending/normalized/views/hospital_glass_partition_side_left_01/repeat_01.png` |
| hospital_glass_partition_side_left_01 / corner_main | [12, 56] | [16, 16] | [4, 40] | [12, -24] | `staging/pending/normalized/views/hospital_glass_partition_side_left_01/corner_main_01.png` |
| hospital_glass_partition_side_left_01 / corner_repeat | [12, 56] | [16, 16] | [4, 40] | [12, -24] | `staging/pending/normalized/views/hospital_glass_partition_side_left_01/corner_repeat_01.png` |
| hospital_glass_partition_side_right_01 / main | [12, 32] | [16, 16] | [8, 16] | [8, 0] | `staging/pending/normalized/hospital_glass_partition_side_right_01.png` |
| hospital_glass_partition_side_right_01 / repeat | [12, 32] | [16, 16] | [8, 16] | [8, 0] | `staging/pending/normalized/views/hospital_glass_partition_side_right_01/repeat_01.png` |
| hospital_glass_partition_side_right_01 / corner_main | [12, 56] | [16, 16] | [8, 40] | [8, -24] | `staging/pending/normalized/views/hospital_glass_partition_side_right_01/corner_main_01.png` |
| hospital_glass_partition_side_right_01 / corner_repeat | [12, 56] | [16, 16] | [8, 40] | [8, -24] | `staging/pending/normalized/views/hospital_glass_partition_side_right_01/corner_repeat_01.png` |
| hospital_glass_partition_front_cutaway_01 / main | [32, 12] | [16, 16] | [16, 4] | [0, 12] | `staging/pending/normalized/hospital_glass_partition_front_cutaway_01.png` |
| hospital_glass_partition_front_cutaway_01 / repeat | [32, 12] | [16, 16] | [16, 4] | [0, 12] | `staging/pending/normalized/views/hospital_glass_partition_front_cutaway_01/repeat_01.png` |

Draw separate floor, separate object, D2, D3, D1, D4, in that order. D1 baseline is4px below its ground centerline; D4 trim begins4px above the south centerline and its exclusive image base is8px below it. Do not equate these edges.
The north return and shallow side body are an intentional cutaway. North corners have48 opaque contact pixels apiece; front corners have32 each. D4 owns the visible front trim contact while the side terminal retains its4px exterior shoulder. No assembly masks or stacked translucent panes are used.
Lighting stays upper-left. Use the independently authored orientation; never rotate or mirror finished art. All frame pixels are opaque255; panes retain alpha150 (D1 also210), and declared corner exterior is0. Floors and objects remain separate.
Supported evidence: straight runs, local2x1, rectangular4x2 and3x3 enclosures and translation. A closed enclosure has no entrance. No arbitrary L/T/cross junction, collision/navigation, animation or other orientation is claimed.
Review the staged PNGs and both contact/QA montages. ChatGPT review and automated QA do not replace human production approval. Future explicit approval promotes every required view of a parent together after preflight; it is not executed by this staging command.
The review ZIP preserves normalized paths relative to its root. Reference provenance fields describe external repository history; only the twelve normalized view paths are runtime artwork in this compact package.
