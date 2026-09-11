from pathlib import Path
import json,sys,shutil,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from rastalr_pipeline import views
OUT=Path(__file__).parent
manifest=json.loads((ROOT/'metadata/manifest.json').read_text())
by_id={a['id']:a for a in manifest['assets']}
files={}; placements=[]
def copy(a, record=None, role='main'):
    r=record or a
    src=r['final_path'] if a['approval_status']=='approved' else r['normalized_path']
    assert src.startswith('assets/') or (a['id'].startswith('hospital_glass_partition_') and src.startswith('staging/pending/normalized/'))
    key=a['id']+'__'+role
    dest='art/'+key+'.png'
    (OUT/'art').mkdir(exist_ok=True)
    shutil.copyfile(ROOT/src,OUT/dest)
    files[key]={'logical_id':a['id'],'role':role,'source_path':src,'path':dest,'approval_status':a['approval_status'],'sha256':hashlib.sha256((ROOT/src).read_bytes()).hexdigest(),'native_size':list(Image.open(ROOT/src).size),'logical_footprint':[a['footprint_width_tiles'],a['footprint_height_tiles']],'anchor':a['anchor'],'reuse_scope':a['reuse_scope']}
    return key

def place(id,x,y,offset=None,collision=None,kind='prop',state='',view=None):
    a=by_id[id]
    if view:
        name,r,_=views.resolve(ROOT,a,**view)
        key=copy(a,r,name); offset=[r['render_origin'][0]-r['cell_anchor'][0],r['render_origin'][1]-r['cell_anchor'][1]]
        x+=r['cell_anchor'][0];y+=r['cell_anchor'][1]
    else:
        key=copy(a)
        if offset is None: offset=[-files[key]['native_size'][0]/2,-files[key]['native_size'][1]]
    p={'asset':key,'position':[x,y],'offset':offset,'kind':kind,'state':state,'collision':collision}
    placements.append(p)
    for c in a.get('components',[]):
        ck=copy(a,c,c['role']);co=c['anchor_relative_to_logical_native']
        placements.append({'asset':ck,'position':[x,y],'offset':[offset[0]+co[0],offset[1]+co[1]],'kind':kind,'state':state,'collision':None})

# Foundation placement follows Batch11 reconstruction: north 52px above floor,
# shallow sides outside floor; south carrier extends 20px inward from floor end.
for y in range(96,448,32):
 for x in range(32,800,32): place('hospital_floor_plain_01',x+16,y+16,[-16,-16],kind='floor')
for x in range(32,800,32):
 place('hospital_wall_back_straight_01',x+16,96,[-16,-52],[x,88,32,8],kind='wall')
 place('hospital_front_wall_cutaway_01',x+16,448,[-16,-20],[x,440,32,8],kind='wall')
for y in range(96,448,32):
 place('hospital_wall_side_left_01',32,y+16,[-20,-16],[24,y,8,32],kind='wall')
 place('hospital_wall_side_right_01',800,y+16,[0,-16],[800,y,8,32],kind='wall')
# Patient room divider, with one two-cell north-facing sliding module.
for x in [576,608,704,736,768]: place('hospital_wall_back_straight_01',x+16,336,[-16,-52],[x,328,32,8],kind='wall')
for y in range(96,320,32): place('hospital_wall_side_left_01',576,y+16,[-20,-16],[568,y,8,32],kind='wall')
for state in ['closed','open']:
 place('hospital_sliding_clinical_doors_'+state+'_01',672,336,[-32,-52],[644,328,56,8] if state=='closed' else None,kind='door',state=state)
# Fixed jamb contacts remain with both states.
for x in [640,700]:
 placements.append({'kind':'contact','position':[x,332],'collision':[x,328,4,8],'state':''})
# Glass back + independently authored sides, run alternatives replace each other.
for i in range(7): place('hospital_glass_partition_back_01',320+i*32,128,collision=[320+i*32,140,32,8],kind='glass',view={'index':i,'count':7})
for side,x in [('left',304),('right',528)]:
 for i in range(5):
  place('hospital_glass_partition_side_'+side+'_01',x,144+i*32,collision=[x+12,144+i*32,8,32],kind='glass',view={'index':i,'count':5,'back_corner':True})
  if i==0: placements[-1]['sort_y']=144 # North return before D1, as authored.
# South runs leave a 64px entrance; D4 owns corner trim. No invented junction.
for start,count in [(320,2),(448,3)]:
 for i in range(count):place('hospital_glass_partition_front_cutaway_01',start+i*32,288,collision=[start+i*32,300,32,8],kind='glass',view={'index':i,'count':count})
props=[
('reception_counter_small_01',144,224,52,24),('waiting_bench_2seat_01',112,320,48,24),('waiting_chair_01',208,320,28,20),('lobby_plant_01',80,160,22,18),('water_cooler_01',256,160,24,20),('brochure_rack_01',256,256,26,18),('hand_sanitizer_stand_01',288,352,16,14),('self_checkin_kiosk_01',80,240,24,20),
('examination_table_01',400,240,38,48),('doctor_stool_01',464,264,26,20),('examination_lamp_01',352,208,22,18),('exam_room_sink_unit_01',464,192,36,24),('exam_room_supply_cabinet_01',528,400,40,26),('patient_scale_01',352,272,22,20),
('hospital_bed_standard_01',672,224,36,52),('bedside_cabinet_01',736,192,28,22),('visitor_chair_patient_room_01',736,272,32,24),('iv_stand_single_01',624,192,20,16),('patient_room_wardrobe_01',768,144,38,26),('patient_room_waste_bin_01',608,272,24,18)]
for id,x,y,w,d in props:place(id,x,y,collision=[x-w/2,y-d,w,d])
(OUT/'runtime_manifest.json').write_text(json.dumps({'baseline':'9a95eba055324f87a7f62ffcda859e1949b207eb','inventory':{'manifest':224,'approved':220,'needs_human_review':4},'grid':32,'files':files,'placements':placements},indent=2)+'\n')
print(f'{len(files)} PNG files; {len(props)} prop types; {len(placements)} placements')
