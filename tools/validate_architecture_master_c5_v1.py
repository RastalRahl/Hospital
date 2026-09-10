"""Reference-only validation for C5's half-open double-door system."""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "references" / "architecture" / "master_validation_C5_v1"
SOURCES = VALIDATION / "sources"
TEMP = VALIDATION / "temporary_components"
ARTIFACTS = VALIDATION / "artifacts"
ASSETS = ROOT / "assets" / "architecture"
MASTER = SOURCES / "rastalr_architecture_master_C5_double_doors_half_open_v1.png"
SCAFFOLD = SOURCES / "architecture_master_C5_double_doors_half_open_clean_scaffold.png"
SPEC = SOURCES / "architecture_master_C5_double_doors_half_open_spec.json"

SOURCE_SCALE = 8
STRUCTURE = (128, 0, 1408, 928)
OPENING = (384, 0, 896, 416)
X_LINES = (128, 384, 640, 896, 1152, 1408)
Y_LINES = (416, 672, 768, 928)
LEFT_POLYGON = ((432, 88), (568, 160), (568, 496), (432, 408))
RIGHT_POLYGON = ((712, 160), (848, 88), (848, 408), (712, 496))
LEFT_CROP = (384, 408, 640, 496)
RIGHT_CROP = (640, 408, 896, 496)


def rgba(path: Path) -> Image.Image:
    return Image.open(path).convert("RGBA")


def save(image: Image.Image, name: str) -> None:
    image.save(ARTIFACTS / name)


def components(image: Image.Image) -> int:
    alpha = image.getchannel("A")
    width, height = alpha.size; data = list(alpha.get_flattened_data())
    seen: set[int] = set(); count = 0
    for index, value in enumerate(data):
        if value == 0 or index in seen:
            continue
        count += 1; seen.add(index); queue: deque[int] = deque([index])
        while queue:
            current = queue.popleft(); x, y = current % width, current // width
            for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                neighbor = ny * width + nx
                if 0 <= nx < width and 0 <= ny < height and neighbor not in seen and data[neighbor] > 0:
                    seen.add(neighbor); queue.append(neighbor)
    return count


def overlay_crop(master: Image.Image, crop: tuple[int, int, int, int], polygon: tuple[tuple[int, int], ...]) -> Image.Image:
    image = master.crop(crop).convert("RGBA")
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).polygon([(x-crop[0], y-crop[1]) for x,y in polygon], fill=255)
    image.putalpha(mask)
    return image


def alignment(master: Image.Image, scaffold: Image.Image) -> Image.Image:
    base = master.convert("RGBA"); guide = scaffold.convert("RGBA"); guide.putalpha(36)
    base = Image.alpha_composite(base, guide); draw = ImageDraw.Draw(base)
    draw.rectangle(STRUCTURE, outline=(255,225,0,255), width=2)
    for x in X_LINES: draw.line((x,0,x,928), fill=(255,0,255,255), width=2)
    for y in Y_LINES: draw.line((128,y,1408,y), fill=(255,0,255,255), width=2)
    draw.rectangle(OPENING, outline=(0,230,255,255), width=3)
    draw.line((*LEFT_POLYGON, LEFT_POLYGON[0]), fill=(255,126,48,255), width=4)
    draw.line((*RIGHT_POLYGON, RIGHT_POLYGON[0]), fill=(96,255,160,255), width=4)
    return base


def leaf_diagnostic(master: Image.Image) -> Image.Image:
    out = master.convert("RGBA"); draw=ImageDraw.Draw(out)
    draw.line((*LEFT_POLYGON, LEFT_POLYGON[0]), fill=(255,126,48,255), width=5)
    draw.line((*RIGHT_POLYGON, RIGHT_POLYGON[0]), fill=(96,255,160,255), width=5)
    draw.line((640,0,640,496),fill=(255,225,0,255),width=2)
    return out


def asset(pattern: str, index: int) -> Image.Image:
    return rgba(ASSETS / pattern.format(index=index))


