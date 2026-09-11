"""Stage four validated glass assets, reconstruct their usage, stop for human review."""
from __future__ import annotations
import json
import hashlib
import sys
import zipfile
from pathlib import Path
from PIL import Image
import validate_architecture_d0 as d0
import validate_architecture_d1 as d1
import validate_architecture_d2_v2 as side
import validate_architecture_d3 as d3
import validate_architecture_d4 as d4
import validate_architecture_d4_appearance as d4app
from rastalr_pipeline import core, views, batch13 as b, production_transition as transition
from rastalr_pipeline.geometry import evidence

ROOT=core.ROOT


def write_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    text=json.dumps(value,indent=2,ensure_ascii=False)+'\n'
    if not path.exists() or path.read_text()!=text:path.write_text(text,encoding='utf-8',newline='\n')


def saved(path,im):
    return d4.saved(path,im)


def run_check(asset,image,placements,coverage,origin,count,corner):
    pp=[[p['origin'][j]-origin[j] for j in range(2)] for p in placements]
    member=asset['family_member']
    if member=='D1':
        main=views.resolve(ROOT,asset)[2]
        q=d1.validate_run(image,main,d1.load(d0.CANON/'glass_partition_1x.png'),d0.read_json(d1.CONTRACT_PATH),count,pp,coverage)
    elif member=='D4':q=d4.check_run(image,pp,coverage,count)
    else:
        shift=24 if corner else 0
        body=image.crop((0,shift,12,image.height));cc=coverage.crop((0,shift,12,coverage.height))
        # First corner carrier starts24px above its logical body; subsequent views do not.
        body_pp=[[p[0],p[1]-shift if i else 0] for i,p in enumerate(pp)]
        q=side.check_run(body,body_pp,cc,count)
    checks={'geometry':q,'layer_max':evidence(1,max(coverage.get_flattened_data()),'Actual per-pixel translucent contribution count')}
    errors=0
    for i,p in enumerate(placements):
        v=asset['views'][p['name']];s=views.contract_view(ROOT,asset,p['name'])
        errors+=p['origin']!=[p['cell'][j]+s['origin'][j] for j in range(2)]
        errors+=p['name']!=views.select_name(asset,index=i,count=count,back_corner=corner)
    checks['placement_and_selection']=evidence(0,errors,'Actual selections/origins versus committed numeric geometry')
    return d1.group(checks,computed={'placements':placements,'carrier_origin':origin,'size':list(image.size)})


def enclosure(assets,name,width,depth,delta=(0,0),*,save=True):
    x0=64+delta[0];top=36+delta[1];north=top+24;east=x0+32*width;south=north+32*depth
    cells={'D1':(x0,top+8),'D2':(x0-16,north),'D3':(east-16,north),'D4':(x0,south-16)}
    runs={a['family_member'].lower():views.run(ROOT,a,depth if a['view_selection_kind']=='side' else width,
        back_corner=a['view_selection_kind']=='side',cell=cells[a['family_member']]) for a in assets}
    q,clean,structure=d4.enclosure({},width,depth,delta,label=name if save else None,artifact_dir=ROOT/b.ART,resolved_runs=runs)
    q['computed']['placements']={n:r[1] for n,r in runs.items()}
    # All layers come from manifest resolution; committed validation images are read-only controls.
    comparison={}
    if save:
        for suffix in ('structure','clean','object_composite','background','object_layer','d1_layer','d2_layer','d3_layer','d4_layer'):
            actual=d1.load(ROOT/b.ART/f'{name}_{suffix}.png');control=d1.load(d4app.ART/f'enclosure_{name}_{suffix}.png')
            comparison[suffix]=evidence(0,d1.pixel_difference(actual,control),'Reload staged reconstruction and committed validation control; compare RGBA pixels')
        for corner,edge,cy in [('northwest',x0,north),('northeast',east,north),('southwest',x0,south),('southeast',east,south)]:
            saved(ROOT/b.ART/f'{name}_{corner}.png',clean.crop((edge-20,cy-32,edge+24,cy+24)))
    q['checks']['validated_reconstruction']=d1.group(comparison)
    q['pass']=all(v['pass'] for v in q['checks'].values())
    return q,clean,structure


