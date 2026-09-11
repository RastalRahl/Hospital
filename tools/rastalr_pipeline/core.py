from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "metadata" / "manifest.json"
CATALOG_PATH = ROOT / "metadata" / "catalog.csv"
QA_JSON_PATH = ROOT / "metadata" / "qa_report.json"
QA_MD_PATH = ROOT / "metadata" / "qa_report.md"
QA_CSV_PATH = ROOT / "metadata" / "qa_report.csv"
CONTACT_SHEET_PATH = ROOT / "previews" / "contact_sheets" / "pilot_pending.png"
ARCHITECTURE_CONTACT_SHEET_PATH = ROOT / "previews" / "contact_sheets" / "architecture_foundation_batch_11.png"
ARCHITECTURE_RECONSTRUCTION_PATH = ROOT / "previews" / "architecture" / "architecture_foundation_batch_11_room_6x4.png"
REVIEW_BUNDLE_PATH = ROOT / "release" / "review_bundle_current.zip"
FILENAME_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*_\d{2}\.png$")
CATEGORIES = {
    "architecture", "reception", "patient_rooms", "examination", "icu", "surgery",
    "radiology", "laboratory", "pharmacy", "emergency", "exterior", "morgue", "staff",
    "cafeteria", "bathroom_utility", "signage_decor", "inventory_ui", "abandoned",
}


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def repo_path(path: str | Path) -> Path:
    path = Path(path)
    return path if path.is_absolute() else ROOT / path


