"""Native disabled controls, actual pointer capsule, merge and busy Undo history."""
import base64,hashlib,io,json,math
from pathlib import Path
from PIL import Image,ImageChops
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def retain(name):
 data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(stage):return json.loads(retain('mouse-audit-prereq-'+stage+'.retropaint'))
def image(layer):return Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',')[1]))).convert('RGBA')
blank=doc('blank')
assert doc('after-disabled-selection')==doc('after-disabled-merge')==doc('add-undone')==blank
added=doc('added-layer');assert doc('add-redone')==added and len(added['layers'])==2
assert added['layers'][0]==blank['layers'][0]
painted=doc('two-painted');assert painted['layers'][0]==blank['layers'][0]
assert len(painted['layers'])==2 and not painted['layers'][1].get('objects')
assert doc('merge-undone')==painted
merged=doc('merged');assert doc('merge-redone')==doc('clear-one-undo')==doc('final-restored')==merged
assert len(merged['layers'])==1
expected=Image.alpha_composite(image(painted['layers'][0]),image(painted['layers'][1]));actual=image(merged['layers'][0])
delta=ImageChops.difference(actual,expected)
assert max(hi for lo,hi in delta.getextrema())<=1
cleared=doc('clear-after-stale-undo');assert doc('clear-redone')==cleared and len(cleared['layers'])==1
assert image(cleared['layers'][0]).tobytes()==Image.new('RGBA',(960,640),'white').tobytes()
states={e['label']:e for e in json.loads((out/'prerequisite-dom-evidence.json').read_bytes())}
for key in ['copyDisabled','flipDisabled','rotateDisabled','redoDisabled']:assert states['no-selection'][key]
for key in ['copyDisabled','flipDisabled','rotateDisabled']:assert not states['selection-created'][key]
assert not states['add-layer-undone']['redoDisabled'] and not states['two-layers']['mergeDisabled'] and states['one-layer-restored']['mergeDisabled']
assert states['stale-undo-during-clear']['milliseconds']<1040
def fixed(stage):return json.loads(retain('mouse-audit-busy-undo-fixed-'+stage+'.retropaint'))
assert fixed('before')==fixed('one-undo')==fixed('final')==merged
assert fixed('cleared')==fixed('redone')
assert image(fixed('cleared')['layers'][0]).tobytes()==Image.new('RGBA',(960,640),'white').tobytes()
feedback=json.loads((out/'busy-undo-feedback-evidence.json').read_bytes())
assert feedback['text']=='Let the current effect finish first.' and feedback['visible'] and feedback['milliseconds']<1040
events=json.loads(retain('mouse-audit-fault-log (4).json'))
pointer=[e['detail'] for e in events if e['type']=='native pointer']
assert len(pointer)==2 and [e['phase'] for e in pointer]==['pointerdown','pointerup']
assert all(e['pointerType']=='mouse' and e['canvas']=={'width':960,'height':640} for e in pointer)
points=[((e['clientX']-e['rect']['x'])*960/e['rect']['width'],(e['clientY']-e['rect']['y'])*640/e['rect']['height']) for e in pointer]
(x0,y0),(x1,y1)=points;assert abs(y1-y0)<1e-8
stroke=image(painted['layers'][1]);bounds=stroke.getbbox();radius=11
for a,b in zip(bounds,[x0-radius,y0-radius,x1+radius,y1+radius]):assert abs(a-b)<1.1
outside=stroke.copy();outside.paste((0,0,0,0),(math.floor(x0-radius-1),math.floor(y0-radius-1),math.ceil(x1+radius+1),math.ceil(y0+radius+1)));assert outside.getbbox() is None
for y in range(math.floor(y0-radius-1),math.ceil(y0+radius+1)):
 for x in range(math.floor(x0-radius-1),math.ceil(x1+radius+1)):
  nearest=min(x1,max(x0,x+.5));distance=math.hypot(x+.5-nearest,y+.5-y0);pixel=stroke.getpixel((x,y))
  if distance<radius-1:assert pixel==(229,57,53,255)
  elif distance>radius+1:assert pixel[3]==0
report={'disabled_selection_and_merge_attempts_leave_whole_document_exact':True,
 'selection_layer_and_undo_prerequisites_enable_corresponding_actions':True,
 'native_pointer_metadata_independently_matches_22px_red_capsule':True,'pointer_paper_coordinates':points,'stroke_alpha_bounds':bounds,
 'merge_matches_independent_rgba_composition_within_1_premultiplied_level':True,
 'stale_undo_delivered_within_clear_animation_ms':states['stale-undo-during-clear']['milliseconds'],
 'stale_busy_click_adds_no_partial_edit_or_extra_undo_step':True,'one_later_undo_restores_exact_preclear_document':True,
 'fixed_native_busy_undo_explains_wait_without_changing_history':feedback,
 'sha256':hashes}
(out/'prerequisites-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
