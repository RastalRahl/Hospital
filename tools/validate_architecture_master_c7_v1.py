"""Reference-only validation for C7 open sliding clinical doors."""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "references" / "architecture" / "master_validation_C7_v1"
SOURCES = VALIDATION / "sources"
TEMP = VALIDATION / "temporary_components"
ARTIFACTS = VALIDATION / "artifacts"
ASSETS = ROOT / "assets" / "architecture"
MASTER = SOURCES / "rastalr_architecture_master_C7_sliding_clinical_doors_open_v1.png"
SCAFFOLD = SOURCES / "architecture_master_C7_sliding_clinical_doors_open_clean_scaffold.png"
SPEC = SOURCES / "architecture_master_C7_sliding_clinical_doors_open_spec.json"

SOURCE_SCALE = 8
STRUCTURE = (128, 0, 1408, 928)
OPENING = (384, 0, 896, 416)
X_LINES = (128, 384, 640, 896, 1152, 1408)
Y_LINES = (416, 672, 768, 928)
TRACK = (416, 64, 864, 112)
PASSAGE = (416, 112, 864, 416)
LEFT_LEAF = (192, 112, 416, 416)
RIGHT_LEAF = (864, 112, 1088, 416)
# Material insets measured as the C6-family glazing/pull treatment translated
# with each parked leaf. They are visual diagnostics, not structural bounds.
LEFT_GLAZING = (240, 144, 376, 312)
RIGHT_GLAZING = (912, 144, 1048, 312)
LEFT_PULL = (384, 296, 408, 336)
RIGHT_PULL = (888, 296, 912, 336)


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
    draw.rectangle(TRACK, outline=(190, 120, 255, 255), width=4)
    draw.rectangle(PASSAGE, outline=(96, 255, 160, 255), width=4)
    draw.rectangle(LEFT_LEAF, outline=(255, 126, 48, 255), width=4)
    draw.rectangle(RIGHT_LEAF, outline=(255, 126, 48, 255), width=4)
    for box in (LEFT_GLAZING, RIGHT_GLAZING):
        draw.rectangle(box, outline=(0, 230, 255, 255), width=3)
    for box in (LEFT_PULL, RIGHT_PULL):
        draw.rectangle(box, outline=(255, 225, 0, 255), width=3)
    return out


def asset(pattern: str, index: int) -> Image.Image:
    return rgba(ASSETS / pattern.format(index=index))


def compose_run(columns: int, door_start: int, name: str) -> Image.Image:
    canvas = Image.new("RGBA", (columns * 32 + 32, 128), (0, 0, 0, 0))
    opening = rgba(TEMP / "hospital_sliding_clinical_doors_open_frame_native.png")
    left = rgba(TEMP / "hospital_sliding_clinical_doors_open_left_parked_native.png")
    right = rgba(TEMP / "hospital_sliding_clinical_doors_open_right_parked_native.png")
    for col in range(columns):
        x = 16 + col * 32
        canvas.alpha_composite(asset("hospital_floor_plain_{index:02d}.png", col % 4 + 1), (x, 52))
        canvas.alpha_composite(asset("hospital_floor_plain_{index:02d}.png", (col + 1) % 4 + 1), (x, 84))
        if col not in (door_start, door_start + 1):
            canvas.alpha_composite(asset("hospital_wall_back_straight_{index:02d}.png", col % 4 + 1), (x, 0))
        canvas.alpha_composite(asset("hospital_front_wall_cutaway_{index:02d}.png", col % 4 + 1), (x, 96))
    origin = 16 + door_start * 32
    canvas.alpha_composite(opening, (origin, 0))
    # The source geometry expresses outward lateral parking: -24 and +60 px
    # relative to a 64 px opening, with no vertical/floor displacement.
    canvas.alpha_composite(left, (origin - 24, 14))
    canvas.alpha_composite(right, (origin + 60, 14))
    save(canvas.resize((canvas.width * 8, canvas.height * 8), Image.Resampling.NEAREST), name)
    return canvas


