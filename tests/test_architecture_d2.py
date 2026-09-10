import pytest
from PIL import Image

import validate_architecture_d0 as d0
import validate_architecture_d1 as d1
import validate_architecture_d2 as d2
from rastalr_pipeline.snapshot import compare_snapshots


@pytest.fixture(scope="module")
def data():
    return (d0.read_json(d2.CONTRACT),d1.load(d2.OUT/"d2_scaffold_native.png"),
            d1.load(d2.OUT/"d2_repeat_scaffold_native.png"))


def test_contract_is_proposed_and_distinguishes_visible_envelope_from_carrier(data):
    c,_,_=data
    assert c["status"]=="PROPOSED_FOR_HUMAN_GEOMETRY_REVIEW"
    assert c["measured_authority"]["canonical_back_dimensions"]==[32,60]
    assert c["measured_authority"]["canonical_back_visible_envelope"]==[0,0,32,52]
    assert c["proposed_choices"]["native_dimensions"]==[32,32]
    assert c["proposed_choices"]["visual_envelope"]==[12,0,26,32]
    assert c["derived"]["render_origin_relative_to_cell"]==[0,0]
    assert c["human_review"]["approval"] is False
    assert c==d2.proposed_contract()  # JSON round-trip must not trip the no-overwrite guard.
    assert all(d0.digest(d0.ROOT/path)==value for path,value in c["sources_sha256"].items())


@pytest.mark.parametrize("view,stem",[("main","d2_scaffold"),("repeat","d2_repeat_scaffold")])
def test_saved_native_and_source_scaffolds_obey_all_proposed_regions(data,view,stem):
    c,_,_=data
    native=d1.load(d2.OUT/f"{stem}_native.png")
    source=d1.load(d2.OUT/f"{stem}_source_8x.png")
    report=d2.validate_scaffold(native,source,c,view)
    assert report["pass"]
    assert report["conformance_to"]==d2.STATUS
    assert native.getpixel((0,0))==(0,0,0,0)
    assert native.getpixel((31,31))==(0,0,0,0)


@pytest.mark.parametrize("defect",["source_subpixel","opaque_exterior","pane_hole","mode","size"])
def test_saved_file_defects_are_detected_without_silent_normalization(data,defect,tmp_path):
    c,main,_=data; image=main.copy()
    source=d1.load(d2.OUT/"d2_scaffold_source_8x.png")
    if defect=="source_subpixel": source.putpixel((0,0),(1,2,3,255))
    if defect=="opaque_exterior": image.putpixel((0,0),(39,55,70,255))
    if defect=="pane_hole": image.putpixel((18,16),(0,0,0,0))
    if defect=="mode": image=image.convert("RGB")
    if defect=="size": image=image.crop((0,0,31,32))
    image.save(tmp_path/"native.png"); source.save(tmp_path/"source.png")
    result=d2.validate_scaffold(d1.load(tmp_path/"native.png"),d1.load(tmp_path/"source.png"),c,"main")
    assert not result["pass"]
    if defect=="source_subpixel":
        assert not result["checks"]["exact_8x_blocks"]["pass"]
        assert result["checks"]["native_roundtrip"]["pass"]


def test_repeat_diff_only_removes_south_support_with_no_rotation(data):
    _,main,repeat=data
    changes=[]
    for y in range(32):
        for x in range(32):
            a,b=main.getpixel((x,y)),repeat.getpixel((x,y))
            if a!=b: changes.append((x,y))
    assert set(changes)=={(x,y) for x in range(14,24) for y in range(28,32)}
    assert all(repeat.getpixel((x,y))==main.getpixel((x,27)) for x,y in changes)


