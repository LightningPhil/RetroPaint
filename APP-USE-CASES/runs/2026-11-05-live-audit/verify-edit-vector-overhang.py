"""Verify preserved native off-paper vector definitions and returned appearance."""
from pathlib import Path
from PIL import Image
import hashlib,io,json,math
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def actual(suffix,ext='retropaint'):
 name=f'mouse-audit-edit-vector-overhang38-{suffix}.{ext}';b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(suffix):return json.loads(actual(suffix))
def image(b):return Image.open(io.BytesIO(b)).convert('RGBA')
def near(a,b):assert len(a)==len(b) and max(abs(x-y) for x,y in zip(a,b))<1e-9
before=doc('before');base_png=image(actual('before','png'));objects=before['layers'][0]['objects'];assert len(objects)==9 and {o['kind'] for o in objects}=={'path','stamp','text','raster'}
fixture=json.loads((out/'mouse-audit-vector-mixed-baseline.retropaint').read_bytes())
for i in (7,8):assert fixture['layers'][0]['objects'][i].pop('wet') is False
assert before==fixture
e=json.loads((out/'edit-vector-overhang38-evidence.json').read_bytes());assert len(e['cases'])==6 and {c['id'] for c in e['cases']}=={o['id'] for o in objects if o['kind']!='raster'};results=[]
for c in e['cases']:
 label=c['label'];i=next(i for i,o in enumerate(objects) if o['id']==c['id']);original=objects[i];outside=doc(label+'-outside');o=outside['layers'][0]['objects'][i];expected=json.loads(json.dumps(before));expected['layers'][0]['objects'][i]['matrix']=o['matrix'];assert outside==expected
 m=original['matrix'];near(o['matrix'],m[:4]+[m[4]-2000-c['x'],m[5]+200-c['y']]);corners=[(o['matrix'][0]*x+o['matrix'][2]*y+o['matrix'][4],o['matrix'][1]*x+o['matrix'][3]*y+o['matrix'][5]) for x,y in [(0,0),(o['width'],0),(o['width'],o['height']),(0,o['height'])]];assert max(x for x,y in corners)<0
 assert c['reselected']==original['id'] and 'whole vector is kept' in c['outsideStatus'] and 'whole shape kept' in c['outsideSize']
 assert image(actual(label+'-outside','png')).tobytes()!=base_png.tobytes()
 returned=doc(label+'-returned');r=returned['layers'][0]['objects'][i];near(r['matrix'],m);expected=json.loads(json.dumps(before));expected['layers'][0]['objects'][i]['matrix']=r['matrix'];assert returned==expected and image(actual(label+'-returned','png')).tobytes()==base_png.tobytes()
 assert doc(label+'-return-undone')==outside and doc(label+'-return-redone')==returned and doc(label+'-undone')==before
 results.append({'label':label,'kind':original['kind'],'off_paper_geometry_and_every_other_field_preserved':True,'piece_reselected_by_id':True,'return_translation_error_max':max(abs(a-b) for a,b in zip(r['matrix'],m)),'returned_PNG_RGBA_exact':True,'whole_undo_redo_exact':True})
assert doc('reopened')==doc('text-return-redone') and image(actual('reopened','png')).tobytes()==base_png.tobytes()
fixed_path=out/'edit-fractional39-verification.json';fixed=fixed_path.exists() and json.loads(fixed_path.read_bytes())['status']=='Pass'
report={'status':'Pass' if fixed else 'Partial','vector_geometry_matrix_status':'Pass','cases':results,'native_project_png_reopen_exact':True,'fractional_controls_live_fixed_build39_verified':fixed,'remaining':None if fixed else 'LIVE-039 fractional position field step validity fix still requires its live fixed-build retest.','sha256':hashes};(out/'edit-vector-overhang38-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
