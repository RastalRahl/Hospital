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
APPROVED_SHA256 = "62c5decd09bbbb5a0d18cb1b0e16178e522b9f3da47db4f38a6bb4f052c82993"
V1_SHA256 = "ebd144c37df0d33c0c432737753f07957ceed57cd05c4a76aad22b743a4df617"

T = (0, 0, 0, 0)
INK = (24, 35, 49, 255)
INK_2 = (39, 55, 70, 255)
CONTACT = (17, 25, 35, 255)
IVORY_HI = (250, 245, 235, 255)
IVORY = (239, 232, 218, 255)
IVORY_MID = (225, 218, 204, 255)
IVORY_SHADE = (201, 195, 184, 255)
IVORY_DEEP = (177, 174, 168, 255)
STEEL_HI = (151, 179, 188, 255)
STEEL = (104, 139, 158, 255)
STEEL_DARK = (66, 91, 112, 255)
TEAL_HI = (139, 187, 179, 255)
TEAL = (91, 151, 148, 255)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rect(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], color: tuple[int, int, int, int]) -> None:
    draw.rectangle(box, fill=color)


def pixel(draw: ImageDraw.ImageDraw, x: int, y: int, color: tuple[int, int, int, int]) -> None:
    draw.point((x, y), fill=color)


def cabinet_v2() -> Image.Image:
    image = Image.new("RGBA", (34, 36), T)
    draw = ImageDraw.Draw(image)

    # Shallow top plane. Every construction edge stays horizontal/vertical;
    # one-pixel corner steps describe a manufactured bevel, not a turned side.
    rect(draw, (7, 3, 26, 3), INK)
    rect(draw, (5, 4, 28, 4), INK_2)
    rect(draw, (5, 5, 28, 9), INK_2)
    rect(draw, (6, 5, 27, 5), IVORY_HI)
    rect(draw, (6, 6, 27, 8), IVORY)
    rect(draw, (6, 9, 27, 9), IVORY_MID)
    pixel(draw, 6, 6, IVORY_HI)
    pixel(draw, 27, 8, IVORY_SHADE)

    # Projecting worktop lip, with a cool hygienic edge and upper-left glint.
    rect(draw, (3, 10, 30, 13), INK)
    rect(draw, (4, 10, 29, 10), IVORY_HI)
    rect(draw, (4, 11, 29, 11), IVORY)
    rect(draw, (4, 12, 29, 12), IVORY_SHADE)
    rect(draw, (4, 13, 29, 13), STEEL_DARK)
    pixel(draw, 4, 11, STEEL_HI)
    pixel(draw, 29, 12, INK_2)

    # Exterior frame and separate corner posts add structure without a broad
    # side plane. The right post is darker solely because light is upper-left.
    rect(draw, (5, 14, 28, 30), INK)
    rect(draw, (6, 14, 8, 29), IVORY_MID)
    rect(draw, (6, 14, 6, 28), IVORY_HI)
    rect(draw, (26, 14, 27, 29), IVORY_SHADE)
    rect(draw, (27, 15, 27, 28), IVORY_DEEP)

    # Recessed steel drawer with chamfered inner corners and a lit metal pull.
    rect(draw, (9, 14, 25, 19), INK_2)
    rect(draw, (10, 15, 24, 18), STEEL)
    rect(draw, (11, 15, 23, 15), STEEL_HI)
    rect(draw, (10, 16, 10, 18), TEAL_HI)
    rect(draw, (24, 16, 24, 18), STEEL_DARK)
    rect(draw, (11, 18, 23, 18), STEEL_DARK)
    pixel(draw, 11, 16, TEAL)
    pixel(draw, 23, 17, STEEL_DARK)
    rect(draw, (14, 16, 20, 18), INK)
    rect(draw, (15, 17, 19, 17), IVORY_HI)

    # Raised lower cupboard panel, latch and two small hinges. Large quiet
    # ivory clusters keep it readable at native scale.
    rect(draw, (9, 20, 25, 29), INK_2)
    rect(draw, (10, 21, 24, 28), IVORY_MID)
    rect(draw, (11, 21, 23, 21), IVORY_HI)
    rect(draw, (10, 22, 10, 27), IVORY_HI)
    rect(draw, (24, 22, 24, 27), IVORY_DEEP)
    rect(draw, (11, 28, 23, 28), IVORY_SHADE)
    rect(draw, (12, 23, 22, 26), IVORY)
    rect(draw, (12, 23, 21, 23), IVORY_HI)
    rect(draw, (22, 24, 22, 26), IVORY_SHADE)
    rect(draw, (12, 26, 21, 26), IVORY_MID)
    rect(draw, (12, 24, 13, 25), STEEL_DARK)
    pixel(draw, 12, 24, STEEL_HI)
    pixel(draw, 24, 23, INK_2)
    pixel(draw, 24, 27, INK_2)

    # Base rail, short feet and a small contact shadow.
    rect(draw, (5, 30, 28, 31), INK)
    rect(draw, (7, 30, 26, 30), STEEL_DARK)
    rect(draw, (8, 31, 25, 31), IVORY_DEEP)
    rect(draw, (7, 32, 10, 33), INK_2)
    rect(draw, (23, 32, 26, 33), INK_2)
    pixel(draw, 8, 32, STEEL_HI)
    pixel(draw, 24, 32, STEEL)
    rect(draw, (9, 34, 24, 34), CONTACT)
    return image


