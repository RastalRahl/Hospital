# D2 revision v2 geometry review

Status: `PROPOSED_FOR_HUMAN_GEOMETRY_REVIEW`. No appearance approval or production ingestion.

Start with `artifacts/d1_d2_corner_clean.png` and `artifacts/d1_d2_corner_annotated.png`, then the proposed contract and report. The montage enlarges the actual saved corner and shows v1, implementation views, repeats, transmission and relocated context.

The recommendation is one explicit **cutaway** proposal. A narrow glazed north return contacts D1's original upper frame and steps down to the shallow side cap. It does not claim a continuous equal-height side rail. Its narrow reveal and abrupt transition require human review before appearance work.

## Implementation views

All views belong to one future logical D2 asset and are mutually exclusive per cell:

- `d2_main_native.png`: 12x32 standalone/terminal side.
- `d2_repeat_native.png`: 12x32 nonterminal side; following cell owns the shared support.
- `d2_corner_main_native.png`: 12x56 single-cell north-west adjacency, with glazed return.
- `d2_corner_repeat_native.png`: 12x56 first cell at the north-west corner when more side cells follow.

Each has an exact `_source_8x.png` export. Origins and anchors are specified in the contract. Never layer two views of the same cell. No D1 assembly mask is used. D1 draws after D2 and owns only the declared opaque overlaps.

The separate `d1_d2_corner_ground_elbow_ownership.png` is ground topology evidence, not a visible patch. Do not render it over the artwork or count it in inventory.

## Reproduction and preservation

Run `python tools/validate_architecture_d2_v2.py` from the repository root. Run the complete suite with `python -m pytest -q`; actual results are captured in `test_results.json` and `test_results.txt`.

`production_before.json` was captured before creating the v2 workspace outputs. Never replace it with current hashes. Every existing canonical, production, D0/D1 and D2 v1 reference file remains protected. Historical report generators were not rerun.

The compact `d2_geometry_review_bundle.zip` contains only the proposed contract, standalone views/exports, report, review images and test/review notes. It excludes repository snapshots and production inventory.
