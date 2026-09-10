# Architecture Master Validation v1

This remains a reference-only validation. No production asset, manifest, catalog, or batch metadata was modified.

## Floors A1 and A2 — preserved PASS

The prior A1/A2 results remain unchanged.

## Golden Room B v1 — preserved failure

The original B remains retained for provenance and failed because of non-affine floor y-drift (top -16 px; internal joint -34 px).

## Golden Room B v2 — PASS

B v2 is 1536×1024 RGB and registers to the canonical source component boxes. Its floor begins at y=416, the second cell begins at y=672, and the front/floor component end is y=928. All named wall and floor regions have zero structural-coordinate deviation. The visible grout is deliberately terminal-edge treated (x centres -3 px; horizontal band y=666–669) but does not move component boundaries or cause progressive drift.

Temporary, true-transparent component cuts rebuilt the original room pixel-identically and produced a 6×4 room with no visible-interior alpha gaps or cumulative grid drift. Corners are composed by layer order (floor, back, sides, front); no standalone corner asset was introduced.
