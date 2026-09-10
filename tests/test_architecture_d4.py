"""D4 conformance is to a proposal; no test grants geometry or production approval."""
import pytest
from PIL import Image
import validate_architecture_d0 as d0
import validate_architecture_d1 as d1
import validate_architecture_d2 as history
import validate_architecture_d2_v2 as side
import validate_architecture_d4 as d4
from rastalr_pipeline.snapshot import compare_snapshots


@pytest.fixture(scope='module')
def inputs():
    c=d0.read_json(d4.OUT/'d4_geometry_alpha_contract_proposed.json')
    return c,{n:d1.load(d4.OUT/f'd4_{n}_native.png') for n in d4.NAMES}


@pytest.fixture(scope='module')
def negatives(inputs):
    return d4.negative_controls(inputs[1])


@pytest.mark.parametrize('name',d4.NAMES)
def test_saved_native_regions_and_every_source_subpixel(inputs,name):
    c,views=inputs;export=d1.load(d4.OUT/f'd4_{name}_source_8x.png')
    q=side.check_view(views[name],export,c,name)
    assert q['pass'] and c['status']==d4.STATUS
    assert q['computed']['alpha_histogram']==({255:240,150:144} if name=='main' else {255:216,150:168})
    assert [a-b for a,b in zip(c['views'][name]['cell_anchor'],c['views'][name]['image_anchor'])]==[0,12]


@pytest.mark.parametrize('count',[1,2,4])
def test_reloaded_repeat_selection_shared_supports_and_transmission(inputs,count):
    _,views=inputs;im,p,cov=d4.assemble(views,count)
    actual=d1.load(d4.ART/f'run_{count}_native.png')
    assert d1.pixel_difference(im,actual)==0
    assert d4.check_run(actual,p,cov,count)['pass']
    assert d1.load(d4.ART/f'run_{count}_glass_coverage.png').tobytes()==cov.convert('L').tobytes()
    for i in range(count):
        assert actual.crop((i*32,0,i*32+32,12)).tobytes()==views['main' if i==count-1 else 'repeat'].tobytes()
    q,backs,obj,scenes=side.transmission(actual)
    assert q['pass'] and q['checks']['pane_response']['observed']==144+(count-1)*168
    for name in backs:
        assert d1.load(d4.ART/f'run_{count}_{name}_background.png').tobytes()==backs[name].tobytes()
        assert d1.load(d4.ART/f'run_{count}_{name}_composite.png').tobytes()==scenes[name].tobytes()
    assert d1.load(d4.ART/f'run_{count}_object_layer.png').tobytes()==obj.tobytes()


@pytest.mark.parametrize('name,width,depth,delta',[
    ('original',4,2,(0,0)),('relocated',4,2,(32,32)),('additional_size',3,3,(0,0)),('local_corners',2,1,(0,0))])
def test_each_saved_enclosure_four_corners_and_exact_saved_layers(inputs,name,width,depth,delta):
    q,scene,structure=d4.enclosure(inputs[1],width,depth,delta)
    assert q['pass']
    label=name if name=='local_corners' else 'enclosure_'+name
    assert scene.tobytes()==d1.load(d4.ART/f'{label}_clean.png').tobytes()
    assert structure.tobytes()==d1.load(d4.ART/f'{label}_structure.png').tobytes()
    composed=Image.new('RGBA',structure.size)
    for n in ('d2','d3','d1','d4'): composed.alpha_composite(d1.load(d4.ART/f'{label}_{n}_layer.png'))
    assert d1.pixel_difference(composed,structure)==0
    bg=d1.load(d4.ART/f'{label}_background.png');obj=d1.load(d4.ART/f'{label}_object_layer.png')
    assert d1.pixel_difference(Image.alpha_composite(bg,structure),scene)==0
    assert d1.pixel_difference(Image.alpha_composite(Image.alpha_composite(bg,obj),structure),d1.load(d4.ART/f'{label}_object_composite.png'))==0
    for corner in ('southwest','southeast'):
        measured=q['checks'][corner]['checks']['overlap']['computed']
        assert measured=={'intentional_opaque':32,'unexpected_opaque':0,'unexpected_overlap':0,'missing_contact':0,'stacked_glass':0,'hidden_glass':0}
        co=q['checks'][corner]['computed'];assert co['front_top']==co['side_base_exclusive']-4
        assert co['front_base_exclusive']==co['side_base_exclusive']+8
    for corner in ('northwest','northeast'):
        assert q['checks'][corner]['computed']['opaque_overlap_pixels']==48
        assert q['checks'][corner]['computed']['hidden_glass_pixels']==q['checks'][corner]['computed']['stacked_glass_pixels']==0


