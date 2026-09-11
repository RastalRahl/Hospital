"""Focused locked-candidate checks; destructive cases use copies or temp files."""
import pytest
from PIL import Image
import validate_architecture_d0 as d0
import validate_architecture_d1 as d1
import validate_architecture_d2 as history
import validate_architecture_d2_v2 as side
import validate_architecture_d4 as d4
import validate_architecture_d4_appearance as app
from rastalr_pipeline.snapshot import compare_snapshots


@pytest.fixture(scope='module')
def inputs():
    return d0.read_json(app.CONTRACT),{n:app.candidate(n) for n in d4.NAMES}


@pytest.fixture(scope='module')
def controls(inputs):
    return app.negative_controls(inputs[1],inputs[0])


def test_archive_and_all_fifteen_reference_copies_match_pinned_git_bytes():
    q=app.integrity()
    assert q['pass'] and q['member_count']==93 and q['pinned_references']==15
    assert q['newline_normalization'] is False


@pytest.mark.parametrize('name',d4.NAMES)
def test_saved_candidate_exact_exports_alpha_and_rgb(inputs,name):
    c,views=inputs;q=app.check_file(name,views[name],app.candidate(name,'source_8x'),c)
    assert q['pass'] and q['checks']['rgb_changed']['observed']==384
    assert q['checks']['alpha_changed']['observed']==0
    assert q['checks']['histogram']['observed']==app.HIST[name]
    assert c['status']=='PROPOSED_FOR_HUMAN_GEOMETRY_REVIEW'


@pytest.mark.parametrize('point,key',[((6,2),'outside'),((30,6),'extension')])
def test_saved_rgb_corruption_fails_relationship_without_changing_alpha(inputs,tmp_path,point,key):
    c,views=inputs;assert app.relationships(views,c)['pass']
    altered={n:im.copy() for n,im in views.items()};im=altered['repeat'];im.putpixel(point,(1,2,3,im.getpixel(point)[3]));im.save(tmp_path/'broken.png')
    altered['repeat']=d1.load(tmp_path/'broken.png')
    assert d1.pixel_difference(altered['repeat'],views['repeat'],(3,))==0
    assert not app.relationships(altered,c)['checks'][key]['pass']


def test_export_subpixel_is_detected_when_roundtrip_passes(inputs,tmp_path):
    c,views=inputs;source=app.candidate('main','source_8x')
    assert app.check_file('main',views['main'],source,c)['pass']
    source.putpixel((0,0),(1,2,3,255));source.save(tmp_path/'broken.png')
    q=app.check_file('main',views['main'],d1.load(tmp_path/'broken.png'),c)
    assert not q['pass'] and q['geometry']['checks']['roundtrip']['pass']
    assert q['geometry']['checks']['blocks']['observed']==1


@pytest.mark.parametrize('name',d4.NAMES)
def test_saved_alpha_edit_rejected_even_with_matching_export(inputs,name,tmp_path):
    c,views=inputs;im=views[name].copy();im.putpixel((6,6),(*im.getpixel((6,6))[:3],0));im.save(tmp_path/'bad.png');im=d1.load(tmp_path/'bad.png')
    q=app.check_file(name,im,im.resize((256,96),Image.Resampling.NEAREST),c)
    assert q['geometry']['checks']['blocks']['pass'] and q['checks']['alpha_changed']['observed']==1 and not q['pass']


@pytest.mark.parametrize('n',[1,2,4])
def test_saved_runs_use_actual_views_and_transmit_every_pane_pixel(inputs,n):
    c,views=inputs;im,p,cov=d4.assemble(views,n);actual=d1.load(app.ART/f'run_{n}_native.png')
    assert actual.tobytes()==im.tobytes() and d4.check_run(actual,p,cov,n)['pass']
    for i in range(n):assert actual.crop((32*i,0,32*i+32,12)).tobytes()==views['main' if i==n-1 else 'repeat'].tobytes()
    q,backs,obj,scenes=side.transmission(actual)
    assert q['pass'] and q['checks']['pane_response']['observed']==144+168*(n-1)
    for key in backs:
        assert d1.load(app.ART/f'run_{n}_{key}_background.png').tobytes()==backs[key].tobytes()
        assert d1.load(app.ART/f'run_{n}_{key}_composite.png').tobytes()==scenes[key].tobytes()
    assert d1.load(app.ART/f'run_{n}_object_layer.png').tobytes()==obj.tobytes()


