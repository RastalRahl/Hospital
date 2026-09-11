# D4 locked appearance candidate

Reference-only candidate for `hospital_glass_partition_front_cutaway_01`.
Not an approved production batch and not an installation package.

## Contents

- `candidate/`: two 32x12 native RGBA views and their exact 256x96 exports.
- `sources/`: 15 unchanged reference PNGs, including the pinned D4 scaffolds,
  committed corner crops, validated D1-D3 artwork and the approved floor.
- `previews/`: actual file-based repeats, separate backgrounds/objects/layers,
  complete enclosures, front corner views and the appearance review board.
- `reports/`: candidate specification, source mapping/hashes, local computed
  checks and the byte-identical candidate rebuild check.
- `tools/build_d4_appearance.py`: reproducible native-grid appearance builder.
  Requires Pillow and numpy. It writes only within this package and never
  changes source PNGs or a production repository.
- `CODEX_PROMPT.txt`: complete independent validation handoff.
- `SHA256SUMS.txt`: package checksums, excluding this checksum file itself.

## Scope

All geometry and alpha match the corresponding D4 scaffold at commit
`2ec243597e60f55435983d2de6a64592273d5f6f` in `RastalRahl/Hospital`.
The authoritative contract stays in the repository at
`references/architecture/master_validation_D4_v1/d4_geometry_alpha_contract_proposed.json`.
It is not duplicated here or given a new approval status.

Main and repeat are mutually exclusive views of ONE logical asset. Use main
for the last panel and repeat for preceding panels. Do not stack them.

Appearance changes affect RGB only. Backgrounds and the yellow test object
are separate preview layers, never embedded in the candidate.

Local checks do not replace the repository's full automated suite or final
human production review. Historical proposed geometry status is unchanged.
The builder's candidate output is deterministic. Review typography can vary
with the local Pillow version/font availability; no fonts are distributed.
