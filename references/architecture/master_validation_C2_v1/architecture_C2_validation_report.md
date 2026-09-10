# Architecture Master C2 Validation v1

## Result

**PASS.** The C2 structural doorway remains the canonical `640..896 × 0..416` one-cell box. The half-open leaf is a specified intentional projection, not structural drift. No production metadata was modified.

## Registration

- Candidate: `1536×1024` `RGB`, source scale 8.
- Structural span: `x=128..1408`, `y=0..928`; all structural bounds, five vertical cell lines, and four horizontal reference lines have `0 px` deviation.
- Doorway: `x=640..896`, `y=0..416`; threshold is `y=416`, all `0 px` deviation.
- Left-hinge leaf envelope: `(688,88) → (840,176) → (840,496) → (688,408)`. The leaf’s `x=840` outer edge and `y=496` lowest point are approved projection geometry.

## Temporary representation

**Recommended: split doorway + leaf projection overlay.** The doorway is an exact `256×416` source (`32×52` native) grid module. The below-threshold leaf continuation is a geometry-masked `256×88` source (`32×11` native) overlay anchored at native `(0,51)` relative to the doorway cell. This preserves visible floor around the leaf and avoids treating a projected state as a larger opaque wall tile. No alpha trim or safety padding is applied.

## Reconstruction

- Original five-cell run: passed with the doorway in the centre cell.
- New eight-cell run: passed with the doorway in the second cell.
- Cap/base/teal/wall and floor/threshold connections remain continuous. The projection sits above the floor, has no clipping, and causes no cumulative drift.

## Scope

The components and outputs are temporary reference artifacts only. C2 is not a Production Batch 12 asset and has not been added to the manifest or catalog.
