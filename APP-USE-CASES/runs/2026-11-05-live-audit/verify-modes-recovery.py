"""Independent native Basic/Advanced artwork and repeated-resume byte oracles."""
import base64,copy,hashlib,io,json
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(stem):
 name='mouse-audit-'+stem+'.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data)
 hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
before=doc('mode-advanced-before');basic=doc('mode-basic-before-paint');raster=doc('mode-basic-raster')
assert before==basic==doc('mode-basic-undone')
assert raster==doc('mode-basic-redone')
assert raster['drawingMode']==before['drawingMode']=='vector'
assert before['active']==raster['active']==104 and before['layers'][:3]==raster['layers'][:3]
a,b=before['layers'][3],raster['layers'][3]
assert a['image']==b['image'] and a['live']==b['live'] and a['objects']==b['objects'][:-1]
piece=b['objects'][-1];assert piece['kind']=='raster' and piece['opacity']==1
assert piece['matrix']==[1,0,0,1,648,450] and piece['width']==223 and piece['height']==23
im=Image.open(io.BytesIO(base64.b64decode(piece['image'].split(',')[1]))).convert('RGBA')
assert im.size==(223,23) and im.getpixel((111,11))==(30,136,229,255) and im.getpixel((0,0))[3]==0
normalized=copy.deepcopy(raster)
assert normalized['layers'][3]['objects'][-1].pop('wet') is False
for stem in ['resume-before-first-reload','resume-before-first-restored','resume-fixed-original','resume-fixed-cycle-1','resume-fixed-cycle-2','resume-fixed-cycle-3','mode-advanced-fixed-restored']:assert doc(stem)==normalized,stem
events=json.loads((out/'resume-native-evidence.json').read_bytes())
assert next(e for e in events if e['label']=='before-fix-original-draft-settled')['text']=='Draft saved'
assert not next(e for e in events if e['label']=='before-fix-second-reload')['resumeVisible']
for cycle,advanced in [(1,False),(2,False),(3,True)]:
 e=next(e for e in events if e['label']=='after-fix-native-resume-cycle-'+str(cycle))
 assert e['advanced']==advanced and e['vectorClass']==advanced and e['status']=='Draft restored'
red=json.loads((out.parent/'resume-reload-before-corrected-setup/report.json').read_bytes())['recovery_resume']
green=json.loads((out.parent/'resume-reload-after-current-guard/report.json').read_bytes())['recovery_resume']
assert red['status']=='Fail' and red['cycles']==1 and green['status']=='Pass' and green['cycles']==3 and not green['errors']
report={'basic_advanced_switch_preserves_whole_document':True,
 'basic_creates_actual_raster_piece_despite_saved_vector_preference':True,'new_stroke_undo_redo_exact':True,
 'all_existing_photo_live_and_stamp_content_exact':True,'both_modes_remembered_across_native_reload':True,
 'native_three_untouched_resume_cycles_whole_document_exact_after_initial_file_open':True,'targeted_regression_red_one_cycle_green_three_cycles':True,
 'initial_native_file_open_normalization':'Optional raster wet:false is omitted by reader; all other metadata and pixels exact. Subsequent recovery cycles compare whole JSON without normalization.',
 'diagnostic':'Early Basic reload before the three-second draft debounce recovered older snapshot; retained as diagnostic, not credited as a successful round trip. Native settled-before-fix repeated resume separately reproduces LIVE-022.',
 'sha256':hashes}
(out/'modes-recovery-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
