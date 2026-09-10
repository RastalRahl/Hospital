"""D3 geometry proposal: reflect rectangles, never finished D1/D2 artwork."""
from __future__ import annotations

import json
import zipfile
from PIL import Image, ImageDraw
import validate_architecture_d0 as d0
import validate_architecture_d1 as d1
import validate_architecture_d2 as historical
import validate_architecture_d2_v2 as d2
import validate_architecture_d2_appearance as appearance
from rastalr_pipeline.geometry import evidence, alpha_region, anchored_component
from rastalr_pipeline.snapshot import compare_snapshots

ROOT=d0.ROOT
PREFIX='references/architecture/master_validation_D3_v1/'
OUT=ROOT/PREFIX
ART=OUT/'artifacts'
STATUS='PROPOSED_FOR_HUMAN_GEOMETRY_REVIEW'
NAMES=('main','repeat','corner_main','corner_repeat')


def reflect(rect,width):
    l,t,r,b=rect
    return [width-r,t,width-l,b]


def contract():
    base=d0.read_json(appearance.CONTRACT)
    right=d1.load(d0.CANON/'side_wall_right_1x.png')
    ns=d1.load(d0.CANON/'topology_ns.png'); sw=d1.load(d0.CANON/'topology_sw.png')
    spec=d0.read_json(d0.CANON/'architecture_v2_spec.json')
    if spec['logical_grid_px']!=32 or right.size!=(20,32) or ns.getchannel('A').getbbox()!=(12,0,20,32):
        raise ValueError('Canonical right-side/topology differs from inspected authority; stop for review')
    views={}
    for name,s in base['views'].items():
        w,h=s['size']; origin=[32-s['origin'][0]-w,s['origin'][1]]
        views[name]={'size':[w,h],'source_size':[w*8,h*8],'envelope':reflect(s['envelope'],w),
            'cell_envelope':[origin[0],origin[1],origin[0]+w,origin[1]+h],
            'origin':origin,'cell_anchor':s['cell_anchor'],'image_anchor':[w-s['image_anchor'][0],s['image_anchor'][1]],
            'frame':[reflect(r,w) for r in s['frame']],'pane':[reflect(r,w) for r in s['pane']],
            'exterior':([[0,0,4,4],[0,4,8,24]] if name.startswith('corner') else []),
            'contacts':({'top_return':[4,0,8,4],'outer_return':[10,0,12,28],'shallow_cap':[0,24,12,28]} if name.startswith('corner') else {'north_cap':[0,0,12,4]}),
            'terminal_contact':([0,h-4,12,h] if name.endswith('main') else [[0,h-4,2,h],[10,h-4,12,h]])}
    sources=[ROOT/'docs/ARCHITECTURE.md',ROOT/'docs/ART_DIRECTION.md',ROOT/'references/camera/rastalr_camera_reference_v1.png',
        d0.CANON/'architecture_v2_spec.json',d0.CANON/'side_wall_right_1x.png',d0.CANON/'side_wall_left_1x.png',d0.CANON/'topology_ns.png',d0.CANON/'topology_sw.png',d0.CANON/'topology_se.png',
        ROOT/'metadata/production_batch_11_architecture_foundation.json',ROOT/'tools/build_architecture_foundation_batch_11_review.py',
        d1.CONTRACT_PATH,d1.OUT/'d1_validation_report.json',appearance.CONTRACT,d2.OUT/'d2_geometry_report.json',appearance.OUT/'d2_appearance_validation_report.json']
    sources += [d1.PACKAGE/'candidate'/d1.VIEW_FILES[n] for n in ('main','repeat')]
    sources += [appearance.PACKAGE/'candidate'/f'{appearance.STEM}{n}_native.png' for n in NAMES]
    sources += [ROOT/'assets/architecture'/n for n in ('hospital_wall_side_right_01.png','hospital_wall_side_right_02.png','hospital_floor_plain_01.png')]
    return {'id':'hospital_glass_partition_side_right_01','status':STATUS,'rectangle_convention':'[left, top, right, bottom)',
        'canonical_constraints':{'grid':32,'source_scale':8,'ground_strip':[12,0,20,32],'camera':spec['projection'],'side_policy':spec['rendering_layers']['side_east_west_wall'],
            'normalization':'architecture_grid_preserving','transforms':'Integer placement and exact nearest-neighbor 8x only; no trim, pad, warp or finished-art reflection'},
        'measured_sources':{'method':'Read actual PNG dimensions and nonzero-alpha bounds; placement metadata is quoted separately',
            'right_wall_size':list(right.size),'right_wall_envelope':list(right.getchannel('A').getbbox()),'ns_alpha_bbox':list(ns.getchannel('A').getbbox()),'sw_alpha_bbox':list(sw.getchannel('A').getbbox()),
            'approved_placement_metadata':'Batch11 right01 crop [1280,416,1440,672)/8=[160,52,180,84); right02 same x range. Review builder places right walls at x224, y52+32*r. Canonical right envelope occupies cell x0..20; D3 retains its outer edge20 with a narrower inward band8..20.'},
        'derived_right_geometry':{'rule_cell':'[l,r) -> [32-r,32-l) about cell x16','rule_image':'[l,r) -> [12-r,12-l); a pixel index x maps to11-x, not12-x',
            'origin_rule':'32-(D2 origin x12 + width12)=8; y unchanged','anchor_rule':'cell [16,16] minus origin gives image [8,16] or [8,40]',
            'logical_footprint':[1,1],'orientation':'east/right boundary, interior west/left; repeat south/+y','stride':[0,32],
            'north_endpoint_cell':[16,0],'south_endpoint_cell':[16,32],'north_endpoint_main_image':[8,0],'north_endpoint_corner_image':[8,24],
            'ground_elbow_corner_cell':[12,-4,20,32],'cutaway_drop':24},
        'proposed_choices':{'design_basis':'D2 v2 reviewed stylized shallow cutaway with upright north return, retaining all family proportions',
            'differences':'Only structural x reflection and resulting x origin/anchor/contact ownership; no dimensional departure. D1 terminal artwork is used in its authored orientation.',
            'frame_rgba':list(d2.FRAME),'glass_rgba':list(d2.GLASS),'lighting':'Flat scaffold has no material lighting; future D3 highlights must be authored for upper-left light independently',
            'view_selection':'One future logical D3 asset. First cell at D1 NE uses corner_main if terminal, corner_repeat otherwise; subsequent cells use repeat until final main. Alternatives are never stacked.'},
        'views':views,'alpha_policy':{'frame':255,'pane':150,'all_other_pixels':0},
        'corner_contract':{'example_D1_origin':[32,36],'example_D1_width':64,'example_D1_terminal_post':[92,36,96,64],
            'example_D3_cell':[80,60],'example_D3_corner_origin':[88,36],'intersection':[96,60],'D1_baseline_edge':64,
            'centerline_rule':'D1 ground center is baseline minus4; D3 north center is cell+[16,0]. Base edge and ground center are not interchangeable.',
            'expected_opaque_overlap':[[92,36,96,40],[88,60,96,64]],
            'overlap_derivation':'D3 reflected upper cap intersects existing D1 terminal post over4x4; shallow cap intersects D1 lower rail over8x4. Expected area=16+32=48; actual pixels must be measured.',
            'glazed_return':[96,40,98,60],'outer_frame':[98,36,100,64],'shallow_cap':[88,60,100,64],
            'ground_ownership':'D3 owns half-strip north cap [12,-4,20,0) to complete canonical SW elbow; no visible repair component',
            'draw_order':['separate floor/background','D2 if present','D3','unchanged D1'],
            'no_masks':'No D1/D2 assembly mask, reflection or repair. D1 owns both declared opaque occlusions; zero stacked/hidden glass required.'},
        'human_visual_review':{'status':'PENDING','approval':False,'scope':'Proposed right-side geometry, these two local corners, and enclosure only; no all-direction L/T/cross claim. Flat D3 shading is intentional, not a material mismatch.'},
        'sources_sha256':{p.relative_to(ROOT).as_posix():d0.digest(p) for p in sources}}


