"""Bounded RGB-only wall reference propagation; no production writes."""
from pathlib import Path
from PIL import Image
import hashlib
import itertools
import json
import math
import shutil

P = Path(__file__).resolve().parent
ROOT = P.parents[3]
V2 = P.parent/'back_wall_refresh_v2/hospital_wall_back_straight_01_refresh_candidate_v2.png'
GROUPS = {
    'back': [f'hospital_wall_back_straight_{i:02}' for i in range(1,5)],
    'left': [f'hospital_wall_side_left_{i:02}' for i in range(1,3)],
    'right': [f'hospital_wall_side_right_{i:02}' for i in range(1,3)],
    'front': [f'hospital_front_wall_cutaway_{i:02}' for i in range(1,5)],
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def luma(pixel):
    return sum(v*c for v,c in zip(pixel, (.2126,.7152,.0722)))

def lines(im, vertical):
    return [[im.getpixel((x,y)) for x in range(im.width)] for y in range(im.height)] if vertical else [[im.getpixel((x,y)) for y in range(im.height)] for x in range(im.width)]

def periodicity(im, vertical):
    values = [sum(map(luma,row))/len(row) for row in lines(im,vertical)]
    n = len(values)
    return {'axis_column_or_row_mean_luma_range': max(values)-min(values),
            'period_32_amplitude': 2*abs(sum(v*complex(math.cos(2*math.pi*i/32),math.sin(2*math.pi*i/32)) for i,v in enumerate(values)))/n}

def build():
    manifest = {a['id']:a for a in json.loads((ROOT/'metadata/manifest.json').read_text())['assets']}
    report = {'status':'reference_only_unapproved', 'visual_language':'human-approved V2 at 1239ed8126ae7446d59a412ce2f2c85fea269ccd; no production approval', 'assets':[], 'adjacencies':[], 'mixed_runs':{}}
    for group,names in GROUPS.items():
        originals = [Image.open(ROOT/manifest[n]['final_path']) for n in names]
        reference = originals[0]
        candidates = []
        for variant,(name,original) in enumerate(zip(names, originals)):
            out = original.copy()
            if group == 'back':
                out = Image.open(V2).copy()
                if variant:
                    for y in range(9,45):
                        for x in range(32): out.putpixel((x,y),(230,223,211,original.getpixel((x,y))[3]))
                    for x,y in [(8+variant,13+variant*3),(18-variant,29+variant),(21,38-variant)]:
                        for dx,dy in [(0,0),(1,0),(0,1)]: out.putpixel((x+dx,y+dy),(228,224,207,255))
            else:
                # Independently sample each approved orientation's own transverse
                # profile. Never rotate/mirror. Keep all structural band coordinates.
                for y in range(out.height):
                    for x in range(out.width):
                        rgb = reference.getpixel((x,16) if group in ('left','right') else (16,y))[:3]
                        out.putpixel((x,y),(*rgb,original.getpixel((x,y))[3]))
                if group == 'front':
                    points = [(9+variant*2,5),(20-variant,8)]
                elif group == 'left':
                    points = [(11,10+variant*5),(13,22-variant*3)]
                else:
                    points = [(5,12+variant*3),(7,23-variant*4)]
                for x,y in points:
                    for dx,dy in [(0,0),(1,0),(0,1)]:
                        r,g,b,a = out.getpixel((x+dx,y+dy))
                        out.putpixel((x+dx,y+dy),(r+2,g-1,b+4,a))
            path = P/(name+'_refresh_candidate.png')
            out.save(path)
            if name == GROUPS['back'][0]: shutil.copyfile(V2,path)
            assert out.size == original.size and out.mode == original.mode == 'RGBA'
            assert out.getchannel('A').tobytes() == original.getchannel('A').tobytes()
            a = manifest[name]
            report['assets'].append({'id':name,'group':group,'source_path':a['final_path'],'candidate_path':path.name,'dimensions':list(out.size),'mode':out.mode,'alpha_changed_pixels':0,'rgb_changed_pixels':sum(p[:3]!=q[:3] for p,q in zip(original.get_flattened_data(),out.get_flattened_data())),'source_sha256':sha(ROOT/a['final_path']),'candidate_sha256':sha(path),'anchor':a['anchor'],'logical_footprint':[a['footprint_width_tiles'],a['footprint_height_tiles']],'source_approval':a['approval_status'],'same_repeat_periodicity':periodicity(out,group in ('left','right'))})
            candidates.append(out)
        vertical = group in ('left','right')
        for i,j in itertools.product(range(len(names)),repeat=2):
            a,b = lines(candidates[i],vertical),lines(candidates[j],vertical)
            assert a[-1] == a[-2] == b[0] == b[1]
            assert all(p[3] == 255 for row in [a[-1],b[0]] for p in row)
            report['adjacencies'].append({'from':names[i],'to':names[j],'edge_rgb_mae':0,'three_transition_rgb_mae':0,'transparent_gap_pixels':0})
        sequence = [0,1,2,3,0,2,1,3] if len(names)==4 else [0,1,0,1,1,0,1,0]
        for label,images in [('approved',originals),('refreshed',candidates)]:
            run = Image.new('RGBA',(20,256) if vertical else (256,reference.height))
            for k,v in enumerate(sequence): run.paste(images[v],(0,k*32) if vertical else (k*32,0))
            run.save(P/f'mixed_{group}_{label}.png')
            if label == 'refreshed': report['mixed_runs'][group] = {'sequence':[names[v] for v in sequence],'stride':32,'gaps':0,'overlaps':0,**periodicity(run,vertical)}
    (P/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print([(a['id'],a['rgb_changed_pixels']) for a in report['assets']])
    print('40 same/cross-variant directed adjacencies passed')

if __name__ == '__main__':
    build()
