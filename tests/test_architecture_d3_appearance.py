"""Candidate-specific tests reuse geometry helpers and preserve all input files."""
import pytest
from PIL import Image
import validate_architecture_d0 as d0
import validate_architecture_d1 as d1
import validate_architecture_d2 as history
import validate_architecture_d2_v2 as d2
import validate_architecture_d2_appearance as d2app
import validate_architecture_d3 as d3
import validate_architecture_d3_appearance as app
from rastalr_pipeline.snapshot import compare_snapshots
from rastalr_pipeline.production_transition import compare_live_snapshot


@pytest.fixture(scope='module')
def inputs():
    return d0.read_json(app.CONTRACT),{n:app.candidate(n) for n in d3.NAMES}


@pytest.fixture(scope='module')
def controls(inputs):
    return d3.negative_controls(inputs[1])


def test_archive_members_and_all_sources_match_pinned_commit():
    q=app.integrity()
    assert q['pass'] and q['member_count']==81 and q['pinned_source_count']==12


@pytest.mark.parametrize('name',d3.NAMES)
def test_actual_saved_rgba_alpha_rgb_counts_and_export(inputs,name):
    c,views=inputs;q=app.check_file(name,views[name],app.candidate(name,'source_8x'),c)
    assert q['pass'] and q['checks']['alpha_histogram']['observed']==app.HIST[name]
    assert q['checks']['alpha_changed']['observed']==0
    assert q['checks']['zero_alpha_rgba_changed']['observed']==0
    assert q['checks']['rgb_changed']['observed']==(496 if name.startswith('corner') else 384)
    assert c['status']=='PROPOSED_FOR_HUMAN_GEOMETRY_REVIEW'


@pytest.mark.parametrize('name',d3.NAMES)
def test_actual_alpha_corruption_rejected_from_temporary_png(inputs,name,tmp_path):
    c,views=inputs;im=views[name].copy();p=(9,10) if name.startswith('corner') else (6,10)
    im.putpixel(p,(*im.getpixel(p)[:3],0));im.save(tmp_path/'bad.png')
    q=app.check_file(name,d1.load(tmp_path/'bad.png'),app.candidate(name,'source_8x'),c)
    assert not q['pass'] and q['checks']['alpha_changed']['observed']==1


@pytest.mark.parametrize('defect',['source_subpixel','invisible_rgb'])
def test_subpixel_and_hidden_rgb_are_not_missed_by_roundtrip_or_alpha(inputs,defect,tmp_path):
    c,views=inputs;im=views['corner_main'].copy();source=app.candidate('corner_main','source_8x')
    if defect=='source_subpixel':source.putpixel((0,0),(1,2,3,255))
    else:im.putpixel((0,0),(1,2,3,0))
    im.save(tmp_path/'native.png');source.save(tmp_path/'source.png')
    q=app.check_file('corner_main',d1.load(tmp_path/'native.png'),d1.load(tmp_path/'source.png'),c)
    assert not q['pass']
    if defect=='source_subpixel':
        assert q['geometry']['checks']['roundtrip']['pass'] and not q['geometry']['checks']['blocks']['pass']
    else:
        assert q['checks']['alpha_changed']['pass'] and q['checks']['zero_alpha_rgba_changed']['observed']==1


@pytest.mark.parametrize('view,point,key',[('repeat',(0,12),'repeat_outside'),('corner_main',(6,40),'corner_body_main'),('corner_repeat',(9,12),'upper_return')])
def test_rgb_relationship_failures_are_independent_of_shape_and_alpha(inputs,view,point,key,tmp_path):
    c,views=inputs;assert app.relationships(views,c)['pass']
    altered={n:im.copy() for n,im in views.items()};rgba=altered[view].getpixel(point)
    altered[view].putpixel(point,(1,2,3,rgba[3]));altered[view].save(tmp_path/'changed.png');altered[view]=d1.load(tmp_path/'changed.png')
    assert not app.relationships(altered,c)['checks'][key]['pass']


