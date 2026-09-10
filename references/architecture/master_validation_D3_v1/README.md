# D3 right-side geometry proposal

Status: `PROPOSED_FOR_HUMAN_GEOMETRY_REVIEW`. This is one proposed right-side counterpart to D2's established cutaway; no appearance or production approval.

Start with `artifacts/northeast_clean.png`, `artifacts/northeast_annotated.png` and `artifacts/enclosure_original_clean.png`. The montage includes enlarged details of both local corners. All scenes are rebuilt from saved D3 scaffolds and actual validated D1/D2 candidates, with approved floors separate.

Four mutually exclusive views belong to one future logical asset:

- `d3_main_native.png`: standalone or terminal straight cell.
- `d3_repeat_native.png`: straight cell followed by another to the south.
- `d3_corner_main_native.png`: single-cell north-east run adjoining D1.
- `d3_corner_repeat_native.png`: first cell adjoining D1 when more side cells follow.

Each has an exact `_source_8x.png` export. Cell/image anchors and reflected half-open regions are specified in `d3_geometry_alpha_contract_proposed.json`. Only structural rectangles were reflected; finished artwork was not mirrored. D3 shading is intentionally flat.

Run `python tools/validate_architecture_d3.py` from the repository root; run the complete suite with `python -m pytest -q`. Captured results are in `test_results.json` and `test_results.txt`. The compact review ZIP excludes the repository and historical snapshots.

Never overwrite `production_before.json` to accommodate later changes. New D3 files are allowed while existing hashes remain mandatory. No manifest/catalog/approval change, Batch 13, D4 or unrelated junction repair is included.
