"""Reference-only D2 material edit. Original geometry/alpha and D1 remain unchanged.

Run from any directory: python tools/build_d2_appearance.py
Dependencies: Pillow, numpy. Production files are never written.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
NAMES=('main','repeat','corner_main','corner_repeat')
PREFIX='rastalr_D2_glass_partition_side_left_locked_v1_'
DARK=(24,35,49); SHADE=(39,55,70); EDGE=(51,73,91)
MID=(86,112,131); LIGHT=(104,134,154); CAP=(137,164,180)
GLASS=(146,182,195); GLASS_SHADE=(137,173,187); GLASS_LIGHT=(153,189,201)

def load(path:Path)->Image.Image:
    with Image.open(path) as im:
        im.load()
        if im.mode!='RGBA': raise ValueError(f'Expected RGBA: {path}')
        return im.copy()

def sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def json_out(path:Path,data:dict)->None:
    path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')

def put_rgb(im:Image.Image,x:int,y:int,rgb:tuple)->None:
    im.putpixel((x,y),(*rgb,im.getpixel((x,y))[3]))

def apply_materials(originals:dict[str,Image.Image])->dict[str,Image.Image]:
    main=originals['main'].copy()
    for y in range(32):
        for x in range(12):
            if x==0 or x==11: color=DARK
            elif x==1: color=LIGHT
            elif x==10: color=EDGE
            elif y<4: color=(CAP,LIGHT,MID,DARK)[y]
            elif y>=28: color=(DARK,EDGE,MID,DARK)[y-28]
            else: color=GLASS_SHADE if x in (2,9) else GLASS
            put_rgb(main,x,y,color)
    # A small RGB-only reflection; the scaffold's alpha remains exactly 150.
    for x,y in ((4,8),(4,9),(5,10),(5,11),(6,12)):
        put_rgb(main,x,y,GLASS_LIGHT)
    repeat=main.copy()
    for y in range(28,32):
        for x in range(2,10): repeat.putpixel((x,y),main.getpixel((x,27)))
    corner=originals['corner_main'].copy()
    for y in range(24):
        for x in range(12):
            alpha=corner.getpixel((x,y))[3]
            if alpha==0: continue
            if y<4:
                color=DARK if x==0 else (CAP,LIGHT,MID,DARK)[y]
            elif x==0: color=DARK
            elif x==1: color=LIGHT
            else: color=GLASS_LIGHT if x==2 else GLASS
            put_rgb(corner,x,y,color)
    # The body is the exact straight view, not a second independently drawn asset.
    corner.paste(main,(0,24))
    corner_repeat=corner.copy();corner_repeat.paste(repeat,(0,24))
    return {'main':main,'repeat':repeat,'corner_main':corner,'corner_repeat':corner_repeat}

def assemble(views:dict,n:int,corner:bool=False,naive:bool=False):
    offset=24 if corner else 0
    out=Image.new('RGBA',(12,32*n+offset)); layers=np.zeros((out.height,12),np.uint8)
    origins=[]
    for i in range(n):
        kind=('corner_' if corner and i==0 else '')+('main' if naive or i==n-1 else 'repeat')
        im=views[kind]; oy=0 if corner and i==0 else offset+i*32
        out.alpha_composite(im,(0,oy));origins.append([0,oy])
        a=np.array(im)[:,:,3];layers[oy:oy+im.height]+=(a>0)&(a<255)
    return out,origins,layers

def run_check(im:Image.Image,n:int,origins:list,layers:np.ndarray)->dict:
    a=np.array(im)[:,:,3];expected=np.full((32*n,12),150,np.uint8)
    expected[:,:2]=255;expected[:,10:]=255
    for i in range(n):expected[i*32:i*32+4]=255
    expected[-4:]=255
    okay=(im.size==(12,32*n)) and np.array_equal(a,expected)
    spans=[];start=None
    for y in range(im.height+1):
        opaque=y<im.height and a[y,6]==255
        if opaque and start is None:start=y
        if not opaque and start is not None:spans.append([start,y]);start=None
    expected_spans=[[i*32,i*32+4] for i in range(n)]+[[n*32-4,n*32]]
    placements=origins==[[0,i*32] for i in range(n)]
    layer_errors=int(np.count_nonzero(layers[a<255]!=1))
    return {'pass':bool(okay and spans==expected_spans and placements and layer_errors==0),
            'dimensions':list(im.size),'support_spans_observed':spans,'actual_origins':origins,
            'alpha_violations':int(np.count_nonzero(a!=expected)), 'pane_layer_violations':layer_errors}

def transmission(im:Image.Image)->dict:
    a=np.array(im)[:,:,3];pane=(a>0)&(a<255);frame=a==255
    bg1=Image.new('RGBA',im.size,(240,237,223,255));bg2=Image.new('RGBA',im.size,(30,40,54,255))
    s1=np.array(Image.alpha_composite(bg1,im));s2=np.array(Image.alpha_composite(bg2,im))
    changed=np.any(s1[:,:,:3]!=s2[:,:,:3],axis=2)
    f=np.array(im).astype(np.int32)
    expected=((f[:,:,:3]*f[:,:,3,None]+np.array([240,237,223])*(255-f[:,:,3,None])+127)//255)
    math_errors=int(np.count_nonzero(np.any(s1[:,:,:3]!=expected,axis=2)))
    return {'pass':bool(np.all(changed[pane]) and not np.any(changed[frame]) and math_errors==0),
            'pane_pixels':int(pane.sum()),'responsive_pane_pixels':int(changed[pane].sum()),
            'responsive_opaque_frame_pixels':int(changed[frame].sum()),'source_over_pixel_errors':math_errors}

def d1run()->Image.Image:
    main=load(ROOT/'sources/rastalr_D1_glass_partition_back_locked_v1_native.png')
    repeat=load(ROOT/'sources/rastalr_D1_glass_partition_back_locked_v1_repeat_native.png')
    out=Image.new('RGBA',(64,28));out.alpha_composite(repeat,(0,0));out.alpha_composite(main,(32,0))
    return out

def corner_scene(views:dict,*,shift:tuple=(0,0)):
    size=(144,140)
    side=Image.new('RGBA',size);front=Image.new('RGBA',size)
    run,_,_=assemble(views,2,corner=True)
    side.alpha_composite(run,(60+shift[0],36+shift[1]));front.alpha_composite(d1run(),(64,36))
    bg=Image.new('RGBA',size,(225,226,213,255))
    scene=Image.alpha_composite(Image.alpha_composite(bg,side),front)
    aa=np.array(side)[:,:,3];bb=np.array(front)[:,:,3]
    overlap=(aa>0)&(bb>0);allowed=np.zeros_like(overlap)
    allowed[36:40,64:68]=True;allowed[60:64,64:72]=True
    opaque=(aa==255)&(bb==255)
    hidden=((aa>0)&(aa<255)&(bb>0))|((bb>0)&(bb<255)&(aa>0))
    front_alone=np.array(Image.alpha_composite(bg,front))
    changed=np.any(np.array(scene)!=front_alone,axis=2)
    checks={'opaque_overlap_pixels':int(opaque.sum()),
            'overlap_ownership_mismatches':int(np.count_nonzero(overlap!=allowed)),
            'hidden_or_stacked_glass_pixels':int(hidden.sum()),
            'D1_composited_pixel_mismatches':int(changed[bb>0].sum())}
    checks['pass']=checks['opaque_overlap_pixels']==48 and all(checks[k]==0 for k in ('overlap_ownership_mismatches','hidden_or_stacked_glass_pixels','D1_composited_pixel_mismatches'))
    return scene,checks,side,front

def room_context(views:dict,relocate:int=0):
    wall=load(ROOT/'sources/hospital_wall_back_straight_01.png');floor=load(ROOT/'sources/hospital_floor_plain_01.png')
    bg=Image.new('RGBA',(192+relocate,176+relocate),(225,226,213,255))
    for y in range(48+relocate,176+relocate,32):
        for x in range(16+relocate,176+relocate,32):bg.alpha_composite(floor,(x,y))
    for x in range(16+relocate,176+relocate,32):bg.alpha_composite(wall,(x,relocate))
    side=Image.new('RGBA',bg.size);front=Image.new('RGBA',bg.size)
    run,_,_=assemble(views,2,corner=True)
    side.alpha_composite(run,(60+relocate,68+relocate));front.alpha_composite(d1run(),(64+relocate,68+relocate))
    scene=Image.alpha_composite(Image.alpha_composite(bg,side),front)
    return scene,bg,side,front

def font(size:int):
    path=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    return ImageFont.truetype(str(path),size) if path.exists() else ImageFont.load_default(size=size)

def preview(views:dict,originals:dict):
    board=Image.new('RGB',(1320,1120),(24,35,49));draw=ImageDraw.Draw(board)
    def text(x,y,s,size=18,fill=(222,232,237)):draw.text((x,y),s,font=font(size),fill=fill)
    def put(im,x,y,k):
        enlarged=im.resize((im.width*k,im.height*k),Image.Resampling.NEAREST)
        if enlarged.mode=='RGBA':
            tile=Image.new('RGBA',enlarged.size,(33,47,62,255));tile.alpha_composite(enlarged);board.paste(tile.convert('RGB'),(x,y))
        else:board.paste(enlarged,(x,y))
    text(28,20,'D2 | LEFT GLASS PARTITION',27)
    text(28,60,'Locked appearance candidate | geometry v2 | RGB-only edit | reference-only',16)
    text(28,104,'Scaffold corner',19);text(384,104,'Appearance corner',19);text(918,104,'Four implementation views',19)
    before,_,_,_=corner_scene(originals);after,_,_,_=corner_scene(views)
    # Crop both scenes identically for display only; standalone asset files are not cropped.
    put(before.crop((52,28,132,128)),28,138,4);put(after.crop((52,28,132,128)),384,138,4)
    for name,x,y in [('main',930,155),('repeat',1090,155),('corner_main',930,340),('corner_repeat',1090,340)]:
        put(views[name],x,y,3);text(x+48,y+4,name.replace('_',' '),13)
    text(28,554,'Approved-wall / floor context',19)
    context,_,_,_=room_context(views);put(context,28,590,2)
    text(456,554,'1 / 2 / 4 cells | identical 32 px depth stride',17)
    for i,n in enumerate((1,2,4)):
        run,_,_=assemble(views,n);put(run,468+i*104,596,3);text(466+i*104,1000,f'{n} cell'+('s' if n>1 else ''),14)
    text(860,554,'Separate backgrounds through the same glass',17)
    for i,(label,color) in enumerate([('Light',(240,237,223,255)),('Dark',(30,40,54,255)),('Object',(61,127,169,255))]):
        run,_,_=assemble(views,2,corner=True)
        bg=Image.new('RGBA',run.size,color)
        if label=='Object':bg.paste((245,183,34,255),(3,36,9,48))
        scene=Image.alpha_composite(bg,run);put(scene,880+i*136,596,3);text(878+i*136,886,label,15)
        bg.save(ROOT/f'previews/transmission_{label.lower()}_background.png')
        scene.save(ROOT/f'previews/transmission_{label.lower()}_composite.png')
    text(28,1060,'Straight: 12x32 | Corner: 12x56 | 4 exclusive views = 1 future logical asset',17)
    text(28,1090,'Intentional cutaway, not a full-height side wall. D1 unchanged. No production approval.',15)
    board.save(ROOT/'previews/d2_locked_appearance_review.png')

def main():
    sources={p.name:sha(p) for p in (ROOT/'sources').iterdir() if p.is_file()}
    originals={n:load(ROOT/f'sources/d2_{n}_native.png') for n in NAMES}
    views=apply_materials(originals);checks={'status':'LOCAL_CANDIDATE_CHECKS_ONLY','views':{},'runs':{},'corner_runs':{}}
    for name,im in views.items():
        npth=ROOT/f'candidate/{PREFIX}{name}_native.png';spth=ROOT/f'candidate/{PREFIX}{name}_source_8x.png'
        im.save(npth);im.resize((im.width*8,im.height*8),Image.Resampling.NEAREST).save(spth)
        re=load(npth);source=load(spth);a=np.array(re);b=np.array(originals[name]);expanded=np.repeat(np.repeat(a,8,axis=0),8,axis=1)
        hist={str(v):int(c) for v,c in zip(*np.unique(a[:,:,3],return_counts=True))}
        q={'native_dimensions':list(re.size),'source_dimensions':list(source.size),'mode':re.mode,
           'alpha_changed_pixels':int(np.count_nonzero(a[:,:,3]!=b[:,:,3])),
           'rgb_changed_pixels':int(np.count_nonzero(np.any(a[:,:,:3]!=b[:,:,:3],axis=2))),
           'transparent_rgba_changed_pixels':int(np.count_nonzero(np.any(a!=b,axis=2)&(b[:,:,3]==0))),
           'source_block_errors':int(np.count_nonzero(np.any(np.array(source)!=expanded,axis=2))),
           'alpha_histogram':hist,'transmission':transmission(re)}
        q['pass']=all(q[k]==0 for k in ('alpha_changed_pixels','transparent_rgba_changed_pixels','source_block_errors')) and q['transmission']['pass']
        assert q['pass'],(name,q);checks['views'][name]=q;views[name]=re
    # Check image relationships from reloaded files, not the material authoring operations.
    m=np.array(views['main']);r=np.array(views['repeat']);expected=m.copy();expected[28:32,2:10]=m[27:28,2:10]
    assert np.array_equal(r,expected)
    for name in ('main','repeat'):assert views['corner_'+name].crop((0,24,12,56)).tobytes()==views[name].tobytes()
    checks['exclusive_view_relationships']='PASS: corner body identical to straight; repeat extends only terminal support region'
    for n in (1,2,4):
        run,origins,layers=assemble(views,n);run.save(ROOT/f'previews/d2_run_{n}_native.png')
        q=run_check(load(ROOT/f'previews/d2_run_{n}_native.png'),n,origins,layers);q['transmission']=transmission(run);assert q['pass'] and q['transmission']['pass'];checks['runs'][str(n)]=q
        cr,co,cl=assemble(views,n,True);cr.save(ROOT/f'previews/d2_corner_run_{n}_native.png')
        body_match=cr.crop((0,24,12,cr.height)).tobytes()==run.tobytes()
        q={'body_matches_straight':body_match,'max_translucent_layers':int(cl.max()),'origins':co,'transmission':transmission(cr)}
        q['pass']=body_match and q['max_translucent_layers']==1 and q['transmission']['pass'];assert q['pass'];checks['corner_runs'][str(n)]=q
    before,_,_,_=corner_scene(originals)
    supplied_before=load(ROOT/'sources/d1_d2_corner_clean_scaffold_v2.png')
    assert before.tobytes()==supplied_before.tobytes(),'Local assembler must reproduce the exact committed clean corner'
    checks['scaffold_corner_reconstructed_byte_exact']=True
    scene,q,side,front=corner_scene(views);assert q['pass'];checks['corner']=q
    for name,im in [('d2_corner_appearance_native',scene),('d2_corner_side_layer',side),('d2_corner_unchanged_D1_layer',front)]:im.save(ROOT/f'previews/{name}.png')
    scene.crop((52,28,132,128)).resize((480,600),Image.Resampling.NEAREST).save(ROOT/'previews/d2_corner_appearance_detail.png')
    for move in (0,32):
        sc,bg,sl,fl=room_context(views,move)
        for label,im in [('scene',sc),('background',bg),('D2_layer',sl),('D1_layer',fl)]:im.save(ROOT/f'previews/context_{move}_{label}.png')
    sc0=room_context(views)[0];sc32=room_context(views,32)[0]
    checks['context_relocation_pixel_match']=sc32.crop((32,32,32+sc0.width,32+sc0.height)).tobytes()==sc0.tobytes()
    assert checks['context_relocation_pixel_match']
    # Actual destructive examples live only in memory; sources are never edited.
    negatives={}
    for label,point,alpha in [('opaque_glass',(5,10),255),('pane_hole',(5,10),0),('broken_frame',(0,10),0)]:
        bad=views['main'].copy();px=bad.getpixel(point);bad.putpixel(point,(*px[:3],alpha))
        negatives[label]=bad.getchannel('A').tobytes()!=originals['main'].getchannel('A').tobytes()
    bad,bo,bl=assemble(views,2,naive=True);negatives['doubled_support']=not run_check(bad,2,bo,bl)['pass']
    good,go,gl=assemble(views,2);bad=good.copy();bad.alpha_composite(views['main'].crop((2,4,10,28)),(2,4))
    negatives['stacked_glass']=not run_check(bad,2,go,gl)['pass']
    displaced=list(map(list,go));displaced[1][1]+=1
    negatives['repeat_displacement_1px']=not run_check(good,2,displaced,gl)['pass']
    bad={**views,'corner_repeat':views['corner_repeat'].copy()};bad['corner_repeat'].paste((0,0,0,0),(0,0,12,24))
    negatives['missing_return']=not corner_scene(bad)[1]['pass']
    negatives['corner_displacement_1px']=not corner_scene(views,shift=(1,0))[1]['pass']
    assert all(negatives.values());checks['negative_controls_rejected']=negatives
    preview(views,originals)
    checks['local_source_hashes_unchanged']=sources=={p.name:sha(p) for p in (ROOT/'sources').iterdir() if p.is_file()}
    assert checks['local_source_hashes_unchanged']
    checks['repository_test_suite']='NOT RUN HERE. Codex independently validates and runs the repository suite.'
    checks['human_production_approval']=False
    checks['pass']=True
    json_out(ROOT/'reports/d2_local_checks.json',checks)
    spec={'id':'hospital_glass_partition_side_left_01','candidate_version':'locked_appearance_v1','status':'REFERENCE_ONLY_APPEARANCE_CANDIDATE',
          'authoritative_geometry_commit':'4f078aec4aa876e5ac3a806b0ef6a5662f42c8cb',
          'authoritative_geometry_contract':'references/architecture/master_validation_D2_v2/d2_geometry_alpha_contract_proposed.json',
          'review_scope':'ChatGPT judged v2 suitable for this controlled appearance trial. No user or production approval is inferred; historical proposed contract remains untouched.',
          'material_policy':'RGB-only edits within source nonzero-alpha regions; all source alpha and zero-alpha RGBA values preserved.',
          'coordinate_convention':'[left, top, right, bottom)','source_scale':8,'normalization':'architecture_grid_preserving','logical_asset_count':1,
          'interpretation':'Low glass partition rendered as a shallow side cutaway, with a glazed north return. Not a full-height glazed side wall.',
          'views':{n:{'native_file':f'candidate/{PREFIX}{n}_native.png','source_8x_file':f'candidate/{PREFIX}{n}_source_8x.png',
                      'source_reference_file':f'sources/d2_{n}_native.png','native_size':list(views[n].size),
                      'render_origin_relative_to_cell':[12,-24] if n.startswith('corner') else [12,0],
                      'image_anchor':[4,40] if n.startswith('corner') else [4,16],'logical_cell_anchor':[16,16]} for n in NAMES},
          'assembly':{'depth_stride':[0,32],'mutually_exclusive_views':True,
                      'selection':'Use corner_main/corner_repeat only for the first D2 cell adjoining D1 at the reviewed NW corner. Main closes a run; repeat continues it. Never layer alternatives.',
                      'corner_body_offset':[0,24],'repeat_edit_region_main':[2,28,10,32],
                      'layer_order':['separate background','D2','unchanged D1'],'intentional_opaque_overlap_pixels':48,'glass_overlap_pixels':0},
          'limits':['Only the existing local NW corner, not every junction, was reviewed.','No production asset, catalog row, or repository file was created.','Independent Codex validation remains required.']}
    json_out(ROOT/'reports/d2_candidate_spec.json',spec)
    lines=['# D2 locked appearance: local checks','', 'Reference-only candidate. No repository-wide test run or production approval.','',
           '| View | Native | Alpha changed | RGB changed | Local result |','| --- | --- | ---: | ---: | --- |']
    for n,q in checks['views'].items():lines.append(f"| {n} | {q['native_dimensions']} | {q['alpha_changed_pixels']} | {q['rgb_changed_pixels']} | PASS |")
    lines+=['','All four alpha maps and all transparent RGBA source pixels are unchanged. Exact 8x blocks verified after reloading.','',
            'One/two/four-cell straight and corner runs pass local repeat/transmission checks. The local assembler reproduces the committed scaffold corner pixel-for-pixel before appearance edits.',
            'The appearance assembly retains exactly 48 intended opaque overlap pixels, zero hidden/stacked glass, and unchanged D1 composition.','',
            'Eight deliberately broken local controls were rejected. These are local checks, not the repository test-suite total.','',
            'Next: independent reference-only validation in Codex. Geometry/appearance user approval and production approval are separate.','']
    (ROOT/'reports/d2_local_checks.md').write_text('\n'.join(lines),encoding='utf-8')
    return checks

if __name__=='__main__':
    result=main()
    print(json.dumps({'pass':result['pass'],'views':{n:{k:q[k] for k in ('native_dimensions','alpha_changed_pixels','rgb_changed_pixels')} for n,q in result['views'].items()},'corner':result['corner']},indent=2))
