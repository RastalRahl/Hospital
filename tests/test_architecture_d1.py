import hashlib

import pytest
from PIL import Image

import validate_architecture_d0 as d0
import validate_architecture_d1 as d1
from rastalr_pipeline.snapshot import compare_snapshots
from rastalr_pipeline.production_transition import compare_live_snapshot


@pytest.fixture(scope="module")
def data():
    return ({key:d1.load(d1.PACKAGE/"candidate"/name) for key,name in d1.VIEW_FILES.items()},
            d1.load(d0.CANON/"glass_partition_1x.png"), d0.read_json(d1.CONTRACT_PATH))


def test_actual_locked_candidate_files_and_block_exports(data):
    views,canonical,contract=data
    report=d1.validate_views(views,canonical,contract)
    assert report["pass"]
    assert report["checks"]["main_rgb_changes"]["observed"]==796
    assert report["checks"]["main_alpha_lock"]["observed"]==0
    assert report["checks"]["main_alpha_histogram"]["observed"]=={"150":421,"210":11,"255":464}


def test_supplied_metadata_must_match_authoritative_anchor(data):
    _,_,contract=data
    spec=d0.read_json(d1.PACKAGE/"reports/d1_candidate_spec.json")
    assert d1.validate_candidate_metadata(spec,contract)["pass"]
    spec["origin_relative_to_cell_native"]=[0,-7]
    result=d1.validate_candidate_metadata(spec,contract)
    assert not result["checks"]["origin_relative_to_cell_native"]["pass"]


def test_source_scale_check_detects_one_bad_subpixel_not_seen_by_downsampling(data):
    views,canonical,contract=data
    changed={**views,"main_8x":views["main_8x"].copy()}
    # Nearest-neighbor samples the block center; corrupting its first pixel
    # must fail the full-block check even though round-trip still matches.
    changed["main_8x"].putpixel((0,0),(1,2,3,255))
    result=d1.validate_views(changed,canonical,contract)
    assert not result["checks"]["main_8x_blocks"]["pass"]
    assert result["checks"]["main_roundtrip"]["pass"]


@pytest.mark.parametrize("mutation",["mode","dimensions"])
def test_actual_png_mode_and_dimensions_are_not_silently_normalized(data,mutation):
    views,canonical,contract=data
    altered=views["repeat"].convert("RGB") if mutation=="mode" else views["repeat"].crop((0,0,31,28))
    result=d1.validate_views({**views,"repeat":altered},canonical,contract)
    assert not result["pass"]
    assert not result["checks"][f"repeat_{mutation}"]["pass"]


@pytest.mark.parametrize("point,check",[((29,10),"repeat_column_extension"),((10,10),"repeat_outside_extension")])
def test_repeat_rgb_corruption_is_detected_inside_and_outside_edit_region(data,point,check):
    views,canonical,contract=data
    broken=views["repeat"].copy()
    broken.putpixel(point,(1,2,3,broken.getpixel(point)[3]))
    result=d1.validate_views({**views,"repeat":broken},canonical,contract)
    assert not result["checks"][check]["pass"]


@pytest.mark.parametrize("count",[1,2,4])
def test_supplied_exclusive_views_repeat_and_transmit_background(data,count):
    views,canonical,contract=data
    run,origins,layers=d1.assemble(views["main"],views["repeat"],count)
    report=d1.validate_run(run,views["main"],canonical,contract,count,origins,layers)
    assert report["pass"]
    assert report["derived"]["pane_widths_native"]==[28]*(count-1)+[24]
    for i in range(count):
        expected=views["main"] if i==count-1 else views["repeat"]
        assert run.crop((i*32,0,(i+1)*32,28)).tobytes()==expected.tobytes()
    transmission,backs,objects,scenes=d1.transmission(run,canonical,count)
    assert transmission["pass"]
    assert transmission["checks"]["pane_background_response"]["observed"]==432+504*(count-1)
    assert transmission["checks"]["object_transmission"]["observed"]==63*count
    assert backs["colored"].tobytes()!=backs["colored_object"].tobytes()


@pytest.mark.parametrize("name",["placement_drift_1px","broken_base_contact","opaque_glass","zero_alpha_glass","doubled_post","overlapping_glass"])
def test_candidate_negative_controls_fail_on_actual_pixels_or_placements(data,name):
    views,canonical,contract=data
    case=d1.negative_controls(views["main"],views["repeat"],canonical,contract)[name]
    assert case["valid_control_pass"] and case["proven"]
    assert not case["validation"]["checks"][case["intended_check"]]["pass"]