@pytest.mark.parametrize('name,w,d,delta',[('local',2,1,(0,0)),('original',4,2,(0,0)),('relocated',4,2,(32,32)),('additional_size',3,3,(0,0))])
def test_saved_actual_enclosure_preserves_sources_and_all_four_contacts(inputs,name,w,d,delta):
    q,scene,structure=d4.enclosure(inputs[1],w,d,delta)
    assert q['pass'] and scene.tobytes()==d1.load(app.ART/f'enclosure_{name}_clean.png').tobytes()
    assert structure.tobytes()==d1.load(app.ART/f'enclosure_{name}_structure.png').tobytes()
    for corner in ('southwest','southeast'):
        co=q['checks'][corner]['checks']['overlap']['computed']
        assert co=={'intentional_opaque':32,'unexpected_opaque':0,'unexpected_overlap':0,'missing_contact':0,'stacked_glass':0,'hidden_glass':0}
    for corner in ('northwest','northeast'):
        co=q['checks'][corner]['computed'];assert co['opaque_overlap_pixels']==48 and co['stacked_glass_pixels']==co['hidden_glass_pixels']==0
    for layer in ('d1','d2','d3'):
        assert (app.ART/f'enclosure_{name}_{layer}_layer.png').read_bytes()==(app.ART/f'scaffold_{name}_{layer}_layer.png').read_bytes()
        if name!='local':assert (app.ART/f'enclosure_{name}_{layer}_layer.png').read_bytes()==(d4.ART/f'enclosure_{name}_{layer}_layer.png').read_bytes()
    before=d1.load(app.ART/f'scaffold_{name}_clean.png');coverage=d1.load(app.ART/f'enclosure_{name}_d4_layer.png')
    assert app.compare_scenes(scene,before,coverage)['pass']
    bg=d1.load(app.ART/f'enclosure_{name}_background.png');obj=d1.load(app.ART/f'enclosure_{name}_object_layer.png')
    assert Image.alpha_composite(Image.alpha_composite(bg,obj),structure).tobytes()==d1.load(app.ART/f'enclosure_{name}_object_composite.png').tobytes()


def test_off_d4_scene_corruption_is_detected_from_saved_pixels(tmp_path):
    scene=d1.load(app.ART/'enclosure_original_clean.png');base=d1.load(app.ART/'scaffold_original_clean.png');mask=d1.load(app.ART/'enclosure_original_d4_layer.png')
    assert app.compare_scenes(scene,base,mask)['pass']
    scene.putpixel((0,0),(1,2,3,255));scene.save(tmp_path/'corrupted.png')
    q=app.compare_scenes(d1.load(tmp_path/'corrupted.png'),base,mask)
    assert not q['pass'] and q['checks']['outside_D4']['observed']==1


def test_relocation_and_local_scaffold_crop_reproduction():
    original=d1.load(app.ART/'enclosure_original_structure.png');moved=d1.load(app.ART/'enclosure_relocated_structure.png')
    assert original.tobytes()==moved.crop((32,32,32+original.width,32+original.height)).tobytes()
    scaffold=d1.load(app.ART/'scaffold_local_clean.png')
    for name,edge in [('southwest',64),('southeast',128)]:assert scaffold.crop((edge-16,72,edge+20,108)).tobytes()==d1.load(d4.ART/f'{name}_clean.png').tobytes()


@pytest.mark.parametrize('name',['repeat_displacement','broken_frame','opaque_glass','pane_hole','doubled_support','wrong_terminal','stacked_glass',
    'anchor_1px','baseline_confusion','missing_contact','wrong_side_terminal','source_subpixel','repeat_rgb_outside','repeat_rgb_continuation'])
def test_negative_controls_use_actual_candidate_and_passing_control(controls,name):
    q=controls[name];assert q['valid_control_pass'] and q['proven']
    assert not q['validation']['checks'][q['intended_check']]['pass']
    assert d1.load(app.ART/f'broken_{name}.png').tobytes()==q['image'].tobytes()


@pytest.mark.parametrize('action,allowed',[('add',True),('modify',False),('delete',False),('lookalike',False)])
def test_authorized_additions_preserve_existing_hashes_in_allowed_tree(tmp_path,action,allowed):
    old=tmp_path/app.PREFIX/'protected.png';old.parent.mkdir(parents=True);old.write_bytes(b'locked')
    def snap():return {'counts':{'manifest':220,'approved':220,'needs_human_review':0},'sha256':{p.relative_to(tmp_path).as_posix():d0.digest(p) for p in tmp_path.rglob('*') if p.is_file()}}
    baseline=snap()
    if action=='add':(old.parent/'new.png').write_bytes(b'new')
    if action=='modify':old.write_bytes(b'changed')
    if action=='delete':old.unlink()  # Only a temporary test fixture.
    if action=='lookalike':
        p=tmp_path/(app.PREFIX.rstrip('/')+'_other/new.png');p.parent.mkdir();p.write_bytes(b'new')
    assert compare_snapshots(baseline,snap(),allowed_addition_prefixes=d0.AUTHORIZED_REFERENCE_ADDITIONS)['pass'] is allowed


def test_all_historical_bytes_and_production_counts_are_preserved():
    q=compare_snapshots(d0.read_json(app.OUT/'production_before.json'),history.snapshot(),allowed_addition_prefixes=(app.PREFIX,))
    assert q['pass'] and q['protected_file_count']==2145
    assert q['observed_counts']=={'manifest':220,'approved':220,'needs_human_review':0}
