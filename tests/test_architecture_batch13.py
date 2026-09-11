"""Production staging, exclusive view resolution and bounded-transition regressions."""
import copy
import json
import shutil
import zipfile
from pathlib import Path
import pytest
from PIL import Image
import build_architecture_glass_partitions_batch_13 as build
import validate_architecture_d4 as d4
from rastalr_pipeline import core, batch13 as b, views, production_transition as transition
from rastalr_pipeline.snapshot import compare_snapshots

ROOT=core.ROOT


@pytest.fixture(scope='module')
def assets():
    actual={a['id']:a for a in core.load_manifest()['assets']}
    return [actual[i] for i in b.IDS]


@pytest.fixture
def isolated(tmp_path,monkeypatch,assets):
    # Sources, contracts and staged PNGs are copied to an isolated project; no real promotion.
    for a in assets:
        names={a['geometry_contract']}
        for v in a['views'].values():names.update(v[k] for k in ('normalized_path','source_native','source_8x'))
        for name in names:
            dest=tmp_path/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dest)
    (tmp_path/'metadata').mkdir(exist_ok=True)
    for name in ('ROOT','MANIFEST_PATH','CATALOG_PATH','QA_JSON_PATH','QA_MD_PATH','QA_CSV_PATH'):
        old=getattr(core,name);monkeypatch.setattr(core,name,tmp_path if name=='ROOT' else tmp_path/old.relative_to(ROOT))
    copied=copy.deepcopy(assets);core.save_manifest({'schema_version':'1.0','native_grid':32,'assets':copied})
    return tmp_path,copied


def test_exact_four_parent_inventory_and_twelve_exclusive_views(assets):
    assert assets==b.blueprints(ROOT)
    assert len(assets)==4 and sum(len(a['views']) for a in assets)==12
    assert all(a['approval_status']=='needs_human_review' and not a['final_path'] for a in assets)
    assert len({v['normalized_path'] for a in assets for v in a['views'].values()})==12
    assert all(a['normalized_path']==a['views']['main']['normalized_path'] for a in assets)
    rows=transition.rows((ROOT/'metadata/catalog.csv').read_text())
    assert len(rows)==224 and len({r['id'] for r in rows})==224
    assert all(r['component_count']=='0' for r in rows if r['id'] in b.IDS)


@pytest.mark.parametrize('member,n,corner,names',[
    (0,1,False,['main']),(0,4,False,['repeat']*3+['main']),
    (1,1,True,['corner_main']),(1,4,True,['corner_repeat','repeat','repeat','main']),
    (2,2,False,['repeat','main']),(2,2,True,['corner_repeat','main']),
    (3,2,False,['repeat','main'])])
def test_exclusive_selection_and_manifest_anchor_mapping(assets,member,n,corner,names):
    a=assets[member];im,pp,cc,origin=views.run(ROOT,a,n,back_corner=corner,cell=(96,128))
    assert [p['name'] for p in pp]==names
    assert build.run_check(a,im,pp,cc,origin,n,corner)['pass']
    for i,p in enumerate(pp):
        v=a['views'][p['name']]
        assert p['cell']==[96+i*a['repeat_stride_native'][0],128+i*a['repeat_stride_native'][1]]
        assert p['origin']==[p['cell'][j]+v['cell_anchor'][j]-v['image_anchor'][j] for j in range(2)]


@pytest.mark.parametrize('member',range(4))
def test_production_glass_qa_actual_twelve_hashes_exports_alpha_and_relationships(assets,member):
    a=assets[member];q=views.qa_asset(ROOT,a)
    assert q['status']=='pass' and len(q['views'])==len(a['views'])
    for name,result in q['views'].items():
        assert result['alpha']['partially_transparent_pixels']>0 and result['alpha']['has_transparency']
        assert result['checks']['source_blocks']['observed']==0 and result['checks']['alpha_map']['observed']==0
        assert result['checks']['sha256']['observed']==views.digest(ROOT/a['views'][name]['source_native'])
    if member in (0,3):assert q['views']['main']['alpha']['fully_transparent_pixels']==0


@pytest.mark.parametrize('defect,key',[
    ('opaque','pane_0'),('hole','pane_0'),('broken_contact','frame_0'),('mode','mode'),('size','size'),('exterior','exterior'),('export_subpixel','source_blocks'),('anchor','render_origin')])
