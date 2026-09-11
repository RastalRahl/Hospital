"""RGB-only D4 appearance candidate. Run: python tools/build_d4_appearance.py

Dependencies: Pillow, numpy. Writes only this package's candidate, previews and
reports directories. Never changes source files or a production repository.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
COMMIT='2ec243597e60f55435983d2de6a64592273d5f6f'
STEM='rastalr_D4_glass_partition_front_cutaway_locked_v1_'
DARK=(24,35,49); EDGE=(51,73,91); MID=(86,112,131)
LIGHT=(104,134,154); CAP=(137,164,180)
GLASS=(146,182,195); GLASS_SHADE=(137,173,187); GLASS_LIGHT=(153,189,201)


def load(p):
    with Image.open(p) as im:
        im.load()
        if im.mode!='RGBA': raise ValueError(f'Expected RGBA without conversion: {p}')
        return im.copy()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def jwrite(p,obj): p.write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
def save(p,im): im.save(p);return load(p)
def diff(a,b):
    if a.size!=b.size or a.mode!=b.mode:return max(a.width*a.height,b.width*b.height)
    return int(np.count_nonzero(np.any(np.asarray(a)!=np.asarray(b),axis=2)))
def rectangle_mask(size,rects):
    mask=np.zeros((size[1],size[0]),bool)
    for l,t,r,b in rects: mask[t:b,l:r]=True
    return mask

def alpha_expected(name):
    a=np.full((12,32),255,np.uint8)
    a[4:10,4:(28 if name=='main' else 32)]=150
    return a

def paint(main_source):
    main=main_source.copy()
    for y in range(12):
        for x in range(32):
            if y<4: c=(CAP,LIGHT,MID,DARK)[y]
            elif y>=10: c=(MID,DARK)[y-10]
            elif x<4: c=(DARK,LIGHT,EDGE,DARK)[x]
            elif x>=28: c=(DARK,MID,EDGE,DARK)[x-28]
            else: c=GLASS_SHADE if y in (4,9) or x==4 else GLASS
            main.putpixel((x,y),(*c,main.getpixel((x,y))[3]))
    for p in ((8,5),(9,6),(10,7)):
        main.putpixel(p,(*GLASS_LIGHT,main.getpixel(p)[3]))
    repeat=main.copy()
    # Only the declared nonterminal pane continuation changes. Preserve rails.
    for y in range(4,10):
        for x in range(28,32):repeat.putpixel((x,y),main.getpixel((27,y)))
    return {'main':main,'repeat':repeat}

def check_view(im,export,source,name):
    a=np.asarray(im);s=np.asarray(source)
    if im.size!=(32,12) or im.mode!='RGBA' or export.size!=(256,96) or export.mode!='RGBA':
        return {'pass':False,'dimensions_or_mode':False}
    q={'native_dimensions':list(im.size),'export_dimensions':list(export.size),'mode':im.mode,
       'alpha_changed_pixels':int(np.count_nonzero(a[:,:,3]!=s[:,:,3])),
       'rgb_changed_pixels':int(np.count_nonzero(np.any(a[:,:,:3]!=s[:,:,:3],axis=2))),
       'alpha_contract_violations':int(np.count_nonzero(a[:,:,3]!=alpha_expected(name))),
       'invisible_rgba_changes':int(np.count_nonzero(np.any(a!=s,axis=2)&(s[:,:,3]==0))),
       'export_block_errors':int(np.count_nonzero(np.any(np.asarray(export)!=np.repeat(np.repeat(a,8,0),8,1),axis=2))),
       'roundtrip_errors':diff(im,export.resize(im.size,Image.Resampling.NEAREST)),
       'alpha_histogram':{str(k):int(v) for k,v in zip(*np.unique(a[:,:,3],return_counts=True))}}
    q['pass']=all(q[k]==0 for k in ('alpha_changed_pixels','alpha_contract_violations','invisible_rgba_changes','export_block_errors','roundtrip_errors'))
    return q

def horizontal(views,count,stride=32,naive=False):
    height=views['main'].height
    out=Image.new('RGBA',(count*32,height));cov=np.zeros((height,count*32),np.uint8);origins=[]
    for i in range(count):
        im=views['main' if naive or i==count-1 else 'repeat'];x=i*stride
        out.alpha_composite(im,(x,0));origins.append([x,0]);end=min(out.width,x+32)
        if end>x:
            a=np.asarray(im)[:,:end-x,3];cov[:,x:end]+=(a>0)&(a<255)
    return out,origins,cov

def span(values):
    out=[];start=None
    for i,v in enumerate(list(values)+[False]):
        if v and start is None:start=i
        if not v and start is not None:out.append([start,i]);start=None
    return out

def check_run(run,origins,cov,count,views):
    if run.size!=(32*count,12):return {'pass':False,'size':list(run.size)}
    a=np.asarray(run)[:,:,3];exp=np.full_like(a,150);exp[:4]=255;exp[10:]=255
    for i in range(count):exp[:,32*i:32*i+4]=255
    exp[:,-4:]=255
    frame=exp==255;glass=exp==150
    q={'origins_match':origins==[[32*i,0] for i in range(count)],
       'frame_violations':int(np.count_nonzero(a[frame]!=255)),
       'pane_violations':int(np.count_nonzero(a[glass]!=150)),
       'shared_support_spans':span(a[6]==255),
       'single_layer_violations':int(np.count_nonzero(cov[glass]!=1)),
       'selected_view_pixel_errors':sum(diff(run.crop((i*32,0,(i+1)*32,12)),views['main' if i==count-1 else 'repeat']) for i in range(count))}
    q['supports_match']=q['shared_support_spans']==[[i*32,i*32+4] for i in range(count)]+[[count*32-4,count*32]]
    q['pass']=q['origins_match'] and q['supports_match'] and all(q[k]==0 for k in ('frame_violations','pane_violations','single_layer_violations','selected_view_pixel_errors'))
    return q

def side_views(n):
    return {v:load(ROOT/'sources'/f'rastalr_{n}_glass_partition_side_{"left" if n=="D2" else "right"}_locked_v1_{v}_native.png') for v in ('main','repeat','corner_main','corner_repeat')}
def side_run(views,count):
    out=Image.new('RGBA',(12,24+32*count))
    for i in range(count):
        key=('corner_' if i==0 else '')+('main' if i==count-1 else 'repeat')
        out.alpha_composite(views[key],(0,0 if i==0 else 24+32*i))
    return out

def overlap(a,b,rects):
    aa=np.asarray(a)[:,:,3];bb=np.asarray(b)[:,:,3]
    actual=(aa>0)&(bb>0);expected=rectangle_mask(a.size,rects)
    opaque=(aa==255)&(bb==255)
    q={'intentional_opaque':int(np.count_nonzero(opaque&expected)),
       'expected_opaque_area':int(expected.sum()),
       'unexpected_overlap':int(np.count_nonzero(actual&~expected)),
       'missing_contact':int(np.count_nonzero(expected&~opaque)),
       'stacked_glass':int(np.count_nonzero((aa>0)&(aa<255)&(bb>0)&(bb<255))),
       'hidden_glass':int(np.count_nonzero(((aa==255)&(bb>0)&(bb<255))|((bb==255)&(aa>0)&(aa<255))))}
    q['pass']=q['intentional_opaque']==q['expected_opaque_area'] and all(q[k]==0 for k in ('unexpected_overlap','missing_contact','stacked_glass','hidden_glass'))
    return q

def enclosure(views,width=4,depth=2,delta=(0,0),front_drift=(0,0),wrong_side_terminal=False):
    x0=64+delta[0];top=36+delta[1];north=top+24;east=x0+32*width;south=north+32*depth
    size=(east+48,south+56)
    backviews={v:load(ROOT/'sources'/f'rastalr_D1_glass_partition_back_locked_v1_{"" if v=="main" else "repeat_"}native.png') for v in ('main','repeat')}
    back=horizontal(backviews,width)[0];left=side_run(side_views('D2'),depth)
    rightviews=side_views('D3')
    if wrong_side_terminal:
        rightviews['main']=rightviews['repeat'];rightviews['corner_main']=rightviews['corner_repeat']
    right=side_run(rightviews,depth);front,_,_=horizontal(views,width)
    poses={'D1':(back,(x0,top)),'D2':(left,(x0-4,top)),'D3':(right,(east-8,top)),
           'D4':(front,(x0+front_drift[0],south-4+front_drift[1]))}
    layers={};clipped=0
    for name,(im,(x,y)) in poses.items():
        layers[name]=Image.new('RGBA',size);layers[name].alpha_composite(im,(x,y))
        for yy in range(im.height):
            for xx in range(im.width):
                clipped+=int(im.getpixel((xx,yy))[3]>0 and not(0<=xx+x<size[0] and 0<=yy+y<size[1]))
    structure=Image.new('RGBA',size)
    for name in ('D2','D3','D1','D4'):structure.alpha_composite(layers[name])
    bg=Image.new('RGBA',size,(225,226,213,255));floor=load(ROOT/'sources/hospital_floor_plain_01.png')
    for y in range(north,south+16,32):
        for x in range(x0,east,32):bg.alpha_composite(floor,(x,y))
    obj=Image.new('RGBA',size);obj.paste((245,183,34,255),(x0+10,south-12,x0+22,south+8))
    scene=Image.alpha_composite(bg,structure);object_scene=Image.alpha_composite(Image.alpha_composite(bg,obj),structure)
    q={
      'southwest':overlap(layers['D4'],layers['D2'],[[x0,south-4,x0+8,south]]),
      'southeast':overlap(layers['D4'],layers['D3'],[[east-8,south-4,east,south]]),
      'northwest':overlap(layers['D1'],layers['D2'],[[x0,top,x0+4,top+4],[x0,north,x0+8,north+4]]),
      'northeast':overlap(layers['D1'],layers['D3'],[[east-4,top,east,top+4],[east-8,north,east,north+4]]),
      'anchor_matches':poses['D4'][1]==(x0,south-4),
      'D4_measured_top':layers['D4'].getchannel('A').getbbox()[1],
      'D4_measured_base':layers['D4'].getchannel('A').getbbox()[3],
      'ground_centerline_y':south,
      'cell_origin':[x0,south-16], 'render_origin':list(poses['D4'][1]),
      'source_layer_pixel_errors':sum(diff(layers[k].crop((p[0],p[1],p[0]+im.width,p[1]+im.height)),im) for k,(im,p) in poses.items()),
      'D1_final_pixel_errors':diff(structure.crop((x0,top,east,top+28)),back),
      'clipped_nonzero_pixels':clipped}
    expected_d4=Image.alpha_composite(bg,layers['D4']);mask=np.asarray(layers['D4'])[:,:,3]>0
    q['D4_final_composite_pixel_errors']=int(np.count_nonzero(np.any(np.asarray(expected_d4)!=np.asarray(scene),axis=2)&mask))
    hits=(np.asarray(layers['D4'])[:,:,3]==150)&(np.asarray(obj)[:,:,3]>0)
    changed=np.any(np.asarray(scene)!=np.asarray(object_scene),axis=2)
    q['object_pane_samples']=int(hits.sum());q['object_responses']=int((hits&changed).sum())
    q['pass']=all(q[n]['pass'] for n in ('southwest','southeast','northwest','northeast')) and q['anchor_matches'] and all(q[n]==0 for n in ('source_layer_pixel_errors','D1_final_pixel_errors','D4_final_composite_pixel_errors','clipped_nonzero_pixels')) and q['object_pane_samples']==q['object_responses']>0
    q['dimensions_cells']=[width,depth]
    images={**{k+'_layer':v for k,v in layers.items()},'structure':structure,'background':bg,'object_layer':obj,'scene':scene,'object_composite':object_scene}
    for name,edge in [('southwest',x0),('southeast',east)]:images[name]=scene.crop((edge-16,south-20,edge+20,south+16))
    return q,images

def transmission(run):
    fg=np.asarray(run).astype(np.int32);a=fg[:,:,3];pane=a==150;frame=a==255
    bg={n:Image.new('RGBA',run.size,c) for n,c in {'light':(240,237,223,255),'dark':(30,40,54,255),'colored':(61,127,169,255)}.items()}
    obj=Image.new('RGBA',run.size);obj.paste((245,183,34,255),(10,1,22,11));bg['object']=Image.alpha_composite(bg['colored'],obj)
    scenes={n:Image.alpha_composite(b,run) for n,b in bg.items()}
    changed=np.any(np.asarray(scenes['light'])!=np.asarray(scenes['dark']),axis=2)
    hit=pane&(np.asarray(obj)[:,:,3]>0);response=np.any(np.asarray(scenes['object'])!=np.asarray(scenes['colored']),axis=2)
    math_errors=0
    for n,b in bg.items():
        expected=(fg[:,:,:3]*a[:,:,None]+np.asarray(b)[:,:,:3].astype(np.int32)*(255-a[:,:,None])+127)//255
        math_errors+=int(np.count_nonzero(np.any(np.asarray(scenes[n])[:,:,:3]!=expected,axis=2)))
    q={'pane_pixels':int(pane.sum()),'responsive_pane_pixels':int(changed[pane].sum()),'responsive_frame_pixels':int(changed[frame].sum()),
       'object_samples':int(hit.sum()),'object_responses':int(response[hit].sum()),'source_over_errors':math_errors}
    q['pass']=q['pane_pixels']==q['responsive_pane_pixels']>0 and q['responsive_frame_pixels']==0 and q['object_samples']==q['object_responses']>0 and math_errors==0
    return q,{**{n+'_background':im for n,im in bg.items()},**{n+'_composite':im for n,im in scenes.items()},'object_layer':obj}

def negative_controls(views):
    good,p,c=horizontal(views,2);control=check_run(good,p,c,2,views);cases={}
    def record(name,q,key): cases[name]={'valid_control_pass':bool(control['pass']),'intended_failure_observed':bool(q[key] is False if isinstance(q[key],bool) else q[key]>0),'rejected':not q['pass'],'check':key}
    im,pp,cc=horizontal(views,2,stride=33);record('repeat_displaced_1px',check_run(im,pp,cc,2,views),'origins_match')
    for name,xy,alpha,key in [('frame_hole',(6,1),0,'frame_violations'),('opaque_pane',(6,6),255,'pane_violations'),('pane_hole',(6,6),0,'pane_violations')]:
        im=good.copy();im.putpixel(xy,(*im.getpixel(xy)[:3],alpha));record(name,check_run(im,p,c,2,views),key)
    im,pp,cc=horizontal(views,2,naive=True);record('doubled_support',check_run(im,pp,cc,2,views),'supports_match')
    bad={'main':views['repeat'],'repeat':views['repeat']};im,pp,cc=horizontal(bad,2);record('missing_terminal',check_run(im,pp,cc,2,views),'supports_match')
    im=good.copy();im.alpha_composite(views['main'].crop((4,4,28,10)),(4,4));cc=c.copy();cc[4:10,4:28]+=1
    record('stacked_glass',check_run(im,p,cc,2,views),'single_layer_violations')
    for name,kwargs in [('anchor_displaced_1px',{'front_drift':(0,1)}),('baseline_confusion_4px',{'front_drift':(0,4)}),('wrong_side_terminal',{'wrong_side_terminal':True})]:
        baseline=enclosure(views)[0];q=enclosure(views,**kwargs)[0]
        badcorner=not q['southwest']['pass'] or not q['southeast']['pass']
        cases[name]={'valid_control_pass':baseline['pass'],'intended_failure_observed':badcorner,'rejected':not q['pass']}
    broken={k:v.copy() for k,v in views.items()};broken['repeat'].putpixel((6,2),(0,0,0,0))
    baseline=enclosure(views)[0];q=enclosure(broken)[0]
    cases['missing_front_contact']={'valid_control_pass':baseline['pass'],'intended_failure_observed':q['southwest']['missing_contact']>0,'rejected':not q['pass']}
    export=views['main'].resize((256,96),Image.Resampling.NEAREST);export.putpixel((0,0),(1,2,3,255))
    q=check_view(views['main'],export,load(ROOT/'sources/d4_main_native.png'),'main')
    cases['source_subpixel']={'valid_control_pass':True,'intended_failure_observed':q['export_block_errors']>0,'rejected':not q['pass']}
    return cases

def font(sz):
    path=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    return ImageFont.truetype(str(path),sz) if path.exists() else ImageFont.load_default(size=sz)
def make_board(views,scaffolds,enclosures,geometry):
    board=Image.new('RGB',(1360,1480),(24,35,49));d=ImageDraw.Draw(board)
    def txt(x,y,s,sz=18):d.text((x,y),s,fill=(227,235,238),font=font(sz))
    def put(im,x,y,k,bg=None):
        if bg is not None:im=Image.alpha_composite(Image.new('RGBA',im.size,bg),im)
        up=im.resize((im.width*k,im.height*k),Image.Resampling.NEAREST)
        board.paste(up,(x,y),up if up.mode=='RGBA' else None)
    txt(28,22,'D4 / FRONT-CUTAWAY GLASS',30)
    txt(28,68,'LOCKED APPEARANCE CANDIDATE  |  native RGB edit  |  geometry and alpha unchanged',18)
    txt(28,112,'D4 scaffold / 10x',18);put(scaffolds['main'],28,145,10,(240,237,223,255))
    txt(455,112,'D4 main / same 10x scale',18);put(views['main'],455,145,10,(240,237,223,255))
    txt(875,112,'Nonterminal repeat / 10x',18);put(views['repeat'],875,145,10,(30,40,54,255))
    txt(28,285,'32x12 RGBA  |  frame 255  |  pane 150  |  4px trim + 6px pane + 2px lower rail',17)
    txt(28,332,'COMPLETE ENCLOSURE / ACTUAL D1-D4 FILES',21)
    scene=enclosures['original']['object_composite'];put(scene.crop((52,28,208,144)),28,370,4)
    txt(720,332,'BEFORE / FLAT D4 GEOMETRY',21)
    put(geometry['scene'].crop((52,28,208,144)),720,370,3)
    txt(720,738,'Existing D1, D2 and D3 stay unchanged.',16)
    txt(720,766,'Gold object is a separate test layer.',16)
    txt(720,794,'Closed enclosure tests joins, not access.',16)
    txt(28,864,'SOUTH-WEST / 8x',18);put(enclosures['original']['southwest'],28,900,8)
    txt(360,864,'SOUTH-EAST / 8x',18);put(enclosures['original']['southeast'],360,900,8)
    txt(720,864,'LIVE TRANSPARENCY / SAME PNG',18)
    _,trans=transmission(views['main'])
    for i,name in enumerate(('light','dark','colored','object')):
        txt(720,907+i*67,name,15);put(trans[name+'_composite'],827,905+i*67,4)
    txt(28,1210,'4px corner shoulders retained. No masks or added corner pieces.',16)
    txt(28,1253,'REPEAT PROOF / ONE, TWO, FOUR CELLS / SAME 4x SCALE',20)
    for i,n in enumerate((1,2,4)):
        run=horizontal(views,n)[0];txt(28,1302+i*56,str(n)+' cell'+('s' if n>1 else ''),16)
        put(run,165,1293+i*56,4,(240,237,223,255))
    txt(760,1286,'STATUS: ready for independent validation',17)
    txt(760,1316,'Reference-only; no production approval.',16)
    txt(760,1346,'4px shared posts, 32px grid stride.',16)
    txt(760,1376,'Backgrounds never baked into glass.',16)
    board.save(ROOT/'previews/d4_locked_appearance_review.png')

def main():
    sources=json.loads((ROOT/'reports/reference_sources.json').read_text());before={n:sha(ROOT/'sources'/n) for n in sources}
    for n,s in sources.items():
        if before[n]!=s['sha256']:raise ValueError(f'Source modified: {n}')
    scaffolds={n:load(ROOT/'sources'/f'd4_{n}_native.png') for n in ('main','repeat')}
    # Check our reproduction against both independently fetched committed crops.
    _,historic=enclosure(scaffolds,2,1)
    geometry_review={n:diff(historic[n],load(ROOT/'sources'/f'{n}_clean.png')) for n in ('southwest','southeast')}
    assert all(v==0 for v in geometry_review.values()),geometry_review
    views=paint(scaffolds['main']);files={}
    for n,im in views.items():
        views[n]=save(ROOT/'candidate'/f'{STEM}{n}_native.png',im)
        export=save(ROOT/'candidate'/f'{STEM}{n}_source_8x.png',im.resize((256,96),Image.Resampling.NEAREST))
        files[n]=check_view(views[n],export,scaffolds[n],n)
    allowed=rectangle_mask((32,12),[[28,4,32,10]])
    aa=np.asarray(views['main']);bb=np.asarray(views['repeat'])
    relationship={'changed_outside_extension':int(np.count_nonzero(np.any(aa!=bb,axis=2)&~allowed)),
                  'extension_pixel_errors':sum(views['repeat'].getpixel((x,y))!=views['main'].getpixel((27,y)) for y in range(4,10) for x in range(28,32))}
    repeats={}
    for n in (1,2,4):
        run,p,c=horizontal(views,n);run=save(ROOT/'previews'/f'run_{n}_native.png',run)
        q=check_run(run,p,c,n,views);trans,ims=transmission(run)
        for name,im in ims.items():save(ROOT/'previews'/f'run_{n}_{name}.png',im)
        repeats[str(n)]={'geometry':q,'transmission':trans}
    checks={};enclosures={}
    for name,w,d,delta in [('original',4,2,(0,0)),('relocated',4,2,(32,32)),('additional_size',3,3,(0,0))]:
        checks[name],enclosures[name]=enclosure(views,w,d,delta)
        for suffix,im in enclosures[name].items():enclosures[name][suffix]=save(ROOT/'previews'/f'enclosure_{name}_{suffix}.png',im)
        loaded=enclosures[name];xx=64+delta[0];nn=60+delta[1];ee=xx+32*w;ss=nn+32*d;tt=nn-24
        # Re-measure declared contacts from the saved/reloaded layer PNGs.
        for key,a,b,rects in [
            ('southwest','D4','D2',[[xx,ss-4,xx+8,ss]]),
            ('southeast','D4','D3',[[ee-8,ss-4,ee,ss]]),
            ('northwest','D1','D2',[[xx,tt,xx+4,tt+4],[xx,nn,xx+8,nn+4]]),
            ('northeast','D1','D3',[[ee-4,tt,ee,tt+4],[ee-8,nn,ee,nn+4]])]:
            checks[name][key]=overlap(loaded[a+'_layer'],loaded[b+'_layer'],rects)
            assert checks[name][key]['pass']
        replay=Image.new('RGBA',loaded['structure'].size)
        for part in ('D2','D3','D1','D4'):replay.alpha_composite(loaded[part+'_layer'])
        checks[name]['reloaded_structure_errors']=diff(replay,loaded['structure'])
        assert checks[name]['reloaded_structure_errors']==0
        _,scaffold_scene=enclosure(scaffolds,w,d,delta)
        checks[name]['D1_D2_D3_layer_changes']=sum(diff(enclosures[name][v+'_layer'],scaffold_scene[v+'_layer']) for v in ('D1','D2','D3'))
        aa=np.asarray(enclosures[name]['scene']);bb=np.asarray(scaffold_scene['scene']);mask=np.asarray(enclosures[name]['D4_layer'])[:,:,3]>0
        checks[name]['off_D4_scene_changes']=int(np.count_nonzero(np.any(aa!=bb,axis=2)&~mask))
    original=enclosures['original']['structure'];moved=enclosures['relocated']['structure']
    relocation=diff(original,moved.crop((32,32,32+original.width,32+original.height)))
    _,geometry=enclosure(scaffolds);save(ROOT/'previews/d4_scaffold_enclosure.png',geometry['scene'])
    make_board(views,scaffolds,enclosures,geometry)
    negatives=negative_controls(views)
    report={'status':'LOCAL_CANDIDATE_CHECKS_PASS','scope':'Local saved-file checks only; repository suite not run. No production or human approval.',
            'pinned_geometry_commit':COMMIT,'geometry_reconstruction_against_committed_corner_crops':geometry_review,
            'files':files,'relationships':relationship,'repeats':repeats,'enclosures':checks,
            'independent_relocation_errors':relocation,'negative_controls':negatives,
            'protected_local_source_count':len(sources),'changed_local_sources':[n for n,h in before.items() if sha(ROOT/'sources'/n)!=h]}
    okay=all(q['pass'] for q in files.values()) and all(v==0 for v in relationship.values()) and all(q['geometry']['pass'] and q['transmission']['pass'] for q in repeats.values()) and all(q['pass'] and q['D1_D2_D3_layer_changes']==q['off_D4_scene_changes']==0 for q in checks.values()) and relocation==0 and all(v['valid_control_pass'] and v['rejected'] and v['intended_failure_observed'] for v in negatives.values()) and not report['changed_local_sources']
    if not okay:report['status']='FAIL'
    jwrite(ROOT/'reports/d4_local_checks.json',report)
    spec={'planning_id':'hospital_glass_partition_front_cutaway_01','status':'REFERENCE_ONLY_APPEARANCE_CANDIDATE',
          'authority':{'repository':'RastalRahl/Hospital','commit':COMMIT,'contract_path':'references/architecture/master_validation_D4_v1/d4_geometry_alpha_contract_proposed.json','contract_git_blob_sha1':'f8d9fb67256addda31ed6f94f0e08004c0d8ccf2'},
          'normalization':'architecture_grid_preserving','logical_grid':32,'source_scale':8,'logical_footprint':[1,1],'cell_anchor':[16,16],'image_anchor':[16,4],'origin_relative_to_cell':[0,12],
          'alpha_policy':{'frame':255,'pane':150,'exterior':0,'unchanged_from_scaffold':True},
          'art_change':'RGB-only pixel painting inside the existing D4 geometry. No D1 flip or crop. Same established family palette.',
          'views':{n:{'native_file':f'candidate/{STEM}{n}_native.png','source_file':f'candidate/{STEM}{n}_source_8x.png','native_dimensions':[32,12],'source_dimensions':[256,96],'scaffold_file':f'sources/d4_{n}_native.png','candidate_sha256':sha(ROOT/'candidate'/f'{STEM}{n}_native.png')} for n in views},
          'relationships':{'repeat':'Copy main; extend native column27 ONLY through [28,4,32,10). All other RGBA pixels unchanged.','selection':'One view per cell; repeat until final main. These are alternatives, not stacked components.','logical_count':1},
          'front_corners':{'opaque_contact_area_each':32,'D1_D2_D3_source_edits':False,'masks':[],'layer_order':['background','object','D2','D3','D1','D4']},
          'review_limits':'Foreground cutaway, 6px pane and 4px exposed shoulders. Enclosure tests only; no entrance, all-direction topology, or production approval implied.'}
    jwrite(ROOT/'reports/d4_candidate_spec.json',spec)
    md=['# D4 local appearance checks','',f"Result: **{report['status']}**.",'','These are local saved-file checks. The repository full suite was not run here.','',
        '| View | Native | 8x | Changed RGB | Changed alpha |','|---|---|---|---:|---:|']
    for n,q in files.items():md.append(f"| {n} | 32x12 RGBA | 256x96 RGBA | {q['rgb_changed_pixels']} | {q['alpha_changed_pixels']} |")
    md+=['','Both native alpha maps and exact exports match their source geometry.',f'Committed south-west and south-east crop reproduction errors: {geometry_review}.','',
         'Original 4x2, relocated +32,+32 and 3x3 enclosure: all local checks pass.' if okay else 'See JSON for failed checks.',
         'Each front corner: 32 intentional opaque overlap pixels. Each back corner: 48.',
         'No unexpected overlap, stacked or hidden glass, missing contacts or clipping in the tested layouts.',
         'D1/D2/D3 source layers unchanged; differences against scaffold scene confined to D4.',
         f'Negative controls: {len(negatives)}; each must reject its actual broken fixture.',
         f'Unchanged local source files: {len(sources)}. This is not a repository-wide preservation claim.',
         '','Historical proposed geometry and production state were not modified.','']
    (ROOT/'reports/d4_local_checks.md').write_text('\n'.join(md),encoding='utf-8')
    if not okay: raise AssertionError('Local validation failure; inspect reports/d4_local_checks.json')
    print(json.dumps({'result':report['status'],'files':files,'negative_controls':len(negatives),'source_files':len(sources),'relocation_errors':relocation},indent=2))
    return report

if __name__=='__main__':main()
