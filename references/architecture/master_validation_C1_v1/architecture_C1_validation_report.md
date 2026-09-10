# Architecture Master C1 Validation v1

## Result

**PASS.** C1 retains the canonical five-cell structural run and the central 256×416 source-pixel opening. No grid warping, recrop adjustment, production ingestion, or metadata mutation was performed.

## Geometry registration

- Candidate: `1536×1024` `RGB`; source scale 8.
- Structural span: `x=128..1408`, `y=0..928`; observed structural connection box deviation: `0 px`.
- Vertical cell boundaries: `128, 384, 640, 896, 1152, 1408`; all `0 px` structural deviation.
- Horizontal boundaries: wall/floor `416`, internal floor `672`, front-cutaway top `768`, floor/front bottom `928`; all `0 px` structural deviation.
- Door structural opening: `x=640..896`, `y=0..416`; all `0 px` structural deviation.
- The visible left coverage begins at x=129 and the leaf is recessed within approximately `x=672..872`, `y=72..408`. These are intentional visual insets within the unchanged structural connection box.

## Temporary candidate

`hospital_door_single_closed_01` was cut only to `640,0,896,416`, then nearest-neighbour normalized to `32×52`. It retains the exact structural edges: no alpha trim or safety padding. Its alpha coverage is intentionally full within the module, so generic transparent-background rules are not applicable.

## Reconstruction

- Original five-cell run: passed. Approved Batch 11 wall/floor/front modules join the temporary centre door on the 32 px grid with no alpha gap or overlap in the architectural interior.
- New eight-cell run: passed. The door is placed in the second cell (zero-based column 1), proving no source-position dependency or cumulative drift.
- Cap, teal base, wall baseline, floor, and threshold align. Pixel-identical comparison to the generated master is not expected because the non-door modules are intentionally drawn from approved Batch 11 materials.

## Scope

This is reference-only validation. The temporary files are not a Production Batch 12 asset, and manifest/catalog state remains unchanged.
