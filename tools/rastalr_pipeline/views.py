"""Opt-in exclusive architecture views; additive components retain their old path."""
from __future__ import annotations

import copy
import hashlib
import json
import shutil
from pathlib import Path, PurePosixPath
from PIL import Image
from .geometry import alpha_region, evidence


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def path(root, value):
    p=PurePosixPath(value)
    if not value or p.is_absolute() or '..' in p.parts or ':' in value or '\\' in value:
        raise ValueError('View paths must be package/repository-relative paths')
    return Path(root)/str(p)


def load(p):
    with Image.open(p) as im:return im.copy()


def contract_view(root, asset, name):
    c=json.loads(path(root,asset['geometry_contract']).read_text())
    if 'views' in c:return c['views'][name]
    e=c['expected'];a=c['derived']['anchor']
    if name not in ('main','repeat'):raise ValueError('Unknown back-partition view')
    return {'size':e['native_dimensions_px'],'cell_anchor':a['logical_cell_native'],'image_anchor':a['image_native'],
        'origin':a['render_origin_relative_to_cell_native'],
        'frame':list(e['frame_regions_native'].values()) if name=='main' else [[0,0,4,28],[4,0,32,5],[4,23,32,28]],
        'pane':[e['glass_region_native']] if name=='main' else [[4,5,32,23]]}


def validate_schema(asset):
    if asset.get('view_semantics')!='exclusive' or asset.get('components'):
        raise ValueError('Exclusive views cannot be additive components')
    kind=asset.get('view_selection_kind');required={'main','repeat'}
    if kind=='side':required|={'corner_main','corner_repeat'}
    elif kind!='horizontal':raise ValueError('Unknown exclusive view selection kind')
    if asset.get('default_view')!='main' or not isinstance(asset.get('views'),dict) or set(asset['views'])!=required:
        raise ValueError('Missing or invalid required exclusive views')
    if asset.get('qa_profile')!='architecture_glass' or asset.get('normalization_mode')!='architecture_grid_preserving':
        raise ValueError('Exclusive glass requires its opt-in QA and grid-preserving mode')
    if asset.get('source_scale')!=8 or asset.get('native_grid')!=32 or [asset.get('footprint_width_tiles'),asset.get('footprint_height_tiles')]!=[1,1]:
        raise ValueError('Invalid glass grid, source scale or logical footprint')
    if asset.get('repeat_stride_native')!=([0,32] if kind=='side' else [32,0]):raise ValueError('Invalid view stride')
    if asset.get('reuse_scope') not in ('hospital_only','everyday_world_common'):raise ValueError('Unknown reuse scope')
    seen=set()
    for name,v in asset['views'].items():
        if v.get('name')!=name:raise ValueError('View role/name mismatch')
        for key in ('dimensions','cell_anchor','image_anchor','render_origin'):
            if not isinstance(v.get(key),list) or len(v[key])!=2 or any(type(x) is not int for x in v[key]):raise ValueError('View requires integer '+key)
        if any(x<=0 for x in v['dimensions']):raise ValueError('Invalid view dimensions')
        if [a-b for a,b in zip(v['cell_anchor'],v['image_anchor'])]!=v['render_origin']:raise ValueError('View anchor mismatch')
        p=v.get('normalized_path','');path(Path('.'),p)
        if p in seen:raise ValueError('Alternative views require distinct paths')
        seen.add(p)
        for key in ('source_native','source_8x'):path(Path('.'),v[key])
    if asset['normalized_path']!=asset['views']['main']['normalized_path']:raise ValueError('Parent must alias its main view')


def select_name(asset, *, index, count, back_corner=False):
    validate_schema(asset)
    if type(count) is not int or count<1 or type(index) is not int or not 0<=index<count:raise ValueError('Invalid run context')
    if back_corner and asset['view_selection_kind']!='side':raise ValueError('Back-corner context requires a side orientation')
    return ('corner_' if back_corner and index==0 else '')+('main' if index==count-1 else 'repeat')


def resolve(root,asset,*,index=0,count=1,back_corner=False):
    name=select_name(asset,index=index,count=count,back_corner=back_corner);v=asset['views'][name]
    # Never fall back to source files, even for an otherwise valid view record.
    p=path(root,v.get('final_path') if asset.get('approval_status')=='approved' else v['normalized_path'])
    if not p.is_file():raise FileNotFoundError(f'Missing selected staged/final view: {p}')
    if digest(p)!=v['sha256']:raise ValueError(f'Corrupted selected view: {p}')
    im=load(p)
    if im.mode!='RGBA' or list(im.size)!=v['dimensions']:raise ValueError('Selected view mode/dimensions mismatch')
    return name,v,im