def test_opaque_glass_fails_background_response_even_with_valid_compositor_math(data):
    views,canonical,_=data
    opaque=views["main"].copy(); opaque.putalpha(255)
    report,_,_,_=d1.transmission(opaque,canonical,1)
    assert report["checks"]["light_source_over"]["pass"]
    assert not report["checks"]["pane_background_response"]["pass"]
    assert not report["checks"]["object_transmission"]["pass"]


@pytest.mark.parametrize("origin",[(32,32),(64,64)])
def test_approved_wall_context_relative_anchors_and_contact_pixels(data,origin):
    views,_,contract=data
    run,_,_=d1.assemble(views["main"],views["repeat"],4)
    wall=d1.load(d1.ROOT/"assets/architecture/hospital_wall_back_straight_01.png")
    floor=d1.load(d1.ROOT/"assets/architecture/hospital_floor_plain_01.png")
    check,scene,background,structure=d1.wall_context(run,wall,floor,contract,origin=origin)
    assert check["pass"]
    assert check["checks"]["relative_origin"]["observed"]==[0,-8]
    assert check["observed"]["shared_baseline"]==origin[1]+52


def test_context_rejects_one_pixel_offset(data):
    views,_,contract=data
    run,_,_=d1.assemble(views["main"],views["repeat"],4)
    wall=d1.load(d1.ROOT/"assets/architecture/hospital_wall_back_straight_01.png")
    floor=d1.load(d1.ROOT/"assets/architecture/hospital_floor_plain_01.png")
    result,_,_,_=d1.wall_context(run,wall,floor,contract,glass_drift=(0,1))
    assert not result["pass"]
    assert not result["checks"]["baseline"]["pass"]
    assert not result["checks"]["glass_anchor"]["checks"]["pixel_mismatches"]["pass"]


def fixture_snapshot(root):
    return {"counts":{"manifest":220,"approved":220,"needs_human_review":0},
            "sha256":{p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in root.rglob("*") if p.is_file()}}


@pytest.mark.parametrize("mutation,expected",[
    ("authorized_addition",True),("modify_protected",False),("delete_protected",False),
    ("modify_existing_under_allowed_prefix",False),("unrelated_addition",False),
    ("prefix_lookalike",False),("counts_changed",False),
])
def test_snapshot_allows_only_authorized_new_files_and_never_weakens_old_hashes(tmp_path,mutation,expected):
    protected=tmp_path/"assets/architecture/approved.png"
    protected.parent.mkdir(parents=True); protected.write_bytes(b"protected production fixture")
    allowed=d0.AUTHORIZED_REFERENCE_ADDITIONS[0]
    existing=tmp_path/allowed/"existing_reference.png"
    existing.parent.mkdir(parents=True); existing.write_bytes(b"protected preexisting reference")
    baseline=fixture_snapshot(tmp_path)
    if mutation=="authorized_addition":
        (existing.parent/"new_reference.png").write_bytes(b"authorized new reference")
    elif mutation=="modify_protected":
        protected.write_bytes(b"changed")
    elif mutation=="delete_protected":
        protected.unlink()  # Disposable tmp_path only, never real assets.
    elif mutation=="modify_existing_under_allowed_prefix":
        existing.write_bytes(b"changed")
    elif mutation in ("unrelated_addition","prefix_lookalike"):
        path=tmp_path/("references/architecture/elsewhere/new.png" if mutation=="unrelated_addition"
                       else allowed.rstrip("/")+"_other/new.png")
        path.parent.mkdir(parents=True); path.write_bytes(b"unapproved scope")
    current=fixture_snapshot(tmp_path)
    if mutation=="counts_changed": current["counts"]["manifest"]=221
    result=compare_snapshots(baseline,current,allowed_addition_prefixes=d0.AUTHORIZED_REFERENCE_ADDITIONS)
    assert result["pass"] is expected
    if mutation=="modify_protected": assert result["changed"]==["assets/architecture/approved.png"]
    if mutation=="delete_protected": assert result["missing"]==["assets/architecture/approved.png"]


def test_original_package_and_task_historical_files_are_unchanged():
    assert d1.package_integrity()["pass"]
    baseline=d0.read_json(d1.OUT/"production_before.json")
    assert compare_live_snapshot(baseline,d1.task_snapshot(),allowed_addition_prefixes=d0.AUTHORIZED_REFERENCE_ADDITIONS)["pass"]
