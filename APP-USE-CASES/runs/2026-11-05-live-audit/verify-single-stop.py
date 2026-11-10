"""Native red failure versus Yellow repair; empty fallback and complete history."""
from pathlib import Path
from PIL import Image
import base64,copy,hashlib,io,json,numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';e=json.loads((out/'single47-evidence.json').read_bytes());hashes={}
def actual(name):
    b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(name):return json.loads(actual(name))
def pixels(d):return np.array(Image.open(io.BytesIO(base64.b64decode(d['layers'][0]['image'].split(',',1)[1]))).convert('RGBA'))
bad=doc('mouse-audit-conveyor46-one-Yellow.retropaint');assert list(pixels(bad)[620,390])==[229,57,53,255]
baseline=doc(e['files']['baseline']);empty=doc(e['files']['empty']);one=doc(e['files']['one']);yy,xx=np.indices((640,960))
for previous,current,start,end,rgb in [(baseline,empty,600,740,[229,57,53]),(empty,one,320,460,[253,216,53])]:
    scoped=copy.deepcopy(previous);scoped['layers'][0]['image']=current['layers'][0]['image'];assert scoped==current
    a,b=pixels(previous),pixels(current);distance=np.sqrt((xx-np.clip(xx,start,end))**2+(yy-620)**2);assert np.all(b[distance<=9]==rgb+[255]) and np.array_equal(a[distance>=13],b[distance>=13])
assert empty==doc(e['files']['undone']) and one==doc(e['files']['redone'])==doc(e['files']['reopened'])
assert e['emptyPreview']=='background: rgb(229, 57, 53);' and e['onePreview']=='background: rgb(253, 216, 53);'
assert e['oneSlots'][0]['background']=='rgb(253, 216, 53)' and all(s['index'] is None for s in e['oneSlots'][1:])
a=np.array(Image.open(io.BytesIO(actual('mouse-audit-conveyor47-one-fixed.png'))).convert('RGBA'));b=np.array(Image.open(io.BytesIO(actual('mouse-audit-conveyor47-one-reopened.png'))).convert('RGBA'));assert np.array_equal(a,b)
report={'status':'Pass','before_fix_Yellow_only_belt_painted_previous_Red':True,'after_fix_Yellow_only_belt_opaque_capsule_exact_Yellow':True,'empty_belt_keeps_defined_Red_fallback_and_matching_preview':True,'only_intended_Raster_capsules_change_all_nine_live_definitions_unchanged':True,'whole_project_Undo_Redo_and_native_reopen_exact':True,'native_controlled_PNG_reopen_RGBA_exact':True,'public_preview_styles_match_Yellow_or_empty_Red':True,'sha256':hashes}
(out/'single47-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
