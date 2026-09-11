"""Explicit Batch13 live-tree audit. The unchanged snapshot comparator stays strict."""
import csv
import io
import json
import zipfile
from pathlib import Path
from PIL import Image
from .snapshot import compare_snapshots
from . import batch13, views

METADATA_CHANGES={'metadata/manifest.json','metadata/catalog.csv'}
# User-requested operational handoff, introduced after Batch13. This permits
# only the named addition; protected_difference still locks every baseline hash.
AUTHORIZED_OPERATIONAL_ADDITIONS={'docs/CODEX_PROJECT_STATE.md'}


def rows(text):
    return list(csv.DictReader(io.StringIO(text)))


def semantics(before_manifest,current_manifest,before_rows,current_rows,expected_assets):
    errors=[];old=before_manifest['assets'];now=current_manifest['assets'];old_map={a['id']:a for a in old};new_map={a['id']:a for a in now}
    expected={a['id']:a for a in expected_assets}
    if len(old_map)!=220 or len(old)!=220 or len(now)!=224 or len(new_map)!=224:errors.append('Logical inventory cardinality')
    if set(new_map)-set(old_map)!=set(expected) or set(old_map)-set(new_map):errors.append('Exact four new IDs required')
    if any(new_map.get(k)!=a for k,a in old_map.items()):errors.append('Existing220 manifest records changed')
    if any(new_map.get(k)!=a for k,a in expected.items()):errors.append('New pending record differs from reviewed native-copy declaration')
    if {k:v for k,v in before_manifest.items() if k!='assets'}!={k:v for k,v in current_manifest.items() if k!='assets'}:errors.append('Manifest header changed')
    counts={'manifest':len(now),'approved':sum(a.get('approval_status')=='approved' for a in now),'needs_human_review':sum(a.get('approval_status')=='needs_human_review' for a in now)}
    if counts!={'manifest':224,'approved':220,'needs_human_review':4}:errors.append('Unauthorized approval/count transition')
    prior={r['id']:r for r in before_rows};current={r['id']:r for r in current_rows}
    if len(before_rows)!=220 or len(current_rows)!=224 or len(current)!=224:errors.append('Catalog logical row count')
    if set(current)!=set(new_map):errors.append('Catalog/manifest IDs differ')
    if any(current.get(k)!=v for k,v in prior.items()):errors.append('Old catalog values/columns changed')
    if before_rows:
        fields=list(before_rows[0])
        for key,a in expected.items():
            row={f:str(a.get(f,'')) for f in fields};row['tags']=';'.join(a['tags']);row['component_count']='0';row['component_roles']=''
            if current.get(key)!=row:errors.append('New catalog row is not derived from parent: '+key)
    return {'pass':not errors,'errors':errors,'expected_counts':before_manifest and {'manifest':220,'approved':220,'needs_human_review':0},'observed_counts':counts,
            'metadata_changes':sorted(METADATA_CHANGES),'catalog_policy':'Same columns; exact old values; one row per parent, alternatives excluded'}


def snapshot(root):
    paths=[p for folder in ('assets','staging','source','references','metadata','previews','release','docs') for p in (root/folder).rglob('*') if p.is_file()]
    m=json.loads((root/'metadata/manifest.json').read_text());assets=m['assets']
    return {'counts':{'manifest':len(assets),'approved':sum(a['approval_status']=='approved' for a in assets),'needs_human_review':sum(a['approval_status']=='needs_human_review' for a in assets)},
            'sha256':{p.relative_to(root).as_posix():views.digest(p) for p in paths}}


def protected_difference(before,current,allowed_additions,*,semantic_pass):
    """Named additions never exempt an existing file; metadata needs semantic proof."""
    exempt=METADATA_CHANGES if semantic_pass else set()
    changed=sorted(p for p,h in before.items() if p not in exempt and current.get(p)!=h)
    unexpected=sorted(set(current)-set(before)-set(allowed_additions))
    return {'pass':not changed and not unexpected,'changed_or_missing':changed,'unauthorized_additions':unexpected}


