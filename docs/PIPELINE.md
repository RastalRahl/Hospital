# Pilot Pipeline

The pipeline processes a small reviewable batch and intentionally stops before approval/final asset promotion.

```text
source/generated/incoming -> staging/pending/raw -> staging/pending/normalized
                                      -> manifest + catalog + QA + contact sheet
```

Install dependencies with `python -m pip install -e ".[dev]"`. Run the full pilot with:

```powershell
python tools/pilot.py pipeline --batch metadata/pilot_batch.json
```

The JSON batch has an `assets` array. Required fields are `source`, `category`, and `asset_type`; paths are repository-relative. Optional `crop` is `[left, top, right, bottom]` using Pillow coordinates. `source_scale` is a positive integer and defaults to `1`; set it explicitly (for example, `8`) only when a sheet was rendered at a known pixel working scale. Supply meaningful `variant`, `orientation`, `state`, `footprint_width_tiles`, `footprint_height_tiles`, `anchor`, `reuse_scope`, `tags`, and `notes` when they differ from defaults.

Grid-locked architecture entries may contain a `components` array when one logical asset needs deterministic implementation layers. Every component declares a stable PNG `filename`, `role`, exact `crop`, `expected_native_dimensions`, `anchor_relative_to_logical_native`, and `alpha_policy`. A validated `mask_polygon_source_px` may be supplied only for an intentional projected overlay; it is a deterministic geometry mask, never an automatic alpha cleanup. Component PNGs are staged and QA'd with their parent, but are not manifest assets or catalog rows.

```json
{
  "assets": [
    {
      "source": "source/generated/incoming/bed_sheet.png",
      "crop": [0, 0, 96, 96],
      "category": "patient_rooms",
      "asset_type": "hospital_bed_standard",
      "source_scale": 8,
      "variant": 1,
      "footprint_width_tiles": 1,
      "footprint_height_tiles": 2,
      "anchor": "bottom_center",
      "reuse_scope": "hospital_only",
      "tags": ["bed", "clean", "furniture"]
    }
  ]
}
```

Useful individual commands:

```powershell
python tools/pilot.py ingest --batch metadata/pilot_batch.json
python tools/pilot.py normalize --padding 2
python tools/pilot.py qa
python tools/pilot.py catalog
python tools/pilot.py contact-sheet --columns 5 --scale 4
```

Normalization converts to RGBA, runs raw technical QA, trims to non-transparent alpha bounds, applies the explicit `source_scale` with nearest-neighbor only, trims again, then adds native-scale transparent safety padding. QA examines both the unnormalized crop (so clipping, background contamination, and accidental padding remain visible) and the normalized output. It flags rather than deletes: missing alpha, opaque canvas borders, source edge clipping, excessive padding, empty images, malformed names, suspicious dimensions, and an implausibly large native canvas relative to its footprint. Contact sheets enlarge these native sprites at 4× by default, also with nearest-neighbor. Re-run with `--force` only to refresh pending artifacts; it never touches approved files.

Create a compact ChatGPT review archive with `python tools/pilot.py review-bundle --batch metadata/production_batch_08_radiology_imaging.json`. It contains only the selected batch metadata, current catalog/manifest/QA/contact sheet, normalized batch PNGs, raw crops for warning assets, and `review_index.json`.
