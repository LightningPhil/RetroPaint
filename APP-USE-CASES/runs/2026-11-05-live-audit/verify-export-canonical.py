"""Preserve native export mismatch and failed first fix; verify corrected source snapshots."""
from pathlib import Path
from PIL import Image
import hashlib,io,json
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
e=json.loads((out/'export-canonical43-evidence.json').read_bytes());assert len(e['cases'])==12 and len(e['reopens'])==12
def actual(prefix,suffix,ext):
 name=f'mouse-audit-{prefix}-{suffix}.{ext}';b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def image(b):return np.array(Image.open(io.BytesIO(b)).convert('RGBA')).astype(int)
expected={'mix-skew-x20':(1,1),'mix-skew-both':(1,1),'mix-skew-x-minus20':(0,0),'patch-skew-x20':(4,2),'patch-skew-x-minus20':(2,2),'patch-skew-both':(3,2)}
results=[]
for c in e['cases']:
 label=c['scene']+'-'+c['label'];base=label.removesuffix('-pass2');p=json.loads(actual('export-canonical43',label+'-placed','retropaint'));reopened=json.loads(actual('export-canonical43',label+'-reopened','retropaint'));old=json.loads(actual('edit-whole42',base+'-placed','retropaint'));assert p==reopened==old
 a=image(actual('export-canonical43',label+'-placed','png'));b=image(actual('export-canonical43',label+'-reopened','png'));stats=(int(np.any(a!=b,axis=2).sum()),int(abs(a-b).max()));assert stats==((0,0) if label.endswith('-pass2') else expected[base]),(label,stats)
 results.append({'case':label,'different_pixels_after_reopen':stats[0],'max_channel_difference':stats[1],'whole_project_unchanged_from_original42_transform':True,'attempt':'two-readback correction' if label.endswith('-pass2') else 'failed first canonicalization attempt'})
report={'status':'Pass','original_42_and_first_43_attempt_mismatches_preserved':True,'six_corrected_native_exports_project_and_png_reopens_exact':True,'cases':results,'headless_limitation':'The isolated generated-block regression passes even before the fix in headless Chrome. Live production-browser downloads are the red/green proof. The first attempted synchronous/asynchronous JSON string comparison also failed due different PNG encodings; that harness assumption was corrected and retained reports are not product failures.','sha256':hashes}
(out/'export-canonical43-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
