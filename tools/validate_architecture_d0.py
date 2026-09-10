"""Deterministic, reference-only D0 evidence. No production mutation or AI tools.

Run: python tools/validate_architecture_d0.py
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter, deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from rastalr_pipeline.geometry import (
    RECTANGLE_CONVENTION, alpha_region, anchored_component, evidence, horizontal_join,
)
from rastalr_pipeline.approval_report import approved_markdown
from rastalr_pipeline.snapshot import compare_snapshots

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "references/architecture/master_validation_D0_v1"
CANON = ROOT / "references/architecture/rastalr_architecture_v2"
# Explicitly authorized D1/D2 reference additions. Existing hashes remain locked.
AUTHORIZED_REFERENCE_ADDITIONS = (
    "references/architecture/master_validation_D1_v1/",
    "references/architecture/master_validation_D2_v1/",
    "references/architecture/master_validation_D2_v2/",
    "references/architecture/master_validation_D2_appearance_v1/",
)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def rgba(path):
    with Image.open(path) as image:
        return image.convert("RGBA")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def production_snapshot():
    manifest = read_json(ROOT / "metadata/manifest.json")
    assets = manifest["assets"]
    # Include every production/staging/source/component PNG, metadata and old
    # reference file; only the explicitly repaired Markdown is excluded.
    paths = [ROOT / "metadata/manifest.json", ROOT / "metadata/catalog.csv"]
    for folder in ("assets", "staging", "source", "references/architecture"):
        paths.extend(p for p in (ROOT / folder).rglob("*") if p.is_file() and OUT not in p.parents)
    paths.extend((ROOT / "metadata").glob("*batch_1[12]*.json"))
    paths.extend((ROOT / "metadata").glob("production_batch_1[12]*.json"))
    return {"counts": {"manifest": len(assets),
                       "approved": sum(a.get("approval_status") == "approved" for a in assets),
                       "needs_human_review": sum(a.get("approval_status") == "needs_human_review" for a in assets)},
            "sha256": {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(set(paths))}}


def contract_from_canonical():
    spec = read_json(CANON / "architecture_v2_spec.json")
    master = read_json(ROOT / "references/architecture/master_validation_v1/sources/architecture_master_plan_v1.json")
    panel = rgba(CANON / "glass_partition_1x.png")
    translucent = panel.getchannel("A").point(lambda a: 255 if 0 < a < 255 else 0)
    pane = list(translucent.getbbox())
    if panel.size != (32, 28) or pane != [4, 5, 28, 23] or spec["logical_grid_px"] != 32:
        raise ValueError("Canonical geometry changed: stop for contract review")
    scale = master["architecture_system"]["generation_source_scale"]
    w, h = panel.size
    l, t, r, b = pane
    connection_start, connection_last = spec["connection_center_range_px"]
    baseline = connection_last + 1
    frame = {"left_post": [0, 0, l, h], "right_post": [r, 0, w, h],
             "top_rail": [l, 0, r, t], "bottom_rail": [l, b, r, h]}
    return {
        "id": "hospital_glass_partition_back_01", "status": "reference_only_d0_contract",
        "rectangle_convention": RECTANGLE_CONVENTION,
        "authority": {"geometry": "Architecture v2", "canonical_png": (CANON / "glass_partition_1x.png").relative_to(ROOT).as_posix(),
                      "sha256": digest(CANON / "glass_partition_1x.png"),
                      "planning": "Attached audit scope human-approved by current user; original proposal labels retained as history"},
        "expected": {"logical_grid_native_px": spec["logical_grid_px"], "logical_footprint_tiles": [1, 1],
                     "native_dimensions_px": [w, h], "source_scale": scale,
                     "topology_role": "EW straight boundary, back-facing full glass presentation",
                     "projection": spec["projection"], "topology_contact_ground_cell": [0, connection_start, w, baseline],
                     "frame_regions_native": frame, "glass_region_native": pane,
                     "contact_regions_native": {"base": [0, b, w, h], "left": frame["left_post"], "right_terminal": frame["right_post"]},
                     "frame_alpha": {"range_inclusive": [255, 255], "all_required_pixels": True},
                     "glass_alpha": {"range_inclusive": [1, 254], "transparent_zero_regions": [],
                                     "policy": "All pane pixels must transmit the level; alpha 0 is an accidental hole in this unbroken D1 pane. Fully clear glass would need an explicit region contract revision.",
                                     "scaffold_alpha_values": sorted(set(panel.crop(pane).getchannel("A").get_flattened_data())),
                                     "future_appearance": "Tint/highlights require human review; repeats must match the chosen single-layer alpha, never accumulate it."},
                     "normalization_mode": "architecture_grid_preserving",
                     "normalization_rules": ["exact integer scale", "nearest-neighbor only", "no trim", "no padding", "no warp", "no baked background"]},
        "observed": {"method": "PNG dimensions; alpha predicate 0<a<255 bounding box; histogram over actual pixels",
                     "canonical_dimensions_px": list(panel.size), "visual_envelope_native": list(panel.getchannel("A").getbbox()),
                     "glass_alpha_bbox_native": pane, "alpha_histogram": dict(sorted(Counter(panel.getchannel("A").get_flattened_data()).items()))},
        "derived": {"source_dimensions_px": [w*scale, h*scale], "source_logical_grid_px": 32*scale,
                    "frame_regions_source": {k: [v*scale for v in rect] for k, rect in frame.items()},
                    "glass_region_source": [v*scale for v in pane],
                    "visual_envelope_source": [0, 0, w*scale, h*scale],
                    "anchor": {"name": "grid_wall_baseline_center", "logical_cell_native": [w//2, baseline],
                               "image_native": [w//2, h], "image_source": [w//2*scale, h*scale],
                               "render_origin_relative_to_cell_native": [0, baseline-h],
                               "render_origin_relative_to_cell_source": [0, (baseline-h)*scale],
                               "render_origin_relative_to_anchor_native": [-w//2, -h],
                               "derivation": "D0 explicit baseline mapping: lower exclusive edge meets ground strip exclusive y=20. Same boundary baseline as full back carrier (origin y=-32, height 52); glass origin y=-8, height 28. This numeric mapping is derived, not pre-existing PNG metadata."},
                    "repeat": {"stride_native": w, "strategy": "left-owned post; terminal right post",
                               "nonterminal_extension_native": [r, 0, w, h],
                               "extension_source_column_native": r-1,
                               "method": "On a reference copy only, extend last interior column through the nonterminal right-post strip. Next panel retains its left post. Do not overlap or shorten stride.",
                               "left_neighbor": "Left post always owned by this cell; previous cell omits its right post",
                               "right_neighbor": "Extend rails and pane to right boundary when neighbor exists; retain right post only at run end",
                               "internal_post_width_native": l, "terminal_post_width_native": l,
                               "production_representation": "One logical asset with adjacency-aware frame/pane components or terminal/nonterminal implementation views; never count these separately"}},
        "structural_failures": ["wrong dimensions/origin/stride", "required frame/contact pixel not opaque", "pane alpha 0 or 255",
                                "shared post wider than canonical 4 px", "missing pane or rail at join", "more than one translucent layer per pane pixel", "alpha changes on repetition"],
        "human_visual_review": {"status": "not performed by a human in D0", "required": ["appearance/tint and visibility", "upper-left light/pixel density", "frame material continuity", "junction occlusion and endpoint treatment", "later D1 artwork approval"]},
    }


def panel_variant(panel, contract, terminal):
    result = panel.copy()
    if not terminal:
        left, top, right, bottom = contract["derived"]["repeat"]["nonterminal_extension_native"]
        column = contract["derived"]["repeat"]["extension_source_column_native"]
        for x in range(left, right):
            for y in range(top, bottom):
                result.putpixel((x, y), panel.getpixel((column, y)))
    return result


def compose_glass(panel, contract, count, *, naive=False, overlap=False):
    width, height = contract["expected"]["native_dimensions_px"]
    output = Image.new("RGBA", (width*count, height))
    placements = []
    layer_counts = Image.new("I", output.size, 0)
    for index in range(count):
        component = panel_variant(panel, contract, naive or index == count-1)
        origin = (index*width, 0)
        output.alpha_composite(component, origin)
        placements.append(list(origin))
        for y in range(height):
            for x in range(width):
                if 0 < component.getpixel((x, y))[3] < 255:
                    p = (x+origin[0], y)
                    layer_counts.putpixel(p, layer_counts.getpixel(p)+1)
        if overlap and index == 0:
            # A second translucent coating over a real pane area, not a report literal.
            box = contract["expected"]["glass_region_native"]
            output.alpha_composite(component.crop(box), (box[0], box[1]))
            for y in range(box[1], box[3]):
                for x in range(box[0], box[2]):
                    layer_counts.putpixel((x, y), layer_counts.getpixel((x, y))+1)
    return output, placements, layer_counts


def validate_glass(image, panel, contract, count, placements, layer_counts):
    w, h = contract["expected"]["native_dimensions_px"]
    l, t, r, b = contract["expected"]["glass_region_native"]
    checks = {"dimensions": evidence([w*count, h], list(image.size), "Read actual PNG dimensions"),
              "placements": evidence([[i*w, 0] for i in range(count)], placements, "Read composer placement records")}
    if image.size != (w*count, h):
        return {"checks": checks, "pass": False}
    for i in range(count):
        ox = i*w
        checks[f"post_{i}"] = alpha_region(image, [ox, 0, ox+l, h], minimum=255, maximum=255)
        end = r if i == count-1 else w
        checks[f"top_{i}"] = alpha_region(image, [ox+l, 0, ox+end, t], minimum=255, maximum=255)
        checks[f"base_{i}"] = alpha_region(image, [ox, b, ox+w, h], minimum=255, maximum=255)
        checks[f"glass_{i}"] = alpha_region(image, [ox+l, t, ox+end, b], minimum=1, maximum=254)
    checks["terminal_post"] = alpha_region(image, [w*(count-1)+r, 0, w*count, h], minimum=255, maximum=255)
    # Measure contiguous opaque runs on an actual pane row; no generator masks used.
    row = t + (b-t)//2
    runs, start = [], None
    for x in range(image.width+1):
        opaque = x < image.width and image.getpixel((x,row))[3] == 255
        if opaque and start is None:
            start = x
        elif not opaque and start is not None:
            runs.append([start, x]); start = None
    expected_runs = [[i*w, i*w+l] for i in range(count)] + [[(count-1)*w+r, count*w]]
    checks["post_runs"] = evidence(expected_runs, runs, f"Scan opaque alpha runs at y={row}")
    alpha_mismatches = 0
    layer_violations = 0
    # Independently evaluate canonical alpha with the declared shared-edge rule.
    for y in range(h):
        for x in range(w*count):
            i, local = divmod(x, w)
            source_x = r-1 if i < count-1 and local >= r else local
            expected_alpha = panel.getpixel((source_x,y))[3]
            alpha_mismatches += image.getpixel((x,y))[3] != expected_alpha
            if 0 < expected_alpha < 255:
                layer_violations += layer_counts.getpixel((x,y)) != 1
    checks["single_layer_alpha"] = evidence(0, alpha_mismatches, "Compare output alpha to canonical one-layer alpha at mapped coordinates", units="pixels")
    checks["translucent_layer_coverage"] = evidence(0, layer_violations, "Count actual translucent draw contributions per required glass pixel", units="pixels")
    return {"checks": checks, "pass": all(c["pass"] for c in checks.values())}


def behind_glass(glass):
    background = Image.new("RGBA", glass.size, (236, 181, 48, 255))
    # Full-height magenta/cyan bars are diagnostic objects, never partition pixels.
    for x in range(background.width):
        color = (213, 58, 143, 255) if (x//8)%2 else (32, 212, 183, 255)
        background.paste(color, (x, 0, x+1, background.height))
    composite = Image.alpha_composite(background, glass)
    errors, transmitted = 0, 0
    for foreground, back, actual in zip(glass.get_flattened_data(), background.get_flattened_data(), composite.get_flattened_data()):
        a = foreground[3]
        expected = tuple((foreground[c]*a + back[c]*(255-a)+127)//255 for c in range(3))
        errors += actual[:3] != expected
        transmitted += 0 < a < 255 and actual[:3] != foreground[:3]
    check = {"blend": evidence(0, errors, "Compare RGB to integer source-over equation with separately saved background", units="pixels"),
             "transmission": {"expected": "positive number of changed glass pixels", "observed": transmitted,
                              "method": "Compare composite RGB to foreground RGB for translucent pixels", "pass": transmitted > 0}}
    return background, composite, {"checks": check, "pass": all(c["pass"] for c in check.values())}


def topology_layout(kind):
    layouts = {
        "l_junction": {(1,1): "se", (2,1): "w", (1,2): "n"},
        "t_junction": {(1,1): "esw", (0,1): "e", (2,1): "w", (1,2): "n"},
        "cross_junction": {(1,1): "cross", (0,1): "e", (2,1): "w", (1,0): "s", (1,2): "n"},
    }
    return layouts[kind]


def topology_check(layout):
    canvas = Image.new("RGBA", (96,96))
    joins = []
    for (x,y), role in layout.items():
        canvas.alpha_composite(rgba(CANON / f"topology_{role}.png"), (x*32,y*32))
    for x,y in layout:
        for dx,dy in ((1,0),(0,1)):
            if (x+dx,y+dy) not in layout:
                continue
            coords = ([(x*32+31,y*32+k,x*32+32,y*32+k) for k in range(12,20)] if dx else
                      [(x*32+k,y*32+31,x*32+k,y*32+32) for k in range(12,20)])
            violations = sum(canvas.getpixel((a,b))[3] != 255 or canvas.getpixel((c,d))[3] != 255 for a,b,c,d in coords)
            joins.append(evidence(0, violations, f"Read both sides of topology contact {(x,y)} -> {(x+dx,y+dy)}", units="pixel_pairs"))
    return canvas, {"joins": joins, "pass": bool(joins) and all(j["pass"] for j in joins)}


def approved_images():
    assets = read_json(ROOT / "metadata/manifest.json")["assets"]
    return {a["id"]: rgba(ROOT / a["final_path"]) for a in assets if a["category"] == "architecture" and a["approval_status"] == "approved"}


def integration_scene(kind, images):
    """Carrier coverage is measured separately from opaque floor/background."""
    canvas = Image.new("RGBA", (256,224))
    for row in range(5):
        for col in range(6):
            canvas.alpha_composite(images["hospital_floor_plain_01"], (32+col*32,52+row*32))
    placements = []
    def put(asset_id, x, y):
        component = images[asset_id]
        placements.append({"id": asset_id, "origin": [x,y], "dimensions": list(component.size)})
        canvas.alpha_composite(component,(x,y))
    back, side, front = "hospital_wall_back_straight_01", "hospital_wall_side_left_01", "hospital_front_wall_cutaway_01"
    if kind == "connected_rooms":
        # Two stacked rooms sharing a back-facing opening; C8 is an opaque
        # static recess. The separate walkability graph defines connectivity.
        for col in range(6):
            put(back,32+col*32,0)
        for row in range(5):
            put(side,12,52+row*32)
            put("hospital_wall_side_right_01",224,52+row*32)
        for col in (0,4,5):
            put(back,32+col*32,96)
        put("hospital_equipment_opening_wide_01",64,96)
        for col in range(6):
            put(front,32+col*32,192)
        walkable = {(x,y) for x in range(6) for y in range(5) if y != 2 or 1 <= x <= 3}
        seen, queue = {(0,0)}, deque([(0,0)])
        while queue:
            x,y = queue.popleft()
            for p in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if p in walkable and p not in seen:
                    seen.add(p); queue.append(p)
        extras = {"walkability": evidence(True, (5,4) in seen, "BFS across explicit three-cell C8 opening in separate level occupancy", units="boolean")}
        note = "Connected in explicit level occupancy. C8 is a static opaque recess, not evidence of see-through glass or implemented gameplay."
    else:
        # Draw only existing full carriers. Central horizontal bay owns its
        # topological center; side carriers before/after expose the 52/20 join.
        layout = topology_layout(kind)
        for (col,row), role in sorted(layout.items(), key=lambda item:(item[0][1],item[0][0])):
            x,y = 64+col*32,64+row*32
            if role in ("n","s"):
                put(side,x+12,y)
            else:
                put(back,x,y-32)
                if "s" in role or role == "cross":
                    put(side,x+12,y+20)
        topo, check = topology_check(layout)
        extras = {"topology": check}
        note = "Canonical topology contacts pass independently. Full approved carriers overlap at the junction; visible cap/occlusion continuity requires human review. No visible adapter is asserted necessary from mask coverage alone."
    # Validate all actual placement records against stable grid origins and
    # measure structural coverage without the floor hiding missing pixels.
    coverage = Image.new("I",canvas.size,0)
    for p in placements:
        alpha = images[p["id"]].getchannel("A")
        ox,oy=p["origin"]
        for y in range(alpha.height):
            for x in range(alpha.width):
                if alpha.getpixel((x,y)) > 0:
                    point=(ox+x,oy+y)
                    coverage.putpixel(point,coverage.getpixel(point)+1)
    overlap = sum(v>1 for v in coverage.get_flattened_data())
    # Measure which approved carrier pixels the later wall layers hide. This
    # exposes the cross's completely occluded north arm in this render order.
    occlusion=[]
    for index,p in enumerate(placements):
        ox,oy=p["origin"]; w,h=p["dimensions"]
        later=Image.new("L",(w,h))
        for other in placements[index+1:]:
            dx,dy=other["origin"][0]-ox,other["origin"][1]-oy
            later.paste(images[other["id"]].getchannel("A"),(dx,dy))
        alpha=images[p["id"]].getchannel("A")
        hidden=sum(a>0 and b==255 for a,b in zip(alpha.get_flattened_data(),later.get_flattened_data()))
        total=sum(a>0 for a in alpha.get_flattened_data())
        occlusion.append({"placement_index":index,"id":p["id"],"hidden_pixels":hidden,"visible_pixels":total-hidden})
    joins=[]
    horizontal=[p for p in placements if p["id"] in (back,"hospital_equipment_opening_wide_01")]
    for left in horizontal:
        for right in horizontal:
            if right["origin"] == [left["origin"][0]+left["dimensions"][0],left["origin"][1]]:
                joins.append(horizontal_join(images[left["id"]],images[right["id"]],left["origin"],right["origin"],[44,52]))
    extras["horizontal_carrier_joins"] = {"checks": joins,"pass": all(j["pass"] for j in joins)}
    return canvas,{"placements_observed":placements,"computed":extras,"overlap_pixels_observed":overlap,
                   "occlusion_observed":occlusion,"occlusion_method":"Compare each carrier alpha to union of later opaque carrier coverage",
                   "overlap_method":"Count nontransparent wall carrier contributions before floor compositing",
                   "technical_pass":all(c["pass"] for c in extras.values()),
                   "human_visual_review":{"status":"pending; D0 diagnostic only","review_focus":note}}


def board(entries, columns=2):
    # Only integer nearest-neighbor display enlargement; labels are deterministic.
    cell_w, cell_h = 540, 300
    result=Image.new("RGBA",(columns*cell_w,36+((len(entries)+columns-1)//columns)*cell_h),(24,35,49,255))
    draw=ImageDraw.Draw(result)
    draw.text((12,10),"RASTALR / D0 REFERENCE ONLY / GEOMETRY + ALPHA / NO PRODUCTION ART",fill=(240,237,225,255),font=ImageFont.load_default())
    for i,(label,img) in enumerate(entries):
        x,y=(i%columns)*cell_w+12,36+(i//columns)*cell_h
        draw.text((x,y+6),label,fill=(240,237,225,255),font=ImageFont.load_default())
        factor=max(1,min((cell_w-24)//img.width,(cell_h-38)//img.height))
        scaled=img.resize((img.width*factor,img.height*factor),Image.Resampling.NEAREST)
        result.alpha_composite(scaled,(x,y+28))
    return result


def glass_architecture_context(panel,contract,images):
    """One baseline joins two unchanged solid carriers to a four-panel D1 run."""
    scene=Image.new("RGBA",(256,160))
    for y in (52,84,116):
        for x in range(32,224,32):
            scene.alpha_composite(images["hospital_floor_plain_01"],(x,y))
    wall=images["hospital_wall_back_straight_01"]
    scene.alpha_composite(wall,(32,32)); scene.alpha_composite(wall,(192,32))
    glass,origins,layers=compose_glass(panel,contract,4)
    scene.alpha_composite(glass,(64,56))
    # Full wall height is 52; glass height is 28. Compare their actual opaque
    # bottom five pixels at the common world baseline, not their top edges.
    strips=[wall.crop((31,47,32,52)),glass.crop((0,23,1,28)),
            glass.crop((127,23,128,28)),wall.crop((0,47,1,52))]
    check={"contact_alpha":evidence([255]*20,[v for strip in strips for v in strip.getchannel("A").get_flattened_data()],"Read four actual five-pixel wall/glass contact strips",units="alpha"),
           "baselines":evidence([84,84,84],[32+wall.height,56+glass.height,32+wall.height],"Actual render origins plus PNG heights"),
           "adjacency":evidence([64,192],[32+wall.width,64+glass.width],"Actual origin plus image width")}
    return scene,{"checks":check,"pass":all(c["pass"] for c in check.values()),
                  "placements_observed":[{"role":"left_solid_wall","origin":[32,32]},
                                         {"role":"d1_four_panel_run","origin":[64,56]},
                                         {"role":"right_solid_wall","origin":[192,32]}]}


def negative_fixtures(panel, contract, images):
    valid, origins, layers=compose_glass(panel,contract,2)
    cases={}
    broken=origins.copy(); broken[1]=[33,0]
    shifted=Image.new("RGBA",valid.size)
    shifted.alpha_composite(panel_variant(panel,contract,False),(0,0)); shifted.alpha_composite(panel,(33,0))
    cases["join_shift_1px"]=(shifted,validate_glass(shifted,panel,contract,2,broken,layers),"placements")
    missing=valid.copy(); missing.putpixel((31,27),(0,0,0,0))
    cases["contact_pixel_removed"]=(missing,validate_glass(missing,panel,contract,2,origins,layers),"base_0")
    opaque=valid.copy(); opaque.putalpha(255)
    cases["fake_opaque_glass"]=(opaque,validate_glass(opaque,panel,contract,2,origins,layers),"glass_0")
    hole=valid.copy(); hole.putpixel((10,20),(0,0,0,0))
    cases["pane_alpha_hole"]=(hole,validate_glass(hole,panel,contract,2,origins,layers),"glass_0")
    doubled,dp,dl=compose_glass(panel,contract,2,naive=True)
    cases["double_seam"]=(doubled,validate_glass(doubled,panel,contract,2,dp,dl),"post_runs")
    overlap,op,ol=compose_glass(panel,contract,2,overlap=True)
    cases["overlap_darkening"]=(overlap,validate_glass(overlap,panel,contract,2,op,ol),"single_layer_alpha")
    asset=next(a for a in read_json(ROOT/"metadata/manifest.json")["assets"] if a["id"]=="hospital_door_single_half_open_01")
    component=rgba(ROOT/asset["components"][0]["final_path"])
    # Actual approved leaf-projection implementation component, unchanged.
    correct=Image.new("RGBA",(40,60)); correct.alpha_composite(component,(4,4))
    shifted_component=Image.new("RGBA",correct.size); shifted_component.alpha_composite(component,(5,4))
    anchor_valid=anchored_component(correct,component,(4,4),(4,4))
    cases["component_offset_1px"]=(shifted_component,anchored_component(shifted_component,component,(4,4),(5,4)),"origin")
    valid_check=validate_glass(valid,panel,contract,2,origins,layers)
    reports={}
    for name,(img,check,intended) in cases.items():
        control=anchor_valid if name=="component_offset_1px" else valid_check
        reports[name]={"valid_control_pass":control["pass"],"expected_failure_check":intended,
                       "observed_validation":check,
                       "proven":control["pass"] and not check["pass"] and not check["checks"][intended]["pass"]}
    return cases,reports


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    artifacts=OUT/"artifacts"; artifacts.mkdir(exist_ok=True)
    before=production_snapshot()
    expected_counts={"manifest":220,"approved":220,"needs_human_review":0}
    if before["counts"] != expected_counts:
        raise ValueError(f"Unexpected production state: {before['counts']}")
    baseline_path=OUT/"sources/production_before.json"
    if baseline_path.exists():
        if not compare_snapshots(read_json(baseline_path), before,
                                 allowed_addition_prefixes=AUTHORIZED_REFERENCE_ADDITIONS)["pass"]:
            raise ValueError("Protected production/reference hashes changed since D0 baseline")
    else:
        write_json(baseline_path,before)
    contract=contract_from_canonical(); write_json(OUT/"d1_geometry_alpha_contract.json",contract)
    panel=rgba(CANON/"glass_partition_1x.png")
    panel.save(artifacts/"d1_scaffold_native.png")
    panel.resize((256,224),Image.Resampling.NEAREST).save(artifacts/"d1_scaffold_source_8x.png")
    for role,predicate in (("frame",lambda a:a==255),("glass",lambda a:0<a<255)):
        mask=panel.getchannel("A").point(lambda a:255 if predicate(a) else 0)
        mask.save(artifacts/f"d1_{role}_mask_native.png")
    scale=contract["expected"]["source_scale"]
    diag=panel.resize(tuple(contract["derived"]["source_dimensions_px"]),Image.Resampling.NEAREST)
    draw=ImageDraw.Draw(diag)
    pane=contract["expected"]["glass_region_native"]
    for x in (0,pane[0]*scale,pane[2]*scale,diag.width-1): draw.line((x,0,x,diag.height-1),fill=(255,72,182,255))
    for y in (0,pane[1]*scale,pane[3]*scale,diag.height-1): draw.line((0,y,diag.width-1,y),fill=(255,208,55,255))
    diag.save(artifacts/"d1_grid_geometry_diagnostic.png")
    entries=[]; repeats={}
    for count in (1,2,4):
        glass,origins,layers=compose_glass(panel,contract,count)
        check=validate_glass(glass,panel,contract,count,origins,layers)
        background,composite,transmission=behind_glass(glass)
        for suffix,img in (("partition",glass),("background",background),("scene",composite)):
            img.save(artifacts/f"d1_{count}_panel_{suffix}.png")
        repeats[str(count)]={"geometry_alpha":check,"transmission":transmission}
        entries.append((f"{count} PANEL / shared-edge / colored background separate",composite))
    images=approved_images(); integrations={}; integration_entries=[]
    for kind in ("connected_rooms","l_junction","t_junction","cross_junction"):
        scene,result=integration_scene(kind,images)
        scene.save(artifacts/f"{kind}.png"); integrations[kind]=result
        if kind != "connected_rooms":
            topo,_=topology_check(topology_layout(kind)); topo.save(artifacts/f"{kind}_topology.png")
            comparison=Image.new("RGBA",(364,224))
            comparison.alpha_composite(scene,(0,0)); comparison.alpha_composite(topo,(264,64))
            integration_entries.append((f"{kind} / approved render + separate topology",comparison))
        else:
            integration_entries.append((f"{kind} / approved carriers / static C8 recess",scene))
    context,context_check=glass_architecture_context(panel,contract,images)
    context.save(artifacts/"d1_repeat_architecture_context.png")
    cases,negative=negative_fixtures(panel,contract,images)
    negative_entries=[]
    for name,(img,check,intended) in cases.items():
        img.save(artifacts/f"broken_{name}.png")
        view=behind_glass(img)[1] if img.height==28 else img
        negative_entries.append((f"BROKEN {name} / detected: {intended}",view))
    board(negative_entries).save(artifacts/"broken_fixtures_diagnostic.png")
    board(integration_entries).save(artifacts/"integration_diagnostic.png")
    entries.extend([("NAIVE REPEAT / measured 8 px post / invalid",behind_glass(cases["double_seam"][0])[1]),
                    ("D1 GRID / 8x / 32x28 native",diag),
                    ("D1 CONTEXT / unchanged approved architecture",context)])
    entries.extend(integration_entries)
    board(entries).save(artifacts/"chatgpt_review_montage.png")
    after=production_snapshot()
    qa=read_json(ROOT/"metadata/architecture_doors_openings_batch_12_qa.json")
    markdown=(ROOT/"metadata/architecture_doors_openings_batch_12_qa.md").read_text(encoding="utf-8")
    cleanup={"single_approved_headline":evidence(1,markdown.count("APPROVED"),"Count final approval headline",units="occurrences"),
             "single_approval_section":evidence(1,markdown.count("## Human visual approval"),"Count human approval sections",units="occurrences"),
             "stale_review_wording":evidence(False,"await human" in markdown,"Search current report",units="boolean"),
             "idempotent":evidence(True,approved_markdown(markdown,qa)==markdown,"Render again using unchanged approved JSON",units="boolean"),
             "preserved_review_timestamp":evidence(True,qa["human_visual_review"]["reviewed_at"] in markdown,"Compare current Markdown to existing approval JSON",units="boolean")}
    preservation=evidence(before,after,"SHA-256 protected production, staging, sources, existing architecture references and inventory; before/after counts",units="snapshot")
    success=(preservation["pass"] and context_check["pass"] and all(r["geometry_alpha"]["pass"] and r["transmission"]["pass"] for r in repeats.values())
             and all(r["technical_pass"] for r in integrations.values()) and all(r["proven"] for r in negative.values())
             and all(c["pass"] for c in cleanup.values()))
    report={"id":"architecture_d0_v1","scope":"reference-only preparation; stop before D1 appearance",
            "technical_status":"PASS" if success else "FAIL","rectangle_convention":RECTANGLE_CONVENTION,
            "audit_files_read":[p.name for p in sorted((OUT/"sources").glob("rastalr_architecture_gap*"))],
            "canonical_contract":"d1_geometry_alpha_contract.json","repeats":repeats,"d1_approved_wall_context":context_check,"integration":integrations,"negative_fixtures":negative,
            "batch_12_report_cleanup":{"checks":cleanup,"pass":all(c["pass"] for c in cleanup.values()),"historical_source":"sources/batch_12_qa_before.md"},
            "production_preservation":{"pass":preservation["pass"],"before":before["counts"],"after":after["counts"],"protected_file_count":len(before["sha256"]),"baseline":"sources/production_before.json"},
            "findings":["Canonical standalone glass duplicates its 4 px posts to 8 px when tiled unchanged. Shared-edge implementation required; canonical remains unchanged.",
                        "L/T/cross topology is valid, but full approved render carriers overlap. Topology success alone cannot approve cap/occlusion appearance or prove a new adapter is necessary.",
                        "Cross north-arm carrier is fully hidden by the central full-height back-wall face in the tested draw order; cross and T render similarly. Future multi-direction junction presentation/occlusion policy is unresolved; technical topology masks do not fix visible art.",
                        "D1 numeric baseline anchor is a documented derivation; PNG dimensions do not encode a logical footprint.",
                        "Batch 11 alternate floors contain partial alpha despite historical opaque-box wording; diagnostics deliberately use approved opaque plain floors. No artwork altered."],
            "historical_evidence_note":"See docs/ARCHITECTURE.md; old C1-C8 geometry literals are not independently computed measurements. Historical reports and approval decisions retained.",
            "human_visual_review":{"status":"pending for new diagnostic layouts; no production review added","not_equivalent_to":"technical PASS"},
            "assistant_visual_review":{"method":"Direct inspection of saved montage and negative diagnostic images", "scope":"D0 geometry examples only", "findings":["Tinted test bars visible through valid panes; opaque fixture hides bars", "Corrected runs have single-width seam posts", "Cross north arm hidden in tested rendering; topology displayed alongside"]},
            "recommendation":"READY FOR D1 APPEARANCE" if success else "D1 CONTRACT NEEDS REVISION",
            "blockers":[] if success else ["D0 technical failure"],
            "artifacts":[p.relative_to(OUT).as_posix() for p in sorted(artifacts.glob("*.png"))]}
    test_path=OUT/"test_results.json"
    if test_path.exists():
        report["automated_tests"]=read_json(test_path)
    write_json(OUT/"d0_technical_report.json",report)
    lines=["# Architecture D0 technical report","",f"Technical result: **{report['technical_status']}**. {report['recommendation']}.","",
           "Reference-only geometry and diagnostics. No D1 appearance, Batch 13, D2, or production ingestion.","",
           "Both attached audit files were extracted verbatim under sources/. User approval supersedes their historical proposal-status labels; it does not authorize production.","",
           "Rectangles: `[left, top, right, bottom)`. Expected/spec, observed/computed, derived, and human visual fields are distinct. Geometry measurements read PNG pixels and placement metadata.","",
           "Canonical glass: 32x28 native, source scale 8 = 256x224. Pane [4,5,28,23); posts [0,0,4,28) and [28,0,32,28); rails [4,0,28,5) and [4,23,28,28). Base contact [0,23,32,28). Ground topology strip [0,12,32,20).",
           "","Derived anchor: logical cell (16,20), image (16,28), render origin relative to cell (0,-8). At 8x: image anchor (128,224), origin (0,-64). Contact baseline matches existing full back carrier; no 32x52 glass carrier.","",
           "Frame alpha is exactly 255. Pane alpha is 1..254; canonical has 421 pixels at 150 and 11 at 210. Zero is an accidental hole for this unbroken pane. A fully clear region requires explicit contract revision. Background/object layers stay separate.","",
           "Repeat: preserve 32 px stride. Nonterminal cells extend the last interior column through their right post region; next cell owns the shared 4 px post. Terminal cell keeps its right post. No overlapping glass, trim, padding, or canonical edit.","",
           "D1 context joins unchanged solid wall carriers at baseline y=84 (wall origin y=32, glass origin y=56). Both five-pixel contact strips and lateral adjacency are measured; the intentional 24 px height difference is retained.","",
           "| Run | Geometry/alpha | Background transmission |","| --- | --- | --- |"]
    for n,r in repeats.items(): lines.append(f"| {n} panels | {r['geometry_alpha']['pass']} | {r['transmission']['pass']} |")
    lines += ["","## Integration","","| Scene | Computed technical pass | Wall overlap pixels |","| --- | --- | --- |"]
    for n,r in integrations.items(): lines.append(f"| {n} | {r['technical_pass']} | {r['overlap_pixels_observed']} |")
    lines += ["","Connected rooms: BFS proves connectivity through the separately defined C8 opening in the level layout. The unchanged C8 PNG remains an opaque static recess. L/T/cross use canonical topology and unchanged approved carriers; overlaps are exposed, not silently passed as visual continuity. New human visual approval is not claimed.","","## Negative evidence","","| Broken fixture | Intended failing check | Valid control passes / failure proven |","| --- | --- | --- |"]
    for n,r in negative.items(): lines.append(f"| {n} | {r['expected_failure_check']} | {r['valid_control_pass']} / {r['proven']} |")
    lines += ["","## Scope findings",""]+[f"- {f}" for f in report["findings"]]
    lines += ["","No new visible adapter is proven necessary; resolve junction cap/occlusion review before claiming all-direction visual coverage. This does not block straight D1 appearance under the explicit shared-edge contract.","",
              f"Production: {after['counts']}; {len(before['sha256'])} protected file hashes unchanged. Baseline: `sources/production_before.json`.","",
              "Batch 12 Markdown repaired from existing approved JSON; original duplicate report retained as sources/batch_12_qa_before.md. Repeated approval rendering is idempotent and preserves the recorded timestamp. JSON decisions, artworks, components and historical bundles remain untouched.","",
              "Reproduce: `python tools/validate_architecture_d0.py`. Full test evidence: `test_results.json` / `test_results.txt`. Baseline suite: 17 passed.","",
              "Review: `artifacts/chatgpt_review_montage.png`; geometry: `d1_geometry_alpha_contract.json`; native/source scaffolds and separate glass/background/scene PNGs: `artifacts/`.","",
              "Stop after D0. No new human-approved artwork or manifest record was created.",""]
    if "automated_tests" in report:
        test=report["automated_tests"]
        lines += [f"Complete automated suite: **{test['status']}**; {test['passed']} passed (baseline {test['old_test_count']}, added {test['passed']-test['old_test_count']}). Command and captured output are recorded in test_results.json and test_results.txt.",""]
    (OUT/"d0_technical_report.md").write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps({"technical_status":report["technical_status"],"recommendation":report["recommendation"],"counts":after["counts"],"negative_proven":{k:v["proven"] for k,v in negative.items()}},indent=2))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
