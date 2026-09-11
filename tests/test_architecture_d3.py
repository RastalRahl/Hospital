"""D3 structural reflection and rendered integration; no production approval."""
import pytest
from PIL import Image
import validate_architecture_d0 as d0
import validate_architecture_d1 as d1
import validate_architecture_d2 as historical
import validate_architecture_d2_v2 as d2
import validate_architecture_d2_appearance as appearance
import validate_architecture_d3 as d3
from rastalr_pipeline.snapshot import compare_snapshots
from rastalr_pipeline.production_transition import compare_live_snapshot


@pytest.fixture(scope='module')
def inputs():
    return d0.read_json(d3.OUT/'d3_geometry_alpha_contract_proposed.json'),{n:d1.load(d3.OUT/f'd3_{n}_native.png') for n in d3.NAMES}


def test_reflection_is_of_regions_and_preserves_proposed_status(inputs):
    c,views=inputs;left=d0.read_json(appearance.CONTRACT)
    assert c==d3.contract() and c['status']=='PROPOSED_FOR_HUMAN_GEOMETRY_REVIEW'
    assert c['human_visual_review']['approval'] is False
    assert d3.reflect([12,0,24,32],32)==[8,0,20,32]
    assert d3.reflect([2,4,4,24],12)==[8,4,10,24]
    for name,s in c['views'].items():
        assert s['frame']==[d3.reflect(r,12) for r in left['views'][name]['frame']]
        assert s['pane']==[d3.reflect(r,12) for r in left['views'][name]['pane']]
        assert [a-b for a,b in zip(s['cell_anchor'],s['image_anchor'])]==s['origin']
        assert set(views[name].get_flattened_data())<={(0,0,0,0),d2.FRAME,d2.GLASS}
    assert all(d0.digest(d0.ROOT/p)==h for p,h in c['sources_sha256'].items())


@pytest.mark.parametrize('name',d3.NAMES)
def test_saved_native_source_alpha_and_envelope(inputs,name):
    c,views=inputs
    assert d2.check_view(views[name],d1.load(d3.OUT/f'd3_{name}_source_8x.png'),c,name)['pass']
    for rect in c['views'][name]['exterior']:
        assert set(views[name].crop(tuple(rect)).get_flattened_data())=={(0,0,0,0)}


@pytest.mark.parametrize('defect',['left_geometry','source_subpixel','exterior','mode','size'])
def test_wrong_orientation_or_export_is_rejected_from_saved_copy(inputs,defect,tmp_path):
    c,views=inputs;im=views['corner_main'].copy();source=d1.load(d3.OUT/'d3_corner_main_source_8x.png')
    if defect=='left_geometry':im=d1.load(d2.OUT/'d2_corner_main_native.png')
    if defect=='source_subpixel':source.putpixel((0,0),(1,2,3,255))
    if defect=='exterior':im.putpixel((0,0),(39,55,70,255))
    if defect=='mode':im=im.convert('RGB')
    if defect=='size':im=im.crop((0,0,11,56))
    im.save(tmp_path/'native.png');source.save(tmp_path/'source.png')
    q=d2.check_view(d1.load(tmp_path/'native.png'),d1.load(tmp_path/'source.png'),c,'corner_main')
    assert not q['pass']
    if defect=='source_subpixel':assert not q['checks']['blocks']['pass'] and q['checks']['roundtrip']['pass']


@pytest.mark.parametrize('count',[1,2,4])
@pytest.mark.parametrize('corner',[False,True])
def test_actual_saved_runs_view_selection_supports_and_transmission(inputs,count,corner):
    _,views=inputs;run,p,l=d2.assemble(views,count,corner=corner)
    name=('corner_' if corner else 'straight_')+str(count)
    saved=d1.load(d3.ART/f'{name}_native.png');assert saved.tobytes()==run.tobytes()
    offset=24 if corner else 0
    assert d2.check_run(saved.crop((0,offset,12,offset+32*count)),[[0,i*32] for i in range(count)],l.crop((0,offset,12,offset+32*count)),count)['pass']
    assert max(l.get_flattened_data())==1
    assert d2.transmission(saved)[0]['pass']
    for i,origin in enumerate(p):
        view=('corner_' if corner and i==0 else '')+('main' if i==count-1 else 'repeat')
        im=views[view];assert saved.crop((0,origin[1],12,origin[1]+im.height)).tobytes()==im.tobytes()