def test_optin_production_qa_rejects_actual_corruptions(isolated,defect,key):
    root,assets=isolated;a=assets[2];name='corner_main';v=a['views'][name];p=root/v['normalized_path']
    assert views.check_view(root,a,name)['status']=='pass'
    im=views.load(p);s=views.contract_view(root,a,name)
    if defect in ('opaque','hole','broken_contact'):
        rect=s['frame' if defect=='broken_contact' else 'pane'][0];point=tuple(rect[:2]);rgb=im.getpixel(point)[:3]
        im.putpixel(point,(*rgb,255 if defect=='opaque' else 0));im.save(p)
    elif defect=='mode':im.convert('RGB').save(p)
    elif defect=='size':im.crop((0,0,11,56)).save(p)
    elif defect=='exterior':
        point=next((x,y) for y in range(im.height) for x in range(im.width) if im.getpixel((x,y))[3]==0)
        im.putpixel(point,(10,20,30,255));im.save(p)
    elif defect=='export_subpixel':
        p=root/v['source_8x'];im=views.load(p);im.putpixel((0,0),(1,2,3,255));im.save(p)
    else:v['render_origin'][0]+=1
    q=views.check_view(root,a,name)
    assert q['status']=='fail' and not q['checks'][key]['pass']


@pytest.mark.parametrize('defect',['missing','corrupt','missing_record','invalid_context'])
def test_selected_alternate_fails_without_reference_fallback(isolated,defect):
    root,assets=isolated;a=assets[1];v=a['views']['corner_repeat']
    assert views.resolve(root,a,index=0,count=2,back_corner=True)[0]=='corner_repeat'
    if defect=='missing':(root/v['normalized_path']).unlink()
    if defect=='corrupt':(root/v['normalized_path']).write_bytes(b'not PNG')
    if defect=='missing_record':del a['views']['corner_repeat']
    assert (root/v['source_native']).is_file()
    with pytest.raises((ValueError,FileNotFoundError)):
        views.resolve(root,a,index=0,count=0 if defect=='invalid_context' else 2,back_corner=True)


def test_future_approval_promotes_all_views_together_only_in_temporary_project(isolated):
    root,assets=isolated;a=assets[1]
    assert core.approve_assets([a['id']])==[a['id']]
    promoted=next(x for x in core.load_manifest()['assets'] if x['id']==a['id'])
    assert promoted['approval_status']=='approved'
    for name,v in promoted['views'].items():
        assert views.digest(root/v['final_path'])==views.digest(root/v['approved_staging_path'])==v['sha256']
    assert views.resolve(root,promoted,count=2,back_corner=True)[0]=='corner_repeat'
    assert all(x['approval_status']=='needs_human_review' for x in core.load_manifest()['assets'] if x['id']!=a['id'])
    assert core.approve_assets([a['id']])==[]


def test_missing_alternate_preflight_prevents_any_partial_promotion(isolated):
    root,assets=isolated;old=(root/'metadata/manifest.json').read_bytes()
    (root/assets[2]['views']['corner_repeat']['normalized_path']).unlink()
    with pytest.raises(ValueError):core.approve_assets([a['id'] for a in assets])
    assert not (root/'assets').exists() and not (root/'staging/approved').exists()
    assert (root/'metadata/manifest.json').read_bytes()==old


def test_native_ingestion_and_normalization_are_idempotent_and_do_not_shrink(isolated):
    root,assets=isolated
    names=[v['normalized_path'] for a in assets for v in a['views'].values()]+['metadata/manifest.json']
    before={p:views.digest(root/p) for p in names}
    views.ingest(core,assets);core.normalize_pending()
    assert {p:views.digest(root/p) for p in names}==before


