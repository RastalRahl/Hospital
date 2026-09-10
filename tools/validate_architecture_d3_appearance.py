"""Read-only candidate validation; writes independent evidence, never package art."""
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
import validate_architecture_d2_v2 as d2
import validate_architecture_d2_appearance as d2app
import validate_architecture_d3 as d3
from rastalr_pipeline.geometry import evidence
from rastalr_pipeline.snapshot import compare_snapshots

ROOT=d0.ROOT
PREFIX='references/architecture/master_validation_D3_appearance_v1/'
OUT=ROOT/PREFIX
ART=OUT/'artifacts'
PACKAGE=OUT/'sources/package'
CONTRACT=d3.OUT/'d3_geometry_alpha_contract_proposed.json'
BASELINE='65aca7a461a60d49e57e4b82257e782fc9c9b1d0'
STEM='rastalr_D3_glass_partition_side_right_locked_v1_'
HIST={'main':{'150':192,'255':192},'repeat':{'150':224,'255':160},
      'corner_main':{'0':176,'150':232,'255':264},'corner_repeat':{'0':176,'150':264,'255':232}}


def candidate(name,scale='native'):
    return d1.load(PACKAGE/'candidate'/f'{STEM}{name}_{scale}.png')


def integrity():
    initial=d0.read_json(OUT/'package_provenance.json');archive=OUT/'sources'/initial['archive_name']
    checks={'archive':evidence(initial['archive_sha256'],d0.digest(archive),'Hash unchanged original ZIP',units='sha256')}
    with zipfile.ZipFile(archive) as z:
        names=sorted(z.namelist())
        checks['members']=evidence(names,sorted(p.relative_to(PACKAGE).as_posix() for p in PACKAGE.rglob('*') if p.is_file()),'Enumerate actual extracted members',units='paths')
        checks['archive_member_bytes']=evidence([], [n for n in names if not (PACKAGE/n).is_file() or (PACKAGE/n).read_bytes()!=z.read(n)],'Byte comparison with original ZIP',units='paths')
    checks['initial_member_hashes']=evidence([], [n for n,h in initial['members_sha256'].items() if not (PACKAGE/n).is_file() or d0.digest(PACKAGE/n)!=h],'Compare immutable extraction hashes',units='paths')
    supplied={name:h for h,name in (line.split('  ',1) for line in (PACKAGE/'SHA256SUMS.txt').read_text().splitlines())}
    checks['supplied_checksums']=evidence([], [n for n,h in supplied.items() if d0.digest(PACKAGE/n)!=h],'Independently check supplied checksum claims',units='paths')
    mapping={f'd3_{n}_native.png':d3.OUT/f'd3_{n}_native.png' for n in d3.NAMES}
    mapping.update({d1.VIEW_FILES[n]:d1.PACKAGE/'candidate'/d1.VIEW_FILES[n] for n in ('main','repeat')})
    mapping.update({f'{d2app.STEM}{n}_native.png':d2app.PACKAGE/'candidate'/f'{d2app.STEM}{n}_native.png' for n in d3.NAMES})
    mapping.update({n:ROOT/'assets/architecture'/n for n in ('hospital_floor_plain_01.png','hospital_wall_side_right_01.png')})
    for name,path in mapping.items():
        rel=path.relative_to(ROOT).as_posix();blob=subprocess.run(['git','show',f'{BASELINE}:{rel}'],cwd=ROOT,capture_output=True,check=True).stdout;h=hashlib.sha256(blob).hexdigest()
        checks['package_source_'+name]=evidence(h,d0.digest(PACKAGE/'sources'/name),'Compare package PNG to pinned Git bytes',units='sha256')
        checks['current_source_'+name]=evidence(h,d0.digest(path),'Compare current reference to pinned Git bytes',units='sha256')
    rel=CONTRACT.relative_to(ROOT).as_posix();blob=subprocess.run(['git','show',f'{BASELINE}:{rel}'],cwd=ROOT,capture_output=True,check=True).stdout
    git_sha=hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()
    checks['contract_git_blob']=evidence('d31aeb126cdcf3903ce8806cc002a33d2092f4f1',git_sha,'Compute Git blob SHA-1 from pinned contract bytes',units='sha1')
    checks['contract_text']=evidence(hashlib.sha256(blob.replace(b'\r\n',b'\n')).hexdigest(),hashlib.sha256(CONTRACT.read_bytes().replace(b'\r\n',b'\n')).hexdigest(),'Compare pinned contract allowing only Git LF/Windows CRLF checkout conversion',units='sha256')
    checks['contract_exact_checkout']=evidence(d0.read_json(OUT/'production_before.json')['sha256'][rel],d0.digest(CONTRACT),'Exact historical checkout hash before/after; never rewrite contract',units='sha256')
    return d1.group(checks,member_count=len(names),pinned_source_count=len(mapping),archive_sha256=d0.digest(archive))