def test_ne_uses_actual_D1_right_terminal_and_measures_overlap(inputs):
    _,views=inputs;q,_,_=d3.assembly(views)
    assert q['pass']
    co=q['checks']['northeast']['computed']
    assert co['opaque_overlap_pixels']==48 and co['stacked_glass_pixels']==co['hidden_glass_pixels']==0
    assert [co['top_y'],co['base_y'],co['cap_y']]==[36,64,60]
    assert q['computed']['sw_missing_before_north_cap']==16
    assert q['computed']['sw_missing_after']==0
    wrong,_,_=d3.assembly(views,defect='d1_missing_terminal')
    assert not wrong['checks']['D1_terminal_post']['pass']
    # A wrong terminal leaves the top/base rails intact; overlap alone cannot
    # detect the missing vertical closing post. Its alpha must fail separately.
    assert wrong['checks']['D1_terminal_post']['observed']['alpha_min']==150
    assert wrong['checks']['northeast']['checks']['upper_contact']['pass']


@pytest.mark.parametrize('name,delta',[('original',(0,0)),('relocated',(32,32))])
def test_saved_enclosure_preserves_D1_D2_and_both_corners(inputs,name,delta):
    _,views=inputs;q,scene,structure=d3.assembly(views,enclosure=True,delta=delta)
    assert q['pass'] and q['checks']['northeast']['pass'] and q['checks']['northwest']['pass']
    assert d1.load(d3.ART/f'enclosure_{name}_structure.png').tobytes()==structure.tobytes()
    assert d1.load(d3.ART/f'enclosure_{name}_clean.png').tobytes()==scene.tobytes()
    assert q['checks']['front_open']['pass'] and q['checks']['side_intersections']['observed']==0
    d2run,_,_=d2.assemble({n:appearance.candidate(n) for n in d3.NAMES},2,corner=True)
    layer=d1.load(d3.ART/f'enclosure_{name}_d2_layer.png');x,y=60+delta[0],36+delta[1]
    assert layer.crop((x,y,x+12,y+d2run.height)).tobytes()==d2run.tobytes()


@pytest.mark.parametrize('name,cell',[('original',(64,64)),('relocated',(96,96))])
def test_saved_right_wall_context_anchor(inputs,name,cell):
    _,views=inputs;run,_,_=d2.assemble(views,2);q,scene=d3.right_context(run,cell)
    assert q['pass'] and q['computed']['origin']==[cell[0]+8,cell[1]]
    assert scene.tobytes()==d1.load(d3.ART/f'right_wall_{name}_clean.png').tobytes()


@pytest.mark.parametrize('name',['wrong_left_origin','anchor_1px','missing_return','displaced_return','D1_wrong_terminal',
    'repeat_drift_1px','broken_contact','pane_hole','opaque_glass','doubled_support','D3_wrong_terminal','stacked_glass'])
def test_broken_fixture_has_passing_control_and_fails_intended_check(inputs,name):
    _,views=inputs;q=d3.negative_controls(views)[name]
    assert q['valid_control_pass'] and q['proven']
    assert not q['validation']['checks'][q['intended_check']]['pass']


@pytest.mark.parametrize('action,allowed',[('add',True),('modify',False),('delete',False),('lookalike',False)])
def test_D3_additions_never_exempt_existing_files(tmp_path,action,allowed):
    old=tmp_path/d3.PREFIX/'protected.png';old.parent.mkdir(parents=True);old.write_bytes(b'locked')
    def snap():return {'counts':{'manifest':220,'approved':220,'needs_human_review':0},'sha256':{p.relative_to(tmp_path).as_posix():d0.digest(p) for p in tmp_path.rglob('*') if p.is_file()}}
    before=snap()
    if action=='add':(old.parent/'new.png').write_bytes(b'new')
    if action=='modify':old.write_bytes(b'changed')
    if action=='delete':old.unlink()  # Only temporary test fixture.
    if action=='lookalike':
        p=tmp_path/(d3.PREFIX.rstrip('/')+'_other/new.png');p.parent.mkdir();p.write_bytes(b'new')
    assert compare_snapshots(before,snap(),allowed_addition_prefixes=d0.AUTHORIZED_REFERENCE_ADDITIONS)['pass'] is allowed


def test_current_task_preserves_every_historical_hash_and_count():
    q=compare_live_snapshot(d0.read_json(d3.OUT/'production_before.json'),historical.snapshot(),allowed_addition_prefixes=(d3.PREFIX,
        'references/architecture/master_validation_D3_appearance_v1/',
        'references/architecture/master_validation_D4_v1/',
        'references/architecture/master_validation_D4_appearance_v1/'))
    assert q['pass'] and q['protected_file_count']==1688
    assert q['observed_counts']=={'manifest':224,'approved':220,'needs_human_review':4}
