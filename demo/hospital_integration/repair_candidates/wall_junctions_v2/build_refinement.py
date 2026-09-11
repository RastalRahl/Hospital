"""Bounded RGB refinement of V1 junctions; geometry, alpha and contacts locked."""
from pathlib import Path
import hashlib
import json
import shutil
from PIL import Image, ImageChops

P = Path(__file__).resolve().parent
V1 = P.parent/'wall_junctions_v1'
FAMILY = P.parent/'foundation_wall_refresh_family_v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    data = json.loads((V1/'junctions.json').read_text())
    back = Image.open(FAMILY/'hospital_wall_back_straight_01_refresh_candidate.png')
    front = Image.open(FAMILY/'hospital_front_wall_cutaway_01_refresh_candidate.png')
    sides = {s: Image.open(FAMILY/f'hospital_wall_side_{s}_01_refresh_candidate.png') for s in ('left','right')}
    checks = []
    for name, a in data['assets'].items():
        old = Image.open(V1/a['path'])
        out = old.copy()
        if name.startswith('north_'):
            side = 'right' if name == 'north_right' else 'left'
            profile = [sides[side].getpixel((x,0)) for x in range(20)]
            exterior = name != 'north_branch'
            edge = 19 if side == 'right' else 0
            for y in range(52):
                for x in range(20):
                    # Full-height back plaster/base crosses the return. There
                    # is no blue cap or dark interior outline running up its face.
                    color = back.getpixel((0,y))
                    if exterior and x == edge:
                        color = profile[edge]
                    elif exterior and x == (18 if side == 'right' else 1) and 9 <= y < 45:
                        color = profile[10 if side == 'right' else 13]
                    # Short grounded contact, only within the back's base band.
                    # The branch meets the low cutaway here, not at a tall post.
                    if 46 <= y < 52 and (x >= 11 if side == 'right' else x < 9):
                        color = profile[x]
                    out.putpixel((x,y),color)
        elif name.startswith('south_'):
            side = name.removeprefix('south_')
            profile = [sides[side].getpixel((x,0)) for x in range(20)]
            edge = 19 if side == 'right' else 0
            # A four-row slate end shoe closes the blue side cap BEFORE the
            # ivory front cap; no blue stub projects through the ivory face.
            end = [profile[x] for x in ([17,15,13,12] if side == 'right' else [2,4,6,7])]
            for y in range(8,12):
                for x in range(20):
                    if (x >= 12 if side == 'right' else x < 8):
                        out.putpixel((x,y),profile[edge] if x == edge else end[y-8])
            for y in range(12,32):
                for x in range(20):
                    out.putpixel((x,y),profile[edge] if x == edge else front.getpixel((0,y-12)))
        # The lower internal divider was already effective. Preserve its file.
        dest = P/a['path']
        if name == 'divider_east':
            shutil.copyfile(V1/a['path'],dest)
        else:
            out.save(dest)
        assert old.size == out.size and old.getchannel('A').tobytes() == out.getchannel('A').tobytes()
        a['sha256'] = sha(dest)
        checks.append({'view':name,'v1_sha256':sha(V1/a['path']),'v2_sha256':a['sha256'],
                       'alpha_changed_pixels':0,
                       'rgb_change_bounds_half_open':ImageChops.difference(old.convert('RGB'),out.convert('RGB')).getbbox(),
                       'rgb_changed_pixels':sum(p[:3]!=q[:3] for p,q in zip(old.get_flattened_data(),out.get_flattened_data()))})
    data['refinement'] = {'baseline':'wall_junctions_v1 at 9740fae2fa9ad8042d4d85433fa5d36944080bfd',
                          'scope':'RGB only: three north returns and two front corners; lower divider byte-identical',
                          'checks':checks}
    (P/'junctions.json').write_text(json.dumps(data,indent=2)+'\n')
    print([(c['view'],c['rgb_changed_pixels']) for c in checks])


if __name__ == '__main__':
    build()