def usage(assets):
    lines=['# Batch13 glass partitions — NEEDS_HUMAN_REVIEW','',
        'Four logical assets; twelve mutually exclusive native views. No production approval has been granted.',
        'Native PNGs are byte-identical copies of validated artwork. Working-source scale8 is provenance; never divide these native files by8 again.', '',
        'Use `rastalr_pipeline.views.resolve(root, asset, index=..., count=..., back_corner=...)` or `views.run`. Missing or corrupt selected files fail; there is no reference-source fallback.',
        'Horizontal runs select repeat until the last main. Side runs select repeat until the last main; at a reviewed north corner only the first cell uses corner_repeat, or corner_main for a one-cell run. Keep the final side support at D4.',
        'These alternatives replace each other once per placement. They are distinct from Batch12 additive components, which remain additive.', '',
        'All logical footprints are1x1 on a32px grid. Rectangles are half-open [left,top,right,bottom). Image origin = cell origin + cell anchor − image anchor. Add [32,0] per horizontal cell, [0,32] per side cell. The24px side return overhang does not change the logical footprint.', '',
        '| Parent / view | Native size | Cell anchor | Image anchor | Relative origin | Native path |',
        '|---|---|---|---|---|---|']
    for a in assets:
        for name,v in a['views'].items():lines.append(f"| {a['id']} / {name} | {v['dimensions']} | {v['cell_anchor']} | {v['image_anchor']} | {v['render_origin']} | `{v['normalized_path']}` |")
    lines += ['', 'Draw separate floor, separate object, D2, D3, D1, D4, in that order. D1 baseline is4px below its ground centerline; D4 trim begins4px above the south centerline and its exclusive image base is8px below it. Do not equate these edges.',
        'The north return and shallow side body are an intentional cutaway. North corners have48 opaque contact pixels apiece; front corners have32 each. D4 owns the visible front trim contact while the side terminal retains its4px exterior shoulder. No assembly masks or stacked translucent panes are used.',
        'Lighting stays upper-left. Use the independently authored orientation; never rotate or mirror finished art. All frame pixels are opaque255; panes retain alpha150 (D1 also210), and declared corner exterior is0. Floors and objects remain separate.',
        'Supported evidence: straight runs, local2x1, rectangular4x2 and3x3 enclosures and translation. A closed enclosure has no entrance. No arbitrary L/T/cross junction, collision/navigation, animation or other orientation is claimed.',
        'Review the staged PNGs and both contact/QA montages. ChatGPT review and automated QA do not replace human production approval. Future explicit approval promotes every required view of a parent together after preflight; it is not executed by this staging command.',
        'The review ZIP preserves normalized paths relative to its root. Reference provenance fields describe external repository history; only the twelve normalized view paths are runtime artwork in this compact package.']
    return '\n'.join(lines)+'\n'


def review_images(assets):
    cards=[]
    for a in assets:
        panels=[]
        for name,v in a['views'].items():
            im=views.load(views.path(ROOT,v['normalized_path']))
            panels.append(side.labeled_panel(im,name,[str(v['dimensions'])+'  origin '+str(v['render_origin'])],factor=5))
        # Two columns keep the12 native views readable without a very wide sheet.
        cards.append(side.labeled_panel(side.stack([side.row(panels[i:i+2]) for i in range(0,len(panels),2)]),a['id'],['NEEDS_HUMAN_REVIEW; exclusive alternatives'],factor=1))
    saved(ROOT/b.CONTACT,side.stack(cards))
    corners=[]
    for name in ('northwest','northeast','southwest','southeast'):
        corners.append(side.labeled_panel(d1.load(ROOT/b.ART/f'original_{name}.png'),name,['48 opaque contact pixels' if name.startswith('north') else '32 opaque contact pixels'],factor=8))
    small=[]
    for a in assets:
        im=views.resolve(ROOT,a)[2];small.append(side.labeled_panel(im,a['family_member']+' main',factor=4))
    panels=[side.row(small[:2]),side.row(small[2:]),side.row(corners[:2]),side.row(corners[2:]),
        side.labeled_panel(d1.load(ROOT/b.ART/'original_object_composite.png'),'Staged D1-D4 enclosure / separate object',factor=4)]
    panels.insert(2,side.row([side.labeled_panel(views.resolve(ROOT,a,count=2,back_corner=True)[2],
        a['family_member']+' corner_repeat',['Exclusive first-cell view; NEEDS_HUMAN_REVIEW'],factor=4) for a in assets[1:3]]))
    for key in ('light','dark','colored','object'):
        panels.append(side.labeled_panel(d1.load(ROOT/b.ART/f'd4_straight_4_{key}_composite.png'),'D4 separate '+key+' transmission',factor=5))
    panels.append(side.labeled_panel(d1.load(ROOT/b.ART/'approved_wall_context.png'),'Unchanged Batch11 walls and floor',factor=2))
    saved(ROOT/b.MONTAGE,side.stack(panels))


