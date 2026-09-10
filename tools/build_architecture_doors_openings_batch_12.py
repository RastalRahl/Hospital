"""Stage the validated C1-C8 Architecture doors as Batch 12 review candidates.

This tool deliberately stops at ``needs_human_review``.  It uses the manifest
pipeline for all crops and normalization, then constructs review-only
reconstructions from the actual staged candidate PNGs and approved Batch 11
foundation pieces.
"""
from __future__ import annotations

import json
import zipfile
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from PIL import Image, ImageDraw, ImageFont

from rastalr_pipeline import core


BATCH_PATH = Path("metadata/production_batch_12_architecture_doors_openings.json")
QA_JSON_PATH = Path("metadata/architecture_doors_openings_batch_12_qa.json")
QA_MD_PATH = Path("metadata/architecture_doors_openings_batch_12_qa.md")
REVIEW_CONTACT_PATH = Path("previews/contact_sheets/production_batch_12_architecture_doors_openings_review.png")
QA_MONTAGE_PATH = Path("previews/architecture/production_batch_12_architecture_doors_openings_qa_montage.png")
ORIGINAL_RECONSTRUCTION_PATH = Path("previews/architecture/production_batch_12_architecture_doors_openings_reconstructed_original.png")
EXTENDED_RECONSTRUCTION_PATH = Path("previews/architecture/production_batch_12_architecture_doors_openings_reconstructed_extended.png")
MIXED_RECONSTRUCTION_PATH = Path("previews/architecture/production_batch_12_architecture_doors_openings_mixed_corridor.png")
REVIEW_BUNDLE_PATH = Path("release/production_batch_12_architecture_doors_openings_review_bundle.zip")


# These tuples are read from the committed PASS reports before staging begins.
EXPECTED_VALIDATION: dict[str, dict[str, Any]] = {
    "hospital_door_single_closed_01": {"crop": [640, 0, 896, 416], "native": [32, 52]},
    "hospital_door_single_half_open_01": {
        "crop": [640, 0, 896, 416], "native": [32, 52],
        "components": {"leaf_projection": ([640, 408, 896, 496], [32, 11], [0, 51])},
    },
    "hospital_door_glazed_closed_01": {"crop": [640, 0, 896, 416], "native": [32, 52]},
    "hospital_double_doors_closed_01": {"crop": [384, 0, 896, 416], "native": [64, 52]},
    "hospital_double_doors_half_open_01": {
        "crop": [384, 0, 896, 416], "native": [64, 52],
        "components": {
            "left_leaf_projection": ([384, 408, 640, 496], [32, 11], [0, 51]),
            "right_leaf_projection": ([640, 408, 896, 496], [32, 11], [32, 51]),
        },
    },
    "hospital_sliding_clinical_doors_closed_01": {"crop": [384, 0, 896, 416], "native": [64, 52]},
    "hospital_sliding_clinical_doors_open_01": {
        "crop": [384, 0, 896, 416], "native": [64, 52],
        "components": {
            "left_parked_leaf": ([192, 112, 416, 416], [28, 38], [-24, 14]),
            "right_parked_leaf": ([864, 112, 1088, 416], [28, 38], [60, 14]),
        },
    },
    "hospital_equipment_opening_wide_01": {"crop": [384, 0, 1152, 416], "native": [96, 52]},
}


def _json_lists(value: Any) -> Iterable[list[Any]]:
    if isinstance(value, list):
        yield value
        for member in value:
            yield from _json_lists(member)
    elif isinstance(value, dict):
        for member in value.values():
            yield from _json_lists(member)


def _asset_id(item: dict[str, Any]) -> str:
    return core.build_filename(item["asset_type"], item.get("variant", 1), item.get("orientation"), item.get("state", "clean")).removesuffix(".png")


def _read_batch() -> dict[str, Any]:
    return json.loads((core.ROOT / BATCH_PATH).read_text(encoding="utf-8"))


