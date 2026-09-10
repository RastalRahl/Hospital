# RastalR Modern Hospital & Emergency Services

Production repository for the first **RastalR Everyday World** asset pack. It contains deterministic architecture references and a small Pillow-based pilot pipeline; it does not yet contain bulk artwork.

## Quick start

```powershell
python -m pip install -e ".[dev]"
python tools/pilot.py pipeline --batch metadata/pilot_batch.json
python -m pytest
```

1. Put received PNGs in `source/generated/incoming/`.
2. Add one record per intended sprite or crop to `metadata/pilot_batch.json`.
3. Run the pipeline. It preserves source inputs, writes cropped originals to `staging/pending/raw/`, normalized versions to `staging/pending/normalized/`, and marks records `technical_pending`.
4. Review `metadata/qa_report.md` and `previews/contact_sheets/pilot_pending.png`. Human approval is intentionally manual; the pilot pipeline never promotes assets to `assets/`.

See `docs/PIPELINE.md` for batch fields and individual commands.