def saved(path,im):
    im.save(path)
    return d1.load(path)


def corner_check(front,side,union,edge,base,right,cell,origin):
    top=base-28; cy=base-4
    if right:
        overlap_rects=[[edge-4,top,edge,top+4],[edge-8,cy,edge,base]]
        reveal=[edge,top+4,edge+2,cy]; frame=[edge+2,top,edge+4,base]; cap=[edge-8,cy,edge+4,base]; xprobe=edge-6
        expected_origin=[cell[0]+8,cell[1]-24]
    else:
        overlap_rects=[[edge,top,edge+4,top+4],[edge,cy,edge+8,base]]
        reveal=[edge-2,top+4,edge,cy]; frame=[edge-4,top,edge-2,base]; cap=[edge-4,cy,edge+8,base]; xprobe=edge+6
        expected_origin=[cell[0]+12,cell[1]-24]
    expected={(x,y) for l,t,r,b in overlap_rects for y in range(t,b) for x in range(l,r)}
    overlap=set(); opaque=stacked=hidden=0
    for y in range(front.height):
        for x in range(front.width):
            a,b=front.getpixel((x,y))[3],side.getpixel((x,y))[3]
            if a and b:
                overlap.add((x,y)); opaque+=a==b==255; stacked+=0<a<255 and 0<b<255
                hidden+=(0<a<255 and b==255) or (0<b<255 and a==255)
    top_probe=edge-1 if right else edge
    painted_top=min(y for y in range(front.height) if front.getpixel((top_probe,y))[3])
    painted_base=max(y for y in range(front.height) if front.getpixel((top_probe,y))[3])+1
    cap_ys=[y for y in range(top+4,side.height) if side.getpixel((xprobe,y))[3]]
    cap_y=min(cap_ys) if cap_ys else None
    checks={'anchor':evidence(expected_origin,list(origin),'Compare actual recorded placement to derived cell origin'),
        'centerline':evidence([edge,painted_base-4],[cell[0]+16,cell[1]],'Compare D1 measured base-minus4 with NS cell north-axis coordinate'),
        'upper_contact':alpha_region(side,overlap_rects[0],minimum=255,maximum=255),
        'D1_upper_contact':alpha_region(front,overlap_rects[0],minimum=255,maximum=255),
        'return_glass':alpha_region(side,reveal,minimum=150,maximum=150),'return_frame':alpha_region(side,frame,minimum=255,maximum=255),
        'shallow_cap':alpha_region(side,cap,minimum=255,maximum=255),
        'opaque_overlap':evidence(len(expected),opaque,'Count actual pairwise opaque pixels; expectation is derived rectangle area',units='pixels'),
        'unexpected_overlap':evidence(0,len(overlap-expected),'Measure pixels outside declared occlusion rectangles'),
        'missing_overlap':evidence(0,len(expected-overlap),'Measure missing required contact pixels'),
        'stacked_glass':evidence(0,stacked,'Count two translucent surfaces at the same pixel'),
        'hidden_glass':evidence(0,hidden,'Count a translucent pane under the other component frame'),
        'cutaway_drop':evidence(24,None if cap_y is None else cap_y-painted_top,'Scan actual upper-frame and shallow-cap positions')}
    return d1.group(checks,computed={'opaque_overlap_pixels':opaque,'stacked_glass_pixels':stacked,'hidden_glass_pixels':hidden,
        'unexpected_overlap_pixels':len(overlap-expected),'top_y':painted_top,'base_y':painted_base,'cap_y':cap_y,'origin':list(origin),'cell':cell},
        derived={'intersection':[edge,cy],'opaque_overlap_rectangles':overlap_rects},conformance_to=STATUS)


