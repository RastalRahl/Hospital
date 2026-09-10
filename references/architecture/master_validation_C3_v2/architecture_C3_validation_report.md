# Architecture Master C3 Locked-Edit Validation v2

## Result

**PASS.** C3 v3 is pixel-locked to validated C1 outside the declared glazing edit rectangle. Its structural geometry is therefore unchanged. This validation is reference-only and has not created a Production Batch 12 asset.

## Pixel lock

- C1 and C3 are both `1536×1024` `RGB` images.
- Changed pixels: `24000`.
- Difference box: `704,120,824,320` (exclusive), exactly matching the authorized `704,120,824,320` region.
- Out-of-region changes: `0`.

## Geometry and glazing

The canonical structural run, vertical grid, horizontal boundaries, and `640,0..896,416` doorway retain `0 px` deviation. The glazing is contained in the inner `712,128..816,312` rectangle: clear of the door frame, left hinge hardware, and handle; large enough to distinguish C3 from the solid C1 door.

## Temporary candidate and reconstruction

A temporary untrimmed `256×416` source crop was nearest-neighbour normalized to `32×52` using `architecture_grid_preserving`. Its structural edges remain intact; alpha is intentionally full. Both the original five-cell and new eight-cell reconstructions pass with zero interior floor alpha gaps, continuous cap/base/teal/baseline/threshold alignment, and no cumulative drift.

## Scope

C3 remains outside the manifest and catalog pending a future explicit production-ingestion instruction.