def bundle(assets):
    target=ROOT/b.BUNDLE;target.parent.mkdir(parents=True,exist_ok=True)
    paths={v['normalized_path'] for a in assets for v in a['views'].values()}
    paths.update((b.BATCH,b.QA,b.QA_MD,b.GUIDE,b.CONTACT,b.MONTAGE))
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(paths):
            info=zipfile.ZipInfo(p,date_time=(2026,9,11,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,(ROOT/p).read_bytes())


def build():
    start=transition.snapshot(ROOT);before=d0.read_json(ROOT/b.AUDIT/'production_before.json')
    # Preflight before inventory mutation; allow only the task's named new files.
    if any(start['sha256'].get(p)!=h for p,h in before['sha256'].items() if p not in transition.METADATA_CHANGES):raise ValueError('Protected file changed before staging')
    current=core.load_manifest();expected=b.blueprints(ROOT)
    if start['counts']==before['counts']:
        if current!=d0.read_json(ROOT/b.AUDIT/'before_manifest.json') or views.digest(ROOT/'metadata/catalog.csv')!=before['sha256']['metadata/catalog.csv']:raise ValueError('Starting inventory conflict')
    elif not transition.semantics(d0.read_json(ROOT/b.AUDIT/'before_manifest.json'),current,transition.rows((ROOT/b.AUDIT/'before_catalog.csv').read_text()),transition.rows((ROOT/'metadata/catalog.csv').read_text()),expected)['pass']:raise ValueError('Conflicting staged inventory')
    write_json(ROOT/b.BATCH,b.declaration(ROOT));core.ingest_batch(ROOT/b.BATCH)
    production_qa=core.run_qa(asset_ids=b.IDS,write_reports=False)
    for item in production_qa['assets']:
        item['path']=Path(item['path']).relative_to(ROOT).as_posix()
    core.write_catalog()
    assets=[next(a for a in core.load_manifest()['assets'] if a['id']==i) for i in b.IDS]
    qa={a['id']:views.qa_asset(ROOT,a) for a in assets}
    if any(q['status']!='pass' for q in qa.values()):raise ValueError('Staged production glass QA failed')
    runs={}
    for a in assets:
        for corner in ((False,True) if a['view_selection_kind']=='side' else (False,)):
            for n in (1,2,4):
                stem=f"{a['family_member'].lower()}_{'corner' if corner else 'straight'}_{n}"
                im,pp,cc,origin=views.run(ROOT,a,n,back_corner=corner)
                im=saved(ROOT/b.ART/f'{stem}_native.png',im)
                q=run_check(a,im,pp,cc,origin,n,corner);trans,backs,obj,scenes=side.transmission(im)
                for key,bg in backs.items():saved(ROOT/b.ART/f'{stem}_{key}_background.png',bg);saved(ROOT/b.ART/f'{stem}_{key}_composite.png',scenes[key])
                saved(ROOT/b.ART/f'{stem}_object_layer.png',obj)
                runs[stem]=d1.group({'run':q,'transmission':trans})
    enclosures={};structures={}
    for name,w,d,delta in [('local',2,1,(0,0)),('original',4,2,(0,0)),('relocated',4,2,(32,32)),('additional_size',3,3,(0,0))]:
        enclosures[name],_,structures[name]=enclosure(assets,name,w,d,delta)
    base=structures['original'];moved=structures['relocated'].crop((32,32,32+base.width,32+base.height))
    relocation=evidence(0,d1.pixel_difference(base,moved),'Reload independent +32,+32 reconstruction, translate and compare all RGBA pixels')
    right=views.run(ROOT,assets[2],2)[0];context,scene=d3.right_context(right);saved(ROOT/b.ART/'approved_wall_context.png',scene)
    mapping=[{'id':a['id'],'view':n,'source':v['source_native'],'staged':v['normalized_path'],'source_sha256':views.digest(ROOT/v['source_native']),'staged_sha256':views.digest(ROOT/v['normalized_path'])} for a in assets for n,v in a['views'].items()]
    write_json(ROOT/b.AUDIT/'source_staged_map.json',mapping)
    (ROOT/b.GUIDE).write_text(usage(assets),encoding='utf-8',newline='\n')
    review_images(assets)
    report={'batch_status':'NEEDS_HUMAN_REVIEW','technical_status':'PASS' if all(q['pass'] for q in [*runs.values(),*enclosures.values(),context,relocation]) else 'FAIL',
        'validation_baseline':b.BASELINE,'rectangle_convention':'[left,top,right,bottom)','production_qa':{k:v for k,v in production_qa.items() if k!='generated_at'},
        'views':qa,'source_staged_map':mapping,'runs':runs,'enclosures':enclosures,'relocation':relocation,'approved_wall_context':context,
        'counts_before':before['counts'],'counts_after':transition.snapshot(ROOT)['counts'],'catalog_rows':len(transition.rows((ROOT/'metadata/catalog.csv').read_text())),
        'human_review':{'status':'NEEDS_HUMAN_REVIEW','approval':False,'limits':'Only documented straight runs, local corners and rectangular enclosures. No entrance or arbitrary junction claim.'},
        'test_evidence':b.AUDIT+'/test_results.json','preservation_evidence':b.AUDIT+'/preservation.json','idempotence_evidence':b.AUDIT+'/idempotence.json'}
    write_json(ROOT/b.QA,report)
    text=f"# Batch13 glass QA — NEEDS_HUMAN_REVIEW\n\nTechnical result: **{report['technical_status']}**. Four logical assets; twelve exclusive native views; no approval.\n\nAll12 staged native hashes equal validated originals. RGBA, source8x blocks/roundtrips, numeric anchors, full alpha maps and continuation relationships were independently checked by the production glass profile.\n\n18 one/two/four-cell straight/corner runs and four complete enclosures were reconstructed from staged paths through manifest metadata. Each back corner measures48 opaque contact pixels; each front corner32. No unexpected overlap, hidden/stacked glass, missing contacts or clipping. Every enclosure layer and scene equals its committed validation control; relocation is pixel-identical after translation. Separate backgrounds and toggled objects transmit through panes; opaque frames remain invariant.\n\nInventory:220/220/0 →224/220/4; catalog224 logical rows. Only manifest/catalog bytes intentionally change among old protected files, following semantic proof of all220 old records/values unchanged. Strict unchanged-state comparison remains false; the explicit bounded transition is audited separately. See `{b.AUDIT}/preservation.json`.\n\nCaptured full suite: `{b.AUDIT}/test_results.json` and `.txt`. Repeated staging evidence: `{b.AUDIT}/idempotence.json`. Historical LIVE snapshot tests opt into the bounded audit; their immutable snapshots and temporary strict tests remain unchanged.\n\nUsage: `{b.GUIDE}`. Review contact sheet: `{b.CONTACT}`. QA montage: `{b.MONTAGE}`.\n\nSTOP: NEEDS_HUMAN_REVIEW. Technical QA does not grant geometry, appearance or production approval.\n"
    (ROOT/b.QA_MD).write_text(text,encoding='utf-8',newline='\n')
    if report['technical_status']!='PASS':raise ValueError('Staged reconstruction failed; inspect JSON')
    bundle(assets)
    hashes={p:views.digest(ROOT/p) for p in sorted(b.allowed_additions(ROOT)) if (ROOT/p).is_file() and p not in {b.AUDIT+'/'+n for n in ('output_hashes.json','preservation.json','idempotence.json','test_results.json','test_results.txt')}}
    write_json(ROOT/b.AUDIT/'output_hashes.json',hashes)
    proof=transition.audit(ROOT);write_json(ROOT/b.AUDIT/'preservation.json',proof)
    if not proof['pass']:raise ValueError('Bounded preservation failed: '+str(proof['errors']))
    return report


def verify_idempotence():
    before=transition.snapshot(ROOT);q=build();after=transition.snapshot(ROOT)
    own=b.AUDIT+'/idempotence.json'
    bh={p:h for p,h in before['sha256'].items() if p!=own};ah={p:h for p,h in after['sha256'].items() if p!=own}
    changed=sorted(p for p in set(bh)|set(ah) if bh.get(p)!=ah.get(p))
    record={'command':'python tools/build_architecture_glass_partitions_batch_13.py --verify-idempotence',
        'pass':not changed and before['counts']==after['counts'],'compared_files':len(bh),'changed_or_added_or_deleted':changed,
        'counts_before':before['counts'],'counts_after':after['counts'],
        'before_hash_map_sha256':hashlib.sha256(json.dumps(bh,sort_keys=True).encode()).hexdigest(),
        'after_hash_map_sha256':hashlib.sha256(json.dumps(ah,sort_keys=True).encode()).hexdigest(),
        'exception':'Only this idempotence evidence file is excluded from comparing itself. No timestamp fields are refreshed.'}
    write_json(ROOT/own,record)
    if not record['pass']:raise ValueError('Repeated staging changed outputs: '+str(changed))
    return q


if __name__=='__main__':
    if sys.argv[1:] not in ([],['--verify-idempotence']):raise SystemExit('Only --verify-idempotence is supported')
    q=verify_idempotence() if sys.argv[1:] else build()
    print(json.dumps({'status':q['batch_status'],'technical_status':q['technical_status'],'counts':q['counts_after']},indent=2))
