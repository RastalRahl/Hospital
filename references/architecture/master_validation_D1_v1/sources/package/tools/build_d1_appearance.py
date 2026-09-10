"""Build a reference-only D1 appearance candidate and measured local review evidence.

Run: python tools/build_d1_appearance.py
Requires: Pillow, numpy. All inputs are local. No repository or network writes.
Geometry/alpha authority: Hospital commit 9ed992f57585d77448f3e396b8f4dc6f25aa5987.
This is NOT production approval and does NOT run the Hospital repository test suite.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SRC, CAND, PREV, REPORT = (ROOT / name for name in ('sources', 'candidate', 'previews', 'reports'))
COMMIT = '9ed992f57585d77448f3e396b8f4dc6f25aa5987'
CANON_HASH = '51a11bddc75b2b51bb387b056f829c79315c0d714459784ab9c0ae3bea3564d6'
INPUT_BLOBS = {
    'hospital_wall_back_straight_01.png': '4dc2a6d91b1302c55aa9e70033a537737c1fa8e4',
    'hospital_floor_plain_01.png': 'e4b7c1e6708af1d2ae648b0787d651fbf9ac2814',
}
STEM = 'rastalr_D1_glass_partition_back_locked_v1'


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> Image.Image:
    with Image.open(path) as image:
        return image.convert('RGBA')


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')


def histogram(array: np.ndarray) -> dict[str, int]:
    return {str(k): int(v) for k, v in sorted(Counter(array.flatten().tolist()).items())}


def edit_rgb(canonical: Image.Image) -> Image.Image:
    """Paint only RGB on the native grid. Never paint/resample the alpha channel."""
    a = np.array(canonical).copy()
    # Uniform pane with two restrained hard-edged horizontal value changes.
    # The last interior column remains neutral, suitable for D0's repeat extension.
    a[5:23, 4:28, :3] = (146, 182, 195)
    a[5:7, 4:28, :3] = (153, 189, 201)
    a[21:23, 4:28, :3] = (137, 173, 187)
    reflection = np.argwhere(a[:, :, 3] == 210)
    for i, (y, x) in enumerate(reflection):
        a[y, x, :3] = ((180, 205, 216) if i < 3 else
                      (171, 199, 211) if i < 7 else (162, 191, 205))

    # Five-pixel rails: silhouette, highlight, two face values, inner gasket.
    top = [(24, 35, 49), (172, 197, 208), (110, 141, 161), (86, 116, 138), (30, 44, 58)]
    bottom = [(30, 44, 58), (104, 134, 154), (80, 109, 130), (61, 87, 108), (24, 35, 49)]
    for y, rgb in enumerate(top):
        a[y, 4:28, :3] = rgb
    for dy, rgb in enumerate(bottom):
        a[23 + dy, 4:28, :3] = rgb

    # Four-pixel posts, lighting from upper-left, same geometry on both sides.
    # No highlight or outline is allowed to expand into the pane.
    post_columns = [(24, 35, 49), (86, 112, 131), (51, 73, 91), (39, 55, 70)]
    for x0 in (0, 28):
        for dx, rgb in enumerate(post_columns):
            a[:, x0 + dx, :3] = rgb
        a[0, x0:x0 + 4, :3] = (24, 35, 49)
        a[1, x0 + 1:x0 + 3, :3] = (137, 164, 180)
        a[2, x0 + 1:x0 + 3, :3] = (86, 112, 131)
        a[26, x0 + 1:x0 + 3, :3] = (51, 73, 91)
        a[27, x0:x0 + 4, :3] = (24, 35, 49)
    if not np.array_equal(a[:, :, 3], np.asarray(canonical)[:, :, 3]):
        raise ValueError('RGB-only edit changed alpha')
    return Image.fromarray(a)


def repeat_variant(terminal: Image.Image) -> Image.Image:
    """D0 rule: extend column 27 into [28,32); following cell owns its left post."""
    a = np.array(terminal).copy()
    a[:, 28:32, :] = a[:, 27:28, :]
    return Image.fromarray(a)


def assemble(terminal: Image.Image, repeat: Image.Image, count: int,
             stride: int = 32) -> tuple[Image.Image, list[list[int]]]:
    out = Image.new('RGBA', (32 * count, 28))
    origins = []
    for i in range(count):
        origins.append([stride * i, 0])
        # Paste without an alpha mask preserves straight RGBA bytes; cells do not overlap.
        out.paste(terminal if i == count - 1 else repeat, (stride * i, 0))
    return out, origins


def opaque_runs(image: Image.Image, y: int = 14) -> list[list[int]]:
    row = np.asarray(image)[:, :, 3][y] == 255
    changes = np.diff(np.r_[False, row, False].astype(int))
    return [[int(l), int(r)] for l, r in zip(np.where(changes == 1)[0], np.where(changes == -1)[0])]


def check_run(image: Image.Image, canonical: Image.Image, count: int,
              origins: list[list[int]]) -> dict:
    """Independently check PNG pixels against the source alpha + declared D0 edge rule."""
    a = np.asarray(image)
    expected_shape = (28, count * 32, 4)
    shape_ok = a.shape == expected_shape
    checks = {'rgba_dimensions': shape_ok,
              'declared_origins_match_stride': origins == [[i * 32, 0] for i in range(count)]}
    if not shape_ok:
        return {'pass': False, 'checks': checks, 'observed_size': list(image.size)}
    canonical_alpha = np.asarray(canonical)[:, :, 3]
    expected_alpha = np.empty((28, count * 32), dtype=np.uint8)
    # This reference calculation does not use repeat_variant() or assemble().
    for y in range(28):
        for x in range(count * 32):
            cell, local_x = divmod(x, 32)
            sample_x = 27 if cell < count - 1 and local_x >= 28 else local_x
            expected_alpha[y, x] = canonical_alpha[y, sample_x]
    actual_alpha = a[:, :, 3]
    frame = expected_alpha == 255
    pane = ~frame
    mismatch_count = int(np.count_nonzero(actual_alpha != expected_alpha))
    observed_runs = opaque_runs(image)
    expected_runs = [[i * 32, i * 32 + 4] for i in range(count)] + [[count * 32 - 4, count * 32]]
    checks.update({
        'exact_source_alpha_with_shared_edge_rule': mismatch_count == 0,
        'required_frame_opaque': bool(np.all(actual_alpha[frame] == 255)),
        'pane_translucent_without_holes': bool(np.all((actual_alpha[pane] > 0) & (actual_alpha[pane] < 255))),
        'measured_post_widths': observed_runs == expected_runs,
        'no_alpha_accumulation': bool(np.array_equal(actual_alpha[pane], expected_alpha[pane])),
    })
    return {'pass': all(checks.values()), 'checks': checks,
            'expected_size': [32 * count, 28], 'observed_size': list(image.size),
            'observed_opaque_post_runs_at_y14': observed_runs,
            'alpha_mismatches': mismatch_count, 'alpha_histogram': histogram(actual_alpha)}


def backing(width: int, height: int, kind: str = 'light') -> Image.Image:
    colors = {'light': (227, 223, 212, 255), 'dark': (49, 62, 76, 255)}
    if kind in colors:
        return Image.new('RGBA', (width, height), colors[kind])
    out = Image.new('RGBA', (width, height), (216, 211, 198, 255))
    d = ImageDraw.Draw(out)
    for x in range(0, width, 16):
        d.rectangle([x, 0, min(width - 1, x + 7), height - 1], fill=(77, 150, 155, 255))
        d.rectangle([x + 8, 0, min(width - 1, x + 15), height - 1], fill=(175, 112, 118, 255))
    for x in range(12, width, 32):
        d.rectangle([x, 10, min(x + 6, width - 1), 18], fill=(235, 211, 155, 255))
        d.line([x, 14, min(x + 6, width - 1), 14], fill=(66, 72, 79, 255))
    return out


def enlarged(image: Image.Image, scale: int) -> Image.Image:
    return image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    # Fonts are used only to label previews. No font files are distributed.
    candidate = '/usr/share/fonts/truetype/dejavu/DejaVuSans' + ('-Bold' if bold else '') + '.ttf'
    try:
        return ImageFont.truetype(candidate, size)
    except OSError:
        return ImageFont.load_default(size=size)


def context_scene(run: Image.Image, wall: Image.Image, floor: Image.Image) -> tuple[Image.Image, Image.Image, dict]:
    """Translation of D0's baseline rule: walls y=0, glass y=24, shared baseline y=52."""
    native = Image.new('RGBA', (192, 116))
    bg = Image.new('RGBA', native.size)
    # Front floor is an unmodified grid of approved tiles.
    for ty in (52, 84):
        for tx in range(0, 192, 32):
            bg.paste(floor, (tx, ty))
    # Separate rear floor samples visible through the panes; not a cream top rail.
    # Their source rows [4,32) continue the front grid (row 0 starts again at y=52).
    for tx in range(32, 160, 32):
        bg.paste(floor.crop((0, 4, 32, 32)), (tx, 24))
    native.alpha_composite(bg)
    native.alpha_composite(wall, (0, 0))
    native.alpha_composite(wall, (160, 0))
    native.alpha_composite(run, (32, 24))
    # Anchors all map to the same baseline; actual context pixels verify placement.
    a = np.asarray(native)
    run_a = np.asarray(run)
    pane = run_a[:, :, 3] < 255
    expected_region = np.asarray(Image.alpha_composite(bg.crop((32, 24, 160, 52)), run))
    observed_region = a[24:52, 32:160]
    report = {
        'wall_origins_native': [[0, 0], [160, 0]], 'glass_origin_native': [32, 24],
        'derived_bottom_edges_native': [wall.height, 24 + run.height, wall.height],
        'same_baseline': wall.height == 24 + run.height == 52,
        'context_compositing_pixel_mismatches': int(np.count_nonzero(np.any(expected_region != observed_region, axis=2))),
        'left_wall_pixels_unchanged': bool(np.array_equal(a[:52, :32], np.asarray(wall))),
        'right_wall_pixels_unchanged': bool(np.array_equal(a[:52, 160:192], np.asarray(wall))),
        'front_floor_all_opaque': bool(np.all(a[52:, :, 3] == 255)),
        'native_size': [192, 116],
        'notes': 'Straight-run context only. No L/T/cross validation or approval is claimed.',
    }
    report['pass'] = (report['same_baseline'] and report['context_compositing_pixel_mismatches'] == 0
                      and report['left_wall_pixels_unchanged'] and report['right_wall_pixels_unchanged']
                      and report['front_floor_all_opaque'])
    return native, bg, report