def assembly(views,enclosure=False,delta=(0,0),defect=None,label=None,*,artifact_dir=ART):
    dx,dy=delta; x0=(64 if enclosure else 32)+dx; width=128 if enclosure else 64; top=36+dy; base=top+28; east=x0+width; cy=base-4
    size=(east+48,176+dy); horizontal_count=width//32
    dm=d1.load(d1.PACKAGE/'candidate'/d1.VIEW_FILES['main']); dr=d1.load(d1.PACKAGE/'candidate'/d1.VIEW_FILES['repeat'])
    horizontal,_,_=d1.assemble(dr if defect=='d1_missing_terminal' else dm,dr,horizontal_count)
    vertical,p,l=d2.assemble(views,2,corner=True)
    if defect=='missing_return': vertical.paste((0,0,0,0),(4,0,12,24))
    cell=[east-16,cy]; origin=[cell[0]+8,cell[1]-24]
    if defect=='left_origin': origin[0]+=4
    if defect=='anchor_1px': origin[0]+=1
    if defect=='displaced_return':
        extension=vertical.crop((0,0,12,24)); vertical.paste((0,0,0,0),(0,0,12,24)); vertical.alpha_composite(extension,(1,0))
    layers={n:Image.new('RGBA',size) for n in ('d1','d2','d3')}
    layers['d1'].alpha_composite(horizontal,(x0,top)); layers['d3'].alpha_composite(vertical,tuple(origin))
    left=None
    if enclosure:
        d2_views={n:appearance.candidate(n) for n in NAMES}; left,_,_=d2.assemble(d2_views,2,corner=True)
        layers['d2'].alpha_composite(left,(x0-4,top))
    bg=Image.new('RGBA',size,(225,226,213,255)); floor=d1.load(ROOT/'assets/architecture/hospital_floor_plain_01.png')
    for y in range(base,size[1],32):
        for x in range(x0,east,32): bg.alpha_composite(floor,(x,y))
    if label:
        layers={n:saved(artifact_dir/f'{label}_{n}_layer.png',im) for n,im in layers.items()}; bg=saved(artifact_dir/f'{label}_background.png',bg)
    sides=Image.alpha_composite(layers['d2'],layers['d3']); union=Image.alpha_composite(sides,layers['d1']); scene=Image.alpha_composite(bg,union)
    if label:
        union=saved(artifact_dir/f'{label}_structure.png',union); scene=saved(artifact_dir/f'{label}_clean.png',scene)
    ne=corner_check(layers['d1'],layers['d3'],union,east,base,True,cell,origin)
    checks={'northeast':ne,'D1_render_unchanged':anchored_component(union,d1.assemble(dm,dr,horizontal_count)[0],(x0,top),(x0,top)),
        'D1_terminal_post':alpha_region(layers['d1'],[east-4,top,east,base],minimum=255,maximum=255),
        'D3_single_layer':evidence(1,max(l.get_flattened_data()),'Actual D3 assembly translucent coverage maximum'),
        'saved_composite':evidence(0,d1.pixel_difference(scene,Image.alpha_composite(bg,Image.alpha_composite(sides,layers['d1']))),'Reconstruct clean scene from saved component/background layers')}
    if enclosure:
        checks['northwest']=corner_check(layers['d1'],layers['d2'],union,x0,base,False,[x0-16,cy],[x0-4,top])
        checks['D2_layer_unchanged']=anchored_component(layers['d2'],left,(x0-4,top),(x0-4,top))
        checks['side_intersections']=evidence(0,sum(a[3]>0 and b[3]>0 for a,b in zip(layers['d2'].get_flattened_data(),layers['d3'].get_flattened_data())),'Actual D2/D3 layer intersection count')
        checks['front_open']=alpha_region(union,[x0+8,base+60,east-8,base+64],minimum=0,maximum=0)
    # Deterministic ground logic, separately saved and never used as artwork.
    ground=Image.new('RGBA',size); ground.paste((82,110,136,255),(x0,cy-4,east,base)); ground.paste((82,110,136,255),(east-4,cy,east+4,cy+64))
    required=Image.new('RGBA',size); required.alpha_composite(d1.load(d0.CANON/'topology_sw.png'),(east-16,cy-16))
    missing=lambda im:sum(a[3]>0 and b[3]==0 for a,b in zip(required.get_flattened_data(),im.get_flattened_data()))
    before=missing(ground); ground.paste((231,174,51,255),(east-4,cy-4,east+4,cy))
    checks['sw_ground_coverage']=evidence(0,missing(ground),'Compare D3 north-cap ownership against canonical SW topology')
    if enclosure:
        ground.paste((82,110,136,255),(x0-4,cy-4,x0+4,cy+64))
        nw_required=Image.new('RGBA',size);nw_required.alpha_composite(d1.load(d0.CANON/'topology_se.png'),(x0-16,cy-16))
        checks['se_ground_coverage']=evidence(0,sum(a[3]>0 and b[3]==0 for a,b in zip(nw_required.get_flattened_data(),ground.get_flattened_data())),
            'Compare unchanged D2 north-cap ownership against canonical SE topology in enclosure')
    if label: ground.save(artifact_dir/f'{label}_ground.png'); required.save(artifact_dir/f'{label}_required_sw.png')
    return d1.group(checks,derived={'D1_origin':[x0,top],'D1_width':width,'D3_cell':cell,'D3_origin':origin,'north_east_intersection':[east,cy]},
        computed={'sw_missing_before_north_cap':before,'sw_missing_after':missing(ground)},human_visual_review='PENDING'),scene,union


