"""Independent regressions for supplied D2 RGBA, never scaffold RGB approval."""
import pytest
from PIL import Image
import validate_architecture_d0 as d0
import validate_architecture_d1 as d1
import validate_architecture_d2 as v1
import validate_architecture_d2_v2 as v2
import validate_architecture_d2_appearance as app
from rastalr_pipeline.snapshot import compare_snapshots


@pytest.fixture(scope='module')
def inputs():
    return d0.read_json(app.CONTRACT),{n:app.candidate(n) for n in app.NAMES}


def test_original_archive_members_and_sources_match_pinned_repository():
    q=app.package_integrity()
    assert q['pass'] and q['member_count']==51
    assert q['checks']['contract_checkout_bytes']['pass']
    assert q['checks']['contract_pinned_text']['pass']


@pytest.mark.parametrize('name',app.NAMES)
def test_saved_candidates_preserve_geometry_alpha_and_expected_rgb_changes(inputs,name):
    c,views=inputs
    q=app.check_candidate(name,views[name],app.candidate(name,'source_8x'),c)
    assert q['pass']
    assert q['checks']['alpha_changed']['observed']==0
    assert q['checks']['rgb_changed']['observed']==app.EXPECTED_RGB[name]
    assert q['checks']['zero_alpha_rgba_changed']['observed']==0
    assert c['status']=='PROPOSED_FOR_HUMAN_GEOMETRY_REVIEW'


@pytest.mark.parametrize('name',app.NAMES)
def test_alpha_corruption_is_detected_from_saved_temporary_copy(inputs,name,tmp_path):
    c,views=inputs; im=views[name].copy(); im.putpixel((3,10),(*im.getpixel((3,10))[:3],0))
    im.save(tmp_path/'broken.png')
    q=app.check_candidate(name,d1.load(tmp_path/'broken.png'),app.candidate(name,'source_8x'),c)
    assert not q['pass'] and not q['checks']['alpha_changed']['pass']
    assert q['checks']['alpha_changed']['observed']==1


@pytest.mark.parametrize('defect',['source_subpixel','transparent_rgb','mode','size'])
def test_export_and_unsupported_changes_fail_without_repair(inputs,defect,tmp_path):
    c,views=inputs; im=views['corner_main'].copy(); source=app.candidate('corner_main','source_8x')
    if defect=='source_subpixel': source.putpixel((0,0),(1,2,3,255))
    if defect=='transparent_rgb': im.putpixel((10,10),(1,2,3,0))
    if defect=='mode': im=im.convert('RGB')
    if defect=='size': im=im.crop((0,0,11,56))
    im.save(tmp_path/'native.png'); source.save(tmp_path/'source.png')
    q=app.check_candidate('corner_main',d1.load(tmp_path/'native.png'),d1.load(tmp_path/'source.png'),c)
    assert not q['pass']
    if defect=='transparent_rgb':
        assert q['checks']['alpha_changed']['pass']
        assert not q['checks']['zero_alpha_rgba_changed']['pass']
    if defect=='source_subpixel':
        assert q['geometry']['checks']['roundtrip']['pass']
        assert not q['geometry']['checks']['blocks']['pass']


def test_exact_candidate_view_relationships_and_anchor_mapping(inputs):
    c,views=inputs; assert app.relationships(views,c)['pass']
    changed={k:v.copy() for k,v in views.items()}
    changed['repeat'].putpixel((0,10),(1,2,3,255))
    q=app.relationships(changed,c)
    assert not q['checks']['repeat_outside_changes']['pass']
    changed={k:v.copy() for k,v in views.items()}
    changed['corner_main'].putpixel((5,40),(1,2,3,150))
    assert not app.relationships(changed,c)['checks']['corner_main_body']['pass']


