"""D2 proposed geometry only. Deterministic regions; no appearance generation.

Run: python tools/validate_architecture_d2.py
Writes only master_validation_D2_v1; never regenerates historical D0/D1 evidence.
"""
from __future__ import annotations

import json
import zipfile
from pathlib import Path
from collections import Counter

from PIL import Image, ImageDraw, ImageFont

import validate_architecture_d0 as d0
import validate_architecture_d1 as d1
from rastalr_pipeline.geometry import alpha_region, anchored_component, evidence
from rastalr_pipeline.snapshot import compare_snapshots

ROOT=d0.ROOT
OUT=ROOT/"references/architecture/master_validation_D2_v1"
CONTRACT=OUT/"d2_geometry_alpha_contract_proposed.json"
STATUS="PROPOSED_FOR_HUMAN_GEOMETRY_REVIEW"


def snapshot():
    value=d1.task_snapshot()
    paths=list((ROOT/"references/camera").rglob("*"))+[ROOT/"docs/ARCHITECTURE.md",ROOT/"docs/ART_DIRECTION.md"]
    value["sha256"].update({p.relative_to(ROOT).as_posix():d0.digest(p) for p in paths if p.is_file()})
    return value


def proposed_contract():
    spec=d0.read_json(d0.CANON/"architecture_v2_spec.json")
    d1_contract=d0.read_json(d1.CONTRACT_PATH)
    side=d1.load(d0.CANON/"side_wall_left_1x.png")
    back=d1.load(d0.CANON/"back_wall_1x.png")
    glass=d1.load(d0.CANON/"glass_partition_1x.png")
    ns=d1.load(d0.CANON/"topology_ns.png")
    back_envelope=back.getchannel("A").getbbox()
    if spec["logical_grid_px"]!=32 or side.size!=(20,32) or back_envelope!=(0,0,32,52) or glass.size!=(32,28) or ns.getchannel("A").getbbox()!=(12,0,20,32):
        raise ValueError("Canonical geometry differs from inspected authority; stop for review")
    side_extra=side.width-spec["topology_wall_thickness_px"]
    back_visible_height=back_envelope[3]-back_envelope[1]
    proposed_extra=round(side_extra*glass.height/back_visible_height)
    visible_width=spec["topology_wall_thickness_px"]+proposed_extra
    sources=["docs/ARCHITECTURE.md","docs/ART_DIRECTION.md","references/camera/rastalr_camera_reference_v1.png",
             "references/architecture/rastalr_architecture_v2/architecture_v2_spec.json",
             "references/architecture/rastalr_architecture_v2/side_wall_left_1x.png",
             "references/architecture/rastalr_architecture_v2/back_wall_1x.png",
             "references/architecture/rastalr_architecture_v2/topology_ns.png",
             "references/architecture/rastalr_architecture_v2/topology_se.png",
             "references/architecture/rastalr_architecture_v2/topology_nw.png",
             "references/architecture/rastalr_architecture_v2/glass_partition_1x.png",
             "metadata/production_batch_11_architecture_foundation.json","tools/build_architecture_foundation_batch_11_review.py",
             "references/architecture/master_validation_D0_v1/sources/rastalr_architecture_gap_audit_scope_v1.json",
             "references/architecture/master_validation_D0_v1/d0_technical_report.md",
             "references/architecture/master_validation_D0_v1/d1_geometry_alpha_contract.json",
             "references/architecture/master_validation_D1_v1/d1_validation_report.json"]
    sources += [(d1.PACKAGE/"candidate"/name).relative_to(ROOT).as_posix() for name in d1.VIEW_FILES.values()]
    return {
        "id":"hospital_glass_partition_side_left_01","status":STATUS,"rectangle_convention":"[left, top, right, bottom)",
        "scope":"One reference-only proposal. No final art, approval, ingestion, or inventory entry.",
        "canonical_requirements":{"logical_grid_px":32,"source_scale":8,
                                  "orientation":"NS depth boundary at room left/west; room interior is east/right; +y goes south/toward viewer",
                                  "ground_strip":[12,0,20,32],"projection":spec["projection"],
                                  "normalization":"architecture_grid_preserving","transform_policy":"integer translation and exact 8x nearest-neighbor only; no rotation, transpose, warp, trim or safety padding"},
        "measured_authority":{"method":"Loaded PNG dimensions, mode, nonzero alpha bounds and histogram; semantic region roles are separately inferred/proposed",
                              "canonical_side_dimensions":list(side.size),"canonical_back_dimensions":list(back.size),"canonical_back_visible_envelope":list(back_envelope),
                              "canonical_glass_dimensions":list(glass.size),"topology_ns_alpha_bbox":list(ns.getchannel("A").getbbox()),
                              "canonical_side_alpha_histogram":{str(k):v for k,v in Counter(side.getchannel("A").get_flattened_data()).items()},
                              "approved_side_placement":"Batch 11 left module source crop [96,416,256,672) /8 = [12,52,32,84); review builder places side images at (12,52+32*r). Metadata anchor is wall_center, without a unique D2 numeric anchor."},
        "proposed_choices":{"logical_footprint_tiles":[1,1],"native_dimensions":[32,32],"visual_envelope":[12,0,12+visible_width,32],
                            "planning_id_note":"Current user-specified side_left ID supersedes the earlier audit's hospital_glass_partition_left_01 spelling; purpose and one-cell planning footprint remain the same.",
                            "carrier_reason":"Retain one full logical cell for direct topology registration and explicit exterior alpha; its transparent regions are declared cell space, not post-export safety padding.",
                            "side_compression_rule":"Choose linear scaling of the canonical extra visible width by D1/back visible heights, rounded to nearest native pixel. The canonical back PNG canvas is 32x60 but its measured visible envelope is 32x52. This is a presentation heuristic proposed for human review, not a recovered physical camera equation.",
                            "long_rail_width":2,"endpoint_support_depth":4,
                            "frame_reason":"4 px depth supports retain D1 family support cadence; two 2 px longitudinal rails leave a readable 10 px pane within the narrower side band. These are new side-facing choices, not a rotated D1.",
                            "pane_alpha":150,"pane_reason":"Use canonical/D0 base glass alpha 150. No 210 gleam is required in a flat geometry scaffold.",
                            "frame_rgba":[39,55,70,255],"glass_rgba":[158,205,216,150],
                            "height_interpretation":"Same nominal installed 28 px partition family as D1; the side view encodes reduced height as a narrower shallow band. It does not demonstrate a continuous 28 px elevation projection at a corner."},
        "derived":{"canonical_extra_side_width":side_extra,"scaled_extra_side_width_unrounded":side_extra*glass.height/back_visible_height,
                   "proposed_extra_side_width":proposed_extra,"visible_side_width":visible_width,
                   "calculation":"20 - 8 = 12; round(12 * 28 / 52) = 6; 8 + 6 = 14 visible pixels; carrier stays 32x32",
                   "source_dimensions":[256,256],"source_visual_envelope":[96,0,208,256],
                   "logical_cell_anchor":[16,16],"image_anchor":[16,16],"render_origin_relative_to_cell":[0,0],
                   "anchor_reason":"Cell-centered NS topology axis x=16; registered full-cell carrier makes image and cell coordinates identical. Numeric anchor is proposed, not pre-existing D2 metadata.",
                   "north_endpoint_logical":[16,0],"south_endpoint_logical":[16,32],
                   "north_endpoint_image":[16,0],"south_endpoint_image":[16,32],
                   "d1_installed_baseline_mapping":d1_contract["derived"]["anchor"]},
        "regions":{"main":{"frame":{"west_rail":[12,0,14,32],"east_rail":[24,0,26,32],"north_support":[14,0,24,4],"south_support":[14,28,24,32]},
                            "pane":[14,4,24,28],"exterior":[[0,0,12,32],[26,0,32,32]],
                            "contact":{"north":[12,0,26,4],"south_terminal":[12,28,26,32]}},
                   "repeat":{"frame":{"west_rail":[12,0,14,32],"east_rail":[24,0,26,32],"north_support":[14,0,24,4]},
                              "pane":[14,4,24,32],"exterior":[[0,0,12,32],[26,0,32,32]],
                              "contact":{"north":[12,0,26,4],"south_west":[12,28,14,32],"south_east":[24,28,26,32]}}},
        "alpha_policy":{"frame":255,"pane":150,"exterior":0,"undeclared_zero_holes":"failure","opaque_glass":"failure"},
        "repeat":{"direction":[0,1],"stride":[0,32],"views_are_mutually_exclusive":True,
                  "representation":"One future logical asset; terminal main and nonterminal implementation views, no independent inventory entries",
                  "ownership":"Every cell owns its north support. The last cell also owns its south support. Nonterminal cells extend the pane to y=32; longitudinal rails continue unchanged.",
                  "derivation":"Side support intervals are measured along depth y, not across D1 x. The explicit side pane/frame rectangles define the extension; row 27 can be extended through rows 28..31 only within x=14..24. No D1 pixels are transformed.",
                  "allowed_view_difference":[14,28,24,32]},
        "corner_proposal":{"location":"Room north-west: D1 eastward from shared base endpoint, D2 southward along west boundary",
                           "endpoint_rule":"D1 left baseline endpoint and D2 north endpoint coincide. This is a base-edge registration; D1 centerline is 4 px north of its baseline edge.",
                           "ownership":"D1 retains its validated left post. D2 owns its north support below the shared baseline. No extra visible post, column or cover is added.",
                           "draw_order":["separate approved floor background","unchanged D1 run","D2 run"],
                           "deliberate_visible_occlusion":"none; footprints of the rendered layers touch but do not overlap",
                           "ground_elbow_component":{"rectangle_relative_to_D2_cell":[12,-8,16,0],"role":"proposed topology-only completion of missing 4x8 quadrant; not visible artwork","source":"canonical topology_se corner (east and south arms at a room north-west corner)"},
                           "unresolved":"D1 head rail is 28 px above the shared base, whereas the shallow D2 north support begins at the base. Ground/base contact does not establish upper-rail/elevation continuity. Human geometry decision required; no visible repair is proposed."},
        "human_review":{"approval":False,"required":["14 px band and 2 px rails readability","same-family height interpretation","unresolved D1/D2 head-rail transition","topology-only elbow completion"]},
        "sources_sha256":{name:d0.digest(ROOT/name) for name in sources},
    }


