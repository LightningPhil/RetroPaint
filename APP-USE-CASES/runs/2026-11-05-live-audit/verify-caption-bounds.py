"""Native numeric edits agree with accepted preview/placed bounds after LIVE-040."""
from pathlib import Path
from PIL import Image
import base64,hashlib,io,json,math
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def image(b):return Image.open(io.BytesIO(b)).convert('RGBA')
def actual(suffix,ext='retropaint',version=40):
 name=f'mouse-audit-caption{version}-bounds-{suffix}.{ext}';b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(suffix,version=40):return json.loads(actual(suffix,version=version))
e=json.loads((out/'caption-bounds40-evidence.json').read_bytes());assert len(e['cases'])==21
for c in e['cases']:
 size=c['id']=='textSize';minimum,maximum,fallback=(6,300,36) if size else (20,4096,360)
 try:value=float(c['typed']) if c['typed'] else fallback
 except ValueError:value=fallback
 accepted=min(maximum,max(minimum,value));accepted=accepted if size else math.floor(accepted+.5);assert float(c['committed']['value'])==accepted and c['committed']['valid'] and not c['committed']['stepMismatch']
 if c['typed'] not in ('','abc'):assert float(c['editing']['value'])==float(c['typed'])
assert next(c for c in e['cases'] if c['typed']=='36.5')['editing']['value']=='36.5' and e['selectionSize']=='20 × 40 px'
before=doc('before');placed=doc('placed');assert before==doc('before',39) and placed==doc('placed',39);complete=json.loads(json.dumps(before));complete['layers'][0]['image']=placed['layers'][0]['image'];assert complete==placed and doc('undone')==before and doc('redone')==placed==doc('reopened')
assert image(actual('placed','png')).tobytes()==image(actual('placed','png',39)).tobytes()==image(actual('reopened','png')).tobytes()
report={'status':'Pass','native_21_bound_fraction_blank_text_edits_match_preview_contract':True,'fractional_font_typing_and_caret_retained':True,'minimum_accepted_caption_pixels_unchanged_from_before_fix':True,'whole_undo_redo_native_project_png_reopen_exact':True,'sha256':hashes};(out/'caption-bounds40-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
