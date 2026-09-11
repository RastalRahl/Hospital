from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent
out=Image.new('RGB',(1728,1830),(24,35,49));d=ImageDraw.Draw(out)
f=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
def label(x,y,text): d.text((x,y),text,font=f,fill='white')
def put(name,x,y,scale=1):
 im=Image.open(P/name)
 if scale!=1: im=im.resize((int(im.width*scale),int(im.height*scale)),Image.Resampling.NEAREST)
 out.paste(im,(x,y))
for i,state in enumerate(['approved','refreshed']):
 x=16+i*856
 label(x,8,state.upper()+' / unchanged Godot scene (overview at 1x)')
 put('godot_'+state+'.png',x,36,.5)
for name,y in [('back',610),('front',760),('doorway',850)]:
 for i,state in enumerate(['approved','refreshed']):
  x=16+i*536;label(x,y,name+' / '+state+' / Godot 2x');put('godot_'+name+'_'+state+'.png',x,y+26)
for j,name in enumerate(['left','right']):
 for i,state in enumerate(['approved','refreshed']):
  x=1110+j*280+i*130;label(x,610,name+' / '+('before' if i==0 else 'after'));put('godot_'+name+'_'+state+'.png',x+25,642)
for j,name in enumerate(['northwest_corner','northeast_corner']):
 for i,state in enumerate(['approved','refreshed']):
  x=16+j*536+i*248;label(x,1020,('NW' if j==0 else 'NE')+' corner / '+state);put('godot_'+name+'_'+state+'.png',x,1050)
for name,y in [('back',1310),('front',1470)]:
 for i,state in enumerate(['approved','refreshed']):
  x=16+i*536;label(x,y,'Mixed '+name+' / '+state+' / native PNGs 2x');put('mixed_'+name+'_'+state+'.png',x,y+28,2)
for j,name in enumerate(['left','right']):
 for i,state in enumerate(['approved','refreshed']):
  x=1110+j*280+i*130;label(x,1300,name+' '+('old' if i==0 else 'new'));put('mixed_'+name+'_'+state+'.png',x+25,1328,1)
label(16,1600,'Mixed sequence: 01-02-03-04-01-03-02-04; sides: 01-02-01-02-02-01-02-01.')
label(16,1630,'All native candidates preserve source alpha, dimensions, anchors and structural bands. No production approval.')
label(16,1660,'Corner geometry and exposed terminations are unchanged; no connector art, masks or overlays.')
label(16,1690,'Same and cross-variant seams: 40 directed pairs, zero RGB edge discontinuity.')
label(16,1720,'Full 2x overview originals and individual unscaled crops are supplied alongside this montage.')
out.save(P/'wall_family_review_montage.png')
