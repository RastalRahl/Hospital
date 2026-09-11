"""D4 proposed cutaway geometry. Only the named reference workspace is written."""
from __future__ import annotations

import json
import zipfile
from PIL import Image, ImageDraw
import validate_architecture_d0 as d0
import validate_architecture_d1 as d1
import validate_architecture_d2 as history
import validate_architecture_d2_v2 as side
import validate_architecture_d2_appearance as d2app
import validate_architecture_d3 as d3
import validate_architecture_d3_appearance as d3app
from rastalr_pipeline.geometry import evidence, alpha_region, anchored_component
from rastalr_pipeline.snapshot import compare_snapshots

ROOT = d0.ROOT
PREFIX = 'references/architecture/master_validation_D4_v1/'
OUT = ROOT / PREFIX
ART = OUT / 'artifacts'
STATUS = 'PROPOSED_FOR_HUMAN_GEOMETRY_REVIEW'
NAMES = ('main', 'repeat')


def contract():
    spec = d0.read_json(d0.CANON/'architecture_v2_spec.json')
    paths = [d0.CANON/n for n in ('front_wall_cutaway_1x.png', 'topology_ew.png', 'topology_ne.png', 'topology_nw.png')]
    paths += [ROOT/'assets/architecture'/f'hospital_front_wall_cutaway_{i:02}.png' for i in range(1,5)]
    measured = {p.relative_to(ROOT).as_posix(): {'size': list(d1.load(p).size), 'alpha_bbox': list(d1.load(p).getchannel('A').getbbox())} for p in paths}
    if spec['logical_grid_px'] != 32 or d1.load(paths[0]).size != (32,20) or d1.load(paths[1]).getchannel('A').getbbox() != (0,12,32,20):
        raise ValueError('Canonical grid/front geometry changed; stop for review')
    paths += [ROOT/'AGENTS.md', ROOT/'docs/ARCHITECTURE.md', ROOT/'docs/ART_DIRECTION.md', ROOT/'references/camera/rastalr_camera_reference_v1.png',
              d0.CANON/'architecture_v2_spec.json', ROOT/'metadata/production_batch_11_architecture_foundation.json', ROOT/'tools/build_architecture_foundation_batch_11_review.py',
              d1.CONTRACT_PATH, d2app.CONTRACT, d3app.CONTRACT]
    for app, report in ((d1,'d1_validation_report.json'), (d2app,'d2_appearance_validation_report.json'), (d3app,'d3_appearance_validation_report.json')):
        p = app.OUT/report
        if d0.read_json(p)['status'] != 'PASS': raise ValueError('Required appearance validation is not PASS')
        paths.append(p)
    paths += [d1.PACKAGE/'candidate'/d1.VIEW_FILES[n] for n in NAMES]
    paths += [app.PACKAGE/'candidate'/f'{app.STEM}{n}_native.png' for app in (d2app,d3app) for n in d3.NAMES]
    views = {}
    for name in NAMES:
        terminal = name == 'main'
        views[name] = {'size':[32,12], 'source_size':[256,96], 'envelope':[0,0,32,12],
            'origin':[0,12], 'cell_anchor':[16,16], 'image_anchor':[16,4],
            'frame':[[0,0,32,4],[0,10,32,12],[0,4,4,10]] + ([[28,4,32,10]] if terminal else []),
            'pane':[[4,4,28 if terminal else 32,10]], 'exterior':[],
            'contacts':{'upper_trim':[0,0,32,4], 'lower_rail':[0,10,32,12], 'left_post':[0,0,4,12]}}
    return {'id':'hospital_glass_partition_front_cutaway_01', 'status':STATUS, 'rectangle_convention':'[left, top, right, bottom)',
        'canonical_requirements':{'grid':32,'scale':8,'camera':spec['projection'],'ground_strip':[0,12,32,20],
            'front_solid_rendering_convention':spec['rendering_layers']['front_south_wall'],
            'normalization':'architecture_grid_preserving','footprint':[1,1],'interior':'north/above','stride':[32,0]},
        'measured_sources':{'method':'Saved PNG dimensions and nonzero-alpha bounds; metadata below is quoted, not pixel measurement','pngs':measured,
            'batch11_metadata':'Front01 crop [256,768,512,928)/8 =>32x20; four variants share dimensions. Review builder uses x32+32*c,y160; sides y52+32*r end180. Those absolute scene coordinates are not D4 anchors.',
            'side_terminal':'Validated main bodies are12x32 with last4 rows fully opaque. Corner bodies have24px north extension, retaining the same terminal support. Actual assembly scans verify these observations.'},
        'derived_geometry':{'side_south_endpoint':'side cell north center + [0,32*depth]; call its y coordinate S. The final side support occupies [S-4,S).',
            'D4_cell':'[west,S-16]; image origin cell+[0,12]=[west,S-4]; image anchor=cell anchor-origin=[16,4]',
            'centerline_image_y':4,'ground_strip_image':[0,0,32,8], 'visible_base_exclusive_image_y':12,
            'scene_edges':'Upper trim begins S-4 and ends S; pane [S,S+6); bottom rail [S+6,S+8); visual base S+8. Ground strip is [S-4,S+4), NOT the image base.',
            'endpoints_cell':[[0,16],[32,16]],'endpoints_image':[[0,4],[32,4]],
            'source_rule':'Every coordinate times8, nearest-neighbor only, no trim/padding/warp.'},
        'proposed_choices':{'visible_height':12,'upper_trim_depth':4,'front_face_height':8,'pane_height':6,'lower_rail_height':2,
            'rationale':'Retain the canonical top-trim plus foreground-face organization, but use the existing shallow side terminal support depth4 for trim and a minimal8px glass face (6px pane +2px lower rail). This is an orientation-specific low cutaway proposal, not the solid wall20px canvas or a new physical height. D1 installed height and D2/D3 north-return design remain unchanged.',
            'endpoint_shoulders':'Unchanged side supports project4px outside each D4 endpoint; the front face turns inward to its4px terminal post. This deliberate stepped silhouette is exposed for review.',
            'frame_rgba':list(side.FRAME),'pane_rgba':list(side.GLASS),
            'representation':'Two mutually exclusive views of ONE future logical asset; no separate visible corner component and no assembly masks.',
            'repeat':'Each cell owns its left4px support. Main owns the closing right4px support; repeat extends its declared pane to x32. This follows explicit D4 region ownership, not a copied D1 pixel-column rule.',
            'ground_caps':'D4 owns a technical8x4 south half-strip cap at each corner centered on the endpoint. It completes canonical NE/NW ground elbows only; it is not rendered artwork or inventory.'},
        'views':views,'alpha_policy':{'frame':255,'pane':150,'all_other_pixels':0},
        'front_corner_contract':{'southwest_overlap_relative_to_intersection':[0,-4,8,0], 'southeast_overlap_relative_to_intersection':[-8,-4,0,0],
            'expected_overlap_reason':'Each side terminal support is12x4; D4 trim intersects its8px inward section. Each intersection is8*4=32 opaque pixels. Measure each separately.',
            'side_view_selection':'Depth1 corner_main; greater depths corner_repeat, then repeat, ending main. Never suppress the terminal to hide a join.',
            'draw_order':['approved separate floor','separate test object','validated D2','validated D3','validated D1','D4'],
            'ownership':'D4 upper trim owns the visible pixels in the two32px opaque contacts; unchanged side supports retain outer4px shoulders. No translucent intersection is permitted.',
            'allowed_hidden_glass':0,'allowed_stacked_glass':0,'allowed_unexpected_overlap':0,'masks':[]},
        'human_visual_review':{'status':'PENDING','approval':False,'review':['12px front cutaway balance','6px pane readability','both4px endpoint shoulders','foreground face relative to side cutaways'],
            'limits':'Closed enclosure is connection evidence, not a room with an entrance; no all-direction junction claim.'},
        'sources_sha256':{p.relative_to(ROOT).as_posix():d0.digest(p) for p in paths}}