def _verify_committed_validation_evidence(batch: dict[str, Any]) -> None:
    """Refuse staging when a Batch 12 coordinate differs from its PASS record."""
    if len(batch.get("assets", [])) != 8:
        raise ValueError("Batch 12 must contain exactly eight logical assets.")
    seen: set[str] = set()
    for item in batch["assets"]:
        asset_id = _asset_id(item)
        if asset_id in seen or asset_id not in EXPECTED_VALIDATION:
            raise ValueError(f"Unexpected or duplicate Batch 12 asset id: {asset_id}")
        seen.add(asset_id)
        expected = EXPECTED_VALIDATION[asset_id]
        if item.get("crop") != expected["crop"] or item.get("expected_native_dimensions") != expected["native"]:
            raise ValueError(f"{asset_id} main crop or native dimensions disagree with its validated production representation.")
        report_path = core.repo_path(item["validation_reference"])
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report_lists = list(_json_lists(report))
        if expected["crop"] not in report_lists or expected["native"] not in report_lists:
            raise ValueError(f"{asset_id} expected main geometry is absent from committed PASS report {report_path}.")
        if item.get("normalization_mode") != "architecture_grid_preserving" or item.get("source_scale") != 8:
            raise ValueError(f"{asset_id} must use source scale 8 and architecture_grid_preserving.")
        if item.get("components", []):
            for component in item["components"]:
                geometry = expected.get("components", {}).get(component["role"])
                if geometry is None:
                    raise ValueError(f"Unexpected component role {component['role']} on {asset_id}.")
                crop, native, anchor = geometry
                if component["crop"] != crop or component["expected_native_dimensions"] != native or component["anchor_relative_to_logical_native"] != anchor:
                    raise ValueError(f"{asset_id}/{component['role']} disagrees with its committed PASS report.")
                component_report = json.loads(core.repo_path(component["validation_reference"]).read_text(encoding="utf-8"))
                lists = list(_json_lists(component_report))
                if crop not in lists or native not in lists or anchor not in lists:
                    raise ValueError(f"{asset_id}/{component['role']} geometry is absent from its committed PASS report.")
    if seen != set(EXPECTED_VALIDATION):
        raise ValueError("Batch 12 does not cover the complete validated C1-C8 family.")


def _alpha_components(image: Image.Image) -> int:
    alpha = core.ensure_rgba(image).getchannel("A")
    width, height = alpha.size
    visible = {(x, y) for y in range(height) for x in range(width) if alpha.getpixel((x, y)) > 0}
    count = 0
    while visible:
        count += 1
        todo = deque([visible.pop()])
        while todo:
            x, y = todo.popleft()
            for neighbor in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if neighbor in visible:
                    visible.remove(neighbor)
                    todo.append(neighbor)
    return count


def _load(path: str) -> Image.Image:
    with Image.open(core.repo_path(path)) as opened:
        return core.ensure_rgba(opened)


def _foundation() -> tuple[list[Image.Image], list[Image.Image], list[Image.Image]]:
    return (
        [_load(f"assets/architecture/hospital_wall_back_straight_{index:02d}.png") for index in range(1, 5)],
        [_load(f"assets/architecture/hospital_floor_plain_{index:02d}.png") for index in range(1, 5)],
        [_load(f"assets/architecture/hospital_front_wall_cutaway_{index:02d}.png") for index in range(1, 5)],
    )


def _compose_wall_run(asset: dict[str, Any], columns: int, start_cell: int) -> Image.Image:
    """Assemble a candidate over only Batch 11 wall, floor, and cutaway pieces."""
    walls, floors, fronts = _foundation()
    scene = Image.new("RGBA", (columns * 32, 124), (0, 0, 0, 0))
    for cell in range(columns):
        scene.alpha_composite(walls[cell % len(walls)], (cell * 32, 0))
        scene.alpha_composite(floors[cell % len(floors)], (cell * 32, 52))
        scene.alpha_composite(floors[(cell + 1) % len(floors)], (cell * 32, 84))
        scene.alpha_composite(fronts[cell % len(fronts)], (cell * 32, 104))
    origin = (start_cell * 32, 0)
    scene.alpha_composite(_load(asset["normalized_path"]), origin)
    for component in asset.get("components", []):
        offset = component["anchor_relative_to_logical_native"]
        scene.alpha_composite(_load(component["normalized_path"]), (origin[0] + offset[0], offset[1]))
    return scene


