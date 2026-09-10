# Independent D2 locked appearance validation

Reference-only. The original archive and all extracted members are unchanged in `sources/`. The package builder was not executed. Supplied reports are supporting evidence; independent results are outside `sources/`.

Read `d2_appearance_validation_report.md` and `artifacts/d2_appearance_review_montage.png`. Region diagnostics, one/two/four-cell straight and corner runs, separate backgrounds, original/relocated corners and approved-wall contexts are in `artifacts/`.

Reproduce independent evidence with `python tools/validate_architecture_d2_appearance.py`. Run all tests with `python -m pytest -q`. Captured results are `test_results.json` and `test_results.txt`.

All four supplied views are mutually exclusive representations of one future logical asset. Historical D2 v2 geometry/status remains `PROPOSED_FOR_HUMAN_GEOMETRY_REVIEW`. This validation does not confer human production approval or alter any inventory.

The historical contract is stored as LF in Git and CRLF in this Windows checkout. Pinned text is compared allowing only that line-ending conversion; its exact checkout bytes are independently protected by the untouched initial task snapshot.
