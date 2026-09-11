"""V1/V2 Godot comparison, following the existing six-contact review layout."""
from pathlib import Path
import json
from PIL import Image, ImageChops, ImageDraw, ImageFont

P = Path(__file__).resolve().parent
data = json.loads((P/'junctions.json').read_text())
before = Image.open(P/'godot_before.png').convert('RGB')
after = Image.open(P/'godot_after.png').convert('RGB')
assert before.size == after.size == (1664,1088)
origin = (before.width//2-368*2, before.height//2-232*2)
mask = Image.new('L',before.size)
d = ImageDraw.Draw(mask)
d.rectangle((0,0,before.width-1,139),fill=255)
changes = {c['view']:c for c in data['refinement']['checks']}
boxes = []
for p in data['placements']:
    a = data['assets'][p['view']]
    bounds = changes[p['view']]['rgb_change_bounds_half_open']
    if bounds is None:
        continue
    x,y = [p['position'][i]-a['image_anchor'][i] for i in range(2)]
    box = [origin[0]+(x+bounds[0])*2,origin[1]+(y+bounds[1])*2,
           origin[0]+(x+bounds[2])*2,origin[1]+(y+bounds[3])*2]
    d.rectangle((box[0],box[1],box[2]-1,box[3]-1),fill=255)
    boxes.append({'junction':p['name'],'screen_bounds_half_open':box})
channels = ImageChops.difference(before,after).split()
changed = ImageChops.lighter(ImageChops.lighter(channels[0],channels[1]),channels[2]).point(lambda p:255 if p else 0)
outside = ImageChops.subtract(changed,mask)
assert outside.getbbox() is None, 'RGB changes outside declared refinement bounds/HUD'
checks = {'status':'reference_only_unapproved','comparison':'fresh Godot V1 vs V2; same camera, placements, collisions and furnished scene',
          'method':'RGB channel union, allowed bounds derived from native V1/V2 RGB diff boxes; HUD excluded',
          'changed_pixels_including_hud':changed.histogram()[255],
          'changed_pixels_outside_refinement_and_hud':outside.histogram()[255],
          'allowed_regions':boxes}
(P/'review_checks.json').write_text(json.dumps(checks,indent=2)+'\n')

out=Image.new('RGB',(1728,1230),(24,35,49)); d=ImageDraw.Draw(out)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
d.text((16,12),'WALL JUNCTION REFINEMENT / V1 to V2 / identical geometry and scene',font=font,fill='white')
for i,state in enumerate(('before','after')):
    x=16+i*856
    d.text((x,46),'V1: framed returns / protruding cap ends' if i==0 else 'V2: continuous plaster / defined cap ends',font=font,fill='white')
    out.paste(Image.open(P/('godot_'+state+'.png')).resize((832,544),Image.Resampling.NEAREST),(x,74))
for i,(name,title) in enumerate([('northwest','Northwest'),('divider_north','North branch'),('northeast','Northeast'),
                                ('southwest','Southwest cap end'),('divider_east','Lower divider: unchanged'),('southeast','Southeast cap end')]):
    x,y=16+(i%3)*568,638+(i//3)*266
    d.text((x,y),title+' / V1                         V2',font=small,fill='white')
    for j,state in enumerate(('before','after')):
        out.paste(Image.open(P/(name+'_'+state+'.png')),(x+j*268,y+28))
d.text((16,1176),'Close-ups: unscaled Godot 2x; props hidden to expose joints. Furnished overviews: 1x.',font=small,fill='white')
d.text((16,1203),'J enables junctions; K compares V1/V2. Reference only; production promotion remains on hold.',font=small,fill='white')
out.save(P/'junction_refinement_review.png')
print('PASS: no scene changes outside five native RGB refinement regions and HUD.')