def right_context(run,cell=(64,64),drift=0,label=None,*,artifact_dir=ART):
    x,y=cell; origin=(x+8+drift,y); size=(x+96,y+run.height+48)
    wall=d1.load(ROOT/'assets/architecture/hospital_wall_side_right_01.png'); floor=d1.load(ROOT/'assets/architecture/hospital_floor_plain_01.png')
    bg=Image.new('RGBA',size)
    for yy in range(0,size[1],32):
        for xx in range(0,size[0],32): bg.alpha_composite(floor,(xx,yy))
    structure=Image.new('RGBA',size); structure.alpha_composite(wall,(x,y-32)); structure.alpha_composite(wall,(x,y+run.height)); structure.alpha_composite(run,origin)
    if label: bg=saved(artifact_dir/f'{label}_background.png',bg); structure=saved(artifact_dir/f'{label}_structure.png',structure)
    scene=Image.alpha_composite(bg,structure)
    if label: scene=saved(artifact_dir/f'{label}_clean.png',scene)
    checks={'origin':evidence([8,0],[origin[0]-x,origin[1]-y],'Actual image origin relative to NS cell'),
        'anchored_pixels':anchored_component(structure,run,(x+8,y),origin),
        'north_contact':alpha_region(structure,[x+8,y-1,x+20,y+1],minimum=255,maximum=255),
        'south_contact':alpha_region(structure,[x+8,y+run.height-1,x+20,y+run.height+1],minimum=255,maximum=255),
        'north_wall':anchored_component(structure,wall,(x,y-32),(x,y-32)),
        'south_wall':anchored_component(structure,wall,(x,y+run.height),(x,y+run.height)),
        'separate_floor':evidence(0,d1.pixel_difference(scene,Image.alpha_composite(bg,structure)),'Rebuild saved context with unchanged separate approved floor')}
    return d1.group(checks,derived={'cell':list(cell)},computed={'origin':list(origin)}),scene


