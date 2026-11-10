"""Real gear drops, accessible selection and scoped Space activation."""
import base64,hashlib,io,json
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
old=json.loads((out/'spiro-drop-before-fix.json').read_bytes());partial=json.loads((out/'spiro-drop-first-fix-still-fails.json').read_bytes());e=json.loads((out/'spiro-drop-fixed32.json').read_bytes())
assert next(g for g in old['before'] if 'picked' in g['class'])['gear']=='red'
assert old['after']['picked']==['orange'] and partial['events'][0]['result']['picked']==['orange']
assert any(g['pressed'] is None and 'picked' in g['class'] for g in old['before'])
assert [(r['label'],r['result']['picked'],r['result']['inner']) for r in e['events']]==[('off-paper',['red'],'36'),('paper-outside-ring',['red'],'36'),('valid-ring-centre',['orange'],'54')]
assert all(r['result']['ghostHidden'] for r in e['events'])
assert len(e['gearStates'])==6
for entry,gear,teeth in zip(e['gearStates'],['pink','purple','red','yellow','green','orange'],[24,30,36,42,48,54]):
 result=entry['result'];assert result['picked']==[gear] and int(result['inner'])==teeth
 for state in result['gearStates']:assert (state['pressed']=='true')==('picked' in state['class'])==(state['gear']==gear)
cancel=e['cancel'];assert cancel['interrupted']<cancel['released']-4000
assert cancel['during']['ghostHidden'] and cancel['during']['picked']==cancel['after']['picked']==['orange']
assert e['keyboardSpace']['picked']==['pink'] and e['keyboardEnter']['picked']==['orange']
assert e['keyboard32']['before']['picked']==['pink'] and e['keyboard32']['afterSpace']['picked']==['orange'] and e['keyboard32']['afterEnter']['picked']==['red']
pan=e['canvasSpace32'];assert pan['dragFinished']<pan['released']-4000
assert abs(pan['after']['paper']['x']-pan['before']['paper']['x']+50/1.1)<.001
assert abs(pan['after']['paper']['y']-pan['before']['paper']['y']-50/1.1)<.001
docs=[]
for label in ['before','after31','after32']:
 name='mouse-audit-spiro-no-paint-'+label
 for ext in ['retropaint','png']:
  data=(downloads/(name+'.'+ext)).read_bytes();(out/(name+'.'+ext)).write_bytes(data);hashes[name+'.'+ext]=hashlib.sha256(data).hexdigest()
  if ext=='retropaint':docs.append(json.loads(data))
  else:
   im=Image.open(io.BytesIO(data)).convert('RGBA');assert im.size==(960,640) and im.getextrema()==((255,255),)*4
assert docs[0]==docs[1]==docs[2]
source=Image.open(io.BytesIO(base64.b64decode(docs[0]['layers'][0]['image'].split(',',1)[1]))).convert('RGBA');assert source.getextrema()==((255,255),)*4
report={'status':'Pass','defects':['LIVE-030','LIVE-031','LIVE-032'],'native_invalid_drops_rejected_valid_drop_and_all_six_taps_work':True,'native_capture_loss_clears_ghost_before_held_mouse_release':True,'native_gear_pressed_states_match_all_six_choices':True,'native_button_space_and_enter_work_after_scoping_pan':True,'native_canvas_space_pan_still_works':True,'before_after31_after32_whole_project_and_blank_png_exact':True,'first_incomplete_drop_fix_retained':True,'sha256':hashes}
(out/'spiro-drop-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