def saved(path, im):
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)
    return d1.load(path)


def assemble(views, count, stride=32, duplicate=False):
    run = Image.new('RGBA',(count*32,12)); coverage = Image.new('I',run.size); origins=[]
    for i in range(count):
        im = views['main' if i==count-1 else 'repeat']; origin=(i*stride,0); origins.append(list(origin))
        run.alpha_composite(im,origin)
        for y in range(im.height):
            for x in range(im.width):
                xx=x+origin[0]
                if 0<=xx<run.width and 0<im.getpixel((x,y))[3]<255: coverage.putpixel((xx,y),coverage.getpixel((xx,y))+1)
    if duplicate:
        pane=views['main'].crop((4,4,28,10)); run.alpha_composite(pane,(4,4))
        for y in range(4,10):
            for x in range(4,28): coverage.putpixel((x,y),coverage.getpixel((x,y))+1)
    return run,origins,coverage


def check_run(run, origins, coverage, count):
    checks={'size':evidence([count*32,12],list(run.size),'Reload run dimensions'),
            'origins':evidence([[32*i,0] for i in range(count)],origins,'Recorded actual blit origins')}
    if run.size!=(count*32,12): return d1.group(checks)
    errors={'frame':0,'pane':0}; spans=[]; start=None
    for x in range(run.width):
        opaque=run.getpixel((x,6))[3]==255
        if opaque and start is None: start=x
        if not opaque and start is not None: spans.append([start,x]);start=None
        for y in range(12):
            role='frame' if y<4 or y>=10 or x%32<4 or x>=run.width-4 else 'pane'
            errors[role]+=run.getpixel((x,y))[3]!=(255 if role=='frame' else 150)
    if start is not None: spans.append([start,run.width])
    for role,n in errors.items(): checks[role]=evidence(0,n,'Independent run alpha predicate for trim, rails, supports and pane')
    checks['support_spans']=evidence([[32*i,32*i+4] for i in range(count)]+[[run.width-4,run.width]],spans,'Scan contiguous opaque spans at image y6')
    checks['single_layer']=evidence(1,max(coverage.get_flattened_data()),'Count actual translucent draw contributions')
    return d1.group(checks)


