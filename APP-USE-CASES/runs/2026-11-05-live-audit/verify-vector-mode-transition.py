"""Preserve original source pixels and objects across native drawing-mode changes."""
from pathlib import Path
from PIL import Image
import base64,hashlib,io,json,numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(n):
    name='mouse-audit-vector74-'+n+'.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
def image(url):return np.array(Image.open(io.BytesIO(base64.b64decode(url.split(',',1)[1]))).convert('RGBA'))
before=doc('raster');converted=doc('converted');heart=doc('heart');returned=doc('return-raster')
for d in [converted,heart,returned]:assert (d['width'],d['height'])==(960,640)
objects=converted['layers'][0]['objects'];assert len(objects)==1 and objects[0]['kind']=='raster'
assert np.array_equal(image(objects[0]['image']),image(before['layers'][0]['image']))
assert objects[0]['matrix']==[1,0,0,1,0,0]
assert len(heart['layers'][0]['objects'])==2 and heart['layers'][0]['objects'][0]==objects[0]
assert heart['layers'][0]['objects'][1]['kind']=='path'
assert returned['layers']==heart['layers'] and returned['drawingMode']=='raster'
report={'status':'Pass','original_pixels_exact':True,'original_addressable_raster_piece':True,'new_heart_separate_path':True,'dimensions_and_identity_unchanged':True,'return_Raster_keeps_all_pieces':True,'sha256':hashes};(out/'vector74-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native raster to Vectors to Raster with exact source pixels and separate geometry')