def scaffold(contract,view):
    image=Image.new("RGBA",tuple(contract["proposed_choices"]["native_dimensions"]),(0,0,0,0))
    regions=contract["regions"][view]
    image.paste(tuple(contract["proposed_choices"]["glass_rgba"]),tuple(regions["pane"]))
    for rect in regions["frame"].values(): image.paste(tuple(contract["proposed_choices"]["frame_rgba"]),tuple(rect))
    return image


def expected_role(x,y,view):
    # Independently stated coordinate predicate for the proposed contract;
    # deliberately does not read the raster builder's mask or image pixels.
    if x<12 or x>=26: return "exterior"
    if x<14 or x>=24 or y<4 or (view=="main" and y>=28): return "frame"
    return "pane"


def validate_scaffold(image,source,contract,view):
    checks={"mode":evidence("RGBA",image.mode,"Read reloaded native PNG mode",units="mode"),
            "dimensions":evidence(contract["proposed_choices"]["native_dimensions"],list(image.size),"Read reloaded native PNG size"),
            "source_mode":evidence("RGBA",source.mode,"Read saved 8x PNG mode",units="mode"),
            "source_dimensions":evidence(contract["derived"]["source_dimensions"],list(source.size),"Read 8x PNG size",units="source_px")}
    if not all(c["pass"] for c in checks.values()): return d1.group(checks)
    errors=sum(source.getpixel((x,y))!=image.getpixel((x//8,y//8)) for y in range(256) for x in range(256))
    checks["exact_8x_blocks"]=evidence(0,errors,"Read all source pixels against native 8x8 blocks",units="pixels")
    checks["native_roundtrip"]=evidence(0,d1.pixel_difference(image,source.resize((32,32),Image.Resampling.NEAREST)),"Compare all native RGBA after nearest-neighbor round-trip",units="pixels")
    checks["visible_envelope"]=evidence(contract["proposed_choices"]["visual_envelope"],list(image.getchannel("A").getbbox()),"Compute nonzero-alpha bounds")
    for role,rect in contract["regions"][view]["frame"].items(): checks[role]=alpha_region(image,rect,minimum=255,maximum=255)
    checks["pane"]=alpha_region(image,contract["regions"][view]["pane"],minimum=150,maximum=150)
    for i,rect in enumerate(contract["regions"][view]["exterior"]): checks[f"exterior_{i}"]=alpha_region(image,rect,minimum=0,maximum=0)
    return d1.group(checks,observed_alpha_histogram=dict(Counter(image.getchannel("A").get_flattened_data())),
                    conformance_to=STATUS)


def assemble(main,repeat,count,*,stride=32,overlap=False):
    run=Image.new("RGBA",(32,32*count)); layers=Image.new("I",run.size,0); origins=[]
    for i in range(count):
        image=main if i==count-1 else repeat
        y0=i*stride; origins.append([0,y0]); run.alpha_composite(image,(0,y0))
        for y in range(32):
            for x in range(32):
                if y+y0<run.height and 0<image.getpixel((x,y))[3]<255:
                    p=(x,y+y0); layers.putpixel(p,layers.getpixel(p)+1)
    if overlap:
        run.alpha_composite(main.crop((14,4,24,28)),(14,4))
        for y in range(4,28):
            for x in range(14,24): layers.putpixel((x,y),layers.getpixel((x,y))+1)
    return run,origins,layers


def validate_run(run,origins,layers,count):
    checks={"dimensions":evidence([32,32*count],list(run.size),"Read assembled image size"),
            "origins":evidence([[0,32*i] for i in range(count)],origins,"Read actual depth placements")}
    if run.size!=(32,32*count): return d1.group(checks)
    bad={"frame":0,"pane":0,"exterior":0}; layer_bad=0
    for y in range(run.height):
        view="main" if y//32==count-1 else "repeat"
        for x in range(32):
            role=expected_role(x,y%32,view); a=run.getpixel((x,y))[3]
            bad[role]+=a!={"frame":255,"pane":150,"exterior":0}[role]
            if role=="pane": layer_bad+=layers.getpixel((x,y))!=1
    for role,total in bad.items(): checks[role]=evidence(0,total,"Read alpha against independent proposed-region predicate",units="pixels")
    checks["single_translucent_layer"]=evidence(0,layer_bad,"Count actual translucent draw contributions at required pane pixels",units="pixels")
    # Measure contiguous opaque supports at x=18, independently of compositor.
    spans=[]; start=None
    for y in range(run.height+1):
        solid=y<run.height and run.getpixel((18,y))[3]==255
        if solid and start is None: start=y
        if not solid and start is not None: spans.append([start,y]); start=None
    checks["support_spans"]=evidence([[i*32,i*32+4] for i in range(count)]+[[32*count-4,32*count]],spans,"Scan opaque runs along depth at x=18")
    for seam in range(1,count):
        checks[f"contact_{seam}"]=alpha_region(run,[12,seam*32,26,seam*32+4],minimum=255,maximum=255)
    return d1.group(checks,conformance_to=STATUS)


def transmission(run,count):
    backs,objects=d1.backgrounds(run.size)
    # Explicit object inside the narrow side pane, independent from the asset.
    objects=Image.new("RGBA",run.size)
    for i in range(count): objects.paste((242,187,43,255),(16,i*32+10,22,i*32+20))
    backs["colored_object"]=Image.alpha_composite(backs["colored"],objects)
    scenes={name:Image.alpha_composite(bg,run) for name,bg in backs.items()}
    pane=responsive=frame_response=object_count=object_response=0; errors=0
    for y in range(run.height):
        for x in range(32):
            role=expected_role(x,y%32,"main" if y//32==count-1 else "repeat")
            response=scenes["light"].getpixel((x,y))!=scenes["dark"].getpixel((x,y))
            pane+=role=="pane"; responsive+=role=="pane" and response
            frame_response+=role=="frame" and response
            if role=="pane" and objects.getpixel((x,y))[3]:
                object_count+=1; object_response+=scenes["colored"].getpixel((x,y))!=scenes["colored_object"].getpixel((x,y))
            f=run.getpixel((x,y))
            for name,bg in backs.items():
                b=bg.getpixel((x,y)); expected=tuple((f[c]*f[3]+b[c]*(255-f[3])+127)//255 for c in range(3))+(255,)
                errors+=scenes[name].getpixel((x,y))!=expected
    return d1.group({"pane_response":evidence(pane,responsive,"Toggle light/dark background at independent pane coordinates",units="pixels"),
                     "frame_invariance":evidence(0,frame_response,"Compare frame RGB on different backgrounds",units="pixels"),
                     "object_response":evidence(object_count,object_response,"Toggle separate yellow object behind pane",units="pixels"),
                     "source_over":evidence(0,errors,"Compare all composites to integer source-over equation",units="pixels")}),backs,objects,scenes


def wall_context(run,origin=(32,32),drift=(0,0)):
    wall=d1.load(ROOT/"assets/architecture/hospital_wall_side_left_01.png")
    floor=d1.load(ROOT/"assets/architecture/hospital_floor_plain_01.png")
    ox,oy=origin; where=(ox,oy+32); actual=(where[0]+drift[0],where[1]+drift[1])
    lower=(ox+12,oy+32+run.height)
    size=(ox+128,oy+64+run.height)
    bg=Image.new("RGBA",size)
    for y in range(oy,size[1],32):
        for x in range(ox,ox+128,32): bg.alpha_composite(floor,(x,y))
    structure=Image.new("RGBA",size)
    structure.alpha_composite(wall,(ox+12,oy)); structure.alpha_composite(wall,lower); structure.alpha_composite(run,actual)
    checks={"anchored_run":anchored_component(structure,run,where,actual),
            "relative_origin":evidence([0,0],[actual[0]-where[0],actual[1]-where[1]],"Compute actual image origin relative to logical-cell origin"),
            "depth_endpoints":evidence([oy+32,lower[1]],[actual[1],actual[1]+run.height],"Compare loaded carrier ends to adjacent solid-wall endpoints"),
            "upper_wall_unchanged":anchored_component(structure,wall,(ox+12,oy),(ox+12,oy)),
            "lower_wall_unchanged":anchored_component(structure,wall,lower,lower)}
    for name,y in (("upper_solid",where[1]-1),("upper_glass",where[1]),("lower_glass",lower[1]-1),("lower_solid",lower[1])):
        checks[name]=alpha_region(structure,[ox+12,y,ox+26,y+1],minimum=255,maximum=255)
    return d1.group(checks,observed={"cell_origin":list(where),"render_origin":list(actual),"solid_origins":[[ox+12,oy],list(lower)]},
                    visual_limit="Visible band reduces from 20 to proposed 14 px (6 px inward-face setback); readability and height interpretation require human review"),Image.alpha_composite(bg,structure),bg,structure


def corner(main,repeat):
    d1_main=d1.load(d1.PACKAGE/"candidate"/d1.VIEW_FILES["main"])
    d1_repeat=d1.load(d1.PACKAGE/"candidate"/d1.VIEW_FILES["repeat"])
    horizontal,_,_=d1.assemble(d1_main,d1_repeat,2)
    vertical,_,_=assemble(main,repeat,2)
    size=(176,160); first=Image.new("RGBA",size); second=Image.new("RGBA",size)
    d1_origin=(64,36); d2_origin=(48,64)
    first.alpha_composite(horizontal,d1_origin); second.alpha_composite(vertical,d2_origin)
    overlaps=glass_overlap=0
    for a,b in zip(first.get_flattened_data(),second.get_flattened_data()):
        overlaps+=a[3]>0 and b[3]>0; glass_overlap+=0<a[3]<255 and 0<b[3]<255
    frame_pairs=sum(first.getpixel((x,63))[3]==255 and second.getpixel((x,64))[3]==255 for x in range(64,74))
    # Ground-only SE elbow at room NW. D1 baseline is the lower y edge of
    # its horizontal 8px ground strip. The missing quadrant is explicit.
    ground=Image.new("RGBA",size)
    ground.paste((82,110,136,255),(64,56,128,64)); ground.paste((82,110,136,255),(60,64,68,128))
    required=Image.new("RGBA",size)
    required.alpha_composite(d1.load(d0.CANON/"topology_se.png"),(48,44))
    missing=Image.new("RGBA",size)
    for y in range(size[1]):
        for x in range(size[0]):
            if required.getpixel((x,y))[3] and not ground.getpixel((x,y))[3]: missing.putpixel((x,y),(239,179,48,255))
    completed=Image.alpha_composite(ground,missing)
    remaining=sum(a[3]>0 and b[3]==0 for a,b in zip(required.get_flattened_data(),completed.get_flattened_data()))
    floor=d1.load(ROOT/"assets/architecture/hospital_floor_plain_01.png")
    bg=Image.new("RGBA",size)
    for y in range(32,160,32):
        for x in range(32,160,32): bg.alpha_composite(floor,(x,y))
    scene=Image.alpha_composite(Image.alpha_composite(bg,first),second)
    # Topmost pixels of actual D1 left post and actual D2 north support.
    first_y=min(y for y in range(size[1]) if first.getpixel((64,y))[3])
    second_y=min(y for y in range(size[1]) if second.getpixel((64,y))[3])
    d1_base=[d1_origin[0],d1_origin[1]+horizontal.height]
    d2_north=[d2_origin[0]+16,d2_origin[1]]
    checks={"base_endpoint":evidence(d1_base,d2_north,"Compare computed D1 left base endpoint (loaded origin+height) to D2 north endpoint (cell origin+NS axis)"),
            "d1_baseline":evidence([64,64],[d1_origin[0],d1_origin[1]+horizontal.height],"Read D1 render origin plus actual height"),
            "rendered_overlap_pixels":evidence(0,overlaps,"Count all pixels covered by both rendered layers",units="pixels"),
            "glass_overlap_pixels":evidence(0,glass_overlap,"Count two translucent glass contributions",units="pixels"),
            "adjacent_frame_pairs":evidence(10,frame_pairs,"Read opaque edge pairs across y=64 at x=64..73",units="pixel_pairs"),
            "topology_after_proposed_component":evidence(0,remaining,"Compare canonical SE alpha to ground union plus separate missing-region mask",units="pixels")}
    return {"base_and_topology_checks":d1.group(checks),"visual_connection_status":"UNRESOLVED_UPPER_RAIL_TRANSITION",
            "observed":{"D1_origin":list(d1_origin),"D2_origin":list(d2_origin),"D1_base_endpoint_computed":d1_base,"D2_north_endpoint_computed":d2_north,
                        "D1_post_top_y":first_y,"D2_north_support_y":second_y,"head_transition_gap_px":second_y-first_y,
                        "missing_ground_pixels_before_component":sum(a>0 for a in missing.getchannel("A").get_flattened_data()),
                        "ground_component_bbox":list(missing.getchannel("A").getbbox()),"rendered_overlap_pixels":overlaps,"hidden_connection_pixels":overlaps},
            "interpretation":"Base-frame adjacency and supplemented ground topology are feasible. They do not prove a continuous upper rail: the shallow side support begins 28 px below D1's head. No visible connector/column/cover was added; the separate 4x8 component is ground logic only.",
            "ownership":"D1 keeps its original post; D2 owns the north support; floor then D1 then D2; zero deliberate opaque occlusion"},scene,ground,missing,completed


def negative_controls(main,repeat):
    valid,origins,layers=assemble(main,repeat,2); control=validate_run(valid,origins,layers,2)
    cases={}
    def add(name,img,p,l,intended):
        check=validate_run(img,p,l,2)
        cases[name]={"image":img,"validation":check,"intended_check":intended,"valid_control_pass":control["pass"],
                     "proven":control["pass"] and not check["checks"][intended]["pass"]}
    img,p,l=assemble(main,repeat,2,stride=33); add("repeat_displacement_1px",img,p,l,"origins")
    img=valid.copy(); img.putpixel((12,32),(0,0,0,0)); add("broken_contact",img,origins,layers,"frame")
    img=valid.copy()
    for y in range(img.height):
        for x in range(32):
            if img.getpixel((x,y))[3]==150: img.putpixel((x,y),(*img.getpixel((x,y))[:3],255))
    add("opaque_glass",img,origins,layers,"pane")
    img=valid.copy(); img.putpixel((18,12),(0,0,0,0)); add("pane_hole",img,origins,layers,"pane")
    img,p,l=assemble(main,main,2); add("doubled_support",img,p,l,"support_spans")
    img,p,l=assemble(main,repeat,2,overlap=True); add("overlapping_glass",img,p,l,"single_translucent_layer")
    good,_,_,_=wall_context(valid); bad,scene,_,_=wall_context(valid,drift=(1,0))
    cases["anchor_mismatch_1px"]={"image":scene,"validation":bad,"intended_check":"relative_origin","valid_control_pass":good["pass"],"proven":good["pass"] and not bad["checks"]["relative_origin"]["pass"]}
    return cases


def board(entries):
    cw,ch=430,355
    image=Image.new("RGBA",(cw*3,40+ch*((len(entries)+2)//3)),(24,35,49,255)); draw=ImageDraw.Draw(image)
    draw.text((14,12),"D2 GEOMETRY PROPOSAL / HUMAN REVIEW REQUIRED / FLAT SCAFFOLDS / NO PRODUCTION APPROVAL",fill=(238,232,219),font=ImageFont.load_default())
    for i,(label,img) in enumerate(entries):
        x,y=(i%3)*cw+14,40+(i//3)*ch
        draw.text((x,y+4),label,fill=(238,232,219),font=ImageFont.load_default())
        factor=max(1,min((cw-28)//img.width,(ch-32)//img.height))
        enlarged=img.resize((img.width*factor,img.height*factor),Image.Resampling.NEAREST)
        image.alpha_composite(enlarged,(x,y+26))
    return image


def main():
    OUT.mkdir(exist_ok=True); artifacts=OUT/"artifacts"; artifacts.mkdir(exist_ok=True)
    contract=proposed_contract()
    if CONTRACT.exists() and d0.read_json(CONTRACT)!=contract: raise ValueError("Existing proposed contract differs; no automatic overwrite")
    d0.write_json(CONTRACT,contract)
    images={}; files={}; entries=[]
    for view in ("main","repeat"):
        stem="d2_scaffold" if view=="main" else "d2_repeat_scaffold"
        img=scaffold(contract,view); img.save(OUT/f"{stem}_native.png")
        img.resize((256,256),Image.Resampling.NEAREST).save(OUT/f"{stem}_source_8x.png")
        native=d1.load(OUT/f"{stem}_native.png"); source=d1.load(OUT/f"{stem}_source_8x.png")
        images[view]=native; files[view]=validate_scaffold(native,source,contract,view)
    diag=d1.load(OUT/"d2_scaffold_source_8x.png"); draw=ImageDraw.Draw(diag)
    for x in (96,112,160,192,208): draw.line((x,0,x,255),fill=(243,188,45,255))
    for y in (32,224): draw.line((0,y,255,y),fill=(240,76,163,255))
    diag.save(artifacts/"d2_grid_geometry_diagnostic.png")
    runs={}; results={}; backgrounds={}
    for n in (1,2,4):
        run,p,l=assemble(images["main"],images["repeat"],n); path=artifacts/f"d2_run_{n}_native.png"; run.save(path); run=d1.load(path)
        results[str(n)]={"geometry":validate_run(run,p,l,n)}
        trans,backs,objects,scenes=transmission(run,n); results[str(n)]["transmission"]=trans
        for name,bg in backs.items():
            bg.save(artifacts/f"d2_run_{n}_{name}_background.png"); scenes[name].save(artifacts/f"d2_run_{n}_{name}_composite.png")
        objects.save(artifacts/f"d2_run_{n}_object_layer.png"); runs[n]=run; backgrounds[n]=scenes
    entries=[("Standalone: 32x32 carrier / 14px visible",backgrounds[1]["colored_object"]),("Two depth cells / 32px stride",backgrounds[2]["colored_object"]),("Four depth cells / single supports",backgrounds[4]["colored_object"])]
    contexts={}
    for name,origin in (("original",(32,32)),("relocated",(64,64))):
        check,scene,bg,structure=wall_context(runs[2],origin=origin); contexts[name]=check
        for suffix,img in (("scene",scene),("background",bg),("structure",structure)): img.save(artifacts/f"d2_context_{name}_{suffix}.png")
        entries.append((f"{name}: approved 20px side / proposed 14px",scene))
    corner_result,corner_scene,ground,connector,completed=corner(images["main"],images["repeat"])
    for name,img in (("scene",corner_scene),("ground_before",ground),("ground_component_only",connector),("ground_completed",completed)): img.save(artifacts/f"d1_d2_corner_{name}.png")
    corner_overlay=corner_scene.copy(); draw=ImageDraw.Draw(corner_overlay)
    draw.line((60,36,60,64),fill=(240,76,163,255),width=1)
    draw.line((56,36,64,36),fill=(240,76,163,255)); draw.line((56,64,64,64),fill=(240,76,163,255))
    board([("Corner: head-rail transition unresolved",corner_overlay),("Ground strips before elbow completion",ground),("Separate topology-only 4x8 mask",connector)]).save(artifacts/"d1_d2_corner_diagnostic.png")
    entries.extend([("D1/D2 corner: 28px head transition unresolved",corner_overlay),("Grid diagnostic / yellow x, pink y",diag),("Main on light background",backgrounds[1]["light"]),("Main on dark background",backgrounds[1]["dark"])])
    board(entries).save(artifacts/"d2_geometry_review_montage.png")
    negative=negative_controls(images["main"],images["repeat"])
    for name,case in negative.items(): case["image"].save(artifacts/f"broken_{name}.png")
    board([(name,c["image"]) for name,c in negative.items()]).save(artifacts/"d2_negative_controls.png")
    preservation=compare_snapshots(d0.read_json(OUT/"production_before.json"),snapshot(),allowed_addition_prefixes=("references/architecture/master_validation_D2_v1/",))
    success=all(v["pass"] for v in files.values()) and all(v["geometry"]["pass"] and v["transmission"]["pass"] for v in results.values()) and all(v["pass"] for v in contexts.values()) and all(v["proven"] for v in negative.values()) and preservation["pass"] and corner_result["base_and_topology_checks"]["pass"]
    report={"contract_status":STATUS,"technical_conformance":"PASS" if success else "FAIL","files":files,"repeats":results,"contexts":contexts,"local_corner":corner_result,
            "negative_controls":{name:{k:v for k,v in c.items() if k!="image"} for name,c in negative.items()},"preservation":preservation,
            "recommendation":"READY FOR HUMAN GEOMETRY REVIEW" if success else "GEOMETRY BLOCKED",
            "limitations":["No human geometry approval; scaffold conforms only to the explicitly proposed contract.","Straight runs are technically consistent; D1/D2 upper-rail continuity remains unresolved and must be judged separately.","Ground elbow mask is reference-only topology, not a visible adapter or asset."]}
    if (OUT/"test_results.json").exists():
        report["tests"]=d0.read_json(OUT/"test_results.json")
        if report["tests"]["exit_code"]!=0: report["recommendation"]="GEOMETRY BLOCKED"; report["technical_conformance"]="FAIL"
    if (OUT/"visual_review.json").exists(): report["visual_review"]=d0.read_json(OUT/"visual_review.json")
    d0.write_json(OUT/"production_preservation.json",preservation); d0.write_json(OUT/"d2_geometry_report.json",report)
    lines=["# D2 geometry proposal and scaffold","",f"**{report['recommendation']}**. Technical conformance: {report['technical_conformance']}. Contract remains `{STATUS}`.","",
           "## Authority and proposal","","Canonical: 32 px logical grid, centered 8 px NS ground strip [12,0,20,32), scale 8, axis-aligned camera and shallow left-side presentation. Canonical side PNG measures 20x32; canonical back canvas 32x60 with measured visible envelope [0,0,32,52); D1 32x28. Approved back carriers are 32x52. No committed low-glass side geometry is specified. Sources and SHA-256 are listed in the contract.","",
           "Proposed native carrier **32x32**, source **256x256**. Visible envelope **[12,0,26,32)** = 14x32. Explicit presentation heuristic: retain 8 px topology reference width and scale the 12 px additional solid-side band by 28/52: round(12*28/52)=6; total 14. This heuristic is not a measured camera/height law. The cell carrier is declared registration space, not safety padding. No D1 sprite was rotated or transposed.","",
           "The side view represents the same nominal 28 px installed partition through a narrower shallow band, not an independently proven elevation projection. This is a design choice for human review, especially at the corner.","",
           "Anchor: logical cell [16,16], image [16,16], render origin [0,0]. Ground-to-image is identity in the full-cell carrier. North endpoint [16,0], south [16,32]; source coordinates are multiplied by 8. Room interior faces east/right; depth recedes toward negative y.","",
           "## Regions and repeat ownership","","Opaque rails: [12,0,14,32), [24,0,26,32). North support: [14,0,24,4); terminal south support: [14,28,24,32). Pane [14,4,24,28) alpha 150. Exterior [0,0,12,32) and [26,0,32,32) alpha 0. Rail width 2 and support depth 4 are proposed choices. Frame alpha is 255; no highlights or appearance polish.","",
           "For a nonterminal cell, the pane extends to y=32 within x=14..24. Every cell owns its north support; only the last owns a south support. Two mutually exclusive views belong to one future logical asset. Stride [0,32]; no overlap or shortened spacing.","",
           "| Cells | Geometry conformance | Background transmission |","| --- | --- | --- |"]
    for n,v in results.items(): lines.append(f"| {n} | {v['geometry']['pass']} | {v['transmission']['pass']} |")
    co=corner_result["observed"]; cc=corner_result["base_and_topology_checks"]["checks"]
    lines += ["","## Context and local north-west corner","",f"Original context conformance: {contexts['original']['pass']}; relocated: {contexts['relocated']['pass']}. Both use unchanged approved Batch 11 floors and left-side wall PNGs. Anchor, depth endpoint and opaque contact evidence is in JSON. The proposed 6 px visible-width reduction remains for human review.","",
              f"D1 actual validated main/repeat files remain unchanged. D1 render origin {co['D1_origin']}, D2 cell/render origin {co['D2_origin']}; computed base endpoints {co['D1_base_endpoint_computed']} and {co['D2_north_endpoint_computed']}. Rendered opaque edge pairs: {cc['adjacent_frame_pairs']['observed']}; rendered overlaps: {co['rendered_overlap_pixels']}; glass overlaps: {cc['glass_overlap_pixels']['observed']}. Draw order: floor, D1, D2; no deliberate opaque occlusion or extra visible support.","",
              f"**Corner remains unresolved at the upper rail.** Measured D1 post top y={co['D1_post_top_y']}; shallow D2 north support y={co['D2_north_support_y']}; transition {co['head_transition_gap_px']} px. A base/topology PASS is not a visual-connection PASS. No column, decorative cover or extra wall conceals this. Straight-run readiness is separate from corner appearance feasibility.","",
              f"The ground strips alone omit {co['missing_ground_pixels_before_component']} pixels of the canonical SE elbow (east/south arms at a room NW corner). Missing-region bbox {co['ground_component_bbox']} is shown as a separate topology-only component; remaining missing pixels after completion: {cc['topology_after_proposed_component']['observed']}. It does not solve the visible head-rail transition and is not production inventory.","",
              "## Negative controls","","| Broken fixture | Intended failing check | Passing control / rejection proven |","| --- | --- | --- |"]
    for n,v in negative.items(): lines.append(f"| {n} | {v['intended_check']} | {v['valid_control_pass']} / {v['proven']} |")
    lines += ["","## Preservation and handoff","",f"Counts before/after: {preservation['expected_counts']} / {preservation['observed_counts']}. Protected historical files: {preservation['protected_file_count']}; changed {preservation['changed']}; missing {preservation['missing']}.","",
              "D0/D1 sources, artwork, reports and snapshots are unchanged. Only the explicit D2 workspace is added to the authorized-reference safeguard; existing protected hashes are never exempted or refreshed.","",
              "Reproduce with `python tools/validate_architecture_d2.py`; complete suite command `python -m pytest -q`. Baseline: 67 passed. Captured results: test_results.json / test_results.txt.","",
              "Review ZIP: d2_geometry_review_bundle.zip. Montage: artifacts/d2_geometry_review_montage.png. Standalone native/source main and repeat scaffolds are beside the proposed contract. No production ingestion, D1/D2 approval, Batch 13, D3 or general junction repairs.",""]
    if "tests" in report: lines += [f"Complete suite: {report['tests']['passed']} passed; exit {report['tests']['exit_code']}.",""]
    (OUT/"d2_geometry_report.md").write_text("\n".join(lines),encoding="utf-8")
    zip_names=[CONTRACT.name,"d2_scaffold_native.png","d2_scaffold_source_8x.png","d2_repeat_scaffold_native.png","d2_repeat_scaffold_source_8x.png","d2_geometry_report.json","d2_geometry_report.md","artifacts/d2_geometry_review_montage.png","artifacts/d1_d2_corner_diagnostic.png","artifacts/d1_d2_corner_ground_component_only.png"]
    for extra in ("test_results.json","test_results.txt","visual_review.json"):
        if (OUT/extra).exists(): zip_names.append(extra)
    with zipfile.ZipFile(OUT/"d2_geometry_review_bundle.zip","w",compression=zipfile.ZIP_DEFLATED) as z:
        for name in sorted(zip_names):
            info=zipfile.ZipInfo(name,date_time=(2026,9,10,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED; z.writestr(info,(OUT/name).read_bytes())
    print(json.dumps({"conformance":report["technical_conformance"],"status":STATUS,"recommendation":report["recommendation"],"corner":corner_result["visual_connection_status"],"counts":preservation["observed_counts"]},indent=2))
    return 0 if report["technical_conformance"]=="PASS" else 1


if __name__=="__main__": raise SystemExit(main())
