from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
P = Path(__file__).resolve().parent
sheet = Image.new('RGB', (1584,572), (24,35,49))
draw = ImageDraw.Draw(sheet)
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
for i,label in enumerate(['approved','v1','v2']):
    x = 8+i*528
    draw.text((x,8),label.upper()+' / Godot 2x / identical camera',font=font,fill='white')
    sheet.paste(Image.open(P/f'godot_8cell_{label}.png'),(x,36))
    draw.text((x,154),'Internal doorway wall / unchanged scene',font=font,fill='white')
    sheet.paste(Image.open(P/f'godot_{label}.png').crop((1024,420,1536,804)),(x,182))
sheet.save(P/'wall_three_way_review.png')
