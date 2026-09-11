"""One explicit alpha-only doorway candidate; no production metadata writes."""
from pathlib import Path
import hashlib,json
from PIL import Image

DEMO=Path(__file__).resolve().parent
ROOT=DEMO.parents[1]
OUT=DEMO/'repair_candidates/sliding_door_open_alpha_v1'
ID='hospital_sliding_clinical_doors_open_01'
BOUNDS=(7,14,59,48)  # Half-open; manually inspected jambs and threshold excluded.

def build():
    a=next(a for a in json.loads((ROOT/'metadata/manifest.json').read_text())['assets'] if a['id']==ID)
    original=ROOT/a['final_path']
    im=Image.open(original)
    assert im.mode=='RGBA' and im.size==(64,52)
    assert hashlib.sha256(original.read_bytes()).hexdigest()==a['normalized_sha256']
    OUT.mkdir(parents=True,exist_ok=True)
    mask=Image.new('L',im.size,0)
    result=im.copy()
    for y in range(BOUNDS[1],BOUNDS[3]):
        for x in range(BOUNDS[0],BOUNDS[2]):
            r,g,b,alpha=im.getpixel((x,y))
            assert alpha==255
            mask.putpixel((x,y),255)
            result.putpixel((x,y),(r,g,b,0))
    candidate=OUT/(ID+'_alpha_candidate.png')
    mask_path=OUT/'passage_alpha_mask.png'
    result.save(candidate)
    mask.save(mask_path)
    saved=Image.open(candidate)
    rgb_changed=sum(p[:3]!=q[:3] for p,q in zip(im.get_flattened_data(),saved.get_flattened_data()))
    alpha_changed=sum(p[3]!=q[3] for p,q in zip(im.get_flattened_data(),saved.get_flattened_data()))
    assert rgb_changed==0 and alpha_changed==1768
    report={'logical_id':ID,'status':'unapproved_repair_candidate','production_manifest_modified':False,
        'source_path':a['final_path'],'source_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),
        'candidate_path':candidate.relative_to(DEMO).as_posix(),'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),
        'mask_path':mask_path.relative_to(DEMO).as_posix(),'mask_sha256':hashlib.sha256(mask_path.read_bytes()).hexdigest(),
        'mask_encoding':'64x52 grayscale L; 255 changes alpha to 0; 0 preserves source RGBA',
        'bounds_half_open_native':list(BOUNDS),'native_canvas':[64,52],'logical_footprint':[2,1],'anchor':'wall_center',
        'demo_anchor':[608,336],'demo_image_offset':[-32,-52],
        'geometry_reference':a['validation_reference'],'source_scale':8,'source_crop':a['crop'],
        'documented_clear_passage_source':[416,112,864,416],'documented_clear_passage_native':[4,14,60,52],
        'refined_mask_source':[440,112,856,384],
        'refinement':'Direct native pixel inspection: x4..6 and x59 are inner jambs; row13 is header undersurface; rows48..51 are threshold. Only x7..58, y14..47 is recessed backing.',
        'boundary_samples_rgba':{str(pt):im.getpixel(pt) for pt in [(6,20),(7,20),(58,20),(59,20),(32,13),(32,14),(32,47),(32,48)]},
        'changed_alpha_pixels':alpha_changed,'changed_rgb_pixels':rgb_changed,'outside_mask_changed_pixels':0,
        'parked_leaves':[{'role':c['role'],'source_path':c['final_path'],'demo_path':'art/'+ID+'__'+c['role']+'.png','sha256':hashlib.sha256((ROOT/c['final_path']).read_bytes()).hexdigest(),'offset_from_main':c['anchor_relative_to_logical_native']} for c in a['components']]}
    (OUT/'repair.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'Candidate: {alpha_changed} alpha changes; {rgb_changed} RGB changes; mask {BOUNDS}')

if __name__=='__main__':build()