def run(root,asset,count,*,back_corner=False,cell=(0,0)):
    placements=[]
    for i in range(count):
        name,v,im=resolve(root,asset,index=i,count=count,back_corner=back_corner)
        logical=[cell[j]+i*asset['repeat_stride_native'][j] for j in range(2)]
        origin=[logical[j]+v['render_origin'][j] for j in range(2)]
        placements.append({'name':name,'cell':logical,'origin':origin,'image':im})
    left=min(p['origin'][0] for p in placements);top=min(p['origin'][1] for p in placements)
    right=max(p['origin'][0]+p['image'].width for p in placements);bottom=max(p['origin'][1]+p['image'].height for p in placements)
    image=Image.new('RGBA',(right-left,bottom-top));coverage=Image.new('I',image.size)
    for p in placements:
        im=p['image'];x,y=p['origin'][0]-left,p['origin'][1]-top;image.alpha_composite(im,(x,y))
        for yy in range(im.height):
            for xx in range(im.width):
                if 0<im.getpixel((xx,yy))[3]<255:coverage.putpixel((x+xx,y+yy),coverage.getpixel((x+xx,y+yy))+1)
    return image,[{k:v for k,v in p.items() if k!='image'} for p in placements],coverage,[left,top]


def check_view(root,asset,name,*,native_override=None):
    v=asset['views'][name];checks={}
    p=Path(native_override) if native_override else path(root,v.get('final_path') if asset.get('approval_status')=='approved' else v['normalized_path'])
    if not p.is_file():return {'status':'fail','issues':[{'code':'missing_view','severity':'error','message':str(p)}],'checks':{'exists':evidence(True,False,'Check actual view file')}}
    im=load(p);ref=load(path(root,v['source_native']));export=load(path(root,v['source_8x']));s=contract_view(root,asset,name)
    checks['mode']=evidence('RGBA',im.mode,'Read saved mode before conversion')
    checks['size']=evidence(s['size'],list(im.size),'Read saved PNG dimensions')
    checks['sha256']=evidence(v['sha256'],digest(p),'Exact native bytes against validated source hash')
    checks['source_identity']=evidence(digest(path(root,v['source_native'])),digest(p),'Byte-identical validated native copy')
    checks['contract_hash']=evidence(asset['geometry_contract_sha256'],digest(path(root,asset['geometry_contract'])),'Exact historical contract version')
    for key,ck in [('dimensions','size'),('cell_anchor','cell_anchor'),('image_anchor','image_anchor'),('render_origin','origin')]:checks[key]=evidence(s[ck],v[key],'Compare numeric metadata with committed geometry')
    checks['alpha_regions']=evidence({'frame':s['frame'],'pane':s['pane'],'pane_values':([150,210] if asset['family_member']=='D1' else [150]),'exterior':0},v['alpha_regions'],'Compare declared regions to contract')
    checks['source_dimensions']=evidence([x*8 for x in s['size']],list(export.size),'Read original8x export dimensions')
    checks['source_export_hash']=evidence(v['source_8x_sha256'],digest(path(root,v['source_8x'])),'Read working export bytes')
    checks['source_mode']=evidence('RGBA',export.mode,'Read original export mode')
    summary={}
    if im.mode=='RGBA' and list(im.size)==s['size'] and ref.size==im.size and export.mode=='RGBA' and export.size==(im.width*8,im.height*8):
        hist=im.getchannel('A').histogram();summary={'fully_transparent_pixels':hist[0],'partially_transparent_pixels':sum(hist[1:255]),'opaque_pixels':hist[255],'has_transparency':sum(hist[:255])>0}
        checks['alpha_map']=evidence(0,sum(a[3]!=b[3] for a,b in zip(im.get_flattened_data(),ref.get_flattened_data())),'Compare every native alpha sample with validated source')
        checks['roundtrip']=evidence(im.tobytes(),export.resize(im.size,Image.Resampling.NEAREST).tobytes(),'Native RGBA roundtrip')
        # Store counts, not large binary values, in the evidence record.
        checks['roundtrip']=evidence(0,0 if checks['roundtrip']['pass'] else 1,'Exact native RGBA nearest-neighbor roundtrip')
        checks['source_blocks']=evidence(0,sum(export.getpixel((x,y))!=im.getpixel((x//8,y//8)) for y in range(export.height) for x in range(export.width)),'Inspect every8x8 source block')
        covered=set()
        for role in ('frame','pane'):
            for i,r in enumerate(s[role]):
                low,high=(255,255) if role=='frame' else (150,210 if asset['family_member']=='D1' else 150)
                checks[f'{role}_{i}']=alpha_region(im,r,minimum=low,maximum=high)
                covered.update((x,y) for y in range(r[1],r[3]) for x in range(r[0],r[2]))
        checks['exterior']=evidence(0,sum(im.getpixel((x,y))[3]!=0 for y in range(im.height) for x in range(im.width) if (x,y) not in covered),'Undeclared exterior alpha must be zero')
    issues=[{'code':k,'severity':'error','message':q['method']} for k,q in checks.items() if not q['pass']]
    return {'status':'fail' if issues else 'pass','issues':issues,'checks':checks,'alpha':summary}


def qa_asset(root,asset,*,source_control=False):
    try:validate_schema(asset)
    except (ValueError,KeyError) as e:return {'status':'fail','issues':[{'code':'view_schema','severity':'error','message':str(e)}],'views':{}}
    reports={n:check_view(root,asset,n,native_override=path(root,v['source_native']) if source_control else None) for n,v in asset['views'].items()}
    relationships={}
    if all(q['status']=='pass' for q in reports.values()):
        images={n:load(path(root,v['source_native' if source_control else ('final_path' if asset.get('approval_status')=='approved' else 'normalized_path')])) for n,v in asset['views'].items()}
        main,repeat=images['main'],images['repeat'];outside=extension=0
        for y in range(main.height):
            for x in range(main.width):
                allowed=(2<=x<10 and 28<=y<32) if asset['view_selection_kind']=='side' else (28<=x<32 and (True if asset['family_member']=='D1' else 4<=y<10))
                if allowed:extension+=repeat.getpixel((x,y))!=main.getpixel((x,27) if asset['view_selection_kind']=='side' else (27,y))
                else:outside+=repeat.getpixel((x,y))!=main.getpixel((x,y))
        relationships['outside']=evidence(0,outside,'Actual repeat RGBA outside permitted continuation')
        relationships['extension']=evidence(0,extension,'Actual repeat continuation against main interior row/column')
        if asset['view_selection_kind']=='side':
            for n in ('main','repeat'):relationships['corner_body_'+n]=evidence(True,images[n].tobytes()==images['corner_'+n].crop((0,24,12,56)).tobytes(),'Compare actual corner body RGBA with main/repeat')
            relationships['upper_return']=evidence(True,images['corner_main'].crop((0,0,12,24)).tobytes()==images['corner_repeat'].crop((0,0,12,24)).tobytes(),'Compare alternate upper returns')
    failed=any(q['status']=='fail' for q in reports.values()) or any(not q['pass'] for q in relationships.values())
    return {'status':'fail' if failed else 'pass','issues':[{'code':'glass_view_qa','severity':'error','message':'A required view or relationship failed'}] if failed else [],'views':reports,'relationships':relationships}


def ingest(core,items):
    """Preflight the entire exclusive batch, then copy already-native bytes once."""
    manifest=core.load_manifest();by_id={a['id']:a for a in manifest['assets']};copies=[]
    for a in items:
        validate_schema(a)
        if a['id'] in by_id and by_id[a['id']]!=a:raise ValueError('Existing asset conflicts with exact native-copy staging: '+a['id'])
        if qa_asset(core.ROOT,a,source_control=True)['status']!='pass':raise ValueError('Validated source/contract QA failed')
        for v in a['views'].values():
            target=path(core.ROOT,v['normalized_path']);source=path(core.ROOT,v['source_native'])
            if target.exists() and digest(target)!=digest(source):raise ValueError('Existing staged view differs; refusing repair')
            if a['id'] in by_id and not target.is_file():raise FileNotFoundError('Previously staged view missing; refusing silent repair')
            copies.append((source,target))
    for source,target in copies:
        if not target.exists():target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    for a in items:
        if qa_asset(core.ROOT,a)['status']!='pass':raise ValueError('Actual staged glass QA failed')
        if a['id'] not in by_id:manifest['assets'].append(copy.deepcopy(a))
    if any(a['id'] not in by_id for a in items):manifest['assets'].sort(key=lambda a:a['id']);core.save_manifest(manifest)
    return items


def promotion_plan(root,asset):
    if qa_asset(root,asset)['status']!='pass':raise ValueError('Cannot promote failing/missing exclusive views')
    plan=[]
    for name,v in asset['views'].items():
        sub=asset['filename'] if name=='main' else f"views/{asset['id']}/{Path(v['normalized_path']).name}"
        src=path(root,v['normalized_path']);stage=Path(root)/'staging/approved'/sub;final=Path(root)/'assets'/asset['category']/sub
        if stage.exists() or final.exists():raise FileExistsError('Refusing an existing promotion destination')
        plan.append((name,src,stage,final))
    return plan


def promote(root,asset,plan):
    for name,src,stage,final in plan:
        stage.parent.mkdir(parents=True,exist_ok=True);final.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,stage);shutil.copyfile(src,final)
        v=asset['views'][name];v['approved_staging_path']=stage.relative_to(root).as_posix();v['final_path']=final.relative_to(root).as_posix()
    asset['approved_staging_path']=asset['views']['main']['approved_staging_path'];asset['final_path']=asset['views']['main']['final_path'];asset['approval_status']='approved'
