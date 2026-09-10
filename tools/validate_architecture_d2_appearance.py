"""Independent D2 appearance QA. Never executes package code or edits artwork."""
from __future__ import annotations

import hashlib
import json
import subprocess
import zipfile
from PIL import Image, ImageDraw
import validate_architecture_d0 as d0
import validate_architecture_d1 as d1
import validate_architecture_d2 as v1
import validate_architecture_d2_v2 as v2
from rastalr_pipeline.geometry import evidence, alpha_region, anchored_component
from rastalr_pipeline.snapshot import compare_snapshots

ROOT=d0.ROOT
PREFIX='references/architecture/master_validation_D2_appearance_v1/'
OUT=ROOT/PREFIX
ART=OUT/'artifacts'
PACKAGE=OUT/'sources/package'
CONTRACT=v2.OUT/'d2_geometry_alpha_contract_proposed.json'
BASELINE='4f078aec4aa876e5ac3a806b0ef6a5662f42c8cb'
STEM='rastalr_D2_glass_partition_side_left_locked_v1_'
NAMES=('main','repeat','corner_main','corner_repeat')
EXPECTED_RGB={'main':384,'repeat':384,'corner_main':496,'corner_repeat':496}


def candidate(name,scale='native'):
    return d1.load(PACKAGE/'candidate'/f'{STEM}{name}_{scale}.png')


def package_integrity():
    initial=d0.read_json(OUT/'package_provenance.json')
    archive=OUT/'sources'/initial['archive_name']
    checks={'original_archive':evidence(initial['archive_sha256'],d0.digest(archive),'Compare archive SHA-256 to initial copy')}
    with zipfile.ZipFile(archive) as z:
        actual=sorted(p.relative_to(PACKAGE).as_posix() for p in PACKAGE.rglob('*') if p.is_file())
        checks['members']=evidence(sorted(z.namelist()),actual,'Enumerate archive and saved extracted members')
        checks['extracted_bytes']=evidence([], [n for n in z.namelist() if not (PACKAGE/n).is_file() or (PACKAGE/n).read_bytes()!=z.read(n)],'Byte-for-byte comparison with original ZIP')
    checks['initial_hashes']=evidence([], [n for n,h in initial['members_sha256'].items() if not (PACKAGE/n).is_file() or d0.digest(PACKAGE/n)!=h],'Compare every member to immutable initial extraction hashes')
    supplied={name:h for h,name in (line.split('  ',1) for line in (PACKAGE/'SHA256SUMS.txt').read_text().splitlines())}
    checks['supplied_checksums']=evidence([], [n for n,h in supplied.items() if d0.digest(PACKAGE/n)!=h],'Independently hash files named by package checksums; supporting integrity evidence')
    # Fixed repository mappings, not paths chosen by a package script.
    mapping={f'd2_{n}_native.png':v2.OUT/f'd2_{n}_native.png' for n in NAMES}
    mapping.update({d1.VIEW_FILES[n]:d1.PACKAGE/'candidate'/d1.VIEW_FILES[n] for n in ('main','repeat')})
    mapping.update({n:ROOT/'assets/architecture'/n for n in ('hospital_floor_plain_01.png','hospital_wall_back_straight_01.png')})
    mapping['d1_d2_corner_clean_scaffold_v2.png']=v2.ART/'d1_d2_corner_clean.png'
    source_hashes={}
    for name,path in mapping.items():
        rel=path.relative_to(ROOT).as_posix()
        blob=subprocess.run(['git','show',f'{BASELINE}:{rel}'],cwd=ROOT,capture_output=True,check=True).stdout
        checks[f'source_{name}']=evidence(hashlib.sha256(blob).hexdigest(),d0.digest(PACKAGE/'sources'/name),'Hash package source against bytes read from pinned Git commit')
        checks[f'current_{name}']=evidence(hashlib.sha256(blob).hexdigest(),d0.digest(path),'Compare current source with pinned commit')
        source_hashes[rel]=d0.digest(path)
    rel=CONTRACT.relative_to(ROOT).as_posix()
    blob=subprocess.run(['git','show',f'{BASELINE}:{rel}'],cwd=ROOT,capture_output=True,check=True).stdout
    # Git stores LF; this Windows checkout uses CRLF. Compare pinned text after
    # only that checkout conversion, while separately locking exact task bytes.
    checks['contract_pinned_text']=evidence(hashlib.sha256(blob.replace(b'\r\n',b'\n')).hexdigest(),
        hashlib.sha256(CONTRACT.read_bytes().replace(b'\r\n',b'\n')).hexdigest(),
        'Compare pinned contract text allowing only Git LF/Windows CRLF checkout conversion')
    checks['contract_checkout_bytes']=evidence(d0.read_json(OUT/'production_before.json')['sha256'][rel],d0.digest(CONTRACT),
        'Exact before/after checkout hash; historical contract is never rewritten')
    return d1.group(checks,source_hashes=source_hashes,archive_sha256=d0.digest(archive),member_count=len(initial['members_sha256']))


