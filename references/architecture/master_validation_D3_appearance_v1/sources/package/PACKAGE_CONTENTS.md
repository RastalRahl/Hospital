# D3 locked appearance review bundle

This is a reference-only appearance candidate and reproducible local check package.
It is NOT an approved production asset pack or repository snapshot.

## Handoff
Use the existing Hospital Codex conversation, GPT-6 Astra / Medium.
Attach this ZIP and ask Codex to read CODEX_PROMPT.txt at the root.
The prompt authorizes independent reference-only validation, not ingestion.

## Contents
- candidate/: four mutually exclusive native RGBA views and four exact 8x exports.
- sources/: unchanged committed D3 flat scaffolds plus hash-verified existing D1/D2,
  plain floor and right wall inputs. No fonts or generated reference boards.
- previews/: compositions made from the saved candidates and separate backgrounds.
- reports/: candidate specification, source provenance and local measured checks.
- tools/build_d3_appearance.py: deterministic RGB authoring and local checks.
- CODEX_PROMPT.txt: complete next task for Codex.
- SHA256SUMS.txt: hashes of all other supplied files.

## Geometry and status
Geometry authority: RastalRahl/Hospital commit
65aca7a461a60d49e57e4b82257e782fc9c9b1d0,
references/architecture/master_validation_D3_v1/d3_geometry_alpha_contract_proposed.json.
The canonical repository contract is NOT rewritten or supplied as an invented new
canonical file. Fetch it from the repository when validating this package.

ChatGPT visual assessment: the right-side cutaway and appearance are suitable
for independent technical validation, limited to the reviewed NW/NE enclosure.
This is assistant review evidence, not a human production approval.
The repository contract's historical proposed status remains unchanged.

No geometry changes, alpha changes, finished-D2 image reflection, or baked
background. Screen-left bevel lighting is intentionally consistent with D2;
identical straight material pixels do not constitute a left/right sprite flip.
The distinctive right-side return and cell anchors are retained.

## Local verification
Run `python tools/build_d3_appearance.py` with Pillow and numpy installed.
Local PASS does not substitute for the repository's full suite or independent
Codex validation. The package's input hashes must remain intact.
