"""Independent read-only D1 candidate validation; never execute package tools.

Run from the repository: python tools/validate_architecture_d1.py
Only this script's reports/artifacts under master_validation_D1_v1 are written.
"""
from __future__ import annotations

import json
import subprocess
import zipfile
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import validate_architecture_d0 as d0
from rastalr_pipeline.geometry import alpha_region, anchored_component, evidence
from rastalr_pipeline.snapshot import compare_snapshots

ROOT = d0.ROOT
OUT = ROOT / "references/architecture/master_validation_D1_v1"
PACKAGE = OUT / "sources/package"
CONTRACT_PATH = d0.OUT / "d1_geometry_alpha_contract.json"
BASELINE_COMMIT = "9ed992f57585d77448f3e396b8f4dc6f25aa5987"
CANONICAL_SHA256 = "51a11bddc75b2b51bb387b056f829c79315c0d714459784ab9c0ae3bea3564d6"
STEM = "rastalr_D1_glass_partition_back_locked_v1"
VIEW_FILES = {"main": f"{STEM}_native.png", "repeat": f"{STEM}_repeat_native.png",
              "main_8x": f"{STEM}_source_8x.png", "repeat_8x": f"{STEM}_repeat_source_8x.png"}


def load(path):
    # Check saved mode, not the result of a conversion which could conceal RGB.
    with Image.open(path) as image:
        return image.copy()


def pixel_difference(first, second, channels=(0, 1, 2, 3)):
    if first.size != second.size or first.mode != second.mode:
        return None
    return sum(any(a[c] != b[c] for c in channels) for a, b in
               zip(first.get_flattened_data(), second.get_flattened_data()))


def group(checks, **details):
    return {"checks": checks, "pass": all(check["pass"] for check in checks.values()), **details}


def task_snapshot():
    result = d0.production_snapshot()
    # D0's collector intentionally excludes its own workspace. For THIS task,
    # protect that entire historical workspace and every existing metadata file.
    for folder in (d0.OUT, ROOT / "metadata"):
        result["sha256"].update({p.relative_to(ROOT).as_posix(): d0.digest(p)
                                 for p in folder.rglob("*") if p.is_file()})
    return result


def package_integrity():
    provenance = d0.read_json(OUT / "package_provenance.json")
    archive = OUT / "sources" / provenance["archive_name"]
    checks = {"archive_sha256": evidence(provenance["archive_sha256"], d0.digest(archive), "SHA-256 of preserved original archive", units="sha256")}
    with zipfile.ZipFile(archive) as zipped:
        names = sorted(i.filename for i in zipped.infolist() if not i.is_dir())
        checks["extracted_members"] = evidence(names, sorted(p.relative_to(PACKAGE).as_posix() for p in PACKAGE.rglob("*") if p.is_file()), "Enumerate archive and extracted files", units="paths")
        mismatch = [name for name in names if not (PACKAGE/name).is_file() or (PACKAGE/name).read_bytes() != zipped.read(name)]
        checks["extracted_bytes"] = evidence([], mismatch, "Compare every extracted member byte-for-byte to original ZIP", units="paths")
    changes = [name for name, expected in provenance["members_sha256"].items()
               if not (PACKAGE/name).is_file() or d0.digest(PACKAGE/name) != expected]
    checks["initial_member_hashes"] = evidence([], changes, "Compare every member to initial extraction hashes", units="paths")
    return group(checks, member_count=len(provenance["members_sha256"]),
                 candidate_sha256={name: d0.digest(PACKAGE/"candidate"/name) for name in VIEW_FILES.values()})


