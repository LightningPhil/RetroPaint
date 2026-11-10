"""Native whole-document evidence for LIVE-044, beyond same pixels alone."""
from pathlib import Path
import copy,hashlib,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def doc(s):
 name='mouse-audit-project44-'+s+'.retropaint';b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return json.loads(b)
before=doc('unrelated-before');leaked=doc('mode-leaked');assert before['drawingMode']=='raster' and leaked['drawingMode']=='vector';expected=copy.deepcopy(before);expected['drawingMode']='vector';assert leaked==expected
assert before==doc('fixed-before')==doc('fixed-returned')==doc('fixed-returned-again');opened=doc('mixed-before');assert opened['drawingMode']=='vector' and opened==doc('fixed-opened')==doc('fixed-redone')
e=json.loads((out/'project44-fixed-evidence.json').read_bytes());assert e['modeProbe']=={'undo':'raster','redo':'vector'};assert all(r['mode']=='raster' and not r['vectorClass'] for r in e['retries'])
report={'status':'Pass','before_fix_all_pixels_layers_retained_but_drawingMode_leaked_Vector':True,'after_fix_whole_Raster_document_and_Vector_Redo_exact':True,'native_drawing_mode_control_matches_undo_redo':True,'first_corruption_attempts_preserved':'Before-fixproject44-evidence.jsonrecordsfirst4rejections. First rejection preservedRasterexact; aftervalidopenUndo onlymodeleaked. SubsequentrejectionsstillpreservedtheircurrentVectorstate, nottheoriginalRasterreference. Notreportedascorrupt-importpartialreplacement.','sha256':hashes};(out/'project44-mode-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