def check_candidate(name,im,source,c,*,reference_path=None):
    geometry=v2.check_view(im,source,c,name)
    ref=d1.load(reference_path if reference_path is not None else v2.OUT/f'd2_{name}_native.png')
    checks={'dimensions_mode':evidence([ref.mode,list(ref.size)],[im.mode,list(im.size)],'Read native PNG mode and dimensions')}
    if im.mode!=ref.mode or im.size!=ref.size: return d1.group(checks,geometry=geometry)
    checks['alpha_changed']=evidence(0,d1.pixel_difference(im,ref,channels=(3,)),'Count native alpha differences against corresponding committed scaffold',units='pixels')
    checks['rgb_changed']=evidence(EXPECTED_RGB[name],d1.pixel_difference(im,ref,channels=(0,1,2)),'Count actual RGB pixel differences against corresponding committed scaffold',units='pixels')
    checks['zero_alpha_rgba_changed']=evidence(0,sum(a!=b for a,b in zip(im.get_flattened_data(),ref.get_flattened_data()) if b[3]==0),'Compare full RGBA at every originally zero-alpha pixel',units='pixels')
    result=d1.group(checks,geometry=geometry)
    result['pass']=result['pass'] and geometry['pass']
    return result


def relationships(views,c):
    checks={}
    for name in ('main','repeat'):
        checks[f'corner_{name}_body']=evidence(0,d1.pixel_difference(views[f'corner_{name}'].crop((0,24,12,56)),views[name]),'Compare all RGBA of saved corner body to supplied straight view',units='pixels')
    main,repeat=views['main'],views['repeat']; inside=outside=extension=0
    for y in range(32):
        for x in range(12):
            changed=main.getpixel((x,y))!=repeat.getpixel((x,y))
            if 2<=x<10 and 28<=y<32:
                inside+=changed; extension+=repeat.getpixel((x,y))!=main.getpixel((x,27))
            else: outside+=changed
    checks['repeat_outside_changes']=evidence(0,outside,'Read changes outside [2,28,10,32)')
    checks['repeat_inside_changes']=evidence(32,inside,'Count changed RGBA inside declared repeat extension')
    checks['repeat_extension']=evidence(0,extension,'Compare each extension pixel to actual candidate row27')
    supplied=d0.read_json(PACKAGE/'reports/d2_candidate_spec.json')
    for name,spec in c['views'].items():
        declared=supplied['views'][name]
        for key,local in [('render_origin_relative_to_cell','origin'),('image_anchor','image_anchor'),('logical_cell_anchor','cell_anchor')]:
            checks[f'{name}_{key}']=evidence(spec[local],declared[key],'Compare supplied placement metadata with unchanged committed contract')
        checks[f'{name}_anchor_mapping']=evidence(spec['origin'],[a-b for a,b in zip(declared['logical_cell_anchor'],declared['image_anchor'])],'Derive image origin from supplied anchors; rendered pixels tested separately')
    return d1.group(checks)


def save_reload(path,im):
    im.save(path)
    return d1.load(path)


