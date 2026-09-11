"""Independent D4 saved-file validation. Never executes package code or edits art."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import subprocess
import zipfile
from PIL import Image, ImageDraw
import validate_architecture_d0 as d0
import validate_architecture_d1 as d1
import validate_architecture_d2 as history
import validate_architecture_d2_v2 as side
import validate_architecture_d2_appearance as d2app
import validate_architecture_d3 as d3
import validate_architecture_d3_appearance as d3app
import validate_architecture_d4 as d4
from rastalr_pipeline.geometry import evidence
from rastalr_pipeline.snapshot import compare_snapshots

ROOT=d0.ROOT
PREFIX='references/architecture/master_validation_D4_appearance_v1/'
OUT=ROOT/PREFIX
ART=OUT/'artifacts'
PACKAGE=OUT/'sources/package'
CONTRACT=d4.OUT/'d4_geometry_alpha_contract_proposed.json'
BASELINE='2ec243597e60f55435983d2de6a64592273d5f6f'
STEM='rastalr_D4_glass_partition_front_cutaway_locked_v1_'
HIST={'main':{'150':144,'255':240},'repeat':{'150':168,'255':216}}


def candidate(name,scale='native'):
    return d1.load(PACKAGE/'candidate'/f'{STEM}{name}_{scale}.png')


def integrity():
    initial=d0.read_json(OUT/'package_provenance.json');archive=OUT/'sources'/initial['archive_name']
    checks={'archive':evidence(initial['archive_sha256'],d0.digest(archive),'SHA-256 versus immutable original archive hash')}
    with zipfile.ZipFile(archive) as z:
        names=sorted(z.namelist())
        checks['members']=evidence(names,sorted(p.relative_to(PACKAGE).as_posix() for p in PACKAGE.rglob('*') if p.is_file()),'Enumerate extracted files')
        checks['member_bytes']=evidence([], [n for n in names if not (PACKAGE/n).is_file() or (PACKAGE/n).read_bytes()!=z.read(n)],'Exact bytes versus original archive')
    checks['initial_hashes']=evidence([], [n for n,h in initial['members_sha256'].items() if not (PACKAGE/n).is_file() or d0.digest(PACKAGE/n)!=h],'Every immutable extraction hash')
    sums={n:h for h,n in (line.split('  ',1) for line in (PACKAGE/'SHA256SUMS.txt').read_text().splitlines())}
    checks['supplied_checksums']=evidence([], [n for n,h in sums.items() if d0.digest(PACKAGE/n)!=h],'Independently measure supplied checksum claims')
    mapping={f'd4_{n}_native.png':d4.OUT/f'd4_{n}_native.png' for n in d4.NAMES}
    mapping.update({f'{n}_clean.png':d4.ART/f'{n}_clean.png' for n in ('southwest','southeast')})
    mapping.update({d1.VIEW_FILES[n]:d1.PACKAGE/'candidate'/d1.VIEW_FILES[n] for n in d4.NAMES})
    mapping.update({f'{app.STEM}{n}_native.png':app.PACKAGE/'candidate'/f'{app.STEM}{n}_native.png' for app in (d2app,d3app) for n in d3.NAMES})
    mapping['hospital_floor_plain_01.png']=ROOT/'assets/architecture/hospital_floor_plain_01.png'
    supplied=d0.read_json(PACKAGE/'reports/reference_sources.json')
    checks['reference_names']=evidence(sorted(mapping),sorted(supplied),'Compare independently established repository reference map')
    for name,path in mapping.items():
        rel=path.relative_to(ROOT).as_posix();blob=subprocess.run(['git','show',f'{BASELINE}:{rel}'],cwd=ROOT,capture_output=True,check=True).stdout
        h=hashlib.sha256(blob).hexdigest();git_hash=hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest();claim=supplied.get(name,{})
        checks[name+'_reference']=evidence([BASELINE,rel,h,git_hash],[claim.get('commit'),claim.get('path'),claim.get('sha256'),claim.get('git_blob_sha1')],'Compare package claims to independently read pinned Git object')
        checks[name+'_package']=evidence(h,d0.digest(PACKAGE/'sources'/name),'Exact PNG bytes against pinned commit')
        checks[name+'_checkout']=evidence(h,d0.digest(path),'Current PNG bytes against pinned commit')
    rel=CONTRACT.relative_to(ROOT).as_posix();blob=subprocess.run(['git','show',f'{BASELINE}:{rel}'],cwd=ROOT,capture_output=True,check=True).stdout
    checks['contract_git_blob']=evidence('f8d9fb67256addda31ed6f94f0e08004c0d8ccf2',hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest(),'Compute pinned contract Git blob SHA-1')
    checks['contract_pinned_bytes']=evidence(hashlib.sha256(blob).hexdigest(),d0.digest(CONTRACT),'Exact text bytes; no newline normalization required for D4')
    checks['contract_checkout_hash']=evidence(d0.read_json(OUT/'production_before.json')['sha256'][rel],d0.digest(CONTRACT),'Immutable task-start checkout hash')
    return d1.group(checks,member_count=len(names),pinned_references=len(mapping),newline_normalization=False)


def check_file(name,im,export,c):
    q=d2app.check_candidate(name,im,export,c,reference_path=d4.OUT/f'd4_{name}_native.png')
    if im.mode=='RGBA':
        q['checks']['histogram']=evidence(HIST[name],{str(a):n for a,n in Counter(im.getchannel('A').get_flattened_data()).items()},'Count actual alpha samples')
        q['pass'] &= q['checks']['histogram']['pass']
    return q


def relationships(views,c):
    main,repeat=views['main'],views['repeat'];outside=inside=extension=0
    for y in range(12):
        for x in range(32):
            a,b=main.getpixel((x,y)),repeat.getpixel((x,y))
            if 28<=x<32 and 4<=y<10:inside+=a!=b;extension+=b!=main.getpixel((27,y))
            else:outside+=a!=b
    checks={'outside':evidence(0,outside,'Count actual RGBA changes outside [28,4,32,10)'),
        'extension':evidence(0,extension,'Compare each repeat continuation pixel with actual main column27'),
        'changed_inside':evidence(24,inside,'Count actual changed pixels in declared continuation'),
        'upper_trim':evidence(0,d1.pixel_difference(main.crop((0,0,32,4)),repeat.crop((0,0,32,4))),'Compare upper trim RGBA'),
        'lower_rail':evidence(0,d1.pixel_difference(main.crop((0,10,32,12)),repeat.crop((0,10,32,12))),'Compare lower rail RGBA')}
    meta=d0.read_json(PACKAGE/'reports/d4_candidate_spec.json');canonical=c['canonical_requirements'];view=c['views']['main']
    expected={'logical_grid':canonical['grid'],'source_scale':canonical['scale'],'logical_footprint':canonical['footprint'],
        'normalization':canonical['normalization'],'cell_anchor':view['cell_anchor'],'image_anchor':view['image_anchor'],'origin_relative_to_cell':view['origin']}
    for k,v in expected.items():checks[k]=evidence(v,meta.get(k),'Compare supplied metadata with unchanged contract; placement measured separately')
    checks['anchor_arithmetic']=evidence(view['origin'],[a-b for a,b in zip(meta['cell_anchor'],meta['image_anchor'])],'Derive cell-to-image mapping from supplied anchors')
    return d1.group(checks)


def run_evidence(views,n):
    run,p,cov=d4.assemble(views,n);run=d4.saved(ART/f'run_{n}_native.png',run)
    cov=d4.saved(ART/f'run_{n}_coverage.png',cov.convert('L'))
    geometry=d4.check_run(run,p,cov,n)
    selected=sum(d1.pixel_difference(run.crop((32*i,0,32*i+32,12)),views['main' if i==n-1 else 'repeat']) for i in range(n))
    selection=d1.group({'selected_rgba':evidence(0,selected,'Compare saved run against actual candidate views, not scaffold RGB')})
    transmission,backs,obj,scenes=side.transmission(run)
    for name,bg in backs.items():d4.saved(ART/f'run_{n}_{name}_background.png',bg);d4.saved(ART/f'run_{n}_{name}_composite.png',scenes[name])
    d4.saved(ART/f'run_{n}_object_layer.png',obj)
    return {'geometry':geometry,'selection':selection,'transmission':transmission}


def compare_scenes(scene,scaffold,coverage):
    changed=outside=0
    for a,b,p in zip(scene.get_flattened_data(),scaffold.get_flattened_data(),coverage.get_flattened_data()):
        changed+=a!=b;outside+=a!=b and p[3]==0
    return d1.group({'outside_D4':evidence(0,outside,'Compare saved appearance/scaffold scenes pixel by pixel outside actual D4 rendered coverage')},computed={'changed_scene_pixels':changed})


def assembly_evidence(views,name,w,d,delta):
    label='enclosure_'+name;scaffolds={n:d1.load(d4.OUT/f'd4_{n}_native.png') for n in d4.NAMES}
    q,scene,structure=d4.enclosure(views,w,d,delta,label=label,artifact_dir=ART)
    base,scaffold,_=d4.enclosure(scaffolds,w,d,delta,label='scaffold_'+name,artifact_dir=ART)
    checks={'candidate_geometry':q,'scaffold_control':base}
    coverage=d1.load(ART/f'{label}_d4_layer.png')
    checks['scene_scope']=compare_scenes(d1.load(ART/f'{label}_clean.png'),d1.load(ART/f'scaffold_{name}_clean.png'),coverage)
    checks['object_scene_scope']=compare_scenes(d1.load(ART/f'{label}_object_composite.png'),d1.load(ART/f'scaffold_{name}_object_composite.png'),coverage)
    for layer in ('d1','d2','d3','background','object_layer'):
        suffix=layer+'_layer' if layer in ('d1','d2','d3') else layer
        checks[layer+'_unchanged_bytes']=evidence(d0.digest(ART/f'scaffold_{name}_{suffix}.png'),d0.digest(ART/f'{label}_{suffix}.png'),'Compare saved unchanged input-layer PNG bytes between assemblies')
    replay=Image.new('RGBA',structure.size)
    for layer in ('d2','d3','d1','d4'):replay.alpha_composite(d1.load(ART/f'{label}_{layer}_layer.png'))
    checks['saved_structure']=evidence(0,d1.pixel_difference(replay,d1.load(ART/f'{label}_structure.png')),'Recompose saved individual RGBA layers')
    checks['saved_scene']=evidence(0,d1.pixel_difference(Image.alpha_composite(d1.load(ART/f'{label}_background.png'),replay),d1.load(ART/f'{label}_clean.png')),'Recompose saved background and saved structure')
    g=q['derived'];sy=g['south_centerline']
    for corner,edge in [('southwest',g['west']),('southeast',g['east'])]:
        crop=(edge-16,sy-20,edge+20,sy+16);im=d4.saved(ART/f'{name}_{corner}_clean.png',scene.crop(crop))
        if name=='local':checks[corner+'_historical_crop']=evidence(0,d1.pixel_difference(scaffold.crop(crop),d1.load(d4.ART/f'{corner}_clean.png')),'Reproduce committed36x36 scaffold corner from2x1 assembly; never use crop as artwork')
        if name=='original':
            anno=im.resize((288,288),Image.Resampling.NEAREST);draw=ImageDraw.Draw(anno)
            draw.line((0,160,287,160),fill=(238,177,40,255),width=2);draw.line((128,0,128,287),fill=(238,177,40,255),width=2)
            draw.line((0,224,287,224),fill=(239,62,150,255),width=2)
            l,t,r,b=q['checks'][corner]['derived']['front_contact'];draw.rectangle(((l-crop[0])*8,(t-crop[1])*8,(r-crop[0])*8-1,(b-crop[1])*8-1),outline=(53,217,165,255),width=2)
            side.labeled_panel(anno,corner+' independent appearance reconstruction',[
                f'Gold center ({edge},{sy}); pink base {sy+8}; trim {sy-4}..{sy}.',
                'Green declared opaque contact; actual32px, no hidden/stacked glass.',
                'Actual validated side terminal retained; no masking or source edits.'],factor=1).save(ART/f'{corner}_annotated.png')
    return d1.group(checks)


def negative_controls(views,c):
    cases=d4.negative_controls(views);valid=relationships(views,c)
    for name,pos,key in [('repeat_rgb_outside',(6,2),'outside'),('repeat_rgb_continuation',(30,6),'extension')]:
        broken={n:im.copy() for n,im in views.items()};rgba=broken['repeat'].getpixel(pos)
        broken['repeat'].putpixel(pos,(1,2,3,rgba[3]));bad=relationships(broken,c)
        cases[name]={'image':broken['repeat'],'validation':bad,'valid_control_pass':valid['pass'],'intended_check':key,'proven':valid['pass'] and not bad['checks'][key]['pass']}
    return cases


def main():
    ART.mkdir(parents=True,exist_ok=True);c=d0.read_json(CONTRACT);views={n:candidate(n) for n in d4.NAMES}
    package=integrity();files={n:check_file(n,views[n],candidate(n,'source_8x'),c) for n in d4.NAMES}
    shapes=all(im.mode=='RGBA' and im.size==(32,12) for im in views.values())
    rel=relationships(views,c) if shapes else d1.group({'shape':evidence(True,False,'Relationships require declared input shape')})
    valid=package['pass'] and all(q['pass'] for q in files.values()) and rel['pass'];runs={};assemblies={};neg={}
    if valid:
        runs={str(n):run_evidence(views,n) for n in (1,2,4)}
        for name,w,d,delta in [('local',2,1,(0,0)),('original',4,2,(0,0)),('relocated',4,2,(32,32)),('additional_size',3,3,(0,0))]:assemblies[name]=assembly_evidence(views,name,w,d,delta)
        first=d1.load(ART/'enclosure_original_structure.png');moved=d1.load(ART/'enclosure_relocated_structure.png')
        assemblies['relocation']=d1.group({'translated_pixels':evidence(0,d1.pixel_difference(first,moved.crop((32,32,32+first.width,32+first.height))),'Independently rebuilt saved structures after removing translation')})
        neg=negative_controls(views,c)
        for name,q in neg.items():d4.saved(ART/f'broken_{name}.png',q['image'])
        side.stack([side.labeled_panel(views[n],n+': actual saved32x12; frame255, pane150; repeat continuation [28,4,32,10)',factor=8) for n in d4.NAMES]).save(ART/'geometry_alpha_relationship_diagnostic.png')
        panels=[side.row([d1.load(ART/f'{n}_annotated.png') for n in ('southwest','southeast')]),
            side.row([side.labeled_panel(d1.load(ART/f'original_{n}_clean.png'),n+' actual candidate clean',factor=8) for n in ('southwest','southeast')]),
            side.labeled_panel(d1.load(ART/'enclosure_original_object_composite.png'),'Unchanged D1/D2/D3 + supplied D4 / separate object',factor=4),
            side.row([side.labeled_panel(views[n],'Saved candidate '+n,factor=8) for n in d4.NAMES]),
            side.stack([side.labeled_panel(d1.load(ART/f'run_{n}_colored_composite.png'),f'{n} cells;32px stride;4px shared posts',factor=4) for n in (1,2,4)]),
            side.stack([side.row([side.labeled_panel(d1.load(ART/f'run_1_{n}_composite.png'),n+' background',factor=6) for n in pair]) for pair in (('light','dark'),('colored','object'))]),
            side.row([side.labeled_panel(d1.load(ART/f'enclosure_{n}_clean.png'),n.replace('_',' '),factor=2) for n in ('relocated','additional_size')])]
        side.stack(panels).save(ART/'d4_appearance_review_montage.png')
    preservation=compare_snapshots(d0.read_json(OUT/'production_before.json'),history.snapshot(),allowed_addition_prefixes=(PREFIX,))
    report={'scope':'INDEPENDENT_REFERENCE_ONLY_APPEARANCE_VALIDATION','contract_status':c['status'],
        'rectangle_convention':c['rectangle_convention'],'geometry_authority':{'commit':BASELINE,'contract_path':CONTRACT.relative_to(ROOT).as_posix()},
        'package_integrity':package,'files':files,'relationships':rel,'runs':runs,'assemblies':assemblies,
        'negative_controls':{n:{k:v for k,v in q.items() if k!='image'} for n,q in neg.items()},'preservation':preservation,
        'review_evidence':{'user_reported':'ChatGPT geometry/appearance review supports independent validation, not human production approval.','human_production_approval':False,'limits':'Existing foreground cutaway and shoulders; no entrance or all-direction junction claim.'}}
    blockers=d4.failures({k:report[k] for k in ('package_integrity','files','relationships','runs','assemblies')})
    if not preservation['pass']:blockers.append({'check':'preservation','details':preservation})
    for name,q in neg.items():
        if not q['proven']:blockers.append({'check':'negative/'+name,'reason':'Valid control failed or defect escaped'})
    if (OUT/'test_results.json').exists():
        report['tests']=d0.read_json(OUT/'test_results.json')
        if report['tests']['exit_code']!=0:blockers.append({'check':'suite','details':report['tests']})
    if (OUT/'visual_review.json').exists():report['assistant_visual_findings']=d0.read_json(OUT/'visual_review.json')
    report.update(status='FAIL' if blockers else 'PASS',blockers=blockers)
    d0.write_json(OUT/'package_integrity.json',package);d0.write_json(OUT/'production_preservation.json',preservation);d0.write_json(OUT/'d4_appearance_validation_report.json',report)
    lines=['# Independent D4 appearance validation','',f"**{report['status']}**. Reference-only; historical contract remains `{c['status']}`. No human production approval.",'',
        'Actual supplied saved RGBA files were read without conversion or repair. Package builder inspected but never executed; local PASS claims were not copied.','',
        '| View | Native | Source | RGB changes | Alpha changes | Histogram |','| --- | --- | --- | ---: | ---: | --- |']
    for name,q in files.items():
        g=q['geometry']['checks'];f=q['checks'];lines.append(f"| {name} | {g['size']['observed']} | {g['source_size']['observed']} | {f.get('rgb_changed',{}).get('observed')} | {f.get('alpha_changed',{}).get('observed')} | {f.get('histogram',{}).get('observed')} |")
    lines+=['',f"Original archive plus {package['member_count']} members preserved; all {package['pinned_references']} reference copies compared to pinned Git bytes. Contract blob SHA1 checked exactly; no newline normalization needed.",'',
        'Every8x8 block and native roundtrip checked. Alpha255 frame and150 glass match the contract. Tight carriers have no internal exterior pixels. Cell anchor[16,16], image anchor[16,4], origin[0,12], stride[32,0], normalization architecture_grid_preserving. These mappings are contract/metadata; rendered anchors are checked separately.','',
        f"View relationships pass: {rel['pass']}. Only24 continuation pixels differ, each copied from actual main column27; upper trim/lower rail unchanged. Two mutually exclusive views are ONE future logical asset.",'']
    for name,q in runs.items():
        t=q['transmission']['checks']
        lines.append(f"- Run{name}: geometry {q['geometry']['pass']}, selected actual RGBA {q['selection']['pass']}, transmission {q['transmission']['pass']}; responding pane pixels {t['pane_response']['observed']}, object response {t['object_response']['observed']}, frame response errors {t['frame_invariance']['observed']}.")
    for name,q in assemblies.items():
        if 'candidate_geometry' not in q['checks']:continue
        g=q['checks']['candidate_geometry'];lines+=['',f"{name}: {g['derived']}. Assembly pass {q['pass']}."]
        for corner in ('southwest','southeast'):
            result=g['checks'][corner];lines.append(f"- {corner}: {result['computed']}; independently measured overlap {result['checks']['overlap']['computed']}.")
        for corner in ('northwest','northeast'):lines.append(f"- {corner} retained: {g['checks'][corner]['computed']}.")
        lines.append(f"Changed scene pixels {q['checks']['scene_scope']['computed']}; off-D4 violations {q['checks']['scene_scope']['checks']['outside_D4']['observed']}. D1/D2/D3 saved input-layer bytes unchanged.")
    lines+=['','Ground center S, side terminal/trim[S-4,S), pane[S,S+6), base S+8 and ground strip[S-4,S+4) remain distinct. D4 draws over only its declared opaque contacts. Side shoulders retained; no masking or source edits. Original4x2, independently relocated+32,+32 and3x3 tested. Both historical36x36 corner crops reproduced independently with the saved scaffold2x1 control.','', '## Negative controls','']
    for name,q in neg.items():lines.append(f"- {name}: valid {q['valid_control_pass']}; intended `{q['intended_check']}` failure proven {q['proven']}.")
    lines+=['',f"Protected files {preservation['protected_file_count']}; changed {preservation['changed']}; missing {preservation['missing']}. Counts before/after {preservation['expected_counts']} / {preservation['observed_counts']}.",'',
        'Only new files in this named workspace are allowed. Existing hashes, including inside allowed prefixes, remain mandatory. Historical reports, contracts, snapshots and production records remain unchanged.','',
        'Reproduce: `python tools/validate_architecture_d4_appearance.py`. Full suite: `python -m pytest -q`. Starting suite269 passed.']
    if 'tests' in report:lines+=['',f"Captured suite: {report['tests']}."]
    lines+=['',f"Blockers: {blockers}",'','No repaint, geometry change, approval, ingestion, Batch13, D5 or unrelated junction repair.','']
    (OUT/'d4_appearance_validation_report.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'status':report['status'],'blockers':blockers,'members':package['member_count'],'protected':preservation['protected_file_count'],'counts':preservation['observed_counts']},indent=2))
    return 1 if blockers else 0


if __name__=='__main__':raise SystemExit(main())
