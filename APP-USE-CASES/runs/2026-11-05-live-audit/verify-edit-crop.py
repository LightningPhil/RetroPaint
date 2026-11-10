"""Independent crop of every layer and translation of retained object geometry."""
from pathlib import Path
from PIL import Image
import base64,hashlib,io,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def image(b):return Image.open(io.BytesIO(b)).convert('RGBA')
def decode(s):return image(base64.b64decode(s.split(',',1)[1]))
def actual(suffix,ext='retropaint'):
 name=f'mouse-audit-edit-crop39-{suffix}.{ext}';b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(suffix):return json.loads(actual(suffix))
before=doc('before');assert (before['width'],before['height'])==(960,640) and len(before['layers'])==4 and before['active']==103 and before['drawingMode']=='raster';assert doc('no-selection')==before
after=doc('cropped');assert (after['width'],after['height'])==(200,100);expected=json.loads(json.dumps(before));expected['width']=200;expected['height']=100
for i,old in enumerate(before['layers']):
 new=after['layers'][i];assert decode(new['image']).tobytes()==decode(old['image']).crop((90,90,290,190)).tobytes();expected['layers'][i]['image']=new['image']
 for j,obj in enumerate(old.get('objects',[])):
  matrix=obj['matrix'][:4]+[obj['matrix'][4]-90,obj['matrix'][5]-90];assert new['objects'][j]['matrix']==matrix;expected['layers'][i]['objects'][j]['matrix']=matrix
assert after==expected and doc('undone')==before and doc('redone')==after and doc('reopened')==after
expected_png=image(actual('before','png')).crop((90,90,290,190));assert image(actual('cropped','png')).tobytes()==image(actual('reopened','png')).tobytes()==expected_png.tobytes()
e=json.loads((out/'edit-crop39-evidence.json').read_bytes());assert e['missingSelectionCropEnabled'] and e['missingSelectionStatus']=='Select the part of the picture to keep first.' and e['size']=='200 × 100 px' and e['dimensions']=='200 × 100 pixels · 4 layers'
patch_before=doc('patch-before');patch_src=image((out.parent/'fixtures/patch-labelled.png').read_bytes());assert decode(patch_before['layers'][0]['image']).tobytes()==patch_src.tobytes();patch_after=doc('patch-cropped');patch_expected=json.loads(json.dumps(patch_before));patch_expected['width']=200;patch_expected['height']=100;patch_expected['layers'][0]['image']=patch_after['layers'][0]['image'];assert patch_after==patch_expected
patch_pixels=patch_src.crop((90,90,290,190));assert decode(patch_after['layers'][0]['image']).tobytes()==patch_pixels.tobytes()==image(actual('patch-cropped','png')).tobytes()==image(actual('patch-reopened','png')).tobytes();assert doc('patch-undone')==patch_before and doc('patch-redone')==patch_after==doc('patch-reopened');assert e['patchSize']=='200 × 100 px' and e['patchDimensions']=='200 × 100 pixels · 1 layer'
report={'status':'Pass','prescribed_PATCH_main_flow_RGBA_exact':True,'all_four_layer_crops_RGBA_exact':True,'retained_stamp_geometry_translates_to_new_origin_without_clipping':True,'known_200x100_export_exact':True,'missing_selection_rejected_without_document_change':True,'whole_undo_redo_native_project_png_reopen_exact':True,'sha256':hashes};(out/'edit-crop39-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
