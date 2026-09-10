# D1 local appearance checks

Status: PASS for local geometry/alpha checks. Awaiting user appearance review.

This report was computed from PNG files saved and reloaded in this package.
It is not a claim that the complete Hospital test suite was run.

- Native main panel: 32x28 RGBA.
- 8x source: 256x224, exact nearest-neighbor blocks.
- Canonical alpha changed pixels: 0.
- RGB changed pixels: 796.
- Native RGBA palette entries: 18.
- Alpha histogram: {'150': 421, '210': 11, '255': 464}.
- Pane pixels responding to a background change: 432/432.
- Frame pixels responding to a background change: 0/464.
- 1-, 2-, 4-panel runs: actual pixel checks PASS.
- Six deliberately broken controls: rejected for their intended reasons.
- Wall-context baseline: 52 native; walls y=0, glass y=24.
- Original reference PNGs unchanged.

## Repeat rule

One logical candidate, two implementation views. The main file is standalone/terminal.
The repeat file is used when a glass cell follows on the right; column 27 is extended
through x=28..32, exactly as D0 specifies. The next cell owns the shared post.
Do not layer both views together and do not repeatedly tile the terminal file.
The final pane is 24 px wide; nonterminal panes are 28 px wide, as contracted.

## Limits

No production ingestion or approval, no Git writes, no D2, no all-direction junction claim.
RGB tint and material treatment need user review and later independent Codex validation.

## Provenance

Contract: Hospital commit `9ed992f57585d77448f3e396b8f4dc6f25aa5987`,
`references/architecture/master_validation_D0_v1/d1_geometry_alpha_contract.json`.
Canonical SHA-256: `51a11bddc75b2b51bb387b056f829c79315c0d714459784ab9c0ae3bea3564d6`.
Context input Git blobs are verified in the build script.

## Next Codex maintenance note

D0's whole-tree snapshot test must allow authorized future additions without rewriting
historical evidence or weakening protection of previously approved assets. This package
does not modify that test or any repository file.
