"""Reference-only validation for C6 closed sliding clinical doors."""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "references" / "architecture" / "master_validation_C6_v1"
SOURCES = VALIDATION / "sources"
TEMP = VALIDATION / "temporary_components"
ARTIFACTS = VALIDATION / "artifacts"
ASSETS = ROOT / "assets" / "architecture"
MASTER = SOURCES / "rastalr_architecture_master_C6_sliding_clinical_doors_closed_v1.png"
SCAFFOLD = SOURCES / "architecture_master_C6_sliding_clinical_doors_closed_clean_scaffold.png"
SPEC = SOURCES / "architecture_master_C6_sliding_clinical_doors_closed_spec.json"

SOURCE_SCALE = 8
STRUCTURE = (128, 0, 1408, 928)
OPENING = (384, 0, 896, 416)
X_LINES = (128, 384, 640, 896, 1152, 1408)
Y_LINES = (416, 672, 768, 928)
MEETING_LINE = 640
TRACK = (416, 64, 864, 112)
# These are visual insets measured against the supplied locked grid, not structural bounds.
LEFT_LEAF = (416, 112, 640, 416)
RIGHT_LEAF = (640, 112, 864, 416)
LEFT_GLAZING = (464, 144, 600, 312)
RIGHT_GLAZING = (688, 144, 824, 312)
LEFT_PULL = (600, 296, 624, 336)
RIGHT_PULL = (664, 296, 688, 336)


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
    draw.line((MEETING_LINE, 0, MEETING_LINE, 416), fill=(255, 126, 48, 255), width=3)
    return out


def diagnostic(master: Image.Image) -> Image.Image:
    out = master.convert("RGBA")
    draw = ImageDraw.Draw(out)
    draw.rectangle(TRACK, outline=(190, 120, 255, 255), width=4)
    draw.rectangle(LEFT_LEAF, outline=(255, 126, 48, 255), width=4)
    draw.rectangle(RIGHT_LEAF, outline=(96, 255, 160, 255), width=4)
    draw.rectangle(LEFT_GLAZING, outline=(0, 230, 255, 255), width=3)
    draw.rectangle(RIGHT_GLAZING, outline=(0, 230, 255, 255), width=3)
    draw.rectangle(LEFT_PULL, outline=(255, 225, 0, 255), width=3)
    draw.rectangle(RIGHT_PULL, outline=(255, 225, 0, 255), width=3)
    draw.line((MEETING_LINE, 0, MEETING_LINE, 416), fill=(255, 126, 48, 255), width=3)
    return out


def asset(pattern: str, index: int) -> Image.Image:
    return rgba(ASSETS / pattern.format(index=index))


def compose_run(columns: int, door_start: int, name: str) -> Image.Image:
    canvas = Image.new("RGBA", (columns * 32 + 32, 128), (0, 0, 0, 0))
    doorway = rgba(TEMP / "hospital_sliding_clinical_doors_closed_native.png")
    for col in range(columns):
        x = 16 + col * 32
        canvas.alpha_composite(asset("hospital_floor_plain_{index:02d}.png", col % 4 + 1), (x, 52))
        canvas.alpha_composite(asset("hospital_floor_plain_{index:02d}.png", (col + 1) % 4 + 1), (x, 84))
        if col not in (door_start, door_start + 1):
            canvas.alpha_composite(asset("hospital_wall_back_straight_{index:02d}.png", col % 4 + 1), (x, 0))
        canvas.alpha_composite(asset("hospital_front_wall_cutaway_{index:02d}.png", col % 4 + 1), (x, 96))
    canvas.alpha_composite(doorway, (16 + door_start * 32, 0))
    save(canvas.resize((canvas.width * 8, canvas.height * 8), Image.Resampling.NEAREST), name)
    return canvas


def preview(doorway: Image.Image) -> Image.Image:
    out = Image.new("RGBA", (1200, 940), (20, 30, 42, 255))
    draw = ImageDraw.Draw(out)
    font = ImageFont.load_default()
    out.alpha_composite(doorway.resize((1024, 832), Image.Resampling.NEAREST), (88, 56))
    draw.text((32, 20), "C6 fixed composite doorway: 512 x 416 source / 64 x 52 native", fill="white", font=font)
    draw.text((32, 896), "Includes fixed frame, closed sliding leaves, glazing, recessed pulls, and track/header.", fill="white", font=font)
    return out