def test_independent_relocation_is_exact_translation():
    first=d1.load(d4.ART/'enclosure_original_structure.png');second=d1.load(d4.ART/'enclosure_relocated_structure.png')
    assert first.tobytes()==second.crop((32,32,32+first.width,32+first.height)).tobytes()


@pytest.mark.parametrize('name',['repeat_displacement','broken_frame','opaque_glass','pane_hole','doubled_support','wrong_terminal','stacked_glass',
    'anchor_1px','baseline_confusion','missing_contact','wrong_side_terminal','source_subpixel'])
def test_actual_negative_pixels_or_coordinates_fail_target_check_with_valid_control(negatives,name):
    q=negatives[name]
    assert q['valid_control_pass'] and q['proven']
    assert not q['validation']['checks'][q['intended_check']]['pass']
    assert d1.load(d4.ART/f'broken_{name}.png').tobytes()==q['image'].tobytes()


def test_single_source_subpixel_corruption_cannot_hide_in_roundtrip(inputs,tmp_path):
    c,views=inputs;im=views['main'];export=d1.load(d4.OUT/'d4_main_source_8x.png')
    assert side.check_view(im,export,c,'main')['pass']
    export.putpixel((0,0),(1,2,3,255));export.save(tmp_path/'broken.png')
    q=side.check_view(im,d1.load(tmp_path/'broken.png'),c,'main')
    assert q['checks']['roundtrip']['pass'] and not q['checks']['blocks']['pass']


@pytest.mark.parametrize('defect',['opaque','hole','frame'])
def test_reloaded_native_alpha_defects_are_rejected_independently_of_export(inputs,tmp_path,defect):
    c,views=inputs;im=views['main'].copy()
    assert side.check_view(im,im.resize((256,96),Image.Resampling.NEAREST),c,'main')['pass']
    point=(5,1) if defect=='frame' else (5,6);a=255 if defect=='opaque' else 0
    im.putpixel(point,(*im.getpixel(point)[:3],a));im.save(tmp_path/'broken.png');im=d1.load(tmp_path/'broken.png')
    q=side.check_view(im,im.resize((256,96),Image.Resampling.NEAREST),c,'main')
    assert q['checks']['blocks']['pass'] and not q['pass']


@pytest.mark.parametrize('action,allowed',[('add',True),('modify',False),('delete',False),('lookalike',False)])
def test_narrow_d4_addition_permission_keeps_existing_hashes_mandatory(tmp_path,action,allowed):
    p=tmp_path/d4.PREFIX/'protected.png';p.parent.mkdir(parents=True);p.write_bytes(b'original')
    def snap():return {'counts':{'manifest':220,'approved':220,'needs_human_review':0},'sha256':{f.relative_to(tmp_path).as_posix():d0.digest(f) for f in tmp_path.rglob('*') if f.is_file()}}
    before=snap()
    if action=='add':(p.parent/'new.png').write_bytes(b'new')
    if action=='modify':p.write_bytes(b'changed')
    if action=='delete':p.unlink()  # Temporary fixture only.
    if action=='lookalike':
        f=tmp_path/(d4.PREFIX.rstrip('/')+'_other/new.png');f.parent.mkdir();f.write_bytes(b'new')
    assert compare_snapshots(before,snap(),allowed_addition_prefixes=d0.AUTHORIZED_REFERENCE_ADDITIONS)['pass'] is allowed


def test_all_historical_bytes_and_production_counts_unchanged():
    q=compare_snapshots(d0.read_json(d4.OUT/'production_before.json'),history.snapshot(),allowed_addition_prefixes=(d4.PREFIX,))
    assert q['pass'] and q['protected_file_count']==2022
    assert q['observed_counts']=={'manifest':220,'approved':220,'needs_human_review':0}


def test_contract_proposal_and_source_hashes_still_match():
    c=d0.read_json(d4.OUT/'d4_geometry_alpha_contract_proposed.json')
    assert c==d4.contract() and c['human_visual_review']['approval'] is False
    for p,h in c['sources_sha256'].items(): assert d0.digest(d4.ROOT/p)==h
