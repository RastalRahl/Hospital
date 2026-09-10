"""Reference-only geometry gate for the failed C3 glazed-door candidate.

This records validation evidence only.  It intentionally does not extract a door or
construct a room: C3's generated geometry is incompatible with the canonical grid.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "references" / "architecture" / "master_validation_C3_v1"
SOURCES = VALIDATION / "sources"
ARTIFACTS = VALIDATION / "artifacts"
MASTER = SOURCES / "rastalr_architecture_master_C3_glazed_single_door_closed_v1.png"
SCAFFOLD = SOURCES / "architecture_master_C3_glazed_single_door_closed_clean_scaffold.png"
SPEC = SOURCES / "architecture_master_C3_glazed_single_door_closed_spec.json"

EXPECTED_X = (128, 384, 640, 896, 1152, 1408)
EXPECTED_Y = (416, 672, 768, 928)
OBSERVED_X = (80, 355, 630, 905, 1180, 1455)
OBSERVED_Y = (580, 665, 753, 819)
EXPECTED_DOOR = (640, 0, 896, 416)
OBSERVED_DOOR = (652, 235, 883, 580)
EXPECTED_GLAZING = (704, 120, 832, 320)
OBSERVED_GLAZING = (703, 278, 835, 515)


def alignment(master: Image.Image, scaffold: Image.Image) -> Image.Image:
    base = master.convert("RGBA")
    faded = scaffold.convert("RGBA")
    faded.putalpha(35)
    base = Image.alpha_composite(base, faded)
    draw = ImageDraw.Draw(base)
    # Canonical geometry: yellow outer structure, magenta grid, cyan expected door.
    draw.rectangle((128, 0, 1408, 928), outline=(255, 225, 0, 255), width=3)
    for x in EXPECTED_X:
        draw.line((x, 0, x, 928), fill=(255, 0, 255, 255), width=2)
    for y in EXPECTED_Y:
        draw.line((128, y, 1408, y), fill=(255, 0, 255, 255), width=2)
    draw.rectangle(EXPECTED_DOOR, outline=(0, 235, 255, 255), width=3)
    # Measured generated landmarks: orange.
    for x in OBSERVED_X:
        draw.line((x, 205, x, 819), fill=(255, 118, 45, 255), width=2)
    for y in OBSERVED_Y:
        draw.line((25, y, 1511, y), fill=(255, 118, 45, 255), width=2)
    draw.rectangle(OBSERVED_DOOR, outline=(255, 118, 45, 255), width=3)
    draw.rectangle(OBSERVED_GLAZING, outline=(100, 255, 180, 255), width=2)
    return base


def diagnostic(master: Image.Image, scaffold: Image.Image) -> Image.Image:
    """Side-by-side geometry evidence: scaffold left, candidate right."""
    left = scaffold.convert("RGBA")
    right = master.convert("RGBA")
    out = Image.new("RGBA", (3072, 1080), (14, 22, 31, 255))
    out.alpha_composite(left, (0, 42))
    out.alpha_composite(right, (1536, 42))
    draw = ImageDraw.Draw(out)
    font = ImageFont.load_default()
    draw.text((12, 12), "Canonical C3 scaffold: 128..1408 x 0..928", fill="white", font=font)
    draw.text((1548, 12), "Generated C3: observed wall 80..1455 x 205..819", fill="white", font=font)
    return out


def main() -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    master = Image.open(MASTER)
    scaffold = Image.open(SCAFFOLD)
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    if master.size != (1536, 1024) or scaffold.size != master.size:
        raise ValueError("C3 source/scaffold canvas must be 1536 x 1024")
    if tuple(spec["opening_source_px"]) != EXPECTED_DOOR:
        raise ValueError("C3 spec opening does not match canonical geometry")
    alignment(master, scaffold).save(ARTIFACTS / "architecture_C3_scaffold_alignment.png")
    diagnostic(master, scaffold).save(ARTIFACTS / "architecture_C3_geometry_diagnostic.png")

    report = {
        "validation_id": "architecture_master_C3_v1",
        "purpose": "reference-only C3 geometry validation",
        "production_metadata_modified": False,
        "source": {"master": str(MASTER.relative_to(ROOT)).replace("\\", "/"), "dimensions": list(master.size), "mode": master.mode, "source_scale": 8},
        "expected": {"vertical_boundaries": list(EXPECTED_X), "horizontal_boundaries": list(EXPECTED_Y), "doorway": list(EXPECTED_DOOR), "glazing": list(EXPECTED_GLAZING)},
        "observed": {"wall_run_x": [80, 1455], "wall_vertical_boundaries": list(OBSERVED_X), "horizontal_landmarks": list(OBSERVED_Y), "door_frame": list(OBSERVED_DOOR), "glazing": list(OBSERVED_GLAZING)},
        "deviation_source_px": {
            "wall_run": {"left": -48, "right": 47},
            "vertical_boundaries": {str(expected): observed - expected for expected, observed in zip(EXPECTED_X, OBSERVED_X)},
            "horizontal_boundaries": {"wall_floor": 164, "internal_floor": -7, "front_cutaway": -15, "floor_bottom": -109},
            "door_frame": {"left": 12, "right": -13, "top": 235, "threshold": 164},
            "glazing": {"left": -1, "right": 3, "top": 158, "bottom": 195},
        },
        "registration_assessment": {
            "horizontal": "generated wall cells are approximately 275 px rather than 256 px; this is a uniform scale/origin mismatch, not usable without warping",
            "vertical": "non-affine: the cap starts around y=205, wall/floor is y=580, then interior and cutaway landmarks contract to 665, 753, and 819",
            "result": "fail: generated material cannot be registered to canonical Geometry safely",
        },
        "extraction": {"attempted": False, "reason": "Failure rule: significant structural/non-affine mismatch; arbitrary crop, warp, and reconstruction are prohibited."},
        "qa": {"candidate_alpha_extrema": list(master.getchannel("A").getextrema()), "candidate_alpha_bbox": list(master.getchannel("A").getbbox()), "clipping_or_debris_review": "not applicable to a rejected pre-extraction geometry candidate"},
        "recommendation": "REGENERATE MASTER",
    }
    (VALIDATION / "architecture_C3_validation_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown = """# Architecture Master C3 Validation v1\n\n## Recommendation: REGENERATE MASTER\n\nC3 cannot be deterministically extracted. Its generated room is not registered to the canonical 32 px Architecture grid. This validation stopped before temporary extraction or reconstruction, as required.\n\n## Measured mismatch\n\n| Landmark | Canonical | Observed candidate | Deviation |\n| --- | --- | --- | --- |\n| Wall run left/right | 128 / 1408 | 80 / 1455 | -48 / +47 px |\n| Five x boundaries | 128, 384, 640, 896, 1152, 1408 | 80, 355, 630, 905, 1180, 1455 | -48, -29, -10, +9, +28, +47 px |\n| Wall/floor | 416 | 580 | +164 px |\n| Internal floor | 672 | 665 | -7 px |\n| Front-cutaway top | 768 | 753 | -15 px |\n| Floor/front bottom | 928 | 819 | -109 px |\n| Door frame | 640,0..896,416 | 652,235..883,580 | +12/-13 x; +235/+164 y |\n| Glazing | 704,120..832,320 | 703,278..835,515 | -1/+3 x; +158/+195 y |\n\nThe horizontal run is approximately 275 px per generated cell rather than 256 px. More importantly, vertical landmarks are not related by one uniform transform: the entire wall is dropped, while the lower floor/front region is compressed. The door frame and glazing are therefore not merely decorative insets.\n\n## Required correction\n\nRegenerate C3 using the supplied clean scaffold/overlay without a vignette, perspective floor expansion, or arbitrary wall/floor scaling. Preserve the exact canonical outer run, opening `640..896 × 0..416`, floor bounds, and specified glazing rectangle.\n\n## Scope\n\nAll files remain reference-only. No Batch 12 metadata, temporary candidate module, reconstruction, manifest, catalog, or approved Architecture asset was changed.\n"""
    (VALIDATION / "architecture_C3_validation_report.md").write_text(markdown, encoding="utf-8")
    print(json.dumps({"recommendation": "REGENERATE MASTER", "report": str(VALIDATION / "architecture_C3_validation_report.json")}, indent=2))


if __name__ == "__main__":
    main()
