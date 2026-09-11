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
        return 32<=x<=800 and 96<=y<=440 and not any(x+9>l and x-9<l+w and y>t and y-8<t+h for l,t,w,h in solids)
    start=(416,400); seen={start}; queue=deque([start])
    while queue:
        x,y=queue.popleft()
        for q in [(x-4,y),(x+4,y),(x,y-4),(x,y+4)]:
            if q not in seen and clear(*q):seen.add(q);queue.append(q)
    for destination in [(144,244),(112,344),(208,344),(416,320),(432,240),(464,288),(672,252),(736,216),(736,300)]:
        assert destination in seen, f'No walking access to {destination}'
