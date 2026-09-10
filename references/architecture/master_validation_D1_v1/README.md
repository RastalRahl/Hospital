# D1 independent reference validation

This workspace validates the supplied locked appearance candidate against the
committed D0 contract. It does not create or approve a production asset.

- `sources/rastalr_D1_locked_appearance_review_bundle.zip`: original attachment.
- `sources/package/`: all 27 extracted members, unchanged. The supplied local
  reports remain here; they are supporting context, not independent proof.
- `d1_validation_report.json` / `.md`: independent results.
- `artifacts/`: reconstructions from actual candidate files, separate backgrounds
  and objects, wall contexts, geometry diagnostic, and negative controls.
- `production_before.json`: initial task snapshot, never refreshed or overwritten.
- `production_preservation.json`: comparison against that initial snapshot.
- `package_provenance.json`: archive and member SHA-256 recorded at extraction.
- `visual_review.json`: explicitly recorded assistant visual findings, separate
  from automated measurements and from human production approval.
- `test_results.json` / `.txt`: complete suite result and captured output.

Run `python tools/validate_architecture_d1.py` and `python -m pytest -q` from the
repository root. Do not run the supplied appearance builder or regenerate D0
historical reports. Candidate files are read only; diagnostics never replace them.

D0's protection check now permits only new files under this explicitly authorized
workspace. Every historical protected path must still exist with its exact hash;
the historical baseline is not updated. This task additionally protects all D0
outputs and existing metadata in its own before/after evidence.

Use the supplied repeat view for a cell with a glass neighbor on the right and
the main view for a standalone/terminal cell. They are mutually exclusive views
of one logical asset. No manifest entry, Batch 13, production approval, D2, or
junction repair belongs to this task.