@pytest.mark.parametrize('count',[1,2,4])
@pytest.mark.parametrize('corner',[False,True])
def test_saved_repeat_pixels_and_single_glass_coverage(inputs,count,corner):
    _,views=inputs; run,p,l=v2.assemble(views,count,corner=corner)
    key=('corner_' if corner else 'straight_')+str(count)
    saved=d1.load(app.ART/f'{key}_native.png')
    assert d1.pixel_difference(run,saved)==0
    assert max(l.get_flattened_data())==1
    offset=24 if corner else 0
    body=saved.crop((0,offset,12,offset+32*count))
    assert v2.check_run(body,[[0,i*32] for i in range(count)],l.crop((0,offset,12,offset+32*count)),count)['pass']
    assert v2.transmission(saved)[0]['pass']
    for i in range(count):
        name=('corner_' if corner and i==0 else '')+('main' if i==count-1 else 'repeat')
        view=views[name]; y=p[i][1]
        assert saved.crop((0,y,12,y+view.height)).tobytes()==view.tobytes()


@pytest.mark.parametrize('name',['original','relocated'])
def test_saved_corner_pixels_and_intended_occlusion(inputs,name):
    _,views=inputs; dx=dy=32 if name=='relocated' else 0
    front=d1.load(app.ART/f'corner_{name}_d1_layer.png')
    side=d1.load(app.ART/f'corner_{name}_d2_layer.png')
    union=d1.load(app.ART/f'corner_{name}_structure.png')
    assert d1.pixel_difference(union,Image.alpha_composite(side,front))==0
    overlapping=[(a,b) for a,b in zip(side.get_flattened_data(),front.get_flattened_data()) if a[3] and b[3]]
    assert len(overlapping)==48 and all(a[3]==b[3]==255 for a,b in overlapping)
    assert side.getpixel((63+dx,50+dy))[3]==150
    h,_,_=d1.assemble(*[d1.load(d1.PACKAGE/'candidate'/d1.VIEW_FILES[n]) for n in ('main','repeat')],2)
    assert union.crop((64+dx,36+dy,64+dx+h.width,36+dy+h.height)).tobytes()==h.tobytes()


@pytest.mark.parametrize('name',['repeat_displacement_1px','broken_contact','opaque_glass','pane_hole','doubled_support',
    'stacked_glass','anchor_mismatch_1px','missing_corner_return','corner_displacement_1px'])
def test_candidate_negative_controls_have_passing_controls(inputs,name):
    _,views=inputs; q=v2.negatives(views)[name]
    assert q['valid_control_pass'] and q['proven']
    assert not q['validation']['checks'][q['intended_check']]['pass']


@pytest.mark.parametrize('action,allowed',[('add',True),('modify',False),('delete',False),('lookalike',False)])
def test_addition_allowance_never_exempts_protected_hashes(tmp_path,action,allowed):
    old=tmp_path/app.PREFIX/'sources/protected.png';old.parent.mkdir(parents=True);old.write_bytes(b'original')
    def snap():
        return {'counts':{'manifest':220,'approved':220,'needs_human_review':0},
                'sha256':{p.relative_to(tmp_path).as_posix():d0.digest(p) for p in tmp_path.rglob('*') if p.is_file()}}
    before=snap()
    if action=='add': (old.parent/'authorized.png').write_bytes(b'new')
    if action=='modify': old.write_bytes(b'changed')
    if action=='delete': old.unlink()  # Temporary fixture only.
    if action=='lookalike':
        p=tmp_path/(app.PREFIX.rstrip('/')+'_other/file.png');p.parent.mkdir();p.write_bytes(b'new')
    assert compare_snapshots(before,snap(),allowed_addition_prefixes=d0.AUTHORIZED_REFERENCE_ADDITIONS)['pass'] is allowed


def test_current_task_protects_all_historical_files_and_counts():
    q=compare_snapshots(d0.read_json(app.OUT/'production_before.json'),v1.snapshot(),allowed_addition_prefixes=(app.PREFIX,
        'references/architecture/master_validation_D3_v1/',
        'references/architecture/master_validation_D3_appearance_v1/'))
    assert q['pass'] and q['protected_file_count']==1537
    assert q['observed_counts']=={'manifest':220,'approved':220,'needs_human_review':0}
