from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
APPROVED = ROOT / "assets/patient_rooms/bedside_cabinet_01.png"
V1 = ROOT / "demo/hospital_integration/repair_candidates/perspective_calibration_v1/bedside_cabinet_01_perspective_candidate.png"
V2 = ROOT / "demo/hospital_integration/repair_candidates/perspective_cabinet_v2/bedside_cabinet_01_art_candidate_v2.png"
LOCKED_HASHES = {
    APPROVED: "62c5decd09bbbb5a0d18cb1b0e16178e522b9f3da47db4f38a6bb4f052c82993",
    V1: "ebd144c37df0d33c0c432737753f07957ceed57cd05c4a76aad22b743a4df617",
    V2: "70c8789986e0f84f0543e64b7f26d8edbe3dbb812c92608ec7b3121bf1d17ed6",
}

T = (0, 0, 0, 0)
INK = (24, 35, 49, 255)
LINE = (52, 70, 86, 255)
CONTACT = (17, 25, 35, 255)
IVORY_HI = (250, 245, 235, 255)
IVORY = (239, 232, 218, 255)
IVORY_MID = (221, 216, 205, 255)
IVORY_SHADE = (185, 184, 179, 255)
STEEL_HI = (153, 183, 191, 255)
STEEL = (104, 139, 158, 255)
STEEL_DARK = (65, 88, 107, 255)
TEAL = (91, 151, 148, 255)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rect(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], color: tuple[int, int, int, int]) -> None:
    draw.rectangle(box, fill=color)


def px(draw: ImageDraw.ImageDraw, x: int, y: int, color: tuple[int, int, int, int]) -> None:
    draw.point((x, y), fill=color)


def cabinet_v3() -> Image.Image:
    image = Image.new("RGBA", (32, 36), T)
    draw = ImageDraw.Draw(image)

    # One shallow top plane. The two stepped corner pixels soften the silhouette
    # without introducing a diagonal side face or a second stacked crown.
    rect(draw, (5, 3, 26, 3), INK)
    rect(draw, (4, 4, 27, 9), INK)
    rect(draw, (3, 6, 28, 9), INK)
    rect(draw, (5, 4, 26, 4), IVORY_HI)
    rect(draw, (4, 5, 27, 7), IVORY)
    rect(draw, (4, 8, 27, 8), IVORY_MID)
    rect(draw, (3, 9, 28, 9), IVORY_SHADE)
    px(draw, 4, 5, IVORY_HI)
    px(draw, 27, 7, IVORY_SHADE)

    # A single slim front edge joins the worktop to the body.
    rect(draw, (2, 10, 29, 12), INK)
    rect(draw, (3, 10, 28, 10), IVORY_HI)
    rect(draw, (3, 11, 28, 11), IVORY)
    rect(draw, (4, 12, 27, 12), STEEL_DARK)
    px(draw, 3, 11, STEEL_HI)

    # Calm body mass. Full-strength ink is reserved for the exterior silhouette;
    # internal construction uses slate so the cabinet does not read as a diagram.
    rect(draw, (4, 13, 27, 30), INK)
    rect(draw, (5, 13, 26, 29), IVORY_MID)
    rect(draw, (5, 13, 5, 28), IVORY_HI)
    rect(draw, (26, 14, 26, 29), IVORY_SHADE)

    # Broad steel drawer face with one compact pull and two material clusters.
    rect(draw, (6, 14, 25, 19), STEEL_DARK)
    rect(draw, (7, 14, 24, 18), STEEL)
    rect(draw, (7, 14, 22, 14), STEEL_HI)
    rect(draw, (7, 15, 7, 17), STEEL_HI)
    rect(draw, (8, 18, 24, 18), STEEL_DARK)
    rect(draw, (13, 16, 19, 17), LINE)
    rect(draw, (14, 16, 18, 16), IVORY_HI)

    # One quiet cupboard plane: a slim separator, a soft right recess, and one
    # readable latch. There are no nested borders or decorative hinge pixels.
    rect(draw, (6, 20, 25, 20), LINE)
    rect(draw, (6, 21, 25, 28), IVORY)
    rect(draw, (6, 21, 23, 21), IVORY_HI)
    rect(draw, (6, 22, 6, 27), IVORY_HI)
    rect(draw, (24, 22, 25, 28), IVORY_SHADE)
    rect(draw, (7, 28, 23, 28), IVORY_MID)
    rect(draw, (8, 23, 9, 25), TEAL)
    px(draw, 8, 23, STEEL_HI)

    # A narrow base, clipped feet, and one small contact cluster.
    rect(draw, (4, 30, 27, 31), INK)
    rect(draw, (6, 30, 25, 30), LINE)
    rect(draw, (7, 31, 24, 31), IVORY_SHADE)
    rect(draw, (6, 32, 9, 33), LINE)
    rect(draw, (22, 32, 25, 33), LINE)
    px(draw, 7, 32, STEEL_HI)
    px(draw, 23, 32, STEEL)
    rect(draw, (9, 34, 22, 34), CONTACT)
    return image


