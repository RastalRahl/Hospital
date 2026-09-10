# Architecture Master C3 Validation v1

## Recommendation: REGENERATE MASTER

C3 cannot be deterministically extracted. Its generated room is not registered to the canonical 32 px Architecture grid. This validation stopped before temporary extraction or reconstruction, as required.

## Measured mismatch

| Landmark | Canonical | Observed candidate | Deviation |
| --- | --- | --- | --- |
| Wall run left/right | 128 / 1408 | 80 / 1455 | -48 / +47 px |
| Five x boundaries | 128, 384, 640, 896, 1152, 1408 | 80, 355, 630, 905, 1180, 1455 | -48, -29, -10, +9, +28, +47 px |
| Wall/floor | 416 | 580 | +164 px |
| Internal floor | 672 | 665 | -7 px |
| Front-cutaway top | 768 | 753 | -15 px |
| Floor/front bottom | 928 | 819 | -109 px |
| Door frame | 640,0..896,416 | 652,235..883,580 | +12/-13 x; +235/+164 y |
| Glazing | 704,120..832,320 | 703,278..835,515 | -1/+3 x; +158/+195 y |

The horizontal run is approximately 275 px per generated cell rather than 256 px. More importantly, vertical landmarks are not related by one uniform transform: the entire wall is dropped, while the lower floor/front region is compressed. The door frame and glazing are therefore not merely decorative insets.

## Required correction

Regenerate C3 using the supplied clean scaffold/overlay without a vignette, perspective floor expansion, or arbitrary wall/floor scaling. Preserve the exact canonical outer run, opening `640..896 × 0..416`, floor bounds, and specified glazing rectangle.

## Scope

All files remain reference-only. No Batch 12 metadata, temporary candidate module, reconstruction, manifest, catalog, or approved Architecture asset was changed.
