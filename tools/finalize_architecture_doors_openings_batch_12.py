"""Explicitly finalize the human-approved Architecture Production Batch 12."""
from __future__ import annotations

import csv
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

from rastalr_pipeline import core
from build_architecture_doors_openings_batch_12 import _compose_wall_run, _labelled_board, _save


BATCH_PATH = Path("metadata/production_batch_12_architecture_doors_openings.json")
QA_JSON_PATH = Path("metadata/architecture_doors_openings_batch_12_qa.json")
QA_MD_PATH = Path("metadata/architecture_doors_openings_batch_12_qa.md")
APPROVED_CONTACT_PATH = Path("previews/contact_sheets/architecture_doors_openings_batch_12_approved.png")
APPROVED_BUNDLE_PATH = Path("release/production_batch_12_architecture_doors_openings_approved_bundle.zip")
REVIEW_ARTIFACT = "previews/architecture/production_batch_12_architecture_doors_openings_qa_montage.png"
ASSET_IDS = [
    "hospital_door_single_closed_01",
    "hospital_door_single_half_open_01",
    "hospital_door_glazed_closed_01",
    "hospital_double_doors_closed_01",
    "hospital_double_doors_half_open_01",
    "hospital_sliding_clinical_doors_closed_01",
    "hospital_sliding_clinical_doors_open_01",
    "hospital_equipment_opening_wide_01",
]


def _image_dimensions(path: str) -> list[int]:
    with Image.open(core.repo_path(path)) as opened:
        image = core.ensure_rgba(opened)
    return [image.width, image.height]


def _compose_final(asset: dict, columns: int, start_cell: int):
    """Re-use the proven reconstruction logic while reading only final files."""
    temporary = dict(asset)
    temporary["normalized_path"] = asset["final_path"]
    temporary["components"] = [
        {**component, "normalized_path": component["final_path"]}
        for component in asset.get("components", [])
    ]
    return _compose_wall_run(temporary, columns, start_cell)


def _verify_final_assets(assets: list[dict]) -> None:
    component_filenames: set[str] = set()
    for asset in assets:
        final = core.repo_path(asset.get("final_path", ""))
        staged = core.repo_path(asset.get("normalized_path", ""))
        if not final.is_file() or not staged.is_file():
            raise FileNotFoundError(f"Missing staged or final main module for {asset['id']}")
        if core.sha256_file(final) != core.sha256_file(staged):
            raise ValueError(f"Approved main module differs from staged candidate: {asset['id']}")
        if _image_dimensions(asset["final_path"]) != asset["expected_native_dimensions"]:
            raise ValueError(f"Approved main dimensions changed: {asset['id']}")
        if asset.get("normalization_mode") != "architecture_grid_preserving":
            raise ValueError(f"Approved module lost grid-preserving normalization: {asset['id']}")
        for component in asset.get("components", []):
            component_filenames.add(component["filename"])
            final_component = core.repo_path(component.get("final_path", ""))
            staged_component = core.repo_path(component.get("normalized_path", ""))
            if not final_component.is_file() or not staged_component.is_file():
                raise FileNotFoundError(f"Missing staged or final component for {asset['id']}/{component['role']}")
            if core.sha256_file(final_component) != core.sha256_file(staged_component):
                raise ValueError(f"Approved component differs from staged candidate: {asset['id']}/{component['role']}")
            if _image_dimensions(component["final_path"]) != component["expected_native_dimensions"]:
                raise ValueError(f"Approved component dimensions changed: {asset['id']}/{component['role']}")
            if not isinstance(component.get("anchor_relative_to_logical_native"), list):
                raise ValueError(f"Approved component anchor is missing: {asset['id']}/{component['role']}")

    with (core.ROOT / "metadata/catalog.csv").open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    catalog_ids = [row["id"] for row in rows]
    if any(catalog_ids.count(asset_id) != 1 for asset_id in ASSET_IDS):
        raise ValueError("Catalog does not contain exactly one row for each Batch 12 logical asset.")
    if component_filenames & set(catalog_ids):
        raise ValueError("A technical component was incorrectly added as a logical catalog row.")