def corner(views,delta=(0,0),label='original'):
    """Reconstruct separately at each grid origin, then inspect saved layers."""
    dx,dy=delta; size=(144+dx,140+dy)
    horizontal,_,_=d1.assemble(*[d1.load(d1.PACKAGE/'candidate'/d1.VIEW_FILES[n]) for n in ('main','repeat')],2)
    vertical,_,_=v2.assemble(views,2,corner=True)
    hp=(64+dx,36+dy); vp=(60+dx,36+dy)
    front=Image.new('RGBA',size); side=Image.new('RGBA',size)
    front.alpha_composite(horizontal,hp); side.alpha_composite(vertical,vp)
    front=save_reload(ART/f'corner_{label}_d1_layer.png',front); side=save_reload(ART/f'corner_{label}_d2_layer.png',side)
    background=save_reload(ART/f'corner_{label}_background.png',Image.new('RGBA',size,(225,226,213,255)))
    union=save_reload(ART/f'corner_{label}_structure.png',Image.alpha_composite(side,front))
    clean=save_reload(ART/f'corner_{label}_clean.png',Image.alpha_composite(background,union))
    shift=lambda r:[r[0]+dx,r[1]+dy,r[2]+dx,r[3]+dy]
    declared={(x,y) for r in ([64,36,68,40],[64,60,72,64]) for y in range(r[1]+dy,r[3]+dy) for x in range(r[0]+dx,r[2]+dx)}
    actual=set(); opaque=stacked=hidden=0
    for y in range(size[1]):
        for x in range(size[0]):
            a,b=side.getpixel((x,y))[3],front.getpixel((x,y))[3]
            if a and b:
                actual.add((x,y)); opaque+=a==b==255; stacked+=0<a<255 and 0<b<255
                hidden+=(0<a<255 and b==255) or (0<b<255 and a==255)
    top=min(y for y in range(size[1]) if front.getpixel((64+dx,y))[3])
    base=max(y for y in range(size[1]) if front.getpixel((64+dx,y))[3])+1
    cap=min(y for y in range(40+dy,size[1]) if side.getpixel((70+dx,y))[3])
    checks={'overlap_ownership':evidence(0,len(actual^declared),'Compare saved layer intersections with declared shifted rectangles'),
        'opaque_overlap':evidence(48,opaque,'Count two opaque input layers'),
        'stacked_glass':evidence(0,stacked,'Count two translucent input layers'),
        'hidden_glass':evidence(0,hidden,'Count glass occluded by other component frame'),
        'upper_contact':alpha_region(side,shift([64,36,68,40]),minimum=255,maximum=255),
        'return_glass':alpha_region(side,shift([62,40,64,60]),minimum=150,maximum=150),
        'return_frame':alpha_region(side,shift([60,36,62,64]),minimum=255,maximum=255),
        'side_cap':alpha_region(side,shift([60,60,72,64]),minimum=255,maximum=255),
        'cutaway':evidence(24,cap-top,'Scan actual saved top-post and shallow-cap alpha starts'),
        'baseline':evidence(64+dy,base,'Scan saved D1 left post bottom exclusive edge'),
        'D1_render_unchanged':anchored_component(union,horizontal,hp,hp),
        'saved_source_over':evidence(0,d1.pixel_difference(clean,Image.alpha_composite(background,Image.alpha_composite(side,front))),'Rebuild from separately saved background/layers')}
    cell=[vp[0]-12,vp[1]+24]; d2_center=[cell[0]+16,cell[1]]; d1_center=[hp[0],base-4]
    checks['centerline_intersection']=evidence(d1_center,d2_center,'Derive centers from actual render origins and the distinct D1 baseline edge')
    return d1.group(checks,computed={'D1_origin':list(hp),'D2_origin':list(vp),'D2_cell':cell,'intersection':d2_center,'D1_baseline_y':base,'D1_top_y':top,'D2_cap_y':cap,'opaque_overlap':opaque,'stacked_glass':stacked,'hidden_glass':hidden}),clean


