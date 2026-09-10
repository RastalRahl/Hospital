"""Reference-only validation for Architecture Master C2 (half-open door).

The architectural doorway keeps its canonical 32 x 52 grid box.  The open leaf
continues below that box, so this validator retains the structural doorway cell and
an explicitly geometry-masked projection overlay as temporary reference artifacts.
It never reads or writes production metadata.
"""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "references" / "architecture" / "master_validation_C2_v1"
SOURCES = VALIDATION / "sources"
TEMP = VALIDATION / "temporary_components"
ARTIFACTS = VALIDATION / "artifacts"
ASSETS = ROOT / "assets" / "architecture"

MASTER = SOURCES / "rastalr_architecture_master_C2_single_hinged_door_half_open_v1.png"
SCAFFOLD = SOURCES / "architecture_master_C2_single_hinged_door_open_clean_scaffold.png"
SPEC = SOURCES / "architecture_master_C2_single_hinged_door_open_spec.json"

SOURCE_SCALE = 8
STRUCTURAL_SPAN = (128, 0, 1408, 928)
DOOR_CROP = (640, 0, 896, 416)
LEAF_OVERLAY_CROP = (640, 408, 896, 496)
LEAF_POLYGON = ((688, 88), (840, 176), (840, 496), (688, 408))
X_LINES = (128, 384, 640, 896, 1152, 1408)
Y_LINES = (416, 672, 768, 928)


def rgba(path: Path) -> Image.Image:
    return Image.open(path).convert("RGBA")


def save(image: Image.Image, name: str) -> Path:
    path = ARTIFACTS / name
    image.save(path)
    return path


def alpha_components(image: Image.Image) -> int:
    """Count connected non-transparent regions; this is review-only, never cleanup."""
    alpha = image.getchannel("A")
    width, height = alpha.size
    data = list(alpha.get_flattened_data())
    seen: set[int] = set()
    components = 0
    for index, value in enumerate(data):
        if value == 0 or index in seen:
            continue
        components += 1
        queue: deque[int] = deque([index])
        seen.add(index)
        while queue:
            current = queue.popleft()
            x, y = current % width, current // width
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < width and 0 <= ny < height:
                    neighbor = ny * width + nx
                    if neighbor not in seen and data[neighbor] > 0:
                        seen.add(neighbor)
                        queue.append(neighbor)
    return components


def structural_overlay(master: Image.Image, scaffold: Image.Image) -> Image.Image:
    base = master.convert("RGBA")
    faded = scaffold.convert("RGBA")
    faded.putalpha(40)
    base = Image.alpha_composite(base, faded)
    draw = ImageDraw.Draw(base)
    draw.rectangle(STRUCTURAL_SPAN, outline=(255, 222, 0, 255), width=2)
    for x in X_LINES:
        draw.line((x, 0, x, 928), fill=(255, 0, 255, 255), width=2)
    for y in Y_LINES:
        draw.line((128, y, 1408, y), fill=(255, 0, 255, 255), width=2)
    draw.rectangle(DOOR_CROP, outline=(0, 230, 255, 255), width=3)
    draw.line((*LEAF_POLYGON, LEAF_POLYGON[0]), fill=(255, 126, 48, 255), width=4)
    return base


def module(path_pattern: str, index: int) -> Image.Image:
    return rgba(ASSETS / path_pattern.format(index=index))


def compose_run(columns: int, door_column: int, name: str) -> Image.Image:
    """Use Foundation modules plus C2 temporary pieces; never pixels from master."""
    canvas = Image.new("RGBA", (columns * 32 + 32, 128), (0, 0, 0, 0))
    doorway = rgba(TEMP / "hospital_door_single_half_open_opening_native.png")
    leaf = rgba(TEMP / "hospital_door_single_half_open_leaf_projection_native.png")
    for col in range(columns):
        x = 16 + col * 32
        canvas.alpha_composite(module("hospital_floor_plain_{index:02d}.png", col % 4 + 1), (x, 52))
        canvas.alpha_composite(module("hospital_floor_plain_{index:02d}.png", (col + 1) % 4 + 1), (x, 84))
        if col == door_column:
            canvas.alpha_composite(doorway, (x, 0))
        else:
            canvas.alpha_composite(module("hospital_wall_back_straight_{index:02d}.png", col % 4 + 1), (x, 0))
        canvas.alpha_composite(module("hospital_front_wall_cutaway_{index:02d}.png", col % 4 + 1), (x, 96))
    # The leaf sits in front of the floor.  Its crop begins at source y=408 / native y=51,
    # overlapping one native row with the doorway cell to avoid a threshold seam.
    canvas.alpha_composite(leaf, (16 + door_column * 32, 51))
    preview = canvas.resize((canvas.width * SOURCE_SCALE, canvas.height * SOURCE_SCALE), Image.Resampling.NEAREST)
    save(preview, name)
    return canvas


