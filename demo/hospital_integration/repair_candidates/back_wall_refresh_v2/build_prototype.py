from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,math,hashlib
P=Path(__file__).resolve().parent
DEMO=P.parents[1];ROOT=P.parents[3]
V1=P.parent/'back_wall_refresh_v1/hospital_wall_back_straight_01_refresh_candidate.png'
SRC=ROOT/'assets/architecture/hospital_wall_back_straight_01.png'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def luminance(p):return .2126*p[0]+.7152*p[1]+.0722*p[2]
def build():
    v1=Image.open(V1);source=Image.open(SRC);out=v1.copy()
    base=(230,223,211)
    # Tiny chromatic plaster inclusions with equal Rec.709 luma to within
    # 0.0012/255; not highlight/shadow, a gradient, or a dither pattern.
    warm=(228,224,207);cool=(232,222,215)
    for y in range(52):
        for x in range(32):
            rgb=base if 9<=y<45 else v1.getpixel((0,y))[:3]
            out.putpixel((x,y),(*rgb,v1.getpixel((x,y))[3]))
    clusters=[(warm,[(8,16),(9,16),(10,16),(8,17),(9,17)]),
              (cool,[(19,22),(20,22),(21,22),(20,23),(21,23)]),
              (cool,[(12,32),(13,32),(12,33),(13,33)]),
              (warm,[(22,38),(23,38),(22,39),(23,39)])]
    for rgb,points in clusters:
        for x,y in points:out.putpixel((x,y),(*rgb,v1.getpixel((x,y))[3]))
    name='hospital_wall_back_straight_01_refresh_candidate_v2.png'
    out.save(P/name);out.resize((256,416),Image.Resampling.NEAREST).save(P/'candidate_8x.png')
    mask=Image.new('L',out.size)
    for y in range(52):
        for x in range(32):mask.putpixel((x,y),255 if out.getpixel((x,y))[:3]!=v1.getpixel((x,y))[:3] else 0)
    mask.save(P/'rgb_change_mask_vs_v1.png')
    report={'status':'reference_only_unapproved','v1_direction':'human_approved_direction_only','candidate':name,'dimensions':list(out.size),'mode':out.mode,'alpha_changed_vs_v1':sum(a[3]!=b[3] for a,b in zip(v1.get_flattened_data(),out.get_flattened_data())),'rgb_changed_vs_v1':sum(a[:3]!=b[:3] for a,b in zip(v1.get_flattened_data(),out.get_flattened_data())),'rgb_changed_vs_approved':sum(a[:3]!=b[:3] for a,b in zip(source.get_flattened_data(),out.get_flattened_data())),'source_sha256':digest(SRC),'v1_sha256':digest(V1),'candidate_sha256':digest(P/name),'anchor':'wall_center','footprint':[1,1],'offset':[-16,-52],'band_rows_half_open':{'cap':[0,8],'separator':[8,9],'face':[9,45],'base_separator':[45,46],'base':[46,51],'bottom':[51,52]},'face_base_rgb':base,'face_detail_rgb':[warm,cool],'detail_pixels':18,'edge_keepout_columns':6,'metrics':{}}
    sheet=Image.new('RGB',(1048,780),(24,35,49));draw=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
    for i,(label,im) in enumerate([('approved',source),('v1',v1),('v2',out)]):
        strip=Image.new('RGBA',(256,52))
        for j in range(8):strip.paste(im,(j*32,0))
        strip.save(P/f'run_8cell_{label}.png')
        draw.text((12,i*260+10),label+' / eight copies / exact 32px stride',font=font,fill='white')
        sheet.paste(strip.resize((1024,208),Image.Resampling.NEAREST),(12,i*260+38))
        seams=[]
        for boundary in range(32,256,32):
            edge=sum(abs(strip.getpixel((boundary-1,y))[c]-strip.getpixel((boundary,y))[c]) for y in range(52) for c in range(3))/(52*3)
            neighborhood=sum(abs(strip.getpixel((x,y))[c]-strip.getpixel((x+1,y))[c]) for x in [boundary-2,boundary-1,boundary] for y in range(52) for c in range(3))/(52*9)
            seams.append({'boundary_x':boundary,'edge_rgb_mae':round(edge,6),'neighborhood_rgb_mae':round(neighborhood,6)})
        bands={}
        for band,rows in [('face',range(9,45)),('base',range(46,51)),('cap',range(0,8))]:
            means=[sum(luminance(strip.getpixel((x,y))) for y in rows)/len(rows) for x in range(256)]
            amplitude=2*abs(sum(complex(math.cos(2*math.pi*x/32),-math.sin(2*math.pi*x/32))*v for x,v in enumerate(means)))/256
            rms=math.sqrt(sum((luminance(strip.getpixel((x,y)))-sum(luminance(strip.getpixel((z,y))) for z in range(256))/256)**2 for y in rows for x in range(256))/(len(rows)*256))
            bands[band]={'column_mean_luma_range':round(max(means)-min(means),8),'period_32_fourier_amplitude':round(amplitude,8),'horizontal_luma_rms':round(rms,8)}
        report['metrics'][label]={'each_boundary':seams,'bands':bands}
    sheet.save(P/'repeat_three_way.png')
    (P/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print({k:v for k,v in report.items() if k!='metrics'})
    print({k:v['bands'] for k,v in report['metrics'].items()})
if __name__=='__main__':build()