def main():
    ART.mkdir(parents=True,exist_ok=True)
    c=d0.read_json(CONTRACT); views={n:candidate(n) for n in NAMES}
    integrity=package_integrity()
    files={n:check_candidate(n,views[n],candidate(n,'source_8x'),c) for n in NAMES}
    valid_shapes=all(views[n].mode=='RGBA' and list(views[n].size)==c['views'][n]['size'] for n in NAMES)
    rel=relationships(views,c) if valid_shapes else d1.group({'input_geometry':evidence(True,False,'Relationships require declared input dimensions and RGBA mode')})
    repeats={}; corners={}; contexts={}; negatives={}
    # Do not normalize or repair a failed input, or run shape-dependent helpers on it.
    inputs_ok=integrity['pass'] and all(v['pass'] for v in files.values()) and rel['pass']
    if inputs_ok:
        for n in (1,2,4):
            for is_corner in (False,True):
                key=('corner_' if is_corner else 'straight_')+str(n)
                run,origins,layers=v2.assemble(views,n,corner=is_corner)
                run=save_reload(ART/f'{key}_native.png',run)
                offset=24 if is_corner else 0
                body=run.crop((0,offset,12,offset+32*n)); body_layers=layers.crop((0,offset,12,offset+32*n))
                body_origins=[[0,p[1]-offset] if i else [0,0] for i,p in enumerate(origins)]
                qa=v2.check_run(body,body_origins,body_layers,n)
                expected_origins=[[0,0]]+[[0,32*i+offset] for i in range(1,n)]
                extra={'origins':evidence(expected_origins,origins,'Read actual placement sequence with corner north extension'),
                    'single_layer':evidence(1,max(layers.get_flattened_data()),'Maximum actual translucent draw contributions')}
                mismatches=0
                for i in range(n):
                    name=('corner_' if is_corner and i==0 else '')+('main' if i==n-1 else 'repeat')
                    im=views[name]; y=origins[i][1]
                    mismatches+=d1.pixel_difference(run.crop((0,y,12,y+im.height)),im)
                extra['candidate_rgba']=evidence(0,mismatches,'Compare each assembled cell with selected supplied candidate, not scaffold RGB')
                trans,backs,obj,scenes=v2.transmission(run)
                for name,bg in backs.items():
                    save_reload(ART/f'{key}_{name}_background.png',bg)
                    save_reload(ART/f'{key}_{name}_composite.png',scenes[name])
                obj.save(ART/f'{key}_object_layer.png')
                repeats[key]={'geometry':qa,'selection':d1.group(extra),'transmission':trans}
        for name,delta in [('original',(0,0)),('relocated',(32,32))]: corners[name],_=corner(views,delta,name)
        original=d1.load(ART/'corner_original_structure.png'); moved=d1.load(ART/'corner_relocated_structure.png')
        corners['relocation_pixels']=d1.group({'translation':evidence(0,d1.pixel_difference(original,moved.crop((32,32,32+original.width,32+original.height))),'Compare independently placed corner structures after removing known grid relocation')})
        run=d1.load(ART/'straight_2_native.png')
        for name,cell in [('original',(32,64)),('relocated',(64,96))]:
            qa,scene,bg,structure=v2.context(run,cell)
            for suffix,im in [('scene',scene),('background',bg),('structure',structure)]: save_reload(ART/f'wall_context_{name}_{suffix}.png',im)
            saved=d1.load(ART/f'wall_context_{name}_structure.png')
            qa['checks']['saved_candidate']=anchored_component(saved,run,(cell[0]+12,cell[1]),(cell[0]+12,cell[1]))
            qa['checks']['saved_composite']=evidence(0,d1.pixel_difference(d1.load(ART/f'wall_context_{name}_scene.png'),Image.alpha_composite(d1.load(ART/f'wall_context_{name}_background.png'),saved)),'Compare saved wall scene with separate approved floor and structure')
            qa['pass']=all(q['pass'] for q in qa['checks'].values()); contexts[name]=qa
        negatives=v2.negatives(views)
        for name,q in negatives.items(): q['image'].save(ART/f'broken_{name}.png')
        source=candidate('main','source_8x'); source.putpixel((0,0),(1,2,3,255)); bad=check_candidate('main',views['main'],source,c)
        negatives['source_subpixel']={'image':source,'valid_control_pass':files['main']['pass'],'proven':files['main']['pass'] and not bad['geometry']['checks']['blocks']['pass'],'intended_check':'exact 8x blocks','validation':bad}
        source.save(ART/'broken_source_subpixel.png')
        # Diagnostic markings are on copies only; neither candidate nor sources are written.
        clean=d1.load(ART/'corner_original_clean.png'); annotated=clean.copy(); draw=ImageDraw.Draw(annotated)
        draw.line((48,60,128,60),fill=(240,184,35,255)); draw.line((64,32,64,124),fill=(240,184,35,255)); draw.line((68,64,128,64),fill=(240,65,151,255))
        for r in ([64,36,68,40],[64,60,72,64]): draw.rectangle((r[0],r[1],r[2]-1,r[3]-1),outline=(55,217,158,255))
        v2.labeled_panel(annotated,'Independent D2 appearance: corner geometry',[
            'Gold centerlines: (64,60). Pink baseline: y64. Cutaway: 24px.',
            'Green: declared 48 opaque overlap pixels. Zero hidden/stacked glass.',
            'D2 origin (60,36), image anchor (4,40); D1 unchanged.'],factor=4).save(ART/'corner_annotated.png')
        region_panels=[]
        for n in NAMES:
            im=views[n].resize((views[n].width*8,views[n].height*8),Image.Resampling.NEAREST); draw=ImageDraw.Draw(im)
            for r in c['views'][n]['pane']: draw.rectangle((r[0]*8,r[1]*8,r[2]*8-1,r[3]*8-1),outline=(238,185,39,255),width=1)
            region_panels.append(v2.labeled_panel(im,n+': outlined pane / frame alpha255 / glass150',factor=1))
        v2.stack([v2.row(region_panels[:2]),v2.row(region_panels[2:])]).save(ART/'geometry_alpha_diagnostic.png')
        repeat_sheet=Image.new('RGBA',(120,152),(225,226,213,255))
        for i,n in enumerate((1,2,4)): repeat_sheet.alpha_composite(d1.load(ART/f'corner_{n}_object_composite.png'),(8+i*40,0))
        transmit=Image.new('RGBA',(120,88),(225,226,213,255))
        for i,n in enumerate(('light','dark','colored','object')): transmit.alpha_composite(d1.load(ART/f'corner_2_{n}_composite.png'),(8+i*28,0))
        montage=v2.stack([v2.row([v2.labeled_panel(clean,'D2 appearance: independent clean corner',factor=4),d1.load(ART/'corner_annotated.png')]),
            v2.row([v2.labeled_panel(repeat_sheet,'1 / 2 / 4 corner runs from supplied RGBA',factor=3),v2.labeled_panel(transmit,'Light / dark / colored / separate-object background',factor=4)]),
            v2.row([v2.labeled_panel(d1.load(ART/'corner_relocated_clean.png'),'Corner independently relocated +32,+32',factor=2),v2.labeled_panel(d1.load(ART/'wall_context_relocated_scene.png'),'Unchanged approved walls/floor: relocated context',factor=2)])])
        montage.save(ART/'d2_appearance_review_montage.png')
    preservation=compare_snapshots(d0.read_json(OUT/'production_before.json'),v1.snapshot(),allowed_addition_prefixes=(PREFIX,))
    success=inputs_ok and all(all(x['pass'] for x in q.values()) for q in repeats.values()) and all(q['pass'] for q in corners.values()) and all(q['pass'] for q in contexts.values()) and all(q['proven'] for q in negatives.values()) and preservation['pass']
    report={'status':'PASS' if success else 'FAIL','scope':'REFERENCE_ONLY_TECHNICAL_APPEARANCE_VALIDATION',
        'geometry_contract_status':c['status'],'geometry_contract_sha256':d0.digest(CONTRACT),'coordinate_convention':c['rectangle_convention'],
        'package_integrity':integrity,'files':files,'relationships':rel,'repeats':repeats,'corners':corners,'wall_contexts':contexts,
        'negative_controls':{name:{k:v for k,v in q.items() if k!='image'} for name,q in negatives.items()},'preservation':preservation,
        'review_evidence':{'user_supplied':'ChatGPT reviewed geometry for an appearance trial and reviewed the supplied candidate. This is not human production approval.',
            'human_production_approval':False,'limits':'Deliberate shallow cutaway; no full-height side-wall claim and no all-direction junction validation.'}}
    if (OUT/'test_results.json').exists():
        report['tests']=d0.read_json(OUT/'test_results.json')
        if report['tests']['exit_code']!=0: report['status']='FAIL'; success=False
    if (OUT/'visual_review.json').exists(): report['assistant_visual_findings']=d0.read_json(OUT/'visual_review.json')
    def failures(value,path=''):
        result=[]
        if isinstance(value,dict):
            if value.get('pass') is False and 'expected' in value: result.append({'check':path,**value})
            for k,v in value.items(): result+=failures(v,path+'/'+str(k))
        return result
    report['blockers']=failures({k:report[k] for k in ('package_integrity','files','relationships','repeats','corners','wall_contexts')})
    if not preservation['pass']: report['blockers'].append({'check':'preservation','details':preservation})
    for name,q in negatives.items():
        if not q['proven']: report['blockers'].append({'check':'negative_control/'+name,'details':'Valid control did not pass or intended defect was not rejected'})
    if 'tests' in report and report['tests']['exit_code']!=0: report['blockers'].append({'check':'complete_test_suite','details':report['tests']})
    d0.write_json(OUT/'production_preservation.json',preservation); d0.write_json(OUT/'d2_appearance_validation_report.json',report)
    lines=['# Independent D2 appearance validation','',f"**{report['status']}** — reference-only technical validation. Historical contract stays `{c['status']}`. No production approval.",'',
        'Actual saved candidate PNGs were read; no montage crops or package builders were used. Expected/spec, computed observations, derived placement and review evidence are separate in JSON.','',
        '| View | Native RGBA | Source RGBA | Alpha changed | RGB changed | Zero-alpha RGBA changed |','| --- | --- | --- | ---: | ---: | ---: |']
    for name,q in files.items():
        g=q['geometry']['checks']; checks=q['checks']
        lines.append(f"| {name} | {g['size']['observed']} | {g['source_size']['observed']} | {checks.get('alpha_changed',{}).get('observed','unavailable')} | {checks.get('rgb_changed',{}).get('observed','unavailable')} | {checks.get('zero_alpha_rgba_changed',{}).get('observed','unavailable')} |")
    lines += ['',f"Package integrity: {integrity['pass']}; {integrity['member_count']} extracted members and original archive preserved. Packaged source copies match pinned Git sources. Exact nearest-neighbor 8x blocks, alpha regions, and native roundtrips were independently checked.",'',
        f"View relationships/anchors: {rel['pass']}. Main/repeat image anchor [4,16], origin [12,0]; corner image anchor [4,40], origin [12,-24]; logical-cell anchor [16,16]. Four mutually exclusive implementation views belong to one future logical asset. Corner bodies equal corresponding straight candidates; repeat only extends candidate row27 within [2,28,10,32).",'']
    for key,q in repeats.items(): lines.append(f"- {key}: geometry {q['geometry']['pass']}, candidate selection {q['selection']['pass']}, transmission {q['transmission']['pass']}.")
    for key in ('original','relocated'):
        if key in corners: lines+=['',f"Corner {key}: {corners[key]['computed']}. All declared corner checks pass: {corners[key]['pass']}."]
    lines += ['', 'Draw order is separate background, D2, unchanged D1. Required top contact, glazed reveal and return frame are checked separately from the baseline. Straight/corner runs preserve 32px ground stride, single 4px supports and terminal closure. Glass alpha150 transmits separate light/dark/colored/object backgrounds; opaque frame alpha255 remains invariant. Approved Batch11 wall/floor contexts are rebuilt independently at original and relocated origins.','', '## Negative controls','']
    for name,q in negatives.items(): lines.append(f"- {name}: valid control {q['valid_control_pass']}; intended rejection proven {q['proven']} ({q['intended_check']}).")
    lines+=['',f"Protected files: {preservation['protected_file_count']}; changed {preservation['changed']}; missing {preservation['missing']}. Counts before/after: {preservation['expected_counts']} / {preservation['observed_counts']}. Historical contracts, reports, snapshots, D1 and approved artwork remain unchanged.",'',
        'The only historical test adjustment permits additions in this named workspace; existing hashes remain mandatory, including within allowed directories. Package sources additionally have immutable archive/member hash checks.','',
        'Run `python tools/validate_architecture_d2_appearance.py`; full suite `python -m pytest -q`. Baseline verified: 124 passed.']
    if 'tests' in report: lines+=['',f"Captured complete suite: {report['tests']['passed']} passed; exit {report['tests']['exit_code']}."]
    lines+=['',f"Blockers: {report['blockers']}",'','ChatGPT review is supporting appearance evidence. No final human production approval, ingestion, Batch13, D3 or all-direction junction coverage is claimed.','']
    (OUT/'d2_appearance_validation_report.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'status':report['status'],'blockers':report['blockers'],'counts':preservation['observed_counts'],'protected':preservation['protected_file_count']},indent=2))
    return 0 if success else 1


if __name__=='__main__': raise SystemExit(main())
