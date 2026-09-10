from PIL import Image
import pytest

from rastalr_pipeline.core import (
    build_filename, downscale_nearest, normalize_architecture_grid_image, normalize_image,
    transparent_bounds, validate_architecture_grid_image, validate_image,
)


def test_filename_omits_default_orientation_and_clean_state():
    assert build_filename("hospital bed standard", 1) == "hospital_bed_standard_01.png"
    assert build_filename("wall door", 2, "north", "open") == "wall_door_north_open_02.png"


def test_filename_requires_positive_integer_variant():
    with pytest.raises(ValueError):
        build_filename("bed", 0)


def test_transparent_bounds_and_normalization_add_exact_padding():
    source = Image.new("RGBA", (10, 8), (0, 0, 0, 0))
    source.putpixel((2, 1), (10, 20, 30, 255))
    source.putpixel((6, 5), (40, 50, 60, 255))
    assert transparent_bounds(source) == (2, 1, 7, 6)
    normalized = normalize_image(source, padding=2)
    assert normalized.size == (9, 9)
    assert transparent_bounds(normalized) == (2, 2, 7, 7)
    assert normalized.getpixel((2, 2)) == (10, 20, 30, 255)


def test_source_scale_one_keeps_native_trimmed_pixels_unchanged():
    source = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    source.putpixel((2, 2), (104, 162, 154, 255))
    normalized = normalize_image(source, padding=1, source_scale=1)
    assert normalized.size == (3, 3)
    assert normalized.getpixel((1, 1)) == (104, 162, 154, 255)


def test_source_scale_eight_uses_nearest_neighbor_and_native_padding():
    source = Image.new("RGBA", (20, 12), (0, 0, 0, 0))
    for y in range(2, 10):
        for x in range(2, 10):
            source.putpixel((x, y), (201, 91, 85, 255))
        for x in range(10, 18):
            source.putpixel((x, y), (104, 162, 154, 255))
    scaled = downscale_nearest(source.crop((2, 2, 18, 10)), 8)
    assert scaled.size == (2, 1)
    assert [scaled.getpixel((x, 0)) for x in range(2)] == [(201, 91, 85, 255), (104, 162, 154, 255)]
    normalized = normalize_image(source, padding=2, source_scale=8)
    assert normalized.size == (6, 5)
    assert [normalized.getpixel((x, 2)) for x in (2, 3)] == [(201, 91, 85, 255), (104, 162, 154, 255)]


@pytest.mark.parametrize("scale", [0, -1, 1.5])
def test_invalid_source_scale_is_rejected(scale):
    with pytest.raises(ValueError, match="source_scale"):
        normalize_image(Image.new("RGBA", (4, 4), (255, 255, 255, 255)), source_scale=scale)


def test_normalize_rejects_fully_transparent_image():
    with pytest.raises(ValueError, match="no non-transparent"):
        normalize_image(Image.new("RGBA", (4, 4), (0, 0, 0, 0)))


def test_validation_flags_opaque_and_edge_touching_source():
    source = Image.new("RGBA", (6, 6), (30, 40, 50, 255))
    report = validate_image(source, filename="bad name.png")
    codes = {issue["code"] for issue in report["issues"]}
    assert {"missing_transparency", "opaque_border", "touching_canvas_edge", "filename_schema"} <= codes
    assert report["status"] == "fail"


def test_validation_passes_safely_padded_sprite():
    sprite = Image.new("RGBA", (7, 7), (0, 0, 0, 0))
    for y in range(2, 6):
        for x in range(2, 6):
            sprite.putpixel((x, y), (242, 235, 221, 255))
    report = validate_image(sprite, filename="iv_stand_dual_01.png")
    assert report["status"] == "pass"
    assert report["alpha"]["has_transparency"] is True


def test_validation_flags_implausibly_large_native_canvas_for_footprint():
    sprite = Image.new("RGBA", (193, 20), (0, 0, 0, 0))
    sprite.putpixel((10, 10), (242, 235, 221, 255))
    report = validate_image(sprite, native_grid=32, footprint_width_tiles=1, footprint_height_tiles=1)
    assert "unusually_large_native_canvas" in {issue["code"] for issue in report["issues"]}


def test_architecture_grid_normalization_preserves_exact_opaque_component_box():
    source = Image.new("RGBA", (256, 416), (32, 48, 64, 255))
    for y in range(8, 16):
        for x in range(8, 16):
            source.putpixel((x, y), (104, 162, 154, 255))
    native = normalize_architecture_grid_image(
        source, source_scale=8, expected_native_dimensions=[32, 52],
    )
    assert native.size == (32, 52)
    assert native.getpixel((1, 1)) == (104, 162, 154, 255)
    report = validate_architecture_grid_image(native, expected_dimensions=[32, 52], filename="hospital_wall_back_straight_01.png")
    assert report["status"] == "pass"
    assert report["connection_edges_covered"] is True
    assert report["alpha"]["has_transparency"] is False
