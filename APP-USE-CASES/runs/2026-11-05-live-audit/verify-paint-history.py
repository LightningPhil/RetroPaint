"""Independent full-pixel checks of native strokes, drawer dismissal and Undo."""
import base64,hashlib,io,json
from pathlib import Path
from PIL import Image,ImageChops
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(stage):
 name='mouse-audit-history-'+stage+'.retropaint';data=(Path.home()/'Downloads'/name).read_bytes()
 (out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
def pixels(d):
 assert d['width']==960 and d['height']==640 and len(d['layers'])==1
 return Image.open(io.BytesIO(base64.b64decode(d['layers'][0]['image'].split(',')[1]))).convert('RGBA')
stages=['blank','blue','blue-red','three','undo-one','undo-two','redo-one','redo-two','after-toolbox-outside','continue-green','new-yellow-branch','yellow-undone','yellow-redone','reopened','after-all-tools','after-compact-tools','after-repeated-tools','after-help']
docs={s:doc(s) for s in stages};images={s:pixels(d) for s,d in docs.items()}
assert images['blank'].tobytes()==Image.new('RGBA',(960,640),'white').tobytes()
for a,b in [('undo-one','blue-red'),('undo-two','blue'),('redo-one','blue-red'),('redo-two','three'),('after-toolbox-outside','three'),('yellow-undone','blue-red'),('yellow-redone','new-yellow-branch'),('reopened','new-yellow-branch')]:assert docs[a]==docs[b],(a,b)
for name in ['after-all-tools','after-compact-tools','after-repeated-tools','after-help']:assert docs[name]==docs['reopened'],name
help_rows=json.loads((out/'help-layout-state-evidence.json').read_bytes())
assert len(help_rows)==12
for r in help_rows:
 assert r['tool']=='stamp' and r['size']=='2.6' and r['scrollHeight']<=r['clientHeight']+1
 assert r['left']>=-.5 and r['top']>=-.5 and r['right']<=r['width']+.5 and r['bottom']<=r['height']+.5
layouts=json.loads((out/'main-tool-layout-evidence.json').read_bytes())
for label in ['320x568','390x844-exact','844x390-exact']:
 rows=[r for r in layouts if r['layout']==label];assert len(rows)==11
 for r in rows:
  assert sum(e['pressed']=='true' for e in r['buttons'])==1
  assert next(e for e in r['buttons'] if e['tool']==r['tool'])['pressed']=='true'
  assert all(min(e['width'],e['height'])>=43.99 for e in r['buttons'])
repeated=json.loads((out/'repeated-tool-settings-evidence.json').read_bytes())
assert len(repeated)==11 and all(r['before']==r['after'] for r in repeated)
white=(255,255,255,255);blue=(30,136,229,255);red=(229,57,53,255);green=(67,160,71,255);yellow=(253,216,53,255)
for stage,colors in [('blue',[blue,white,white,white]),('blue-red',[blue,red,white,white]),('three',[blue,red,green,white]),('continue-green',[blue,red,green,green]),('new-yellow-branch',[blue,red,white,yellow])]:
 assert [images[stage].getpixel((280,y)) for y in [149,274,399,524]]==colors
deltas={}
for a,b,band in [('blank','blue',149),('blue','blue-red',274),('blue-red','three',399),('three','continue-green',524),('blue-red','new-yellow-branch',524)]:
 delta=ImageChops.difference(images[a].convert('RGB'),images[b].convert('RGB'));bbox=delta.getbbox();assert bbox
 assert 140<=bbox[0]<180 and 395<bbox[2]<=430 and band-16<=bbox[1]<=band and band<bbox[3]<=band+16,bbox
 outside=delta.copy();outside.paste((0,0,0),(140,band-16,430,band+16));assert not outside.getbbox()
 deltas[a+' -> '+b]=bbox
report={'separate_native_gestures_have_known_colour_and_bounded_changed_pixels':True,
 'each_undo_removes_one_whole_stroke_exactly':True,'each_redo_restores_whole_document_exactly':True,
 'toolbox_tabs_and_native_outside_click_leave_document_exact':True,
 'all_eleven_tools_plus_symmetry_reachable_at_three_exact_compact_breakpoints':True,
 'selected_tool_pressed_state_and_minimum_44px_targets_verified':True,
 'reopening_each_active_tool_preserves_all_exposed_settings':True,
 'all_help_categories_fit_four_layouts_preserving_stamp_size_and_picture':True,
 'continuing_after_drawer_uses_same_green_ink':True,'new_yellow_branch_does_not_restore_abandoned_green_strokes':True,
 'whole_native_reopen_exact':True,'delta_bounds_pixels':deltas,'sha256':hashes}
(out/'paint-history-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