@pytest.mark.parametrize("n",[1,2,4])
def test_saved_depth_runs_support_width_and_background_response(data,n,tmp_path):
    _,main,repeat=data
    run,p,l=d2.assemble(main,repeat,n); run.save(tmp_path/"run.png"); loaded=d1.load(tmp_path/"run.png")
    check=d2.validate_run(loaded,p,l,n)
    assert check["pass"]
    assert check["checks"]["support_spans"]["observed"]==[[i*32,i*32+4] for i in range(n)]+[[n*32-4,n*32]]
    for i in range(n):
        assert loaded.crop((0,i*32,32,(i+1)*32)).tobytes()==(main if i==n-1 else repeat).tobytes()
    trans,_,objects,_=d2.transmission(loaded,n)
    assert trans["pass"]
    assert trans["checks"]["pane_response"]["observed"]==240+280*(n-1)
    assert trans["checks"]["object_response"]["observed"]==60*n


@pytest.mark.parametrize("name",["repeat_displacement_1px","anchor_mismatch_1px","broken_contact","opaque_glass","pane_hole","doubled_support","overlapping_glass"])
def test_each_negative_control_has_passing_valid_control_and_measured_failure(data,name):
    _,main,repeat=data
    result=d2.negative_controls(main,repeat)[name]
    assert result["proven"] and result["valid_control_pass"]
    assert not result["validation"]["checks"][result["intended_check"]]["pass"]


@pytest.mark.parametrize("origin",[(32,32),(64,64)])
def test_original_and_relocated_contexts_preserve_approved_walls(data,origin):
    _,main,repeat=data
    run,_,_=d2.assemble(main,repeat,2)
    result,_,_,_=d2.wall_context(run,origin=origin)
    assert result["pass"]
    assert result["observed"]["render_origin"]==[origin[0],origin[1]+32]


def test_local_corner_keeps_visual_limitation_separate_from_ground_coverage(data):
    _,main,repeat=data
    result,_,ground,mask,completed=d2.corner(main,repeat)
    assert result["base_and_topology_checks"]["pass"]
    assert result["visual_connection_status"]=="UNRESOLVED_UPPER_RAIL_TRANSITION"
    assert result["observed"]["head_transition_gap_px"]==28
    assert result["observed"]["rendered_overlap_pixels"]==0
    assert mask.getchannel("A").getbbox()==(60,56,64,64)
    assert sum(a>0 for a in mask.getchannel("A").get_flattened_data())==32
    assert ground.tobytes()!=completed.tobytes()


@pytest.mark.parametrize("mutation,allowed",[("new_d2",True),("protected_change",False),("protected_delete",False),("lookalike",False)])
def test_d2_snapshot_allowance_does_not_exempt_existing_files(tmp_path,mutation,allowed):
    prefix="references/architecture/master_validation_D2_v1/"
    old=tmp_path/prefix/"protected_reference.png"; old.parent.mkdir(parents=True); old.write_bytes(b"original")
    def snap():
        return {"counts":{"manifest":220,"approved":220,"needs_human_review":0},
                "sha256":{p.relative_to(tmp_path).as_posix():d0.digest(p) for p in tmp_path.rglob("*") if p.is_file()}}
    before=snap()
    if mutation=="new_d2": (old.parent/"authorized_scaffold.png").write_bytes(b"new")
    if mutation=="protected_change": old.write_bytes(b"changed")
    if mutation=="protected_delete": old.unlink()  # Isolated temporary fixture only.
    if mutation=="lookalike":
        target=tmp_path/(prefix.rstrip("/")+"_other/new.png"); target.parent.mkdir(); target.write_bytes(b"not authorized")
    assert compare_snapshots(before,snap(),allowed_addition_prefixes=d0.AUTHORIZED_REFERENCE_ADDITIONS)["pass"] is allowed


def test_task_preserves_all_production_d0_d1_history_and_authorities():
    report=compare_snapshots(d0.read_json(d2.OUT/"production_before.json"),d2.snapshot(),
                             allowed_addition_prefixes=("references/architecture/master_validation_D2_v1/",
                                                        "references/architecture/master_validation_D2_v2/",
                                                        "references/architecture/master_validation_D2_appearance_v1/",
                                                        "references/architecture/master_validation_D3_v1/",
                                                        "references/architecture/master_validation_D3_appearance_v1/",
                                                        "references/architecture/master_validation_D4_v1/"))
    assert report["pass"]
    assert report["observed_counts"]=={"manifest":220,"approved":220,"needs_human_review":0}