def font(size: int) -> ImageFont.ImageFont:
    for path in (Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/segoeui.ttf")):
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def montage(approved: Image.Image, v1: Image.Image, v2: Image.Image) -> Image.Image:
    scale = 8
    result = Image.new("RGBA", (920, 470), (237, 232, 218, 255))
    draw = ImageDraw.Draw(result)
    draw.text((24, 18), "Bedside cabinet art pilot — approved / V1 / V2", font=font(24), fill=INK)
    draw.text((24, 52), "Native pixels enlarged 8x; all views keep the same logical ID and 1x1 footprint", font=font(16), fill=INK_2)
    items = [("APPROVED", approved), ("V1 GEOMETRY", v1), ("V2 ART PILOT", v2)]
    centers = [155, 450, 745]
    floor_y = 422
    for (label, image), center in zip(items, centers):
        draw.text((center - 70, 84), label, font=font(16), fill=STEEL_DARK)
        enlarged = image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)
        result.alpha_composite(enlarged, (center - enlarged.width // 2, floor_y - enlarged.height))
        draw.line((center - 5, floor_y, center + 5, floor_y), fill=(218, 164, 66, 255), width=2)
        draw.line((center, floor_y - 5, center, floor_y + 5), fill=(218, 164, 66, 255), width=2)
    draw.line((20, floor_y + 8, 900, floor_y + 8), fill=INK_2, width=2)
    draw.text((24, 444), "V2: hard alpha, 13-color family palette, asymmetric light, recessed hardware, no broad side face", font=font(14), fill=INK_2)
    return result


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    assert digest(APPROVED) == APPROVED_SHA256
    assert digest(V1) == V1_SHA256
    approved_copy = OUT / "bedside_cabinet_01_approved.png"
    v1_copy = OUT / "bedside_cabinet_01_v1_geometry.png"
    shutil.copyfile(APPROVED, approved_copy)
    shutil.copyfile(V1, v1_copy)
    v2 = cabinet_v2()
    assert v2.size == (34, 36)
    assert v2.getbbox() == (3, 3, 31, 35)
    assert all(a in (0, 255) for a in v2.getchannel("A").get_flattened_data())
    palette = {p for p in v2.get_flattened_data() if p[3]}
    assert palette == {INK, INK_2, CONTACT, IVORY_HI, IVORY, IVORY_MID, IVORY_SHADE, IVORY_DEEP, STEEL_HI, STEEL, STEEL_DARK, TEAL_HI, TEAL}
    candidate = OUT / "bedside_cabinet_01_art_candidate_v2.png"
    v2.save(candidate)
    montage(Image.open(APPROVED).convert("RGBA"), Image.open(V1).convert("RGBA"), v2).save(OUT / "bedside_cabinet_art_review.png")
    mapping = {
        "status": "needs_human_review",
        "logical_id": "bedside_cabinet_01",
        "scope": "reference-only V2 art pilot; production and approval unchanged",
        "approved": {"path": APPROVED.relative_to(ROOT).as_posix(), "sha256": digest(APPROVED)},
        "v1_geometry_reference": {"path": V1.relative_to(ROOT).as_posix(), "sha256": digest(V1), "status": "rejected_as_art_baseline"},
        "candidate": {
            "path": candidate.relative_to(ROOT).as_posix(),
            "sha256": digest(candidate),
            "dimensions": list(v2.size),
            "alpha_bbox": list(v2.getbbox()),
            "opaque_palette_size": len(palette),
            "partial_alpha_pixels": 0,
            "logical_footprint_tiles": [1, 1],
            "anchor": "bottom_center",
        },
        "approval_status_changed": False,
    }
    (OUT / "mapping.json").write_text(json.dumps(mapping, indent=2) + "\n", encoding="utf-8")
    print("BEDSIDE_CABINET_V2_BUILD_PASS: native art pilot; 13 opaque colors; hard alpha; approved and V1 hashes locked")


if __name__ == "__main__":
    main()
