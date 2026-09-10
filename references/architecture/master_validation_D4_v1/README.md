# D4 front-cutaway geometry review

This workspace is reference-only. The proposed contract remains
`PROPOSED_FOR_HUMAN_GEOMETRY_REVIEW`; no geometry or production approval is recorded.

The 32x12 main and repeat scaffolds are two mutually exclusive implementation
views of one future logical asset. Use repeat only when another D4 cell follows
on the right; use main for a standalone or final cell. The source exports are
exact nearest-neighbor 8x versions. They contain no baked background or scene.

The four-pixel upper trim shares only opaque terminal-support pixels with the
unchanged validated side partitions. The six-pixel glass pane and two-pixel base
rail form an eight-pixel foreground face. Both outer four-pixel side shoulders
remain visible. No source masking, new visible connector or extra asset is needed.
This is a proposed rendering choice, not a measured canonical D4 dimension.

Review `d4_geometry_alpha_contract_proposed.json`, `d4_geometry_report.md`, and
`artifacts/d4_geometry_review_montage.png`. Both front corners have clean and
annotated evidence. Separate ground masks establish topology independently of
rendered contacts. The compact `d4_geometry_review_bundle.zip` is the requested
review deliverable, not a repository snapshot or temporary transfer archive.

All reconstructions use the actual saved D4 scaffolds and the latest committed
validated D1/D2/D3 appearance files. Original and relocated 4x2 enclosures and a
3x3 enclosure use approved floor tiles as a separate layer. The closed enclosure
tests connections; it does not imply a usable entrance.

Reproduce with `python tools/validate_architecture_d4.py` and test with
`python -m pytest -q`. `production_before.json` is the immutable task-start
snapshot captured before this workspace was created. Preservation checks allow
only named reference additions; every historical hash remains mandatory.

The first complete-suite invocation collected 237 tests. Creation of this new
workspace while that invocation was running caused two previously loaded
historical preservation tests to reject the new path (235 passed, 2 failed).
Those safeguards were extended only for the explicitly authorized D4 directory.
The final full-suite result and exact output are captured separately in
`test_results.json` and `test_results.txt`.