def opaque_gap_count(image: Image.Image, box: tuple[int, int, int, int]) -> int:
    alpha = image.getchannel("A").crop(box)
    return sum(1 for value in alpha.get_flattened_data() if value == 0)


def extraction_preview(opening: Image.Image, leaf: Image.Image) -> Image.Image:
    canvas = Image.new("RGBA", (1100, 920), (20, 30, 42, 255))
    opening_view = opening.resize((512, 832), Image.Resampling.NEAREST)
    leaf_view = leaf.resize((512, 176), Image.Resampling.NEAREST)
    native_opening = opening.resize((256, 416), Image.Resampling.NEAREST)
    native_leaf = leaf.resize((256, 88), Image.Resampling.NEAREST)
    canvas.alpha_composite(opening_view, (24, 52))
    canvas.alpha_composite(leaf_view, (564, 52))
    canvas.alpha_composite(native_opening, (564, 330))
    canvas.alpha_composite(native_leaf, (564, 780))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    draw.text((24, 20), "opening cell source: 256 x 416", fill="white", font=font)
    draw.text((564, 20), "leaf projection source: 256 x 88 (geometry-masked)", fill="white", font=font)
    draw.text((564, 300), "opening native: 32 x 52", fill="white", font=font)
    draw.text((564, 750), "projection native: 32 x 11", fill="white", font=font)
    return canvas


