# Architecture Master C4 Validation v1

## Result

**PASS.** C4 retains the canonical five-cell run, intentionally grid-aligned two-cell opening `384..896`, and required `x=640` meeting seam. No production state was changed.

## Geometry

- Candidate: `1536×1024` `RGB`, source scale 8.
- Structural bounds: `128..1408 × 0..928`; vertical grid `128, 384, 640, 896, 1152, 1408`; horizontal boundaries `416, 672, 768, 928`; all `0 px` deviation.
- Double-door crop: `384,0,896,416`; central leaf meeting seam `x=640`, `0 px` deviation.
- Visible material coverage is slightly inset (`130,7..1407,927`) because of cap/panel edge treatment, not structural drift.

## Temporary candidate and reconstructions

The temporary composite is an untrimmed `512×416` source crop, normalized nearest-neighbour to `64×52` under `architecture_grid_preserving`. It remains one composite module so the two leaves cannot drift independently. Both the source five-cell layout and an eight-cell run with the module moved to columns 4–5 pass, with zero interior floor alpha gaps and continuous cap/base/teal/baseline/threshold/seam connections.

## Scope

This is validation evidence only; no Batch 12 asset has been ingested.
