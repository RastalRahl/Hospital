"""Pixel and placement checks for the proposed cutaway; never human approval."""
import pytest
from PIL import Image
import validate_architecture_d0 as d0
import validate_architecture_d1 as d1
import validate_architecture_d2 as v1
import validate_architecture_d2_v2 as v2
from rastalr_pipeline.snapshot import compare_snapshots


@pytest.fixture(scope='module')
def views():
    return {name:d1.load(v2.OUT/f'd2_{name}_native.png') for name in v2.contract()['views']}


def test_contract_stays_proposed_and_hashes_authorities():
    c=d0.read_json(v2.OUT/'d2_geometry_alpha_contract_proposed.json')
    assert c==v2.contract()
    assert c['status']=='PROPOSED_FOR_HUMAN_GEOMETRY_REVIEW'
    assert c['proposed_presentation']['approval'] is False
    assert all(d0.digest(d0.ROOT/name)==value for name,value in c['sources_sha256'].items())
    assert c['derived_mapping']['D1_centerline_y']==60
    assert c['derived_mapping']['D1_base_exclusive_y']==64
    for spec in c['views'].values():
        assert [a-b for a,b in zip(spec['cell_anchor'],spec['origin'])]==spec['image_anchor']


@pytest.mark.parametrize('name',['main','repeat','corner_main','corner_repeat'])
def test_actual_native_source_and_declared_regions(views,name):
    source=d1.load(v2.OUT/f'd2_{name}_source_8x.png')
    assert v2.check_view(views[name],source,v2.contract(),name)['pass']


@pytest.mark.parametrize('defect',['source_subpixel','mode','exterior','hole','opaque'])
def test_file_negative_controls(views,defect,tmp_path):
    im=views['corner_main'].copy(); src=d1.load(v2.OUT/'d2_corner_main_source_8x.png')
    if defect=='source_subpixel': src.putpixel((0,0),(1,2,3,255))
    if defect=='mode': im=im.convert('RGB')
    if defect=='exterior': im.putpixel((10,10),(39,55,70,255))
    if defect=='hole': im.putpixel((3,10),(0,0,0,0))
    if defect=='opaque': im.putpixel((3,10),(158,205,216,255))
    im.save(tmp_path/'native.png'); src.save(tmp_path/'source.png')
    assert not v2.check_view(d1.load(tmp_path/'native.png'),d1.load(tmp_path/'source.png'),v2.contract(),'corner_main')['pass']


@pytest.mark.parametrize('count',[1,2,4])
def test_repeats_and_corner_ownership_have_no_double_glass(views,count,tmp_path):
    run,p,l=v2.assemble(views,count)
    assert v2.check_run(d1.load(v2.ART/f'd2_run_{count}_native.png'),p,l,count)['pass']
    corner,cp,cl=v2.assemble(views,count,corner=True)
    corner.save(tmp_path/'corner.png'); actual=d1.load(tmp_path/'corner.png')
    # Upper return adds 24px carrier, never changes the 32px ground stride/body.
    assert actual.crop((0,24,12,24+32*count)).tobytes()==run.tobytes()
    assert cp==[[0,0]]+[[0,24+32*i] for i in range(1,count)]
    assert max(cl.get_flattened_data())==1
    trans,_,_,_=v2.transmission(run)
    assert trans['pass']
    assert trans['checks']['pane_response']['observed']==192+224*(count-1)


def test_corner_saved_pixels_prove_upper_connection_independently_of_base(views):
    report,scene,side,front,*_=v2.local_corner(views,saved=True)
    assert report['pass']
    assert report['computed']['opaque_overlap_pixels']==48
    assert report['computed']['translucent_overlap_pixels']==0
    assert report['computed']['cutaway_drop_px']==24
    assert report['computed']['ground_missing_before_cap']==16
    assert report['computed']['ground_missing_after_cap']==0
    assert report['visual_review']=='PENDING_HUMAN_REVIEW_OF_EXPLICIT_CUTAWAY'
    assert side.getpixel((63,50))[3]==150  # Glazed reveal, not an opaque cover.
    bad,*_=v2.local_corner(views,missing=True)
    assert bad['checks']['side_cap']['pass']  # Base still passes.
    assert bad['checks']['elbow_coverage']['pass']  # Topology still passes.
    assert not bad['checks']['upper_contact']['pass']  # Upper transition must fail.


@pytest.mark.parametrize('name',['repeat_displacement_1px','broken_contact','opaque_glass','pane_hole',
    'doubled_support','stacked_glass','anchor_mismatch_1px','missing_corner_return','corner_displacement_1px'])
def test_negative_controls_have_valid_controls_and_intended_failure(views,name):
    q=v2.negatives(views)[name]
    assert q['valid_control_pass'] and q['proven']
    assert not q['validation']['checks'][q['intended_check']]['pass']


@pytest.mark.parametrize('name,cell',[('original',(32,64)),('relocated',(64,96))])
def test_saved_relocated_contexts(views,name,cell):
    run,_,_=v2.assemble(views,2)
    q,*_=v2.context(run,cell,saved_name=name)
    assert q['pass']
    assert q['computed']['render_origin']==[cell[0]+12,cell[1]]


@pytest.mark.parametrize('action,allowed',[('add',True),('change',False),('delete',False),('lookalike',False)])
def test_v2_additions_never_exempt_historical_files(tmp_path,action,allowed):
    old=tmp_path/v2.PREFIX/'old.png'; old.parent.mkdir(parents=True); old.write_bytes(b'locked')
    def snapshot():
        return {'counts':{'manifest':220,'approved':220,'needs_human_review':0},
            'sha256':{p.relative_to(tmp_path).as_posix():d0.digest(p) for p in tmp_path.rglob('*') if p.is_file()}}
    before=snapshot()
    if action=='add': (old.parent/'new.png').write_bytes(b'new')
    if action=='change': old.write_bytes(b'changed')
    if action=='delete': old.unlink()  # Temporary fixture only.
    if action=='lookalike':
        other=tmp_path/(v2.PREFIX.rstrip('/')+'_other/new.png'); other.parent.mkdir(); other.write_bytes(b'new')
    assert compare_snapshots(before,snapshot(),allowed_addition_prefixes=d0.AUTHORIZED_REFERENCE_ADDITIONS)['pass'] is allowed


def test_all_production_and_historical_d2_v1_files_preserved():
    before=d0.read_json(v2.OUT/'production_before.json')
    report=compare_snapshots(before,v1.snapshot(),allowed_addition_prefixes=(v2.PREFIX,
        'references/architecture/master_validation_D2_appearance_v1/',
        'references/architecture/master_validation_D3_v1/',
        'references/architecture/master_validation_D3_appearance_v1/'))
    assert report['pass'] and report['protected_file_count']==1435
    assert report['observed_counts']=={'manifest':220,'approved':220,'needs_human_review':0}
    historical=[p for p in before['sha256'] if p.startswith('references/architecture/master_validation_D2_v1/')]
    assert len(historical)==len([p for p in v1.OUT.rglob('*') if p.is_file()])
