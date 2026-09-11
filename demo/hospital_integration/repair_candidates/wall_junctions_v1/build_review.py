"""Present unchanged-camera Godot captures and measure bounded pixel changes."""
from pathlib import Path
import json
from PIL import Image, ImageChops, ImageDraw, ImageFont

P = Path(__file__).resolve().parent
data = json.loads((P/'junctions.json').read_text())
before = Image.open(P/'godot_before.png').convert('RGB')
after = Image.open(P/'godot_after.png').convert('RGB')
assert before.size == after.size == (1664, 1088)
# Same fixed camera as main.gd: center (368,232), integer zoom 2.
origin = (before.width//2 - 368*2, before.height//2 - 232*2)
mask = Image.new('L', before.size)
draw = ImageDraw.Draw(mask)
draw.rectangle((0, 0, before.width-1, 139), fill=255)  # HUD only
boxes = []
for p in data['placements']:
    a = data['assets'][p['view']]
    x, y = [p['position'][i] - a['image_anchor'][i] for i in range(2)]
    w, h = a['native_size']
    box = [origin[0]+x*2, origin[1]+y*2, origin[0]+(x+w)*2, origin[1]+(y+h)*2]
    draw.rectangle((box[0], box[1], box[2]-1, box[3]-1), fill=255)
    boxes.append({'junction': p['name'], 'screen_bounds_half_open': box})
# RGB-to-L can round very small chromatic changes away; union channel masks.
diff = ImageChops.difference(before, after)
changed = ImageChops.lighter(ImageChops.lighter(*diff.split()[:2]), diff.split()[2]).point(lambda p: 255 if p else 0)
outside = ImageChops.subtract(changed, mask)
assert outside.getbbox() is None, 'Changes outside explicit junction carriers and HUD'
checks = {'status': 'reference_only_unapproved', 'method': 'Godot before/after RGB channel union, fixed camera at 2x; allowed mask is six explicit native carrier bounds plus HUD',
          'changed_pixels_including_hud': changed.histogram()[255],
          'changed_pixels_outside_junctions_and_hud': outside.histogram()[255],
          'allowed_junction_regions': boxes}
(P/'review_checks.json').write_text(json.dumps(checks, indent=2)+'\n')

out = Image.new('RGB', (1728, 1230), (24,35,49))
d = ImageDraw.Draw(out)
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 20)
small = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 17)
d.text((16,12), 'WALL JUNCTION PROTOTYPE / reference only / same Godot scene and grid positions', font=font, fill='white')
for i, state in enumerate(('before','after')):
    x = 16 + i*856
    d.text((x,46), 'BEFORE: refreshed walls' if i == 0 else 'AFTER: connected returns and corners', font=font, fill='white')
    im = Image.open(P/('godot_'+state+'.png'))
    out.paste(im.resize((832,544), Image.Resampling.NEAREST), (x,74))
for i, (name,title) in enumerate([
    ('northwest','Northwest corner'), ('divider_north','Internal north branch'), ('northeast','Northeast corner'),
    ('southwest','Southwest corner'), ('divider_east','Side to full-height wall'), ('southeast','Southeast corner'),
]):
    x, y = 16 + (i%3)*568, 638+(i//3)*266
    d.text((x,y), title+' / before                 after', font=small, fill='white')
    for j,state in enumerate(('before','after')):
        out.paste(Image.open(P/(name+'_'+state+'.png')), (x+j*268,y+28))
d.text((16,1176), 'Close-ups: unscaled Godot 2x crops; props hidden only to expose joints. No layout changes.',font=small,fill='white')
d.text((16,1203), 'J toggles this prototype. Six native views; no production approval or inventory additions.',font=small,fill='white')
out.save(P/'junction_review_montage.png')
print('Comparison verified: 0 changed pixels outside six junction carriers and HUD.')