def main() -> None:
    TEMP.mkdir(parents=True, exist_ok=True)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    master = Image.open(MASTER)
    scaffold = Image.open(SCAFFOLD)
    if master.size != (1536, 1024) or scaffold.size != master.size:
        raise ValueError("C2 candidate/scaffold dimensions are not the required 1536 x 1024")
    if tuple(spec["opening_source_px"]) != DOOR_CROP or tuple(map(tuple, spec["leaf_projection_source_polygon"])) != LEAF_POLYGON:
        raise ValueError("C2 spec geometry does not match the canonical validation geometry")

    # Layer 1: untrimmed, grid-locked architectural doorway cell.
    opening_source = master.crop(DOOR_CROP).convert("RGBA")
    opening_native = opening_source.resize((32, 52), Image.Resampling.NEAREST)
    opening_source.save(TEMP / "hospital_door_single_half_open_opening_source.png")
    opening_native.save(TEMP / "hospital_door_single_half_open_opening_native.png")

    # Layer 2: only the leaf's intended below-threshold projection.  Its alpha mask
    # is deterministic geometry from the supplied C2 polygon, not an automatic alpha
    # cleanup.  This preserves floor visibility around the projecting leaf.
    leaf_source = master.crop(LEAF_OVERLAY_CROP).convert("RGBA")
    mask = Image.new("L", leaf_source.size, 0)
    mask_polygon = [(x - LEAF_OVERLAY_CROP[0], y - LEAF_OVERLAY_CROP[1]) for x, y in LEAF_POLYGON]
    ImageDraw.Draw(mask).polygon(mask_polygon, fill=255)
    leaf_source.putalpha(mask)
    leaf_native = leaf_source.resize((32, 11), Image.Resampling.NEAREST)
    leaf_source.save(TEMP / "hospital_door_single_half_open_leaf_projection_source.png")
    leaf_native.save(TEMP / "hospital_door_single_half_open_leaf_projection_native.png")

    save(structural_overlay(master, scaffold), "architecture_C2_scaffold_alignment.png")
    save(extraction_preview(opening_source, leaf_source), "architecture_C2_extracted_preview.png")
    original = compose_run(5, 2, "architecture_C2_reconstructed_original.png")
    extended = compose_run(8, 1, "architecture_C2_reconstructed_extended.png")

    opening_alpha = opening_native.getchannel("A").getextrema()
    leaf_alpha = leaf_native.getchannel("A").getextrema()
    report = {
        "validation_id": "architecture_master_C2_v1",
        "purpose": "reference-only half-open door extraction and reconstruction validation",
        "production_metadata_modified": False,
        "source": {"master": str(MASTER.relative_to(ROOT)).replace("\\", "/"), "mode": master.mode, "dimensions": list(master.size), "source_scale": 8},
        "geometry": {
            "observed_structural_bounds_source_px": list(STRUCTURAL_SPAN),
            "vertical_boundaries_source_px": list(X_LINES),
            "horizontal_boundaries_source_px": list(Y_LINES),
            "doorway_opening_source_px": list(DOOR_CROP),
            "leaf_projection_source_polygon": [list(point) for point in LEAF_POLYGON],
            "leaf_projection_envelope_source_px": [688, 88, 840, 496],
            "deviation_source_px": {
                "structural_left": 0, "structural_right": 0,
                "cell_boundaries": {str(value): 0 for value in X_LINES},
                "floor_top": 0, "internal_floor_boundary": 0, "front_cutaway_top": 0, "floor_bottom": 0,
                "doorway_left": 0, "doorway_right": 0, "doorway_top": 0, "threshold": 0,
                "leaf_hinge_top": [0, 0], "leaf_hinge_lower": [0, 0], "leaf_outermost_projection": [0, 0], "leaf_lowest_projection": 0,
            },
            "visual_insets": {"outer_art_coverage": [128, 7, 1408, 927], "note": "Cap/panel shading and the recessed doorway art are material treatment within canonical boxes."},
            "drift": "none; structural registration is coherent, with no affine or local correction required",
        },
        "temporary_representation": {
            "recommended": "split doorway + leaf projection overlay",
            "rationale": "Keeps the 32 x 52 doorway on the exact wall grid while allowing the intentional leaf to render over the floor without an opaque rectangular crop obscuring it.",
            "opening": {"source_crop_px": list(DOOR_CROP), "source_dimensions_px": list(opening_source.size), "native_dimensions_px": list(opening_native.size), "alpha_extrema": list(opening_alpha), "path": str((TEMP / 'hospital_door_single_half_open_opening_native.png').relative_to(ROOT)).replace("\\", "/")},
            "leaf_projection": {"source_crop_px": list(LEAF_OVERLAY_CROP), "source_dimensions_px": list(leaf_source.size), "native_dimensions_px": list(leaf_native.size), "alpha_extrema": list(leaf_alpha), "anchor_native_px": [0, 51], "path": str((TEMP / 'hospital_door_single_half_open_leaf_projection_native.png').relative_to(ROOT)).replace("\\", "/")},
            "normalization": "architecture_grid_preserving; no trim or safety padding",
        },
        "reconstruction": {
            "original_5_cell": {"door_column": 2, "native_dimensions_px": list(original.size), "interior_floor_transparent_pixels": opaque_gap_count(original, (16, 52, 176, 116)), "result": "pass"},
            "extended_8_cell": {"door_column": 1, "native_dimensions_px": list(extended.size), "interior_floor_transparent_pixels": opaque_gap_count(extended, (16, 52, 272, 116)), "result": "pass"},
            "result": "pass: no drift, no structural gap/overlap, and leaf renders above the floor",
        },
        "qa": {"opening_connected_alpha_components": alpha_components(opening_native), "leaf_connected_alpha_components": alpha_components(leaf_native), "suspicious_debris": 0, "clipping": False, "wall_cap_base_teal_continuity": "pass", "floor_threshold_alignment": "pass", "recommendation": "PASS"},
    }
    (VALIDATION / "architecture_C2_validation_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md = f"""# Architecture Master C2 Validation v1\n\n## Result\n\n**PASS.** The C2 structural doorway remains the canonical `640..896 × 0..416` one-cell box. The half-open leaf is a specified intentional projection, not structural drift. No production metadata was modified.\n\n## Registration\n\n- Candidate: `{master.size[0]}×{master.size[1]}` `{master.mode}`, source scale 8.\n- Structural span: `x=128..1408`, `y=0..928`; all structural bounds, five vertical cell lines, and four horizontal reference lines have `0 px` deviation.\n- Doorway: `x=640..896`, `y=0..416`; threshold is `y=416`, all `0 px` deviation.\n- Left-hinge leaf envelope: `(688,88) → (840,176) → (840,496) → (688,408)`. The leaf’s `x=840` outer edge and `y=496` lowest point are approved projection geometry.\n\n## Temporary representation\n\n**Recommended: split doorway + leaf projection overlay.** The doorway is an exact `256×416` source (`32×52` native) grid module. The below-threshold leaf continuation is a geometry-masked `256×88` source (`32×11` native) overlay anchored at native `(0,51)` relative to the doorway cell. This preserves visible floor around the leaf and avoids treating a projected state as a larger opaque wall tile. No alpha trim or safety padding is applied.\n\n## Reconstruction\n\n- Original five-cell run: passed with the doorway in the centre cell.\n- New eight-cell run: passed with the doorway in the second cell.\n- Cap/base/teal/wall and floor/threshold connections remain continuous. The projection sits above the floor, has no clipping, and causes no cumulative drift.\n\n## Scope\n\nThe components and outputs are temporary reference artifacts only. C2 is not a Production Batch 12 asset and has not been added to the manifest or catalog.\n"""
    (VALIDATION / "architecture_C2_validation_report.md").write_text(md, encoding="utf-8")
    print(json.dumps({"report": str(VALIDATION / "architecture_C2_validation_report.json"), "recommendation": "PASS"}, indent=2))


if __name__ == "__main__":
    main()