def slug(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    if not value:
        raise ValueError("A filename field became empty after normalization.")
    return value


def build_filename(
    asset_type: str,
    variant: int | str = 1,
    orientation: str | None = None,
    state: str = "clean",
) -> str:
    """Build the stable commercial filename described in ASSET_CATALOG.md."""
    try:
        number = int(variant)
    except (TypeError, ValueError) as error:
        raise ValueError("variant must be an integer") from error
    if number < 1:
        raise ValueError("variant must be at least 1")
    pieces = [slug(asset_type)]
    if orientation and orientation not in {"default", "none"}:
        pieces.append(slug(orientation))
    if state and state != "clean":
        pieces.append(slug(state))
    return "_".join(pieces + [f"{number:02d}"]) + ".png"


def ensure_rgba(image: Image.Image) -> Image.Image:
    return image.convert("RGBA") if image.mode != "RGBA" else image.copy()


def transparent_bounds(image: Image.Image) -> tuple[int, int, int, int] | None:
    """Return alpha bounds in Pillow's (left, top, right, bottom) convention."""
    return ensure_rgba(image).getchannel("A").getbbox()


def validate_source_scale(source_scale: int) -> int:
    if isinstance(source_scale, bool) or not isinstance(source_scale, int) or source_scale < 1:
        raise ValueError("source_scale must be a positive integer.")
    return source_scale


def downscale_nearest(image: Image.Image, source_scale: int = 1) -> Image.Image:
    """Downscale an explicit working-scale source with no pixel interpolation."""
    source_scale = validate_source_scale(source_scale)
    rgba = ensure_rgba(image)
    if source_scale == 1:
        return rgba
    size = (
        max(1, (rgba.width + source_scale - 1) // source_scale),
        max(1, (rgba.height + source_scale - 1) // source_scale),
    )
    return rgba.resize(size, Image.Resampling.NEAREST)


def normalize_image(image: Image.Image, padding: int = 2, source_scale: int = 1) -> Image.Image:
    """Trim, explicitly nearest-neighbor downscale, re-trim, and add native padding."""
    if padding < 0:
        raise ValueError("padding cannot be negative")
    source_scale = validate_source_scale(source_scale)
    rgba = ensure_rgba(image)
    bounds = transparent_bounds(rgba)
    if bounds is None:
        raise ValueError("Image has no non-transparent pixels and cannot be normalized.")
    cropped = rgba.crop(bounds)
    scaled = downscale_nearest(cropped, source_scale)
    scaled_bounds = transparent_bounds(scaled)
    if scaled_bounds is None:
        raise ValueError("Downscaling removed all visible pixels and cannot be normalized.")
    cropped = scaled.crop(scaled_bounds)
    result = Image.new("RGBA", (cropped.width + padding * 2, cropped.height + padding * 2), (0, 0, 0, 0))
    result.alpha_composite(cropped, (padding, padding))
    return result


def normalize_architecture_grid_image(
    image: Image.Image,
    *,
    source_scale: int,
    expected_native_dimensions: Iterable[int],
) -> Image.Image:
    """Downscale a canonical architecture component without trim or padding.

    Architecture grid modules intentionally occupy their complete component box.
    Applying the ordinary prop normalizer would change connection coordinates by
    trimming edge pixels and adding safety padding, so this explicit mode keeps
    the validated source rectangle intact while still using nearest-neighbor
    conversion to native resolution.
    """
    dimensions = tuple(expected_native_dimensions)
    if len(dimensions) != 2 or not all(isinstance(value, int) and value > 0 for value in dimensions):
        raise ValueError("expected_native_dimensions must contain two positive integers.")
    scale = validate_source_scale(source_scale)
    rgba = ensure_rgba(image)
    expected_source = (dimensions[0] * scale, dimensions[1] * scale)
    if rgba.size != expected_source:
        raise ValueError(
            f"Architecture source crop must be exactly {expected_source[0]}x{expected_source[1]} px; got {rgba.width}x{rgba.height}."
        )
    native = rgba.resize(dimensions, Image.Resampling.NEAREST)
    if native.size != dimensions:  # Defensive guard against future normalization changes.
        raise ValueError("Architecture native dimensions changed during normalization.")
    return native


def validate_architecture_grid_image(
    image: Image.Image,
    *,
    expected_dimensions: Iterable[int],
    filename: str | None = None,
) -> dict[str, Any]:
    """Validate intentional full-box architecture modules without relaxing prop QA."""
    dimensions = tuple(expected_dimensions)
    rgba = ensure_rgba(image)
    alpha = rgba.getchannel("A")
    issues: list[dict[str, str]] = []
    if rgba.size != dimensions:
        issues.append({
            "code": "architecture_dimension_mismatch", "severity": "error",
            "message": f"Expected native dimensions {dimensions[0]}x{dimensions[1]}, got {rgba.width}x{rgba.height}.",
        })
    if rgba.mode != "RGBA":
        issues.append({"code": "architecture_not_rgba", "severity": "error", "message": "Architecture component is not RGBA."})
    transparent = sum(1 for value in alpha.get_flattened_data() if value == 0)
    if transparent:
        issues.append({
            "code": "architecture_alpha_gap", "severity": "error",
            "message": f"Architecture component has {transparent} transparent pixel(s); canonical connection box must be opaque.",
        })
    if filename and not FILENAME_RE.fullmatch(filename):
        issues.append({"code": "filename_schema", "severity": "error", "message": "Filename is not lowercase snake_case ending in _NN.png."})
    return {
        "dimensions": {"width": rgba.width, "height": rgba.height},
        "mode": rgba.mode,
        "alpha": alpha_summary(rgba),
        "connection_edges_covered": alpha.getextrema()[0] > 0,
        "intentional_alpha_policy": "full_coverage_structural_component_box",
        "issues": issues,
        "status": "fail" if issues else "pass",
    }


def validate_architecture_component_image(
    image: Image.Image,
    *,
    expected_dimensions: Iterable[int],
    filename: str | None = None,
    alpha_policy: str = "full_coverage_structural_component_box",
) -> dict[str, Any]:
    """Validate a grid-preserving module or a deliberately masked overlay.

    ``masked_overlay`` exists for architectural door leaves whose transparent
    regions are intentional.  It is metadata on a single logical asset, never
    a second catalog asset.
    """
    if alpha_policy == "full_coverage_structural_component_box":
        return validate_architecture_grid_image(
            image, expected_dimensions=expected_dimensions, filename=filename,
        )
    if alpha_policy != "masked_overlay":
        raise ValueError(f"Unknown architecture component alpha policy: {alpha_policy!r}.")
    dimensions = tuple(expected_dimensions)
    rgba = ensure_rgba(image)
    alpha = rgba.getchannel("A")
    issues: list[dict[str, str]] = []
    if rgba.size != dimensions:
        issues.append({
            "code": "architecture_dimension_mismatch", "severity": "error",
            "message": f"Expected native dimensions {dimensions[0]}x{dimensions[1]}, got {rgba.width}x{rgba.height}.",
        })
    if rgba.mode != "RGBA":
        issues.append({"code": "architecture_not_rgba", "severity": "error", "message": "Architecture component is not RGBA."})
    bounds = alpha.getbbox()
    if bounds is None:
        issues.append({"code": "empty_sprite", "severity": "error", "message": "Masked architecture overlay has no visible pixels."})
    if alpha.getextrema()[0] > 0:
        issues.append({
            "code": "overlay_missing_transparency", "severity": "error",
            "message": "Masked architecture overlay must retain its validated transparent pixels.",
        })
    if filename and not FILENAME_RE.fullmatch(filename):
        issues.append({"code": "filename_schema", "severity": "error", "message": "Filename is not lowercase snake_case ending in _NN.png."})
    return {
        "dimensions": {"width": rgba.width, "height": rgba.height},
        "mode": rgba.mode,
        "alpha": alpha_summary(rgba),
        "alpha_bounds": list(bounds) if bounds else None,
        "connection_edges_covered": False,
        "intentional_alpha_policy": "masked_overlay",
        "issues": issues,
        "status": "fail" if issues else "pass",
    }


def alpha_summary(image: Image.Image) -> dict[str, Any]:
    rgba = ensure_rgba(image)
    alpha = rgba.getchannel("A")
    histogram = alpha.histogram()
    total = rgba.width * rgba.height
    transparent = histogram[0]
    opaque = histogram[255]
    return {
        "has_transparency": transparent > 0,
        "transparent_pixels": transparent,
        "opaque_pixels": opaque,
        "total_pixels": total,
        "transparent_ratio": round(transparent / total, 4) if total else 0,
    }


def _border_alpha_is_opaque(image: Image.Image) -> bool:
    rgba = ensure_rgba(image)
    if rgba.width < 2 or rgba.height < 2:
        return rgba.getchannel("A").getextrema()[0] == 255
    alpha = rgba.getchannel("A")
    samples = list(alpha.crop((0, 0, rgba.width, 1)).get_flattened_data())
    samples += list(alpha.crop((0, rgba.height - 1, rgba.width, rgba.height)).get_flattened_data())
    samples += list(alpha.crop((0, 1, 1, rgba.height - 1)).get_flattened_data())
    samples += list(alpha.crop((rgba.width - 1, 1, rgba.width, rgba.height - 1)).get_flattened_data())
    return bool(samples) and min(samples) == 255


def validate_image(
    image: Image.Image,
    *,
    filename: str | None = None,
    native_grid: int | None = None,
    footprint_width_tiles: int | None = None,
    footprint_height_tiles: int | None = None,
) -> dict[str, Any]:
    """Technical-only checks. Findings are warnings; nothing is deleted or scored aesthetically."""
    rgba = ensure_rgba(image)
    bounds = transparent_bounds(rgba)
    issues: list[dict[str, str]] = []
    summary = alpha_summary(rgba)
    if bounds is None:
        issues.append({"code": "empty_sprite", "severity": "error", "message": "No visible pixels found."})
    else:
        left, top, right, bottom = bounds
        if left == 0 or top == 0 or right == rgba.width or bottom == rgba.height:
            issues.append({"code": "touching_canvas_edge", "severity": "warning", "message": "Visible pixels reach a canvas edge; source may be clipped."})
        tight_area = (right - left) * (bottom - top)
        if tight_area and rgba.width * rgba.height / tight_area > 4:
            issues.append({"code": "excessive_padding", "severity": "warning", "message": "Canvas area is over four times the tight alpha bounds."})
    if not summary["has_transparency"]:
        issues.append({"code": "missing_transparency", "severity": "warning", "message": "No fully transparent pixels found."})
    if _border_alpha_is_opaque(rgba):
        issues.append({"code": "opaque_border", "severity": "warning", "message": "Every outer-edge pixel is opaque; inspect for a generated background."})
    if rgba.width > 2048 or rgba.height > 2048:
        issues.append({"code": "unusually_large_canvas", "severity": "warning", "message": "Canvas exceeds 2048 px in one dimension."})
    if rgba.width < 2 or rgba.height < 2:
        issues.append({"code": "unusually_small_canvas", "severity": "warning", "message": "Canvas is smaller than 2 px in one dimension."})
    if native_grid and footprint_width_tiles and footprint_height_tiles:
        # Six logical tiles per footprint axis is deliberately generous: tall equipment,
        # signs, and overhangs are valid, but working-scale source sheets are not native art.
        width_limit = native_grid * footprint_width_tiles * 6
        height_limit = native_grid * footprint_height_tiles * 6
        if rgba.width > width_limit or rgba.height > height_limit:
            issues.append({
                "code": "unusually_large_native_canvas",
                "severity": "warning",
                "message": f"Native canvas exceeds generous {width_limit}x{height_limit} px footprint-based limits; check source_scale.",
            })
    if filename and not FILENAME_RE.fullmatch(filename):
        issues.append({"code": "filename_schema", "severity": "error", "message": "Filename is not lowercase snake_case ending in _NN.png."})
    return {
        "dimensions": {"width": rgba.width, "height": rgba.height},
        "mode": rgba.mode,
        "alpha": summary,
        "alpha_bounds": list(bounds) if bounds else None,
        "issues": issues,
        "status": "fail" if any(item["severity"] == "error" for item in issues) else ("warning" if issues else "pass"),
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def perceptual_hash(image: Image.Image, side: int = 8) -> str:
    """A small average hash for duplicate triage, not a decision to delete assets."""
    rgba = ensure_rgba(image)
    background = Image.new("RGBA", rgba.size, (242, 235, 221, 255))
    background.alpha_composite(rgba)
    pixels = list(background.convert("L").resize((side, side), Image.Resampling.LANCZOS).get_flattened_data())
    average = sum(pixels) / len(pixels)
    return f"{int(''.join('1' if pixel >= average else '0' for pixel in pixels), 2):0{side * side // 4}x}"


def hash_distance(first: str, second: str) -> int:
    return (int(first, 16) ^ int(second, 16)).bit_count()


def load_manifest() -> dict[str, Any]:
    if not MANIFEST_PATH.exists():
        return {"schema_version": "1.0", "native_grid": 32, "assets": []}
    with MANIFEST_PATH.open(encoding="utf-8") as file:
        manifest = json.load(file)
    manifest.setdefault("schema_version", "1.0")
    manifest.setdefault("native_grid", 32)
    manifest.setdefault("assets", [])
    return manifest


def save_manifest(manifest: dict[str, Any]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST_PATH.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(manifest, file, indent=2, ensure_ascii=False)
        file.write("\n")


def upsert_asset(manifest: dict[str, Any], asset: dict[str, Any]) -> None:
    assets = manifest["assets"]
    for index, existing in enumerate(assets):
        if existing["id"] == asset["id"]:
            if existing.get("approval_status") == "approved":
                raise ValueError(f"Refusing to alter approved asset {asset['id']} automatically.")
            assets[index] = asset
            break
    else:
        assets.append(asset)
    assets.sort(key=lambda entry: entry["id"])


def _batch_assets(batch_path: str | Path) -> list[dict[str, Any]]:
    with repo_path(batch_path).open(encoding="utf-8") as file:
        batch = json.load(file)
    assets = batch.get("assets")
    if not isinstance(assets, list):
        raise ValueError("Batch JSON must contain an assets array.")
    return assets


def _validate_batch_item(item: dict[str, Any]) -> None:
    if item.get("views") is not None:
        from .views import validate_schema
        validate_schema(item)
    missing = [key for key in ("source", "category", "asset_type") if not item.get(key)]
    if missing:
        raise ValueError(f"Batch asset missing required field(s): {', '.join(missing)}")
    if item["category"] not in CATEGORIES:
        raise ValueError(f"Unknown category {item['category']!r}; use a repository asset category.")
    validate_source_scale(item.get("source_scale", 1))
    crop = item.get("crop")
    if crop is not None and (not isinstance(crop, list) or len(crop) != 4 or not all(isinstance(v, int) for v in crop)):
        raise ValueError("crop must be four integer Pillow coordinates [left, top, right, bottom].")
    mode = item.get("normalization_mode", "standard")
    if mode not in {"standard", "architecture_grid_preserving"}:
        raise ValueError("normalization_mode must be 'standard' or 'architecture_grid_preserving'.")
    if mode == "architecture_grid_preserving":
        dimensions = item.get("expected_native_dimensions")
        if not isinstance(dimensions, list) or len(dimensions) != 2 or not all(isinstance(value, int) and value > 0 for value in dimensions):
            raise ValueError("architecture_grid_preserving assets require expected_native_dimensions [width, height].")
    components = item.get("components", [])
    if not isinstance(components, list):
        raise ValueError("components must be an optional array of implementation components.")
    roles: set[str] = set()
    filenames: set[str] = set()
    for component in components:
        if not isinstance(component, dict):
            raise ValueError("Each component must be an object.")
        missing_component = [key for key in ("role", "filename", "crop", "expected_native_dimensions", "anchor_relative_to_logical_native") if key not in component]
        if missing_component:
            raise ValueError(f"Architecture component missing required field(s): {', '.join(missing_component)}")
        role = slug(component["role"])
        filename = component["filename"]
        if role in roles or filename in filenames:
            raise ValueError("Component roles and filenames must be unique within one logical asset.")
        roles.add(role)
        filenames.add(filename)
        if not isinstance(filename, str) or not FILENAME_RE.fullmatch(filename):
            raise ValueError("Component filename must be lowercase snake_case ending in _NN.png.")
        crop = component["crop"]
        if not isinstance(crop, list) or len(crop) != 4 or not all(isinstance(value, int) for value in crop):
            raise ValueError("Component crop must be four integer Pillow coordinates [left, top, right, bottom].")
        dimensions = component["expected_native_dimensions"]
        if not isinstance(dimensions, list) or len(dimensions) != 2 or not all(isinstance(value, int) and value > 0 for value in dimensions):
            raise ValueError("Component expected_native_dimensions must contain two positive integers.")
        anchor = component["anchor_relative_to_logical_native"]
        if not isinstance(anchor, list) or len(anchor) != 2 or not all(isinstance(value, int) for value in anchor):
            raise ValueError("Component anchor_relative_to_logical_native must be two integer native coordinates.")
        if component.get("normalization_mode", mode) != "architecture_grid_preserving":
            raise ValueError("Architecture implementation components must use architecture_grid_preserving.")
        if component.get("alpha_policy", "full_coverage_structural_component_box") not in {
            "full_coverage_structural_component_box", "masked_overlay",
        }:
            raise ValueError("Component alpha_policy is not recognized.")
        polygon = component.get("mask_polygon_source_px")
        if polygon is not None and (
            not isinstance(polygon, list) or len(polygon) < 3
            or any(not isinstance(point, list) or len(point) != 2 or not all(isinstance(value, int) for value in point) for point in polygon)
        ):
            raise ValueError("mask_polygon_source_px must be a list of at least three [x, y] source-pixel points.")


def ingest_batch(batch_path: str | Path, *, force: bool = False) -> list[dict[str, Any]]:
    """Crop configured source images into traceable pending raw files and register them."""
    items = _batch_assets(batch_path)
    if any("views" in item for item in items):
        from .views import ingest
        if not all(item.get("ingestion_mode") == "validated_native_copy" for item in items):
            raise ValueError("Exclusive native-copy batches must not mix legacy crop ingestion")
        for item in items:
            _validate_batch_item(item)
        return ingest(__import__(__name__, fromlist=["ROOT"]), items)
    manifest = load_manifest()
    ingested: list[dict[str, Any]] = []
    for item in _batch_assets(batch_path):
        _validate_batch_item(item)
        source = repo_path(item["source"])
        if not source.is_file():
            raise FileNotFoundError(f"Input PNG was not found: {source}")
        filename = build_filename(item["asset_type"], item.get("variant", 1), item.get("orientation"), item.get("state", "clean"))
        raw_path = ROOT / "staging" / "pending" / "raw" / filename
        existing = next((asset for asset in manifest["assets"] if asset["id"] == filename[:-4]), None)
        if existing and existing.get("approval_status") == "approved":
            raise ValueError(f"Refusing to ingest over approved asset {filename}.")
        if raw_path.exists() and not force:
            raise FileExistsError(f"{raw_path} exists. Use --force only for pending pilot artifacts.")
        with Image.open(source) as opened:
            image = ensure_rgba(opened)
        source_size = {"width": image.width, "height": image.height}
        if item.get("crop"):
            left, top, right, bottom = item["crop"]
            if not (0 <= left < right <= image.width and 0 <= top < bottom <= image.height):
                raise ValueError(f"Crop {item['crop']} lies outside {source} ({image.width}x{image.height}).")
            image = image.crop(tuple(item["crop"]))
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(raw_path, format="PNG")
        # This occurs before trimming/scaling so source-art contamination and clipping
        # remain observable even when the native output becomes technically clean.
        raw_qa = validate_image(image, filename=filename)
        asset = {
            "id": filename[:-4], "filename": filename, "category": item["category"],
            "subcategory": item.get("subcategory", ""), "asset_type": slug(item["asset_type"]),
            "variant": int(item.get("variant", 1)), "orientation": item.get("orientation", "default"),
            "state": item.get("state", "clean"), "reuse_scope": item.get("reuse_scope", "hospital_only"),
            "native_grid": 32, "source_scale": validate_source_scale(item.get("source_scale", 1)),
            "canvas_width": None, "canvas_height": None,
            "footprint_width_tiles": int(item.get("footprint_width_tiles", 1)),
            "footprint_height_tiles": int(item.get("footprint_height_tiles", 1)),
            "anchor": item.get("anchor", "bottom_center"), "tags": item.get("tags", []),
            "source": rel(source), "source_sha256": sha256_file(source), "source_dimensions": source_size,
            "crop": item.get("crop"), "staging_path": rel(raw_path), "normalized_path": "", "final_path": "",
            "raw_qa_status": raw_qa["status"], "raw_qa_issues": raw_qa["issues"],
            "approval_status": "technical_pending", "qa_status": "not_run", "qa_issues": [],
            "perceptual_hash": "", "notes": item.get("notes", ""),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        for key in (
            "normalization_mode", "expected_native_dimensions", "architecture_structural_role",
            "architecture_provenance", "validation_reference",
        ):
            if key in item:
                asset[key] = item[key]
        components: list[dict[str, Any]] = []
        for configured in item.get("components", []):
            component_source = repo_path(configured.get("source", item["source"]))
            if not component_source.is_file():
                raise FileNotFoundError(f"Component input PNG was not found: {component_source}")
            with Image.open(component_source) as opened:
                component_image = ensure_rgba(opened)
            component_source_size = {"width": component_image.width, "height": component_image.height}
            left, top, right, bottom = configured["crop"]
            if not (0 <= left < right <= component_image.width and 0 <= top < bottom <= component_image.height):
                raise ValueError(
                    f"Component crop {configured['crop']} lies outside {component_source} "
                    f"({component_image.width}x{component_image.height})."
                )
            component_image = component_image.crop(tuple(configured["crop"]))
            if configured.get("mask_polygon_source_px") is not None:
                mask = Image.new("L", component_image.size, 0)
                ImageDraw.Draw(mask).polygon([
                    (x - left, y - top) for x, y in configured["mask_polygon_source_px"]
                ], fill=255)
                component_image.putalpha(mask)
            component_raw = ROOT / "staging" / "pending" / "raw" / "components" / filename[:-4] / configured["filename"]
            if component_raw.exists() and not force:
                raise FileExistsError(f"{component_raw} exists. Use --force only for pending pilot artifacts.")
            component_raw.parent.mkdir(parents=True, exist_ok=True)
            component_image.save(component_raw, format="PNG")
            component = {
                "role": slug(configured["role"]), "filename": configured["filename"],
                "source": rel(component_source), "source_sha256": sha256_file(component_source),
                "source_dimensions": component_source_size, "crop": configured["crop"],
                "source_scale": validate_source_scale(configured.get("source_scale", item.get("source_scale", 1))),
                "expected_native_dimensions": configured["expected_native_dimensions"],
                "normalization_mode": "architecture_grid_preserving",
                "anchor_relative_to_logical_native": configured["anchor_relative_to_logical_native"],
                "alpha_policy": configured.get("alpha_policy", "full_coverage_structural_component_box"),
                "validation_reference": configured.get("validation_reference", item.get("validation_reference", "")),
                "staging_path": rel(component_raw), "normalized_path": "", "raw_qa_status": validate_image(component_image, filename=configured["filename"])["status"],
                "raw_qa_issues": validate_image(component_image, filename=configured["filename"])["issues"],
                "qa_status": "not_run", "qa_issues": [],
            }
            if configured.get("mask_polygon_source_px") is not None:
                component["mask_polygon_source_px"] = configured["mask_polygon_source_px"]
                component["deterministic_geometry_mask"] = "validated_source_polygon"
            components.append(component)
        if components:
            asset["components"] = components
        upsert_asset(manifest, asset)
        ingested.append(asset)
    save_manifest(manifest)
    return ingested


def normalize_pending(
    *, padding: int = 2, force: bool = False, asset_ids: Iterable[str] | None = None,
) -> list[str]:
    """Normalize pending assets, optionally restricting work to explicit asset ids."""
    manifest = load_manifest()
    selected = set(asset_ids) if asset_ids is not None else None
    normalized: list[str] = []
    for asset in manifest["assets"]:
        if selected is not None and asset["id"] not in selected:
            continue
        if asset.get("approval_status") == "approved" or not asset.get("staging_path"):
            continue
        if asset.get("ingestion_mode") == "validated_native_copy":
            from .views import qa_asset
            if qa_asset(ROOT, asset)["status"] != "pass":
                raise ValueError("Already-native exclusive view failed QA; refusing normalization/repair")
            normalized.append(asset["id"])
            continue
        raw_path = repo_path(asset["staging_path"])
        if not raw_path.is_file():
            raise FileNotFoundError(f"Missing staged raw image for {asset['id']}: {raw_path}")
        output = ROOT / "staging" / "pending" / "normalized" / asset["filename"]
        if output.exists() and not force:
            raise FileExistsError(f"{output} exists. Use --force to refresh pending output.")
        with Image.open(raw_path) as opened:
            if asset.get("normalization_mode") == "architecture_grid_preserving":
                image = normalize_architecture_grid_image(
                    opened,
                    source_scale=validate_source_scale(asset.get("source_scale", 1)),
                    expected_native_dimensions=asset.get("expected_native_dimensions", []),
                )
            else:
                image = normalize_image(opened, padding, source_scale=validate_source_scale(asset.get("source_scale", 1)))
        output.parent.mkdir(parents=True, exist_ok=True)
        image.save(output, format="PNG")
        asset["normalized_path"] = rel(output)
        asset["canvas_width"], asset["canvas_height"] = image.size
        asset["normalized_sha256"] = sha256_file(output)
        asset["perceptual_hash"] = perceptual_hash(image)
        if asset.get("normalization_mode") == "architecture_grid_preserving":
            asset["normalization_exception"] = {
                "kind": "architecture_grid_preserving",
                "reason": "Canonical architecture modules intentionally retain exact opaque connection boxes; generic alpha trim and transparent safety padding would shift grid-aligned edges.",
                "padding_applied": 0,
                "trim_applied": False,
                "scaler": "nearest_neighbor",
            }
        for component in asset.get("components", []):
            component_raw = repo_path(component.get("staging_path", ""))
            if not component_raw.is_file():
                raise FileNotFoundError(f"Missing staged raw component for {asset['id']}/{component.get('role')}: {component_raw}")
            component_output = ROOT / "staging" / "pending" / "normalized" / "components" / asset["id"] / component["filename"]
            if component_output.exists() and not force:
                raise FileExistsError(f"{component_output} exists. Use --force to refresh pending output.")
            with Image.open(component_raw) as opened:
                component_image = normalize_architecture_grid_image(
                    opened,
                    source_scale=validate_source_scale(component.get("source_scale", asset.get("source_scale", 1))),
                    expected_native_dimensions=component["expected_native_dimensions"],
                )
            component_output.parent.mkdir(parents=True, exist_ok=True)
            component_image.save(component_output, format="PNG")
            component["normalized_path"] = rel(component_output)
            component["canvas_width"], component["canvas_height"] = component_image.size
            component["normalized_sha256"] = sha256_file(component_output)
            component["perceptual_hash"] = perceptual_hash(component_image)
            component["normalization_exception"] = {
                "kind": "architecture_grid_preserving",
                "reason": "Validated architecture implementation component retains its exact crop, anchor, and alpha behavior.",
                "padding_applied": 0, "trim_applied": False, "scaler": "nearest_neighbor",
            }
        asset["updated_at"] = datetime.now(timezone.utc).isoformat()
        normalized.append(asset["id"])
    save_manifest(manifest)
    return normalized


def remove_confirmed_laboratory_biosafety_debris() -> str:
    """Remove the single human-confirmed isolated native pixel from Batch 09.

    This is intentionally asset- and coordinate-specific; it is not a general
    connected-component cleanup operation.
    """
    asset_id = "laboratory_biosafety_cabinet_01"
    coordinate = (39, 44)
    manifest = load_manifest()
    asset = next((entry for entry in manifest["assets"] if entry["id"] == asset_id), None)
    if asset is None:
        raise ValueError(f"Cannot find {asset_id} in the manifest.")
    if asset.get("approval_status") == "approved":
        raise ValueError(f"Refusing to alter already-approved asset {asset_id}.")
    path = repo_path(asset.get("normalized_path", ""))
    if not path.is_file():
        raise FileNotFoundError(f"Missing normalized file for {asset_id}: {path}")
    with Image.open(path) as opened:
        image = ensure_rgba(opened)
    x, y = coordinate
    if not (0 <= x < image.width and 0 <= y < image.height):
        raise ValueError(f"Confirmed cleanup coordinate {coordinate} is outside {path}.")
    if image.getpixel(coordinate)[3] == 0:
        raise ValueError(f"Confirmed cleanup coordinate {coordinate} is already transparent.")
    image.putpixel(coordinate, (0, 0, 0, 0))
    image.save(path, format="PNG")
    asset["normalized_sha256"] = sha256_file(path)
    asset["perceptual_hash"] = perceptual_hash(image)
    asset["technical_cleanup"] = {
        "kind": "human_confirmed_isolated_alpha_debris",
        "coordinate": [x, y],
        "performed_at": datetime.now(timezone.utc).isoformat(),
    }
    asset["updated_at"] = datetime.now(timezone.utc).isoformat()
    save_manifest(manifest)
    return asset_id


def approve_assets(asset_ids: Iterable[str], *, human_qa_disposition: str | None = None) -> list[str]:
    """Promote explicitly reviewed assets; warnings require a recorded human disposition."""
    requested = list(dict.fromkeys(asset_ids))
    manifest = load_manifest()
    by_id = {asset["id"]: asset for asset in manifest["assets"]}
    missing = [asset_id for asset_id in requested if asset_id not in by_id]
    if missing:
        raise ValueError(f"Cannot approve missing asset(s): {', '.join(missing)}")
    approved: list[str] = []
    from .views import promotion_plan, promote
    # Validate every requested exclusive parent's views before any file is copied.
    view_plans = {asset_id: promotion_plan(ROOT, by_id[asset_id]) for asset_id in requested
                  if by_id[asset_id].get("views") and by_id[asset_id].get("approval_status") != "approved"}
    for asset_id in requested:
        asset = by_id[asset_id]
        if asset.get("approval_status") == "approved":
            continue
        qa_status = asset.get("qa_status")
        if qa_status == "fail":
            raise ValueError(f"Cannot approve {asset_id}; technical QA status is {qa_status!r}.")
        if qa_status == "warning":
            if not human_qa_disposition or not human_qa_disposition.strip():
                raise ValueError(
                    f"Cannot approve {asset_id}; technical warnings require an explicit human QA disposition."
                )
            asset["human_qa_disposition"] = human_qa_disposition.strip()
            asset["human_qa_reviewed_at"] = datetime.now(timezone.utc).isoformat()
        elif qa_status != "pass":
            raise ValueError(f"Cannot approve {asset_id}; technical QA status is {qa_status!r}.")
        if asset_id in view_plans:
            promote(ROOT, asset, view_plans[asset_id])
            asset["updated_at"] = datetime.now(timezone.utc).isoformat()
            approved.append(asset_id)
            continue
        source = repo_path(asset.get("normalized_path", ""))
        if not source.is_file():
            raise FileNotFoundError(f"Cannot approve {asset_id}; normalized image is missing: {source}")
        approved_stage = ROOT / "staging" / "approved" / asset["filename"]
        final = ROOT / "assets" / asset["category"] / asset["filename"]
        approved_stage.parent.mkdir(parents=True, exist_ok=True)
        final.parent.mkdir(parents=True, exist_ok=True)
        if final.exists():
            raise FileExistsError(f"Refusing to overwrite existing final asset: {final}")
        shutil.copy2(source, approved_stage)
        shutil.copy2(source, final)
        for component in asset.get("components", []):
            component_source = repo_path(component.get("normalized_path", ""))
            if not component_source.is_file():
                raise FileNotFoundError(
                    f"Cannot approve {asset_id}; normalized component {component.get('role')} is missing: {component_source}"
                )
            component_stage = ROOT / "staging" / "approved" / "components" / asset_id / component["filename"]
            component_final = ROOT / "assets" / asset["category"] / "components" / asset_id / component["filename"]
            component_stage.parent.mkdir(parents=True, exist_ok=True)
            component_final.parent.mkdir(parents=True, exist_ok=True)
            if component_final.exists():
                raise FileExistsError(f"Refusing to overwrite existing final component asset: {component_final}")
            shutil.copy2(component_source, component_stage)
            shutil.copy2(component_source, component_final)
            component["approved_staging_path"] = rel(component_stage)
            component["final_path"] = rel(component_final)
        asset["approved_staging_path"] = rel(approved_stage)
        asset["final_path"] = rel(final)
        asset["approval_status"] = "approved"
        asset["updated_at"] = datetime.now(timezone.utc).isoformat()
        approved.append(asset_id)
    save_manifest(manifest)
    return approved


def _architecture_component_qa_report(
    raw_path: Path,
    image_path: Path,
    *,
    filename: str,
    source_scale: int,
    expected_native_dimensions: Iterable[int],
    alpha_policy: str,
    native_grid: int = 32,
    footprint_width_tiles: int | None = None,
    footprint_height_tiles: int | None = None,
    normalization_exception: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run raw and native QA while retaining intentional architecture cues."""
    expected_native = list(expected_native_dimensions)
    expected_source = [value * validate_source_scale(source_scale) for value in expected_native]
    with Image.open(raw_path) as image:
        generic_raw = validate_image(image, filename=filename)
        raw_report = validate_architecture_component_image(
            image, expected_dimensions=expected_source, filename=filename, alpha_policy=alpha_policy,
        )
    with Image.open(image_path) as image:
        generic_native = validate_image(
            image, filename=filename, native_grid=native_grid,
            footprint_width_tiles=footprint_width_tiles, footprint_height_tiles=footprint_height_tiles,
        )
        report = validate_architecture_component_image(
            image, expected_dimensions=expected_native, filename=filename, alpha_policy=alpha_policy,
        )
    intentional_codes = {"missing_transparency", "opaque_border", "touching_canvas_edge"}
    generic_issues = generic_raw["issues"] + [
        issue for issue in generic_native["issues"] if issue not in generic_raw["issues"]
    ]
    unexpected_generic = [issue for issue in generic_issues if issue["code"] not in intentional_codes]
    report["raw_dimensions"] = raw_report["dimensions"]
    report["architecture_qa"] = {
        "raw": raw_report,
        "native": report.copy(),
        "generic_findings_retained_as_intentional": [
            issue for issue in generic_issues if issue["code"] in intentional_codes
        ],
        "normalization_exception": normalization_exception or {},
    }
    report["issues"] = unexpected_generic + report["issues"]
    report["status"] = "fail" if any(issue["severity"] == "error" for issue in report["issues"]) else (
        "warning" if report["issues"] else "pass"
    )
    return report


def run_qa(*, asset_ids: Iterable[str] | None = None, write_reports: bool = True) -> dict[str, Any]:
    manifest = load_manifest()
    selected = set(asset_ids) if asset_ids is not None else None
    reports: list[dict[str, Any]] = []
    for asset in manifest["assets"]:
        if selected is not None and asset["id"] not in selected:
            continue
        raw_path = repo_path(asset.get("staging_path", ""))
        image_path = repo_path(asset.get("normalized_path") or asset.get("staging_path", ""))
        if asset.get("qa_profile") == "architecture_glass":
            from .views import qa_asset
            report = qa_asset(ROOT, asset)
            for name, result in report.get("views", {}).items():
                asset["views"][name]["qa_status"] = result["status"]
        elif not raw_path.is_file() or not image_path.is_file():
            missing = raw_path if not raw_path.is_file() else image_path
            report = {"status": "fail", "issues": [{"code": "missing_staged_file", "severity": "error", "message": str(missing)}]}
        elif asset.get("normalization_mode") == "architecture_grid_preserving":
            report = _architecture_component_qa_report(
                raw_path, image_path, filename=asset["filename"],
                source_scale=validate_source_scale(asset.get("source_scale", 1)),
                expected_native_dimensions=asset.get("expected_native_dimensions", []),
                alpha_policy="full_coverage_structural_component_box",
                native_grid=asset.get("native_grid", 32),
                footprint_width_tiles=asset.get("footprint_width_tiles"),
                footprint_height_tiles=asset.get("footprint_height_tiles"),
                normalization_exception=asset.get("normalization_exception", {}),
            )
        else:
            # QA must inspect the raw crop as well: normalization intentionally adds a
            # transparent border and would mask a source sprite clipped at its canvas edge.
            with Image.open(raw_path) as image:
                raw_report = validate_image(image, filename=asset["filename"])
            with Image.open(image_path) as image:
                report = validate_image(
                    image,
                    filename=asset["filename"],
                    native_grid=asset.get("native_grid", 32),
                    footprint_width_tiles=asset.get("footprint_width_tiles"),
                    footprint_height_tiles=asset.get("footprint_height_tiles"),
                )
            issues = raw_report["issues"] + [issue for issue in report["issues"] if issue not in raw_report["issues"]]
            report["raw_dimensions"] = raw_report["dimensions"]
            report["issues"] = issues
            report["status"] = "fail" if any(item["severity"] == "error" for item in issues) else ("warning" if issues else "pass")
        component_reports: list[dict[str, Any]] = []
        for component in asset.get("components", []):
            component_raw = repo_path(component.get("staging_path", ""))
            component_image = repo_path(component.get("normalized_path") or component.get("staging_path", ""))
            if not component_raw.is_file() or not component_image.is_file():
                missing = component_raw if not component_raw.is_file() else component_image
                component_report = {
                    "status": "fail", "issues": [{"code": "missing_staged_component", "severity": "error", "message": str(missing)}],
                }
            else:
                component_report = _architecture_component_qa_report(
                    component_raw, component_image, filename=component["filename"],
                    source_scale=validate_source_scale(component.get("source_scale", asset.get("source_scale", 1))),
                    expected_native_dimensions=component["expected_native_dimensions"],
                    alpha_policy=component.get("alpha_policy", "full_coverage_structural_component_box"),
                    native_grid=asset.get("native_grid", 32),
                    normalization_exception=component.get("normalization_exception", {}),
                )
            component["qa_status"] = component_report["status"]
            component["qa_issues"] = component_report["issues"]
            component_reports.append({"role": component["role"], "filename": component["filename"], **component_report})
        if component_reports:
            report["components"] = component_reports
            if any(component["status"] == "fail" for component in component_reports):
                report["issues"].append({
                    "code": "component_qa_failed", "severity": "error",
                    "message": "One or more implementation components failed technical QA.",
                })
            elif any(component["status"] == "warning" for component in component_reports):
                report["issues"].append({
                    "code": "component_qa_warning", "severity": "warning",
                    "message": "One or more implementation components has a technical QA warning.",
                })
            report["status"] = "fail" if any(issue["severity"] == "error" for issue in report["issues"]) else (
                "warning" if report["issues"] else "pass"
            )
        asset["qa_status"] = report["status"]
        asset["qa_issues"] = report["issues"]
        if asset.get("approval_status") == "technical_pending":
            asset["approval_status"] = "needs_human_review" if report["status"] != "fail" else "technical_failed"
        reports.append({"id": asset["id"], "filename": asset["filename"], "path": str(image_path) if image_path else "", **report})
    manifest["assets"].sort(key=lambda entry: entry["id"])
    save_manifest(manifest)
    near_duplicates = find_near_duplicates(manifest["assets"])
    if selected is not None:
        near_duplicates = [m for m in near_duplicates if m["first"] in selected or m["second"] in selected]
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(), "assets_checked": len(reports),
        "status_counts": dict(Counter(report["status"] for report in reports)), "assets": reports,
        "near_duplicates": near_duplicates,
    }
    if write_reports:
        write_qa_reports(result)
    return result


def find_near_duplicates(assets: Iterable[dict[str, Any]], threshold: int = 4) -> list[dict[str, Any]]:
    candidates = [asset for asset in assets if asset.get("perceptual_hash") and asset.get("approval_status") != "rejected"]
    matches: list[dict[str, Any]] = []
    for index, first in enumerate(candidates):
        for second in candidates[index + 1:]:
            distance = hash_distance(first["perceptual_hash"], second["perceptual_hash"])
            if distance <= threshold:
                matches.append({"first": first["id"], "second": second["id"], "distance": distance, "threshold": threshold})
    return matches


def write_qa_reports(result: dict[str, Any]) -> None:
    QA_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with QA_JSON_PATH.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(result, file, indent=2)
        file.write("\n")
    with QA_CSV_PATH.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["id", "filename", "status", "issue_codes", "path"])
        writer.writeheader()
        for report in result["assets"]:
            writer.writerow({"id": report["id"], "filename": report["filename"], "status": report["status"], "issue_codes": ";".join(issue["code"] for issue in report["issues"]), "path": report["path"]})
    lines = ["# Technical QA Report", "", f"Assets checked: {result['assets_checked']}", "", "| Asset | Status | Findings |", "| --- | --- | --- |"]
    for report in result["assets"]:
        findings = "; ".join(issue["code"] for issue in report["issues"]) or "none"
        lines.append(f"| `{report['filename']}` | {report['status']} | {findings} |")
    lines += ["", "## Near-duplicate triage", "", "Perceptual matches are review cues only; no assets are removed automatically.", ""]
    if result["near_duplicates"]:
        for match in result["near_duplicates"]:
            lines.append(f"- `{match['first']}` / `{match['second']}` — distance {match['distance']} of {match['threshold']}")
    else:
        lines.append("No candidate pairs.")
    with QA_MD_PATH.open("w", encoding="utf-8", newline="\n") as file:
        file.write("\n".join(lines) + "\n")


def write_catalog() -> Path:
    manifest = load_manifest()
    fields = [
        "id", "filename", "category", "subcategory", "asset_type", "variant", "orientation", "state", "reuse_scope",
        "native_grid", "source_scale", "canvas_width", "canvas_height", "footprint_width_tiles", "footprint_height_tiles", "anchor",
        "approval_status", "qa_status", "component_count", "component_roles", "tags", "source", "normalized_path", "notes",
    ]
    with CATALOG_PATH.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for asset in manifest["assets"]:
            row = {field: asset.get(field, "") for field in fields}
            row["component_count"] = len(asset.get("components", []))
            row["component_roles"] = ";".join(component.get("role", "") for component in asset.get("components", []))
            row["tags"] = ";".join(asset.get("tags", []))
            writer.writerow(row)
    return CATALOG_PATH


def create_contact_sheet(*, columns: int = 5, scale: int = 4) -> Path:
    if columns < 1 or scale < 1:
        raise ValueError("columns and scale must be at least 1")
    manifest = load_manifest()
    entries = [asset for asset in manifest["assets"] if asset.get("normalized_path") and repo_path(asset["normalized_path"]).is_file() and asset.get("approval_status") != "rejected"]
    if not entries:
        raise ValueError("No normalized pending assets are available for a contact sheet.")
    thumb_size, label_height, margin = 128, 16, 8
    rows = (len(entries) + columns - 1) // columns
    cell_w, cell_h = thumb_size + margin * 2, thumb_size + label_height + margin * 3
    sheet = Image.new("RGBA", (columns * cell_w, rows * cell_h), (242, 235, 221, 255))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, asset in enumerate(entries):
        with Image.open(repo_path(asset["normalized_path"])) as opened:
            image = ensure_rgba(opened)
        image.thumbnail((thumb_size, thumb_size), Image.Resampling.NEAREST)
        col, row = index % columns, index // columns
        x, y = col * cell_w + margin, row * cell_h + margin
        draw.rectangle((x - 1, y - 1, x + thumb_size, y + thumb_size), fill=(221, 214, 201, 255), outline=(39, 55, 70, 255))
        sheet.alpha_composite(image, (x + (thumb_size - image.width) // 2, y + (thumb_size - image.height) // 2))
        draw.text((x, y + thumb_size + margin), asset["filename"][:24], fill=(24, 35, 49, 255), font=font)
    if scale > 1:
        sheet = sheet.resize((sheet.width * scale, sheet.height * scale), Image.Resampling.NEAREST)
    CONTACT_SHEET_PATH.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CONTACT_SHEET_PATH, format="PNG")
    return CONTACT_SHEET_PATH


def create_review_bundle(batch_path: str | Path) -> Path:
    """Create a compact, metadata-driven review ZIP for one production batch."""
    batch_file = repo_path(batch_path)
    if not batch_file.is_file():
        raise FileNotFoundError(batch_file)
    with batch_file.open(encoding="utf-8") as file:
        batch = json.load(file)
    manifest = load_manifest()
    by_id = {asset["id"]: asset for asset in manifest["assets"]}
    requested = [build_filename(item["asset_type"], item.get("variant", 1), item.get("orientation"), item.get("state", "clean")).removesuffix(".png") for item in batch.get("assets", [])]
    assets = [by_id[asset_id] for asset_id in requested if asset_id in by_id]
    if len(assets) != len(requested):
        missing = sorted(set(requested) - set(by_id))
        raise ValueError(f"Batch assets missing from manifest: {', '.join(missing)}")
    required = [batch_file, MANIFEST_PATH, CATALOG_PATH, QA_MD_PATH, CONTACT_SHEET_PATH]
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(path)
    summary = {"batch": rel(batch_file), "assets": [{"id": a["id"], "filename": a["filename"], "qa_status": a.get("qa_status"), "warning_codes": [i["code"] for i in a.get("qa_issues", [])]} for a in assets]}
    REVIEW_BUNDLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(REVIEW_BUNDLE_PATH, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in required:
            archive.write(path, rel(path))
        archive.writestr("review_index.json", json.dumps(summary, indent=2) + "\n")
        for asset in assets:
            normalized = repo_path(asset["normalized_path"])
            archive.write(normalized, f"normalized/{asset['filename']}")
            for name, view in asset.get("views", {}).items():
                if name != asset.get("default_view"):
                    archive.write(repo_path(view["normalized_path"]), f"normalized/views/{asset['id']}/{Path(view['normalized_path']).name}")
            if asset.get("qa_status") == "warning":
                raw = repo_path(asset["staging_path"])
                archive.write(raw, f"raw_warnings/{asset['filename']}")
    return REVIEW_BUNDLE_PATH