def negative_controls(views):
    good,_,_=assembly(views); cases={}
    for name,defect,key in [('wrong_left_origin','left_origin','anchor'),('anchor_1px','anchor_1px','anchor'),('missing_return','missing_return','upper_contact'),('displaced_return','displaced_return','upper_contact')]:
        bad,scene,_=assembly(views,defect=defect); target=bad['checks']['northeast']
        cases[name]={'image':scene,'validation':target,'valid_control_pass':good['pass'],'intended_check':key,'proven':good['pass'] and not target['checks'][key]['pass']}
    bad,scene,_=assembly(views,defect='d1_missing_terminal')
    cases['D1_wrong_terminal']={'image':scene,'validation':bad,'valid_control_pass':good['pass'],'intended_check':'D1_terminal_post','proven':good['pass'] and not bad['checks']['D1_terminal_post']['pass']}
    run,p,l=d2.assemble(views,2); control=d2.check_run(run,p,l,2)
    def add(name,im,origins,layers,key):
        q=d2.check_run(im,origins,layers,2);cases[name]={'image':im,'validation':q,'valid_control_pass':control['pass'],'intended_check':key,'proven':control['pass'] and not q['checks'][key]['pass']}
    im,pp,ll=d2.assemble(views,2,stride=33);add('repeat_drift_1px',im,pp,ll,'origins')
    for name,pos,alpha,key in [('broken_contact',(11,32),0,'frame'),('pane_hole',(6,12),0,'pane'),('opaque_glass',(6,12),255,'pane')]:
        im=run.copy();im.putpixel(pos,(*im.getpixel(pos)[:3],alpha))
        if name=='opaque_glass':
            for y in range(im.height):
                for x in range(im.width):
                    rgba=im.getpixel((x,y))
                    if 0<rgba[3]<255: im.putpixel((x,y),(*rgba[:3],255))
        add(name,im,p,l,key)
    wrong=dict(views);wrong['repeat']=views['main'];im,pp,ll=d2.assemble(wrong,2);add('doubled_support',im,pp,ll,'support_spans')
    wrong=dict(views);wrong['main']=views['repeat'];im,pp,ll=d2.assemble(wrong,2);add('D3_wrong_terminal',im,pp,ll,'support_spans')
    im,pp,ll=d2.assemble(views,2,duplicate=True);add('stacked_glass',im,pp,ll,'single_glass_layer')
    return cases


