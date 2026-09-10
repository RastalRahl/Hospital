import json

import pytest
from PIL import Image

from rastalr_pipeline.approval_report import approved_markdown
from rastalr_pipeline.core import normalize_architecture_grid_image
from rastalr_pipeline.geometry import alpha_region, anchored_component, horizontal_join, rectangle_pixels
from rastalr_pipeline.snapshot import compare_snapshots
from validate_architecture_d0 import (
    AUTHORIZED_REFERENCE_ADDITIONS,
    CANON, OUT, ROOT, approved_images, behind_glass, compose_glass, contract_from_canonical,
    glass_architecture_context, integration_scene, negative_fixtures, production_snapshot, rgba, topology_check,
    topology_layout, validate_glass,
)


@pytest.fixture(scope="module")
def fixture_data():
    return rgba(CANON/"glass_partition_1x.png"), contract_from_canonical(), approved_images()


def test_half_open_single_pixel_and_bounds():
    assert list(rectangle_pixels([3,4,4,5])) == [(3,4)]
    with pytest.raises(ValueError):
        list(rectangle_pixels([0,0,0,1]))
    assert not alpha_region(Image.new("RGBA",(1,1),(1,2,3,255)),[0,0,2,1],minimum=255,maximum=255)["pass"]


def test_native_geometry_and_exact_source_roundtrip(fixture_data):
    panel,contract,_=fixture_data
    assert panel.size == (32,28)
    assert contract["observed"]["glass_alpha_bbox_native"] == [4,5,28,23]
    assert contract["derived"]["anchor"]["render_origin_relative_to_cell_native"] == [0,-8]
    source=panel.resize((256,224),Image.Resampling.NEAREST)
    native=normalize_architecture_grid_image(source,source_scale=8,expected_native_dimensions=[32,28])
    assert native.tobytes() == panel.tobytes()
    assert all(source.getpixel((x*8+dx,y*8+dy)) == panel.getpixel((x,y))
               for x in range(32) for y in range(28) for dx in range(8) for dy in range(8))


@pytest.mark.parametrize("count",[1,2,4])
def test_valid_glass_repeat_and_background_transmission(fixture_data,count):
    panel,contract,_=fixture_data
    result,origins,layers=compose_glass(panel,contract,count)
    report=validate_glass(result,panel,contract,count,origins,layers)
    assert report["pass"]
    assert report["checks"]["post_runs"]["observed"] == [[i*32,i*32+4] for i in range(count)]+[[count*32-4,count*32]]
    background,scene,transmission=behind_glass(result)
    assert transmission["pass"]
    assert result.tobytes() != scene.tobytes()
    assert background.getchannel("A").getextrema() == (255,255)
    if count == 1:
        assert result.tobytes() == panel.tobytes()


@pytest.mark.parametrize("name",[
    "join_shift_1px","contact_pixel_removed","component_offset_1px","fake_opaque_glass",
    "double_seam","overlap_darkening","pane_alpha_hole",
])
def test_broken_pixel_and_coordinate_fixtures_fail_for_intended_reason(fixture_data,name):
    panel,contract,images=fixture_data
    cases,reports=negative_fixtures(panel,contract,images)
    report=reports[name]
    assert report["valid_control_pass"]
    assert report["proven"]
    assert not cases[name][1]["checks"][report["expected_failure_check"]]["pass"]


def test_join_detects_shift_and_missing_contact_even_with_opaque_carriers():
    panel=Image.new("RGBA",(32,28),(39,55,70,255))
    assert horizontal_join(panel,panel,[0,0],[32,0],[23,28])["pass"]
    assert not horizontal_join(panel,panel,[0,0],[33,0],[23,28])["pass"]
    broken=panel.copy(); broken.putpixel((0,26),(0,0,0,0))
    assert not horizontal_join(panel,broken,[0,0],[32,0],[23,28])["pass"]


def test_anchor_pixels_fail_even_when_metadata_claims_correct_origin():
    component=Image.new("RGBA",(4,5),(39,55,70,255))
    canvas=Image.new("RGBA",(12,12)); canvas.alpha_composite(component,(5,4))
    report=anchored_component(canvas,component,(4,4),(4,4))
    assert report["checks"]["origin"]["pass"]
    assert not report["checks"]["pixel_mismatches"]["pass"]


def test_transparent_component_rgb_does_not_create_false_anchor_failure():
    component=Image.new("RGBA",(4,5),(100,100,100,0))
    component.putpixel((2,2),(39,55,70,255))
    canvas=Image.new("RGBA",(12,12)); canvas.alpha_composite(component,(4,4))
    assert anchored_component(canvas,component,(4,4),(4,4))["pass"]


def test_d1_connects_solid_walls_at_shared_baseline(fixture_data):
    panel,contract,images=fixture_data
    _,result=glass_architecture_context(panel,contract,images)
    assert result["pass"]
    assert result["checks"]["baselines"]["observed"]==[84,84,84]


@pytest.mark.parametrize("kind",["connected_rooms","l_junction","t_junction","cross_junction"])
def test_existing_architecture_integration_has_computed_contacts(fixture_data,kind):
    _,_,images=fixture_data
    before={key:img.tobytes() for key,img in images.items()}
    scene,result=integration_scene(kind,images)
    assert result["technical_pass"]
    assert scene.size == (256,224)
    assert all(images[key].tobytes()==data for key,data in before.items())
    if kind != "connected_rooms":
        _,topology=topology_check(topology_layout(kind))
        assert topology["pass"]
        assert result["overlap_pixels_observed"] > 0
        if kind == "cross_junction":
            assert any(p["visible_pixels"] == 0 for p in result["occlusion_observed"])


def test_approval_markdown_idempotent_preserves_record_and_sections():
    qa=json.loads((ROOT/"metadata/architecture_doors_openings_batch_12_qa.json").read_text())
    original=(OUT/"sources/batch_12_qa_before.md").read_text(encoding="utf-8")
    once=approved_markdown(original,qa)
    assert approved_markdown(once,qa)==once
    assert once.count("APPROVED")==1
    assert once.count("## Human visual approval")==1
    assert "await human" not in once
    assert qa["human_visual_review"]["reviewed_at"] in once
    assert "hospital_equipment_opening_wide_01" in once
    with pytest.raises(ValueError):
        approved_markdown(original,{"status":"needs_human_review"})


def test_production_and_canonical_hashes_unchanged():
    baseline=json.loads((OUT/"sources/production_before.json").read_text())
    assert compare_snapshots(baseline, production_snapshot(),
                             allowed_addition_prefixes=AUTHORIZED_REFERENCE_ADDITIONS)["pass"]
    assert baseline["counts"]=={"manifest":220,"approved":220,"needs_human_review":0}
