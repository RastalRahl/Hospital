"""Deterministic D2 cutaway-return proposal. Writes only the new v2 workspace."""
from __future__ import annotations

from collections import Counter
import json
import zipfile
from PIL import Image, ImageDraw, ImageFont
import validate_architecture_d0 as d0
import validate_architecture_d1 as d1
import validate_architecture_d2 as v1
from rastalr_pipeline.geometry import evidence, alpha_region, anchored_component
from rastalr_pipeline.snapshot import compare_snapshots

ROOT = d0.ROOT
OUT = ROOT / 'references/architecture/master_validation_D2_v2'
ART = OUT / 'artifacts'
PREFIX = 'references/architecture/master_validation_D2_v2/'
STATUS = 'PROPOSED_FOR_HUMAN_GEOMETRY_REVIEW'
FRAME = (39, 55, 70, 255)
GLASS = (158, 205, 216, 150)


def contract():
    old = d0.read_json(v1.CONTRACT)
    sources = dict(old['sources_sha256'])
    for p in (v1.CONTRACT, v1.OUT/'d2_geometry_report.json', v1.OUT/'artifacts/d1_d2_corner_scene.png'):
        sources[p.relative_to(ROOT).as_posix()] = d0.digest(p)
    side = d1.load(d0.CANON/'side_wall_left_1x.png')
    glass = d1.load(d0.CANON/'glass_partition_1x.png')
    return {
        'id': 'hospital_glass_partition_side_left_01', 'revision': 2, 'status': STATUS,
        'rectangle_convention': '[left, top, right, bottom)',
        'canonical_requirements': {'grid':32, 'scale':8, 'ground_strip':[12,0,20,32],
            'camera':'rectangular-grid RPG oblique; axis-aligned ground; orientation-aware shallow side',
            'normalization':'architecture_grid_preserving', 'D1_unchanged':True},
        'measured_sources': {'method':'Read saved PNG sizes and alpha bounds',
            'canonical_side_size':list(side.size), 'canonical_side_envelope':list(side.getchannel('A').getbbox()),
            'canonical_glass_size':list(glass.size)},
        'proposed_presentation': {
            'type':'Explicit stylized cutaway with glazed upright north return; not a continuous equal-height side rail',
            'reason':'v1 placed a shallow band at the back-wall base with no visible upper connection. v2 exposes the cutaway with a return cheek touching both the D1 upper frame and the side cap.',
            'orientation':'left/west room boundary; room interior east/right; repeat south/+y',
            'logical_footprint':[1,1], 'visible_width':12,
            'width_reason':'8 px topology strip plus a proposed 4 px inward shallow face; replaces the unapproved 14 px height-ratio heuristic. No physical camera equation is claimed.',
            'frame_width':2, 'support_depth':4,
            'return_reason':'A 4 px wide side-facing return cheek, matching D1 post width, carries a 2 px glazed reveal and 2 px outer frame. It belongs to D2, adjacent to the unchanged D1 upright post. Its cap reaches 4 px over that opaque post.',
            'cutaway':'The full-height north return starts at D1 top, then drops 24 screen pixels to the shallow side cap at the ground centerline. This is deliberate orientation-dependent cutaway geometry, not a statement that the actual partition height drops.',
            'human_review_required':['2 px return glass legibility','deliberate abrupt 24 px cutaway','12 px side width and frame balance','material continuity with D1 after future appearance work'],
            'approval':False},
        'views': {
            'main': {'size':[12,32], 'envelope':[0,0,12,32], 'origin':[12,0], 'image_anchor':[4,16], 'cell_anchor':[16,16],
                'frame':[[0,0,2,32],[10,0,12,32],[2,0,10,4],[2,28,10,32]], 'pane':[[2,4,10,28]]},
            'repeat': {'size':[12,32], 'envelope':[0,0,12,32], 'origin':[12,0], 'image_anchor':[4,16], 'cell_anchor':[16,16],
                'frame':[[0,0,2,32],[10,0,12,32],[2,0,10,4]], 'pane':[[2,4,10,32]]},
            'corner_main': {'size':[12,56], 'envelope':[0,0,12,56], 'origin':[12,-24], 'image_anchor':[4,40], 'cell_anchor':[16,16],
                'frame':[[0,0,8,4],[0,4,2,24],[0,24,12,28],[0,28,2,56],[10,28,12,56],[2,52,10,56]],
                'pane':[[2,4,4,24],[2,28,10,52]]},
            'corner_repeat': {'size':[12,56], 'envelope':[0,0,12,56], 'origin':[12,-24], 'image_anchor':[4,40], 'cell_anchor':[16,16],
                'frame':[[0,0,8,4],[0,4,2,24],[0,24,12,28],[0,28,2,56],[10,28,12,56]],
                'pane':[[2,4,4,24],[2,28,10,56]]}},
        'alpha_policy':{'frame':255,'pane':150,'all_other_pixels':0,'outside_envelope':0},
        'derived_mapping': {
            'D1_cell_example':[64,44], 'D1_render_origin':[64,36],
            'D1_centerline_y':60, 'D1_base_exclusive_y':64, 'D1_top_y':36,
            'intersection':[64,60], 'D2_cell_example':[48,60], 'D2_corner_origin':[60,36],
            'D2_straight_origin':[60,60],
            'calculation':'D1 cell y44 + center16 =60; base44+20=64; top44-8=36. D2 north axis is cell+[16,0]. Return top offset=36-60=-24. Cell anchor minus origin gives image anchor [4,40].',
            'endpoints':'D2 north center [16,0], south center [16,32]; north contact cap reaches y=4 (the D1 base edge). The image upper return is not the ground endpoint.',
            'source_rule':'Every native coordinate and size multiplied exactly by 8; no trim, padding, warp, rotation or transpose.'},
        'repeat': {'stride':[0,32], 'ownership':'Every cell owns north support. Only final cell owns south support. First cell may use corner adjacency view; mutually exclusive with main/repeat. No extra logical asset.',
            'corner_carrier_overlap':'Corner carrier extends north by24; subsequent cells still begin every32 at their ground origins. Carrier padding is not added; bounds enclose declared visible geometry.'},
        'corner_contract': {
            'top_contact_D2_image':[4,0,8,4], 'D1_post_local':[0,0,4,4],
            'return_glass_D2_image':[2,4,4,24], 'return_outer_frame':[0,0,2,28],
            'shallow_cap_D2_image':[0,24,12,28],
            'expected_opaque_overlap_scene':[[64,36,68,40],[64,60,72,64]],
            'layer_order':['separate background','D2 corner/run','unchanged D1'],
            'occlusion':'D1 opaque post hides 4x4 of D2 return cap; D1 opaque base hides 8x4 of the side cap. These are the only overlaps. No translucent surface may be drawn twice.',
            'assembly_mask':'none; D1 pixels and alpha remain untouched',
            'ground_elbow_ownership':[12,-4,20,32],
            'v1_mask_reassessment':'v1 began the NS strip at baseline y64 rather than center y60; its 4x8 missing quadrant mixed a 4px registration discrepancy with elbow ownership. v2 starts at center60, and D2 owns a half-strip cap to y56. Before that cap only the 4x4 NW quadrant is missing; cap completes it without a separate repair mask.',
            'testable_transition':'Required opaque return cap intersects D1 top post, the 2px glazed reveal is present, outer frame is connected down to the side cap, and side cap meets D1 base. All checked on saved layers plus assembly; ground coverage alone is insufficient.'},
        'sources_sha256':sources}


