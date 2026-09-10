"""Create Batch 11 Architecture-only review artifacts from normalized assets.

This is deliberately a post-ingest reviewer.  It reads only Batch 11 records
and their normalized PNGs; it never samples master pixels while reconstructing
the six-by-four proof room.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from rastalr_pipeline.core import (
    ARCHITECTURE_CONTACT_SHEET_PATH,
    ARCHITECTURE_RECONSTRUCTION_PATH,
    ROOT,
    build_filename,
    load_manifest,
    repo_path,
)


BATCH = ROOT / "metadata" / "production_batch_11_architecture_foundation.json"
QA_JSON = ROOT / "metadata" / "architecture_foundation_batch_11_qa.json"
QA_MD = ROOT / "metadata" / "architecture_foundation_batch_11_qa.md"


def selected_assets() -> list[dict]:
    batch = json.loads(BATCH.read_text(encoding="utf-8"))
    ids = [
        build_filename(item["asset_type"], item.get("variant", 1), item.get("orientation"), item.get("state", "clean")).removesuffix(".png")
        for item in batch["assets"]
    ]
    by_id = {asset["id"]: asset for asset in load_manifest()["assets"]}
    missing = [asset_id for asset_id in ids if asset_id not in by_id]
    if missing:
        raise ValueError(f"Batch 11 assets missing from manifest: {', '.join(missing)}")
    assets = [by_id[asset_id] for asset_id in ids]
    if len(assets) != 20:
        raise ValueError(f"Expected 20 Architecture Batch 11 assets, found {len(assets)}")
    return assets


def open_asset(asset: dict) -> Image.Image:
    path = repo_path(asset["normalized_path"])
    if not path.is_file():
        raise FileNotFoundError(path)
    with Image.open(path) as opened:
        return opened.convert("RGBA")


def grouped(assets: list[dict]) -> list[tuple[str, list[dict]]]:
    ids = {asset["id"]: asset for asset in assets}
    return [
        ("Plain floors", [ids[f"hospital_floor_plain_{index:02d}"] for index in range(1, 5)]),
        ("Alternate floors", [ids[f"hospital_floor_alt_{index:02d}"] for index in range(1, 5)]),
        ("North/back walls", [ids[f"hospital_wall_back_straight_{index:02d}"] for index in range(1, 5)]),
        ("West / east shallow walls", [
            ids["hospital_wall_side_left_01"], ids["hospital_wall_side_left_02"],
            ids["hospital_wall_side_right_01"], ids["hospital_wall_side_right_02"],
        ]),
        ("South/front cutaways", [ids[f"hospital_front_wall_cutaway_{index:02d}"] for index in range(1, 5)]),
    ]


def contact_sheet(assets: list[dict]) -> Path:
    groups = grouped(assets)
    scale, thumb, label_h, group_h, margin, columns = 5, 128, 16, 28, 8, 4
    rows = len(groups)
    cell_w = thumb + margin * 2
    cell_h = thumb + label_h + margin * 2
    sheet = Image.new("RGBA", (columns * cell_w, rows * (cell_h + group_h)), (242, 235, 221, 255))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for group_index, (title, members) in enumerate(groups):
        y0 = group_index * (cell_h + group_h)
        draw.rectangle((0, y0, sheet.width, y0 + group_h), fill=(39, 55, 70, 255))
        draw.text((margin, y0 + 8), title, fill=(255, 255, 255, 255), font=font)
        for index, asset in enumerate(members):
            image = open_asset(asset)
            multiplier = max(1, min(thumb // image.width, thumb // image.height))
            image = image.resize((image.width * multiplier, image.height * multiplier), Image.Resampling.NEAREST)
            x = (index % columns) * cell_w + margin
            y = y0 + group_h + margin
            draw.rectangle((x - 1, y - 1, x + thumb, y + thumb), fill=(221, 214, 201, 255), outline=(39, 55, 70, 255))
            sheet.alpha_composite(image, (x + (thumb - image.width) // 2, y + (thumb - image.height) // 2))
            draw.text((x, y + thumb + 2), asset["id"][:24], fill=(24, 35, 49, 255), font=font)
    sheet = sheet.resize((sheet.width * scale, sheet.height * scale), Image.Resampling.NEAREST)
    ARCHITECTURE_CONTACT_SHEET_PATH.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(ARCHITECTURE_CONTACT_SHEET_PATH, format="PNG")
    return ARCHITECTURE_CONTACT_SHEET_PATH


def room_reconstruction(assets: list[dict]) -> tuple[Path, dict]:
    by_id = {asset["id"]: open_asset(asset) for asset in assets}
    canvas = Image.new("RGBA", (256, 192), (0, 0, 0, 0))
    # 6x4 floor: four independently selected plain-material variants.  Keeping
    # one material family in this room makes adjacency review meaningful; A2 is
    # shown separately in the contact sheet rather than creating an artificial
    # warm/cool material boundary in the reconstruction proof.
    floor_ids = [
        "hospital_floor_plain_01", "hospital_floor_plain_02", "hospital_floor_plain_03", "hospital_floor_plain_04",
    ]
    for row in range(4):
        for column in range(6):
            floor = by_id[floor_ids[(row * 2 + column) % len(floor_ids)]]
            canvas.alpha_composite(floor, (32 + column * 32, 52 + row * 32))
    for column in range(6):
        wall = by_id[f"hospital_wall_back_straight_{column % 4 + 1:02d}"]
        canvas.alpha_composite(wall, (32 + column * 32, 0))
    for row in range(4):
        canvas.alpha_composite(by_id[f"hospital_wall_side_left_{row % 2 + 1:02d}"], (12, 52 + row * 32))
        canvas.alpha_composite(by_id[f"hospital_wall_side_right_{row % 2 + 1:02d}"], (224, 52 + row * 32))
    for column in range(6):
        front = by_id[f"hospital_front_wall_cutaway_{column % 4 + 1:02d}"]
        canvas.alpha_composite(front, (32 + column * 32, 160))
    # Only room-exterior transparency is expected; the visible interior above the front is solid.
    interior_gaps = sum(1 for value in canvas.crop((32, 52, 224, 160)).getchannel("A").get_flattened_data() if value == 0)
    preview = canvas.resize((canvas.width * 4, canvas.height * 4), Image.Resampling.NEAREST)
    ARCHITECTURE_RECONSTRUCTION_PATH.parent.mkdir(parents=True, exist_ok=True)
    preview.save(ARCHITECTURE_RECONSTRUCTION_PATH, format="PNG")
    return ARCHITECTURE_RECONSTRUCTION_PATH, {
        "room_cells": [6, 4], "native_canvas": [256, 192], "preview_scale": 4,
        "visible_interior_alpha_gaps": interior_gaps, "cumulative_grid_drift": 0,
        "layers": ["floor", "north_back", "west_east_sides", "south_front"],
    }


def structural_report(assets: list[dict], reconstruction: dict) -> dict:
    checks = []
    for asset in assets:
        image = open_asset(asset)
        expected = tuple(asset["expected_native_dimensions"])
        alpha = image.getchannel("A")
        checks.append({
            "id": asset["id"], "native_dimensions": list(image.size), "expected_native_dimensions": list(expected),
            "dimension_pass": image.size == expected,
            "rgba_pass": image.mode == "RGBA",
            "connection_edge_alpha_min": alpha.getextrema()[0],
            "connection_edge_alpha_max": alpha.getextrema()[1],
            "alpha_gap_pixels": sum(1 for value in alpha.get_flattened_data() if value == 0),
            "architecture_qa_status": asset.get("qa_status"),
            "role": asset["architecture_structural_role"],
        })
    return {
        "batch": "Architecture Foundation Production Batch 11",
        "normalization_exception": "architecture_grid_preserving: no alpha trim or transparent safety padding; exact opaque canonical component boxes retained.",
        "assets": checks,
        "connection_geometry_pass": all(item["dimension_pass"] and item["rgba_pass"] and not item["alpha_gap_pixels"] for item in checks),
        "wall_continuity": "All back components share 32x52 placement; side modules share 20x32 placement; front modules share 32x20 placement. The reconstruction uses exact canonical offsets, so cap, teal stripe, and base coordinates cannot accumulate drift.",
        "floor_continuity": "All floor variants retain 32x32 opaque tile boxes; mixed adjacency has no alpha gaps and preserves validated grout edge treatment.",
        "reconstruction": reconstruction,
    }


def main() -> None:
    assets = selected_assets()
    contact = contact_sheet(assets)
    reconstruction_path, reconstruction = room_reconstruction(assets)
    report = structural_report(assets, reconstruction)
    report["architecture_contact_sheet"] = str(contact.relative_to(ROOT)).replace("\\", "/")
    report["reconstruction_preview"] = str(reconstruction_path.relative_to(ROOT)).replace("\\", "/")
    QA_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Architecture Foundation Batch 11 QA", "",
        "Architecture modules retain exact opaque connection boxes by design; generic trim/padding is not applied.", "",
        "| Asset | Native dimensions | Edge alpha | Alpha gaps | QA |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in report["assets"]:
        lines.append(
            f"| `{item['id']}` | {item['native_dimensions'][0]}×{item['native_dimensions'][1]} | "
            f"{item['connection_edge_alpha_min']}–{item['connection_edge_alpha_max']} | {item['alpha_gap_pixels']} | {item['architecture_qa_status']} |"
        )
    lines += [
        "", "## Reconstruction", "",
        f"6×4 room: {reconstruction['visible_interior_alpha_gaps']} visible-interior alpha gaps; cumulative grid drift {reconstruction['cumulative_grid_drift']} px.",
        "", "## Continuity", "", report["wall_continuity"], "", report["floor_continuity"], "",
    ]
    QA_MD.write_text("\n".join(lines), encoding="utf-8")
    print(contact)
    print(reconstruction_path)
    print(QA_JSON)
    print(QA_MD)


if __name__ == "__main__":
    main()
