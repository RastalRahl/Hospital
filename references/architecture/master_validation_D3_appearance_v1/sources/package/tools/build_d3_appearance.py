"""Rebuild the local, reference-only D3 RGB appearance candidate.

Dependencies: Pillow and numpy. Run: python tools/build_d3_appearance.py
Writes only this package's candidate/, previews/ and reports/ directories.
Never edits inputs, a repository, a manifest, or approval records.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
NAMES = ('main', 'repeat', 'corner_main', 'corner_repeat')
STEM = 'rastalr_D3_glass_partition_side_right_locked_v1_'
BASELINE = '65aca7a461a60d49e57e4b82257e782fc9c9b1d0'
# Same palette as D2. Placement of highlights is authored in screen coordinates.
DARK=(24,35,49); EDGE=(51,73,91); MID=(86,112,131)
LIGHT=(104,134,154); CAP=(137,164,180)
GLASS=(146,182,195); GLASS_SHADE=(137,173,187); GLASS_LIGHT=(153,189,201)


def load(path: Path) -> Image.Image:
    with Image.open(path) as im:
        im.load()
        if im.mode != 'RGBA':
            raise ValueError(f'Expected saved RGBA, not implicit conversion: {path}')
        return im.copy()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def saved(path: Path, im: Image.Image) -> Image.Image:
    im.save(path)
    return load(path)


def diff(a: Image.Image, b: Image.Image) -> int:
    if a.size != b.size or a.mode != b.mode:
        return max(a.width*a.height, b.width*b.height)
    return int(np.count_nonzero(np.any(np.asarray(a) != np.asarray(b), axis=2)))


def rgb(im: Image.Image, x: int, y: int, color: tuple[int,int,int]) -> None:
    im.putpixel((x,y), (*color, im.getpixel((x,y))[3]))


def paint(scaffolds: dict[str,Image.Image]) -> dict[str,Image.Image]:
    """RGB-only edit of D3 files, not reflection of any D2 finished image."""
    main=scaffolds['main'].copy()
    for y in range(32):
        for x in range(12):
            if x in (0,11): color=DARK
            elif x == 1: color=LIGHT             # Screen-left bevel catches light.
            elif x == 10: color=EDGE            # Screen-right bevel stays darker.
            elif y < 4: color=(CAP,LIGHT,MID,DARK)[y]
            elif y >= 28: color=(DARK,EDGE,MID,DARK)[y-28]
            else: color=GLASS_SHADE if x in (2,9) else GLASS
            rgb(main,x,y,color)
    for x,y in ((4,8),(4,9),(5,10),(5,11),(6,12)):
        rgb(main,x,y,GLASS_LIGHT)
    repeat=main.copy()
    for y in range(28,32):
        for x in range(2,10): repeat.putpixel((x,y),main.getpixel((x,27)))
    corner=scaffolds['corner_main'].copy()
    for y in range(24):
        for x in range(12):
            if corner.getpixel((x,y))[3] == 0:
                continue                        # Even invisible RGB is immutable.
            if y < 4:
                color=DARK if x == 11 else (CAP,LIGHT,MID,DARK)[y]
            elif x == 11: color=DARK
            elif x == 10: color=LIGHT            # Left bevel of the right-hand post.
            elif x == 8: color=GLASS_LIGHT       # Screen-left edge of glazed reveal.
            else: color=GLASS
            rgb(corner,x,y,color)
    corner.paste(main,(0,24))                     # Exact body, not a new drawing.
    corner_repeat=corner.copy();corner_repeat.paste(repeat,(0,24))
    return {'main':main,'repeat':repeat,'corner_main':corner,'corner_repeat':corner_repeat}


def expected_alpha(name: str) -> np.ndarray:
    """Independent region mask transcribed from the committed D3 contract."""
    h=56 if name.startswith('corner_') else 32
    a=np.zeros((h,12),np.uint8)
    terminal=name.endswith('main')
    if h == 32:
        a[:,0:2]=255;a[:,10:12]=255;a[0:4,2:10]=255
        a[4:(28 if terminal else 32),2:10]=150
        if terminal:a[28:32,2:10]=255
    else:
        a[0:4,4:12]=255;a[4:24,10:12]=255
        a[4:24,8:10]=150;a[24:28,:]=255
        a[28:56,0:2]=255;a[28:56,10:12]=255
        a[28:(52 if terminal else 56),2:10]=150
        if terminal:a[52:56,2:10]=255
    return a


def check_view(im: Image.Image, export: Image.Image, source: Image.Image, name: str) -> dict:
    a=np.asarray(im); b=np.asarray(source); expected=expected_alpha(name)
    expanded=np.repeat(np.repeat(a,8,axis=0),8,axis=1)
    q={'native_mode':im.mode,'source_mode':export.mode,'native_dimensions':list(im.size),
       'source_dimensions':list(export.size),
       'alpha_changed_pixels':int(np.count_nonzero(a[:,:,3]!=b[:,:,3])),
       'rgb_changed_pixels':int(np.count_nonzero(np.any(a[:,:,:3]!=b[:,:,:3],axis=2))),
       'zero_alpha_rgba_changed_pixels':int(np.count_nonzero(np.any(a!=b,axis=2)&(b[:,:,3]==0))),
       'contract_alpha_violations':int(np.count_nonzero(a[:,:,3]!=expected)),
       'source_block_errors':int(np.count_nonzero(np.any(np.asarray(export)!=expanded,axis=2))),
       'native_roundtrip_errors':diff(im,export.resize(im.size,Image.Resampling.NEAREST)),
       'alpha_histogram':{str(v):int(n) for v,n in zip(*np.unique(a[:,:,3],return_counts=True))}}
    q['pass']=im.mode==export.mode=='RGBA' and im.size==source.size and export.size==(im.width*8,im.height*8) and all(q[k]==0 for k in ('alpha_changed_pixels','zero_alpha_rgba_changed_pixels','contract_alpha_violations','source_block_errors','native_roundtrip_errors'))
    return q


def side_run(views: dict[str,Image.Image], count: int, corner: bool=False,
             stride: int=32, naive: bool=False) -> tuple[Image.Image,list,list,np.ndarray]:
    off=24 if corner else 0
    out=Image.new('RGBA',(12,32*count+off));cov=np.zeros((out.height,12),np.uint8)
    origins=[];selected=[]
    for i in range(count):
        name=('corner_' if corner and i==0 else '')+('main' if naive or i==count-1 else 'repeat')
        im=views[name];y=0 if corner and i==0 else off+i*stride
        out.alpha_composite(im,(0,y));origins.append([0,y]);selected.append(name)
        alpha=np.asarray(im)[:,:,3];end=min(y+im.height,out.height)
        if end>y:cov[y:end]+=(alpha[:end-y]>0)&(alpha[:end-y]<255)
    return out,origins,selected,cov


def spans(values: np.ndarray) -> list[list[int]]:
    result=[];start=None
    for i,v in enumerate(list(values)+[False]):
        if v and start is None:start=i
        if not v and start is not None:result.append([start,i]);start=None
    return result


def check_run(im: Image.Image, origins: list, selected: list, cov: np.ndarray,
              views: dict[str,Image.Image], count: int, corner: bool) -> dict:
    off=24 if corner else 0;a=np.asarray(im)[:,:,3]
    expected=np.full((32*count,12),150,np.uint8)
    expected[:,:2]=255;expected[:,10:]=255
    for i in range(count):expected[32*i:32*i+4,:]=255
    expected[-4:]=255
    origins_expected=[[0,0]]+[[0,off+32*i] for i in range(1,count)]
    names_expected=[('corner_' if corner and i==0 else '')+('main' if i==count-1 else 'repeat') for i in range(count)]
    selection_errors=sum(diff(im.crop((0,p[1],12,p[1]+views[n].height)),views[n]) for p,n in zip(origins,selected))
    actual_spans=spans(a[off:,6]==255)
    expected_spans=[[i*32,i*32+4] for i in range(count)]+[[count*32-4,count*32]]
    q={'dimensions':list(im.size),'origins':origins,'selected_views':selected,
       'body_alpha_violations':int(np.count_nonzero(a[off:]!=expected)),
       'support_spans':actual_spans,'single_layer_violations':int(np.count_nonzero(cov[(a>0)&(a<255)]!=1)),
       'selection_pixel_errors':selection_errors,'origin_pass':origins==origins_expected,
       'selection_pass':selected==names_expected,'supports_pass':actual_spans==expected_spans}
    if corner:q['return_alpha_violations']=int(np.count_nonzero(a[:24]!=expected_alpha('corner_main')[:24]))
    q['pass']=q['origin_pass'] and q['selection_pass'] and q['supports_pass'] and all(q[k]==0 for k in ('body_alpha_violations','single_layer_violations','selection_pixel_errors')) and q.get('return_alpha_violations',0)==0
    return q


def transmission(im: Image.Image, stem: str | None=None) -> dict:
    f=np.asarray(im).astype(np.int32);a=f[:,:,3];pane=(a>0)&(a<255);frame=a==255
    backgrounds={n:Image.new('RGBA',im.size,c) for n,c in {'light':(240,237,223,255),'dark':(30,40,54,255),'colored':(61,127,169,255)}.items()}
    obj=Image.new('RGBA',im.size)
    # Toggle an independent object through every pane pixel, including thin return.
    for y in range(im.height):
        for x in range(im.width):
            if pane[y,x] and (x+y)%9 < 5:obj.putpixel((x,y),(245,183,34,255))
    backgrounds['object']=Image.alpha_composite(backgrounds['colored'],obj)
    scenes={n:Image.alpha_composite(bg,im) for n,bg in backgrounds.items()}
    changed=np.any(np.asarray(scenes['light'])[:,:,:3]!=np.asarray(scenes['dark'])[:,:,:3],axis=2)
    toggled=np.any(np.asarray(scenes['object'])[:,:,:3]!=np.asarray(scenes['colored'])[:,:,:3],axis=2)
    covered=pane & (np.asarray(obj)[:,:,3]>0)
    errors=0
    for n,bg in backgrounds.items():
        b=np.asarray(bg).astype(np.int32)
        expect=(f[:,:,:3]*a[:,:,None]+b[:,:,:3]*(255-a[:,:,None])+127)//255
        errors+=int(np.count_nonzero(np.any(np.asarray(scenes[n])[:,:,:3]!=expect,axis=2)))
        if stem:
            saved(ROOT/f'previews/{stem}_{n}_background.png',bg)
            saved(ROOT/f'previews/{stem}_{n}_composite.png',scenes[n])
    if stem:saved(ROOT/f'previews/{stem}_object_layer.png',obj)
    q={'pane_pixels':int(pane.sum()),'responsive_pane_pixels':int(changed[pane].sum()),
       'frame_response_pixels':int(changed[frame].sum()),'object_covered_pane_pixels':int(covered.sum()),
       'object_responsive_pane_pixels':int(toggled[covered].sum()),'source_over_pixel_errors':errors}
    q['pass']=q['pane_pixels']>0 and q['responsive_pane_pixels']==q['pane_pixels'] and q['frame_response_pixels']==0 and q['object_covered_pane_pixels']>0 and q['object_responsive_pane_pixels']==q['object_covered_pane_pixels'] and errors==0
    return q


def horizontal(count: int) -> Image.Image:
    main=load(ROOT/'sources/rastalr_D1_glass_partition_back_locked_v1_native.png')
    repeat=load(ROOT/'sources/rastalr_D1_glass_partition_back_locked_v1_repeat_native.png')
    out=Image.new('RGBA',(32*count,28))
    for i in range(count):out.alpha_composite(main if i==count-1 else repeat,(32*i,0))
    return out


def prior_d2() -> dict:
    return {n:load(ROOT/f'sources/rastalr_D2_glass_partition_side_left_locked_v1_{n}_native.png') for n in NAMES}


def corner_check(front: Image.Image, side: Image.Image, right: bool,
                 edge: int, base: int, cell: tuple[int,int], origin: tuple[int,int]) -> dict:
    top=base-28;cy=base-4;a=np.asarray(front)[:,:,3];b=np.asarray(side)[:,:,3]
    if right:
        rects=[[edge-4,top,edge,top+4],[edge-8,cy,edge,base]]
        reveal=[edge,top+4,edge+2,cy];outer=[edge+2,top,edge+4,base];cap=[edge-8,cy,edge+4,base]
        expected_origin=(cell[0]+8,cell[1]-24)
    else:
        rects=[[edge,top,edge+4,top+4],[edge,cy,edge+8,base]]
        reveal=[edge-2,top+4,edge,cy];outer=[edge-4,top,edge-2,base];cap=[edge-4,cy,edge+8,base]
        expected_origin=(cell[0]+12,cell[1]-24)
    allowed=np.zeros_like(a,dtype=bool)
    for l,t,r,bt in rects:allowed[t:bt,l:r]=True
    overlap=(a>0)&(b>0)
    opaque=(a==255)&(b==255)
    hidden=((a>0)&(a<255)&(b==255))|((b>0)&(b<255)&(a==255))
    stacked=(a>0)&(a<255)&(b>0)&(b<255)
    def violations(rect,alpha):
        l,t,r,bt=rect;return int(np.count_nonzero(b[t:bt,l:r]!=alpha))
    q={'actual_origin':list(origin),'expected_origin':list(expected_origin),
       'anchor_pass':origin==expected_origin,'centerline_pass':list(cell)==[edge-16,cy],
       'opaque_overlap_pixels':int(opaque.sum()),'expected_overlap_pixels':int(allowed.sum()),
       'overlap_ownership_errors':int(np.count_nonzero(overlap!=allowed)),
       'unexpected_overlap_pixels':int(np.count_nonzero(overlap&~allowed)),
       'stacked_glass_pixels':int(stacked.sum()),'hidden_glass_pixels':int(hidden.sum()),
       'upper_contact_violations':violations(rects[0],255),'return_frame_violations':violations(outer,255),
       'return_glass_violations':violations(reveal,150),'shallow_cap_violations':violations(cap,255),
       'ground_centerline': [edge,cy],'baseline_y':base,'top_y':top,'cutaway_drop':cy-top}
    q['pass']=q['anchor_pass'] and q['centerline_pass'] and q['opaque_overlap_pixels']==q['expected_overlap_pixels'] and all(q[k]==0 for k in ('overlap_ownership_errors','stacked_glass_pixels','hidden_glass_pixels','upper_contact_violations','return_frame_violations','return_glass_violations','shallow_cap_violations'))
    return q


def enclosure(views: dict, *, full: bool=True, delta: tuple[int,int]=(0,0), drift: int=0):
    dx,dy=delta;x0=(64 if full else 32)+dx;w=128 if full else 64;top=36+dy;base=top+28;east=x0+w;cy=base-4
    size=(east+48,176+dy)
    front=Image.new('RGBA',size);left=Image.new('RGBA',size);right=Image.new('RGBA',size)
    h=horizontal(w//32);front.alpha_composite(h,(x0,top))
    run,_,_,_=side_run(views,2,True);origin=(east-8+drift,top);right.alpha_composite(run,origin)
    if full:left.alpha_composite(side_run(prior_d2(),2,True)[0],(x0-4,top))
    bg=Image.new('RGBA',size,(225,226,213,255));floor=load(ROOT/'sources/hospital_floor_plain_01.png')
    for y in range(base,size[1],32):
        for x in range(x0,east,32):bg.alpha_composite(floor,(x,y))
    sides=Image.alpha_composite(left,right);structure=Image.alpha_composite(sides,front)
    scene=Image.alpha_composite(bg,structure)
    q={'northeast':corner_check(front,right,True,east,base,(east-16,cy),origin),
       'D1_structure_pixel_errors':diff(structure.crop((x0,top,east,base)),h),
       'D1_composited_pixel_errors':int(np.count_nonzero(np.any(np.asarray(scene)!=np.asarray(Image.alpha_composite(bg,front)),axis=2)&(np.asarray(front)[:,:,3]>0)))}
    if full:
        q['northwest']=corner_check(front,left,False,x0,base,(x0-16,cy),(x0-4,top))
        q['side_intersection_pixels']=int(np.count_nonzero((np.asarray(left)[:,:,3]>0)&(np.asarray(right)[:,:,3]>0)))
        q['front_open']=bool(np.all(np.asarray(structure)[base+60:base+64,x0+8:east-8,3]==0))
        q['D2_layer_pixel_errors']=diff(left.crop((x0-4,top,x0+8,top+88)),side_run(prior_d2(),2,True)[0])
    q['pass']=q['northeast']['pass'] and q['D1_structure_pixel_errors']==q['D1_composited_pixel_errors']==0 and (not full or (q['northwest']['pass'] and q['front_open'] and q['side_intersection_pixels']==q['D2_layer_pixel_errors']==0))
    return scene,{'background':bg,'D1_layer':front,'D2_layer':left,'D3_layer':right,'structure':structure},q


def wall_context(views: dict, delta: int=0):
    wall=load(ROOT/'sources/hospital_wall_side_right_01.png');floor=load(ROOT/'sources/hospital_floor_plain_01.png')
    size=(176+delta,192+delta);cell=(112+delta,64+delta);run,_,_,_=side_run(views,2)
    bg=Image.new('RGBA',size,(225,226,213,255))
    for y in range(32+delta,192+delta,32):
        for x in range(16+delta,128+delta,32):bg.alpha_composite(floor,(x,y))
    walls=Image.new('RGBA',size);glass=Image.new('RGBA',size)
    walls.alpha_composite(wall,(cell[0],cell[1]-32));walls.alpha_composite(wall,(cell[0],cell[1]+64))
    glass.alpha_composite(run,(cell[0]+8,cell[1]))
    structure=Image.alpha_composite(walls,glass);scene=Image.alpha_composite(bg,structure)
    wa=np.asarray(walls)[:,:,3];ga=np.asarray(glass)[:,:,3];x=cell[0]+8;y=cell[1]
    upper=(wa[y-1,x:x+12]==255)&(ga[y,x:x+12]==255)
    lower=(ga[y+63,x:x+12]==255)&(wa[y+64,x:x+12]==255)
    unchanged=diff(structure.crop((cell[0],cell[1]-32,cell[0]+20,cell[1])),wall)==0 and diff(structure.crop((cell[0],cell[1]+64,cell[0]+20,cell[1]+96)),wall)==0
    q={'cell':list(cell),'render_origin':[x,y],'origin_relative_to_cell':[8,0],
       'upper_opaque_contact_pixels':int(upper.sum()),'lower_opaque_contact_pixels':int(lower.sum()),
       'wall_pixels_unchanged':unchanged,'overlap_pixels':int(np.count_nonzero((wa>0)&(ga>0)))}
    q['pass']=q['upper_opaque_contact_pixels']==q['lower_opaque_contact_pixels']==12 and unchanged and q['overlap_pixels']==0
    return scene,{'background':bg,'wall_layer':walls,'D3_layer':glass,'structure':structure},q


def preview(scaffolds: dict, views: dict) -> None:
    board=Image.new('RGB',(1360,1460),(24,35,49));d=ImageDraw.Draw(board)
    font_path=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    def f(size):return ImageFont.truetype(str(font_path),size) if font_path.exists() else ImageFont.load_default()
    def text(x,y,s,size=18,fill=(222,232,237)):d.text((x,y),s,font=f(size),fill=fill)
    def put(im,x,y,k,bg=(33,47,62,255)):
        enlarged=im.resize((im.width*k,im.height*k),Image.Resampling.NEAREST)
        tile=Image.new('RGBA',enlarged.size,bg);tile.alpha_composite(enlarged);board.paste(tile.convert('RGB'),(x,y))
    text(28,20,'D3 | RIGHT GLASS PARTITION',29)
    text(28,64,'RGB-only appearance candidate | D1 and D2 unchanged | no production approval',18)
    text(28,104,'Geometry scaffold in the existing family',20)
    text(704,104,'Appearance candidate in the same enclosure',20)
    before=enclosure(scaffolds)[0];after=enclosure(views)[0]
    crop=(56,28,204,140)
    put(before.crop(crop),28,142,4);put(after.crop(crop),704,142,4)
    text(28,612,'Four exclusive views = one future logical asset',20)
    for i,name in enumerate(NAMES):
        x=40+i*154
        put(views[name],x,680,4)
        text(x,646,name.replace('_',' '),15)
        text(x,920,f'{views[name].width}x{views[name].height}',15)
    text(704,612,'Depth repeats: 1 / 2 / 4 cells',20)
    for i,n in enumerate((1,2,4)):
        run=side_run(views,n,True)[0];put(run,728+i*176,652,2)
        text(724+i*176,980,f'{n} cell'+('s' if n!=1 else ''),16)
    text(28,1008,'Right-wall context / 1x inset',19)
    ctx=wall_context(views)[0]
    put(ctx.crop((96,24,140,168)),28,1044,2)
    put(after.crop(crop),152,1070,1)
    text(152,1200,'Same scene at 1x',14)
    text(460,1008,'Same RGBA glass / separate backgrounds',19)
    run=side_run(views,2,True)[0]
    for i,(name,col) in enumerate([('Light',(240,237,223,255)),('Dark',(30,40,54,255)),('Object',(61,127,169,255))]):
        bg=Image.new('RGBA',run.size,col)
        if name=='Object':bg.paste((245,183,34,255),(3,34,9,49));bg.paste((189,78,142,255),(3,70,9,84))
        put(Image.alpha_composite(bg,run),480+i*136,1044,3)
        text(474+i*136,1322,name,16)
    text(918,1010,'What is locked',20)
    for i,line in enumerate(['All alpha values','Frame and pane regions','32 px depth stride','D3 origin: [8,0]','Corner origin: [8,-24]','24 px intentional cutaway','48 opaque overlap px / corner']):text(918,1052+i*35,line,16)
    text(28,1380,'Upper-left lighting is authored in screen space. Finished D2 artwork was not flipped.',18)
    text(28,1418,'Local candidate checks only. Independent Codex validation is the next gate.',17)
    board.save(ROOT/'previews/d3_locked_appearance_review.png')


def main() -> dict:
    for n in ('candidate','previews','reports'):(ROOT/n).mkdir(exist_ok=True)
    provenance=json.loads((ROOT/'reports/source_provenance.json').read_text())
    for n,record in provenance['files'].items():
        if sha(ROOT/'sources'/n)!=record['sha256']:raise ValueError(f'Protected input changed: {n}')
    originals={n:load(ROOT/f'sources/d3_{n}_native.png') for n in NAMES}
    for n in NAMES:
        assert np.array_equal(np.asarray(originals[n])[:,:,3],expected_alpha(n)),n
    generated=paint(originals);views={};report={'scope':'LOCAL_CANDIDATE_CHECKS_ONLY','baseline_commit':BASELINE,'views':{},'runs':{},'corners':{},'enclosures':{},'contexts':{}}
    for n,im in generated.items():
        p=ROOT/f'candidate/{STEM}{n}_native.png';sp=ROOT/f'candidate/{STEM}{n}_source_8x.png'
        views[n]=saved(p,im);ex=saved(sp,im.resize((im.width*8,im.height*8),Image.Resampling.NEAREST))
        q=check_view(views[n],ex,originals[n],n);assert q['pass'],q;report['views'][n]=q
    arr=np.asarray(views['main']).copy();arr[28:32,2:10]=arr[27:28,2:10]
    rel={'repeat_pixel_errors':int(np.count_nonzero(np.any(arr!=np.asarray(views['repeat']),axis=2)))}
    for n in ('main','repeat'):rel['corner_'+n+'_body_pixel_errors']=diff(views['corner_'+n].crop((0,24,12,56)),views[n])
    rel['pass']=all(v==0 for v in rel.values());assert rel['pass'];report['relationships']=rel
    d2=prior_d2();report['lighting']={'method':'Palette assigned directly at screen-space coordinates; source alpha copied; no finished-art reflection in builder','D3_vs_flipped_D2_pixel_differences':{n:int(np.count_nonzero(np.any(np.asarray(views[n])!=np.flip(np.asarray(d2[n]),axis=1),axis=2))) for n in NAMES},'main_left_bevel_RGB':list(views['main'].getpixel((1,10))[:3]),'main_right_bevel_RGB':list(views['main'].getpixel((10,10))[:3])}
    assert all(v>0 for v in report['lighting']['D3_vs_flipped_D2_pixel_differences'].values())
    for n in (1,2,4):
        for corner in (False,True):
            key=('corner' if corner else 'straight')+f'_{n}'
            im,origins,selected,cov=side_run(views,n,corner)
            im=saved(ROOT/f'previews/{key}_native.png',im)
            q=check_run(im,origins,selected,cov,views,n,corner);q['transmission']=transmission(im,'transmission' if key=='corner_2' else None)
            assert q['pass'] and q['transmission']['pass'];report['runs'][key]=q
    for full in (False,True):
        label='enclosure' if full else 'northeast'
        for move in (0,32):
            sc,layers,q=enclosure(views,full=full,delta=(move,move));assert q['pass'],q
            q['saved_composite_errors']=diff(saved(ROOT/f'previews/{label}_{move}_scene.png',sc),Image.alpha_composite(layers['background'],layers['structure']))
            for n,im in layers.items():saved(ROOT/f'previews/{label}_{move}_{n}.png',im)
            report['enclosures' if full else 'corners'][str(move)]=q
        a=enclosure(views,full=full)[1]['structure'];b=enclosure(views,full=full,delta=(32,32))[1]['structure']
        measured=diff(a,b.crop((32,32,32+a.width,32+a.height)))
        report[label+'_relocation_structure_errors']=measured
        assert measured==0
    # Explicit preservation of the old left corner between pre/post appearance.
    old_scene,old_layers,_=enclosure(originals);new_scene,new_layers,_=enclosure(views)
    report['D2_layer_errors_vs_scaffold_context']=diff(old_layers['D2_layer'],new_layers['D2_layer']);assert report['D2_layer_errors_vs_scaffold_context']==0
    saved(ROOT/'previews/d3_scaffold_enclosure.png',old_scene)
    for move in (0,32):
        sc,layers,q=wall_context(views,move);assert q['pass'];saved(ROOT/f'previews/right_wall_context_{move}.png',sc)
        for name,im in layers.items():saved(ROOT/f'previews/right_wall_context_{move}_{name}.png',im)
        report['contexts'][str(move)]=q
    a=wall_context(views)[1]['structure'];b=wall_context(views,32)[1]['structure']
    report['wall_context_relocation_structure_errors']=diff(a,b.crop((32,32,32+a.width,32+a.height)));assert report['wall_context_relocation_structure_errors']==0
    # Negative controls call the same pixel/placement predicates as valid controls.
    neg={};good,po,se,co=side_run(views,2);control=check_run(good,po,se,co,views,2,False)['pass']
    for name,point,alpha in [('opaque_glass',(5,10),255),('pane_hole',(5,10),0),('broken_frame',(0,10),0)]:
        bad=good.copy();bad.putpixel(point,(*bad.getpixel(point)[:3],alpha))
        q=check_run(bad,po,se,co,views,2,False);neg[name]={'valid_control_pass':control,'rejected':not q['pass']}
    bad,bp,bs,bc=side_run(views,2,naive=True);neg['wrong_terminal_or_doubled_support']={'valid_control_pass':control,'rejected':not check_run(bad,bp,bs,bc,views,2,False)['pass']}
    bad,bp,bs,bc=side_run(views,2,stride=33);neg['repeat_drift_1px']={'valid_control_pass':control,'rejected':not check_run(bad,bp,bs,bc,views,2,False)['pass']}
    bad=good.copy();bad.alpha_composite(views['main'].crop((2,4,10,28)),(2,4));bc=co.copy();bc[4:28,2:10]+=1
    neg['stacked_glass']={'valid_control_pass':control,'rejected':not check_run(bad,po,se,bc,views,2,False)['pass']}
    for name,drift in [('corner_drift_1px',1),('wrong_left_origin',4)]:neg[name]={'valid_control_pass':report['corners']['0']['pass'],'rejected':not enclosure(views,full=False,drift=drift)[2]['pass']}
    bad={**views,'corner_repeat':views['corner_repeat'].copy()};bad['corner_repeat'].paste((0,0,0,0),(0,0,12,24))
    neg['missing_corner_return']={'valid_control_pass':report['corners']['0']['pass'],'rejected':not enclosure(bad,full=False)[2]['pass']}
    ex=load(ROOT/f'candidate/{STEM}main_source_8x.png');ex.putpixel((0,0),(1,2,3,255))
    neg['source_subpixel']={'valid_control_pass':report['views']['main']['pass'],'rejected':not check_view(views['main'],ex,originals['main'],'main')['pass']}
    assert all(v['valid_control_pass'] and v['rejected'] for v in neg.values());report['negative_controls']=neg
    report['sources_unchanged']=all(sha(ROOT/'sources'/n)==record['sha256'] for n,record in provenance['files'].items());assert report['sources_unchanged']
    report['status']='PASS_LOCAL_CANDIDATE_CHECKS';report['repository_suite_rerun']=False
    report['review_limits']=['Right-side cutaway and the reviewed NW/NE enclosure only; not full-height side glass or all-direction junction approval.','Appearance readiness is ChatGPT visual judgement, not recorded human production approval.','Committed D3 historical contract stays proposed.','PNG outputs are local files; no repository was modified.']
    write_json(ROOT/'reports/d3_local_checks.json',report)
    spec={'planning_id':'hospital_glass_partition_side_right_01','version':'locked_appearance_v1','status':'REFERENCE_ONLY_APPEARANCE_CANDIDATE','authority':{'repository':'RastalRahl/Hospital','commit':BASELINE,'contract_path':provenance['contract_path'],'contract_git_blob_sha1':provenance['contract_git_blob_sha1']},'normalization':'architecture_grid_preserving','logical_grid':32,'source_scale':8,'cell_anchor':[16,16],'depth_stride':[0,32],'alpha_policy':{'frame':255,'pane':150,'exterior':0,'unchanged_pixel_for_pixel_from_corresponding_scaffold':True},'art_change':'RGB-only screen-space palette assignment, never mirrored D2 pixels','views':{},'relationships':{'repeat':'Copy main; extend row 27 into rows 28..31 ONLY for x2..9.','corner_body':'corner_main/repeat crop [0,24,12,56) exactly equals main/repeat.','selection':'Use one alternative per ground cell. North-east first cell chooses corner_main if last, otherwise corner_repeat. Later cells choose repeat, then terminal main.'},'corner':{'layer_order':['separate background','unchanged D2 when present','D3','unchanged D1'],'main_origin':[8,0],'corner_origin':[8,-24],'cutaway_drop':24,'expected_opaque_overlap_per_back_corner':48,'glass_overlap_allowed':False,'D1_D2_modified':False},'scope':'All four views belong to ONE future logical asset. No production registration or approval.'}
    for name in NAMES:
        spec['views'][name]={'native_file':f'candidate/{STEM}{name}_native.png','source_file':f'candidate/{STEM}{name}_source_8x.png','native_dimensions':list(views[name].size),'source_dimensions':[views[name].width*8,views[name].height*8],'image_anchor':[8,40 if name.startswith('corner') else 16],'origin_relative_to_cell':[8,-24 if name.startswith('corner') else 0],'scaffold_file':f'sources/d3_{name}_native.png','source_sha256':sha(ROOT/f'sources/d3_{name}_native.png'),'candidate_sha256':sha(ROOT/f'candidate/{STEM}{name}_native.png')}
    write_json(ROOT/'reports/d3_candidate_spec.json',spec)
    lines=['# D3 local appearance checks','','Status: PASS_LOCAL_CANDIDATE_CHECKS. These are local package checks, not the repository test suite.','','| View | Native | Export | Alpha changes | RGB changes | Invisible RGBA changes |','|---|---|---|---:|---:|---:|']
    for n,q in report['views'].items():lines.append(f"| {n} | {q['native_dimensions']} | {q['source_dimensions']} | {q['alpha_changed_pixels']} | {q['rgb_changed_pixels']} | {q['zero_alpha_rgba_changed_pixels']} |")
    lines+=['','All eight exports preserve exact 8x blocks and native round-trips. The four native views preserve their scaffold alpha maps.','Straight/corner runs at 1, 2 and 4 cells pass actual pixel, selection, support-width, stride and transmission checks.','North-east and both-corner enclosure checks pass at original and +32,+32 relocated origins; each reviewed corner has 48 intentionally opaque overlapping pixels, no stacked or hidden glass.','D1 pixels and D2 layer bytes remain unchanged; the front stays open. Right-wall context uses a hash-verified approved Batch 11 wall and floor unchanged.','Ten actual negative controls are rejected, each with a passing valid control.','Lighting is independently placed in screen space, not a horizontal flip of D2 finished art.','All input files retained their hashes. No repository, inventory, approval or historical contract was changed.','','Run: `python tools/build_d3_appearance.py`. Dependencies: Pillow and numpy.','The package previews are generated from the saved candidate files, not a generative image board.','The scaffold review reconstruction is locally assembled from verified inputs and the committed layout. No claim of matching repository preview PNG encoder bytes is made.','']
    (ROOT/'reports/d3_local_checks.md').write_text('\n'.join(lines),encoding='utf-8')
    preview(originals,views)
    return report


if __name__ == '__main__':
    result=main()
    print(json.dumps({'status':result['status'],'views':result['views'],'negative_controls':len(result['negative_controls']),'repository_suite_rerun':False},indent=2))