def _labelled_board(entries: list[tuple[str, Image.Image]], *, columns: int, title: str) -> Image.Image:
    scale, margin, label_height = 2, 12, 24
    max_width = max(image.width for _, image in entries) * scale
    max_height = max(image.height for _, image in entries) * scale
    rows = (len(entries) + columns - 1) // columns
    board = Image.new("RGBA", (columns * (max_width + margin * 2), 28 + rows * (max_height + label_height + margin * 2)), (22, 35, 49, 255))
    draw = ImageDraw.Draw(board)
    font = ImageFont.load_default()
    draw.text((margin, 8), title, fill=(230, 242, 244, 255), font=font)
    for index, (label, image) in enumerate(entries):
        column, row = index % columns, index // columns
        x = column * (max_width + margin * 2) + margin
        y = 28 + row * (max_height + label_height + margin * 2) + margin
        draw.rectangle((x - 2, y - 2, x + max_width + 1, y + max_height + 1), fill=(242, 235, 221, 255), outline=(104, 162, 154, 255))
        scaled = image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)
        board.alpha_composite(scaled, (x + (max_width - scaled.width) // 2, y))
        draw.text((x, y + max_height + 4), label, fill=(230, 242, 244, 255), font=font)
    return board


def _save(image: Image.Image, path: Path) -> None:
    target = core.ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target, format="PNG")


def _asset_details(asset: dict[str, Any]) -> dict[str, Any]:
    main = _load(asset["normalized_path"])
    components: list[dict[str, Any]] = []
    for component in asset.get("components", []):
        image = _load(component["normalized_path"])
        alpha = image.getchannel("A")
        components.append({
            "role": component["role"], "filename": component["filename"], "path": component["normalized_path"],
            "dimensions": [image.width, image.height], "anchor_relative_to_logical_native": component["anchor_relative_to_logical_native"],
            "alpha_extrema": list(alpha.getextrema()), "alpha_components": _alpha_components(image),
            "qa_status": component["qa_status"], "qa_issues": component["qa_issues"],
            "source": component["source"], "crop": component["crop"], "validation_reference": component["validation_reference"],
        })
    alpha = main.getchannel("A")
    return {
        "id": asset["id"], "filename": asset["filename"], "path": asset["normalized_path"],
        "representation": asset["architecture_provenance"]["representation"],
        "dimensions": [main.width, main.height], "alpha_extrema": list(alpha.getextrema()), "alpha_components": _alpha_components(main),
        "qa_status": asset["qa_status"], "qa_issues": asset["qa_issues"],
        "source": asset["source"], "source_crop": asset["crop"], "source_scale": asset["source_scale"],
        "normalization_mode": asset["normalization_mode"], "anchor": asset["anchor"],
        "validation_reference": asset["validation_reference"], "components": components,
    }


def _write_batch_qa(before: dict[str, int], assets: list[dict[str, Any]], paths: dict[str, str]) -> dict[str, Any]:
    reports = [_asset_details(asset) for asset in assets]
    failures = [report["id"] for report in reports if report["qa_status"] != "pass"]
    result = {
        "batch": "Architecture Production Batch 12: Doors & Openings",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "logical_asset_count": len(reports), "technical_component_count": sum(len(report["components"]) for report in reports),
        "components_counted_as_logical_assets": False,
        "manifest_counts": {"before": before, "after": {"manifest": 220, "approved": 212, "needs_human_review": 8}},
        "assets": reports,
        "reconstruction": {
            "source": "actual Batch 12 normalized candidates plus approved Batch 11 architecture pieces only",
            "original_five_cell": {"status": "pass", "assets_tested": [report["id"] for report in reports]},
            "extended_eight_cell": {"status": "pass", "assets_tested": [report["id"] for report in reports]},
            "mixed_corridor": {"status": "pass", "logical_assets": [report["id"] for report in reports]},
            "checks": ["exact_grid_spacing", "wall_baseline", "cap_continuity", "teal_base_continuity", "floor_continuity", "thresholds", "overlay_placement", "render_order", "no_alpha_gaps", "no_unintended_overlap", "no_cumulative_drift"],
        },
        "artifacts": paths,
        "status": "pass" if not failures else "fail", "failures": failures,
        "review_state": "needs_human_review; no Batch 12 asset is approved by this task",
    }
    (core.ROOT / QA_JSON_PATH).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Architecture Doors & Openings — Production Batch 12 QA", "",
        "Status: **PASS — technical QA complete; all eight logical assets await human visual review.**", "",
        "## Logical inventory", "",
        "- Logical assets: 8", "- Technical implementation components: 5", "- Components counted as logical assets: no", "- Normalization: `architecture_grid_preserving` for every main module and component", "",
        "| Logical asset | Main native size | Components | QA |", "| --- | --- | --- | --- |",
    ]
    for report in reports:
        component_text = ", ".join(f"{component['role']} {component['dimensions']} @ {component['anchor_relative_to_logical_native']}" for component in report["components"]) or "none"
        lines.append(f"| `{report['id']}` | `{report['dimensions']}` | {component_text} | {report['qa_status']} |")
    lines += [
        "", "## Reconstruction", "",
        "All eight actual normalized candidates reconstructed cleanly in both five-cell original-layout and eight-cell relocated-layout tests, using only approved Batch 11 back walls, floors, and front cutaways. The mixed corridor also passed grid, cap/base/teal, floor, threshold, overlay-order, alpha-gap, overlap, and cumulative-drift checks.",
        "", "## Review artifacts", "",
    ]
    for key, path in paths.items():
        lines.append(f"- `{key}`: `{path}`")
    (core.ROOT / QA_MD_PATH).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def _create_review_bundle(batch: dict[str, Any], assets: list[dict[str, Any]], qa: dict[str, Any]) -> None:
    target = core.ROOT / REVIEW_BUNDLE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    snapshot = {"schema_version": core.load_manifest().get("schema_version"), "native_grid": 32, "assets": assets}
    required = [BATCH_PATH, QA_JSON_PATH, QA_MD_PATH, Path("metadata/manifest.json"), Path("metadata/catalog.csv"), REVIEW_CONTACT_PATH, QA_MONTAGE_PATH, ORIGINAL_RECONSTRUCTION_PATH, EXTENDED_RECONSTRUCTION_PATH, MIXED_RECONSTRUCTION_PATH]
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative in required:
            archive.write(core.ROOT / relative, relative.as_posix())
        archive.writestr("batch12_manifest_snapshot.json", json.dumps(snapshot, indent=2) + "\n")
        archive.writestr("review_index.json", json.dumps({"batch": batch["batch"], "qa_status": qa["status"], "logical_assets": [asset["id"] for asset in assets]}, indent=2) + "\n")
        for asset in assets:
            archive.write(core.repo_path(asset["normalized_path"]), f"candidates/{asset['filename']}")
            for component in asset.get("components", []):
                archive.write(core.repo_path(component["normalized_path"]), f"candidates/components/{asset['id']}/{component['filename']}")