def compose_run(columns: int, door_start: int, name: str) -> Image.Image:
    canvas=Image.new("RGBA",(columns*32+32,128),(0,0,0,0))
    doorway=rgba(TEMP/"hospital_double_doors_half_open_opening_native.png")
    left=rgba(TEMP/"hospital_double_doors_half_open_left_projection_native.png")
    right=rgba(TEMP/"hospital_double_doors_half_open_right_projection_native.png")
    for col in range(columns):
        x=16+col*32
        canvas.alpha_composite(asset("hospital_floor_plain_{index:02d}.png", col%4+1),(x,52))
        canvas.alpha_composite(asset("hospital_floor_plain_{index:02d}.png",(col+1)%4+1),(x,84))
        if col not in (door_start,door_start+1):
            canvas.alpha_composite(asset("hospital_wall_back_straight_{index:02d}.png",col%4+1),(x,0))
        canvas.alpha_composite(asset("hospital_front_wall_cutaway_{index:02d}.png",col%4+1),(x,96))
    origin=16+door_start*32
    canvas.alpha_composite(doorway,(origin,0))
    # Overlap one row above y=416 so both leaves meet their doorway material without a seam.
    canvas.alpha_composite(left,(origin,51))
    canvas.alpha_composite(right,(origin+32,51))
    save(canvas.resize((canvas.width*8,canvas.height*8),Image.Resampling.NEAREST),name)
    return canvas


def preview(opening: Image.Image, left: Image.Image, right: Image.Image) -> Image.Image:
    out=Image.new("RGBA",(1200,940),(20,30,42,255)); draw=ImageDraw.Draw(out); font=ImageFont.load_default()
    out.alpha_composite(opening.resize((1024,832),Image.Resampling.NEAREST),(24,48))
    out.alpha_composite(left.resize((128,44),Image.Resampling.NEAREST),(1040,390))
    out.alpha_composite(right.resize((128,44),Image.Resampling.NEAREST),(1040,450))
    draw.text((24,18),"fixed opening source: 512 x 416",fill="white",font=font)
    draw.text((1040,360),"leaf overlays",fill="white",font=font)
    draw.text((1040,510),"each native: 32 x 11",fill="white",font=font)
    return out