def _write_approval_records(assets: list[dict], reviewed_at: str) -> None:
    batch = json.loads((core.ROOT / BATCH_PATH).read_text(encoding="utf-8"))
    batch["status"] = "approved"
    batch["purpose"] = "Validated C1-C8 production assets; human visual review PASS and approved for production. Components remain implementation files attached to their one logical asset."
    batch["human_visual_review"] = {
        "result": "PASS", "reviewed_artifact": REVIEW_ARTIFACT,
        "reviewed_at": reviewed_at, "reviewer_instruction": "User explicitly approved all eight Batch 12 logical assets.",
    }
    batch["approval"] = {"status": "approved", "approved_asset_ids": ASSET_IDS, "approved_at": reviewed_at}
    (core.ROOT / BATCH_PATH).write_text(json.dumps(batch, indent=2) + "\n", encoding="utf-8")

    manifest = core.load_manifest()
    by_id = {asset["id"]: asset for asset in manifest["assets"]}
    for asset_id in ASSET_IDS:
        by_id[asset_id]["human_visual_review"] = {
            "result": "PASS", "reviewed_artifact": REVIEW_ARTIFACT, "reviewed_at": reviewed_at,
            "batch": "Architecture Production Batch 12: Doors & Openings",
        }
    core.save_manifest(manifest)

    qa = json.loads((core.ROOT / QA_JSON_PATH).read_text(encoding="utf-8"))
    qa["technical_status"] = qa.get("technical_status") if qa.get("technical_status") in {"pass", "warning", "fail"} else "pass"
    qa["status"] = "approved"
    qa["review_state"] = "approved"
    qa["human_visual_review"] = {"result": "PASS", "reviewed_artifact": REVIEW_ARTIFACT, "reviewed_at": reviewed_at}
    qa["manifest_counts"]["after"] = {"manifest": 220, "approved": 220, "needs_human_review": 0}
    qa["artifacts"]["approved_contact_sheet"] = APPROVED_CONTACT_PATH.as_posix()
    qa["artifacts"]["approved_bundle"] = APPROVED_BUNDLE_PATH.as_posix()
    for report in qa["assets"]:
        asset = by_id[report["id"]]
        report["approved_production_path"] = asset["final_path"]
        for component_report, component in zip(report["components"], asset.get("components", []), strict=True):
            component_report["approved_production_path"] = component["final_path"]
    (core.ROOT / QA_JSON_PATH).write_text(json.dumps(qa, indent=2) + "\n", encoding="utf-8")
    with (core.ROOT / QA_MD_PATH).open("a", encoding="utf-8", newline="\n") as file:
        file.write("\n## Human visual approval\n\n")
        file.write(f"**APPROVED.** Human visual review recorded `PASS` on `{reviewed_at}` against `{REVIEW_ARTIFACT}`. All eight logical assets were promoted with their five implementation components; components remain non-logical and are absent from the catalog.\n")


def _write_approved_bundle(assets: list[dict]) -> None:
    target = core.ROOT / APPROVED_BUNDLE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    required = [BATCH_PATH, QA_JSON_PATH, QA_MD_PATH, Path("metadata/manifest.json"), Path("metadata/catalog.csv"), APPROVED_CONTACT_PATH]
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative in required:
            archive.write(core.ROOT / relative, relative.as_posix())
        for asset in assets:
            archive.write(core.repo_path(asset["final_path"]), f"assets/{asset['filename']}")
            for component in asset.get("components", []):
                archive.write(core.repo_path(component["final_path"]), f"assets/components/{asset['id']}/{component['filename']}")


def main() -> int:
    manifest = core.load_manifest()
    before = {
        "manifest": len(manifest["assets"]),
        "approved": sum(asset.get("approval_status") == "approved" for asset in manifest["assets"]),
        "needs_human_review": sum(asset.get("approval_status") == "needs_human_review" for asset in manifest["assets"]),
    }
    if before != {"manifest": 220, "approved": 212, "needs_human_review": 8}:
        raise ValueError(f"Unexpected pre-finalization state: {before}")
    by_id = {asset["id"]: asset for asset in manifest["assets"]}
    if set(ASSET_IDS) - set(by_id):
        raise ValueError("A required Batch 12 asset is missing from the manifest.")
    if any(by_id[asset_id].get("approval_status") != "needs_human_review" for asset_id in ASSET_IDS):
        raise ValueError("Only the eight Batch 12 review candidates may be promoted.")
    if any(by_id[asset_id].get("qa_status") != "pass" for asset_id in ASSET_IDS):
        raise ValueError("Batch 12 technical QA must pass before human approval promotion.")

    core.approve_assets(ASSET_IDS)
    reviewed_at = datetime.now(timezone.utc).isoformat()
    _write_approval_records([], reviewed_at)
    core.run_qa()
    core.write_catalog()
    manifest = core.load_manifest()
    by_id = {asset["id"]: asset for asset in manifest["assets"]}
    assets = [by_id[asset_id] for asset_id in ASSET_IDS]
    after = {
        "manifest": len(manifest["assets"]),
        "approved": sum(asset.get("approval_status") == "approved" for asset in manifest["assets"]),
        "needs_human_review": sum(asset.get("approval_status") == "needs_human_review" for asset in manifest["assets"]),
    }
    if after != {"manifest": 220, "approved": 220, "needs_human_review": 0}:
        raise ValueError(f"Unexpected finalization state: {after}")
    _verify_final_assets(assets)

    starts = {asset["id"]: (2 if asset["footprint_width_tiles"] == 1 else 1) for asset in assets}
    staged = [_compose_wall_run(asset, 5, starts[asset["id"]]) for asset in assets]
    final = [_compose_final(asset, 5, starts[asset["id"]]) for asset in assets]
    if any(first.tobytes() != second.tobytes() for first, second in zip(staged, final, strict=True)):
        raise ValueError("Approved file reconstruction differs from validated pending reconstruction.")
    board = _labelled_board(list(zip(ASSET_IDS, final, strict=True)), columns=4, title="Batch 12 — approved production modules in Batch 11 wall context")
    _save(board, APPROVED_CONTACT_PATH)
    _write_approval_records(assets, reviewed_at)
    _write_approved_bundle(assets)
    print(json.dumps({"before": before, "after": after, "approved_ids": ASSET_IDS, "components": sum(len(asset.get("components", [])) for asset in assets)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
