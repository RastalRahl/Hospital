"""Compose unscaled Godot crops plus native-diff inspection panels."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
# 8-cell crops are saved by Godot itself; room context crops retain 2x pixels.
out=Image.new('RGB',(1060,692),(24,35,49));d=ImageDraw.Draw(out)
for i,state in enumerate(('before','after')):
 x=12+i*524
 d.text((x,10),'APPROVED CURRENT' if i==0 else 'REFERENCE-ONLY PROTOTYPE',font=font,fill='white')
 out.paste(Image.open(P/f'godot_8cell_{state}.png').convert('RGB'),(x,38))
 d.text((x,155),'North run: eight copies / native 32px stride',font=font,fill='white')
 shot=Image.open(P/f'godot_{state}.png').convert('RGB')
 out.paste(shot.crop((1024,420,1536,804)),(x,188))
 d.text((x,582),'Internal wall comparison; door + sides unchanged',font=font,fill='white')
 d.text((x,614),'Exact 32x52 RGBA; same anchors and 2x zoom',font=font,fill='white')
d.text((12,656),'No production replacement. Compare repeating face texture before any family propagation.',font=font,fill=(229,220,204))
out.save(P/'wall_review_montage.png')
out=Image.new('RGB',(812,470),(24,35,49));d=ImageDraw.Draw(out)
for i,(name,label) in enumerate([('hospital_wall_back_straight_01_refresh_candidate.png','Native candidate at 8x'),('rgb_change_mask.png','White = changed RGB'),('rgb_absolute_diff.png','Absolute RGB difference')]):
 d.text((12+i*268,10),label,font=font,fill='white')
 out.paste(Image.open(P/name).convert('RGB').resize((256,416),Image.Resampling.NEAREST),(12+i*268,40))
out.save(P/'rgb_diff_diagnostic.png')