def make_preview(canonical: Image.Image, candidate: Image.Image, runs: dict[int, Image.Image],
                 scene: Image.Image, local_qa: dict) -> Image.Image:
    board = Image.new('RGB', (1408, 1336), (23, 35, 48))
    d = ImageDraw.Draw(board)
    text = (230, 234, 235)
    muted = (162, 180, 193)
    def label(x, y, s, size=16, bold=False, subdued=False):
        d.text((x, y), s, font=font(size, bold), fill=muted if subdued else text)
    def panel(x, y, rgba, scale=8, kind='light'):
        view = Image.alpha_composite(backing(*rgba.size, kind), rgba).convert('RGB')
        board.paste(enlarged(view, scale), (x, y))
    label(32, 18, 'D1  /  LOW GLASS PARTITION', 26, True)
    label(32, 56, 'Actual native-grid appearance candidate. RGBA, geometry and alpha locked. Not production-approved.', 15, subdued=True)
    label(32, 98, 'BEFORE: CANONICAL', 16, True)
    label(352, 98, 'D1: RGB-ONLY EDIT', 16, True)
    label(816, 98, 'TWO PANELS / SHARED POST', 16, True)
    panel(32, 128, canonical)
    panel(352, 128, candidate)
    panel(816, 128, runs[2])
    label(32, 362, '32 x 28 native, shown at 8x', 13, subdued=True)
    label(352, 362, 'Same 896 alpha values, revised RGB', 13, subdued=True)
    label(816, 362, '64 x 28 native, also shown at 8x', 13, subdued=True)
    label(32, 408, 'FOUR PANELS / SAME 8x SCALE', 16, True)
    panel(192, 440, runs[4])
    label(192, 678, '32 px stride. Shared posts measure 4 px. Last cell retains its closing post.', 14, subdued=True)
    d.line((32, 720, 1376, 720), fill=(70, 89, 105), width=1)
    label(32, 748, 'TRANSPARENCY CHECK / 4x', 16, True)
    label(608, 748, 'APPROVED-WALL CONTEXT / 4x', 16, True)
    bg = backing(32, 28, 'pattern')
    board.paste(enlarged(bg.convert('RGB'), 4), (48, 794))
    board.paste(enlarged(Image.alpha_composite(bg, candidate).convert('RGB'), 4), (296, 794))
    label(48, 918, 'Background only', 13, subdued=True)
    label(296, 918, 'Same background + D1', 13, subdued=True)
    label(48, 960, 'D1 on a dark background', 14)
    panel(48, 990, candidate, scale=4, kind='dark')
    label(224, 990, 'Measured local checks', 15, True)
    label(224, 1022, 'Alpha changes: 0', 14)
    label(224, 1048, 'RGBA/native size: PASS', 14)
    label(224, 1074, '1 / 2 / 4 repeats: PASS', 14)
    label(224, 1100, 'Exact 8x blocks: PASS', 14)
    bgscene = Image.new('RGBA', scene.size, (49, 62, 76, 255))
    board.paste(enlarged(Image.alpha_composite(bgscene, scene).convert('RGB'), 4), (608, 790))
    label(32, 1170, 'Native view:', 14)
    panel(150, 1168, candidate, scale=1)
    label(32, 1294, 'Preview backgrounds and labels are separate. No generated board is used as a source.', 14, subdued=True)
    return board


