from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rastalr_pipeline.core import (
    CONTACT_SHEET_PATH, ROOT, approve_assets, create_contact_sheet, create_review_bundle, ingest_batch, normalize_pending,
    remove_confirmed_laboratory_biosafety_debris, run_qa, write_catalog,
)


def parser() -> argparse.ArgumentParser:
    program = argparse.ArgumentParser(description="RastalR Hospital pilot asset pipeline")
    subs = program.add_subparsers(dest="command", required=True)
    ingest = subs.add_parser("ingest", help="Crop and register source PNGs from a batch JSON file")
    ingest.add_argument("--batch", default="metadata/pilot_batch.json")
    ingest.add_argument("--force", action="store_true", help="Refresh existing pending raw files only")
    normalize = subs.add_parser("normalize", help="Trim pending assets and add transparent padding")
    normalize.add_argument("--padding", type=int, default=2)
    normalize.add_argument("--force", action="store_true", help="Refresh existing pending normalized files only")
    normalize.add_argument("--asset-ids", nargs="+", help="Normalize only these explicit pending asset ids")
    subs.add_parser("qa", help="Write technical QA reports for pending assets")
    subs.add_parser("catalog", help="Regenerate metadata/catalog.csv from the manifest")
    approve = subs.add_parser("approve", help="Promote explicitly human-reviewed assets")
    approve.add_argument("asset_ids", nargs="+", help="Manifest ids to promote; never inferred automatically")
    approve.add_argument(
        "--human-qa-disposition",
        help="Required only to approve an asset with technical warnings; stored in the manifest.",
    )
    subs.add_parser(
        "cleanup-confirmed-laboratory-biosafety-debris",
        help="Remove only the human-confirmed native debris pixel from Laboratory Batch 09.",
    )
    contact = subs.add_parser("contact-sheet", help="Create the pending-assets contact sheet")
    contact.add_argument("--columns", type=int, default=5)
    contact.add_argument("--scale", type=int, default=4, help="Integer nearest-neighbor review scale")
    review = subs.add_parser("review-bundle", help="Create a compact metadata-driven review ZIP for one batch")
    review.add_argument("--batch", required=True)
    pipeline = subs.add_parser("pipeline", help="Run ingest, normalize, QA, catalog, and contact sheet")
    pipeline.add_argument("--batch", default="metadata/pilot_batch.json")
    pipeline.add_argument("--padding", type=int, default=2)
    pipeline.add_argument("--columns", type=int, default=5)
    pipeline.add_argument("--scale", type=int, default=4, help="Integer nearest-neighbor review scale")
    pipeline.add_argument("--force", action="store_true", help="Refresh pending artifacts; never approved assets")
    return program


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "ingest":
            print(f"Ingested {len(ingest_batch(args.batch, force=args.force))} asset(s).")
        elif args.command == "normalize":
            print(f"Normalized {len(normalize_pending(padding=args.padding, force=args.force, asset_ids=args.asset_ids))} asset(s).")
        elif args.command == "qa":
            report = run_qa()
            print(f"QA checked {report['assets_checked']} asset(s): {report['status_counts']}")
        elif args.command == "catalog":
            print(f"Wrote {write_catalog().relative_to(ROOT)}")
        elif args.command == "approve":
            print(f"Approved {len(approve_assets(args.asset_ids, human_qa_disposition=args.human_qa_disposition))} asset(s).")
        elif args.command == "cleanup-confirmed-laboratory-biosafety-debris":
            print(f"Cleaned confirmed debris from {remove_confirmed_laboratory_biosafety_debris()}.")
        elif args.command == "contact-sheet":
            print(f"Wrote {create_contact_sheet(columns=args.columns, scale=args.scale).relative_to(ROOT)}")
        elif args.command == "review-bundle":
            print(f"Wrote {create_review_bundle(args.batch).relative_to(ROOT)}")
        elif args.command == "pipeline":
            ingested = ingest_batch(args.batch, force=args.force)
            normalized = normalize_pending(padding=args.padding, force=args.force)
            report = run_qa()
            catalog = write_catalog()
            try:
                contact = create_contact_sheet(columns=args.columns, scale=args.scale)
            except ValueError as error:
                if "No normalized pending assets" not in str(error):
                    raise
                contact = None
            print(f"Ingested {len(ingested)}, normalized {len(normalized)}, QA {report['status_counts']}")
            print(f"Wrote {catalog.relative_to(ROOT)}" + (f" and {contact.relative_to(ROOT)}" if contact else "; no contact sheet (empty batch)."))
    except (FileNotFoundError, FileExistsError, ValueError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