def overlap(first, second, expected_rects):
    expected={(x,y) for l,t,r,b in expected_rects for y in range(t,b) for x in range(l,r)}
    actual=set(); opaque=intentional=stacked=hidden=0
    for y in range(first.height):
        for x in range(first.width):
            a,b=first.getpixel((x,y))[3],second.getpixel((x,y))[3]
            if a and b:
                actual.add((x,y));opaque+=a==b==255
                intentional+=a==b==255 and (x,y) in expected
                stacked+=0<a<255 and 0<b<255
                hidden+=(a==255 and 0<b<255) or (b==255 and 0<a<255)
    values={'intentional_opaque':intentional,'unexpected_opaque':opaque-intentional,'unexpected_overlap':len(actual-expected),'missing_contact':len(expected-actual),'stacked_glass':stacked,'hidden_glass':hidden}
    checks={k:evidence(len(expected) if k=='intentional_opaque' else 0,v,'Count pairwise RGBA alpha classes and exact declared contact-set difference') for k,v in values.items()}
    return d1.group(checks,computed=values,derived={'expected_rectangles':expected_rects})


def front_corner(front, vertical, edge, south, right, cell, origin):
    rect=[edge-8 if right else edge,south-4,edge if right else edge+8,south]
    side_rect=[edge-8 if right else edge-4,south-4,edge+4 if right else edge+8,south]
    probe=edge-1 if right else edge
    side_ys=[y for y in range(vertical.height) if vertical.getpixel((probe,y))[3]]
    front_ys=[y for y in range(front.height) if front.getpixel((probe,y))[3]]
    observed_end=max(side_ys)+1 if side_ys else None
    observed_trim=min(front_ys) if front_ys else None
    observed_base=max(front_ys)+1 if front_ys else None
    checks={'placement':evidence([cell[0],cell[1]+12],list(origin),'Actual blit origin compared to cell-to-image anchor mapping'),
        'centerline_registration':evidence(south,cell[1]+16,'Recorded front cell center versus side logical south endpoint'),
        'side_terminal_edge':evidence(south,observed_end,'Scan nonzero side alpha at corner probe; exclusive edge'),
        'upper_trim_edge':evidence(south-4,observed_trim,'Scan first front alpha at endpoint post'),
        'front_base_edge':evidence(south+8,observed_base,'Scan last front alpha plus1, distinct from centerline'),
        'side_support':alpha_region(vertical,side_rect,minimum=255,maximum=255),
        'front_contact':alpha_region(front,rect,minimum=255,maximum=255),
        'overlap':overlap(front,vertical,[rect])}
    return d1.group(checks,computed={'side_base_exclusive':observed_end,'front_top':observed_trim,'front_base_exclusive':observed_base},
        derived={'intersection':[edge,south],'ground_edges_y':[south-4,south+4],'front_contact':rect,'side_terminal':side_rect,
                 'front_cell':list(cell),'front_origin':list(origin),'image_anchor':[16,4]},conformance_to=STATUS)