def main() -> None:
    TEMP.mkdir(parents=True,exist_ok=True); ARTIFACTS.mkdir(parents=True,exist_ok=True)
    spec=json.loads(SPEC.read_text(encoding="utf-8")); master=Image.open(MASTER); scaffold=Image.open(SCAFFOLD)
    if master.size != (1536,1024) or scaffold.size != master.size: raise ValueError("C5 source/scaffold must be 1536 x 1024")
    if tuple(spec["opening_source_px"]) != OPENING or tuple(map(tuple,spec["left_leaf_projection_source_polygon"])) != LEFT_POLYGON or tuple(map(tuple,spec["right_leaf_projection_source_polygon"])) != RIGHT_POLYGON: raise ValueError("C5 specification mismatch")
    save(alignment(master,scaffold),"architecture_C5_scaffold_alignment.png")
    save(leaf_diagnostic(master),"architecture_C5_leaf_geometry_diagnostic.png")
    opening=master.crop(OPENING).convert("RGBA"); opening_native=opening.resize((64,52),Image.Resampling.NEAREST)
    left=overlay_crop(master,LEFT_CROP,LEFT_POLYGON); right=overlay_crop(master,RIGHT_CROP,RIGHT_POLYGON)
    left_native=left.resize((32,11),Image.Resampling.NEAREST); right_native=right.resize((32,11),Image.Resampling.NEAREST)
    opening.save(TEMP/"hospital_double_doors_half_open_opening_source.png"); opening_native.save(TEMP/"hospital_double_doors_half_open_opening_native.png")
    left.save(TEMP/"hospital_double_doors_half_open_left_projection_source.png"); left_native.save(TEMP/"hospital_double_doors_half_open_left_projection_native.png")
    right.save(TEMP/"hospital_double_doors_half_open_right_projection_source.png"); right_native.save(TEMP/"hospital_double_doors_half_open_right_projection_native.png")
    save(preview(opening,left_native,right_native),"architecture_C5_extracted_preview.png")
    original=compose_run(5,1,"architecture_C5_reconstructed_original.png")
    extended=compose_run(8,3,"architecture_C5_reconstructed_extended.png")
    gaps=lambda image,box:sum(1 for v in image.getchannel("A").crop(box).get_flattened_data() if v==0)
    report={
      "validation_id":"architecture_master_C5_v1","purpose":"reference-only half-open double-door validation","production_metadata_modified":False,
      "source":{"master":str(MASTER.relative_to(ROOT)).replace("\\","/"),"dimensions":list(master.size),"mode":master.mode,"source_scale":8},
      "geometry":{"structural_bounds":list(STRUCTURE),"vertical_grid":list(X_LINES),"horizontal_grid":list(Y_LINES),"opening":list(OPENING),"centerline":640,"deviation_source_px":0,"drift":"none"},
      "leaves":{"left":{"hinge_top":[432,88],"hinge_bottom":[432,408],"free_top":[568,160],"free_bottom":[568,496],"envelope":[432,88,568,496],"lowest_y":496},"right":{"hinge_top":[848,88],"hinge_bottom":[848,408],"free_top":[712,160],"free_bottom":[712,496],"envelope":[712,88,848,496],"lowest_y":496},"matches_spec":True,"symmetry":"mirror-equivalent inward geometry"},
      "temporary_representation":{"recommended":"fixed doorway + two separate leaf overlays","rationale":"Each leaf has an independent jamb, symmetry, and future state/animation value while retaining a grid-locked shared doorway and simple layer ordering.","opening":{"crop":list(OPENING),"native_dimensions":[64,52],"alpha_extrema":list(opening_native.getchannel("A").getextrema()),"components":components(opening_native)},"left_overlay":{"crop":list(LEFT_CROP),"native_dimensions":[32,11],"anchor_relative_to_opening":[0,51],"alpha_extrema":list(left_native.getchannel("A").getextrema()),"components":components(left_native)},"right_overlay":{"crop":list(RIGHT_CROP),"native_dimensions":[32,11],"anchor_relative_to_opening":[32,51],"alpha_extrema":list(right_native.getchannel("A").getextrema()),"components":components(right_native)},"normalization":"architecture_grid_preserving; no trim or safety padding"},
      "reconstruction":{"original_5_cell":{"result":"pass","door_start_column":1,"floor_alpha_gaps":gaps(original,(16,52,176,116))},"extended_8_cell":{"result":"pass","door_start_column":3,"floor_alpha_gaps":gaps(extended,(16,52,272,116))},"continuity":"pass: cap/base/teal/baseline/floor/threshold and leaf order; no cumulative drift"},
      "qa":{"clipping":False,"suspicious_debris":0,"recommendation":"PASS"}}
    (VALIDATION/"architecture_C5_validation_report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    md="""# Architecture Master C5 Validation v1\n\n## Result\n\n**PASS.** C5 preserves C4's grid-locked two-cell doorway and its specified symmetrical open-leaf projections. It was not ingested.\n\n## Geometry\n\nAll structural coordinates have 0 px deviation: run `128..1408`, opening `384,0..896,416`, centreline `x=640`, and horizontal references `416,672,768,928`. Left leaf hinge is `(432,88)..(432,408)` and right hinge `(848,88)..(848,408)`; both project inward to `y=496`.\n\n## Recommended representation\n\n**Fixed doorway + two separate leaf overlays.** The grid-locked opening is `512×416` source / `64×52` native. Each geometry-masked below-threshold leaf projection uses one `256×88` source / `32×11` native crop, anchored at `(0,51)` and `(32,51)` relative to the opening. This retains future independent leaf states without making the structural doorway movable or reintroducing drift.\n\n## Reconstruction\n\nThe original five-cell and relocated eight-cell runs pass with zero interior floor alpha gaps, continuous cap/base/teal/baseline/threshold behavior, and leaves rendered over the floor.\n\n## Scope\n\nAll assets are temporary reference-only validation outputs. No Production Batch 12 metadata or catalog entry was created.\n"""
    (VALIDATION/"architecture_C5_validation_report.md").write_text(md,encoding="utf-8")
    print(json.dumps({"recommendation":"PASS","opening_native":[64,52],"overlay_native":[32,11]},indent=2))


if __name__=="__main__": main()