@pytest.mark.parametrize('count',[1,2,4])
@pytest.mark.parametrize('corner',[False,True])
def test_saved_straight_and_corner_repeats_match_selected_candidate(inputs,count,corner):
    _,views=inputs;im,p,l=d2.assemble(views,count,corner=corner);name=('corner_' if corner else 'straight_')+str(count)
    actual=d1.load(app.ART/f'{name}_native.png');assert actual.tobytes()==im.tobytes()
    assert max(l.get_flattened_data())==1
    offset=24 if corner else 0
    assert d2.check_run(actual.crop((0,offset,12,offset+32*count)),[[0,i*32] for i in range(count)],l.crop((0,offset,12,offset+32*count)),count)['pass']
    transmission,_,_,_=d2.transmission(actual);assert transmission['pass']
    assert transmission['checks']['pane_response']['observed']==192+224*(count-1)+(40 if corner else 0)
    for i,(x,y) in enumerate(p):
        name=('corner_' if corner and i==0 else '')+('main' if i==count-1 else 'repeat');view=views[name]
        assert actual.crop((x,y,x+view.width,y+view.height)).tobytes()==view.tobytes()


@pytest.mark.parametrize('name,delta',[('original',(0,0)),('relocated',(32,32))])
def test_saved_both_corners_and_enclosure_preserve_unchanged_sources(inputs,name,delta):
    _,views=inputs;q,scene,structure=d3.assembly(views,enclosure=True,delta=delta)
    assert q['pass'] and q['checks']['front_open']['pass']
    assert d1.load(app.ART/f'enclosure_{name}_structure.png').tobytes()==structure.tobytes()
    assert d1.load(app.ART/f'enclosure_{name}_clean.png').tobytes()==scene.tobytes()
    for side in ('northeast','northwest'):
        co=q['checks'][side]['computed']
        assert co['opaque_overlap_pixels']==48 and co['stacked_glass_pixels']==co['hidden_glass_pixels']==0
    d2run,_,_=d2.assemble({n:d2app.candidate(n) for n in d3.NAMES},2,corner=True)
    layer=d1.load(app.ART/f'enclosure_{name}_d2_layer.png');x,y=60+delta[0],36+delta[1]
    assert layer.crop((x,y,x+12,y+d2run.height)).tobytes()==d2run.tobytes()


@pytest.mark.parametrize('name',['wrong_left_origin','anchor_1px','missing_return','displaced_return','D1_wrong_terminal',
    'repeat_drift_1px','broken_contact','pane_hole','opaque_glass','doubled_support','D3_wrong_terminal','stacked_glass'])
def test_candidate_negative_controls_have_valid_controls(controls,name):
    q=controls[name];assert q['valid_control_pass'] and q['proven']
    assert not q['validation']['checks'][q['intended_check']]['pass']


@pytest.mark.parametrize('action,allowed',[('add',True),('modify',False),('delete',False),('lookalike',False)])
def test_authorized_additions_keep_exact_hash_protection(tmp_path,action,allowed):
    old=tmp_path/app.PREFIX/'sources/protected.png';old.parent.mkdir(parents=True);old.write_bytes(b'locked')
    def snap():return {'counts':{'manifest':220,'approved':220,'needs_human_review':0},'sha256':{p.relative_to(tmp_path).as_posix():d0.digest(p) for p in tmp_path.rglob('*') if p.is_file()}}
    baseline=snap()
    if action=='add':(old.parent/'new.png').write_bytes(b'new')
    if action=='modify':old.write_bytes(b'changed')
    if action=='delete':old.unlink()  # Temporary fixture only.
    if action=='lookalike':
        p=tmp_path/(app.PREFIX.rstrip('/')+'_other/new.png');p.parent.mkdir();p.write_bytes(b'new')
    assert compare_snapshots(baseline,snap(),allowed_addition_prefixes=d0.AUTHORIZED_REFERENCE_ADDITIONS)['pass'] is allowed


def test_all_historical_production_files_and_counts_unchanged():
    q=compare_live_snapshot(d0.read_json(app.OUT/'production_before.json'),history.snapshot(),allowed_addition_prefixes=(app.PREFIX,
        'references/architecture/master_validation_D4_v1/',
        'references/architecture/master_validation_D4_appearance_v1/'))
    assert q['pass'] and q['protected_file_count']==1810
    assert q['observed_counts']=={'manifest':224,'approved':220,'needs_human_review':4}
