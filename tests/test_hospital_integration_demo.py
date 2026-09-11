"""Focused integration contracts; does not mutate production assets."""
from collections import Counter, deque
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / 'demo/hospital_integration'

def read():
    return json.loads((DEMO / 'runtime_manifest.json').read_text())

def test_demo_native_sources_and_pending_boundary():
    m = json.loads((ROOT / 'metadata/manifest.json').read_text())
    assert Counter(a['approval_status'] for a in m['assets']) == {'approved':220,'needs_human_review':4}
    source = {a['id']:a for a in m['assets']}
    d = read()
    pending = set()
    for f in d['files'].values():
        a = source[f['logical_id']]
        assert f['approval_status'] == a['approval_status']
        assert f['logical_footprint'] == [a['footprint_width_tiles'],a['footprint_height_tiles']]
        assert (DEMO/f['path']).read_bytes() == (ROOT/f['source_path']).read_bytes()
        assert hashlib.sha256((DEMO/f['path']).read_bytes()).hexdigest() == f['sha256']
        if a['approval_status'] == 'approved':
            assert f['source_path'].startswith('assets/')
        else:
            pending.add(a['id'])
            assert f['source_path'].startswith('staging/pending/normalized/')
    assert pending == {a['id'] for a in m['assets'] if a['approval_status']=='needs_human_review'}

def test_demo_exclusive_glass_and_additive_door():
    d = read()
    glass = [p for p in d['placements'] if p['kind']=='glass']
    assert len({(d['files'][p['asset']]['logical_id'],tuple(p['position'])) for p in glass}) == len(glass)
    assert all(d['files'][p['asset']]['role'] in ('main','repeat','corner_repeat') for p in glass)
    opened = [p for p in d['placements'] if p.get('state')=='open']
    assert {d['files'][p['asset']]['role'] for p in opened} == {'main','left_parked_leaf','right_parked_leaf'}
    assert all(p['collision'] is None for p in opened)
    assert len({p['asset'] for p in d['placements'] if p['kind']=='prop'}) == 20
    from PIL import Image
    def pixels(p):
        im = Image.open(DEMO/d['files'][p['asset']]['path'])
        ox,oy = [int(p['position'][j]+p['offset'][j]) for j in range(2)]
        return {(ox+x,oy+y): im.getpixel((x,y))[3] for y in range(im.height) for x in range(im.width) if im.getpixel((x,y))[3]}
    horizontal = [p for p in glass if 'back_01' in p['asset'] or 'front_cutaway' in p['asset']]
    for side in ('left','right'):
        for role,expected in [('corner_repeat',48),('main',32)]:
            p = next(p for p in glass if 'side_'+side in p['asset'] and d['files'][p['asset']]['role']==role)
            a=pixels(p); overlap=[]
            for h in horizontal:
                b=pixels(h)
                overlap += [(a[k],b[k]) for k in a.keys() & b.keys()]
            assert len(overlap)==expected
            assert all(pair==(255,255) for pair in overlap), 'No stacked or hidden glass at corners'


def test_demo_walk_clearance():
    # Flood-fill the same 18x8 foot rectangle with the door open. This tests
    # practical access around the furnishings, not tall-image bounding boxes.
    solids = [p['collision'] for p in read()['placements'] if p['collision'] and p.get('state')!='closed']
    def clear(x,y):
        return 32<=x<=704 and 96<=y<=408 and not any(x+9>l and x-9<l+w and y>t and y-8<t+h for l,t,w,h in solids)
    start=(352,368); seen={start}; queue=deque([start])
    while queue:
        x,y=queue.popleft()
        for q in [(x-4,y),(x+4,y),(x,y-4),(x,y+4)]:
            if q not in seen and clear(*q):seen.add(q);queue.append(q)
    for destination in [(128,216),(112,312),(176,312),(352,320),(400,248),(432,296),(608,248),(656,232),(656,296),(304,216)]:
        assert destination in seen, f'No walking access to {destination}'


def test_open_door_candidate_changes_only_documented_aperture_alpha():
    from PIL import Image
    folder = DEMO/'repair_candidates/sliding_door_open_alpha_v1'
    r = json.loads((folder/'repair.json').read_text())
    original = Image.open(ROOT/r['source_path'])
    candidate = Image.open(DEMO/r['candidate_path'])
    mask = Image.open(DEMO/r['mask_path'])
    assert original.size == candidate.size == mask.size == (64,52)
    assert original.mode == candidate.mode == 'RGBA' and mask.mode == 'L'
    assert mask.getbbox() == tuple(r['bounds_half_open_native']) == (7,14,59,48)
    assert original.convert('RGB').tobytes() == candidate.convert('RGB').tobytes()
    changed = 0
    for y in range(52):
        for x in range(64):
            selected = 7<=x<59 and 14<=y<48
            assert mask.getpixel((x,y)) == (255 if selected else 0)
            a,b = original.getpixel((x,y)),candidate.getpixel((x,y))
            assert b[3] == (0 if selected else a[3])
            changed += a[3] != b[3]
    assert changed == r['changed_alpha_pixels'] == 1768
    for key in ('source','candidate','mask'):
        root = ROOT if key == 'source' else DEMO
        assert hashlib.sha256((root/r[key+'_path']).read_bytes()).hexdigest() == r[key+'_sha256']
    for leaf in r['parked_leaves']:
        assert (ROOT/leaf['source_path']).read_bytes() == (DEMO/leaf['demo_path']).read_bytes()
        assert hashlib.sha256((DEMO/leaf['demo_path']).read_bytes()).hexdigest() == leaf['sha256']
    assert r['status'] == 'unapproved_repair_candidate'


def test_wall_prototype_preserves_alpha_geometry_and_quiet_repeat_edges():
    from PIL import Image
    folder = DEMO/'repair_candidates/back_wall_refresh_v1'
    r = json.loads((folder/'checks.json').read_text())
    a = next(a for a in json.loads((ROOT/'metadata/manifest.json').read_text())['assets'] if a['id']==r['id'])
    source = Image.open(ROOT/a['final_path'])
    candidate = Image.open(folder/r['candidate_path'])
    assert source.mode == candidate.mode == 'RGBA'
    assert source.size == candidate.size == (32,52)
    assert source.getchannel('A').tobytes() == candidate.getchannel('A').tobytes()
    assert r['anchor'] == a['anchor'] == 'wall_center'
    assert r['logical_footprint'] == [a['footprint_width_tiles'],a['footprint_height_tiles']] == [1,1]
    assert hashlib.sha256((ROOT/a['final_path']).read_bytes()).hexdigest() == r['source_sha256'] == a['normalized_sha256']
    assert sum(p[:3]!=q[:3] for p,q in zip(source.get_flattened_data(),candidate.get_flattened_data())) == r['rgb_changed_pixels']
    assert set(candidate.get_flattened_data()) <= set(source.get_flattened_data())
    for y in range(52):
        assert candidate.getpixel((0,y)) == candidate.getpixel((31,y))
        # Matching two dark boundary pixels alone must not pass the check.
        assert candidate.getpixel((0,y)) == candidate.getpixel((1,y)) == candidate.getpixel((30,y))
    assert r['status'] == 'reference_only_unapproved'
