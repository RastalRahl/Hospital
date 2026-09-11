# D4 local appearance checks

Result: **LOCAL_CANDIDATE_CHECKS_PASS**.

These are local saved-file checks. The repository full suite was not run here.

| View | Native | 8x | Changed RGB | Changed alpha |
|---|---|---|---:|---:|
| main | 32x12 RGBA | 256x96 RGBA | 384 | 0 |
| repeat | 32x12 RGBA | 256x96 RGBA | 384 | 0 |

Both native alpha maps and exact exports match their source geometry.
Committed south-west and south-east crop reproduction errors: {'southwest': 0, 'southeast': 0}.

Original 4x2, relocated +32,+32 and 3x3 enclosure: all local checks pass.
Each front corner: 32 intentional opaque overlap pixels. Each back corner: 48.
No unexpected overlap, stacked or hidden glass, missing contacts or clipping in the tested layouts.
D1/D2/D3 source layers unchanged; differences against scaffold scene confined to D4.
Negative controls: 12; each must reject its actual broken fixture.
Unchanged local source files: 15. This is not a repository-wide preservation claim.

Historical proposed geometry and production state were not modified.
