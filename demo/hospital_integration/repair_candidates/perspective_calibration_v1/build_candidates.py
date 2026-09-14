from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
TRANSPARENT = (0, 0, 0, 0)
INK = (24, 35, 49, 255)
INK_2 = (39, 55, 70, 255)
IVORY_HI = (250, 245, 235, 255)
IVORY = (239, 232, 218, 255)
IVORY_SHADE = (211, 204, 191, 255)
STEEL_HI = (128, 157, 176, 255)
STEEL = (91, 123, 148, 255)
STEEL_DARK = (66, 91, 112, 255)
TEAL = (102, 159, 157, 255)
CONTACT = (17, 25, 35, 255)

SOURCES = {
    "reception_counter_straight_01": {
        "path": ROOT / "assets/reception/reception_counter_straight_01.png",
        "sha256": "f4fc1403163cfb4ea26e3ed8e86442c4e3ad1d29a12d41badeb2c805b2a7d213",
        "footprint": [2, 1],
    },
    "bedside_cabinet_01": {
        "path": ROOT / "assets/patient_rooms/bedside_cabinet_01.png",
        "sha256": "62c5decd09bbbb5a0d18cb1b0e16178e522b9f3da47db4f38a6bb4f052c82993",
        "footprint": [1, 1],
    },
    "medical_cart_base_01": {
        "path": ROOT / "assets/examination/medical_cart_base_01.png",
        "sha256": "be0f578478b9334433e81d56d0749460a5f2ec24cfd2cfe21faa3c4daefabfd8",
        "footprint": [1, 1],
    },
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canvas(size: tuple[int, int]) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGBA", size, TRANSPARENT)
    return image, ImageDraw.Draw(image)


def rect(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], color: tuple[int, int, int, int]) -> None:
    draw.rectangle(box, fill=color)


def build_counter() -> Image.Image:
    image, draw = canvas((72, 38))
    # Two-tile rectangular top: rear and front edges stay parallel and the
    # shallow depth moves straight upward, with no rendered right-side plane.
    rect(draw, (5, 4, 66, 5), INK)
    rect(draw, (4, 6, 67, 13), INK_2)
    rect(draw, (6, 6, 65, 7), IVORY_HI)
    rect(draw, (6, 8, 65, 11), IVORY)
    rect(draw, (5, 12, 66, 13), IVORY_SHADE)
    # Straight modular front face.
    rect(draw, (4, 14, 67, 35), INK)
    rect(draw, (6, 15, 65, 33), STEEL_DARK)
    rect(draw, (6, 15, 65, 17), STEEL_HI)
    rect(draw, (6, 18, 65, 31), STEEL)
    rect(draw, (6, 30, 65, 33), STEEL_DARK)
    rect(draw, (9, 18, 10, 29), TEAL)
    rect(draw, (61, 18, 62, 29), INK_2)
    rect(draw, (7, 34, 64, 35), INK_2)
    rect(draw, (10, 36, 61, 36), CONTACT)
    return image


def build_cabinet() -> Image.Image:
    image, draw = canvas((32, 36))
    # Compact 1x1 top; the rear edge is directly above the front edge.
    rect(draw, (7, 4, 24, 5), INK)
    rect(draw, (5, 6, 26, 12), INK_2)
    rect(draw, (7, 6, 24, 7), IVORY_HI)
    rect(draw, (7, 8, 24, 10), IVORY)
    rect(draw, (6, 11, 25, 12), IVORY_SHADE)
    # One drawer and one cupboard retain the original bedside function.
    rect(draw, (6, 13, 25, 31), INK)
    rect(draw, (8, 14, 23, 19), STEEL)
    rect(draw, (8, 14, 23, 15), STEEL_HI)
    rect(draw, (13, 17, 18, 18), INK_2)
    rect(draw, (8, 21, 23, 29), IVORY)
    rect(draw, (8, 21, 23, 22), IVORY_HI)
    rect(draw, (10, 24, 11, 26), INK_2)
    rect(draw, (8, 30, 23, 31), IVORY_SHADE)
    rect(draw, (8, 32, 10, 33), INK_2)
    rect(draw, (21, 32, 23, 33), INK_2)
    rect(draw, (9, 34, 22, 34), CONTACT)
    return image


