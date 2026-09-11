"""Single native RGB appearance prototype; only review previews are enlarged."""
from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent
ROOT=P.parents[3]
SOURCE=ROOT/'assets/architecture/hospital_wall_back_straight_01.png'
ID='hospital_wall_back_straight_01'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build():
    src=Image.open(SOURCE)
    assert src.size==(32,52) and src.mode=='RGBA'
    a=next(a for a in json.loads((ROOT/'metadata/manifest.json').read_text())['assets'] if a['id']==ID)
    assert digest(SOURCE)==a['normalized_sha256']
    out=src.copy()
    # These are actual source swatches, not a generated palette. Discrete 2px
    # clusters give quiet material variation and upper-left-biased relief.
    face_samples=[(8,10),(16,11),(16,17),(3,25),(16,28),(16,30),(8,40)]
    face=[src.getpixel(pt)[:3] for pt in face_samples]
    for y in range(52):
        for x in range(32):
            if 9<=y<45:
                offsets=[0,0,0,2,2,0,-2,0]
                level=max(0,min(6,(y-9+offsets[x//4])//6))
                # Sparse connected clusters, not dithering or per-pixel noise.
                if 4<=x<12 and 17<=y<21:level=max(0,level-1)
                if 20<=x<26 and 31<=y<35:level=min(6,level+1)
                rgb=face[level]
            elif y in (0,7,8,45,51):
                rgb=src.getpixel((8,y))[:3]
            else:
                # Preserve every cap/base row and highlight height. Interior
                # samples suppress the old vertical edge treatment.
                sample=8
                if x in range(4,12) or x in range(20,24):sample=12
                rgb=src.getpixel((sample,y))[:3]
            out.putpixel((x,y),(*rgb,src.getpixel((x,y))[3]))
    candidate=P/(ID+'_refresh_candidate.png')
    out.save(candidate)
    out.resize((256,416),Image.Resampling.NEAREST).save(P/'candidate_8x.png')
    mask=Image.new('L',src.size)
    diff=Image.new('RGB',src.size)
    changed=alpha=0
    for y in range(52):
        for x in range(32):
            before,after=src.getpixel((x,y)),out.getpixel((x,y))
            c=before[:3]!=after[:3];changed+=c;alpha+=before[3]!=after[3]
            mask.putpixel((x,y),255 if c else 0)
            diff.putpixel((x,y),tuple(abs(v-w) for v,w in zip(before[:3],after[:3])))
    mask.save(P/'rgb_change_mask.png');diff.save(P/'rgb_absolute_diff.png')
    def seam(im):
        # Boundary cost includes both interior-to-edge transitions: the original
        # has two similarly dark edges, so last-vs-first alone is misleading.
        return round(sum(abs(im.getpixel((x,y))[c]-im.getpixel((z,y))[c]) for x,z in [(30,31),(31,0),(0,1)] for y in range(52) for c in range(3))/(52*3*3),3)
    def repeat(im,n):
        strip=Image.new('RGBA',(32*n,52))
        for i in range(n):strip.paste(im,(32*i,0))
        assert strip.getchannel('A').getextrema()==(255,255)
        return strip
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
    sheet=Image.new('RGB',(1056,1440),(24,35,49));draw=ImageDraw.Draw(sheet)
    for row,n in enumerate([1,4,8]):
        y=row*480
        draw.text((12,y+8),f'{n} copies / exact 32px native stride / approved original',font=font,fill='white')
        draw.text((12,y+246),f'{n} copies / reference-only RGB prototype',font=font,fill='white')
        for im,dy in [(src,34),(out,272)]:
            strip=repeat(im,n)
            sheet.paste(strip.resize((32*n*4,208),Image.Resampling.NEAREST),(12,y+dy))
    sheet.save(P/'repeat_comparison.png')
    report={'id':ID,'status':'reference_only_unapproved','source_path':SOURCE.relative_to(ROOT).as_posix(),'source_sha256':digest(SOURCE),'candidate_path':candidate.name,'candidate_sha256':digest(candidate),'dimensions':list(out.size),'mode':out.mode,'alpha_changed_pixels':alpha,'rgb_changed_pixels':changed,'palette_colors':len(set(out.get_flattened_data())),'colors_all_sampled_from_source':set(out.get_flattened_data())<=set(src.get_flattened_data()),'anchor':a['anchor'],'logical_footprint':[a['footprint_width_tiles'],a['footprint_height_tiles']],'native_grid':32,'demo_image_offset':[-16,-52],'band_rows_half_open':{'cap':[0,8],'cap_face_separator':[8,9],'ivory_face':[9,45],'base_separator':[45,46],'teal_band':[46,51],'bottom_outline':[51,52]},'face_palette_samples':face_samples,'baseline':'bottom exclusive y52; demo wall anchor unchanged','repeat_counts':[1,4,8],'stride':32,'repeat_gaps':0,'repeat_overlaps':0,'opposite_edge_rgb_mismatched_rows':sum(out.getpixel((0,y))!=out.getpixel((31,y)) for y in range(52)),'boundary_neighborhood_mean_abs_rgb_delta':{'original':seam(src),'candidate':seam(out)},'no_metadata_or_production_writes':True}
    (P/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':build()