@pytest.mark.parametrize('bad_source',[False,True])
def test_actual_batch_ingestion_route_preflights_all_sources_before_any_copy(isolated,bad_source):
    root,assets=isolated
    for a in assets:
        for v in a['views'].values():(root/v['normalized_path']).unlink()
    core.save_manifest({'schema_version':'1.0','native_grid':32,'assets':[]})
    batch=root/'metadata/batch.json';batch.write_text(json.dumps({'assets':assets}))
    if bad_source:
        p=root/assets[-1]['views']['repeat']['source_native'];im=views.load(p);im.putpixel((6,6),(1,2,3,255));im.save(p)
        with pytest.raises(ValueError):core.ingest_batch(batch)
        assert core.load_manifest()['assets']==[]
        assert not list((root/'staging/pending/normalized').rglob('*.png'))
    else:
        core.ingest_batch(batch)
        assert len(core.load_manifest()['assets'])==4
        q=core.run_qa(asset_ids=b.IDS,write_reports=False)
        assert q['status_counts']=={'pass':4} and q['assets_checked']==4
        assert all(views.digest(root/v['normalized_path'])==v['sha256'] for a in assets for v in a['views'].values())


@pytest.mark.parametrize('name,w,d,delta',[('local',2,1,(0,0)),('original',4,2,(0,0)),('relocated',4,2,(32,32)),('additional_size',3,3,(0,0))])
def test_manifest_resolved_staged_enclosures_equal_saved_validation_and_all_corners(assets,name,w,d,delta):
    q,clean,structure=build.enclosure(assets,name,w,d,delta,save=False)
    assert q['pass']
    assert clean.tobytes()==views.load(ROOT/b.ART/f'{name}_clean.png').tobytes()
    assert structure.tobytes()==views.load(build.d4app.ART/f'enclosure_{name}_structure.png').tobytes()
    for corner in ('southwest','southeast'):
        assert q['checks'][corner]['checks']['overlap']['computed']=={'intentional_opaque':32,'unexpected_opaque':0,'unexpected_overlap':0,'missing_contact':0,'stacked_glass':0,'hidden_glass':0}
    for corner in ('northwest','northeast'):
        co=q['checks'][corner]['computed'];assert co['opaque_overlap_pixels']==48 and co['stacked_glass_pixels']==co['hidden_glass_pixels']==0


@pytest.fixture(scope='module')
def negative_controls(assets):
    actual={n:views.load(ROOT/v['normalized_path']) for n,v in assets[3]['views'].items()}
    return d4.negative_controls(actual)


@pytest.mark.parametrize('name',['repeat_displacement','broken_frame','opaque_glass','pane_hole','doubled_support','wrong_terminal','stacked_glass','anchor_1px','baseline_confusion','missing_contact','wrong_side_terminal'])
def test_staged_geometry_negative_controls_have_passing_valid_controls(negative_controls,name):
    q=negative_controls[name]
    assert q['valid_control_pass'] and q['proven']
    assert not q['validation']['checks'][q['intended_check']]['pass']


def test_one_pixel_metadata_anchor_and_missing_corner_return_are_detected(assets):
    a=copy.deepcopy(assets[2]);im,pp,cc,o=views.run(ROOT,a,2,back_corner=True)
    assert build.run_check(a,im,pp,cc,o,2,True)['pass']
    pp[1]['origin'][1]+=1
    assert not build.run_check(a,im,pp,cc,o,2,True)['pass']
    with pytest.raises(ValueError):
        a['views']['corner_repeat']['render_origin'][0]-=4;views.resolve(ROOT,a,count=2,back_corner=True)
    # Required return pixels checked directly from saved production layers.
    q=build.enclosure(assets,'original',4,2,save=False)[0];assert q['checks']['northeast']['pass']
    right=views.load(ROOT/b.ART/'original_d3_layer.png');back=views.load(ROOT/b.ART/'original_d1_layer.png');union=views.load(ROOT/b.ART/'original_structure.png')
    right.paste((0,0,0,0),(184,36,196,60))
    bad=build.d3.corner_check(back,right,union,192,64,True,[176,60],[184,36])
    assert not bad['checks']['upper_contact']['pass']


