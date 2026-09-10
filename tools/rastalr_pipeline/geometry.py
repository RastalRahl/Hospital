"""Opt-in measured Architecture QA. Rectangles are [left, top, right, bottom).

Existing reports and production validation retain their historical semantics.
Callers supply expectations; observations must come from pixels or placements.
"""
from __future__ import annotations

from PIL import Image

RECTANGLE_CONVENTION = "[left, top, right, bottom)"


def rectangle_pixels(rect):
    left, top, right, bottom = rect
    if not all(type(v) is int for v in rect) or right <= left or bottom <= top:
        raise ValueError("Rectangle must contain integer, nonempty half-open bounds")
    return ((x, y) for y in range(top, bottom) for x in range(left, right))


def evidence(expected, observed, method, *, units="native_px"):
    """An equality assertion with explicit provenance, never a literal PASS."""
    return {"expected": expected, "observed": observed, "method": method,
            "units": units, "pass": expected == observed}


def alpha_region(image, rect, *, minimum, maximum):
    alpha = image.convert("RGBA").getchannel("A")
    samples = [alpha.getpixel(p) if 0 <= p[0] < image.width and 0 <= p[1] < image.height else -1
               for p in rectangle_pixels(rect)]
    bad = sum(not minimum <= value <= maximum for value in samples)
    return {"expected": {"rectangle": list(rect), "alpha_range_inclusive": [minimum, maximum], "violations": 0},
            "observed": {"alpha_min": min(samples), "alpha_max": max(samples), "violations": bad,
                         "sample_count": len(samples)},
            "method": "Read every alpha pixel in the required region; out-of-canvas is a violation",
            "pass": bad == 0}


def anchored_component(image, component, expected_origin, observed_origin):
    """Validate recorded placement AND exact rendered component pixels."""
    x, y = expected_origin
    actual = image.crop((x, y, x + component.width, y + component.height))
    # Transparent RGB is not rendered and can differ after alpha compositing.
    mismatches = sum(a[3] != b[3] or (b[3] > 0 and a[:3] != b[:3])
                     for a, b in zip(actual.convert("RGBA").get_flattened_data(),
                                     component.convert("RGBA").get_flattened_data()))
    checks = {"origin": evidence(list(expected_origin), list(observed_origin), "Read placement metadata"),
              "pixel_mismatches": evidence(0, mismatches, "Compare rendered crop to unchanged component", units="pixels")}
    return {"checks": checks, "pass": all(c["pass"] for c in checks.values())}


def horizontal_join(left, right, left_origin, right_origin, contact_y):
    """Check abutting carrier coordinates and both required contact strips."""
    expected = [left_origin[0] + left.width, left_origin[1]]
    checks = {"placement": evidence(expected, list(right_origin), "Read actual carrier placements"),
              "left_contact": alpha_region(left, [left.width-1, contact_y[0], left.width, contact_y[1]], minimum=255, maximum=255),
              "right_contact": alpha_region(right, [0, contact_y[0], 1, contact_y[1]], minimum=255, maximum=255)}
    return {"checks": checks, "pass": all(c["pass"] for c in checks.values())}
