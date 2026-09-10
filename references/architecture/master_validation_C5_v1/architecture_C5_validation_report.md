# Architecture Master C5 Validation v1

## Result

**PASS.** C5 preserves C4's grid-locked two-cell doorway and its specified symmetrical open-leaf projections. It was not ingested.

## Geometry

All structural coordinates have 0 px deviation: run `128..1408`, opening `384,0..896,416`, centreline `x=640`, and horizontal references `416,672,768,928`. Left leaf hinge is `(432,88)..(432,408)` and right hinge `(848,88)..(848,408)`; both project inward to `y=496`.

## Recommended representation

**Fixed doorway + two separate leaf overlays.** The grid-locked opening is `512×416` source / `64×52` native. Each geometry-masked below-threshold leaf projection uses one `256×88` source / `32×11` native crop, anchored at `(0,51)` and `(32,51)` relative to the opening. This retains future independent leaf states without making the structural doorway movable or reintroducing drift.

## Reconstruction

The original five-cell and relocated eight-cell runs pass with zero interior floor alpha gaps, continuous cap/base/teal/baseline/threshold behavior, and leaves rendered over the floor.

## Scope

All assets are temporary reference-only validation outputs. No Production Batch 12 metadata or catalog entry was created.
