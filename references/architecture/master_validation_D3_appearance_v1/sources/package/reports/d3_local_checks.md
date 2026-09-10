# D3 local appearance checks

Status: PASS_LOCAL_CANDIDATE_CHECKS. These are local package checks, not the repository test suite.

| View | Native | Export | Alpha changes | RGB changes | Invisible RGBA changes |
|---|---|---|---:|---:|---:|
| main | [12, 32] | [96, 256] | 0 | 384 | 0 |
| repeat | [12, 32] | [96, 256] | 0 | 384 | 0 |
| corner_main | [12, 56] | [96, 448] | 0 | 496 | 0 |
| corner_repeat | [12, 56] | [96, 448] | 0 | 496 | 0 |

All eight exports preserve exact 8x blocks and native round-trips. The four native views preserve their scaffold alpha maps.
Straight/corner runs at 1, 2 and 4 cells pass actual pixel, selection, support-width, stride and transmission checks.
North-east and both-corner enclosure checks pass at original and +32,+32 relocated origins; each reviewed corner has 48 intentionally opaque overlapping pixels, no stacked or hidden glass.
D1 pixels and D2 layer bytes remain unchanged; the front stays open. Right-wall context uses a hash-verified approved Batch 11 wall and floor unchanged.
Ten actual negative controls are rejected, each with a passing valid control.
Lighting is independently placed in screen space, not a horizontal flip of D2 finished art.
All input files retained their hashes. No repository, inventory, approval or historical contract was changed.

Run: `python tools/build_d3_appearance.py`. Dependencies: Pillow and numpy.
The package previews are generated from the saved candidate files, not a generative image board.
The scaffold review reconstruction is locally assembled from verified inputs and the committed layout. No claim of matching repository preview PNG encoder bytes is made.
