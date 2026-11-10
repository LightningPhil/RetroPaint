"""Independent native Keep/Escape/Clear history and full rendered white frame."""
import base64,hashlib,io,json
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def retain(name):
 data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(stage):return json.loads(retain('mouse-audit-clear-'+stage+'.retropaint'))
def check_white(d):
 assert d['width']==960 and d['height']==640 and len(d['layers'])==1
 l=d['layers'][0];assert l['paper'] and l['visible'] and l['opacity']==1
 assert not l.get('objects') and not l.get('cad') and not l.get('photo') and all(not v for v in l['live'].values())
 im=Image.open(io.BytesIO(base64.b64decode(l['image'].split(',')[1]))).convert('RGBA')
 assert im.size==(960,640) and im.tobytes()==Image.new('RGBA',im.size,'white').tobytes()
baseline=doc('mix-baseline')
assert [l['name'] for l in baseline['layers']]==['Paper','Backdrop','Character','Caption']
assert baseline['layers'][2]['opacity']==.5 and baseline['layers'][2]['photo']['settings']['brightness']==12
assert len(baseline['layers'][3]['objects'])==1 and baseline['layers'][3]['objects'][0]['kind']=='stamp'
live=baseline['layers'][1]['live'];assert len(live['strokes'])==1 and len(live['fills'])==2
assert live['strokes'][0]['spec']['kind']=='conveyor' and all(f['spec']['texture']=='water' for f in live['fills'])
for stage in ['kept','escaped','undone','restored','restored-reopened','final-restored']:assert doc(stage)==baseline,stage
cleared=doc('cleared');check_white(cleared);assert doc('redone')==cleared
young=doc('young-before');assert doc('young-undone')==young
young_clear=doc('young-cleared');check_white(young_clear);assert doc('young-redone')==young_clear
timing=json.loads((out/'young-clear-dom-evidence.json').read_bytes())
assert timing['millisecondsSinceFirstStroke']<120000 and not timing['confirmationOpen']
png=Image.open(io.BytesIO(retain('mouse-audit-clear-visible-white.png'))).convert('RGBA')
assert png.size==(960,640) and png.tobytes()==Image.new('RGBA',png.size,'white').tobytes()
report={'keep_escape_preserve_whole_document_exact':True,'one_step_undo_restores_all_four_layers_exact':True,
 'live_water_conveyor_photo_recipe_stamp_and_half_opacity_retained':True,'redo_repeats_exact_clear':True,
 'new_picture_clear_has_no_confirmation_and_is_fully_undoable':True,'new_picture_clear_milliseconds':timing['millisecondsSinceFirstStroke'],
 'actual_rendered_clear_png_every_pixel_white':True,'whole_native_restored_project_reopen_exact':True,'sha256':hashes}
(out/'clear-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