def enclosure(views, width=4, depth=2, delta=(0,0), defect=None, label=None, *, artifact_dir=ART, resolved_runs=None):
    x0=64+delta[0]; top=36+delta[1]; north=top+24; east=x0+32*width; south=north+32*depth
    size=(east+48,south+56); cell=[x0,south-16]; origin=[x0,south-4]
    if defect=='anchor_1px': origin[1]+=1
    if defect=='baseline_confusion': cell[1]+=4;origin[1]+=4
    if resolved_runs is None:
        dm=d1.load(d1.PACKAGE/'candidate'/d1.VIEW_FILES['main']);dr=d1.load(d1.PACKAGE/'candidate'/d1.VIEW_FILES['repeat'])
        back,_,_=d1.assemble(dm,dr,width)
        left,_,_=side.assemble({n:d2app.candidate(n) for n in d3.NAMES},depth,corner=True)
        right,_,_=side.assemble({n:d3app.candidate(n) for n in d3.NAMES},depth,corner=True)
        front,pp,coverage=assemble(views,width)
    else:
        back,left,right,front=[resolved_runs[n][0] for n in ('d1','d2','d3','d4')]
        _,placements,coverage,origin=resolved_runs['d4'];cell=placements[0]['cell']
        pp=[[p['origin'][j]-origin[j] for j in range(2)] for p in placements]
    if defect=='missing_contact': front.putpixel((6,2),(0,0,0,0))
    if defect=='wrong_side_terminal':
        wrong={n:d3app.candidate(n) for n in d3.NAMES};wrong['main']=wrong['repeat'];wrong['corner_main']=wrong['corner_repeat']
        right,_,_=side.assemble(wrong,depth,corner=True)
    sources={'d1':(back,[x0,top]),'d2':(left,[x0-4,top]),'d3':(right,[east-8,top]),'d4':(front,origin)}
    if resolved_runs is not None:
        sources={n:(r[0],r[3]) for n,r in resolved_runs.items()}
    layers={};clip=0
    for name,(im,pos) in sources.items():
        layer=Image.new('RGBA',size);layer.alpha_composite(im,tuple(pos));layers[name]=layer
        clip+=sum(a[3]>0 and not(0<=x+pos[0]<size[0] and 0<=y+pos[1]<size[1]) for y in range(im.height) for x in range(im.width) for a in [im.getpixel((x,y))])
        if label: layers[name]=saved(artifact_dir/f'{label}_{name}_layer.png',layer)
    structure=Image.new('RGBA',size)
    for name in ('d2','d3','d1','d4'):structure.alpha_composite(layers[name])
    bg=Image.new('RGBA',size,(225,226,213,255));floor=d1.load(ROOT/'assets/architecture/hospital_floor_plain_01.png')
    for y in range(north,south+16,32):
        for x in range(x0,east,32): bg.alpha_composite(floor,(x,y))
    obj=Image.new('RGBA',size);obj.paste((245,183,34,255),(x0+10,south-12,x0+22,south+8))
    if label:
        structure=saved(artifact_dir/f'{label}_structure.png',structure);bg=saved(artifact_dir/f'{label}_background.png',bg);obj=saved(artifact_dir/f'{label}_object_layer.png',obj)
    clean=Image.alpha_composite(bg,structure);with_obj=Image.alpha_composite(Image.alpha_composite(bg,obj),structure)
    checks={
        'southwest':front_corner(layers['d4'],layers['d2'],x0,south,False,cell,origin),
        'southeast':front_corner(layers['d4'],layers['d3'],east,south,True,[cell[0]+32*(width-1),cell[1]],[origin[0]+32*(width-1),origin[1]]),
        'northwest':d3.corner_check(layers['d1'],layers['d2'],structure,x0,north+4,False,[x0-16,north],[x0-4,top]),
        'northeast':d3.corner_check(layers['d1'],layers['d3'],structure,east,north+4,True,[east-16,north],[east-8,top]),
        'front_run':check_run(front,pp,coverage,width),
        'clipped_nonzero_pixels':evidence(0,clip,'Check each source nonzero pixel against actual composed canvas'),
        'D1_final_pixels':anchored_component(structure,back,(x0,top),(x0,top)),
        'D4_final_pixels':anchored_component(structure,front,(x0,south-4),tuple(origin)),
        'front_back_overlap':overlap(layers['d4'],layers['d1'],[]), 'side_side_overlap':overlap(layers['d2'],layers['d3'],[])}
    for name,(im,pos) in sources.items():checks[name+'_layer_exact']=anchored_component(layers[name],im,tuple(pos),tuple(pos))
    responses=total=0
    for y in range(size[1]):
        for x in range(size[0]):
            if 0<layers['d4'].getpixel((x,y))[3]<255 and obj.getpixel((x,y))[3]:
                total+=1;responses+=clean.getpixel((x,y))!=with_obj.getpixel((x,y))
    checks['object_response']=evidence(total,responses,'Compare object toggled on/off through actual D4 pane pixels')
    checks['object_hits_pane']=evidence(True,total>0,'Require nonempty object/pane intersection')
    # Ground masks are independently checked against canonical elbow rasters.
    ground=Image.new('RGBA',size)
    for rect in ([x0,north-4,east,north+4],[x0-4,north-4,x0+4,south],[east-4,north-4,east+4,south],[x0,south-4,east,south+4],
                 [x0-4,south,x0+4,south+4],[east-4,south,east+4,south+4]): ground.paste((82,110,136,255),rect)
    for name,cx,cy,mask in [('southwest',x0,south,'ne'),('southeast',east,south,'nw'),('northwest',x0,north,'se'),('northeast',east,north,'sw')]:
        required=Image.new('RGBA',size);required.alpha_composite(d1.load(d0.CANON/f'topology_{mask}.png'),(cx-16,cy-16))
        checks[name+'_ground']=evidence(0,sum(a[3]>0 and b[3]==0 for a,b in zip(required.get_flattened_data(),ground.get_flattened_data())),'Compare separate ground mask with canonical elbow pixels')
        if label:saved(artifact_dir/f'{label}_{name}_required_ground.png',required)
    if label:
        saved(artifact_dir/f'{label}_ground.png',ground);clean=saved(artifact_dir/f'{label}_clean.png',clean);saved(artifact_dir/f'{label}_object_composite.png',with_obj)
    return d1.group(checks,derived={'size_cells':[width,depth],'west':x0,'east':east,'north_centerline':north,'south_centerline':south,
        'D1_origin':[x0,top],'D2_origin':[x0-4,top],'D3_origin':[east-8,top],'D4_cell':cell,'D4_origin':origin},
        computed={'object_pane_samples':total,'object_responses':responses}),clean,structure


