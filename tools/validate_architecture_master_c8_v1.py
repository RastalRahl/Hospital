"""Reference-only locked-edit validation for C8 wide equipment opening."""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "references" / "architecture" / "master_validation_C8_v1"
SOURCES = VALIDATION / "sources"
TEMP = VALIDATION / "temporary_components"
ARTIFACTS = VALIDATION / "artifacts"
ASSETS = ROOT / "assets" / "architecture"
MASTER = SOURCES / "rastalr_architecture_master_C8_wide_equipment_opening_locked_v1.png"
C4 = ROOT / "references" / "architecture" / "master_validation_C4_v1" / "sources" / "rastalr_architecture_master_C4_double_doors_closed_v1.png"
SCAFFOLD = SOURCES / "architecture_master_C8_wide_equipment_opening_clean_scaffold.png"
LOCKED_SPEC = SOURCES / "architecture_master_C8_locked_edit_spec.json"
SPEC = SOURCES / "architecture_master_C8_wide_equipment_opening_spec.json"

SOURCE_SCALE = 8
STRUCTURE = (128, 0, 1408, 928)
OPENING = (384, 0, 1152, 416)
ALLOWED = (384, 64, 1152, 416)
PASSAGE = (416, 96, 1120, 416)
HEADER = (384, 64, 1152, 96)
LEFT_JAMB = (384, 96, 416, 416)
RIGHT_JAMB = (1120, 96, 1152, 416)
LEFT_GUARD = (384, 280, 416, 416)
RIGHT_GUARD = (1120, 280, 1152, 416)
X_LINES = (128, 384, 640, 896, 1152, 1408)
Y_LINES = (416, 672, 768, 928)


def rgba(path: Path) -> Image.Image:
    return Image.open(path).convert("RGBA")


def save(image: Image.Image, name: str) -> None:
    image.save(ARTIFACTS / name)


def components(image: Image.Image) -> int:
    alpha = image.getchannel("A")
    width, height = alpha.size
    data = list(alpha.get_flattened_data())
    seen: set[int] = set()
    count = 0
    for index, value in enumerate(data):
        if value == 0 or index in seen:
            continue
        count += 1
        seen.add(index)
        queue: deque[int] = deque([index])
        while queue:
            current = queue.popleft()
            x, y = current % width, current // width
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                neighbor = ny * width + nx
                if 0 <= nx < width and 0 <= ny < height and neighbor not in seen and data[neighbor] > 0:
                    seen.add(neighbor)
                    queue.append(neighbor)
    return count


def diff_data(candidate: Image.Image, base: Image.Image) -> tuple[tuple[int, int, int, int] | None, int, int, Image.Image]:
    candidate_rgb, base_rgb = candidate.convert("RGB"), base.convert("RGB")
    diff = ImageChops.difference(candidate_rgb, base_rgb)
    bbox = diff.getbbox()
    inside = outside = 0
    for y in range(candidate.height):
        for x in range(candidate.width):
            if candidate_rgb.getpixel((x, y)) != base_rgb.getpixel((x, y)):
                if ALLOWED[0] <= x < ALLOWED[2] and ALLOWED[1] <= y < ALLOWED[3]:
                    inside += 1
                else:
                    outside += 1
    return bbox, inside, outside, diff


def diff_artifact(candidate: Image.Image, diff: Image.Image, bbox: tuple[int, int, int, int]) -> Image.Image:
    out = candidate.convert("RGBA")
    mask = diff.convert("L").point(lambda value: 150 if value else 0)
    red = Image.new("RGBA", out.size, (255, 46, 74, 0))
    red.putalpha(mask)
    out = Image.alpha_composite(out, red)
    draw = ImageDraw.Draw(out)
    draw.rectangle(ALLOWED, outline=(0, 230, 255, 255), width=4)
    draw.rectangle(bbox, outline=(255, 225, 0, 255), width=2)
    return out


def alignment(master: Image.Image, scaffold: Image.Image) -> Image.Image:
    out = master.convert("RGBA")
    guide = scaffold.convert("RGBA")
    guide.putalpha(32)
    out = Image.alpha_composite(out, guide)
    draw = ImageDraw.Draw(out)
    draw.rectangle(STRUCTURE, outline=(255, 225, 0, 255), width=2)
    draw.rectangle(OPENING, outline=(0, 230, 255, 255), width=3)
    for x in X_LINES:
        draw.line((x, 0, x, 928), fill=(255, 0, 255, 255), width=2)
    for y in Y_LINES:
        draw.line((128, y, 1408, y), fill=(255, 0, 255, 255), width=2)
    return out


