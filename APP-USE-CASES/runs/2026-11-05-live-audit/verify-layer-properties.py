"""Check native rename/opacity mutations against complete saved documents."""
from pathlib import Path
from PIL import Image
import copy,hashlib,io,json,numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(n):
    name='mouse-audit-layer68-'+n+'.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
def only(d,index,key,value):
    expected=copy.deepcopy(d);expected['layers'][index][key]=value;return expected
before=doc('before');assert doc('renamed')==only(before,2,'name','Character renamed');assert doc('name-undone')==before
assert doc('blank-name')==only(before,2,'name','Layer')
long=doc('long-name');assert long==only(before,2,'name','Character long name long name long name long name long name')
zero=doc('opacity-zero');full=doc('opacity-full');half=doc('opacity-half')
assert zero==only(before,2,'opacity',0);assert full==only(before,2,'opacity',1);assert half==before
assert doc('opacity-undone')==full and doc('opacity-redone')==half
for name,expected in [('zero',[30,136,229,255]),('full',[255,0,0,255]),('half',[142,68,115,255])]:
    filename='mouse-audit-layer68-opacity-'+name+'.png';data=(Path.home()/'Downloads'/filename).read_bytes();(out/filename).write_bytes(data)
    a=np.array(Image.open(io.BytesIO(data)).convert('RGBA'));assert np.max(np.abs(a[120:160,120:180].astype(int)-expected))<=1
live=doc('live-before');assert len(live['layers'][1]['live']['fills'])==2
assert doc('live-zero')==only(live,1,'opacity',0);assert doc('live-full')==only(live,1,'opacity',1)
report={'status':'Pass','rename_blank_long_identity_and_Undo_exact':True,'opacity_all_other_document_data_exact':True,'half_composite_within1':True,'slider_gesture_Undo_Redo_exact':True,'live_definitions_exact':True,'sha256':hashes};(out/'layer68-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS rename/opacity, independent composition, live preservation and exact history')