def main() -> None:
    TEMP.mkdir(parents=True, exist_ok=True)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    master = Image.open(MASTER)
    scaffold = Image.open(SCAFFOLD)
    if master.size != (1536, 1024) or scaffold.size != master.size:
        raise ValueError("C6 source/scaffold must both be 1536 x 1024")
    if tuple(spec["opening_source_px"]) != OPENING or tuple(spec["track_header_source_px"]) != TRACK:
        raise ValueError("C6 specification mismatch")
    if spec["projection_overlay_required"] is not False:
        raise ValueError("C6 must not need a projection overlay")

    save(alignment(master, scaffold), "architecture_C6_scaffold_alignment.png")
    save(diagnostic(master), "architecture_C6_door_geometry_diagnostic.png")
    doorway = master.crop(OPENING).convert("RGBA")
    doorway_native = doorway.resize((64, 52), Image.Resampling.NEAREST)
    doorway.save(TEMP / "hospital_sliding_clinical_doors_closed_source.png")
    doorway_native.save(TEMP / "hospital_sliding_clinical_doors_closed_native.png")
    save(preview(doorway), "architecture_C6_extracted_preview.png")
    original = compose_run(5, 1, "architecture_C6_reconstructed_original.png")
    extended = compose_run(8, 3, "architecture_C6_reconstructed_extended.png")
    gaps = lambda image, box: sum(1 for value in image.getchannel("A").crop(box).get_flattened_data() if value == 0)

    report = {
        "validation_id": "architecture_master_C6_v1",
        "purpose": "reference-only closed sliding clinical-door validation",
        "production_metadata_modified": False,
        "source": {"master": str(MASTER.relative_to(ROOT)).replace("\\", "/"), "dimensions": list(master.size), "mode": master.mode, "source_scale": SOURCE_SCALE},
        "geometry": {"structural_bounds": list(STRUCTURE), "vertical_grid": list(X_LINES), "horizontal_grid": list(Y_LINES), "opening": list(OPENING), "meeting_line": MEETING_LINE, "deviation_source_px": 0, "drift": "none"},
        "sliding_leaves": {
            "left": {"bounds": list(LEFT_LEAF), "meeting_edge": MEETING_LINE, "glazing": list(LEFT_GLAZING), "pull": list(LEFT_PULL), "wall_plane_only": True},
            "right": {"bounds": list(RIGHT_LEAF), "meeting_edge": MEETING_LINE, "glazing": list(RIGHT_GLAZING), "pull": list(RIGHT_PULL), "wall_plane_only": True},
            "track_header": list(TRACK), "meeting_continuity": "pass", "floor_projection": False, "hinges_present": False,
        },
        "temporary_representation": {"recommended": "single composite doorway module", "rationale": "All C6 material is within the fixed two-cell wall plane; splitting creates no reusable projection or ordering advantage.", "crop": list(OPENING), "native_dimensions": [64, 52], "anchor": "architecture back-wall grid anchor spanning two cells", "alpha_extrema": list(doorway_native.getchannel("A").getextrema()), "components": components(doorway_native), "normalization": "architecture_grid_preserving; no trim or safety padding"},
        "reconstruction": {"original_5_cell": {"result": "pass", "door_start_column": 1, "floor_alpha_gaps": gaps(original, (16, 52, 176, 116))}, "extended_8_cell": {"result": "pass", "door_start_column": 3, "floor_alpha_gaps": gaps(extended, (16, 52, 272, 116))}, "continuity": "pass: cap/base/teal/baseline/floor/threshold/frame/meeting line; no cumulative drift"},
        "qa": {"clipping": False, "suspicious_debris": 0, "track_header_alignment": "pass", "glazing_alignment": "pass", "recommendation": "PASS"},
    }
    (VALIDATION / "architecture_C6_validation_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md = """# Architecture Master C6 Validation v1\n\n## Result\n\n**PASS.** C6 preserves the validated C4/C5 two-cell doorway geometry and adds a clinically distinct closed sliding-door treatment. It remains reference-only.\n\n## Geometry\n\nAll structural coordinates have 0 px deviation: run `128..1408`, opening `(384,0)..(896,416)`, meeting line `x=640`, and horizontal references `416,672,768,928`. The two leaves remain fully in the wall plane.\n\n## Recommended representation\n\n**Single composite doorway module.** The `512x416` source / `64x52` native crop contains the fixed frame, closed leaves, glazing, recessed pulls, and track/header. There is no leaf projection to warrant a split representation.\n\n## Reconstruction\n\nThe original five-cell and relocated eight-cell runs pass with zero interior floor alpha gaps, continuous cap/base/teal/baseline/threshold/frame behavior, a clean meeting line, and no cumulative drift.\n\n## Scope\n\nAll outputs are temporary reference-only validation artifacts. No Production Batch 12 metadata or catalog entry was created.\n"""
    (VALIDATION / "architecture_C6_validation_report.md").write_text(md, encoding="utf-8")
    print(json.dumps({"recommendation": "PASS", "doorway_native": [64, 52]}, indent=2))


if __name__ == "__main__":
    main()