@pytest.mark.parametrize('defect',['none','old_record','old_status','delete_parent','fifth','alternate_as_asset','auto_approve','catalog_old_value','catalog_view_row'])
def test_bounded_inventory_semantics_reject_unauthorized_transition(assets,defect):
    before=json.loads((ROOT/b.AUDIT/'before_manifest.json').read_text());current=copy.deepcopy(core.load_manifest())
    br=transition.rows((ROOT/b.AUDIT/'before_catalog.csv').read_text());cr=transition.rows((ROOT/'metadata/catalog.csv').read_text())
    if defect=='old_record':current['assets'][0]['notes']='unauthorized'
    if defect=='old_status':current['assets'][0]['approval_status']='needs_human_review'
    if defect=='delete_parent':current['assets'].pop(0)
    if defect in ('fifth','alternate_as_asset'):
        extra=copy.deepcopy(assets[0]);extra['id']='unauthorized_01' if defect=='fifth' else assets[0]['id']+'_repeat';current['assets'].append(extra)
    if defect=='auto_approve':next(a for a in current['assets'] if a['id']==b.IDS[0])['approval_status']='approved'
    if defect=='catalog_old_value':cr[0]['notes']='changed'
    if defect=='catalog_view_row':cr.append(dict(cr[-1],id='view_01'))
    q=transition.semantics(before,current,br,cr,assets)
    assert q['pass'] is (defect=='none')


@pytest.mark.parametrize('action,ok',[('add',True),('modify',False),('delete',False),('lookalike',False)])
def test_named_output_allowance_never_exempts_existing_protected_file(tmp_path,action,ok):
    p=tmp_path/'views/existing.png';p.parent.mkdir();p.write_bytes(b'locked')
    snap=lambda:{f.relative_to(tmp_path).as_posix():views.digest(f) for f in tmp_path.rglob('*') if f.is_file()}
    before=snap()
    if action=='add':(p.parent/'authorized.png').write_bytes(b'new')
    if action=='modify':p.write_bytes(b'changed')
    if action=='delete':p.unlink()
    if action=='lookalike':(p.parent/'unauthorized.png').write_bytes(b'new')
    assert transition.protected_difference(before,snap(),{'views/authorized.png','views/existing.png'},semantic_pass=True)['pass'] is ok


def test_manifest_hash_exception_requires_semantic_proof():
    old={'metadata/manifest.json':'old'};new={'metadata/manifest.json':'new'}
    assert not transition.protected_difference(old,new,set(),semantic_pass=False)['pass']
    assert transition.protected_difference(old,new,set(),semantic_pass=True)['pass']
    assert not compare_snapshots({'counts':{'manifest':220},'sha256':old},{'counts':{'manifest':224},'sha256':new})['pass']


def test_live_transition_keeps_strict_unchanged_result_false_and_old_bytes_locked():
    q=transition.audit(ROOT)
    assert q['pass'] and not q['unchanged_state_pass'] and q['mode']=='authorized_batch13_production_transition'
    assert q['protected_file_count']==2436 and q['unchanged_protected_file_count']==2434
    assert q['observed_counts']=={'manifest':224,'approved':220,'needs_human_review':4}
    assert q['changed_or_missing_protected_files']==q['unauthorized_additions']==[]
    before=json.loads((ROOT/b.AUDIT/'production_before.json').read_text())
    assert not compare_snapshots(before,transition.snapshot(ROOT))['pass']


def test_review_zip_native_paths_resolve_to_exact_pending_files(assets):
    with zipfile.ZipFile(ROOT/b.BUNDLE) as z:
        package=json.loads(z.read(b.BATCH));assert package['status']=='needs_human_review'
        assert len(package['assets'])==4
        native={v['normalized_path'] for a in package['assets'] for v in a['views'].values()}
        assert len(native)==12
        for p in native:assert z.read(p)==(ROOT/p).read_bytes()
        assert not any('source_8x' in p or 'sources/package' in p for p in z.namelist())
        assert set(z.namelist())==native|{b.BATCH,b.QA,b.QA_MD,b.GUIDE,b.CONTACT,b.MONTAGE}


def test_batch12_additive_records_and_component_bytes_are_unchanged():
    before=json.loads((ROOT/b.AUDIT/'before_manifest.json').read_text());old={a['id']:a for a in before['assets'] if a.get('components')}
    current={a['id']:a for a in core.load_manifest()['assets']}
    assert old and all(current[k]==v and 'views' not in v for k,v in old.items())
    locked=json.loads((ROOT/b.AUDIT/'production_before.json').read_text())['sha256']
    for a in old.values():
        for c in a['components']:
            for key in ('normalized_path','final_path'):
                if c.get(key):assert views.digest(ROOT/c[key])==locked[c[key]]