def build_cart() -> Image.Image:
    image, draw = canvas((36, 42))
    # Raised tray differentiates the cart from the cabinet while keeping the
    # same front-facing rectangular projection.
    rect(draw, (8, 3, 27, 4), INK)
    rect(draw, (6, 5, 29, 12), INK_2)
    rect(draw, (8, 5, 27, 6), IVORY_HI)
    rect(draw, (8, 7, 27, 10), IVORY)
    rect(draw, (7, 11, 28, 12), IVORY_SHADE)
    rect(draw, (5, 13, 30, 16), INK)
    rect(draw, (7, 13, 28, 14), IVORY_HI)
    rect(draw, (7, 15, 28, 16), IVORY_SHADE)
    # Three drawer bands, with square corner rails and no diagonal side face.
    rect(draw, (6, 17, 29, 35), INK)
    rect(draw, (8, 18, 27, 22), STEEL)
    rect(draw, (8, 18, 27, 19), STEEL_HI)
    rect(draw, (14, 20, 21, 21), INK_2)
    rect(draw, (8, 24, 27, 28), IVORY)
    rect(draw, (8, 24, 27, 25), IVORY_HI)
    rect(draw, (14, 26, 21, 27), INK_2)
    rect(draw, (8, 30, 27, 34), STEEL)
    rect(draw, (8, 30, 27, 31), STEEL_HI)
    rect(draw, (14, 32, 21, 33), INK_2)
    rect(draw, (7, 35, 28, 36), INK_2)
    # Small caster stems and contact wheels.
    rect(draw, (9, 37, 11, 38), INK_2)
    rect(draw, (24, 37, 26, 38), INK_2)
    rect(draw, (7, 39, 12, 40), INK)
    rect(draw, (23, 39, 28, 40), INK)
    rect(draw, (8, 39, 10, 39), STEEL_HI)
    rect(draw, (24, 39, 26, 39), STEEL_HI)
    return image


BUILDERS = {
    "reception_counter_straight_01": build_counter,
    "bedside_cabinet_01": build_cabinet,
    "medical_cart_base_01": build_cart,
}


def opaque_colors(image: Image.Image) -> set[tuple[int, int, int, int]]:
    return {pixel for pixel in image.get_flattened_data() if pixel[3]}


def font(size: int) -> ImageFont.ImageFont:
    candidates = [Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/segoeui.ttf")]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def compose_review(candidates: dict[str, Image.Image]) -> Image.Image:
    scale = 5
    review = Image.new("RGBA", (1060, 660), (237, 232, 218, 255))
    draw = ImageDraw.Draw(review)
    title = font(24)
    body = font(17)
    small = font(14)
    draw.text((24, 18), "Perspective calibration V1 — approved vs candidate", font=title, fill=INK)
    draw.text((24, 52), "Native sprites enlarged 5x with nearest-neighbor; identical logical IDs", font=body, fill=INK_2)
    columns = [30, 420, 700]
    ids = list(BUILDERS)
    for x, asset_id in zip(columns, ids):
        source = Image.open(SOURCES[asset_id]["path"]).convert("RGBA")
        candidate = candidates[asset_id]
        draw.text((x, 88), asset_id.replace("_01", ""), font=small, fill=INK)
        draw.text((x, 116), "APPROVED", font=small, fill=STEEL_DARK)
        before = source.resize((source.width * scale, source.height * scale), Image.Resampling.NEAREST)
        review.alpha_composite(before, (x, 140))
        draw.text((x, 396), "CANDIDATE", font=small, fill=STEEL_DARK)
        after = candidate.resize((candidate.width * scale, candidate.height * scale), Image.Resampling.NEAREST)
        review.alpha_composite(after, (x, 420))
    draw.line((20, 378, 1040, 378), fill=INK_2, width=2)
    draw.text((24, 635), "Candidate pixels: hard alpha, 10-color family palette, no right-side mass", font=small, fill=INK_2)
    return review


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    candidates: dict[str, Image.Image] = {}
    mapping = {
        "status": "needs_human_review",
        "scope": "reference-only perspective calibration; production and approvals unchanged",
        "camera": "rectangular-grid RPG oblique; depth recedes upward; no default right-side face",
        "assets": [],
    }
    for asset_id, builder in BUILDERS.items():
        source = SOURCES[asset_id]["path"]
        assert digest(source) == SOURCES[asset_id]["sha256"], f"approved source changed: {asset_id}"
        approved_copy = OUT / f"{asset_id}_approved.png"
        shutil.copyfile(source, approved_copy)
        candidate = builder()
        assert candidate.getbbox() is not None
        assert all(alpha in (0, 255) for alpha in candidate.getchannel("A").get_flattened_data())
        assert opaque_colors(candidate).issubset({INK, INK_2, IVORY_HI, IVORY, IVORY_SHADE, STEEL_HI, STEEL, STEEL_DARK, TEAL, CONTACT})
        candidate_path = OUT / f"{asset_id}_perspective_candidate.png"
        candidate.save(candidate_path)
        candidates[asset_id] = candidate
        mapping["assets"].append({
            "logical_id": asset_id,
            "approved_path": source.relative_to(ROOT).as_posix(),
            "approved_sha256": digest(source),
            "candidate_path": candidate_path.relative_to(ROOT).as_posix(),
            "candidate_sha256": digest(candidate_path),
            "candidate_dimensions": list(candidate.size),
            "candidate_alpha_bbox": list(candidate.getbbox()),
            "logical_footprint_tiles": SOURCES[asset_id]["footprint"],
            "anchor": "bottom_center",
            "approval_status_changed": False,
        })
    review = compose_review(candidates)
    review.save(OUT / "perspective_calibration_review.png")
    (OUT / "mapping.json").write_text(json.dumps(mapping, indent=2) + "\n", encoding="utf-8")
    print("PERSPECTIVE_CALIBRATION_BUILD_PASS: 3 candidates; hard alpha; controlled palette; approved sources unchanged")


if __name__ == "__main__":
    main()