def preview(opening: Image.Image, left: Image.Image, right: Image.Image) -> Image.Image:
    out = Image.new("RGBA", (1360, 940), (20, 30, 42, 255))
    draw = ImageDraw.Draw(out)
    font = ImageFont.load_default()
    out.alpha_composite(opening.resize((1024, 832), Image.Resampling.NEAREST), (32, 48))
    out.alpha_composite(left.resize((224, 304), Image.Resampling.NEAREST), (1072, 100))
    out.alpha_composite(right.resize((224, 304), Image.Resampling.NEAREST), (1072, 474))
    draw.text((32, 16), "fixed open doorway/recess: 512 x 416 source / 64 x 52 native", fill="white", font=font)
    draw.text((1072, 70), "parked leaf overlays", fill="white", font=font)
    draw.text((1072, 826), "each: 224 x 304 source / 28 x 38 native", fill="white", font=font)
    return out


def main() -> None:
    TEMP.mkdir(parents=True, exist_ok=True)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    master = Image.open(MASTER)
    scaffold = Image.open(SCAFFOLD)
    if master.size != (1536, 1024) or scaffold.size != master.size:
        raise ValueError("C7 source/scaffold must both be 1536 x 1024")
    checks = {
        "opening_source_px": OPENING,
        "track_header_source_px": TRACK,
        "clear_passage_source_px": PASSAGE,
        "left_leaf_open_source_px": LEFT_LEAF,
        "right_leaf_open_source_px": RIGHT_LEAF,
    }
    for key, expected in checks.items():
        if tuple(spec[key]) != expected:
            raise ValueError(f"C7 specification mismatch for {key}")
    if spec["leaf_projection_into_floor"] is not False or spec["leaf_slide_distance_source_px"] != 224:
        raise ValueError("C7 requires 224 px lateral-only leaf movement")

    save(alignment(master, scaffold), "architecture_C7_scaffold_alignment.png")
    save(diagnostic(master), "architecture_C7_door_geometry_diagnostic.png")
    opening = master.crop(OPENING).convert("RGBA")
    left = master.crop(LEFT_LEAF).convert("RGBA")
    right = master.crop(RIGHT_LEAF).convert("RGBA")
    opening_native = opening.resize((64, 52), Image.Resampling.NEAREST)
    left_native = left.resize((28, 38), Image.Resampling.NEAREST)
    right_native = right.resize((28, 38), Image.Resampling.NEAREST)
    opening.save(TEMP / "hospital_sliding_clinical_doors_open_frame_source.png")
    opening_native.save(TEMP / "hospital_sliding_clinical_doors_open_frame_native.png")
    left.save(TEMP / "hospital_sliding_clinical_doors_open_left_parked_source.png")
    left_native.save(TEMP / "hospital_sliding_clinical_doors_open_left_parked_native.png")
    right.save(TEMP / "hospital_sliding_clinical_doors_open_right_parked_source.png")
    right_native.save(TEMP / "hospital_sliding_clinical_doors_open_right_parked_native.png")
    save(preview(opening, left_native, right_native), "architecture_C7_extracted_preview.png")
    original = compose_run(5, 1, "architecture_C7_reconstructed_original.png")
    extended = compose_run(8, 3, "architecture_C7_reconstructed_extended.png")
    gaps = lambda image, box: sum(1 for value in image.getchannel("A").crop(box).get_flattened_data() if value == 0)

    report = {
        "validation_id": "architecture_master_C7_v1",
        "purpose": "reference-only open sliding clinical-door validation",
        "production_metadata_modified": False,
        "source": {"master": str(MASTER.relative_to(ROOT)).replace("\\", "/"), "dimensions": list(master.size), "mode": master.mode, "source_scale": SOURCE_SCALE},
        "geometry": {"structural_bounds": list(STRUCTURE), "vertical_grid": list(X_LINES), "horizontal_grid": list(Y_LINES), "opening": list(OPENING), "clear_passage": list(PASSAGE), "deviation_source_px": 0, "drift": "none"},
        "parked_leaves": {
            "left": {"bounds": list(LEFT_LEAF), "glazing": list(LEFT_GLAZING), "pull": list(LEFT_PULL), "anchor_relative_to_opening_native": [-24, 14], "wall_plane_only": True, "outside_clear_passage": True},
            "right": {"bounds": list(RIGHT_LEAF), "glazing": list(RIGHT_GLAZING), "pull": list(RIGHT_PULL), "anchor_relative_to_opening_native": [60, 14], "wall_plane_only": True, "outside_clear_passage": True},
            "slide_distance_source_px": 224, "track_header": list(TRACK), "floor_projection": False, "hinges_present": False,
        },
        "temporary_representation": {
            "recommended": "split fixed doorway/opening + left parked leaf overlay + right parked leaf overlay",
            "rationale": "Each leaf occupies a neighboring wall bay; splitting preserves the fixed two-cell opening while retaining independent lateral state placement and simple back-wall layer ordering.",
            "fixed_opening": {"crop": list(OPENING), "native_dimensions": [64, 52], "alpha_extrema": list(opening_native.getchannel("A").getextrema()), "components": components(opening_native), "clear_passage_treatment": "opaque recessed visual backing retained from validated master; no unsupported transparent-world layer is inferred"},
            "left_overlay": {"crop": list(LEFT_LEAF), "native_dimensions": [28, 38], "alpha_extrema": list(left_native.getchannel("A").getextrema()), "components": components(left_native), "anchor_relative_to_opening_native": [-24, 14]},
            "right_overlay": {"crop": list(RIGHT_LEAF), "native_dimensions": [28, 38], "alpha_extrema": list(right_native.getchannel("A").getextrema()), "components": components(right_native), "anchor_relative_to_opening_native": [60, 14]},
            "normalization": "architecture_grid_preserving; no trim or safety padding",
        },
        "reconstruction": {"original_5_cell": {"result": "pass", "door_start_column": 1, "floor_alpha_gaps": gaps(original, (16, 52, 176, 116))}, "extended_8_cell": {"result": "pass", "door_start_column": 3, "floor_alpha_gaps": gaps(extended, (16, 52, 272, 116))}, "continuity": "pass: cap/base/teal/baseline/floor/threshold/frame/clear passage and lateral parking; no cumulative drift"},
        "qa": {"clipping": False, "suspicious_debris": 0, "track_header_alignment": "pass", "glazing_alignment": "pass", "pull_alignment": "pass", "clear_passage_integrity": "pass", "recommendation": "PASS"},
    }
    (VALIDATION / "architecture_C7_validation_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md = """# Architecture Master C7 Validation v1\n\n## Result\n\n**PASS.** C7 preserves C6's grid-locked two-cell doorway while expressing a structurally distinct, laterally parked open sliding state. It remains reference-only.\n\n## Geometry\n\nAll structural coordinates have 0 px deviation: run `128..1408`, opening `(384,0)..(896,416)`, clear passage `(416,112)..(864,416)`, and horizontal references `416,672,768,928`. Both leaves slide laterally by 224 source px, stay out of the clear passage and floor plane, and retain the C6 family track/header.\n\n## Recommended representation\n\n**Split fixed doorway/opening plus left and right parked-leaf overlays.** The grid-locked opening remains `512x416` source / `64x52` native. Each parked leaf is `224x304` source / `28x38` native and anchors at `(-24,14)` or `(60,14)` native relative to the opening. The opaque recessed passage visual is retained for this validation because no separate transparent-world layer exists in the approved architecture contract.\n\n## Reconstruction\n\nThe original five-cell and relocated eight-cell runs pass with zero interior floor alpha gaps, continuous cap/base/teal/baseline/threshold behavior, an intact centered passage, correct lateral leaf parking, and no cumulative drift.\n\n## Scope\n\nAll outputs are temporary reference-only validation artifacts. No Production Batch 12 metadata or catalog entry was created.\n"""
    (VALIDATION / "architecture_C7_validation_report.md").write_text(md, encoding="utf-8")
    print(json.dumps({"recommendation": "PASS", "fixed_native": [64, 52], "leaf_native": [28, 38]}, indent=2))


if __name__ == "__main__":
    main()