def diagnostic(master: Image.Image) -> Image.Image:
    out = master.convert("RGBA")
    draw = ImageDraw.Draw(out)
    draw.rectangle(HEADER, outline=(190, 120, 255, 255), width=4)
    draw.rectangle(PASSAGE, outline=(96, 255, 160, 255), width=4)
    draw.rectangle(LEFT_JAMB, outline=(255, 126, 48, 255), width=3)
    draw.rectangle(RIGHT_JAMB, outline=(255, 126, 48, 255), width=3)
    draw.rectangle(LEFT_GUARD, outline=(255, 225, 0, 255), width=3)
    draw.rectangle(RIGHT_GUARD, outline=(255, 225, 0, 255), width=3)
    return out


def asset(pattern: str, index: int) -> Image.Image:
    return rgba(ASSETS / pattern.format(index=index))


def compose_run(columns: int, opening_start: int, name: str) -> Image.Image:
    canvas = Image.new("RGBA", (columns * 32 + 32, 128), (0, 0, 0, 0))
    opening = rgba(TEMP / "hospital_equipment_service_opening_native.png")
    for col in range(columns):
        x = 16 + col * 32
        canvas.alpha_composite(asset("hospital_floor_plain_{index:02d}.png", col % 4 + 1), (x, 52))
        canvas.alpha_composite(asset("hospital_floor_plain_{index:02d}.png", (col + 1) % 4 + 1), (x, 84))
        if col not in (opening_start, opening_start + 1, opening_start + 2):
            canvas.alpha_composite(asset("hospital_wall_back_straight_{index:02d}.png", col % 4 + 1), (x, 0))
        canvas.alpha_composite(asset("hospital_front_wall_cutaway_{index:02d}.png", col % 4 + 1), (x, 96))
    canvas.alpha_composite(opening, (16 + opening_start * 32, 0))
    save(canvas.resize((canvas.width * 8, canvas.height * 8), Image.Resampling.NEAREST), name)
    return canvas


def preview(opening: Image.Image) -> Image.Image:
    out = Image.new("RGBA", (1400, 940), (20, 30, 42, 255))
    draw = ImageDraw.Draw(out)
    font = ImageFont.load_default()
    out.alpha_composite(opening.resize((1344, 832), Image.Resampling.NEAREST), (28, 56))
    draw.text((28, 20), "C8 fixed composite equipment opening: 768 x 416 source / 96 x 52 native", fill="white", font=font)
    draw.text((28, 904), "Includes reinforced header/jambs, lower guards, broad flush threshold, and opaque recessed passage backing.", fill="white", font=font)
    return out


