# Architecture Foundation Batch 11 QA

Architecture modules retain exact opaque connection boxes by design; generic trim/padding is not applied.

| Asset | Native dimensions | Edge alpha | Alpha gaps | QA |
| --- | --- | --- | --- | --- |
| `hospital_floor_plain_01` | 32×32 | 255–255 | 0 | pass |
| `hospital_floor_plain_02` | 32×32 | 255–255 | 0 | pass |
| `hospital_floor_plain_03` | 32×32 | 255–255 | 0 | pass |
| `hospital_floor_plain_04` | 32×32 | 255–255 | 0 | pass |
| `hospital_floor_alt_01` | 32×32 | 232–246 | 0 | pass |
| `hospital_floor_alt_02` | 32×32 | 236–246 | 0 | pass |
| `hospital_floor_alt_03` | 32×32 | 236–246 | 0 | pass |
| `hospital_floor_alt_04` | 32×32 | 236–245 | 0 | pass |
| `hospital_wall_back_straight_01` | 32×52 | 255–255 | 0 | pass |
| `hospital_wall_back_straight_02` | 32×52 | 255–255 | 0 | pass |
| `hospital_wall_back_straight_03` | 32×52 | 255–255 | 0 | pass |
| `hospital_wall_back_straight_04` | 32×52 | 255–255 | 0 | pass |
| `hospital_wall_side_left_01` | 20×32 | 255–255 | 0 | pass |
| `hospital_wall_side_left_02` | 20×32 | 255–255 | 0 | pass |
| `hospital_wall_side_right_01` | 20×32 | 255–255 | 0 | pass |
| `hospital_wall_side_right_02` | 20×32 | 255–255 | 0 | pass |
| `hospital_front_wall_cutaway_01` | 32×20 | 255–255 | 0 | pass |
| `hospital_front_wall_cutaway_02` | 32×20 | 255–255 | 0 | pass |
| `hospital_front_wall_cutaway_03` | 32×20 | 255–255 | 0 | pass |
| `hospital_front_wall_cutaway_04` | 32×20 | 255–255 | 0 | pass |

## Reconstruction

6×4 room: 0 visible-interior alpha gaps; cumulative grid drift 0 px.

## Continuity

All back components share 32x52 placement; side modules share 20x32 placement; front modules share 32x20 placement. The reconstruction uses exact canonical offsets, so cap, teal stripe, and base coordinates cannot accumulate drift.

All floor variants retain 32x32 opaque tile boxes; mixed adjacency has no alpha gaps and preserves validated grout edge treatment.