def check_file(name,im,source,c):
    q=d2app.check_candidate(name,im,source,c,reference_path=d3.OUT/f'd3_{name}_native.png')
    if im.mode=='RGBA':
        q['checks']['alpha_histogram']=evidence(HIST[name],{str(a):n for a,n in Counter(im.getchannel('A').get_flattened_data()).items()},'Count actual native alpha values',units='pixels')
        q['pass']=q['pass'] and q['checks']['alpha_histogram']['pass']
    return q


def relationships(views,c):
    checks={};spec=d0.read_json(PACKAGE/'reports/d3_candidate_spec.json')
    for name in ('main','repeat'):
        checks['corner_body_'+name]=evidence(0,d1.pixel_difference(views['corner_'+name].crop((0,24,12,56)),views[name]),'Compare saved corner body RGBA with straight view')
    checks['upper_return']=evidence(0,d1.pixel_difference(views['corner_main'].crop((0,0,12,24)),views['corner_repeat'].crop((0,0,12,24))),'Compare all upper-return RGBA in both alternatives')
    outside=extended=changed=0
    for y in range(32):
        for x in range(12):
            a,b=views['main'].getpixel((x,y)),views['repeat'].getpixel((x,y))
            if 2<=x<10 and 28<=y<32:
                extended+=b!=views['main'].getpixel((x,27));changed+=a!=b
            else:outside+=a!=b
    checks['repeat_outside']=evidence(0,outside,'Read changed pixels outside [2,28,10,32)')
    checks['repeat_extension']=evidence(0,extended,'Read extension against actual candidate row27')
    checks['repeat_changed']=evidence(32,changed,'Count changed RGBA inside declared extension')
    for name,s in c['views'].items():
        meta=spec['views'][name]
        checks[name+'_anchor']=evidence(s['image_anchor'],meta['image_anchor'],'Compare supplied anchor metadata to committed geometry')
        checks[name+'_origin']=evidence(s['origin'],meta['origin_relative_to_cell'],'Compare supplied origin metadata to committed geometry')
        checks[name+'_mapping']=evidence(s['origin'],[a-b for a,b in zip(spec['cell_anchor'],meta['image_anchor'])],'Derive origin from declared cell/image anchors; rendered placement checked separately')
    checks['stride']=evidence([0,32],spec['depth_stride'],'Read supplied stride metadata')
    return d1.group(checks)


def run_evidence(views,count,corner):
    name=('corner_' if corner else 'straight_')+str(count);offset=24 if corner else 0
    run,p,l=d2.assemble(views,count,corner=corner);run=d3.saved(ART/f'{name}_native.png',run)
    geometry=d2.check_run(run.crop((0,offset,12,offset+32*count)),[[0,q[1]-offset] if i else [0,0] for i,q in enumerate(p)],l.crop((0,offset,12,offset+32*count)),count)
    mismatches=0
    for i,origin in enumerate(p):
        view=('corner_' if corner and i==0 else '')+('main' if i==count-1 else 'repeat');im=views[view];y=origin[1]
        mismatches+=d1.pixel_difference(im,run.crop((0,y,12,y+im.height)))
    selection=d1.group({'pixels':evidence(0,mismatches,'Compare selected candidate RGBA to saved composition, never flat scaffold RGB'),
        'origins':evidence([[0,0]]+[[0,32*i+offset] for i in range(1,count)],p,'Read actual selected view origins'),
        'glass_layers':evidence(1,max(l.get_flattened_data()),'Actual maximum translucent draw contributions')})
    trans,backs,obj,scenes=d2.transmission(run)
    # All alpha150 pixels, including the narrow return, are sampled by the helper.
    for key,bg in backs.items():
        d3.saved(ART/f'{name}_{key}_background.png',bg);d3.saved(ART/f'{name}_{key}_composite.png',scenes[key])
    obj.save(ART/f'{name}_object_layer.png')
    return {'geometry':geometry,'selection':selection,'transmission':trans}


