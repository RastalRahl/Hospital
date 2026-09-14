from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
APPROVED = ROOT / "assets/patient_rooms/bedside_cabinet_01.png"
V3 = ROOT / "demo/hospital_integration/repair_candidates/perspective_cabinet_v3/bedside_cabinet_01_art_candidate_v3.png"
LOCKED_HASHES = {
    APPROVED: "62c5decd09bbbb5a0d18cb1b0e16178e522b9f3da47db4f38a6bb4f052c82993",
    V3: "a8dc0dca4766fe6caf02f8d0323fb444224ac66c22fd352d2e75bb3b52d7941a",
}

T = (0, 0, 0, 0)
INK = (24, 35, 49, 255)
LINE = (52, 70, 86, 255)
CONTACT = (17, 25, 35, 255)
IVORY_HI = (250, 245, 235, 255)
IVORY = (239, 232, 218, 255)
IVORY_WARM = (229, 221, 204, 255)
IVORY_SHADE = (193, 188, 178, 255)
STEEL_HI = (153, 183, 191, 255)
STEEL = (104, 139, 158, 255)
STEEL_DARK = (65, 88, 107, 255)
TEAL_HI = (139, 187, 179, 255)
TEAL = (91, 151, 148, 255)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rect(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], color: tuple[int, int, int, int]) -> None:
    draw.rectangle(box, fill=color)


def px(draw: ImageDraw.ImageDraw, x: int, y: int, color: tuple[int, int, int, int]) -> None:
    draw.point((x, y), fill=color)


def cabinet_v4() -> Image.Image:
    image = Image.new("RGBA", (32, 36), T)
    draw = ImageDraw.Draw(image)

    # One continuous molded work surface. Its stepped corners form a compact
    # manufactured silhouette; there is no separate crown or front slab.
    rect(draw, (6, 3, 25, 3), INK)
    rect(draw, (4, 4, 27, 4), INK)
    rect(draw, (3, 5, 28, 8), INK)
    rect(draw, (2, 7, 29, 9), INK)
    rect(draw, (6, 4, 25, 4), IVORY_HI)
    rect(draw, (4, 5, 27, 7), IVORY)
    rect(draw, (3, 7, 28, 8), IVORY_WARM)
    rect(draw, (3, 9, 28, 9), IVORY_SHADE)
    rect(draw, (5, 5, 18, 5), IVORY_HI)
    px(draw, 4, 6, IVORY_HI)
    px(draw, 27, 7, IVORY_SHADE)

    # The cabinet body tucks directly under the work surface. One-pixel shoulder
    # steps and clipped lower corners keep the silhouette from becoming a box.
    rect(draw, (4, 10, 27, 29), INK)
    rect(draw, (5, 10, 26, 29), IVORY_WARM)
    rect(draw, (5, 10, 5, 28), IVORY_HI)
    rect(draw, (26, 11, 26, 28), IVORY_SHADE)

    # Smaller steel drawer: a quiet band instead of the dominant blue block in V3.
    rect(draw, (7, 12, 24, 16), LINE)
    rect(draw, (8, 12, 23, 15), STEEL)
    rect(draw, (8, 12, 20, 12), STEEL_HI)
    rect(draw, (8, 13, 8, 14), STEEL_HI)
    rect(draw, (9, 15, 23, 15), STEEL_DARK)
    rect(draw, (14, 13, 18, 14), LINE)
    rect(draw, (15, 13, 17, 13), IVORY_HI)

    # Large warm door plane with a few material clusters. The right recess and
    # bottom shadow imply construction without outlining a panel inside a panel.
    rect(draw, (7, 18, 24, 28), IVORY)
    rect(draw, (7, 18, 21, 18), IVORY_HI)
    rect(draw, (7, 19, 7, 25), IVORY_HI)
    rect(draw, (8, 27, 22, 28), IVORY_WARM)
    rect(draw, (23, 19, 24, 27), IVORY_SHADE)
    rect(draw, (9, 21, 10, 24), TEAL)
    rect(draw, (9, 21, 9, 22), TEAL_HI)
    px(draw, 11, 19, IVORY_HI)
    px(draw, 22, 26, IVORY_SHADE)

    # Narrow undercarriage and compact hospital casters give the base a distinct,
    # useful silhouette while keeping the contact shadow local.
    rect(draw, (5, 29, 26, 30), INK)
    rect(draw, (7, 29, 24, 29), LINE)
    rect(draw, (8, 30, 23, 30), IVORY_SHADE)
    rect(draw, (6, 31, 9, 31), LINE)
    rect(draw, (22, 31, 25, 31), LINE)
    rect(draw, (5, 32, 9, 33), INK)
    rect(draw, (22, 32, 26, 33), INK)
    rect(draw, (6, 32, 8, 32), STEEL_HI)
    rect(draw, (23, 32, 25, 32), STEEL)
    px(draw, 7, 33, STEEL_DARK)
    px(draw, 24, 33, STEEL_DARK)
    rect(draw, (9, 34, 22, 34), CONTACT)
    return image