def validate_views(views, canonical, contract):
    checks = {}
    for name, image in views.items():
        expected_size = contract["derived"]["source_dimensions_px"] if name.endswith("8x") else contract["expected"]["native_dimensions_px"]
        checks[f"{name}_mode"] = evidence("RGBA", image.mode, "Read saved PNG mode", units="mode")
        checks[f"{name}_dimensions"] = evidence(expected_size, list(image.size), "Read saved PNG dimensions", units="source_px" if name.endswith("8x") else "native_px")
    if not all(c["pass"] for c in checks.values()):
        return group(checks)
    main, repeat = views["main"], views["repeat"]
    scale = contract["expected"]["source_scale"]
    for name in ("main", "repeat"):
        native, source = views[name], views[f"{name}_8x"]
        errors = sum(source.getpixel((x, y)) != native.getpixel((x//scale, y//scale))
                     for y in range(source.height) for x in range(source.width))
        checks[f"{name}_8x_blocks"] = evidence(0, errors, "Read all 57,344 source pixels against their native 8x8 block", units="pixels")
        checks[f"{name}_roundtrip"] = evidence(0, pixel_difference(native, source.resize(native.size, Image.Resampling.NEAREST)), "Nearest-neighbor source-to-native comparison of all RGBA pixels", units="pixels")
    checks["main_alpha_lock"] = evidence(0, pixel_difference(main, canonical, (3,)), "Compare all 896 alpha samples with canonical PNG", units="pixels")
    checks["main_rgb_changes"] = evidence(796, pixel_difference(main, canonical, (0,1,2)), "Compare RGB triples with canonical PNG", units="pixels")
    histogram = {str(k): v for k, v in sorted(Counter(main.getchannel("A").get_flattened_data()).items())}
    checks["main_alpha_histogram"] = evidence({"150":421,"210":11,"255":464}, histogram, "Count alpha values from saved main PNG", units="pixels_per_alpha")
    for role, rect in contract["expected"]["frame_regions_native"].items():
        checks[role] = alpha_region(main, rect, minimum=255, maximum=255)
    pane = contract["expected"]["glass_region_native"]
    checks["pane_locked_alpha_values"] = evidence([150,210], sorted(set(main.crop(pane).getchannel("A").get_flattened_data())), "Read unique alpha values inside half-open pane region", units="alpha")
    checks["visual_envelope"] = evidence([0,0,32,28], list(main.getchannel("A").getbbox()), "Compute nonzero alpha bounding box; required outer frame remains present")
    # Independent per-coordinate calculation; do not use package builder or
    # D0 panel_variant to generate/replace the supplied implementation view.
    outside_changes = extension_errors = 0
    extension = contract["derived"]["repeat"]["nonterminal_extension_native"]
    column = contract["derived"]["repeat"]["extension_source_column_native"]
    for y in range(main.height):
        for x in range(main.width):
            if extension[0] <= x < extension[2] and extension[1] <= y < extension[3]:
                extension_errors += repeat.getpixel((x,y)) != main.getpixel((column,y))
            else:
                outside_changes += repeat.getpixel((x,y)) != main.getpixel((x,y))
    checks["repeat_column_extension"] = evidence(0, extension_errors, "Compare supplied repeat columns 28..31 with main column 27, all RGBA channels", units="pixels")
    checks["repeat_outside_extension"] = evidence(0, outside_changes, "Compare every pixel outside the allowed half-open extension region", units="pixels")
    return group(checks, measured_palette_entries=len(set(main.get_flattened_data())),
                 policy="Main RGB-only appearance edit is authorized; alpha/topology changes are not. Repeat differs only by the specified column extension.")


def assemble(main, repeat, count, *, stride=32, double_coat=False):
    """Compose only supplied views; one mutually exclusive view per cell."""
    run = Image.new("RGBA", (32*count,28))
    layers = Image.new("I", run.size, 0)
    placements = []
    for index in range(count):
        image = main if index == count-1 else repeat
        x0 = index*stride
        placements.append([x0,0])
        run.alpha_composite(image,(x0,0))
        for y in range(image.height):
            for x in range(image.width):
                if 0 <= x+x0 < run.width and 0 < image.getpixel((x,y))[3] < 255:
                    point=(x+x0,y); layers.putpixel(point,layers.getpixel(point)+1)
    if double_coat:
        run.alpha_composite(main.crop((4,5,28,23)),(4,5))
        for y in range(5,23):
            for x in range(4,28):
                layers.putpixel((x,y),layers.getpixel((x,y))+1)
    return run, placements, layers


def validate_run(run, main, canonical, contract, count, placements, layers):
    measured = d0.validate_glass(run, canonical, contract, count, placements, layers)
    if run.size != (32*count,28):
        return measured
    errors=0
    for y in range(run.height):
        for x in range(run.width):
            cell, local = divmod(x,32)
            source_x = 27 if cell < count-1 and local >= 28 else local
            errors += run.getpixel((x,y)) != main.getpixel((source_x,y))
    measured["checks"]["candidate_rgba_mapping"] = evidence(0, errors, "Compare actual run pixels to D1 main candidate RGB/alpha under the contract extension rule", units="pixels")
    measured["pass"] = all(c["pass"] for c in measured["checks"].values())
    measured["derived"] = {"pane_widths_native": [28]*(count-1)+[24], "implementation_views": ["repeat"]*(count-1)+["main_terminal"]}
    return measured


def validate_candidate_metadata(spec, contract):
    """Package metadata is observed input, checked against committed authority."""
    anchors=contract["derived"]["anchor"]
    expected={"id":contract["id"],"native_dimensions":contract["expected"]["native_dimensions_px"],
              "source_scale":contract["expected"]["source_scale"],
              "source_dimensions":contract["derived"]["source_dimensions_px"],
              "frame_regions_native":contract["expected"]["frame_regions_native"],
              "pane_native":contract["expected"]["glass_region_native"],
              "anchor_cell_native":anchors["logical_cell_native"],
              "anchor_image_native":anchors["image_native"],
              "origin_relative_to_cell_native":anchors["render_origin_relative_to_cell_native"],
              "normalization_mode":contract["expected"]["normalization_mode"]}
    checks={key:evidence(value,spec.get(key),"Read supplied candidate metadata; compare with committed D0 contract, not a PNG measurement",units="contract_field")
            for key,value in expected.items()}
    for key,value in {"logical_assets":1,"implementation_views":2,"stride_native":32,
                      "shared_post_width_native":4,"terminal_pane_width_native":24,"nonterminal_pane_width_native":28}.items():
        checks[f"repeat_{key}"]=evidence(value,spec.get("repeat",{}).get(key),"Read declared mutually exclusive implementation-view metadata",units="contract_field")
    return group(checks)


def backgrounds(size):
    light = Image.new("RGBA",size,(238,232,219,255))
    dark = Image.new("RGBA",size,(29,42,58,255))
    colored = Image.new("RGBA",size,(39,184,171,255))
    for x in range(size[0]):
        if x//8%2:
            colored.paste((196,73,143,255),(x,0,x+1,size[1]))
    objects = Image.new("RGBA",size)
    for x in range(10,size[0],32):
        objects.paste((242,187,43,255),(x,10,x+7,19))
    return {"light":light,"dark":dark,"colored":colored,
            "colored_object":Image.alpha_composite(colored,objects)}, objects


def transmission(run, canonical, count):
    backs, objects=backgrounds(run.size)
    scenes={name:Image.alpha_composite(back,run) for name,back in backs.items()}
    checks={}
    for name,back in backs.items():
        errors=0
        for f,b,pixel in zip(run.get_flattened_data(),back.get_flattened_data(),scenes[name].get_flattened_data()):
            expected=tuple((f[c]*f[3]+b[c]*(255-f[3])+127)//255 for c in range(3))+(255,)
            errors += pixel != expected
        checks[f"{name}_source_over"] = evidence(0,errors,"Compare composited pixels to independent integer source-over equation",units="pixels")
    pane_total=pane_responsive=frame_responsive=object_total=object_responsive=0
    for y in range(run.height):
        for x in range(run.width):
            cell,local=divmod(x,32)
            source_x=27 if cell<count-1 and local>=28 else local
            pane=canonical.getpixel((source_x,y))[3]<255
            changed=scenes["light"].getpixel((x,y)) != scenes["dark"].getpixel((x,y))
            pane_total += pane
            pane_responsive += pane and changed
            frame_responsive += not pane and changed
            if pane and objects.getpixel((x,y))[3]:
                object_total+=1
                object_responsive+=scenes["colored_object"].getpixel((x,y)) != scenes["colored"].getpixel((x,y))
    checks["pane_background_response"] = evidence(pane_total,pane_responsive,"Compare light versus dark composites at independently canonical-mapped pane pixels",units="pixels")
    checks["frame_background_response"] = evidence(0,frame_responsive,"Compare background response in required frame pixels",units="pixels")
    checks["object_transmission"] = evidence(object_total,object_responsive,"Toggle separate yellow object layer behind pane and compare output pixels",units="pixels")
    checks["object_exercised"] = evidence(True,object_total>0,"Require at least one independently masked object pixel behind glass",units="boolean")
    return group(checks), backs, objects, scenes


def wall_context(run, wall, floor, contract, *, origin=(32,32), glass_drift=(0,0)):
    """Translation-safe context using unchanged approved PNGs and actual run."""
    ox,oy=origin
    baseline=oy+wall.height
    expected_glass=(ox+wall.width,baseline-run.height)
    actual_glass=(expected_glass[0]+glass_drift[0],expected_glass[1]+glass_drift[1])
    right=(expected_glass[0]+run.width,oy)
    canvas_size=(right[0]+wall.width+32,baseline+64)
    background=Image.new("RGBA",canvas_size)
    for y in range(baseline-32,baseline+64,32):
        for x in range(ox,right[0]+wall.width,32):
            background.alpha_composite(floor,(x,y))
    structure=Image.new("RGBA",canvas_size)
    structure.alpha_composite(wall,origin)
    structure.alpha_composite(wall,right)
    structure.alpha_composite(run,actual_glass)
    scene=Image.alpha_composite(background,structure)
    # Anchored component comparison tests pixels as well as placement metadata.
    anchor_check=anchored_component(structure,run,expected_glass,actual_glass)
    checks={"glass_anchor":anchor_check,
            "left_wall_unchanged":anchored_component(structure,wall,origin,origin),
            "right_wall_unchanged":anchored_component(structure,wall,right,right),
            "baseline":evidence([baseline]*3,[oy+wall.height,actual_glass[1]+run.height,right[1]+wall.height],"Actual origins plus loaded PNG heights"),
            "adjacency":evidence([ox+wall.width,right[0]],[actual_glass[0],actual_glass[0]+run.width],"Actual carrier bounds at both solid/glass joins")}
    logical_cell=(expected_glass[0],baseline-contract["derived"]["anchor"]["logical_cell_native"][1])
    relative=[actual_glass[i]-logical_cell[i] for i in range(2)]
    checks["relative_origin"] = evidence(contract["derived"]["anchor"]["render_origin_relative_to_cell_native"],relative,"Compute render origin minus explicit logical-cell origin")
    for label,x in (("left_solid",expected_glass[0]-1),("left_glass",expected_glass[0]),
                    ("right_glass",right[0]-1),("right_solid",right[0])):
        checks[f"{label}_contact"] = alpha_region(structure,[x,baseline-5,x+1,baseline],minimum=255,maximum=255)
    expected_region=Image.alpha_composite(background.crop((*expected_glass,expected_glass[0]+run.width,baseline)),run)
    observed_region=scene.crop((*expected_glass,expected_glass[0]+run.width,baseline))
    checks["rendered_composite"] = evidence(0,pixel_difference(expected_region,observed_region),"Read scene crop against separate background plus unchanged candidate run",units="pixels")
    return group(checks, observed={"wall_origins":[list(origin),list(right)],"glass_origin":list(actual_glass),
                                  "logical_cell_origin":list(logical_cell),"shared_baseline":baseline},
                 scope="Straight wall/glass only; no L/T/cross appearance claim"), scene, background, structure


def negative_controls(main, repeat, canonical, contract):
    valid,origins,layers=assemble(main,repeat,2)
    valid_check=validate_run(valid,main,canonical,contract,2,origins,layers)
    cases={}
    def add(name,image,placements,coverage,intended):
        report=validate_run(image,main,canonical,contract,2,placements,coverage)
        cases[name]={"image":image,"validation":report,"intended_check":intended,
                     "valid_control_pass":valid_check["pass"],
                     "proven":valid_check["pass"] and not report["pass"] and not report["checks"][intended]["pass"]}
    shifted,p,l=assemble(main,repeat,2,stride=33)
    add("placement_drift_1px",shifted,p,l,"placements")
    broken=valid.copy(); broken.putpixel((31,27),(0,0,0,0))
    add("broken_base_contact",broken,origins,layers,"base_0")
    broken=valid.copy(); broken.putalpha(255)
    add("opaque_glass",broken,origins,layers,"glass_0")
    broken=valid.copy(); broken.putpixel((10,15),(0,0,0,0))
    add("zero_alpha_glass",broken,origins,layers,"glass_0")
    doubled,p,l=assemble(main,main,2)
    add("doubled_post",doubled,p,l,"post_runs")
    overlap,p,l=assemble(main,repeat,2,double_coat=True)
    add("overlapping_glass",overlap,p,l,"single_layer_alpha")
    return cases


def montage(entries):
    cw,ch=550,285
    board=Image.new("RGBA",(cw*2,40+ch*((len(entries)+1)//2)),(24,35,49,255))
    draw=ImageDraw.Draw(board)
    draw.text((16,12),"D1 / INDEPENDENT REFERENCE VALIDATION / TWO EXCLUSIVE VIEWS / NO PRODUCTION APPROVAL",fill=(238,232,219),font=ImageFont.load_default())
    for i,(label,image) in enumerate(entries):
        x,y=(i%2)*cw+16,40+(i//2)*ch
        draw.text((x,y+5),label,fill=(238,232,219),font=ImageFont.load_default())
        scale=max(1,min((cw-32)//image.width,(ch-36)//image.height))
        display=image.resize((image.width*scale,image.height*scale),Image.Resampling.NEAREST)
        board.alpha_composite(display,(x,y+28))
    return board


def write_report(report):
    d0.write_json(OUT/"d1_validation_report.json",report)
    lines=["# D1 independent reference validation","",f"Result: **{report['status']}**. Reference-only; no production approval or ingestion.","",
           "The saved main and repeat PNGs are two mutually exclusive implementation views of one proposed logical asset. Package reports and build tools were read as supporting context; no supplied tool was executed and no preview was used as artwork.","",
           "Authority: committed D0 contract at `9ed992f57585d77448f3e396b8f4dc6f25aa5987`. All rectangles use `[left, top, right, bottom)`. JSON separates expected/observed checks, derived placement information, and visual findings.","",
           "## File and pixel checks","","| Check | Independently observed | Pass |","| --- | --- | --- |"]
    for key,check in report["files"]["checks"].items():
        if "observed" in check:
            lines.append(f"| {key} | `{check['observed']}` | {check['pass']} |")
    lines += ["","Frame regions: left [0,0,4,28), right [28,0,32,28), top [4,0,28,5), bottom [4,23,28,28). Required alpha 255; pane [4,5,28,23) retains alpha 150/210 pixel-for-pixel. No zero-alpha pane holes or opaque fake glass. The intentional full-canvas frame contacts are not treated as generic prop clipping.","",
              "## Repetition and transmission","","| Panels | Run checks | Separate-background checks |","| --- | --- | --- |"]
    for n,value in report.get("runs",{}).items():
        lines.append(f"| {n} | {value['geometry']['pass']} | {value['transmission']['pass']} |")
    lines += ["","Runs are assembled from the supplied native files at 32 px stride. RGB checks use the D1 candidate, not canonical colors. Shared posts remain 4 px, the closing post remains present, pane widths are 28 px for nonterminal views and 24 px for the terminal view. Layer counts and output alpha are measured independently.","",
              "Light, dark, colored and colored-with-object backgrounds are separate PNGs. Source-over equations, all-pane background response, frame invariance and object-toggle response are checked from actual pixels.","",
              "## Anchors and context","","Cell anchor [16,20], image anchor [16,28], render origin [0,-8]; architecture_grid_preserving normalization. Unchanged approved Batch 11 walls/floors surround the supplied four-panel run. Original and relocated contexts test relative anchors, shared baselines, adjacency, actual frame contacts and compositing.",""]
    for name,context in report.get("contexts",{}).items():
        lines.append(f"- {name}: pass={context['pass']}; placements/baseline `{context.get('observed')}`.")
    lines += ["","No L/T/cross appearance validation or repairs were performed. Their D0 presentation limitations remain.","",
              "## Negative controls","","| Fixture | Intended failing check | Failure proven with passing valid control |","| --- | --- | --- |"]
    for name,value in report.get("negative_controls",{}).items():
        lines.append(f"| {name} | {value['intended_check']} | {value['proven']} |")
    lines += ["","## Preservation and test safeguard","",
              "The original ZIP and every extracted package member are preserved under sources/. New diagnostics and reports are outside sources/. Exact member bytes and initial SHA-256 hashes are checked on every validation run.","",
              f"Task counts before/after: `{report['preservation']['expected_counts']}` / `{report['preservation']['observed_counts']}`. Protected existing files: {report['preservation']['protected_file_count']}. Missing: {report['preservation']['missing']}; changed: {report['preservation']['changed']}.","",
              "D0's historical snapshot and reports are unchanged. Its safeguard compares every historical path/hash and permits only additions beneath the explicitly authorized D1 workspace. Existing files are never exempted, even if they are under an allowed prefix. Temporary-fixture tests reject modification, deletion, count changes, unrelated additions and prefix lookalikes.","",
              "Full automated suite evidence is in test_results.json and test_results.txt; baseline was 39 passed. Reproduce validation with `python tools/validate_architecture_d1.py`; run tests with `python -m pytest -q`.","",
              "## Review limits","",
              "User reports ChatGPT appearance review passed for proceeding to technical validation; this is not final human production approval. Technical transmission proves live background response, not semantic absence of a painted scene. Direct visual inspection of the actual supplied candidate is recorded separately in visual_review.json.","",
              f"Blockers: {report['blockers'] or 'none'}.","",
              "Review montage: artifacts/d1_review_montage.png. Production remains unchanged; no Batch 13, no manifest/catalog entry, no D2.",""]
    if "tests" in report:
        lines += [f"Complete test suite: **{report['tests']['status']}**, {report['tests']['passed']} passed; baseline 39.",""]
    (OUT/"d1_validation_report.md").write_text("\n".join(lines),encoding="utf-8")


def main():
    artifact=OUT/"artifacts"; artifact.mkdir(exist_ok=True)
    contract=d0.read_json(CONTRACT_PATH)
    canonical=load(d0.CANON/"glass_partition_1x.png")
    committed=subprocess.run(["git","show",f"{BASELINE_COMMIT}:{CONTRACT_PATH.relative_to(ROOT).as_posix()}"],cwd=ROOT,capture_output=True,check=True).stdout
    authority=group({"canonical_sha256":evidence(CANONICAL_SHA256,d0.digest(d0.CANON/"glass_partition_1x.png"),"Hash actual canonical PNG",units="sha256"),
                     "committed_contract":evidence(True,json.loads(committed)==contract,"Compare local contract JSON with specified Git commit",units="boolean")})
    package=package_integrity()
    metadata=validate_candidate_metadata(d0.read_json(PACKAGE/"reports/d1_candidate_spec.json"),contract)
    views={name:load(PACKAGE/"candidate"/filename) for name,filename in VIEW_FILES.items()}
    files=validate_views(views,canonical,contract)
    report={"status":"FAIL","scope":"reference_only_independent_d1_validation","authority":authority,
            "package_integrity":package,"candidate_metadata":metadata,"files":files,"blockers":[],"runs":{},"contexts":{},"negative_controls":{}}
    # Invalid carriers must produce a report, never a silently repaired canvas.
    geometry_ok=all(image.mode=="RGBA" and image.size==((256,224) if name.endswith("8x") else (32,28)) for name,image in views.items())
    if geometry_ok:
        entries=[]; runs={}
        for n in (1,2,4):
            run,placements,layers=assemble(views["main"],views["repeat"],n)
            path=artifact/f"d1_run_{n}_native.png"; run.save(path); run=load(path)
            geometry=validate_run(run,views["main"],canonical,contract,n,placements,layers)
            trans,backs,objects,scenes=transmission(run,canonical,n)
            for name,back in backs.items():
                back.save(artifact/f"d1_run_{n}_{name}_background.png")
                scenes[name].save(artifact/f"d1_run_{n}_{name}_composite.png")
            objects.save(artifact/f"d1_run_{n}_object_layer.png")
            report["runs"][str(n)]={"geometry":geometry,"transmission":trans}; runs[n]=run
            entries.append((f"{n} panel(s) / actual candidate / 32 px stride",scenes["colored_object"]))
        wall=load(ROOT/"assets/architecture/hospital_wall_back_straight_01.png")
        floor=load(ROOT/"assets/architecture/hospital_floor_plain_01.png")
        for name,origin in (("original",(32,32)),("relocated",(64,64))):
            check,scene,background,structure=wall_context(runs[4],wall,floor,contract,origin=origin)
            report["contexts"][name]=check
            for suffix,image in (("scene",scene),("background",background),("structure",structure)):
                image.save(artifact/f"d1_wall_context_{name}_{suffix}.png")
            entries.append((f"Approved walls + supplied D1 / {name}",scene))
        cases=negative_controls(views["main"],views["repeat"],canonical,contract)
        negative_entries=[]
        for name,case in cases.items():
            case["image"].save(artifact/f"broken_{name}.png")
            negative_entries.append((f"BROKEN {name} / {case['intended_check']}",case["image"]))
            report["negative_controls"][name]={key:value for key,value in case.items() if key!="image"}
        montage(negative_entries).save(artifact/"d1_negative_controls.png")
        diag=views["main_8x"].copy(); draw=ImageDraw.Draw(diag)
        for x in (0,32,224,255): draw.line((x,0,x,223),fill=(255,75,165,255))
        for y in (0,40,184,223): draw.line((0,y,255,y),fill=(241,192,49,255))
        diag.save(artifact/"d1_geometry_alpha_diagnostic.png")
        entries.append(("Geometry / required frame and pane / 8x",diag))
        backs,_=backgrounds(views["main"].size)
        entries.extend([(f"Actual main / {name} background",Image.alpha_composite(backs[name],views["main"])) for name in ("light","dark")])
        montage(entries).save(artifact/"d1_review_montage.png")
    baseline=d0.read_json(OUT/"production_before.json")
    report["preservation"]=compare_snapshots(baseline,task_snapshot(),allowed_addition_prefixes=d0.AUTHORIZED_REFERENCE_ADDITIONS)
    d0.write_json(OUT/"production_preservation.json",report["preservation"])
    groups={"authority":authority,"package":package,"candidate_metadata":metadata,"candidate_files":files,"production_preservation":report["preservation"]}
    groups.update({f"run_{n}":group(value) for n,value in report["runs"].items()})
    groups.update({f"context_{name}":value for name,value in report["contexts"].items()})
    for name,check in groups.items():
        if not check["pass"]:
            report["blockers"].append({"group":name,"failed_checks":[key for key,value in check.get("checks",{}).items() if not value["pass"]]})
    for name,value in report["negative_controls"].items():
        if not value["proven"]: report["blockers"].append({"negative_control":name})
    if (OUT/"test_results.json").exists():
        report["tests"]=d0.read_json(OUT/"test_results.json")
        if report["tests"]["exit_code"]!=0: report["blockers"].append({"tests":"complete suite failed"})
    if (OUT/"visual_review.json").exists():
        report["visual_review"]=d0.read_json(OUT/"visual_review.json")
    report["status"]="PASS" if not report["blockers"] else "FAIL"
    write_report(report)
    print(json.dumps({"status":report["status"],"blockers":report["blockers"],"counts":report["preservation"]["observed_counts"],"negative_controls":{k:v["proven"] for k,v in report["negative_controls"].items()}},indent=2))
    return 0 if report["status"]=="PASS" else 1


if __name__=="__main__":
    raise SystemExit(main())