def negative_controls(views):
    cases={};run,p,cov=assemble(views,2);good=check_run(run,p,cov,2)
    def add(name,im,pp,cc,key):
        bad=check_run(im,pp,cc,2);cases[name]={'image':im,'validation':bad,'valid_control_pass':good['pass'],'intended_check':key,'proven':good['pass'] and not bad['checks'][key]['pass']}
    im,pp,cc=assemble(views,2,stride=33);add('repeat_displacement',im,pp,cc,'origins')
    for name,point,alpha,key in [('broken_frame',(6,1),0,'frame'),('opaque_glass',(6,6),255,'pane'),('pane_hole',(6,6),0,'pane')]:
        im=run.copy();im.putpixel(point,(*im.getpixel(point)[:3],alpha))
        if name=='opaque_glass':
            for y in range(im.height):
                for x in range(im.width):
                    rgba=im.getpixel((x,y))
                    if 0<rgba[3]<255:im.putpixel((x,y),(*rgba[:3],255))
        add(name,im,p,cov,key)
    for name,replacement in [('doubled_support',{'repeat':views['main']}),('wrong_terminal',{'main':views['repeat']})]:
        im,pp,cc=assemble({**views,**replacement},2);add(name,im,pp,cc,'support_spans')
    im,pp,cc=assemble(views,2,duplicate=True);add('stacked_glass',im,pp,cc,'single_layer')
    valid,_,_=enclosure(views,2,1)
    for name,corner,key in [('anchor_1px','southwest','placement'),('baseline_confusion','southwest','centerline_registration'),('missing_contact','southwest','front_contact'),('wrong_side_terminal','southeast','side_support')]:
        q,im,_=enclosure(views,2,1,defect=name);bad=q['checks'][corner]
        cases[name]={'image':im,'validation':bad,'valid_control_pass':valid['pass'],'intended_check':key,'proven':valid['pass'] and not bad['checks'][key]['pass']}
    c=contract();im=views['main'];export=im.resize((256,96),Image.Resampling.NEAREST);valid_file=side.check_view(im,export,c,'main')
    export.putpixel((0,0),(1,2,3,255));bad=side.check_view(im,export,c,'main')
    cases['source_subpixel']={'image':export,'validation':bad,'valid_control_pass':valid_file['pass'],'intended_check':'blocks','proven':valid_file['pass'] and not bad['checks']['blocks']['pass']}
    return cases