def font(size: int) -> ImageFont.ImageFont:
    for path in (Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/segoeui.ttf")):
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def montage(approved: Image.Image, v3: Image.Image, v4: Image.Image) -> Image.Image:
    scale = 8
    result = Image.new("RGBA", (930, 445), (237, 232, 218, 255))
    draw = ImageDraw.Draw(result)
    draw.text((24, 16), "Bedside cabinet refinement — approved / V3 / V4", font=font(24), fill=INK)
    draw.text((24, 48), "Native pixels enlarged 8x; common 1x1 footprint and bottom-center anchor", font=font(16), fill=LINE)
    centers = [155, 465, 775]
    floor_y = 398
    for (label, source), center in zip([("APPROVED", approved), ("V3 REJECTED", v3), ("V4 ART", v4)], centers):
        draw.text((center - 72, 78), label, font=font(16), fill=STEEL_DARK)
        enlarged = source.resize((source.width * scale, source.height * scale), Image.Resampling.NEAREST)
        result.alpha_composite(enlarged, (center - enlarged.width // 2, floor_y - enlarged.height))
        draw.line((center - 5, floor_y, center + 5, floor_y), fill=(218, 164, 66, 255), width=2)
        draw.line((center, floor_y - 5, center, floor_y + 5), fill=(218, 164, 66, 255), width=2)
    draw.line((20, floor_y + 8, 910, floor_y + 8), fill=LINE, width=2)
    draw.text((24, 420), "V4: single molded top, smaller drawer, warm door plane, compact casters", font=font(14), fill=LINE)
    return result


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for path, expected in LOCKED_HASHES.items():
        assert digest(path) == expected
    approved_copy = OUT / "bedside_cabinet_01_approved.png"
    v3_copy = OUT / "bedside_cabinet_01_v3_art.png"
    shutil.copyfile(APPROVED, approved_copy)
    shutil.copyfile(V3, v3_copy)
    v4 = cabinet_v4()
    assert v4.size == (32, 36)
    assert v4.getbbox() == (2, 3, 30, 35)
    assert all(alpha in (0, 255) for alpha in v4.getchannel("A").get_flattened_data())
    palette = {color for color in v4.get_flattened_data() if color[3]}
    expected_palette = {INK, LINE, CONTACT, IVORY_HI, IVORY, IVORY_WARM, IVORY_SHADE, STEEL_HI, STEEL, STEEL_DARK, TEAL_HI, TEAL}
    assert palette == expected_palette
    candidate = OUT / "bedside_cabinet_01_art_candidate_v4.png"
    v4.save(candidate)
    montage(Image.open(approved_copy).convert("RGBA"), Image.open(v3_copy).convert("RGBA"), v4).save(OUT / "bedside_cabinet_v4_review.png")
    mapping = {
        "status": "needs_human_review",
        "logical_id": "bedside_cabinet_01",
        "scope": "reference-only V4 art pilot; production and approval unchanged",
        "approved": {"path": APPROVED.relative_to(ROOT).as_posix(), "sha256": digest(APPROVED)},
        "v3": {"path": V3.relative_to(ROOT).as_posix(), "sha256": digest(V3), "status": "rejected_as_release_baseline"},
        "candidate": {
            "path": candidate.relative_to(ROOT).as_posix(),
            "sha256": digest(candidate),
            "dimensions": list(v4.size),
            "alpha_bbox": list(v4.getbbox()),
            "opaque_palette_size": len(palette),
            "partial_alpha_pixels": 0,
            "logical_footprint_tiles": [1, 1],
            "anchor": "bottom_center",
        },
        "approval_status_changed": False,
    }
    (OUT / "mapping.json").write_text(json.dumps(mapping, indent=2) + "\n", encoding="utf-8")
    print("BEDSIDE_CABINET_V4_BUILD_PASS: 32x36 native sprite; 12 opaque colors; hard alpha; inputs locked")


if __name__ == "__main__":
    main()
