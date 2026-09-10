# Independent D3 appearance validation

The original ZIP and all extracted members are unchanged in `sources/`. Package scripts were not executed. Supplied local reports and ChatGPT review are supporting context; independent evidence is outside `sources/`.

Start with `d3_appearance_validation_report.md` and `artifacts/d3_appearance_review_montage.png`. Original/relocated corners, enclosures, right-wall contexts, repeat runs, separate backgrounds and composites are saved individually. No montage crop supplies artwork.

Run `python tools/validate_architecture_d3_appearance.py`, then the complete suite with `python -m pytest -q`. Actual test output is captured separately. Reused helpers accept an explicit reference PNG or output directory; their original defaults are unchanged and no historical generator was rerun.

All four views are mutually exclusive representations of one future logical D3 asset. Historical geometry remains `PROPOSED_FOR_HUMAN_GEOMETRY_REVIEW`; no human approval record is created. Identical D2/D3 straight-view material pixels, where present, are not artificially changed.

`production_before.json` and initial package hashes must never be refreshed to bypass preservation. Existing files stay protected even within an authorized directory. Git attributes preserve package text and binary bytes on checkout. Pinned contract comparison accounts only for Git LF/Windows CRLF conversion; exact local historical bytes remain separately locked.
