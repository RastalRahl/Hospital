"""Six deterministic exclusive junction views for six existing demo junctions.

Native pixels, independently sampled left/right profiles; no production writes.
All boxes are half-open. Footprints and anchors are explicit, not canvas-derived.
"""
from pathlib import Path
import hashlib
import json
from PIL import Image

P = Path(__file__).resolve().parent
DEMO = P.parents[1]
FAMILY = P.parent / 'foundation_wall_refresh_family_v1'
IDS = {
    'back': 'hospital_wall_back_straight_01',
    'left': 'hospital_wall_side_left_01',
    'right': 'hospital_wall_side_right_01',
    'front': 'hospital_front_wall_cutaway_01',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    source = {k: FAMILY / (v + '_refresh_candidate.png') for k, v in IDS.items()}
    images = {k: Image.open(v).convert('RGBA') for k, v in source.items()}
    back, front = images['back'], images['front']
    assets = {}
    for side in ('left', 'right'):
        profile = [images[side].getpixel((x, 0)) for x in range(20)]
        # The first side cell owns the 52px north return. Native side body is
        # unchanged; the return meets the existing back cap with a square turn.
        out = Image.new('RGBA', (20, 84))
        for y in range(84):
            for x in range(20):
                edge_distance = x if side == 'left' else 19-x
                color = profile[x]
                if y < 9 and y <= edge_distance:
                    color = back.getpixel((0, y))
                out.putpixel((x, y), color)
        # Retain the exact original native cell, including its subtle texture.
        out.paste(images[side], (0, 52))
        name = 'north_' + side
        path = P / (name + '_junction_candidate.png')
        out.save(path)
        assets[name] = {'path': path.name, 'native_size': list(out.size),
                        'logical_footprint': [1, 1], 'image_anchor': [20 if side == 'left' else 0, 68],
                        'source_paths': [str(source[side].relative_to(DEMO)), str(source['back'].relative_to(DEMO))]}

        # Last side cell owns the front face/base across its full width. The
        # cap terminates at the front top; the exterior edge remains continuous.
        out = images[side].copy()
        for y in range(12, 32):
            for x in range(20):
                outer = x == (0 if side == 'left' else 19)
                color = profile[x] if outer else front.getpixel((0, y-12))
                if y < 15 and (x < 8 if side == 'left' else x >= 12):
                    color = profile[x]
                out.putpixel((x, y), color)
        name = 'south_' + side
        path = P / (name + '_junction_candidate.png')
        out.save(path)
        assets[name] = {'path': path.name, 'native_size': list(out.size),
                        'logical_footprint': [1, 1], 'image_anchor': [20 if side == 'left' else 0, 16],
                        'source_paths': [str(source[side].relative_to(DEMO)), str(source['front'].relative_to(DEMO))]}

    # A branch has wall on both sides of its north contact, unlike an exterior
    # corner: let the horizontal top cap pass over the vertical return.
    out = Image.open(P/'north_left_junction_candidate.png').copy()
    for y in range(9):
        for x in range(20):
            if y < 7 or x >= 9:
                out.putpixel((x, y), back.getpixel((0, y)))
    path = P/'north_branch_junction_candidate.png'
    out.save(path)
    assets['north_branch'] = {**assets['north_left'], 'path': path.name}

    # The divider's final two cells own a full-height east-going return.
    # Back cap starts 28px into this carrier (world y=284); base ends at y=336.
    # Native footprint stays two cells; the extra 16px is declared visual extent.
    out = Image.new('RGBA', (20, 80))
    left = images['left']
    for y in range(80):
        for x in range(20):
            color = left.getpixel((x, y % 32))
            if y >= 28:
                color = back.getpixel((0, y-28))
                if x == 0 or (y < 36 and x < 8):
                    color = left.getpixel((x, 0))
            out.putpixel((x, y), color)
    path = P / 'divider_east_junction_candidate.png'
    out.save(path)
    assets['divider_east'] = {'path': path.name, 'native_size': list(out.size),
                              'logical_footprint': [1, 2], 'image_anchor': [20, 64],
                              'source_paths': [str(source['left'].relative_to(DEMO)), str(source['back'].relative_to(DEMO))]}
    for a in assets.values():
        a.update(status='reference_only_unapproved', reuse_scope='everyday_world_common',
                 anchor='grid', sha256=sha(P/a['path']))
    # A replacement selector addresses an existing sprite by logical key and
    # ground position. No existing sprite transform or collision is rewritten.
    def selector(side, x, y):
        return {'asset': IDS[side] + '__main', 'position': [x, y]}
    placements = [
        {'name': 'northwest', 'view': 'north_left', 'position': [32, 112], 'sort_y': 112,
         'replaces': [selector('left', 32, 112)]},
        {'name': 'northeast', 'view': 'north_right', 'position': [704, 112], 'sort_y': 112,
         'replaces': [selector('right', 704, 112)]},
        {'name': 'divider_north', 'view': 'north_branch', 'position': [512, 112], 'sort_y': 112,
         'replaces': [selector('left', 512, 112)]},
        {'name': 'southwest', 'view': 'south_left', 'position': [32, 400], 'sort_y': 416,
         'replaces': [selector('left', 32, 400)]},
        {'name': 'southeast', 'view': 'south_right', 'position': [704, 400], 'sort_y': 416,
         'replaces': [selector('right', 704, 400)]},
        {'name': 'divider_east', 'view': 'divider_east', 'position': [512, 320], 'sort_y': 336,
         'replaces': [selector('left', 512, 272), selector('left', 512, 304)]},
    ]
    report = {'status': 'reference_only_unapproved', 'grid_px': 32,
              'inventory_delta': 0, 'assets': assets, 'placements': placements,
              'source_sha256': {str(v.relative_to(DEMO)): sha(v) for v in source.values()},
              'runtime_manifest_sha256': sha(DEMO/'runtime_manifest.json'),
              'collision_additions': [[24,88,8,8], [704,88,8,8], [504,320,8,16]],
              'collision_note': 'Complete missing centered 8px strip contacts only while junction mode is enabled.'}
    (P/'junctions.json').write_text(json.dumps(report, indent=2)+'\n')
    print('Built 6 exclusive reference views at 6 junctions; 0 logical inventory additions.')


if __name__ == '__main__':
    build()
