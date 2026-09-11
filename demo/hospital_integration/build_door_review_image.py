"""Assemble labelled, unscaled crops of actual Godot captures for this repair."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent
OUT=P/'captures/door_alpha_repair/door_and_glass_review.png'
# Same pixel coordinates for each pair; no scaling, repainting or compositing
# within the capture crops. 2x native engine pixels remain 2x native pixels.
panels=[
 ('BEFORE: approved opaque opening','captures/door_alpha_repair/before_opaque.png',(1056,576,1568,832)),
 ('AFTER: UNAPPROVED alpha-only candidate','captures/door_alpha_repair/after_transparent.png',(1056,576,1568,832)),
 ('Batch 13 PENDING: figure behind glass','captures/layout_glass_behind.png',(576,256,1088,512)),
 ('Batch 13 PENDING: figure in front of glass','captures/layout_glass_front.png',(576,256,1088,512))]
canvas=Image.new('RGB',(1060,616),(24,35,49))
draw=ImageDraw.Draw(canvas)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
for i,(title,name,box) in enumerate(panels):
 x=12+(i%2)*524;y=10+(i//2)*296
 draw.text((x,y),title,font=font,fill=(239,232,216))
 canvas.paste(Image.open(P/name).convert('RGB').crop(box),(x,y+28))
draw.text((12,599),'Godot viewport crops at 2x. Layout, parked leaves and glass unchanged.',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',13),fill=(210,218,226))
canvas.save(OUT)
print(OUT)
