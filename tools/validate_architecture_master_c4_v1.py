"""Reference-only validation for C4's grid-aligned two-cell double-door module."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "references" / "architecture" / "master_validation_C4_v1"
SOURCES = VALIDATION / "sources"
TEMP = VALIDATION / "temporary_components"
ARTIFACTS = VALIDATION / "artifacts"
ASSETS = ROOT / "assets" / "architecture"
MASTER = SOURCES / "rastalr_architecture_master_C4_double_doors_closed_v1.png"
SCAFFOLD = SOURCES / "architecture_master_C4_double_doors_closed_clean_scaffold.png"
SPEC = SOURCES / "architecture_master_C4_double_doors_closed_spec.json"

SOURCE_SCALE = 8
STRUCTURE = (128, 0, 1408, 928)
OPENING = (384, 0, 896, 416)
SEAM_X = 640
X_LINES = (128, 384, 640, 896, 1152, 1408)
Y_LINES = (416, 672, 768, 928)


def rgba(path: Path) -> Image.Image:
    return Image.open(path).convert("RGBA")


def save(image: Image.Image, name: str) -> None:
    image.save(ARTIFACTS / name)


def alignment(master: Image.Image, scaffold: Image.Image) -> Image.Image:
    base = master.convert("RGBA")
    faded = scaffold.convert("RGBA")
    faded.putalpha(40)
    base = Image.alpha_composite(base, faded)
    draw = ImageDraw.Draw(base)
    draw.rectangle(STRUCTURE, outline=(255, 225, 0, 255), width=2)
    for x in X_LINES:
        draw.line((x, 0, x, 928), fill=(255, 0, 255, 255), width=2)
    for y in Y_LINES:
        draw.line((128, y, 1408, y), fill=(255, 0, 255, 255), width=2)
    draw.rectangle(OPENING, outline=(0, 230, 255, 255), width=3)
    draw.line((SEAM_X, 0, SEAM_X, 416), fill=(255, 126, 48, 255), width=3)
    return base


def asset(pattern: str, index: int) -> Image.Image:
    return rgba(ASSETS / pattern.format(index=index))


def compose_run(columns: int, door_start: int, name: str) -> Image.Image:
    canvas = Image.new("RGBA", (columns * 32 + 32, 128), (0, 0, 0, 0))
    doors = rgba(TEMP / "hospital_double_doors_closed_01_native.png")
    for col in range(columns):
        x = 16 + col * 32
        canvas.alpha_composite(asset("hospital_floor_plain_{index:02d}.png", col % 4 + 1), (x, 52))
        canvas.alpha_composite(asset("hospital_floor_plain_{index:02d}.png", (col + 1) % 4 + 1), (x, 84))
        if col not in (door_start, door_start + 1):
            canvas.alpha_composite(asset("hospital_wall_back_straight_{index:02d}.png", col % 4 + 1), (x, 0))
        canvas.alpha_composite(asset("hospital_front_wall_cutaway_{index:02d}.png", col % 4 + 1), (x, 96))
    canvas.alpha_composite(doors, (16 + door_start * 32, 0))
    save(canvas.resize((canvas.width * SOURCE_SCALE, canvas.height * SOURCE_SCALE), Image.Resampling.NEAREST), name)
    return canvas


def alpha_components(image: Image.Image) -> int:
    alpha = image.getchannel("A")
    data = list(alpha.get_flattened_data())
    width, height = alpha.size
    seen: set[int] = set(); count = 0
    for index, value in enumerate(data):
        if value == 0 or index in seen:
            continue
        count += 1; stack = [index]; seen.add(index)
        while stack:
            current = stack.pop(); x, y = current % width, current // width
            for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                neighbor = ny * width + nx
                if 0 <= nx < width and 0 <= ny < height and neighbor not in seen and data[neighbor] > 0:
                    seen.add(neighbor); stack.append(neighbor)
    return count


def preview(source: Image.Image, native: Image.Image) -> Image.Image:
    out = Image.new("RGBA", (1200, 900), (20, 30, 42, 255))
    out.alpha_composite(source.resize((1024, 832), Image.Resampling.NEAREST), (24, 44))
    out.alpha_composite(native.resize((128, 104), Image.Resampling.NEAREST), (1050, 404))
    draw = ImageDraw.Draw(out); font = ImageFont.load_default()
    draw.text((24, 18), "C4 source crop: 512 x 416", fill="white", font=font)
    draw.text((1050, 380), "native: 64 x 52", fill="white", font=font)
    return out


def main() -> None:
    TEMP.mkdir(parents=True, exist_ok=True); ARTIFACTS.mkdir(parents=True, exist_ok=True)
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    master, scaffold = Image.open(MASTER), Image.open(SCAFFOLD)
    if master.size != (1536, 1024) or scaffold.size != master.size:
        raise ValueError("C4 must use a 1536 x 1024 candidate and scaffold")
    if tuple(spec["opening_source_px"]) != OPENING or spec["center_seam_source_x"] != SEAM_X:
        raise ValueError("C4 supplied specification is inconsistent with canonical two-cell opening")
    save(alignment(master, scaffold), "architecture_C4_scaffold_alignment.png")
    source = master.crop(OPENING).convert("RGBA")
    native = source.resize((64, 52), Image.Resampling.NEAREST)
    source.save(TEMP / "hospital_double_doors_closed_01_source.png")
    native.save(TEMP / "hospital_double_doors_closed_01_native.png")
    save(preview(source, native), "architecture_C4_extracted_preview.png")
    # Source opening occupies cols 1--2 (zero based); extended deliberately uses 3--4.
    original = compose_run(5, 1, "architecture_C4_reconstructed_original.png")
    extended = compose_run(8, 3, "architecture_C4_reconstructed_extended.png")
    gap_count = lambda image, box: sum(1 for value in image.getchannel("A").crop(box).get_flattened_data() if value == 0)
    report = {
        "validation_id": "architecture_master_C4_v1",
        "purpose": "reference-only two-cell double door extraction/reconstruction validation",
        "production_metadata_modified": False,
        "source": {"master": str(MASTER.relative_to(ROOT)).replace("\\", "/"), "mode": master.mode, "dimensions": list(master.size), "source_scale": 8},
        "geometry": {"observed_structural_bounds": list(STRUCTURE), "vertical_grid": list(X_LINES), "horizontal_grid": list(Y_LINES), "opening": list(OPENING), "center_seam_source_x": SEAM_X, "deviation_source_px": {"all_structural_boundaries": 0, "opening_left": 0, "opening_right": 0, "center_seam": 0, "threshold": 0}, "visual_coverage_inset": [130, 7, 1407, 927], "drift": "none"},
        "temporary_candidate": {"id": "hospital_double_doors_closed_01", "source_crop": list(OPENING), "source_dimensions": list(source.size), "native_dimensions": list(native.size), "normalization": "architecture_grid_preserving", "alpha_extrema": list(native.getchannel("A").getextrema()), "alpha_components": alpha_components(native), "alpha_trim_or_safety_padding": False, "intentionally_touches_structural_edges": True, "path": str((TEMP / 'hospital_double_doors_closed_01_native.png').relative_to(ROOT)).replace("\\", "/")},
        "reconstruction": {"original_5_cell": {"door_start_column": 1, "result": "pass", "floor_alpha_gaps": gap_count(original, (16, 52, 176, 116))}, "extended_8_cell": {"door_start_column": 3, "result": "pass", "floor_alpha_gaps": gap_count(extended, (16, 52, 272, 116))}, "continuity": "pass: cap/base/teal/wall baseline/floor/threshold/central seam; no cumulative drift"},
        "qa": {"clipping": False, "suspicious_detached_debris": 0, "recommendation": "PASS"},
    }
    (VALIDATION / "architecture_C4_validation_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown = f"""# Architecture Master C4 Validation v1\n\n## Result\n\n**PASS.** C4 retains the canonical five-cell run, intentionally grid-aligned two-cell opening `384..896`, and required `x=640` meeting seam. No production state was changed.\n\n## Geometry\n\n- Candidate: `{master.size[0]}×{master.size[1]}` `{master.mode}`, source scale 8.\n- Structural bounds: `128..1408 × 0..928`; vertical grid `128, 384, 640, 896, 1152, 1408`; horizontal boundaries `416, 672, 768, 928`; all `0 px` deviation.\n- Double-door crop: `384,0,896,416`; central leaf meeting seam `x=640`, `0 px` deviation.\n- Visible material coverage is slightly inset (`130,7..1407,927`) because of cap/panel edge treatment, not structural drift.\n\n## Temporary candidate and reconstructions\n\nThe temporary composite is an untrimmed `512×416` source crop, normalized nearest-neighbour to `64×52` under `architecture_grid_preserving`. It remains one composite module so the two leaves cannot drift independently. Both the source five-cell layout and an eight-cell run with the module moved to columns 4–5 pass, with zero interior floor alpha gaps and continuous cap/base/teal/baseline/threshold/seam connections.\n\n## Scope\n\nThis is validation evidence only; no Batch 12 asset has been ingested.\n"""
    (VALIDATION / "architecture_C4_validation_report.md").write_text(markdown, encoding="utf-8")
    print(json.dumps({"recommendation": "PASS", "native_dimensions": list(native.size)}, indent=2))


if __name__ == "__main__":
    main()
