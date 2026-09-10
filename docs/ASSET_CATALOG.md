# Asset Catalog and Manifest

`metadata/manifest.json` is the canonical machine-readable inventory. `metadata/catalog.csv` is a generated review/export view and should not be edited as the source of truth.

Each asset has a stable `id` (normally the filename stem), deterministic filename, category/subcategory/type/variant, orientation and state, reuse scope, grid/footprint/anchor, tags, provenance paths/hashes, dimensions, approval status, and QA result. `source_scale` records the explicit positive-integer working-to-native scale (default `1`). `canvas_*` describes the normalized native PNG, while `source_dimensions`, `crop`, and `footprint_*_tiles` respectively preserve source provenance and game placement.

Allowed initial reuse scopes are `hospital_only` and `everyday_world_common`. Typical statuses are `technical_pending`, `needs_human_review`, `approved`, and `rejected`. A unique asset count is the number of non-rejected manifest entries; exports and frames are not separate entries.

Architecture entries may additionally contain an optional `components` array for deterministic implementation PNGs such as an anchored open-door leaf. Components retain their role, exact source crop, dimensions, source scale, alpha policy, and native anchor relative to the one logical asset. They are never separate manifest entries or catalog rows, so they do not increase the logical inventory count. When a logical asset is later explicitly approved, its components move with it into a component subdirectory; approval never creates extra catalog assets.

Filename convention: `asset_type[_orientation][_state]_NN.png`. The clean state and default orientation are omitted. Examples: `hospital_bed_standard_01.png`, `wall_door_north_open_01.png`, and `iv_stand_dual_01.png`.
