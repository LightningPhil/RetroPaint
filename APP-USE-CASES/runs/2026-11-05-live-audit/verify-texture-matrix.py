"""Independent native texture periods, animation masks, history and view checks."""
from pathlib import Path
from PIL import Image
import base64,copy,hashlib,io,json,numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';plan=json.loads((root/'test-results/audit-2026-11-05/fixtures/texture51/plan.json').read_bytes());hashes={}
def actual(label,ext='retropaint'):
    name='mouse-audit-texture52-'+label+'.'+ext;b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(label):return json.loads(actual(label))
def decode(url):return np.array(Image.open(io.BytesIO(base64.b64decode(url.split(',',1)[1]))).convert('RGBA'))
def pixels(d):return decode(d['layers'][0]['image'])
def png(label):return np.array(Image.open(io.BytesIO(actual(label,'png'))).convert('RGBA'))
before=doc('before');assert np.all(pixels(before)==255);final=doc('static-fill');a=png('all-12345');b=png('all-23456');results=[]
assert doc('last-fill-undone')==doc('water-fill');assert doc('last-fill-redone')==final==doc('view-restored');assert np.array_equal(a,png('zoomed-12345'))
colours={'brick':[(196,73,44),(163,59,36)],'dots':[(255,246,232),(239,71,111)],'weave':[(243,230,200),(196,138,74)],'grass':[(45,106,79),(149,213,178)],'stone':[(141,153,174),(43,45,66),(237,242,244)]}
for row in plan['rows']:
    y=row['paint_line'][0][1];period=row['period'];regions=[(slice(y-20,y+20),slice(150,300)),(slice(y-30,y+30),slice(550,800))]
    for ys,xs in regions:
        assert np.array_equal(a[ys,xs],a[ys,slice(xs.start+period,xs.stop+period)]),(row['name'],'period')
        if not row['animated']:assert np.array_equal(a[ys,xs],b[ys,xs])
        else:assert np.any(a[ys,xs]!=b[ys,xs])
    if row['name'] in colours:
        present=set(map(tuple,a[y-30:y+30,550:800,:3].reshape(-1,3)));assert set(colours[row['name']])<=present,row['name']
    results.append({'name':row['name'],'paint_and_fill_period_exact':period,'expected_animation':row['animated'],'named_structure':'Live screenshot plus declared base/structure RGB for fixed textures'})
fills=final['layers'][0]['live']['fills'];assert [f['spec']['texture'] for f in fills]==['water','static','water','static']
animated=np.zeros((640,960),bool)
for f in fills:animated|=decode(f['mask'])[:,:,3]>0
assert np.array_equal(a[~animated],b[~animated]);assert all(np.any(a[decode(f['mask'])[:,:,3]>0]!=b[decode(f['mask'])[:,:,3]>0]) for f in fills)
old=doc('outlines')
for row in plan['rows']:
    current=doc(row['name']+'-fill');previous=pixels(old);now=pixels(current);y=row['fill_seed'][1];area=np.zeros((640,960),bool);area[y-40:y+41,519:932]=True;assert np.array_equal(previous[~area],now[~area]),row['name'];assert current['layers'][0]['live']['fills'][:len(old['layers'][0]['live']['fills'])]==old['layers'][0]['live']['fills'];old=current
labelled=doc('labelled');label_png=png('labelled-12345');assert len(labelled['layers'][0]['live']['fills'])==0; # Retained pre-fix LIVE-050 reproduction.
assert np.array_equal(label_png[:,49:],a[:,49:]);assert np.any(label_png[:,:49]!=a[:,:49])
fixed=doc('recovered-labels');objects=fixed['layers'][0]['objects'];assert len(objects)==8
assert objects[0]['image']==final['layers'][0]['image'] and objects[0]['live']==final['layers'][0]['live']
assert doc('reopened-labels')==fixed
for clock,original in [(12345,a),(23456,b)]:
    labelled_frame=png('recovered-labels-'+str(clock));assert np.array_equal(labelled_frame[:,49:],original[:,49:]);assert np.any(labelled_frame[:,:49]!=original[:,:49])
reopened_png=doc('reopened-png');assert np.array_equal(pixels(reopened_png),png('recovered-labels-23456'))
assert doc('cropped-cancel')==final==doc('cropped-undone')
cropped=doc('cropped-label');assert doc('cropped-redone')==cropped
co=cropped['layers'][0]['objects'];assert len(co)==2 and co[0]['image']==final['layers'][0]['image'] and co[0]['live']==final['layers'][0]['live']
assert (co[1]['width'],co[1]['height'])==(28,9)
assert np.array_equal(png('cropped-label-23456')[:,49:],b[:,49:])
report={'status':'Pass','completed':results,'all_four_animation_masks_change_only_inside_their_masks':True,'previous_texture_definitions_and_outside_fill_regions_exact':True,'whole_Undo_Redo_and_zoom_invariance_exact':True,'pre_fix_labels_bake_live_ink_reproduced':True,'fixed_labels_retain_original_raster_and_live_definitions_exact':True,'fixed_label_frames_outside_labels_exact_at_both_clocks':True,'native_labelled_project_roundtrip_exact':True,'native_labelled_PNG_roundtrip_exact':True,'cropped_piece_cancel_undo_redo_exact':True,'remaining':[],'sha256':hashes};(out/'texture52-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Verified7paint+fillperiods, animation/history/zoom, fixed labels and project/PNG roundtrips and cropped-piece cancellation/history')
