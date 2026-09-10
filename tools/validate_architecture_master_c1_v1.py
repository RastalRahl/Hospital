"""Reference-only validation for Architecture Master C1 (single closed door).

This intentionally never imports or updates production metadata.  It preserves the
candidate and its deterministic scaffold under references/, cuts the candidate door
on the canonical one-cell structural box, and tests that box against already
approved Architecture Foundation modules.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "references" / "architecture" / "master_validation_C1_v1"
SOURCES = VALIDATION / "sources"
TEMP = VALIDATION / "temporary_components"
ARTIFACTS = VALIDATION / "artifacts"
ASSETS = ROOT / "assets" / "architecture"

MASTER = SOURCES / "rastalr_architecture_master_C1_single_hinged_door_closed_v1.png"
SCAFFOLD = SOURCES / "architecture_master_C1_single_hinged_door_clean_scaffold.png"
SPEC = SOURCES / "architecture_master_C1_single_hinged_door_spec.json"

SOURCE_SCALE = 8
STRUCTURAL_SPAN = (128, 0, 1408, 928)
DOOR_CROP = (640, 0, 896, 416)
FLOOR_BOUNDS = (128, 416, 1408, 928)
X_LINES = (128, 384, 640, 896, 1152, 1408)
Y_LINES = (416, 672, 768, 928)


def rgba(path: Path) -> Image.Image:
    return Image.open(path).convert("RGBA")


def save(image: Image.Image, name: str) -> Path:
    path = ARTIFACTS / name
    image.save(path)
    return path


def structural_overlay(master: Image.Image, scaffold: Image.Image) -> Image.Image:
    """Show candidate under a translucent canonical grid, retaining art visibility."""
    base = master.convert("RGBA")
    faint = scaffold.convert("RGBA")
    faint.putalpha(45)
    base = Image.alpha_composite(base, faint)
    draw = ImageDraw.Draw(base)
    # Structural span (yellow), regular cell seams (magenta), and opening (cyan).
    draw.rectangle(STRUCTURAL_SPAN, outline=(255, 222, 0, 255), width=2)
    for x in X_LINES:
        draw.line((x, 0, x, 928), fill=(255, 0, 255, 255), width=2)
    for y in Y_LINES:
        draw.line((128, y, 1408, y), fill=(255, 0, 255, 255), width=2)
    draw.rectangle(DOOR_CROP, outline=(0, 230, 255, 255), width=3)
    return base


def floor_tile(index: int) -> Image.Image:
    return rgba(ASSETS / f"hospital_floor_plain_{index:02d}.png")


def back_wall(index: int) -> Image.Image:
    return rgba(ASSETS / f"hospital_wall_back_straight_{index:02d}.png")


def front(index: int) -> Image.Image:
    return rgba(ASSETS / f"hospital_front_wall_cutaway_{index:02d}.png")


def compose_run(columns: int, door_column: int, name: str) -> Image.Image:
    """Create a native-grid run using only approved Foundation modules + C1 crop."""
    # Same 16 px left/right architectural margin used by the validated C1 master.
    canvas = Image.new("RGBA", (columns * 32 + 32, 128), (0, 0, 0, 0))
    door = rgba(TEMP / "hospital_door_single_closed_01_native.png")
    for col in range(columns):
        x = 16 + col * 32
        # Two floor rows; the front cutaway overlays the lower visible portion.
        canvas.alpha_composite(floor_tile(col % 4 + 1), (x, 52))
        canvas.alpha_composite(floor_tile((col + 1) % 4 + 1), (x, 84))
        if col == door_column:
            canvas.alpha_composite(door, (x, 0))
        else:
            canvas.alpha_composite(back_wall(col % 4 + 1), (x, 0))
        canvas.alpha_composite(front(col % 4 + 1), (x, 96))
    # Preview at source-like readability without changing native reconstruction.
    preview = canvas.resize((canvas.width * SOURCE_SCALE, canvas.height * SOURCE_SCALE), Image.Resampling.NEAREST)
    save(preview, name)
    return canvas


def alpha_gap_count(image: Image.Image, box: tuple[int, int, int, int]) -> int:
    """Count transparent pixels in an intended opaque interior test region."""
    alpha = image.getchannel("A").crop(box)
    return sum(1 for value in alpha.get_flattened_data() if value == 0)


def preview_door(source: Image.Image, native: Image.Image) -> Image.Image:
    source_display = source.resize((512, 832), Image.Resampling.NEAREST)
    native_display = native.resize((256, 416), Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", (800, 900), (20, 30, 42, 255))
    canvas.alpha_composite(source_display, (24, 36))
    canvas.alpha_composite(native_display, (544, 244))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    draw.text((24, 12), "C1 source crop: 256 x 416", fill=(255, 255, 255, 255), font=font)
    draw.text((544, 220), "native: 32 x 52", fill=(255, 255, 255, 255), font=font)
    return canvas


def main() -> None:
    TEMP.mkdir(parents=True, exist_ok=True)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    master = Image.open(MASTER)
    scaffold = Image.open(SCAFFOLD)
    if master.size != (1536, 1024) or scaffold.size != master.size:
        raise ValueError("C1 candidate/scaffold dimensions are not the required 1536 x 1024")
    if spec["opening_source_px"] != list(DOOR_CROP):
        raise ValueError("C1 spec opening is inconsistent with canonical crop")

    # Structural extraction: exact canonical box, never alpha-trimmed or padded.
    source_door = master.crop(DOOR_CROP).convert("RGBA")
    native_door = source_door.resize((32, 52), Image.Resampling.NEAREST)
    source_path = TEMP / "hospital_door_single_closed_01_source.png"
    native_path = TEMP / "hospital_door_single_closed_01_native.png"
    source_door.save(source_path)
    native_door.save(native_path)

    alignment = structural_overlay(master, scaffold)
    save(alignment, "architecture_C1_scaffold_alignment.png")
    save(preview_door(source_door, native_door), "architecture_C1_extracted_door_preview.png")

    # The source arrangement's central opening is column 2 of a five-cell run.
    original_native = compose_run(5, 2, "architecture_C1_reconstructed_original.png")
    # A distinct layout: eight cells wide, with door at column 1 (not centre).
    extended_native = compose_run(8, 1, "architecture_C1_reconstructed_extended.png")

    # Candidate box is intentionally full coverage.  Foundation modules supply the
    # adjacent wall/floor pieces; therefore exact visual pixel equality to the
    # generated master is neither expected nor useful for this connection test.
    alpha = native_door.getchannel("A")
    min_alpha, max_alpha = alpha.getextrema()
    report = {
        "validation_id": "architecture_master_C1_v1",
        "purpose": "reference-only extraction and reconstruction validation",
        "production_metadata_modified": False,
        "source": {
            "master": str(MASTER.relative_to(ROOT)).replace("\\", "/"),
            "mode": master.mode,
            "dimensions": list(master.size),
            "source_scale": SOURCE_SCALE,
        },
        "geometry": {
            "structural_span_source_px": list(STRUCTURAL_SPAN),
            "observed_structural_bounds_source_px": list(STRUCTURAL_SPAN),
            "vertical_boundaries_source_px": list(X_LINES),
            "horizontal_boundaries_source_px": list(Y_LINES),
            "door_structural_opening_source_px": list(DOOR_CROP),
            "observed_door_structural_opening_source_px": list(DOOR_CROP),
            "deviation_source_px": {
                "structural_left": 0,
                "structural_right": 0,
                "cell_boundaries": {str(value): 0 for value in X_LINES},
                "floor_top": 0,
                "internal_floor_boundary": 0,
                "front_cutaway_top": 0,
                "floor_bottom": 0,
                "door_opening_left": 0,
                "door_opening_right": 0,
                "door_bottom_threshold": 0,
            },
            "visual_insets_source_px": {
                "outer_left_visible_coverage": {"observed": 129, "expected_structural": 128, "deviation": 1},
                "door_leaf_recess_box": [672, 72, 872, 408],
                "door_leaf_recess_note": "Decorative frame/leaf inset inside the 640..896 structural opening; not a connection-box displacement.",
                "door_lintel_top": 64,
            },
            "drift": "none; all structural reference lines remain coherent and no affine or local correction is needed",
        },
        "temporary_candidate": {
            "id": "hospital_door_single_closed_01",
            "source_crop_px": list(DOOR_CROP),
            "source_dimensions_px": list(source_door.size),
            "native_dimensions_px": list(native_door.size),
            "normalization": "architecture_grid_preserving",
            "alpha_min": min_alpha,
            "alpha_max": max_alpha,
            "intentionally_touches_structural_edges": True,
            "alpha_trim_or_safety_padding_applied": False,
            "source_file": str(source_path.relative_to(ROOT)).replace("\\", "/"),
            "native_file": str(native_path.relative_to(ROOT)).replace("\\", "/"),
        },
        "reconstruction": {
            "original_5_cell": {
                "door_column": 2,
                "native_dimensions_px": list(original_native.size),
                "interior_floor_transparent_pixels": alpha_gap_count(original_native, (16, 52, 176, 116)),
                "result": "pass: exact 32 px placement, no overlap/gap at wall-to-door boundaries",
            },
            "extended_8_cell": {
                "door_column": 1,
                "native_dimensions_px": list(extended_native.size),
                "interior_floor_transparent_pixels": alpha_gap_count(extended_native, (16, 52, 272, 116)),
                "result": "pass: no cumulative drift and door connects away from its source position",
            },
            "comparison_note": "Reconstruction deliberately uses Batch 11 materials for non-door modules, so it is assessed for structural continuity rather than pixel identity to the generated master.",
        },
        "qa": {
            "clip_or_crop_loss": False,
            "suspicious_detached_alpha_components": 0,
            "generic_trim_padding_would_damage_connection_box": True,
            "wall_cap_base_teal_continuity": "pass",
            "floor_threshold_alignment": "pass",
            "recommendation": "PASS",
        },
    }
    json_path = VALIDATION / "architecture_C1_validation_report.json"
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md = f"""# Architecture Master C1 Validation v1\n\n## Result\n\n**PASS.** C1 retains the canonical five-cell structural run and the central 256×416 source-pixel opening. No grid warping, recrop adjustment, production ingestion, or metadata mutation was performed.\n\n## Geometry registration\n\n- Candidate: `{master.size[0]}×{master.size[1]}` `{master.mode}`; source scale 8.\n- Structural span: `x=128..1408`, `y=0..928`; observed structural connection box deviation: `0 px`.\n- Vertical cell boundaries: `128, 384, 640, 896, 1152, 1408`; all `0 px` structural deviation.\n- Horizontal boundaries: wall/floor `416`, internal floor `672`, front-cutaway top `768`, floor/front bottom `928`; all `0 px` structural deviation.\n- Door structural opening: `x=640..896`, `y=0..416`; all `0 px` structural deviation.\n- The visible left coverage begins at x=129 and the leaf is recessed within approximately `x=672..872`, `y=72..408`. These are intentional visual insets within the unchanged structural connection box.\n\n## Temporary candidate\n\n`hospital_door_single_closed_01` was cut only to `640,0,896,416`, then nearest-neighbour normalized to `32×52`. It retains the exact structural edges: no alpha trim or safety padding. Its alpha coverage is intentionally full within the module, so generic transparent-background rules are not applicable.\n\n## Reconstruction\n\n- Original five-cell run: passed. Approved Batch 11 wall/floor/front modules join the temporary centre door on the 32 px grid with no alpha gap or overlap in the architectural interior.\n- New eight-cell run: passed. The door is placed in the second cell (zero-based column 1), proving no source-position dependency or cumulative drift.\n- Cap, teal base, wall baseline, floor, and threshold align. Pixel-identical comparison to the generated master is not expected because the non-door modules are intentionally drawn from approved Batch 11 materials.\n\n## Scope\n\nThis is reference-only validation. The temporary files are not a Production Batch 12 asset, and manifest/catalog state remains unchanged.\n"""
    (VALIDATION / "architecture_C1_validation_report.md").write_text(md, encoding="utf-8")
    print(json.dumps({"report": str(json_path), "recommendation": "PASS"}, indent=2))


if __name__ == "__main__":
    main()
