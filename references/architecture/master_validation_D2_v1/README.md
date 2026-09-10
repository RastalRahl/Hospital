# D2 proposed geometry handoff

Status: **PROPOSED_FOR_HUMAN_GEOMETRY_REVIEW**.

This is one deterministic proposal, not final D2 artwork. Its 32×32 native
carrier registers a 14×32 visible side band to the NS ground strip. The proposal
explains the shallow-width heuristic, flat frame/pane regions, endpoints and
repeat ownership. It does not assume the solid side wall or a rotated D1 defines
the correct D2 appearance.

The standalone RGBA files beside the contract are the actual tested scaffolds.
The main view closes a run; the repeat view is used when another depth cell
follows. They are mutually exclusive implementation views of one future asset.
All backgrounds, test objects, masks and labels remain separate.

The D1/D2 corner has aligned base endpoints and a separate topology-only elbow
completion. Its upper-rail/elevation transition remains unresolved. This finding
is retained for human review rather than concealed with a visible connector.

- Contract: `d2_geometry_alpha_contract_proposed.json`
- Native/source: `d2_scaffold_native.png`, `d2_scaffold_source_8x.png`
- Repeat view: `d2_repeat_scaffold_native.png`, `d2_repeat_scaffold_source_8x.png`
- Independent evidence: `d2_geometry_report.json`, `d2_geometry_report.md`
- Review montage: `artifacts/d2_geometry_review_montage.png`
- Compact handoff: `d2_geometry_review_bundle.zip`
- Immutable task baseline: `production_before.json`
- Current protection comparison: `production_preservation.json`
- Complete suite: `test_results.json`, `test_results.txt`

Reproduce with `python tools/validate_architecture_d2.py`; run all tests with
`python -m pytest -q`. Do not regenerate D0/D1 historical evidence. Their files
and all approved artwork remain protected. Only the explicit D2 addition is
authorized; existing baseline files are never exempted by an allowed directory.

No manifest/catalog change, D1/D2 production ingestion or approval, Batch 13,
D3, or general junction repair is included.