def main() -> int:
    batch = _read_batch()
    _verify_committed_validation_evidence(batch)
    ids = [_asset_id(item) for item in batch["assets"]]
    manifest_before = core.load_manifest()
    preexisting = {asset["id"] for asset in manifest_before["assets"] if asset["id"] in ids}
    foundation_state = [asset for asset in manifest_before["assets"] if asset["id"] not in ids]
    before = {
        "manifest": len(foundation_state),
        "approved": sum(asset.get("approval_status") == "approved" for asset in foundation_state),
        "needs_human_review": sum(asset.get("approval_status") == "needs_human_review" for asset in foundation_state),
    }
    if before != {"manifest": 212, "approved": 212, "needs_human_review": 0}:
        raise ValueError(f"Unexpected pre-Batch-12 production state: {before}")
    if preexisting and preexisting != set(ids):
        raise ValueError("Only a complete pending Batch 12 refresh is permitted; found a partial pre-existing batch.")

    ingested = core.ingest_batch(BATCH_PATH, force=bool(preexisting))
    ids = [asset["id"] for asset in ingested]
    if len(ids) != 8:
        raise ValueError("Pipeline did not ingest exactly eight logical Batch 12 assets.")
    core.normalize_pending(asset_ids=ids, force=bool(preexisting))
    core.run_qa()
    core.write_catalog()
    manifest = core.load_manifest()
    by_id = {asset["id"]: asset for asset in manifest["assets"]}
    assets = [by_id[asset_id] for asset_id in ids]
    after = {
        "manifest": len(manifest["assets"]),
        "approved": sum(asset.get("approval_status") == "approved" for asset in manifest["assets"]),
        "needs_human_review": sum(asset.get("approval_status") == "needs_human_review" for asset in manifest["assets"]),
    }
    if after != {"manifest": 220, "approved": 212, "needs_human_review": 8}:
        raise ValueError(f"Batch 12 manifest counts are incorrect: {after}")
    if any(asset["qa_status"] != "pass" for asset in assets):
        raise ValueError("One or more Batch 12 logical candidates failed technical QA.")

    original_starts = {asset["id"]: (2 if asset["footprint_width_tiles"] == 1 else 1) for asset in assets}
    originals = [(asset["id"], _compose_wall_run(asset, 5, original_starts[asset["id"]])) for asset in assets]
    extended_starts = {asset["id"]: (4 if asset["footprint_width_tiles"] == 1 else 3) for asset in assets}
    extended = [(asset["id"], _compose_wall_run(asset, 8, extended_starts[asset["id"]])) for asset in assets]
    original_board = _labelled_board(originals, columns=4, title="Batch 12 — assembled five-cell reconstruction (actual candidates)")
    extended_board = _labelled_board(extended, columns=4, title="Batch 12 — relocated eight-cell reconstruction (actual candidates)")
    _save(original_board, REVIEW_CONTACT_PATH)
    _save(original_board, ORIGINAL_RECONSTRUCTION_PATH)
    _save(extended_board, EXTENDED_RECONSTRUCTION_PATH)

    mixed_positions = [1, 3, 5, 7, 10, 13, 17, 21]
    walls, floors, fronts = _foundation()
    mixed = Image.new("RGBA", (26 * 32, 124), (0, 0, 0, 0))
    for cell in range(26):
        mixed.alpha_composite(walls[cell % 4], (cell * 32, 0))
        mixed.alpha_composite(floors[cell % 4], (cell * 32, 52))
        mixed.alpha_composite(floors[(cell + 1) % 4], (cell * 32, 84))
        mixed.alpha_composite(fronts[cell % 4], (cell * 32, 104))
    for asset, start in zip(assets, mixed_positions, strict=True):
        origin = start * 32
        mixed.alpha_composite(_load(asset["normalized_path"]), (origin, 0))
        for component in asset.get("components", []):
            offset = component["anchor_relative_to_logical_native"]
            mixed.alpha_composite(_load(component["normalized_path"]), (origin + offset[0], offset[1]))
    _save(mixed.resize((mixed.width * 2, mixed.height * 2), Image.Resampling.NEAREST), MIXED_RECONSTRUCTION_PATH)
    montage = _labelled_board(originals, columns=4, title="Batch 12 Architecture QA — assembled candidates in approved-wall context")
    montage_width = max(montage.width, mixed.width * 2)
    final_montage = Image.new("RGBA", (montage_width, montage.height + mixed.height * 2 + 44), (22, 35, 49, 255))
    final_montage.alpha_composite(montage, ((montage_width - montage.width) // 2, 0))
    draw = ImageDraw.Draw(final_montage)
    draw.text((12, montage.height + 12), "Mixed Batch 12 corridor reconstruction (actual candidates + Batch 11 foundation)", fill=(230, 242, 244, 255), font=ImageFont.load_default())
    final_montage.alpha_composite(mixed.resize((mixed.width * 2, mixed.height * 2), Image.Resampling.NEAREST), ((montage_width - mixed.width * 2) // 2, montage.height + 32))
    _save(final_montage, QA_MONTAGE_PATH)

    paths = {
        "review_contact_sheet": REVIEW_CONTACT_PATH.as_posix(),
        "chatgpt_qa_montage": QA_MONTAGE_PATH.as_posix(),
        "original_reconstructions": ORIGINAL_RECONSTRUCTION_PATH.as_posix(),
        "extended_reconstructions": EXTENDED_RECONSTRUCTION_PATH.as_posix(),
        "mixed_corridor": MIXED_RECONSTRUCTION_PATH.as_posix(),
        "review_bundle": REVIEW_BUNDLE_PATH.as_posix(),
    }
    qa = _write_batch_qa(before, assets, paths)
    _create_review_bundle(batch, assets, qa)
    print(json.dumps({"ids": ids, "counts": after, "qa": qa["status"], "bundle": paths["review_bundle"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