def font(size: int) -> ImageFont.ImageFont:
    for path in (Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/segoeui.ttf")):
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def montage(images: list[tuple[str, Image.Image]]) -> Image.Image:
    scale = 7
    result = Image.new("RGBA", (1080, 430), (237, 232, 218, 255))
    draw = ImageDraw.Draw(result)
    draw.text((24, 16), "Bedside cabinet art pilot — approved / V1 / V2 / V3", font=font(24), fill=INK)
    draw.text((24, 48), "Native pixels enlarged 7x; common 1x1 footprint and bottom-center anchor", font=font(16), fill=LINE)
    centers = [130, 390, 650, 910]
    floor_y = 385
    for (label, source), center in zip(images, centers):
        draw.text((center - 76, 78), label, font=font(16), fill=STEEL_DARK)
        enlarged = source.resize((source.width * scale, source.height * scale), Image.Resampling.NEAREST)
        result.alpha_composite(enlarged, (center - enlarged.width // 2, floor_y - enlarged.height))
        draw.line((center - 5, floor_y, center + 5, floor_y), fill=(218, 164, 66, 255), width=2)
        draw.line((center, floor_y - 5, center, floor_y + 5), fill=(218, 164, 66, 255), width=2)
    draw.line((20, floor_y + 8, 1060, floor_y + 8), fill=LINE, width=2)
    draw.text((24, 406), "V3: one top plane, exterior-weighted outline, quiet door, larger clusters", font=font(14), fill=LINE)
    return result


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for path, expected in LOCKED_HASHES.items():
        assert digest(path) == expected
    copies = {
        "APPROVED": (APPROVED, OUT / "bedside_cabinet_01_approved.png"),
        "V1 GEOMETRY": (V1, OUT / "bedside_cabinet_01_v1_geometry.png"),
        "V2 REJECTED": (V2, OUT / "bedside_cabinet_01_v2_art.png"),
    }
    for source, destination in copies.values():
        shutil.copyfile(source, destination)
    v3 = cabinet_v3()
    assert v3.size == (32, 36)
    assert v3.getbbox() == (2, 3, 30, 35)
    assert all(alpha in (0, 255) for alpha in v3.getchannel("A").get_flattened_data())
    palette = {color for color in v3.get_flattened_data() if color[3]}
    expected_palette = {INK, LINE, CONTACT, IVORY_HI, IVORY, IVORY_MID, IVORY_SHADE, STEEL_HI, STEEL, STEEL_DARK, TEAL}
    assert palette == expected_palette
    candidate = OUT / "bedside_cabinet_01_art_candidate_v3.png"
    v3.save(candidate)
    review_items = [(label, Image.open(destination).convert("RGBA")) for label, (_, destination) in copies.items()]
    review_items.append(("V3 ART", v3))
    montage(review_items).save(OUT / "bedside_cabinet_v3_review.png")
    mapping = {
        "status": "needs_human_review",
        "logical_id": "bedside_cabinet_01",
        "scope": "reference-only V3 art pilot; production and approval unchanged",
        "references": [
            {"label": label.lower().replace(" ", "_"), "path": source.relative_to(ROOT).as_posix(), "sha256": digest(source)}
            for label, (source, _) in copies.items()
        ],
        "candidate": {
            "path": candidate.relative_to(ROOT).as_posix(),
            "sha256": digest(candidate),
            "dimensions": list(v3.size),
            "alpha_bbox": list(v3.getbbox()),
            "opaque_palette_size": len(palette),
            "partial_alpha_pixels": 0,
            "logical_footprint_tiles": [1, 1],
            "anchor": "bottom_center",
        },
        "approval_status_changed": False,
    }
    (OUT / "mapping.json").write_text(json.dumps(mapping, indent=2) + "\n", encoding="utf-8")
    print("BEDSIDE_CABINET_V3_BUILD_PASS: 32x36 native sprite; 11 opaque colors; hard alpha; prior hashes locked")


if __name__ == "__main__":
    main()