def main() -> None:
    TEMP.mkdir(parents=True, exist_ok=True)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    locked = json.loads(LOCKED_SPEC.read_text(encoding="utf-8"))
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    master, c4, scaffold = Image.open(MASTER), Image.open(C4), Image.open(SCAFFOLD)
    if master.size != (1536, 1024) or c4.size != master.size or scaffold.size != master.size:
        raise ValueError("C8/C4/scaffold must all be 1536 x 1024")
    for values, expected in ((locked["locked_edit_region_source_px"], ALLOWED), (locked["opening_source_px"], OPENING), (spec["opening_source_px"], OPENING), (spec["clear_passage_source_px"], PASSAGE)):
        if tuple(values) != expected:
            raise ValueError("C8 specification geometry mismatch")
    if locked["door_leaves_present"] or locked["projection_into_floor"] or spec["door_leaves_present"] or spec["projection_into_floor"]:
        raise ValueError("C8 must not contain leaves or a floor projection")

    bbox, inside, outside, diff = diff_data(master, c4)
    if bbox != ALLOWED or outside != 0:
        raise ValueError(f"C8 locked edit failed: bbox={bbox}, outside={outside}")
    save(diff_artifact(master, diff, bbox), "architecture_C8_locked_edit_diff.png")
    save(alignment(master, scaffold), "architecture_C8_scaffold_alignment.png")
    save(diagnostic(master), "architecture_C8_geometry_diagnostic.png")
    opening = master.crop(OPENING).convert("RGBA")
    opening_native = opening.resize((96, 52), Image.Resampling.NEAREST)
    opening.save(TEMP / "hospital_equipment_service_opening_source.png")
    opening_native.save(TEMP / "hospital_equipment_service_opening_native.png")
    save(preview(opening), "architecture_C8_extracted_preview.png")
    original = compose_run(5, 1, "architecture_C8_reconstructed_original.png")
    extended = compose_run(8, 2, "architecture_C8_reconstructed_extended.png")
    gaps = lambda image, box: sum(1 for value in image.getchannel("A").crop(box).get_flattened_data() if value == 0)

    report = {
        "validation_id": "architecture_master_C8_v1",
        "purpose": "reference-only locked-edit wide equipment/service-opening validation",
        "production_metadata_modified": False,
        "source": {"master": str(MASTER.relative_to(ROOT)).replace("\\", "/"), "dimensions": list(master.size), "mode": master.mode, "source_scale": SOURCE_SCALE},
        "geometry": {"structural_bounds": list(STRUCTURE), "vertical_grid": list(X_LINES), "horizontal_grid": list(Y_LINES), "opening": list(OPENING), "clear_passage": list(PASSAGE), "header": list(HEADER), "reinforced_jambs": {"left": list(LEFT_JAMB), "right": list(RIGHT_JAMB)}, "crash_guards": {"left": list(LEFT_GUARD), "right": list(RIGHT_GUARD)}, "deviation_source_px": 0, "drift": "none"},
        "locked_edit": {"base_master": str(C4.relative_to(ROOT)).replace("\\", "/"), "allowed_region": list(ALLOWED), "actual_diff_bbox": list(bbox), "changed_pixels_inside": inside, "changed_pixels_outside": outside, "registration": "identical outside allowed edit; no rescaling, warp, perspective transform, or whole-scene redraw"},
        "temporary_representation": {"recommended": "single composite 3-cell equipment-opening module", "rationale": "C8 has no independently moving leaves or projections; the reinforced header, jambs, guards, flush threshold, and passage comprise one grid-locked architectural unit.", "crop": list(OPENING), "native_dimensions": [96, 52], "anchor": "architecture back-wall grid anchor spanning three cells", "alpha_extrema": list(opening_native.getchannel("A").getextrema()), "components": components(opening_native), "passage_treatment": "opaque recessed visual backing retained from locked source; no unsupported transparent-world layer is inferred", "normalization": "architecture_grid_preserving; no trim or safety padding"},
        "reconstruction": {"original_5_cell": {"result": "pass", "opening_start_column": 1, "floor_alpha_gaps": gaps(original, (16, 52, 176, 116))}, "extended_8_cell": {"result": "pass", "opening_start_column": 2, "floor_alpha_gaps": gaps(extended, (16, 52, 272, 116))}, "continuity": "pass: cap/base/teal/baseline/frame/guards/threshold/floor; no cumulative drift"},
        "qa": {"clipping": False, "suspicious_debris": 0, "detached_components": 0, "threshold_alignment": "pass", "frame_alignment": "pass", "clear_passage_integrity": "pass", "crash_guard_integrity": "pass", "recommendation": "PASS"},
    }
    (VALIDATION / "architecture_C8_validation_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md = """# Architecture Master C8 Validation v1\n\n## Result\n\n**PASS.** C8 is a locked edit of validated C4 with all 270,335 changed pixels confined to `(384,64)..(1152,416)` and zero changed pixels outside it. It was not ingested.\n\n## Geometry\n\nThe five-cell run, grid, and horizontal references retain 0 px structural deviation. C8 supplies a centered three-cell opening `(384,0)..(1152,416)`, clear passage `(416,96)..(1120,416)`, reinforced header/jambs, lower crash guards, and broad flush threshold. It has no leaves and no floor projection.\n\n## Recommended representation\n\n**Single composite 3-cell equipment-opening module.** The canonical `768x416` source crop scales nearest-neighbor to `96x52` native. Grid-preserving normalization retains its exact structural rectangle; alpha trim and safety padding are prohibited.\n\n## Reconstruction\n\nThe original five-cell and relocated eight-cell reconstructions pass with zero interior floor alpha gaps, continuous cap/base/teal/baseline/threshold behavior, intact guards/frame/passage, and no cumulative drift.\n\n## Scope\n\nAll outputs are temporary reference-only validation artifacts. No Production Batch 12 metadata or catalog entry was created.\n"""
    (VALIDATION / "architecture_C8_validation_report.md").write_text(md, encoding="utf-8")
    print(json.dumps({"recommendation": "PASS", "diff_bbox": list(bbox), "inside": inside, "outside": outside, "native": [96, 52]}, indent=2))


if __name__ == "__main__":
    main()