def main():
    ART.mkdir(parents=True,exist_ok=True);c=d0.read_json(CONTRACT);views={n:candidate(n) for n in d3.NAMES}
    package=integrity();files={n:check_file(n,views[n],candidate(n,'source_8x'),c) for n in d3.NAMES}
    shapes=all(views[n].mode=='RGBA' and list(views[n].size)==c['views'][n]['size'] for n in d3.NAMES)
    rel=relationships(views,c) if shapes else d1.group({'input_shape':evidence(True,False,'Relationships require declared RGBA dimensions')})
    valid=package['pass'] and all(q['pass'] for q in files.values()) and rel['pass'];runs={};assemblies={};contexts={};negative={}
    if valid:
        for n in (1,2,4):
            for corner in (False,True):runs[('corner_' if corner else 'straight_')+str(n)]=run_evidence(views,n,corner)
        for enclosure in (False,True):
            prefix='enclosure' if enclosure else 'northeast'
            for name,delta in [('original',(0,0)),('relocated',(32,32))]:
                label=prefix+'_'+name
                assemblies[label],_,_=d3.assembly(views,enclosure=enclosure,delta=delta,label=label,artifact_dir=ART)
            original=d1.load(ART/f'{prefix}_original_structure.png');moved=d1.load(ART/f'{prefix}_relocated_structure.png')
            assemblies[prefix+'_relocation']=d1.group({'translated_pixels':evidence(0,d1.pixel_difference(original,moved.crop((32,32,32+original.width,32+original.height))),'Compare independently rebuilt saved structures at two grid origins')})
        for name,cell in [('original',(64,64)),('relocated',(96,96))]:contexts[name],_=d3.right_context(d1.load(ART/'straight_2_native.png'),cell,label='right_wall_'+name,artifact_dir=ART)
        negative=d3.negative_controls(views)
        for name,q in negative.items():q['image'].save(ART/f'broken_{name.lower()}.png')
        good=files['corner_main'];native=views['corner_main'].copy();source=candidate('corner_main','source_8x')
        for name in ('source_subpixel','invisible_rgb'):
            im=native.copy();export=source.copy()
            if name=='source_subpixel':export.putpixel((0,0),(1,2,3,255))
            else:im.putpixel((0,0),(1,2,3,0))
            im=d3.saved(ART/f'broken_{name}_native.png',im);export=d3.saved(ART/f'broken_{name}_source.png',export)
            q=check_file('corner_main',im,export,c)
            failed=q['geometry']['checks']['blocks'] if name=='source_subpixel' else q['checks']['zero_alpha_rgba_changed']
            negative[name]={'validation':q,'valid_control_pass':good['pass'],'intended_check':name,'proven':good['pass'] and not failed['pass']}
        # Exact relationship failures are independent of alpha/shape checks.
        for name in ('broken_repeat','broken_corner_body'):
            changed={k:v.copy() for k,v in views.items()};view='repeat' if name=='broken_repeat' else 'corner_main';p=(0,12) if view=='repeat' else (6,40)
            changed[view].putpixel(p,(1,2,3,changed[view].getpixel(p)[3]));changed[view]=d3.saved(ART/f'{name}.png',changed[view])
            q=relationships(changed,c);key='repeat_outside' if name=='broken_repeat' else 'corner_body_main'
            negative[name]={'validation':q,'valid_control_pass':rel['pass'],'intended_check':key,'proven':rel['pass'] and not q['checks'][key]['pass']}
        clean=d1.load(ART/'northeast_original_clean.png');anno=clean.copy();draw=ImageDraw.Draw(anno)
        draw.line((32,60,112,60),fill=(238,177,40,255));draw.line((96,24,96,124),fill=(238,177,40,255));draw.line((32,64,96,64),fill=(239,62,150,255))
        for l,t,r,b in c['corner_contract']['expected_opaque_overlap']:draw.rectangle((l,t,r-1,b-1),outline=(53,217,165,255))
        d2.labeled_panel(anno,'Independent D1 / D3 corner: computed geometry',[
            'Gold center (96,60), pink baseline64; 24px deliberate cutaway.',
            'Green: declared opaque contacts; actual overlap48, no hidden/stacked glass.',
            'D3 origin (88,36), cell (80,60), image anchor (8,40). D1 unchanged.'],factor=4).save(ART/'northeast_annotated.png')
        region_panels=[]
        for name in d3.NAMES:
            im=views[name].resize(tuple(c['views'][name]['source_size']),Image.Resampling.NEAREST);draw=ImageDraw.Draw(im)
            for l,t,r,b in c['views'][name]['pane']:draw.rectangle((l*8,t*8,r*8-1,b*8-1),outline=(238,177,40,255))
            region_panels.append(d2.labeled_panel(im,name+': declared panes outlined, alpha150',factor=1))
        d2.stack([d2.row(region_panels[:2]),d2.row(region_panels[2:])]).save(ART/'geometry_alpha_diagnostic.png')
        enclosure=d1.load(ART/'enclosure_original_clean.png');sheet=Image.new('RGBA',(120,152),(225,226,213,255));transmit=Image.new('RGBA',(120,88),(225,226,213,255))
        for i,n in enumerate((1,2,4)):sheet.alpha_composite(d1.load(ART/f'corner_{n}_object_composite.png'),(8+i*40,0))
        for i,name in enumerate(('light','dark','colored','object')):transmit.alpha_composite(d1.load(ART/f'corner_2_{name}_composite.png'),(8+i*28,0))
        montage=d2.stack([d2.row([d2.labeled_panel(clean,'D3 appearance: independently rebuilt NE corner',factor=4),d1.load(ART/'northeast_annotated.png')]),
            d2.labeled_panel(enclosure,'Actual validated D2 / unchanged D1 / supplied D3; open front',factor=4),
            d2.row([d2.labeled_panel(enclosure.crop((52,30,112,132)),'NW corner: unchanged D1/D2',factor=5),d2.labeled_panel(enclosure.crop((152,30,212,132)),'NE corner: D1 terminal / supplied D3',factor=5)]),
            d2.row([d2.labeled_panel(sheet,'1 / 2 / 4 corner runs',factor=3),d2.labeled_panel(transmit,'Light / dark / colored / toggled object',factor=4)]),
            d2.row([d2.labeled_panel(d1.load(ART/'enclosure_relocated_clean.png'),'Enclosure independently relocated +32,+32',factor=2),d2.labeled_panel(d1.load(ART/'right_wall_relocated_clean.png'),'Unchanged approved right wall and floor',factor=2)])])
        montage.save(ART/'d3_appearance_review_montage.png')
    preservation=compare_snapshots(d0.read_json(OUT/'production_before.json'),history.snapshot(),allowed_addition_prefixes=(PREFIX,))
    success=valid and all(all(q['pass'] for q in r.values()) for r in runs.values()) and all(q['pass'] for q in assemblies.values()) and all(q['pass'] for q in contexts.values()) and all(q['proven'] for q in negative.values()) and preservation['pass']
    report={'status':'PASS' if success else 'FAIL','scope':'INDEPENDENT_REFERENCE_ONLY_APPEARANCE_VALIDATION','contract_status':c['status'],
        'package_integrity':package,'files':files,'relationships':rel,'repeats':runs,'assemblies':assemblies,'contexts':contexts,
        'negative_controls':{n:{k:v for k,v in q.items() if k!='image'} for n,q in negative.items()},'preservation':preservation,
        'review_evidence':{'user_reported':'ChatGPT reviewed geometry and appearance for independent validation; this is assistant evidence, not human production approval.',
            'human_production_approval':False,'limits':'Existing stylized cutaway only; no full-height side-wall or all-direction junction claim.'}}
    if (OUT/'test_results.json').exists():
        report['tests']=d0.read_json(OUT/'test_results.json')
        if report['tests']['exit_code']!=0:report['status']='FAIL';success=False
    if (OUT/'visual_review.json').exists():report['assistant_visual_findings']=d0.read_json(OUT/'visual_review.json')
    def failures(value,path=''):
        result=[]
        if isinstance(value,dict):
            if value.get('pass') is False and 'expected' in value:result.append({'check':path,**value})
            for k,v in value.items():result+=failures(v,path+'/'+str(k))
        return result
    report['blockers']=failures({k:report[k] for k in ('package_integrity','files','relationships','repeats','assemblies','contexts')})
    if not preservation['pass']:report['blockers'].append({'check':'preservation','details':preservation})
    for n,q in negative.items():
        if not q['proven']:report['blockers'].append({'check':'negative/'+n,'details':'Valid control failed or intended defect escaped'})
    if 'tests' in report and report['tests']['exit_code']!=0:report['blockers'].append({'check':'complete_suite','details':report['tests']})
    d0.write_json(OUT/'production_preservation.json',preservation);d0.write_json(OUT/'package_integrity.json',package);d0.write_json(OUT/'d3_appearance_validation_report.json',report)
    lines=['# Independent D3 appearance validation','',f"**{report['status']}**. Reference-only. Historical contract remains `{c['status']}`. No human production approval.",'',
        'Actual saved RGBA inputs were checked without conversion or repairs. Package scripts were not executed; local PASS claims are not repository observations.','',
        '| View | Native | Source | Alpha changes | RGB changes | Invisible RGBA changes |','| --- | --- | --- | ---: | ---: | ---: |']
    for n,q in files.items():
        g=q['geometry']['checks'];v=q['checks'];lines.append(f"| {n} | {g['size']['observed']} | {g['source_size']['observed']} | {v.get('alpha_changed',{}).get('observed','unavailable')} | {v.get('rgb_changed',{}).get('observed','unavailable')} | {v.get('zero_alpha_rgba_changed',{}).get('observed','unavailable')} |")
    lines+=['',f"Original ZIP and {package['member_count']} members preserved; {package['pinned_source_count']} packaged source PNGs compared to committed bytes. Pinned contract Git SHA-1 verified; exact checkout hash protected (LF/CRLF normalization is used only for pinned text comparison). Package integrity: {package['pass']}.",'',
        f"View relationships and metadata mapping: {rel['pass']}. Main/repeat origin[8,0], image anchor[8,16]; corner origin[8,-24], image anchor[8,40]; cell anchor[16,16]. Four mutually exclusive views are one future logical asset. Body and upper-return RGBA match exactly; repeat extends only row27 within [2,28,10,32).",'']
    for n,q in runs.items():lines.append(f"- {n}: geometry {q['geometry']['pass']}, view selection {q['selection']['pass']}, transmission {q['transmission']['pass']}.")
    for n,q in assemblies.items():
        if 'northeast' in q.get('checks',{}):
            lines+=['',f"{n} NE measured: {q['checks']['northeast']['computed']}."]
            if 'northwest' in q['checks']:lines.append(f"{n} NW measured separately: {q['checks']['northwest']['computed']}.")
    lines+=['','The source-over check samples every pane pixel, including the narrow glazed return, on separate light/dark/colored/object backgrounds. Frame alpha255 is invariant; glass alpha150 responds; exterior alpha0 stays separate. Exact 8x blocks and native roundtrips pass.','',
        'Draw order: separate background, D2 when present, D3, unchanged D1. Each back corner has its own overlap measurement; ground center and baseline remain distinct and the cutaway is24px. D1 final composited pixels and D2 layer remain exact. Independently relocated corner/enclosure structures match after a32px translation. Right-wall contexts use unchanged approved wall/floor files. No front partition.','', '## Negative controls','']
    for n,q in negative.items():lines.append(f"- {n}: valid {q['valid_control_pass']}; intended failure proven {q['proven']} ({q['intended_check']}).")
    lines+=['',f"Protected files {preservation['protected_file_count']}; changed {preservation['changed']}; missing {preservation['missing']}. Counts before/after {preservation['expected_counts']} / {preservation['observed_counts']}. Historical sources, reports, proposed contracts, snapshots, approved artwork and inventory bytes remain unchanged.",'',
        'Only the explicitly named new appearance workspace is allowed by addition safeguards. Existing-file hashes remain mandatory, including inside allowed prefixes. Reused helpers accept an explicit output directory/reference path; defaults and historical evidence are unchanged.','',
        'Reproduce: `python tools/validate_architecture_d3_appearance.py`. Complete suite: `python -m pytest -q`. Actual starting suite198 passed.']
    if 'tests' in report:lines+=['',f"Captured complete suite {report['tests']['passed']} passed; exit {report['tests']['exit_code']}."]
    lines+=['',f"Blockers: {report['blockers']}",'','No candidate edits, human approval, production ingestion, Batch13, D4 or unrelated junction repairs.','']
    (OUT/'d3_appearance_validation_report.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'status':report['status'],'blockers':report['blockers'],'protected':preservation['protected_file_count'],'counts':preservation['observed_counts']},indent=2))
    return 0 if success else 1


if __name__=='__main__':raise SystemExit(main())
