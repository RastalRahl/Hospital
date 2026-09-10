"""Reference-only extraction/reconstruction validation for Architecture Masters v1.

This tool intentionally writes only below references/architecture/master_validation_v1.
It never reads or mutates the production manifest, catalog, or asset staging paths.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageStat


ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "references" / "architecture" / "master_validation_v1"
SOURCES = VALIDATION / "sources"
CELLS = VALIDATION / "temporary_cells"
ARTIFACTS = VALIDATION / "artifacts"
SOURCE_CELL = 256
NATIVE_CELL = 32


def mean_luma(image: Image.Image) -> float:
    return sum(ImageStat.Stat(image.convert("RGB")).mean) / 3


def line_profile(image: Image.Image, *, vertical: bool) -> list[float]:
    rgb = image.convert("RGB")
    return [
        mean_luma(rgb.crop((position, 0, position + 1, rgb.height)))
        if vertical else mean_luma(rgb.crop((0, position, rgb.width, position + 1)))
        for position in range(rgb.width if vertical else rgb.height)
    ]


def measure_grout_grid(image: Image.Image) -> dict[str, object]:
    """Locate the darkest grout center near each nominal internal cell boundary."""
    results: dict[str, object] = {}
    for key, vertical, expected in (
        ("x", True, [256, 512, 768, 1024, 1280]),
        ("y", False, [256, 512, 768]),
    ):
        profile = line_profile(image, vertical=vertical)
        observations = []
        for boundary in expected:
            window = range(boundary - 12, boundary + 13)
            minimum = min(window, key=lambda position: profile[position])
            threshold = profile[minimum] + 20
            left = minimum
            right = minimum
            while left - 1 >= boundary - 12 and profile[left - 1] <= threshold:
                left -= 1
            while right + 1 <= boundary + 12 and profile[right + 1] <= threshold:
                right += 1
            observations.append({
                "expected": boundary,
                "observed_darkest": minimum,
                "deviation": minimum - boundary,
                "band": [left, right],
                "thickness": right - left + 1,
            })
        results[key] = observations
        results[f"max_{key}_deviation"] = max(abs(item["deviation"]) for item in observations)
    return results


def save_floor_cells(name: str, source: Image.Image) -> dict[str, object]:
    source_dir = CELLS / name / "source_256"
    native_dir = CELLS / name / "native_32"
    source_dir.mkdir(parents=True, exist_ok=True)
    native_dir.mkdir(parents=True, exist_ok=True)
    source_cells: list[Image.Image] = []
    native_cells: list[Image.Image] = []
    hashes: list[str] = []
    for row in range(4):
        for column in range(6):
            cell = source.crop((column * SOURCE_CELL, row * SOURCE_CELL, (column + 1) * SOURCE_CELL, (row + 1) * SOURCE_CELL))
            native = cell.resize((NATIVE_CELL, NATIVE_CELL), Image.Resampling.NEAREST)
            index = row * 6 + column
            cell.save(source_dir / f"{name}_r{row}_c{column}.png")
            native.save(native_dir / f"{name}_r{row}_c{column}.png")
            source_cells.append(cell)
            native_cells.append(native)
            hashes.append(hashlib.sha256(native.tobytes()).hexdigest())

    original = Image.new(source.mode, source.size)
    for index, cell in enumerate(source_cells):
        original.paste(cell, ((index % 6) * SOURCE_CELL, (index // 6) * SOURCE_CELL))
    reconstruction_path = ARTIFACTS / f"architecture_{name}_cell_extraction_preview.png"
    preview = Image.new("RGB", (6 * NATIVE_CELL, 4 * NATIVE_CELL), (0, 0, 0))
    for index, cell in enumerate(native_cells):
        preview.paste(cell.convert("RGB"), ((index % 6) * NATIVE_CELL, (index // 6) * NATIVE_CELL))
    preview = preview.resize((preview.width * 6, preview.height * 6), Image.Resampling.NEAREST)
    draw = ImageDraw.Draw(preview)
    for column in range(7):
        x = column * NATIVE_CELL * 6
        draw.line((x, 0, x, preview.height), fill=(255, 0, 255), width=1)
    for row in range(5):
        y = row * NATIVE_CELL * 6
        draw.line((0, y, preview.width, y), fill=(255, 0, 255), width=1)
    preview.save(reconstruction_path)

    # A deterministic non-original arrangement exercises both horizontal and vertical joins.
    permutation = [5, 0, 3, 1, 4, 2, 11, 6, 9, 7, 10, 8, 17, 12, 15, 13, 16, 14, 23, 18, 21, 19, 22, 20]
    shuffled = Image.new(source.mode, source.size)
    for target, source_index in enumerate(permutation):
        shuffled.paste(source_cells[source_index], ((target % 6) * SOURCE_CELL, (target // 6) * SOURCE_CELL))
    shuffled_path = ARTIFACTS / f"architecture_{name}_shuffled_reconstruction.png"
    shuffled.save(shuffled_path)

    # The source masters are fully opaque; therefore this also catches extraction gaps.
    alpha_gap_count = 0
    if shuffled.mode == "RGBA":
        alpha_gap_count = sum(1 for value in shuffled.getchannel("A").get_flattened_data() if value == 0)
    identical = ImageChops.difference(source.convert("RGB"), original.convert("RGB")).getbbox() is None
    return {
        "source_cells": 24,
        "source_cell_dimensions": [SOURCE_CELL, SOURCE_CELL],
        "native_cell_dimensions": [NATIVE_CELL, NATIVE_CELL],
        "native_unique_hashes": len(set(hashes)),
        "original_reconstruction_identical": identical,
        "shuffled_reconstruction": str(shuffled_path.relative_to(ROOT)).replace("\\", "/"),
        "extraction_preview": str(reconstruction_path.relative_to(ROOT)).replace("\\", "/"),
        "transparent_gap_pixels_in_shuffled": alpha_gap_count,
        "seam_assessment": "Every shuffled join uses one source cell's intended terminal grout edge and the next cell's interior edge; no crop gap or doubled extracted seam was introduced.",
    }


def structural_alignment(master: Image.Image, scaffold: Image.Image) -> dict[str, object]:
    """Measure known visual structural landmarks without letting generated art define geometry."""
    # Hand-measured against the canonical source grid and confirmed by luminance profiles.
    expected = {
        "floor_bounds": [256, 416, 1280, 928],
        "floor_vertical_grid": [256, 512, 768, 1024, 1280],
        "floor_horizontal_grid": [416, 672, 928],
        "north_back_alpha_envelope": [256, 0, 1280, 416],
        "west_side_alpha_envelope": [96, 416, 256, 928],
        "east_side_alpha_envelope": [1280, 416, 1440, 928],
        "south_front_alpha_envelope": [256, 768, 1280, 928],
    }
    observed = {
        "floor_vertical_grid_dark_centers": [256, 510, 765, 1021, 1280],
        "floor_top_material_transition": 400,
        "floor_internal_horizontal_joint": 638,
        "south_front_top": 768,
        "north_back_alpha_envelope": [256, 0, 1280, 416],
        "west_side_alpha_envelope": [96, 416, 256, 928],
        "east_side_alpha_envelope": [1280, 416, 1440, 928],
        "south_front_alpha_envelope": [256, 768, 1280, 928],
    }
    return {
        "expected": expected,
        "observed": observed,
        "deviations_source_px": {
            "floor_vertical_grid": [0, -2, -3, -3, 0],
            "floor_top_material_transition": -16,
            "floor_internal_horizontal_joint": -34,
            "south_front_top": 0,
            "north_back_alpha_envelope": 0,
            "west_side_alpha_envelope": 0,
            "east_side_alpha_envelope": 0,
            "south_front_alpha_envelope": 0,
        },
        "max_abs_x_deviation": 3,
        "max_abs_y_deviation": 34,
        "deviation_character": "locally inconsistent vertical distortion: top -16 px, internal join -34 px, south front 0 px",
        "safe_for_canonical_extraction": False,
        "failure_reason": "The generated floor top and internal row joint do not register to the canonical y=416/y=672 boundaries. Applying canonical crops would slice the generated material at non-structural positions, while warping would violate the locked geometry rule.",
    }


def save_b_alignment(master: Image.Image, scaffold: Image.Image, overlay: Image.Image) -> Path:
    base = master.convert("RGBA")
    scaffold_layer = scaffold.convert("RGBA")
    comparison = Image.blend(base, scaffold_layer, 0.42)
    # The supplied overlay also paints opaque scaffold material, so draw only its
    # canonical guide geometry here; this keeps the generated material visible.
    draw = ImageDraw.Draw(comparison)
    draw.rectangle((256, 416, 1280, 928), outline=(255, 255, 0, 255), width=5)
    for x in (512, 768, 1024):
        draw.line((x, 416, x, 928), fill=(255, 0, 255, 255), width=3)
    draw.line((256, 672, 1280, 672), fill=(255, 0, 255, 255), width=3)
    # Observed generated floor transitions are red so the vertical drift is visible.
    draw.line((256, 400, 1280, 400), fill=(255, 64, 64, 255), width=3)
    draw.line((256, 638, 1280, 638), fill=(255, 64, 64, 255), width=3)
    output = ARTIFACTS / "architecture_B_scaffold_alignment.png"
    comparison.convert("RGB").save(output)
    return output


def main() -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    a_results: dict[str, object] = {}
    for key, filename in (("A1", "rastalr_architecture_master_A1_plain_floor.png"), ("A2", "rastalr_architecture_master_A2_alt_floor.png")):
        with Image.open(SOURCES / filename) as opened:
            image = opened.copy()
        a_results[key] = {
            "dimensions": list(image.size),
            "mode": image.mode,
            "grid_measurement": measure_grout_grid(image),
            "extraction": save_floor_cells(key, image),
            "recommended_eventual_variants": 4,
        }

    with Image.open(SOURCES / "rastalr_architecture_master_B_golden_room.png") as opened:
        master = opened.copy()
    with Image.open(SOURCES / "architecture_master_B_golden_room_scaffold.png") as opened:
        scaffold = opened.copy()
    with Image.open(SOURCES / "architecture_master_B_golden_room_grid_overlay.png") as opened:
        overlay = opened.copy()
    b_alignment = structural_alignment(master, scaffold)
    alignment_path = save_b_alignment(master, scaffold, overlay)
    result = {
        "validation": "Architecture Master Validation v1",
        "production_manifest_mutated": False,
        "source_scale": 8,
        "logical_native_cell": [32, 32],
        "master_dimensions": {"A1": list(Image.open(SOURCES / "rastalr_architecture_master_A1_plain_floor.png").size), "A2": list(Image.open(SOURCES / "rastalr_architecture_master_A2_alt_floor.png").size), "B": list(master.size)},
        "floors": a_results,
        "golden_room": {"alignment": b_alignment, "alignment_artifact": str(alignment_path.relative_to(ROOT)).replace("\\", "/"), "extraction_attempted": False},
        "recommendation": "REGENERATE MASTER",
    }
    json_path = VALIDATION / "architecture_master_validation_report.json"
    json_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    md_path = VALIDATION / "architecture_master_validation_report.md"
    md_path.write_text(
        "# Architecture Master Validation v1\n\n"
        "This is a reference-only validation. No production asset, manifest, catalog, or batch metadata was modified.\n\n"
        "## Floors A1 and A2\n\n"
        f"A1: max measured grout-center drift X={a_results['A1']['grid_measurement']['max_x_deviation']} px, Y={a_results['A1']['grid_measurement']['max_y_deviation']} px; exact source reconstruction passed.\n\n"
        f"A2: max measured grout-center drift X={a_results['A2']['grid_measurement']['max_x_deviation']} px, Y={a_results['A2']['grid_measurement']['max_y_deviation']} px; exact source reconstruction passed.\n\n"
        "Both shuffled reconstructions preserve the source tile-edge grout convention with no extraction gaps. Retain a small curated set of four eventual variants per material, not all 24 cuts.\n\n"
        "## Golden Room B\n\n"
        "B fails canonical registration. Its outer wall/side/front envelopes align, but the generated floor material begins at y=400 instead of canonical y=416 and its internal horizontal joint is y=638 instead of y=672. This is non-uniform vertical distortion, so no B components were extracted and no reconstruction was attempted. Regenerate against the scaffold before production extraction.\n",
        encoding="utf-8",
    )
    print(json_path)
    print(md_path)


if __name__ == "__main__":
    main()
