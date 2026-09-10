# D2 locked appearance candidate v1

This is a reference-only RGB appearance edit over the committed D2 geometry v2 at `4f078aec4aa876e5ac3a806b0ef6a5662f42c8cb`. It is not an approved production asset pack. The deliberate cutaway is a camera presentation choice, not a full-height side elevation.

- `candidate/`: Four alternative native RGBA implementation views and their exact 8x exports. Select one view per cell; never overlay alternatives.
- `sources/`: Byte-preserved source scaffolds, validated D1 files, approved-wall/floor inputs and committed clean-corner reference.
- `previews/`: Actual saved-file reconstructions and separate transmission backgrounds. None is a source for extraction.
- `reports/`: Candidate specification, pinned provenance and local checks. Independent repository validation is pending.
- `tools/build_d2_appearance.py`: Reproducible RGB-only material edit and local image checks. Uses Pillow and numpy. Fonts are not included; preview typography may differ across environments.
- `CODEX_PROMPT.txt`: Exact next reference-validation task. Use the existing Hospital Codex conversation.

Main/repeat: 12x32 native, image anchor [4,16], cell-relative origin [12,0]. Corner-main/repeat: 12x56 native, image anchor [4,40], cell-relative origin [12,-24]. All use logical-cell anchor [16,16] and 32 px depth stride.

No canonical file, approved asset, repository manifest, catalog, approval record or remote repository was modified to create this package. ChatGPT reviewed this candidate; no final human production approval is recorded.