def main() -> dict:
    for folder in (SRC, CAND, PREV, REPORT):
        folder.mkdir(parents=True, exist_ok=True)
    if sha256(SRC / 'glass_partition_1x.png') != CANON_HASH:
        raise ValueError('Canonical input SHA-256 does not match committed D0 contract')
    for name, expected in INPUT_BLOBS.items():
        data = (SRC / name).read_bytes()
        actual = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if actual != expected:
            raise ValueError(f'Approved context input changed: {name}')
    input_hashes = {p.name: sha256(p) for p in SRC.iterdir() if p.is_file()}
    canonical = load(SRC / 'glass_partition_1x.png')
    if canonical.size != (32, 28):
        raise ValueError('Canonical dimensions are not 32x28')
    native = edit_rgb(canonical)
    native_path = CAND / (STEM + '_native.png')
    native.save(native_path)
    native = load(native_path)
    nonterminal = repeat_variant(native)
    repeat_path = CAND / (STEM + '_repeat_native.png')
    nonterminal.save(repeat_path)
    nonterminal = load(repeat_path)
    source_path = CAND / (STEM + '_source_8x.png')
    repeat_source_path = CAND / (STEM + '_repeat_source_8x.png')
    enlarged(native, 8).save(source_path)
    enlarged(nonterminal, 8).save(repeat_source_path)
    before, after = np.asarray(canonical), np.asarray(native)
    alpha_changes = int(np.count_nonzero(before[:, :, 3] != after[:, :, 3]))
    rgb_changes = int(np.count_nonzero(np.any(before[:, :, :3] != after[:, :, :3], axis=2)))
    block_exact = bool(np.array_equal(np.asarray(load(source_path)), np.repeat(np.repeat(after, 8, axis=0), 8, axis=1)))
    source_roundtrip = bool(np.array_equal(np.asarray(load(source_path).resize((32, 28), Image.Resampling.NEAREST)), after))
    runs, run_qa = {}, {}
    for count in (1, 2, 4):
        run, origins = assemble(native, nonterminal, count)
        run_path = PREV / f'd1_run_{count}_native_rgba.png'
        run.save(run_path)
        run = load(run_path)
        runs[count] = run
        run_qa[str(count)] = check_run(run, canonical, count, origins)
        enlarged(run, 8).save(PREV / f'd1_run_{count}_source_8x_rgba.png')
    bg = backing(32, 28, 'pattern')
    bg.save(PREV / 'd1_transmission_background_only.png')
    transmitted = Image.alpha_composite(bg, native)
    transmitted.save(PREV / 'd1_transmission_composite.png')
    light, dark = backing(32, 28, 'light'), backing(32, 28, 'dark')
    c1, c2 = np.asarray(Image.alpha_composite(light, native)), np.asarray(Image.alpha_composite(dark, native))
    pane = after[:, :, 3] < 255
    responsive = np.any(c1[:, :, :3] != c2[:, :, :3], axis=2)
    transmitted_count = int(np.count_nonzero(responsive & pane))
    frame_responsive = int(np.count_nonzero(responsive & ~pane))
    tests = {
        'exact_native_rgba_geometry': native.size == (32, 28) and native.mode == 'RGBA',
        'alpha_map_pixel_lock': alpha_changes == 0,
        'appearance_rgb_changed': rgb_changes > 0,
        'source_exact_eight_by_eight_blocks': block_exact,
        'source_native_roundtrip': source_roundtrip,
        'all_pane_pixels_transmit_background': transmitted_count == int(np.count_nonzero(pane)),
        'opaque_frame_not_affected_by_background': frame_responsive == 0,
        'one_two_four_panel_checks': all(r['pass'] for r in run_qa.values()),
    }
    negative = {}
    broken = native.copy(); broken.putpixel((5, 10), (*broken.getpixel((5, 10))[:3], 0))
    negative['pane_alpha_hole'] = check_run(broken, canonical, 1, [[0, 0]])
    broken = native.copy(); broken.putpixel((1, 26), (0, 0, 0, 0))
    negative['broken_opaque_base'] = check_run(broken, canonical, 1, [[0, 0]])
    broken = native.copy(); broken.putalpha(255)
    negative['fake_opaque_glass'] = check_run(broken, canonical, 1, [[0, 0]])
    broken, origins = assemble(native, native, 2)
    negative['double_width_seam'] = check_run(broken, canonical, 2, origins)
    broken, origins = assemble(native, nonterminal, 2, stride=33)
    negative['one_pixel_stride_shift'] = check_run(broken, canonical, 2, origins)
    broken, origins = assemble(native, nonterminal, 2)
    broken.alpha_composite(native.crop((4, 5, 28, 23)), (4, 5))
    negative['double_coated_glass'] = check_run(broken, canonical, 2, origins)
    intended = {
        'pane_alpha_hole': 'pane_translucent_without_holes',
        'broken_opaque_base': 'required_frame_opaque',
        'fake_opaque_glass': 'pane_translucent_without_holes',
        'double_width_seam': 'measured_post_widths',
        'one_pixel_stride_shift': 'declared_origins_match_stride',
        'double_coated_glass': 'no_alpha_accumulation',
    }
    negative_summary = {}
    for name, result in negative.items():
        key = intended[name]
        detected = not result['pass'] and not result['checks'][key]
        negative_summary[name] = {'intended_check': key, 'detected_for_intended_reason': detected,
                                  'details': result}
    tests['all_six_broken_controls_rejected'] = all(r['detected_for_intended_reason'] for r in negative_summary.values())
    wall, floor = load(SRC / 'hospital_wall_back_straight_01.png'), load(SRC / 'hospital_floor_plain_01.png')
    scene, scene_bg, context_qa = context_scene(runs[4], wall, floor)
    scene.save(PREV / 'd1_approved_wall_context_native.png')
    enlarged(scene, 4).save(PREV / 'd1_approved_wall_context_4x.png')
    scene_bg.save(PREV / 'd1_context_background_only.png')
    tests['straight_approved_wall_context'] = context_qa['pass']
    tests['all_source_files_unchanged'] = input_hashes == {p.name: sha256(p) for p in SRC.iterdir() if p.is_file()}
    qa = {
        'stage': 'local_reference_only_appearance_review', 'repository_commit_read': COMMIT,
        'scope': 'Checks executed here on saved/reloaded candidate PNGs. Not the repository-wide test suite.',
        'status': 'PASS' if all(tests.values()) else 'FAIL', 'checks': tests,
        'native': {'size': list(native.size), 'mode': native.mode, 'rgb_changed_pixels': rgb_changes,
                   'alpha_changed_pixels': alpha_changes, 'alpha_histogram': histogram(after[:, :, 3]),
                   'rgba_color_count': int(len(np.unique(after.reshape(-1, 4), axis=0))),
                   'responsive_pane_pixels': transmitted_count, 'opaque_frame_pixels_responsive_to_background': frame_responsive},
        'source_8x': {'size': [256, 224], 'exact_block_replication': block_exact, 'roundtrip': source_roundtrip},
        'repeats': run_qa, 'straight_context': context_qa, 'negative_controls': negative_summary,
        'source_sha256': input_hashes,
        'limitations': ['No L/T/cross junction appearance or topology work.',
                       'No production ingestion, manifest changes or repository writes.',
                       'Independent Codex validation and user visual approval are still required.',
                       'Terminal/nonterminal files are implementation views of one proposed logical asset.'],
    }
    if not all(tests.values()):
        write_json(REPORT / 'd1_local_checks.json', qa)
        raise ValueError('Local candidate validation failed; see d1_local_checks.json')
    spec = {
        'id': 'hospital_glass_partition_back_01', 'candidate_version': 'locked_appearance_v1',
        'status': 'awaiting_user_appearance_review_reference_only', 'coordinate_convention': '[left,top,right,bottom)',
        'contract_repository_path': 'references/architecture/master_validation_D0_v1/d1_geometry_alpha_contract.json',
        'contract_commit': COMMIT, 'canonical_sha256': CANON_HASH,
        'native_dimensions': [32, 28], 'source_scale': 8, 'source_dimensions': [256, 224],
        'frame_regions_native': {'left_post': [0, 0, 4, 28], 'right_post': [28, 0, 32, 28],
                                 'top_rail': [4, 0, 28, 5], 'bottom_rail': [4, 23, 28, 28]},
        'pane_native': [4, 5, 28, 23], 'alpha_edit_policy': 'Canonical alpha preserved pixel-for-pixel in the terminal/main candidate.',
        'frame_alpha': 255, 'pane_alpha_values': [150, 210],
        'anchor_cell_native': [16, 20], 'anchor_image_native': [16, 28], 'origin_relative_to_cell_native': [0, -8],
        'repeat': {'stride_native': 32, 'shared_post_width_native': 4,
                   'nonterminal_edit_rect': [28, 0, 32, 28], 'extension_column': 27,
                   'use_rule': 'Use repeat/nonterminal for every cell with a glass neighbor on the right. Use main/terminal for the final cell or standalone panel. Do not place both files on the same cell.',
                   'logical_assets': 1, 'implementation_views': 2,
                   'terminal_pane_width_native': 24, 'nonterminal_pane_width_native': 28},
        'normalization_mode': 'architecture_grid_preserving',
        'production_artwork_changed': False, 'canonical_changed': False,
        'sources': {'glass_partition_1x.png': 'references/architecture/rastalr_architecture_v2/glass_partition_1x.png',
                    'hospital_wall_back_straight_01.png': 'assets/architecture/hospital_wall_back_straight_01.png',
                    'hospital_floor_plain_01.png': 'assets/architecture/hospital_floor_plain_01.png'},
    }
    write_json(REPORT / 'd1_candidate_spec.json', spec)
    write_json(REPORT / 'd1_local_checks.json', qa)
    board = make_preview(canonical, native, runs, scene, qa)
    board.save(PREV / 'rastalr_D1_locked_appearance_review.png')
    # Export a simple alpha-lock diagnostic separate from artwork.
    amap = np.where(after[:, :, 3] == 255, 255, np.where(after[:, :, 3] == 210, 170, 90)).astype(np.uint8)
    alpha_img = Image.fromarray(amap).convert('RGB')
    enlarged(alpha_img, 8).save(PREV / 'd1_alpha_regions_diagnostic_8x.png')
    report_md = f'''# D1 local appearance checks\n\nStatus: {qa['status']} for local geometry/alpha checks. Awaiting user appearance review.\n\nThis report was computed from PNG files saved and reloaded in this package.\nIt is not a claim that the complete Hospital test suite was run.\n\n- Native main panel: 32x28 RGBA.\n- 8x source: 256x224, exact nearest-neighbor blocks.\n- Canonical alpha changed pixels: {alpha_changes}.\n- RGB changed pixels: {rgb_changes}.\n- Native RGBA palette entries: {qa['native']['rgba_color_count']}.\n- Alpha histogram: {histogram(after[:, :, 3])}.\n- Pane pixels responding to a background change: {transmitted_count}/432.\n- Frame pixels responding to a background change: {frame_responsive}/464.\n- 1-, 2-, 4-panel runs: actual pixel checks PASS.\n- Six deliberately broken controls: rejected for their intended reasons.\n- Wall-context baseline: 52 native; walls y=0, glass y=24.\n- Original reference PNGs unchanged.\n\n## Repeat rule\n\nOne logical candidate, two implementation views. The main file is standalone/terminal.\nThe repeat file is used when a glass cell follows on the right; column 27 is extended\nthrough x=28..32, exactly as D0 specifies. The next cell owns the shared post.\nDo not layer both views together and do not repeatedly tile the terminal file.\nThe final pane is 24 px wide; nonterminal panes are 28 px wide, as contracted.\n\n## Limits\n\nNo production ingestion or approval, no Git writes, no D2, no all-direction junction claim.\nRGB tint and material treatment need user review and later independent Codex validation.\n\n## Provenance\n\nContract: Hospital commit `{COMMIT}`,\n`references/architecture/master_validation_D0_v1/d1_geometry_alpha_contract.json`.\nCanonical SHA-256: `{CANON_HASH}`.\nContext input Git blobs are verified in the build script.\n\n## Next Codex maintenance note\n\nD0's whole-tree snapshot test must allow authorized future additions without rewriting\nhistorical evidence or weakening protection of previously approved assets. This package\ndoes not modify that test or any repository file.\n'''
    (REPORT / 'd1_local_checks.md').write_text(report_md, encoding='utf-8')
    (ROOT / 'PACKAGE_CONTENTS.md').write_text('''# D1 locked appearance candidate\n\nThis is a reference-only candidate, not an installed or approved asset pack.\n\nOpen `previews/rastalr_D1_locked_appearance_review.png` for appearance review.\n`candidate/*_native.png` contains the actual RGBA artwork.\nThe main file is standalone/terminal; the repeat file is the nonterminal view.\n`*_source_8x.png` is an exact nearest-neighbor working-scale copy.\n\nPreviews are assembled from these candidate files, not independently generated images.\nTheir backgrounds and text labels do not exist in the candidate PNGs.\n\n`sources/` holds unchanged reference inputs, not extra candidates.\n`reports/` holds the local checks and candidate specification.\n`tools/build_d1_appearance.py` reproduces the files using Pillow and numpy.\nNo font binaries are included.\n\nNo approved production files or repository records were changed.\n''', encoding='utf-8')
    files = sorted(p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name != 'SHA256SUMS.txt')
    (ROOT / 'SHA256SUMS.txt').write_text(''.join(f'{sha256(p)}  {p.relative_to(ROOT).as_posix()}\n' for p in files), encoding='utf-8')
    bundle = ROOT.parent / 'rastalr_D1_locked_appearance_review_bundle.zip'
    with zipfile.ZipFile(bundle, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(ROOT.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts:
                # Reproducible archive metadata, independent of local filesystem timestamps.
                info = zipfile.ZipInfo(p.relative_to(ROOT).as_posix(), (2026, 9, 10, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, p.read_bytes())
    return qa


if __name__ == '__main__':
    result = main()
    print('D1 local appearance checks:', result['status'])
    print('Native alpha changes:', result['native']['alpha_changed_pixels'])
    print('Native RGB changes:', result['native']['rgb_changed_pixels'])
    print('Runs:', {k: v['pass'] for k, v in result['repeats'].items()})
