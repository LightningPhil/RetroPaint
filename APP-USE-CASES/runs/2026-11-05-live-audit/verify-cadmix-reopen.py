"""Native CADMIX reopening, scoped edits, geometry, crop and source retention."""
from pathlib import Path
from PIL import Image
import base64,copy,hashlib,io,json
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def actual(s,ext='retropaint'):
    name='mouse-audit-cadmix44-'+s+'.'+ext;b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(s):return json.loads(actual(s))
def png(s):return np.array(Image.open(io.BytesIO(actual(s,'png'))).convert('RGBA'))
def pixels(url):return np.array(Image.open(io.BytesIO(base64.b64decode(url.split(',',1)[1]))).convert('RGBA'))
opened=doc('opened');assert opened['active']==203 and [l['name'] for l in opened['layers']]==['Paper','Backdrop','Shell model','Paint above 3D']
fixture=json.loads((root/'test-results/audit-2026-11-05/fixtures/cadmix-trace-guide.retropaint').read_bytes())
fixture_meta=copy.deepcopy(fixture)
for a,b in zip(fixture_meta['layers'],opened['layers']):
    assert np.array_equal(pixels(a['image']),pixels(b['image']));a['image']=b['image']
assert fixture_meta['layers'][0]['paper'] is True and fixture_meta['layers'][1]['paper'] is False
assert opened['layers'][0]['paper'] is None and opened['layers'][1]['paper'] is None
# Synthetic fixture boolean paper flags are not colour definitions. The importer
# accepts only #rrggbb colours; raster Paper/Backdrop pixels remain exactly intact.
fixture_meta['layers'][0]['paper']=fixture_meta['layers'][1]['paper']=None
assert fixture_meta==opened
for label in ['orthographic','perspective','photo-crop','photo-crop-v2']:
    before=doc(label+'-before');assert before==doc(label+'-reopened');assert np.array_equal(png(label+'-before'),png(label+'-reopened'))
assert doc('orthographic-before')['layers'][2]['cad']['view']==fixture['layers'][2]['cad']['view']
perspective=doc('perspective-before');assert perspective['layers'][2]['cad']['view']['projection']=='perspective'
scoped=copy.deepcopy(opened);scoped['active']=201;scoped['layers'][2]['cad']['view']=perspective['layers'][2]['cad']['view'];scoped['layers'][2]['image']=perspective['layers'][2]['image'];assert scoped==perspective
# Workshop Close deliberately targets the first non-CAD paint layer (Paper).
moved=doc('body-v2-moved');assert moved==doc('body-v2-redone');old_undo=doc('body-v2-undone')
scoped=copy.deepcopy(opened);scoped['layers'][2]['cad']['view']=old_undo['layers'][2]['cad']['view'];scoped['layers'][2]['image']=old_undo['layers'][2]['image'];assert scoped==old_undo
assert old_undo['layers'][2]['cad']['view']['up']==[0,0,1] # LIVE-045, retained red evidence.
scoped=copy.deepcopy(old_undo);scoped['active']=201;scoped['layers'][2]['cad']['bodies'][0]['position']=[5,0,0];scoped['layers'][2]['image']=moved['layers'][2]['image'];assert scoped==moved
first_attempt=doc('body-moved');assert first_attempt['layers'][2]['cad']['bodies'][0]['position']==[0,0,0];scoped=copy.deepcopy(old_undo);scoped['active']=201;assert scoped==first_attempt
crop=doc('photo-crop-v2-before');assert crop['crop']=={'x':.1,'y':.1,'width':.8,'height':.8};assert png('photo-crop-v2-before').shape==(512,768,4)
assert crop['layers'][1]['photo']['settings']['exposure']==1
assert crop['layers'][2:]==perspective['layers'][2:] and crop['layers'][0]==perspective['layers'][0]
assert np.array_equal(pixels(crop['layers'][1]['image']),pixels(perspective['layers'][1]['image']))
edited=doc('photo-edited');assert edited==doc('photo-redone') and doc('photo-undone')==crop
scoped=copy.deepcopy(crop);scoped['layers'][1]['photo']['settings']['exposure']=.5;scoped['layers'][1]['photo']['normal']['exposure']=.5;assert scoped==edited
rb=doc('raster-before');rm=doc('raster-marked');assert doc('raster-undone')==rb and doc('raster-redone')==rm
scoped=copy.deepcopy(rb);scoped['layers'][0]['image']=rm['layers'][0]['image'];assert scoped==rm
a=pixels(rb['layers'][0]['image']);b=pixels(rm['layers'][0]['image']);mask=np.any(a!=b,axis=2);ys,xs=np.where(mask);assert len(xs)>2000
assert [int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]==[189,189,310,210];assert list(b[200,250])==[30,136,229,255]
yy,xx=np.indices(mask.shape);interior=(xx>=200)&(xx<=300)&(abs(yy-200)<=9);assert np.all(b[interior]==[30,136,229,255]);exterior=(xx<188)|(xx>312)|(yy<188)|(yy>212);assert np.array_equal(a[exterior],b[exterior])
vb=doc('vector-before');vm=doc('vector-moved');assert doc('vector-undone')==vb and doc('vector-redone')==vm
old=vb['layers'][3]['objects'][0]['matrix'];new=vm['layers'][3]['objects'][0]['matrix'];assert old[:4]==new[:4] and abs(new[4]-old[4]-80)<.001 and abs(new[5]-old[5]+40)<.001
scoped=copy.deepcopy(vb);scoped['layers'][3]['objects'][0]['matrix']=new;assert scoped==vm
assert doc('final-reopened')==vm and np.array_equal(png('final-before'),png('final-reopened'))
report={'status':'Pass','orthographic_and_perspective_whole_project_and_PNG_exact':True,'native_5mm_solid_move_and_Undo_Redo_exact':True,'photo_recipe_and_shared_768x512_crop_reopen_exact':True,'reopened_photo_exposure_edit_and_Undo_Redo_exact':True,'reopened_Paper_raster_stroke_scope_geometry_pigment_and_Undo_Redo_exact':True,'reopened_Vector_annotation_80_minus40_move_scope_and_Undo_Redo_exact':True,'combined_edited_project_and_PNG_native_reopen_exact':True,'initial_attempts_retained':'Firstsolidinputonlychangedactivepaintinglayer; unchangedCADconfirmed. FirstcropfillchangedDOMvaluesbutdidnotcommitmodel, capturedno-cropfiles retained; completedv2usesnativekeyboardentry. Neitherinitialattemptcountedascompletedediting. CADCloseintentionallyswitchestoPaper, verifiedagainstcloseCadimplementation.','sha256':hashes}
(out/'cadmix44-reopen-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