def raster(c, view):
    spec=c['views'][view]; im=Image.new('RGBA',tuple(spec['size']))
    for r in spec['pane']: im.paste(GLASS,tuple(r))
    for r in spec['frame']: im.paste(FRAME,tuple(r))
    return im


def check_view(im, source, c, view):
    spec=c['views'][view]; w,h=spec['size']
    checks={'mode':evidence('RGBA',im.mode,'Reload native PNG mode'),
        'size':evidence([w,h],list(im.size),'Reload native dimensions'),
        'source_mode':evidence('RGBA',source.mode,'Reload source PNG mode'),
        'source_size':evidence([w*8,h*8],list(source.size),'Reload source dimensions')}
    if not all(v['pass'] for v in checks.values()): return d1.group(checks)
    checks['blocks']=evidence(0,sum(source.getpixel((x,y))!=im.getpixel((x//8,y//8)) for y in range(h*8) for x in range(w*8)), 'Compare every source pixel with its native 8x8 block')
    checks['roundtrip']=evidence(0,d1.pixel_difference(im,source.resize(im.size,Image.Resampling.NEAREST)),'Lossless nearest-neighbor native roundtrip')
    checks['envelope']=evidence(spec['envelope'],list(im.getchannel('A').getbbox()),'Read saved nonzero-alpha envelope')
    covered=set()
    for role in ('frame','pane'):
        for i,r in enumerate(spec[role]):
            a=c['alpha_policy'][role]; checks[f'{role}_{i}']=alpha_region(im,r,minimum=a,maximum=a)
            covered.update((x,y) for y in range(r[1],r[3]) for x in range(r[0],r[2]))
    checks['exterior']=evidence(0,sum(im.getpixel((x,y))[3]!=0 for y in range(h) for x in range(w) if (x,y) not in covered),'Check undeclared pixels have zero alpha')
    return d1.group(checks,computed={'alpha_histogram':dict(Counter(im.getchannel('A').get_flattened_data())), 'envelope':list(im.getchannel('A').getbbox())},conformance_to=STATUS)


def assemble(views,n,corner=False,stride=32,duplicate=False):
    offset=24 if corner else 0
    run=Image.new('RGBA',(12,n*32+offset)); coverage=Image.new('I',run.size); origins=[]
    for i in range(n):
        name=('corner_' if corner and i==0 else '')+('main' if i==n-1 else 'repeat')
        im=views[name]; origin=(0,i*stride+(0 if corner and i==0 else offset)); origins.append(list(origin))
        run.alpha_composite(im,origin)
        for y in range(im.height):
            for x in range(im.width):
                p=(x,y+origin[1])
                if p[1]<run.height and 0<im.getpixel((x,y))[3]<255: coverage.putpixel(p,coverage.getpixel(p)+1)
    if duplicate:
        pane=views['main'].crop((2,4,10,28)); run.alpha_composite(pane,(2,offset+4))
        for y in range(offset+4,offset+28):
            for x in range(2,10): coverage.putpixel((x,y),coverage.getpixel((x,y))+1)
    return run,origins,coverage


def check_run(run,origins,layers,n):
    checks={'size':evidence([12,32*n],list(run.size),'Read saved run dimensions'),
        'origins':evidence([[0,32*i] for i in range(n)],origins,'Read actual draw coordinates')}
    errors={'frame':0,'pane':0}; stacked=0; spans=[]; start=None
    for y in range(32*n):
        support=y%32<4 or y>=32*n-4
        for x in range(12):
            frame=x<2 or x>=10 or support
            role='frame' if frame else 'pane'; a=run.getpixel((x,y))[3]
            errors[role]+=a!=(255 if frame else 150)
            if not frame: stacked+=layers.getpixel((x,y))!=1
        opaque=run.getpixel((6,y))[3]==255
        if opaque and start is None: start=y
        if not opaque and start is not None: spans.append([start,y]); start=None
    if start is not None: spans.append([start,32*n])
    for role,total in errors.items(): checks[role]=evidence(0,total,'Independent alpha predicate for regular side rails, pane and owned supports')
    checks['support_spans']=evidence([[i*32,i*32+4] for i in range(n)]+[[n*32-4,n*32]],spans,'Scan opaque support spans at pane center x6')
    checks['single_glass_layer']=evidence(0,stacked,'Count actual translucent draw contributions')
    return d1.group(checks)


def transmission(run):
    backs={name:Image.new('RGBA',run.size,color) for name,color in {'light':(240,237,223,255),'dark':(30,40,54,255),'colored':(61,127,169,255)}.items()}
    obj=Image.new('RGBA',run.size); obj.paste((245,183,34,255),(3,8,9,min(20,run.height)))
    backs['object']=Image.alpha_composite(backs['colored'],obj)
    scenes={k:Image.alpha_composite(v,run) for k,v in backs.items()}
    total=response=object_total=object_response=frame_response=errors=0
    for y in range(run.height):
        for x in range(run.width):
            p=(x,y); f=run.getpixel(p)
            if 0<f[3]<255:
                total+=1; response+=scenes['light'].getpixel(p)!=scenes['dark'].getpixel(p)
                if obj.getpixel(p)[3]:
                    object_total+=1; object_response+=scenes['object'].getpixel(p)!=scenes['colored'].getpixel(p)
            if f[3]==255: frame_response+=scenes['light'].getpixel(p)!=scenes['dark'].getpixel(p)
            for k,bg in backs.items():
                b=bg.getpixel(p); expected=tuple((f[i]*f[3]+b[i]*(255-f[3])+127)//255 for i in range(3))+(255,)
                errors+=scenes[k].getpixel(p)!=expected
    return d1.group({'pane_response':evidence(total,response,'Toggle separate light/dark background'),
        'object_response':evidence(object_total,object_response,'Toggle separate yellow object behind glass'),
        'object_present':evidence(True,object_total>0,'Count object-covered pane samples'),
        'frame_invariance':evidence(0,frame_response,'Opaque frame must hide background'),
        'source_over':evidence(0,errors,'Integer source-over equation at every pixel')}),backs,obj,scenes


def local_corner(views,shift=(0,0),missing=False,saved=False):
    main=d1.load(d1.PACKAGE/'candidate'/d1.VIEW_FILES['main'])
    repeat=d1.load(d1.PACKAGE/'candidate'/d1.VIEW_FILES['repeat'])
    horizontal,_,_=d1.assemble(main,repeat,2)
    run,_,_=assemble(views,2,corner=True)
    if missing: run.paste((0,0,0,0),(0,0,8,24))
    size=(144,140); front=Image.new('RGBA',size); side=Image.new('RGBA',size)
    h_origin=(64,36); s_origin=(60+shift[0],36+shift[1])
    front.alpha_composite(horizontal,h_origin); side.alpha_composite(run,s_origin)
    if saved:
        front=d1.load(ART/'d1_d2_corner_d1_layer.png')
        side=d1.load(ART/'d1_d2_corner_d2_layer.png')
    union=Image.alpha_composite(side,front)
    expected_overlap={(x,y) for l,t,r,b in ((64,36,68,40),(64,60,72,64)) for y in range(t,b) for x in range(l,r)}
    overlap=set(); glass_overlap=opaque=glass_hidden=0
    for y in range(size[1]):
        for x in range(size[0]):
            a,b=side.getpixel((x,y))[3],front.getpixel((x,y))[3]
            if a and b:
                overlap.add((x,y)); opaque+=a==255 and b==255
                glass_overlap+=0<a<255 and 0<b<255; glass_hidden+=(0<a<255 and b==255) or (a==255 and 0<b<255)
    top=[64,36,68,40]; cap=[60,60,72,64]
    checks={'origin':evidence([60,36],list(s_origin),'Read actual return draw origin; ground anchor implies y36'),
        'upper_contact':alpha_region(side,top,minimum=255,maximum=255),
        'D1_upper_contact':alpha_region(front,top,minimum=255,maximum=255),
        'return_reveal':alpha_region(side,[62,40,64,60],minimum=150,maximum=150),
        'return_frame':alpha_region(side,[60,36,62,64],minimum=255,maximum=255),
        'side_cap':alpha_region(side,cap,minimum=255,maximum=255),
        'overlap_ownership':evidence(0,len(overlap^expected_overlap),'Compare actual overlap set against two declared opaque ownership rectangles'),
        'glass_overlap':evidence(0,glass_overlap,'Count translucent/translucent intersections'),
        'glass_hidden':evidence(0,glass_hidden,'Count any pane hidden by the other component frame'),
        'D1_render_unchanged':anchored_component(union,horizontal,h_origin,h_origin)}
    # Registration uses center (64,60), not the D1 baseline (64,64).
    ground=Image.new('RGBA',size); ground.paste((86,122,147,255),(64,56,128,64)); ground.paste((86,122,147,255),(60,60,68,124))
    required=Image.new('RGBA',size); required.alpha_composite(d1.load(d0.CANON/'topology_se.png'),(48,44))
    count_missing=lambda im:sum(a[3]>0 and b[3]==0 for a,b in zip(required.get_flattened_data(),im.get_flattened_data()))
    before=count_missing(ground); elbow=Image.new('RGBA',size); elbow.paste((231,174,51,255),(60,56,68,60)); completed=Image.alpha_composite(ground,elbow)
    checks['elbow_coverage']=evidence(0,count_missing(completed),'Compare center-registered strip union with canonical SE topology after D2 half-strip cap ownership')
    # Read top and base boundary from the actual retained D1 frame and D2 cap.
    top_y=min(y for y in range(size[1]) if front.getpixel((64,y))[3])
    base=max(y for y in range(size[1]) if front.getpixel((64,y))[3])+1
    shallow_y=min(y for y in range(40,size[1]) if side.getpixel((70,y))[3])
    observed={'intersection':[64,60],'D1_baseline_edge_y':base,'D1_top_y':top_y,
        'D2_shallow_cap_y':shallow_y,'cutaway_drop_px':shallow_y-top_y,
        'opaque_overlap_pixels':opaque,'translucent_overlap_pixels':glass_overlap,'hidden_glass_pixels':glass_hidden,
        'unexpected_overlap_pixels':len(overlap-expected_overlap),'missing_declared_overlap_pixels':len(expected_overlap-overlap),
        'ground_missing_before_cap':before,'ground_missing_after_cap':count_missing(completed),
        'D1_origin':list(h_origin),'D2_origin':list(s_origin),
        'coordinate_provenance':'Intersection is declared topology placement; D1 top/base and D2 shallow-cap y are scanned from actual alpha.'}
    checks['cutaway_drop']=evidence(24,shallow_y-top_y,'Measure upper-post start versus shallow-cap start, separately from base contact')
    bg=Image.new('RGBA',size,(225,226,213,255))
    if saved:
        checks['saved_composite']=evidence(0,d1.pixel_difference(d1.load(ART/'d1_d2_corner_clean.png'),Image.alpha_composite(bg,union)),
            'Reload both saved RGBA layers and clean scene; compare full source-over reconstruction')
    return d1.group(checks,computed=observed,visual_review='PENDING_HUMAN_REVIEW_OF_EXPLICIT_CUTAWAY'),Image.alpha_composite(bg,union),side,front,ground,elbow,completed


def context(run,cell=(32,64),drift=(0,0),saved_name=None):
    wall=d1.load(ROOT/'assets/architecture/hospital_wall_side_left_01.png')
    floor=d1.load(ROOT/'assets/architecture/hospital_floor_plain_01.png')
    x,y=cell; expected=(x+12,y); actual=(expected[0]+drift[0],expected[1]+drift[1]); size=(x+112,y+run.height+48)
    bg=Image.new('RGBA',size)
    for yy in range(0,size[1],32):
        for xx in range(0,size[0],32): bg.alpha_composite(floor,(xx,yy))
    structure=Image.new('RGBA',size); structure.alpha_composite(wall,(x+12,y-32)); structure.alpha_composite(wall,(x+12,y+run.height)); structure.alpha_composite(run,actual)
    if saved_name:
        structure=d1.load(ART/f'd2_context_{saved_name}_structure.png')
        bg=d1.load(ART/f'd2_context_{saved_name}_background.png')
    checks={'anchor':anchored_component(structure,run,expected,actual),
        'render_origin':evidence([12,0],[actual[0]-x,actual[1]-y],'Compare actual render placement with grid origin'),
        'north_contact':alpha_region(structure,[x+12,y-1,x+24,y+1],minimum=255,maximum=255),
        'south_contact':alpha_region(structure,[x+12,y+run.height-1,x+24,y+run.height+1],minimum=255,maximum=255)}
    if saved_name:
        checks['saved_composite']=evidence(0,d1.pixel_difference(d1.load(ART/f'd2_context_{saved_name}_scene.png'),Image.alpha_composite(bg,structure)), 'Reload saved structure/background and compare scene')
    return d1.group(checks,computed={'cell':list(cell),'render_origin':list(actual)}),Image.alpha_composite(bg,structure),bg,structure


def negatives(views):
    run,p,l=assemble(views,2); good=check_run(run,p,l,2); cases={}
    def add(name,im,result,key,control=good):
        cases[name]={'image':im,'validation':result,'intended_check':key,'valid_control_pass':control['pass'],
                     'proven':control['pass'] and not result['checks'][key]['pass']}
    im,p2,l2=assemble(views,2,stride=33); add('repeat_displacement_1px',im,check_run(im,p2,l2,2),'origins')
    for name,pos,alpha,key in [('broken_contact',(0,32),0,'frame'),('opaque_glass',(6,12),255,'pane'),('pane_hole',(6,12),0,'pane')]:
        im=run.copy(); im.putpixel(pos,(*im.getpixel(pos)[:3],alpha))
        if name=='opaque_glass':
            for yy in range(im.height):
                for xx in range(im.width):
                    pixel=im.getpixel((xx,yy))
                    if 0<pixel[3]<255: im.putpixel((xx,yy),(*pixel[:3],255))
        add(name,im,check_run(im,p,l,2),key)
    wrong=dict(views); wrong['repeat']=views['main']; im,p2,l2=assemble(wrong,2); add('doubled_support',im,check_run(im,p2,l2,2),'support_spans')
    im,p2,l2=assemble(views,2,duplicate=True); add('stacked_glass',im,check_run(im,p2,l2,2),'single_glass_layer')
    control,*_=context(run); bad,im,*_=context(run,drift=(1,0)); add('anchor_mismatch_1px',im,bad,'render_origin',control)
    control,*_=local_corner(views)
    bad,im,*_=local_corner(views,missing=True); add('missing_corner_return',im,bad,'upper_contact',control)
    bad,im,*_=local_corner(views,shift=(1,0)); add('corner_displacement_1px',im,bad,'overlap_ownership',control)
    return cases


def labeled_panel(im,title,lines=(),factor=4):
    w=max(im.width*factor+32,600); h=im.height*factor+60+18*len(lines)
    out=Image.new('RGBA',(w,h),(24,35,49,255)); draw=ImageDraw.Draw(out)
    draw.text((16,12),title,fill='white',font=ImageFont.load_default(size=16))
    out.alpha_composite(im.resize((im.width*factor,im.height*factor),Image.Resampling.NEAREST),(16,40))
    for i,line in enumerate(lines): draw.text((16,im.height*factor+48+i*18),line,fill='white',font=ImageFont.load_default(size=13))
    return out


def stack(panels):
    out=Image.new('RGBA',(max(p.width for p in panels),sum(p.height for p in panels)),(24,35,49,255)); y=0
    for p in panels: out.alpha_composite(p,(0,y)); y+=p.height
    return out


def row(panels):
    out=Image.new('RGBA',(sum(p.width for p in panels),max(p.height for p in panels)),(24,35,49,255)); x=0
    for p in panels: out.alpha_composite(p,(x,0)); x+=p.width
    return out


def main():
    ART.mkdir(parents=True,exist_ok=True)
    if not (OUT/'production_before.json').exists(): raise ValueError('Initial task snapshot must be captured before work; never replace historical hashes')
    c=contract(); target=OUT/'d2_geometry_alpha_contract_proposed.json'
    if target.exists() and d0.read_json(target)!=c: raise ValueError('Proposal changed: explicit review required before replacement')
    d0.write_json(target,c); views={}; files={}
    for name in c['views']:
        im=raster(c,name); im.save(OUT/f'd2_{name}_native.png'); im.resize((im.width*8,im.height*8),Image.Resampling.NEAREST).save(OUT/f'd2_{name}_source_8x.png')
        views[name]=d1.load(OUT/f'd2_{name}_native.png'); files[name]=check_view(views[name],d1.load(OUT/f'd2_{name}_source_8x.png'),c,name)
    # Establish and save the local corner before expanding any montage or context.
    corner,clean,side,front,ground,elbow,completed=local_corner(views)
    for name,im in [('clean',clean),('d2_layer',side),('d1_layer',front),('ground_before',ground),('ground_elbow_ownership',elbow),('ground_completed',completed)]: im.save(ART/f'd1_d2_corner_{name}.png')
    corner,clean,side,front,ground,elbow,completed=local_corner(views,saved=True)
    clean=d1.load(ART/'d1_d2_corner_clean.png')
    anno=clean.copy(); draw=ImageDraw.Draw(anno)
    draw.line((48,60,128,60),fill=(238,177,40,255)); draw.line((64,32,64,124),fill=(238,177,40,255))
    draw.line((68,64,128,64),fill=(238,66,154,255)); draw.rectangle((60,36,67,39),outline=(68,220,163,255)); draw.rectangle((60,60,71,63),outline=(68,220,163,255))
    draw.ellipse((62,58,66,62),fill=(245,245,240,255))
    labeled_panel(anno,'D2 v2: annotated centerline and cutaway return',[
        'Gold: ground axes intersect (64,60). Pink: D1 base edge y64, NOT centerline.',
        'Green: required upper contact y36..40 and shallow cap y60..64; 24px cutaway.',
        'D1 origin (64,36), image anchor (16,28); D2 origin (60,36), image anchor (4,40).',
        'D2 thin glass reveal x62..64 connects top cap to shallow side cap beside D1 post.',
        'Layer order: plain background, D2, unchanged D1. 48px opaque overlap; no pane overlap.']).save(ART/'d1_d2_corner_annotated.png')
    repeats={}; contexts={}; corner_repeats={}
    for n in (1,2,4):
        im,p,l=assemble(views,n); im.save(ART/f'd2_run_{n}_native.png'); im=d1.load(ART/f'd2_run_{n}_native.png')
        qa=check_run(im,p,l,n); trans,backs,obj,scenes=transmission(im)
        repeats[str(n)]={'geometry':qa,'transmission':trans}
        raised,cp,cl=assemble(views,n,corner=True); raised.save(ART/f'd2_corner_run_{n}_native.png')
        raised=d1.load(ART/f'd2_corner_run_{n}_native.png')
        corner_repeats[str(n)]=d1.group({
            'body_unchanged':evidence(0,d1.pixel_difference(raised.crop((0,24,12,24+32*n)),im),'Read saved corner-run body against saved straight run'),
            'origins':evidence([[0,0]]+[[0,24+32*i] for i in range(1,n)],cp,'Actual image origins; ground stride remains32'),
            'single_glass_layer':evidence(1,max(cl.get_flattened_data()),'Maximum translucent draw count in corner run')})
        trans_corner,corner_backs,corner_object,corner_scenes=transmission(raised)
        corner_repeats[str(n)]['transmission']=trans_corner
        for key,bg in corner_backs.items(): bg.save(ART/f'd2_corner_run_{n}_{key}_background.png'); corner_scenes[key].save(ART/f'd2_corner_run_{n}_{key}_composite.png')
        corner_object.save(ART/f'd2_corner_run_{n}_object_layer.png')
        for k,bg in backs.items(): bg.save(ART/f'd2_run_{n}_{k}_background.png'); scenes[k].save(ART/f'd2_run_{n}_{k}_composite.png')
        obj.save(ART/f'd2_run_{n}_object_layer.png')
        if n==2:
            for key,cell in [('original',(32,64)),('relocated',(64,96))]:
                qa,scene,bg,structure=context(im,cell); contexts[key]=qa
                for suffix,img in [('scene',scene),('background',bg),('structure',structure)]: img.save(ART/f'd2_context_{key}_{suffix}.png')
                contexts[key]=context(im,cell,saved_name=key)[0]
    old=d1.load(v1.OUT/'artifacts/d1_d2_corner_scene.png')
    comparison=stack([labeled_panel(old,'BEFORE: preserved v1, unconnected shallow strip',factor=3),labeled_panel(clean,'AFTER: v2 explicit upright return / shallow cutaway',factor=4)])
    comparison.save(ART/'d2_corner_before_after.png')
    standalone=Image.new('RGBA',(72,64),(225,226,213,255)); standalone.alpha_composite(views['main'],(8,24)); standalone.alpha_composite(views['corner_repeat'],(36,0))
    repeat_sheet=Image.new('RGBA',(120,128),(225,226,213,255))
    for i,n in enumerate((1,2,4)): repeat_sheet.alpha_composite(d1.load(ART/f'd2_run_{n}_object_composite.png'),(8+i*40,0))
    transmission_sheet=Image.new('RGBA',(120,88),(225,226,213,255))
    for i,key in enumerate(('light','dark','colored','object')): transmission_sheet.alpha_composite(d1.load(ART/f'd2_corner_run_2_{key}_composite.png'),(8+i*28,0))
    montage=stack([row([labeled_panel(clean,'D2 v2 PROPOSED: clean cutaway corner',[
        'Human geometry review pending. Intentional cutaway, not equal-height rail continuity.',
        'Saved scaffold views; D1 unchanged; 48px declared opaque overlap.'],factor=4),d1.load(ART/'d1_d2_corner_annotated.png')]),
        row([labeled_panel(old,'Preserved v1: missing visible upper relationship',factor=2),labeled_panel(standalone,'Saved main (left) / corner-repeat (right)',factor=5)]),
        row([labeled_panel(repeat_sheet,'1 / 2 / 4 cells; 32px depth stride; 4px supports',factor=3),labeled_panel(transmission_sheet,'Corner run: light / dark / colored / separate object',factor=4)]),
        row([labeled_panel(d1.load(ART/'d2_context_original_scene.png'),'Approved-wall context: original',factor=2),
        labeled_panel(d1.load(ART/'d2_context_relocated_scene.png'),'Approved-wall context: relocated',factor=2)])])
    montage.save(ART/'d2_geometry_review_montage.png')
    negative=negatives(views)
    for name,case in negative.items(): case['image'].save(ART/f'broken_{name}.png')
    preservation=compare_snapshots(d0.read_json(OUT/'production_before.json'),v1.snapshot(),allowed_addition_prefixes=(PREFIX,))
    success=all(q['pass'] for q in files.values()) and corner['pass'] and all(r['geometry']['pass'] and r['transmission']['pass'] for r in repeats.values()) and all(r['pass'] and r['transmission']['pass'] for r in corner_repeats.values()) and all(q['pass'] for q in contexts.values()) and all(q['proven'] for q in negative.values()) and preservation['pass']
    report={'contract_status':STATUS,'computed_conformance':'PASS' if success else 'FAIL','corner':corner,'files':files,'repeats':repeats,'corner_repeats':corner_repeats,'contexts':contexts,
        'negative_controls':{n:{k:v for k,v in q.items() if k!='image'} for n,q in negative.items()},'preservation':preservation,
        'human_visual_review':'PENDING: explicit cutaway and narrow glazed return need human geometry judgment; no final appearance readiness claimed',
        'recommendation':'REVISED_GEOMETRY_HANDOFF_FOR_HUMAN_REVIEW' if success else 'GEOMETRY_BLOCKED'}
    if (OUT/'test_results.json').exists():
        report['tests']=d0.read_json(OUT/'test_results.json')
        if report['tests']['exit_code']!=0:
            success=False; report['computed_conformance']='FAIL'; report['recommendation']='GEOMETRY_BLOCKED'
    if (OUT/'visual_review.json').exists(): report['assistant_visual_findings']=d0.read_json(OUT/'visual_review.json')
    d0.write_json(OUT/'production_preservation.json',preservation); d0.write_json(OUT/'d2_geometry_report.json',report)
    co=corner['computed']
    md=f'''# D2 geometry revision v2 — proposed cutaway return

Contract: {STATUS}. Computed conformance: {report['computed_conformance']}. Human geometry review remains pending; no final appearance readiness or approval.

V1's shallow strip began at D1's baseline without a visible upper transition. V2 explicitly proposes a glazed north return and a stylized cutaway into the shallow side. This is not a new global camera or equal-height rail projection.

Canonical requirements remain 32 px grid, 8 px NS strip, axis-aligned ground, shallow orientation-aware side and 8x source scale. Measured canonical side is 20x32; D1 is 32x28. The 12 px side band, 2 px rails and cutaway arrangement are NEW proposed presentation choices, replacing v1's 14 px width ratio. Half-open rectangles are used throughout.

Main/repeat: 12x32 native, 96x256 source; origin [12,0] relative to cell, cell anchor [16,16], image anchor [4,16]. Corner-main/repeat: 12x56 native, 96x448 source; origin [12,-24], image anchor [4,40]. The carrier contains the declared north return, with no arbitrary padding/trim. All export pixels are exact 8x blocks. Footprint is 1x1 independently of carrier dimensions.

D1 cell [64,44] maps to render [64,36]. Its ground centerline is y60; baseline edge is y64. D2 cell [48,60] has north center [64,60]; its cap occupies y60..64 and meets the distinct D1 base edge. The corner image starts at [60,36], derived from D1's 28 px image height and 4 px center-to-base offset, not an unanchored upward shift.

The D2 upper cap [0,0,8,4), outer frame [0,0,2,28), glazed reveal [2,4,4,24) and shallow cap [0,24,12,28) explicitly form the transition. The return is a side-facing cheek beside D1's original post, not an added column or cover. Its 2 px glass reveal and abrupt cutaway are visual review risks. Main pane [2,4,10,28) has alpha150, frame255; all undeclared corner pixels are alpha0. Corner and straight views are mutually exclusive parts of one future logical asset. No D1 assembly mask is used.

Measured D1 top y{co['D1_top_y']}, side cap y{co['D2_shallow_cap_y']}: deliberate {co['cutaway_drop_px']} px cutaway. Draw order is background, D2, unchanged D1. Actual opaque overlap: {co['opaque_overlap_pixels']} px, confined to [64,36,68,40) and [64,60,72,64). Translucent overlap: {co['translucent_overlap_pixels']}; hidden glass: {co['hidden_glass_pixels']}; unexpected overlap: {co['unexpected_overlap_pixels']}. Required upper contact, glazed reveal and continuous return-frame checks pass independently of base/topology checks. D1 pixels remain exact in the finished composition.

The v1 4x8 topology mask mixed baseline registration error with elbow ownership. With centerline registration, the missing quadrant is {co['ground_missing_before_cap']} px (4x4). D2 owns a half-strip cap [12,-4,20,0) within its corner ground region [12,-4,20,32); this fills that quadrant with {co['ground_missing_after_cap']} missing pixels remaining. It is separately shown as ground ownership, never rendered over the artwork or counted as an asset.

One/two/four-cell runs use 32 px depth stride, north-owned 4 px supports and a terminal south support. Geometry, contact continuity and separate light/dark/colored/object transmission pass. Original and relocated unchanged Batch 11 wall/floor contexts pass. The side/wall width step remains a presentation review item, not a general junction repair.

Negative controls (each has a passing valid control):
'''
    md+='\n'
    for name,q in negative.items(): md+=f"- {name}: intended check `{q['intended_check']}`, rejection proven {q['proven']}.\n"
    md+=f"\nProtected files: {preservation['protected_file_count']}; changed {preservation['changed']}; missing {preservation['missing']}. Counts before/after: {preservation['expected_counts']} / {preservation['observed_counts']}. Entire D2 v1 and D0/D1 history remain unchanged. Only D2 v2 reference additions are authorized; existing hashes remain locked.\n\nReproduce: `python tools/validate_architecture_d2_v2.py`. Full suite: `python -m pytest -q`; previous baseline 94.\n"
    if 'tests' in report: md+=f"\nCaptured complete suite: {report['tests']['passed']} passed; exit {report['tests']['exit_code']}.\n"
    md+='\nNo human approval, final appearance, production ingestion, Batch 13 or D3. Review the explicit cutaway before any appearance task.\n'
    (OUT/'d2_geometry_report.md').write_text(md,encoding='utf-8')
    names=['d2_geometry_alpha_contract_proposed.json','d2_geometry_report.json','d2_geometry_report.md']
    names += [f'd2_{name}_{scale}.png' for name in c['views'] for scale in ('native','source_8x')]
    names += ['artifacts/'+n+'.png' for n in ('d1_d2_corner_clean','d1_d2_corner_annotated','d1_d2_corner_ground_elbow_ownership','d2_corner_before_after','d2_geometry_review_montage')]
    for extra in ('test_results.json','test_results.txt','visual_review.json','README.md'):
        if (OUT/extra).exists(): names.append(extra)
    with zipfile.ZipFile(OUT/'d2_geometry_review_bundle.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
        for name in sorted(names):
            info=zipfile.ZipInfo(name,date_time=(2026,9,11,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED; z.writestr(info,(OUT/name).read_bytes())
    print(json.dumps({'conformance':report['computed_conformance'],'corner':co,'preservation':preservation['pass']},indent=2))
    return 0 if success else 1


if __name__=='__main__': raise SystemExit(main())
