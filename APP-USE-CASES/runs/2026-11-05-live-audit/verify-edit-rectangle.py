"""Independent native rectangle crops, moves, alpha, history and reopen."""
import base64,hashlib,io,json,math
from datetime import datetime
from pathlib import Path
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def actual(name,ext='retropaint'):
 filename=name+'.'+ext;data=(downloads/filename).read_bytes();(out/filename).write_bytes(data);hashes[filename]=hashlib.sha256(data).hexdigest();return data
def doc(name):return json.loads(actual(name))
def image(data):return Image.open(io.BytesIO(data)).convert('RGBA')
def source(d):return image(base64.b64decode(d['layers'][0]['image'].split(',',1)[1]))
fixture=root/'test-results/audit-2026-11-05/fixtures/patch-labelled.png';original=image(fixture.read_bytes());assert original.size==(960,640)
provenance=json.loads((fixture.parent/'patch-labelled-provenance.json').read_bytes());assert hashlib.sha256(fixture.read_bytes()).hexdigest()==provenance['sha256'][fixture.name]
before=doc('mouse-audit-edit-rect37-before');assert source(before).tobytes()==original.tobytes() and image(actual('mouse-audit-edit-rect37-before','png')).tobytes()==original.tobytes()
assert before['drawingMode']=='raster' and not before['layers'][0].get('objects')
e=json.loads((out/'edit-rect37-evidence.json').read_bytes());assert len(e['cases'])==2 and e['zero']['redoBefore'] and e['zero']['redoAfter'] and not e['zero']['selectionVisible']
assert doc('mouse-audit-edit-rect37-zero')==before
native=[]
for line in (out.parent/'fault-controls/requests.jsonl').read_text(encoding='utf-8').splitlines():
 if 'native pointer' in line:
  row=json.loads(line)['event'];native.append((datetime.fromisoformat(row['at'].replace('Z','+00:00')).timestamp()*1000,row['detail']))
def gesture(action):
 events=[p for at,p in native if action['start']<=at<=action['end']]
 downs=[p for p in events if p['phase']=='pointerdown'];ups=[p for p in events if p['phase']=='pointerup'];assert len(downs)==len(ups)==1
 assert all(p['target']=='view' and p['pointerType']=='mouse' for p in downs+ups)
 def xy(p):return np.array([(p['clientX']-p['rect']['x'])/p['rect']['width']*960,(p['clientY']-p['rect']['y'])/p['rect']['height']*640])
 down,up=xy(downs[0]),xy(ups[0]);assert np.max(abs(down-action['from']))<.001 and np.max(abs(up-action['to']))<.001;return down,up
results=[]
for case in e['cases']:
 prefix=case['prefix'];clipped=case['kind']=='clipped';box=(0,0,150,130) if clipped else (95,95,205,185);destination=(200,200) if clipped else (245,195)
 down,up=gesture(case['select']);bounds=[max(0,math.floor(min(down[i],up[i]))) for i in range(2)]+[min([960,640][i],math.ceil(max(down[i],up[i]))) for i in range(2)];assert bounds==list(box)
 down,up=gesture(case['move']);assert tuple(np.rint(up-down).astype(int))==((200,200) if clipped else (150,100))
 crop=original.crop(box);copied=image((out/(prefix+'-copied.png')).read_bytes());assert copied.size==crop.size and copied.tobytes()==crop.tobytes()
 assert case['size']==f'{crop.width} × {crop.height} px'
 expected=original.copy();expected.paste((0,0,0,0),box);expected.alpha_composite(crop,destination)
 after=doc(prefix);assert source(after).tobytes()==expected.tobytes()
 expected_doc=json.loads(json.dumps(before));expected_doc['layers'][0]['image']=after['layers'][0]['image'];assert after==expected_doc
 assert doc(prefix+'-undone')==before and doc(prefix+'-redone')==after and doc(prefix+'-reopened')==after
 png=image(actual(prefix,'png'));assert png.tobytes()==expected.tobytes()==image(actual(prefix+'-reopened','png')).tobytes()
 assert source(after).getpixel((450,330))==(255,0,0,128),'Unrelated half-alpha patch changed'
 results.append({'kind':case['kind'],'selection_bounds':box,'destination':destination,'clipboard_and_full_result_rgba_exact':True,'whole_undo_redo_and_native_project_png_reopen_exact':True})
old=doc('mouse-audit-edit-rect36-clipped');old_copied=image((out/'mouse-audit-edit-rect36-clipped-copy.png').read_bytes());assert old_copied.tobytes()==original.crop((0,0,150,130)).tobytes()
expected=original.copy();expected.paste((0,0,0,0),(0,0,150,130));expected.alpha_composite(old_copied,(200,200));a=np.array(source(old));b=np.array(expected);yy,xx=np.nonzero(np.any(a!=b,axis=2));assert len(xx)==30 and set(xx)=={149} and set(yy)==set(range(100,130)) and all(tuple(a[y,x])==(255,0,0,1) for x,y in zip(xx,yy))
report={'status':'Pass','original_fixture_sha256':hashlib.sha256(fixture.read_bytes()).hexdigest(),'native_mouse_cases':results,'zero_area_no_selection_no_edit_redo_preserved':True,'before_fix_residual_red_pixels':30,'before_fix_residual_alpha':1,'fixed_results_all_source_pixels_exact':True,'sha256':hashes}
(out/'edit-rectangle37-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