def failures(value,path=''):
    result=[]
    if isinstance(value,dict):
        if value.get('pass') is False and 'expected' in value: result.append({'check':path,**value})
        for key,v in value.items():result+=failures(v,path+'/'+str(key))
    return result


def main():
    ART.mkdir(parents=True,exist_ok=True);c=contract();path=OUT/'d4_geometry_alpha_contract_proposed.json'
    if path.exists() and d0.read_json(path)!=c:raise ValueError('Existing proposed contract differs; no silent revision')
    d0.write_json(path,c);views={};files={}
    for name in NAMES:
        views[name]=saved(OUT/f'd4_{name}_native.png',side.raster(c,name))
        export=saved(OUT/f'd4_{name}_source_8x.png',views[name].resize((256,96),Image.Resampling.NEAREST))
        files[name]=side.check_view(views[name],export,c,name)
    # Establish both local front corners before the larger reconstruction.
    local,scene,_=enclosure(views,2,1,label='local_corners')
    for name,right in [('southwest',False),('southeast',True)]:
        g=local['derived'];edge=g['east'] if right else g['west'];sy=g['south_centerline']
        crop=[edge-16,sy-20,edge+20,sy+16];clean=saved(ART/f'{name}_clean.png',scene.crop(crop))
        anno=clean.resize((288,288),Image.Resampling.NEAREST);draw=ImageDraw.Draw(anno)
        draw.line((0,160,287,160),fill=(240,170,32,255),width=2);draw.line((128,0,128,287),fill=(240,170,32,255),width=2)
        draw.line((0,224,287,224),fill=(232,53,140,255),width=2)
        l,t,r,b=local['checks'][name]['derived']['front_contact'];draw.rectangle(((l-crop[0])*8,(t-crop[1])*8,(r-crop[0])*8-1,(b-crop[1])*8-1),outline=(48,220,155,255),width=2)
        side.labeled_panel(anno,name+' proposed connection',[
            f'Gold ground center ({edge},{sy}); strip y{sy-4}..{sy+4}.',
            f'Trim y{sy-4}..{sy}; pane y{sy}..{sy+6}; pink base {sy+8}.',
            'Green: exact 8x4 opaque contact; retained outer4px shoulder.',
            f'D4 cell {local["checks"][name]["derived"]["front_cell"]}; origin {local["checks"][name]["derived"]["front_origin"]}; anchor [16,4].',
            'D4 on top of unchanged terminal side support; no masks.'],factor=1).save(ART/f'{name}_annotated.png')
    runs={};transmission={}
    for count in (1,2,4):
        run,p,cov=assemble(views,count);run=saved(ART/f'run_{count}_native.png',run);saved(ART/f'run_{count}_glass_coverage.png',cov.convert('L'))
        runs[str(count)]=check_run(run,p,cov,count)
        selected=sum(d1.pixel_difference(run.crop((32*i,0,32*i+32,12)),views['main' if i==count-1 else 'repeat']) for i in range(count))
        runs[str(count)]['checks']['selected_rgba']=evidence(0,selected,'Compare saved run cells to actual selected RGBA view')
        runs[str(count)]['pass'] &= selected==0
        q,backs,obj,scenes=side.transmission(run);transmission[str(count)]=q
        for name,bg in backs.items():saved(ART/f'run_{count}_{name}_background.png',bg);saved(ART/f'run_{count}_{name}_composite.png',scenes[name])
        saved(ART/f'run_{count}_object_layer.png',obj)
    enclosures={}
    for name,w,d,delta in [('original',4,2,(0,0)),('relocated',4,2,(32,32)),('additional_size',3,3,(0,0))]:
        enclosures[name],_,_=enclosure(views,w,d,delta,label='enclosure_'+name)
    original=d1.load(ART/'enclosure_original_structure.png');moved=d1.load(ART/'enclosure_relocated_structure.png')
    relocation=d1.group({'translated_structure':evidence(0,d1.pixel_difference(original,moved.crop((32,32,32+original.width,32+original.height))),'Compare independently rendered saved structures after removing +32,+32 translation')})
    neg=negative_controls(views)
    for name,q in neg.items():saved(ART/f'broken_{name}.png',q['image'])
    panels=[side.row([d1.load(ART/'southwest_annotated.png'),d1.load(ART/'southeast_annotated.png')]),
        side.row([side.labeled_panel(d1.load(ART/f'{n}_clean.png'),n+' clean / actual saved files',factor=8) for n in ('southwest','southeast')]),
        side.labeled_panel(d1.load(ART/'enclosure_original_object_composite.png'),'D1/D2/D3 validated appearance + proposed D4 / separate gold test object',factor=4),
        side.row([side.labeled_panel(views[n],'D4 '+n+' flat scaffold / 32x12',factor=8) for n in NAMES]),
        side.stack([side.labeled_panel(d1.load(ART/f'run_{n}_colored_composite.png'),f'{n} cells / 32px stride / single glass layer',factor=4) for n in (1,2,4)]),
        side.stack([side.row([side.labeled_panel(d1.load(ART/f'run_1_{n}_composite.png'),n+' separate background',factor=6) for n in pair]) for pair in (('light','dark'),('colored','object'))]),
        side.row([side.labeled_panel(d1.load(ART/f'enclosure_{n}_clean.png'),n.replace('_',' '),factor=2) for n in ('relocated','additional_size')])]
    side.stack(panels).save(ART/'d4_geometry_review_montage.png')
    side.stack([side.labeled_panel(views[n],n+': trim y0..4, pane y4..10, base y10..12; anchors in contract',factor=8) for n in NAMES]).save(ART/'geometry_alpha_diagnostic.png')
    preservation=compare_snapshots(d0.read_json(OUT/'production_before.json'),history.snapshot(),allowed_addition_prefixes=(PREFIX,))
    report={'contract_status':STATUS,'files':files,'local_corners':local,'runs':runs,'transmission':transmission,'enclosures':enclosures,'relocation':relocation,
        'negative_controls':{n:{k:v for k,v in q.items() if k!='image'} for n,q in neg.items()},'preservation':preservation,
        'human_visual_review':c['human_visual_review']}
    blockers=failures({k:report[k] for k in ('files','local_corners','runs','transmission','enclosures','relocation')})
    for name,q in neg.items():
        if not q['proven']:blockers.append({'check':'negative/'+name,'reason':'Valid failed or broken fixture escaped'})
    if not preservation['pass']:blockers.append({'check':'preservation','details':preservation})
    if (OUT/'test_results.json').exists():
        report['tests']=d0.read_json(OUT/'test_results.json')
        if report['tests']['exit_code']!=0:blockers.append({'check':'complete_suite','details':report['tests']})
    if (OUT/'visual_review.json').exists():report['assistant_visual_review']=d0.read_json(OUT/'visual_review.json')
    report.update(status='PASS' if not blockers else 'FAIL',recommendation='READY FOR HUMAN GEOMETRY REVIEW' if not blockers else 'GEOMETRY BLOCKED',blockers=blockers)
    d0.write_json(OUT/'d4_geometry_report.json',report);d0.write_json(OUT/'production_preservation.json',preservation)
    lines=['# D4 front cutaway geometry proposal','',f"**{report['recommendation']}**. Computed conformance {report['status']} to `{STATUS}`; no human approval.",'',
        'Canonical:32px grid,8px centered ground strip, axis-aligned oblique camera, shallow foreground cutaway and integer8x export. Canonical solid front wall measures32x20 (8px trim +12px face). This is context, not D4 canvas authority.','',
        'Proposed D4:32x12 RGBA /256x96 source; main and repeat are mutually exclusive views of one future asset. Native envelope[0,0,32,12), footprint1x1, cell anchor[16,16], image anchor[16,4], relative origin[0,12], stride[32,0]. Frame255, pane150, undeclared exterior0 (no exterior pixels within this tight carrier). No trim, padding, rotated artwork or masks.','',
        'Corner-first derivation: side south center S is its terminal support exclusive edge; terminal support spans[S-4,S). D4 trim occupies that same4px band. The proposed8px front face below S contains6px pane and2px lower rail. Thus image top S-4, ground center S, strip bottom S+4, image base S+8 are distinct. The12px carrier is a proposed foreground cutaway, not a change to installed physical height. Side north returns retain their existing24px drop.','',
        'Ownership: each horizontal cell owns its left4px post; only main owns the right closing4px post. Repeat declares pane through x32. Side final main views retain their12x4 terminal support. D4 trim intersects each inward8x4 section; side outer4px shoulders remain visible. D4 draws over those opaque contacts only; no side glass is erased. Technical8x4 ground half-strip caps complete NE/NW elbow topology without visible components.','',
        'Each reconstruction uses actual saved D4 files, validated D1 main/repeat, validated D2/D3 corner_repeat then main (or corner_main for depth1), unchanged approved floor and separate object. Layers: floor, object, D2, D3, D1, D4. No entry opening is implied.','']
    for name,q in enclosures.items():
        lines.append(f"{name} size {q['derived']['size_cells']}: conformance {q['pass']}; object samples/responses {q['computed']}.")
        for corner in ('southwest','southeast'):
            lines.append(f"- {corner}: observed {q['checks'][corner]['computed']}; overlap {q['checks'][corner]['checks']['overlap']['computed']}.")
        for corner in ('northwest','northeast'):lines.append(f"- {corner} retained: {q['checks'][corner]['computed']}.")
    lines+=['',f"Original/relocated structure comparison: {relocation}. Runs1/2/4 and separate light/dark/colored/toggled-object transmission all independently checked.",'','## Negative controls','']
    for n,q in neg.items():lines.append(f"- {n}: passing valid control {q['valid_control_pass']}; intended `{q['intended_check']}` failure proven {q['proven']}.")
    lines+=['',f"Protected historical files {preservation['protected_file_count']}; changed {preservation['changed']}; missing {preservation['missing']}. Production before/after: {preservation['expected_counts']} / {preservation['observed_counts']}.",'',
        'Safeguards permit only new D4 workspace files; existing hashes remain mandatory even within allowed directories. No historical baseline is refreshed.','',
        'Reproduce: `python tools/validate_architecture_d4.py`. Complete suite: `python -m pytest -q`; recorded prior baseline237.']
    if 'tests' in report:lines+=['',f"Captured complete suite: {report['tests']}."]
    lines+=['',f"Blockers: {blockers}",'','Pending human geometry review:6px front-pane legibility, foreground height and exposed4px shoulders. This is a deliberately stylized cutaway, not final appearance or a continuous equal-height rail. No assets or approval records changed; no ingestion, Batch13, D5 or other junction work.','']
    (OUT/'d4_geometry_report.md').write_text('\n'.join(lines),encoding='utf-8')
    names=['d4_geometry_alpha_contract_proposed.json','d4_geometry_report.json','d4_geometry_report.md']+[f'd4_{n}_{s}.png' for n in NAMES for s in ('native','source_8x')]
    names += ['artifacts/'+n+'.png' for n in ('southwest_clean','southwest_annotated','southeast_clean','southeast_annotated','enclosure_original_object_composite','enclosure_relocated_clean','enclosure_additional_size_clean','d4_geometry_review_montage')]
    for n in ('README.md','test_results.json','test_results.txt','visual_review.json'):
        if (OUT/n).exists():names.append(n)
    with zipfile.ZipFile(OUT/'d4_geometry_review_bundle.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
        for n in sorted(names):
            info=zipfile.ZipInfo(n,date_time=(2026,9,11,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,(OUT/n).read_bytes())
    print(json.dumps({'status':report['status'],'blockers':blockers,'protected':preservation['protected_file_count'],'counts':preservation['observed_counts']},indent=2))
    return 0 if not blockers else 1


if __name__=='__main__':raise SystemExit(main())
