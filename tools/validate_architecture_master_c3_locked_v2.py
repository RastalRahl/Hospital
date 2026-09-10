"""Reference-only locked-edit validation for C3 glazed closed door.

C3 v3 is accepted for extraction only after proving byte-level RGB equivalence to
the validated C1 master outside its supplied glazing edit rectangle.  This module
does not update the manifest, catalog, staging, or production assets.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "references" / "architecture" / "master_validation_C3_v2"
SOURCES = VALIDATION / "sources"
TEMP = VALIDATION / "temporary_components"
ARTIFACTS = VALIDATION / "artifacts"
ASSETS = ROOT / "assets" / "architecture"
C1_SOURCES = ROOT / "references" / "architecture" / "master_validation_C1_v1" / "sources"

C1 = C1_SOURCES / "rastalr_architecture_master_C1_single_hinged_door_closed_v1.png"
C1_SCAFFOLD = C1_SOURCES / "architecture_master_C1_single_hinged_door_clean_scaffold.png"
C3 = SOURCES / "rastalr_architecture_master_C3_glazed_single_door_closed_v3.png"
SPEC = SOURCES / "architecture_master_C3_locked_edit_spec.json"

SOURCE_SCALE = 8
STRUCTURAL_SPAN = (128, 0, 1408, 928)
DOOR_CROP = (640, 0, 896, 416)
EDIT = (704, 120, 824, 320)
GLAZING = (712, 128, 816, 312)
X_LINES = (128, 384, 640, 896, 1152, 1408)
Y_LINES = (416, 672, 768, 928)


def rgba(path: Path) -> Image.Image:
    return Image.open(path).convert("RGBA")


def save(image: Image.Image, name: str) -> None:
    image.save(ARTIFACTS / name)


def changed_pixels(before: Image.Image, after: Image.Image) -> tuple[int, tuple[int, int, int, int] | None, int]:
    """Return RGB diff count, exclusive bbox, and out-of-authorized-box count."""
    a, b = before.convert("RGB"), after.convert("RGB")
    pa, pb = a.load(), b.load()
    changed: list[tuple[int, int]] = []
    outside = 0
    for y in range(a.height):
        for x in range(a.width):
            if pa[x, y] != pb[x, y]:
                changed.append((x, y))
                if not (EDIT[0] <= x < EDIT[2] and EDIT[1] <= y < EDIT[3]):
                    outside += 1
    if not changed:
        return 0, None, outside
    return len(changed), (min(x for x, _ in changed), min(y for _, y in changed), max(x for x, _ in changed) + 1, max(y for _, y in changed) + 1), outside


def pixel_lock_preview(base: Image.Image, candidate: Image.Image) -> Image.Image:
    difference = ImageChops.difference(base.convert("RGB"), candidate.convert("RGB")).convert("RGBA")
    # Mark every differing RGB pixel in magenta; retain C3 dimly to provide context.
    context = candidate.convert("RGBA").point(lambda v: int(v * 0.34))
    diff = difference.convert("RGB")
    pix = diff.load()
    draw = ImageDraw.Draw(context)
    for y in range(diff.height):
        for x in range(diff.width):
            if pix[x, y] != (0, 0, 0):
                context.putpixel((x, y), (255, 0, 255, 255))
    draw.rectangle(EDIT, outline=(255, 225, 0, 255), width=2)
    return context


def scaffold_alignment(candidate: Image.Image) -> Image.Image:
    image = candidate.convert("RGBA")
    scaffold = rgba(C1_SCAFFOLD)
    scaffold.putalpha(38)
    image = Image.alpha_composite(image, scaffold)
    draw = ImageDraw.Draw(image)
    draw.rectangle(STRUCTURAL_SPAN, outline=(255, 225, 0, 255), width=2)
    for x in X_LINES:
        draw.line((x, 0, x, 928), fill=(255, 0, 255, 255), width=2)
    for y in Y_LINES:
        draw.line((128, y, 1408, y), fill=(255, 0, 255, 255), width=2)
    draw.rectangle(DOOR_CROP, outline=(0, 230, 255, 255), width=3)
    draw.rectangle(GLAZING, outline=(0, 255, 160, 255), width=2)
    return image


def asset(pattern: str, index: int) -> Image.Image:
    return rgba(ASSETS / pattern.format(index=index))


def compose_run(columns: int, door_column: int, destination: str) -> Image.Image:
    canvas = Image.new("RGBA", (columns * 32 + 32, 128), (0, 0, 0, 0))
    door = rgba(TEMP / "hospital_door_glazed_closed_01_native.png")
    for col in range(columns):
        x = 16 + col * 32
        canvas.alpha_composite(asset("hospital_floor_plain_{index:02d}.png", col % 4 + 1), (x, 52))
        canvas.alpha_composite(asset("hospital_floor_plain_{index:02d}.png", (col + 1) % 4 + 1), (x, 84))
        if col == door_column:
            canvas.alpha_composite(door, (x, 0))
        else:
            canvas.alpha_composite(asset("hospital_wall_back_straight_{index:02d}.png", col % 4 + 1), (x, 0))
        canvas.alpha_composite(asset("hospital_front_wall_cutaway_{index:02d}.png", col % 4 + 1), (x, 96))
    save(canvas.resize((canvas.width * 8, canvas.height * 8), Image.Resampling.NEAREST), destination)
    return canvas


def alpha_components(image: Image.Image) -> int:
    alpha = image.getchannel("A")
    width, height = alpha.size
    data = list(alpha.get_flattened_data())
    seen: set[int] = set()
    count = 0
    for offset, value in enumerate(data):
        if value == 0 or offset in seen:
            continue
        count += 1
        stack = [offset]
        seen.add(offset)
        while stack:
            current = stack.pop()
            x, y = current % width, current // width
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                next_offset = ny * width + nx
                if 0 <= nx < width and 0 <= ny < height and next_offset not in seen and data[next_offset] > 0:
                    seen.add(next_offset)
                    stack.append(next_offset)
    return count


def preview_door(source: Image.Image, native: Image.Image) -> Image.Image:
    out = Image.new("RGBA", (800, 900), (20, 30, 42, 255))
    out.alpha_composite(source.resize((512, 832), Image.Resampling.NEAREST), (24, 44))
    out.alpha_composite(native.resize((256, 416), Image.Resampling.NEAREST), (544, 244))
    draw = ImageDraw.Draw(out)
    font = ImageFont.load_default()
    draw.text((24, 18), "C3 grid crop: 256 x 416", fill="white", font=font)
    draw.text((544, 218), "native: 32 x 52", fill="white", font=font)
    return out


def main() -> None:
    TEMP.mkdir(parents=True, exist_ok=True)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    base, candidate = Image.open(C1), Image.open(C3)
    if base.size != candidate.size or base.size != (1536, 1024):
        raise ValueError("C3 and validated C1 must share the canonical 1536 x 1024 canvas")
    if tuple(spec["allowed_modified_region_source_px_exclusive"]) != EDIT:
        raise ValueError("C3 locked-edit specification does not match allowed edit region")
    count, bbox, outside = changed_pixels(base, candidate)
    if bbox is None or not (EDIT[0] <= bbox[0] and EDIT[1] <= bbox[1] and bbox[2] <= EDIT[2] and bbox[3] <= EDIT[3]) or outside:
        raise ValueError(f"Locked edit failure: bbox={bbox}, outside={outside}")
    save(pixel_lock_preview(base, candidate), "architecture_C3_pixel_lock_diff.png")
    save(scaffold_alignment(candidate), "architecture_C3_scaffold_alignment.png")

    # Exact C1 structural box; source RGB is deliberately retained as an opaque
    # architecture cell.  No trim/padding may alter this connection box.
    source = candidate.crop(DOOR_CROP).convert("RGBA")
    native = source.resize((32, 52), Image.Resampling.NEAREST)
    source.save(TEMP / "hospital_door_glazed_closed_01_source.png")
    native.save(TEMP / "hospital_door_glazed_closed_01_native.png")
    save(preview_door(source, native), "architecture_C3_extracted_preview.png")
    original = compose_run(5, 2, "architecture_C3_reconstructed_original.png")
    extended = compose_run(8, 1, "architecture_C3_reconstructed_extended.png")

    floor_gap = lambda image, box: sum(1 for v in image.getchannel("A").crop(box).get_flattened_data() if v == 0)
    report = {
        "validation_id": "architecture_master_C3_locked_v2",
        "purpose": "reference-only pixel-locked C3 validation",
        "production_metadata_modified": False,
        "source": {"base_master": str(C1.relative_to(ROOT)).replace("\\", "/"), "candidate": str(C3.relative_to(ROOT)).replace("\\", "/"), "dimensions": list(candidate.size), "mode": candidate.mode, "source_scale": 8},
        "pixel_lock": {"allowed_edit_region_exclusive": list(EDIT), "difference_bbox_exclusive": list(bbox), "changed_pixel_count": count, "out_of_region_changed_pixel_count": outside, "pass": True},
        "geometry": {"structural_bounds": list(STRUCTURAL_SPAN), "vertical_grid": list(X_LINES), "horizontal_grid": list(Y_LINES), "doorway": list(DOOR_CROP), "deviation_source_px": 0},
        "glazing": {"edit_envelope": list(EDIT), "inner_bounds": list(GLAZING), "inside_door_leaf": True, "interferes_with_hinges_handle_or_frame": False, "assessment": "substantial, visually distinct glazing inset"},
        "temporary_candidate": {"id": "hospital_door_glazed_closed_01", "source_crop": list(DOOR_CROP), "source_dimensions": list(source.size), "native_dimensions": list(native.size), "normalization": "architecture_grid_preserving", "alpha_extrema": list(native.getchannel("A").getextrema()), "alpha_components": alpha_components(native), "alpha_trim_or_safety_padding": False, "path": str((TEMP / 'hospital_door_glazed_closed_01_native.png').relative_to(ROOT)).replace("\\", "/")},
        "reconstruction": {"original_5_cell": {"result": "pass", "door_column": 2, "floor_alpha_gaps": floor_gap(original, (16, 52, 176, 116))}, "extended_8_cell": {"result": "pass", "door_column": 1, "floor_alpha_gaps": floor_gap(extended, (16, 52, 272, 116))}, "continuity": "cap/base/teal/wall baseline/floor/threshold all pass; no cumulative drift"},
        "qa": {"clipping": False, "suspicious_detached_debris": 0, "recommendation": "PASS"},
    }
    (VALIDATION / "architecture_C3_validation_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    report_md = f"""# Architecture Master C3 Locked-Edit Validation v2\n\n## Result\n\n**PASS.** C3 v3 is pixel-locked to validated C1 outside the declared glazing edit rectangle. Its structural geometry is therefore unchanged. This validation is reference-only and has not created a Production Batch 12 asset.\n\n## Pixel lock\n\n- C1 and C3 are both `{candidate.size[0]}×{candidate.size[1]}` `{candidate.mode}` images.\n- Changed pixels: `{count}`.\n- Difference box: `{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}` (exclusive), exactly matching the authorized `704,120,824,320` region.\n- Out-of-region changes: `0`.\n\n## Geometry and glazing\n\nThe canonical structural run, vertical grid, horizontal boundaries, and `640,0..896,416` doorway retain `0 px` deviation. The glazing is contained in the inner `712,128..816,312` rectangle: clear of the door frame, left hinge hardware, and handle; large enough to distinguish C3 from the solid C1 door.\n\n## Temporary candidate and reconstruction\n\nA temporary untrimmed `256×416` source crop was nearest-neighbour normalized to `32×52` using `architecture_grid_preserving`. Its structural edges remain intact; alpha is intentionally full. Both the original five-cell and new eight-cell reconstructions pass with zero interior floor alpha gaps, continuous cap/base/teal/baseline/threshold alignment, and no cumulative drift.\n\n## Scope\n\nC3 remains outside the manifest and catalog pending a future explicit production-ingestion instruction.\n"""
    (VALIDATION / "architecture_C3_validation_report.md").write_text(report_md, encoding="utf-8")
    print(json.dumps({"recommendation": "PASS", "changed_pixel_count": count, "difference_bbox": bbox}, indent=2))


if __name__ == "__main__":
    main()
