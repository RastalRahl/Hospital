"""Fixed, reviewed Batch 13 ingestion declaration; no artwork creation."""
from pathlib import Path
import json
from . import views

BASELINE='a1ac6cb6f1bc9522a269af91c6c992bbc4a34324'
IDS=['hospital_glass_partition_back_01','hospital_glass_partition_side_left_01','hospital_glass_partition_side_right_01','hospital_glass_partition_front_cutaway_01']
BATCH='metadata/production_batch_13_architecture_glass_partitions.json'
QA='metadata/architecture_glass_partitions_batch_13_qa.json'
QA_MD='metadata/architecture_glass_partitions_batch_13_qa.md'
AUDIT='metadata/batch_13_transition'
ART='previews/architecture/batch_13_glass_partitions'
CONTACT='previews/contact_sheets/production_batch_13_architecture_glass_partitions_review.png'
MONTAGE='previews/architecture/production_batch_13_architecture_glass_partitions_qa_montage.png'
BUNDLE='release/production_batch_13_architecture_glass_partitions_review_bundle.zip'
GUIDE='docs/architecture_glass_partitions_batch_13_usage.md'


def blueprints(root):
    import validate_architecture_d1 as d1
    import validate_architecture_d2_appearance as d2
    import validate_architecture_d3_appearance as d3
    import validate_architecture_d4_appearance as d4
    apps=[d1,d2,d3,d4];out=[]
    for index,(asset_id,app) in enumerate(zip(IDS,apps),1):
        relative=lambda p:p.relative_to(d1.ROOT).as_posix()
        report=relative(app.OUT/('d1_validation_report.json' if index==1 else f'd{index}_appearance_validation_report.json'))
        r=json.loads((root/report).read_text())
        if r['status']!='PASS':raise ValueError('Required committed validation is not PASS: '+report)
        # Read accompanying human-readable evidence as well; never rewrite it.
        (root/Path(report).with_suffix('.md')).read_text()
        contract=relative(d1.CONTRACT_PATH if index==1 else app.CONTRACT)
        names=('main','repeat') if index in (1,4) else ('main','repeat','corner_main','corner_repeat')
        filename=asset_id+'.png';main_path='staging/pending/normalized/'+filename
        a={'id':asset_id,'filename':filename,'category':'architecture','subcategory':'glass_partition','asset_type':asset_id[:-3],
            'variant':1,'orientation':['back','side_left','side_right','front_cutaway'][index-1],'state':'clean','reuse_scope':'hospital_only',
            'native_grid':32,'source_scale':8,'footprint_width_tiles':1,'footprint_height_tiles':1,'anchor':'architecture_grid',
            'tags':['architecture','glass','fixed_partition','modular','grid_32',f'D{index}','batch_13'],
            'normalization_mode':'architecture_grid_preserving','ingestion_mode':'validated_native_copy','already_native':True,
            'qa_profile':'architecture_glass','view_semantics':'exclusive','default_view':'main','view_selection_kind':'horizontal' if index in (1,4) else 'side',
            'repeat_stride_native':[32,0] if index in (1,4) else [0,32],'family_member':f'D{index}',
            'approval_status':'needs_human_review','qa_status':'pass','qa_issues':[], 'raw_qa_status':'pass','raw_qa_issues':[],
            'staging_path':main_path,'normalized_path':main_path,'final_path':'','perceptual_hash':'',
            'geometry_contract':contract,'geometry_contract_sha256':views.digest(root/contract),'validation_reference':report,
            'architecture_structural_role':['north_back_glass','west_side_glass_cutaway','east_side_glass_cutaway','south_front_glass_cutaway'][index-1],
            'architecture_provenance':{'validation_commit':BASELINE,'contract':contract,'report':report,'authorization':'Batch13 staging only; no human production approval'},
            'notes':'Validated native bytes copied unchanged; exclusive implementation views belong to one logical asset. Awaiting staged-file human review.',
            'views':{}}
        for name in names:
            native=relative(app.PACKAGE/'candidate'/(d1.VIEW_FILES[name] if index==1 else f'{app.STEM}{name}_native.png'))
            export=relative(app.PACKAGE/'candidate'/(d1.VIEW_FILES[name+'_8x'] if index==1 else f'{app.STEM}{name}_source_8x.png'))
            s=views.contract_view(root,a,name)
            p=main_path if name=='main' else f'staging/pending/normalized/views/{asset_id}/{name}_01.png'
            a['views'][name]={'name':name,'role':name,'normalized_path':p,'final_path':'','dimensions':s['size'],
                'cell_anchor':s['cell_anchor'],'image_anchor':s['image_anchor'],'render_origin':s['origin'],
                'normalization_mode':'architecture_grid_preserving','source_scale':8,'native_scale':1,
                'source_native':native,'source_8x':export,'source_8x_dimensions':[x*8 for x in s['size']],
                'sha256':views.digest(root/native),'source_8x_sha256':views.digest(root/export),
                'alpha_regions':{'frame':s['frame'],'pane':s['pane'],'pane_values':[150,210] if index==1 else [150],'exterior':0},
                'validation_reference':report,'qa_reference':QA,'qa_status':'pass'}
        v=a['views']['main'];a.update(source=v['source_native'],source_sha256=v['sha256'],working_source=v['source_8x'],
            source_dimensions={'width':v['dimensions'][0],'height':v['dimensions'][1]},canvas_width=v['dimensions'][0],canvas_height=v['dimensions'][1],
            expected_native_dimensions=v['dimensions'],normalized_sha256=v['sha256'],crop=None,
            normalization_exception={'kind':'validated_native_copy','trim_applied':False,'padding_applied':0,'source_scale_applied':1,'reason':'Already-native validated PNG; source_scale8 records working export provenance only'})
        views.validate_schema(a);out.append(a)
    return out


def declaration(root):
    return {'name':'Production Batch13: Architecture Glass Partitions','status':'needs_human_review','view_semantics':'exclusive',
            'logical_asset_count':4,'native_view_count':12,'validation_baseline':BASELINE,'assets':blueprints(root)}


def artifact_names():
    names=[]
    for member in ('D1','D2','D3','D4'):
        for corner in ((False,True) if member in ('D2','D3') else (False,)):
            for count in (1,2,4):
                stem=f'{member.lower()}_{"corner" if corner else "straight"}_{count}'
                names += [f'{stem}_{s}.png' for s in ('native','object_layer','light_background','dark_background','colored_background','object_background','light_composite','dark_composite','colored_composite','object_composite')]
    for name in ('local','original','relocated','additional_size'):
        names += [f'{name}_{s}.png' for s in ('structure','background','object_layer','clean','object_composite','d1_layer','d2_layer','d3_layer','d4_layer','ground')]
        names += [f'{name}_{s}.png' for s in ('northwest','northeast','southwest','southeast')]
        names += [f'{name}_{s}_required_ground.png' for s in ('northwest','northeast','southwest','southeast')]
    names += ['approved_wall_context.png']
    return names


def allowed_additions(root):
    result={v['normalized_path'] for a in blueprints(root) for v in a['views'].values()}
    result.update({BATCH,QA,QA_MD,GUIDE,CONTACT,MONTAGE,BUNDLE,'metadata/.gitattributes','docs/.gitattributes'})
    result.update(f'{ART}/{n}' for n in artifact_names())
    result.update(f'{AUDIT}/{n}' for n in ('.gitattributes','production_before.json','before_manifest.json','before_catalog.csv','staging_request.txt','baseline_tests.json','test_results.json','test_results.txt','preservation.json','idempotence.json','source_staged_map.json','output_hashes.json'))
    return result
