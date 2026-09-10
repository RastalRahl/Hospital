# D2 locked appearance: local checks

Reference-only candidate. No repository-wide test run or production approval.

| View | Native | Alpha changed | RGB changed | Local result |
| --- | --- | ---: | ---: | --- |
| main | [12, 32] | 0 | 384 | PASS |
| repeat | [12, 32] | 0 | 384 | PASS |
| corner_main | [12, 56] | 0 | 496 | PASS |
| corner_repeat | [12, 56] | 0 | 496 | PASS |

All four alpha maps and all transparent RGBA source pixels are unchanged. Exact 8x blocks verified after reloading.

One/two/four-cell straight and corner runs pass local repeat/transmission checks. The local assembler reproduces the committed scaffold corner pixel-for-pixel before appearance edits.
The appearance assembly retains exactly 48 intended opaque overlap pixels, zero hidden/stacked glass, and unchanged D1 composition.

Eight deliberately broken local controls were rejected. These are local checks, not the repository test-suite total.

Next: independent reference-only validation in Codex. Geometry/appearance user approval and production approval are separate.