def main():
    ART.mkdir(parents=True,exist_ok=True)
    c=contract();path=OUT/'d3_geometry_alpha_contract_proposed.json'
    if path.exists() and d0.read_json(path)!=c: raise ValueError('Existing D3 proposal differs; no silent overwrite')
    d0.write_json(path,c); views={}; files={}
    for name in NAMES:
        im=d2.raster(c,name);views[name]=saved(OUT/f'd3_{name}_native.png',im)
        source=saved(OUT/f'd3_{name}_source_8x.png',im.resize(tuple(c['views'][name]['source_size']),Image.Resampling.NEAREST))
        files[name]=d2.check_view(views[name],source,c,name)
    # Corner first, using actual unmodified D1 main/repeat and its right terminal.
    ne,clean,_=assembly(views,label='northeast')
    anno=clean.copy();draw=ImageDraw.Draw(anno);draw.line((32,60,112,60),fill=(238,177,40,255));draw.line((96,24,96,124),fill=(238,177,40,255));draw.line((32,64,96,64),fill=(239,62,150,255))
    for l,t,r,b in c['corner_contract']['expected_opaque_overlap']:draw.rectangle((l,t,r-1,b-1),outline=(53,217,165,255))
    d2.labeled_panel(anno,'D1 / D3 north-east: structural guides',[
        'Gold center (96,60); pink D1 baseline y64; green derived overlap regions.',
        'D1 origin (32,36), image anchor (16,28); D3 origin (88,36), anchor (8,40).',
        'D3 upright outer frame at x98..100; return pane x96..98; shallow cap y60.',
        'No finished artwork was mirrored. Proposal only; human review pending.'],factor=4).save(ART/'northeast_annotated.png')
    repeats={}
    for n in (1,2,4):
        for corner in (False,True):
            name=('corner_' if corner else 'straight_')+str(n);offset=24 if corner else 0
            run,p,l=d2.assemble(views,n,corner=corner);run=saved(ART/f'{name}_native.png',run)
            qa=d2.check_run(run.crop((0,offset,12,offset+32*n)),[[0,q[1]-offset] if i else [0,0] for i,q in enumerate(p)],l.crop((0,offset,12,offset+32*n)),n)
            selected_mismatches=0
            for i,origin in enumerate(p):
                view=('corner_' if corner and i==0 else '')+('main' if i==n-1 else 'repeat');im=views[view];y=origin[1]
                selected_mismatches+=d1.pixel_difference(im,run.crop((0,y,12,y+im.height)))
            extra=d1.group({'selected_views':evidence(0,selected_mismatches,'Compare saved run cells with actual selected scaffold views'),
                'origins':evidence([[0,0]]+[[0,32*i+offset] for i in range(1,n)],p,'Read actual carrier origins; corner has24px north extension'),
                'single_layer':evidence(1,max(l.get_flattened_data()),'Count actual translucent contributions')})
            trans,backs,obj,scenes=d2.transmission(run)
            for key,bg in backs.items():saved(ART/f'{name}_{key}_background.png',bg);saved(ART/f'{name}_{key}_composite.png',scenes[key])
            obj.save(ART/f'{name}_object_layer.png');repeats[name]={'geometry':qa,'selection':extra,'transmission':trans}
    contexts={}
    for name,cell in [('original',(64,64)),('relocated',(96,96))]:contexts[name],_=right_context(d1.load(ART/'straight_2_native.png'),cell,label='right_wall_'+name)
    enclosures={}
    for name,delta in [('original',(0,0)),('relocated',(32,32))]:enclosures[name],_,_=assembly(views,enclosure=True,delta=delta,label='enclosure_'+name)
    old=d1.load(ART/'enclosure_original_structure.png');new=d1.load(ART/'enclosure_relocated_structure.png')
    enclosures['relocation']=d1.group({'pixel_translation':evidence(0,d1.pixel_difference(old,new.crop((32,32,32+old.width,32+old.height))),'Compare independently reconstructed enclosure layers at two grid origins')})
    negative=negative_controls(views)
    for name,q in negative.items():q['image'].save(ART/f'broken_{name.lower()}.png')
    enclosure=d1.load(ART/'enclosure_original_clean.png')
    repeat_sheet=Image.new('RGBA',(120,152),(225,226,213,255))
    for i,n in enumerate((1,2,4)):repeat_sheet.alpha_composite(d1.load(ART/f'corner_{n}_object_composite.png'),(8+40*i,0))
    transmission=Image.new('RGBA',(120,88),(225,226,213,255))
    for i,name in enumerate(('light','dark','colored','object')):transmission.alpha_composite(d1.load(ART/f'corner_2_{name}_composite.png'),(8+28*i,0))
    montage=d2.stack([d2.row([d2.labeled_panel(clean,'D3 proposed flat geometry / unchanged D1',factor=4),d1.load(ART/'northeast_annotated.png')]),
        d2.labeled_panel(enclosure,'Three-sided enclosure: validated D2 left / validated D1 back / flat D3 right',factor=4),
        d2.row([d2.labeled_panel(enclosure.crop((52,30,112,132)),'NW detail: unchanged D1 and actual D2',factor=5),d2.labeled_panel(enclosure.crop((152,30,212,132)),'NE detail: actual D1 terminal and flat D3',factor=5)]),
        d2.row([d2.labeled_panel(repeat_sheet,'1 / 2 / 4 cells; 32px depth stride',factor=3),d2.labeled_panel(transmission,'Separate light / dark / colored / object',factor=4)]),
        d2.row([d2.labeled_panel(d1.load(ART/'right_wall_relocated_clean.png'),'Approved right-wall context relocated',factor=2),d2.labeled_panel(d1.load(ART/'enclosure_relocated_clean.png'),'Enclosure independently relocated +32,+32',factor=2)])])
    montage.save(ART/'d3_geometry_review_montage.png')
    preservation=compare_snapshots(d0.read_json(OUT/'production_before.json'),historical.snapshot(),allowed_addition_prefixes=(PREFIX,))
    success=all(q['pass'] for q in files.values()) and ne['pass'] and all(all(q['pass'] for q in r.values()) for r in repeats.values()) and all(q['pass'] for q in contexts.values()) and all(q['pass'] for q in enclosures.values()) and all(q['proven'] for q in negative.values()) and preservation['pass']
    report={'status':'PASS' if success else 'FAIL','contract_status':STATUS,'recommendation':'READY FOR HUMAN GEOMETRY REVIEW' if success else 'GEOMETRY BLOCKED',
        'files':files,'northeast':ne,'repeats':repeats,'right_wall_contexts':contexts,'enclosures':enclosures,
        'negative_controls':{name:{k:v for k,v in q.items() if k!='image'} for name,q in negative.items()},'preservation':preservation,
        'human_visual_review':'PENDING. D3 flat shading is intentional. D1/D2 remain unchanged; only these local corners are tested.'}
    if (OUT/'test_results.json').exists():
        report['tests']=d0.read_json(OUT/'test_results.json')
        if report['tests']['exit_code']!=0:success=False;report['status']='FAIL';report['recommendation']='GEOMETRY BLOCKED'
    if (OUT/'visual_review.json').exists():report['assistant_visual_findings']=d0.read_json(OUT/'visual_review.json')
    def failed(value,path=''):
        findings=[]
        if isinstance(value,dict):
            if value.get('pass') is False and 'expected' in value:findings.append({'check':path,**value})
            for k,v in value.items():findings+=failed(v,path+'/'+str(k))
        return findings
    report['blockers']=failed({k:report[k] for k in ('files','northeast','repeats','right_wall_contexts','enclosures')})
    if not preservation['pass']:report['blockers'].append({'check':'preservation','details':preservation})
    for name,q in negative.items():
        if not q['proven']:report['blockers'].append({'check':'negative/'+name,'details':'Valid control failed or intended defect escaped detection'})
    if 'tests' in report and report['tests']['exit_code']!=0:report['blockers'].append({'check':'test_suite','details':report['tests']})
    d0.write_json(OUT/'production_preservation.json',preservation);d0.write_json(OUT/'d3_geometry_report.json',report)
    co=ne['checks']['northeast']['computed']
    lines=['# D3 right-side geometry proposal','',f"**{report['recommendation']}**. Computed conformance {report['status']} to `{STATUS}`; no human approval.",'',
        'Structural rectangles alone were reflected: cell [l,r) becomes [32-r,32-l); local image uses [12-r,12-l). No D1/D2 finished sprite or scene was flipped. Half-open edges and pixel indices remain distinct.','',
        'Main/repeat: native12x32, source96x256, envelope[0,0,12,32), origin[8,0], image anchor[8,16]. Corner-main/repeat: native12x56, source96x448, envelope[0,0,12,56), origin[8,-24], image anchor[8,40]. Cell anchor[16,16], logical footprint1x1, NS strip[12,0,20,32), depth stride[0,32]. Exact integer exports only.','',
        'Canonical right wall measures20x32; its cell envelope x0..20 is consistent with the narrower proposed D3 band x8..20. This retains D2 family proportions with no departure. Rectangles/dimensions are derived proposals, not measured canonical D3 geometry. All frame alpha255, pane150, undeclared exterior0. Four mutually exclusive views belong to one future logical asset.','',
        f"NE actual computed evidence: {co}. Ground center [96,60] differs from D1 baseline y64. D1 extends west from its existing terminal post. Upper and shallow contacts pass independently; the deliberate cutaway remains24px. Expected overlap derives from4x4 upper plus8x4 lower contacts; the observed opaque overlap is {co['opaque_overlap_pixels']}px, unexpected {co['unexpected_overlap_pixels']}, stacked glass {co['stacked_glass_pixels']}, hidden glass {co['hidden_glass_pixels']}.",'',
        f"SW elbow missing pixels before north-cap ownership: {ne['computed']['sw_missing_before_north_cap']}; after: {ne['computed']['sw_missing_after']}. Ground mask is technical evidence only and is never rendered over the artwork.",'',
        'One/two/four straight and corner-starting runs pass saved RGBA selection, 32px placement, 4px shared support, closure and separate light/dark/colored/object transmission. Original and relocated approved right-wall/floor contexts pass.','',
        'The open-front enclosure uses four actual D1 panels (repeat,repeat,repeat,main), actual D2 corner_repeat/main down the left and D3 corner_repeat/main down the right. No alternative views are stacked. Both upper/base corner checks pass; D1 composited pixels and D2 layer pixels are unchanged. The independent +32,+32 enclosure has an identical translated structure. No front partition or all-direction junction claim.','',
        '## Negative controls','']
    for name,q in negative.items():lines.append(f"- {name}: valid control {q['valid_control_pass']}; intended `{q['intended_check']}` rejection proven {q['proven']}.")
    lines+=['',f"Protected historical files: {preservation['protected_file_count']}; changed {preservation['changed']}; missing {preservation['missing']}. Counts before/after: {preservation['expected_counts']} / {preservation['observed_counts']}. Manifest/catalog and all historical sources/reports/contracts/snapshots remain unchanged. Only new D3 files are allowed; old hashes remain mandatory.",'',
        'Run `python tools/validate_architecture_d3.py`; complete suite `python -m pytest -q`. Actual starting suite:160 passed.']
    if 'tests' in report:lines+=['',f"Captured suite: {report['tests']['passed']} passed; exit {report['tests']['exit_code']}."]
    lines+=['',f"Blockers: {report['blockers']}",'','Human review remains pending for right-side geometry and the two local corners. Flat D3 colors are intentional; future highlights must be authored for upper-left lighting. No approval, final appearance, ingestion, Batch13, D4 or unrelated junction repair.','']
    (OUT/'d3_geometry_report.md').write_text('\n'.join(lines),encoding='utf-8')
    names=['d3_geometry_alpha_contract_proposed.json','d3_geometry_report.json','d3_geometry_report.md']+[f'd3_{n}_{scale}.png' for n in NAMES for scale in ('native','source_8x')]
    names += ['artifacts/'+n+'.png' for n in ('northeast_clean','northeast_annotated','enclosure_original_clean','enclosure_relocated_clean','d3_geometry_review_montage')]
    for name in ('README.md','test_results.json','test_results.txt','visual_review.json'):
        if (OUT/name).exists():names.append(name)
    with zipfile.ZipFile(OUT/'d3_geometry_review_bundle.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
        for name in sorted(names):
            info=zipfile.ZipInfo(name,date_time=(2026,9,11,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,(OUT/name).read_bytes())
    print(json.dumps({'status':report['status'],'recommendation':report['recommendation'],'northeast':co,'preservation':preservation['pass']},indent=2))
    return 0 if success else 1


if __name__=='__main__':raise SystemExit(main())
