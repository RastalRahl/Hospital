# Independent D4 locked appearance validation

Reference-only validation against the unchanged D4 proposed geometry contract
at `2ec243597e60f55435983d2de6a64592273d5f6f`. Historical contract status and
approval records remain unchanged. No production approval or ingestion occurs.

The original archive and all 93 members are preserved under `sources/`.
The package's builder was inspected and never executed. Its local reports and
previews are supporting evidence only. New results are separate from the package.

`d4_appearance_validation_report.json` contains expected/observed comparisons,
derived placements, preservation evidence and negative-control outcomes.
The Markdown report summarizes these results. `artifacts/` contains independent
repeats, backgrounds, objects, source layers, clean and annotated front corners,
original/relocated/additional-size enclosures and the compact review montage.

All assemblies use the actual supplied D4 native PNGs and the existing validated
D1/D2/D3 artwork. Main and repeat are alternatives for one logical asset. No
alternative views are stacked. The scene comparison uses the committed D4
scaffolds only as a control; all appearance differences must remain within D4.

The existing enclosure helper gained an optional output-directory argument;
its default behavior is unchanged. New outputs are routed here, never into the
historical geometry workspace. Addition safeguards admit only this named
workspace, while keeping every existing protected hash mandatory.

Reproduce with `python tools/validate_architecture_d4_appearance.py`.
Run the full suite with `python -m pytest -q`.
The clean starting suite was 269 passed; final command, result and output are
captured in `test_results.json` and `test_results.txt`.

This task stops at independent reference validation. It does not authorize
Batch 13 staging, final human review, production ingestion, D5 or junction repairs.