def output_derivation(root):
    """Check named aggregates against staged metadata and immutable scene controls."""
    import validate_architecture_d4_appearance as d4app
    errors=[];assets=batch13.blueprints(root)
    try:
        report=json.loads((root/batch13.QA).read_text())
        if report['batch_status']!='NEEDS_HUMAN_REVIEW' or report['technical_status']!='PASS' or set(report['views'])!=set(batch13.IDS):errors.append('Batch QA scope/status mismatch')
        ledger=json.loads((root/batch13.AUDIT/'output_hashes.json').read_text())
        excluded={batch13.AUDIT+'/'+n for n in ('output_hashes.json','preservation.json','idempotence.json','test_results.json','test_results.txt')}
        required=batch13.allowed_additions(root)-excluded
        if set(ledger)!=required:errors.append('Output ledger differs from exact named outputs')
        for p,h in ledger.items():
            if not (root/p).is_file() or views.digest(root/p)!=h:errors.append('Derived output missing/changed: '+p)
        mapping=[{'id':a['id'],'view':n,'source':v['source_native'],'staged':v['normalized_path'],'source_sha256':views.digest(root/v['source_native']),'staged_sha256':views.digest(root/v['normalized_path'])} for a in assets for n,v in a['views'].items()]
        if json.loads((root/batch13.AUDIT/'source_staged_map.json').read_text())!=mapping or report['source_staged_map']!=mapping:errors.append('Source/staged map derivation')
        for a in assets:
            for corner in ((False,True) if a['view_selection_kind']=='side' else (False,)):
                for n in (1,2,4):
                    stem=f"{a['family_member'].lower()}_{'corner' if corner else 'straight'}_{n}"
                    expected,placements,_,_=views.run(root,a,n,back_corner=corner)
                    actual=views.load(root/batch13.ART/f'{stem}_native.png')
                    if actual.size!=expected.size or actual.tobytes()!=expected.tobytes():errors.append('Run derivation: '+stem)
                    if report['runs'][stem]['checks']['run']['computed']['placements']!=placements:errors.append('Run placement evidence: '+stem)
                    for key in ('light','dark','colored','object'):
                        bg=views.load(root/batch13.ART/f'{stem}_{key}_background.png');scene=views.load(root/batch13.ART/f'{stem}_{key}_composite.png')
                        if scene.tobytes()!=Image.alpha_composite(bg,actual).tobytes():errors.append('Transmission composition: '+stem+'/'+key)
        for name in ('local','original','relocated','additional_size'):
            for suffix in ('structure','background','object_layer','clean','object_composite','d1_layer','d2_layer','d3_layer','d4_layer'):
                actual=views.load(root/batch13.ART/f'{name}_{suffix}.png')
                control=views.load(root/d4app.ART.relative_to(d4app.ROOT)/f'enclosure_{name}_{suffix}.png')
                if actual.size!=control.size or actual.tobytes()!=control.tobytes():errors.append('Validated scene control: '+name+'/'+suffix)
        with zipfile.ZipFile(root/batch13.BUNDLE) as z:
            expected={v['normalized_path'] for a in assets for v in a['views'].values()}|{batch13.BATCH,batch13.QA,batch13.QA_MD,batch13.GUIDE,batch13.CONTACT,batch13.MONTAGE}
            if set(z.namelist())!=expected or len(z.namelist())!=len(expected):errors.append('Review bundle exact member set')
            for p in expected:
                if z.read(p)!=(root/p).read_bytes():errors.append('Bundle member derivation: '+p)
    except (OSError,ValueError,KeyError,zipfile.BadZipFile) as e:errors.append('Missing or invalid derived evidence: '+str(e))
    return {'pass':not errors,'errors':errors,'methods':['Exact output hash ledger','Native runs and placements reassembled through metadata','Separate source-over recomposition','Four immutable validation scene controls','Exact package member derivation']}


def audit(root):
    root=Path(root);folder=root/batch13.AUDIT;before=json.loads((folder/'production_before.json').read_text());current=snapshot(root)
    bm=folder/'before_manifest.json';bc=folder/'before_catalog.csv'
    proof=semantics(json.loads(bm.read_text()),json.loads((root/'metadata/manifest.json').read_text()),rows(bc.read_text()),rows((root/'metadata/catalog.csv').read_text()),batch13.blueprints(root))
    errors=list(proof['errors'])
    if views.digest(bm)!=before['sha256']['metadata/manifest.json'] or views.digest(bc)!=before['sha256']['metadata/catalog.csv']:errors.append('Captured pre-task inventory hash mismatch')
    delta=protected_difference(before['sha256'],current['sha256'],batch13.allowed_additions(root)|AUTHORIZED_OPERATIONAL_ADDITIONS,semantic_pass=proof['pass'])
    changed=delta['changed_or_missing'];unexpected=delta['unauthorized_additions']
    if changed:errors.append('Protected historical file changed or deleted')
    if unexpected:errors.append('Unauthorized output addition')
    for a in batch13.blueprints(root):
        for v in a['views'].values():
            if current['sha256'].get(v['normalized_path'])!=v['sha256']:errors.append('Missing/corrupt staged view: '+v['normalized_path'])
    declared=root/batch13.BATCH
    if not declared.is_file() or json.loads(declared.read_text())!=batch13.declaration(root):errors.append('Batch declaration mismatch')
    outputs=output_derivation(root)
    errors.extend(outputs['errors'])
    return {**proof,'pass':not errors,'errors':errors,'mode':'authorized_batch13_production_transition','unchanged_state_pass':False,
        'protected_file_count':len(before['sha256']),'unchanged_protected_file_count':len(before['sha256'])-2-len(changed),'changed_or_missing_protected_files':changed,
        'unauthorized_additions':unexpected,'authorized_operational_additions':sorted(AUTHORIZED_OPERATIONAL_ADDITIONS),
        'authorized_new_ids':batch13.IDS,'native_view_count':12,'output_derivation':outputs}


def compare_live_snapshot(baseline,current,*,allowed_addition_prefixes=(),root=None):
    """Opt-in only at LIVE historical test call sites, never in the default comparator."""
    if root is None:root=Path(__file__).resolve().parents[2]
    proof=audit(root);before=json.loads((root/batch13.AUDIT/'production_before.json').read_text())
    old=baseline['sha256'];new=current['sha256']
    missing=sorted(set(old)-set(new));changed=sorted(p for p,h in old.items() if p not in METADATA_CHANGES and new.get(p)!=h)
    # Historical additions are locked by the immutable task-start snapshot;
    # the exact post-Batch13 operational document is declared separately.
    unexpected=sorted(set(new)-set(old)-set(before['sha256'])-batch13.allowed_additions(root)-AUTHORIZED_OPERATIONAL_ADDITIONS)
    metadata_baseline=all(old.get(p)==before['sha256'].get(p) for p in METADATA_CHANGES if p in old)
    strict=compare_snapshots(baseline,current,allowed_addition_prefixes=allowed_addition_prefixes)
    return {'pass':proof['pass'] and not missing and not changed and not unexpected and metadata_baseline,
        'mode':'authorized_batch13_production_transition','unchanged_state_pass':strict['pass'],'transition':proof,
        'protected_file_count':len(old),'expected_counts':baseline['counts'],'observed_counts':current['counts'],
        'changed':changed,'missing':missing,'unauthorized_additions':unexpected,'authorized_metadata_changes':sorted(METADATA_CHANGES)}
