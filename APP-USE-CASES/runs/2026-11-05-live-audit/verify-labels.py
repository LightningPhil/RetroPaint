"""Independent editable-label history, native-input and rendered-pixel oracles."""
import copy,hashlib,io,json,math
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def retain(name):
 data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(stage):return json.loads(retain('mouse-audit-label-r2-'+stage+'.retropaint'))
def objects(d):return d['layers'][-1].get('objects',[])
def obj(stage):return objects(doc(stage))[1]
def world(o,p):
 m=o['matrix'];return[m[0]*p['x']+m[2]*p['y']+m[4],m[1]*p['x']+m[3]*p['y']+m[5]]
def tip(o):return world(o,o['callout']['tip'])
def near(a,b,tol=.00001):assert max(abs(x-y) for x,y in zip(a,b))<tol,(a,b)
def without(o,*keys):return{k:v for k,v in o.items() if k not in keys}
before=doc('before');assert doc('blank')==doc('cancelled')==before
long=doc('raster-long');assert len(long['layers'])==3 and long['layers'][:2]==before['layers']
assert long['layers'][-1]['name']=='Annotations' and len(objects(long))==1
a=objects(long)[0]
text='A long wrapping label identifies this castle and its rounded towers.\nSupercalifragilisticexpialidocious demonstrates word splitting.'
assert a['kind']=='text' and a['callout']['text']==text and a['callout']['wrapWidth']==180
assert a['font']=='18px "Courier New"' and a['size']==18 and len(a['lines'])==11
assert ''.join(''.join(x['text'].split()) for x in a['lines'])==''.join(text.split())
# Courier New has constant1229/2048-em advance; verify actual glyph layout
# independently of the application's Canvas measureText calls.
for j,line in enumerate(a['lines']):
 near([line['width']],[len(line['text'])*18*1229/2048]);assert line['width']<=172
 near([line['y']],[12+j*18*1.35]);assert line['x']==12
near([a['width']],[max(x['width'] for x in a['lines'])+24]);assert a['height']==291
assert doc('raster-undone')==before and doc('raster-redone')==long
styled=doc('vector-styled');assert len(styled['layers'])==3 and len(objects(styled))==2
assert objects(styled)[0]==a and styled['layers'][:2]==before['layers']
b=objects(styled)[1]
assert b['kind']=='text' and b['font']=='italic bold 25px "Georgia"'
assert b['color']=='#112233' and b['paper']=='#dcf0fa' and b['underline'] and b['strike'] and b['align']=='right'
assert b['callout']['text']=='Vector label' and b['callout']['wrapWidth']==240
assert b['callout']['border'] is False and b['callout']['rounded'] is False
vector_before=copy.deepcopy(long);vector_before['drawingMode']='vector'
assert doc('vector-undone')==vector_before and doc('vector-redone')==styled
assert doc('edit-cancelled')==styled
edited=doc('edited');c=objects(edited)[1]
assert c['id']==b['id'] and c['matrix']==b['matrix'] and c['callout']['tip']==b['callout']['tip']
assert c['callout']['text']=='Edited vector label' and c['callout']['wrapWidth']==150 and c['size']==21
assert c['callout']['border'] and c['callout']['rounded'] and c['align']=='center'
assert doc('edit-undone')==styled and doc('edit-redone')==edited
stages=['box-moved','tip-left','tip-top','tip-right','tip-bottom','tip-top-left','tip-top-right','tip-bottom-right','tip-bottom-left','tip-outside','zoom-tip-moved','rotated-box-moved']
rows=[json.loads(line) for line in (out.parent/'fault-controls/requests.jsonl').read_text().splitlines()]
events=[row['event'] for row in rows if row.get('event',{}).get('type')=='native pointer' and '2026-11-05T19:43:38'<=row['event'].get('at','')<'2026-11-05T19:48:18']
assert len(events)==24
(out/'label-native-pointer-evidence.json').write_text(json.dumps(events,indent=2)+'\n')
def paper(e):
 d=e['detail'];r=d['rect'];return[(d['clientX']-r['x'])*d['canvas']['width']/r['width'],(d['clientY']-r['y'])*d['canvas']['height']/r['height']]
prior=c;pointer_checks=[]
for j,stage in enumerate(stages):
 if stage=='zoom-tip-moved':prior=obj('zoom-before')
 if stage=='rotated-box-moved':prior=obj('rotated')
 current=obj(stage);down,up=events[j*2:j*2+2]
 assert down['detail']['phase']=='pointerdown' and up['detail']['phase']=='pointerup'
 p,q=paper(down),paper(up);delta=[y-x for x,y in zip(p,q)]
 assert current['id']==prior['id']
 if stage in ['box-moved','rotated-box-moved']:
  near(tip(current),tip(prior));near(current['matrix'][4:],[prior['matrix'][4]+delta[0],prior['matrix'][5]+delta[1]])
  assert current['matrix'][:4]==prior['matrix'][:4]
 else:
  assert current['matrix']==prior['matrix'];near(tip(current),[x+y for x,y in zip(tip(prior),delta)])
  assert without(current['callout'],'tip')==without(prior['callout'],'tip')
 assert without(current,'matrix','callout')==without(prior,'matrix','callout')
 pointer_checks.append({'stage':stage,'paper_delta':delta,'tip_mm_or_px':tip(current)})
 prior=current
assert tip(obj('tip-outside'))[0]<0
assert doc('zoom-before')==doc('tip-bottom-left')==doc('zoom-undone')
assert doc('zoom-redone')==doc('zoom-tip-moved')
resized=doc('resized');d=objects(resized)[1]
assert without(d,'matrix')==without(obj('zoom-tip-moved'),'matrix')
assert abs(d['matrix'][0]-d['matrix'][3])<.00001
near([d['matrix'][0]*(d['callout']['tip']['x']+10)],[300],.02)
assert doc('resize-undone')==doc('zoom-tip-moved') and doc('resize-redone')==resized
rotated=doc('rotated');e=objects(rotated)[1];assert without(e,'matrix')==without(d,'matrix')
near(e['matrix'][:4],[d['matrix'][0]*math.cos(math.pi/6),d['matrix'][0]*.5,-d['matrix'][3]*.5,d['matrix'][3]*math.cos(math.pi/6)])
assert doc('rotate-undone')==resized and doc('rotate-redone')==rotated
assert doc('rotated-box-undone')==rotated and doc('rotated-box-redone')==doc('rotated-box-moved')
dup=doc('duplicated');prev=doc('rotated-box-moved');assert objects(dup)[:2]==objects(prev)
f=objects(dup)[2];original=objects(dup)[1];assert f['id']!=original['id']
assert without(f,'id','matrix')==without(original,'id','matrix')
near(f['matrix'][:4],original['matrix'][:4]);near(f['matrix'][4:],[x+20 for x in original['matrix'][4:]])
dup_edit=doc('duplicate-edited');assert objects(dup_edit)[:2]==objects(dup)[:2]
assert objects(dup_edit)[2]['callout']['text']=='Independent duplicate' and objects(dup_edit)[2]['size']==19
# Earlier native CtrlV delivered stale OS text; those attempted-paste files
# are diagnostic only. The app's explicit Paste action is the credited path.
pasted=doc('button-pasted');assert len(objects(pasted))==4
assert objects(pasted)[:3]==objects(dup_edit)
g,h=objects(pasted)[2:];assert g['id']!=h['id'] and without(g,'id','matrix')==without(h,'id','matrix')
near(h['matrix'][:4],g['matrix'][:4]);near(h['matrix'][4:],[x+20 for x in g['matrix'][4:]])
assert doc('button-paste-undone')==dup_edit and doc('button-paste-redone')==pasted
final=doc('pasted-edited');assert objects(final)[:3]==objects(pasted)[:3]
assert objects(final)[3]['callout']['text']=='Independent pasted label'
assert doc('reopened')==final
assert doc('vector-blank')==doc('vector-cancelled')==doc('vector-long-undone')
vl=doc('vector-long');assert len(objects(vl))==5 and len(vl['layers'])==3
assert objects(vl)[:4]==objects(final)
v=objects(vl)[4]
for key in ['kind','font','size','lines','width','height','align']:assert v[key]==a[key]
assert v['callout']['text']==text and v['callout']['wrapWidth']==180
assert doc('vector-long-redone')==vl
keyboard=doc('browser-key-pasted');assert len(objects(keyboard))==5 and objects(keyboard)[:4]==objects(final)
old,new=objects(keyboard)[3:];assert old['id']!=new['id']
assert without(old,'id','matrix')==without(new,'id','matrix')
near(new['matrix'][:4],old['matrix'][:4]);near(new['matrix'][4:],[x+20 for x in old['matrix'][4:]])
assert doc('browser-key-undone')==doc('vector-blank') and doc('browser-key-redone')==keyboard
key_evidence=json.loads((out/'label-browser-key-paste-evidence.json').read_bytes())
assert len(key_evidence['pieceOptions'])==6 and '"types":["text/plain","Files"]' in key_evidence['trace']
assert '"ownMarker":"RetroPaint editable pieces ' in key_evidence['trace']
for stage in stages+['vector-styled','edited','resized','rotated','duplicated','duplicate-edited','button-pasted','pasted-edited','reopened']:
 d=doc(stage);assert d['layers'][:2]==before['layers'] and objects(d)[0]==a
pixel_checks=[]
for edge in ['left','top','right','bottom','top-left','top-right','bottom-right','bottom-left']:
 stage='tip-'+edge;o=obj(stage);w,h=o['width'],o['height'];p=o['callout']['tip'];tx,ty=p['x'],p['y']
 # Closest point on the rounded rectangle: project onto its straight edge,
 # or radially onto the radius8 corner when outside both adjacent sides.
 x,y=max(0,min(w,tx)),max(0,min(h,ty));r=8
 if (x<r or x>w-r) and (y<r or y>h-r):
  cx=r if x<r else w-r;cy=r if y<r else h-r;length=math.hypot(tx-cx,ty-cy);x=cx+r*(tx-cx)/length;y=cy+r*(ty-cy)/length
 image=Image.open(io.BytesIO(retain('mouse-audit-label-r2-'+stage+'.png'))).convert('RGBA');assert image.size==(960,640)
 samples=[]
 for f in [.12,.25,.5,.75,.88]:
  q=world(o,{'x':x+(tx-x)*f,'y':y+(ty-y)*f});ix,iy=map(round,q)
  values=[image.getpixel((xx,yy)) for xx in range(ix-1,ix+2) for yy in range(iy-1,iy+2)]
  assert any(max(v[:3])<100 and v[3]==255 for v in values),(edge,q,values)
  samples.append(q)
 bx,by=world(o,{'x':8,'y':h/2});assert image.getpixel((round(bx),round(by)))==(220,240,250,255)
 pixel_checks.append({'edge':edge,'independent_attachment_local':[x,y],'five_actual_arrow_pixel_probes':samples})
route=json.loads((out/'label-cad-route-evidence.json').read_bytes());assert route['workshop'] and route['textInert'] and route['textAbsentFromAccessibility']
assert 'Painting on Paper.' in route['returnHint'] and 'Annotations' in route['explicitAnnotationHint']
result={'blank_cancel_and_edit_cancel_leave_document_exact':True,'raster_and_vector_preferences_create_editable_labels':True,'courier_glyph_advance_wrapping_and_autosize_verified':True,'new_annotation_sheet_removed_in_one_undo_existing_sheet_reused':True,'styles_identity_transforms_neighbours_and_history_exact':True,'native_pointer_coordinate_checks':pointer_checks,'all_eight_rendered_arrow_attachment_checks':pixel_checks,'independent_duplicate_explicit_paste_and_browser_keyboard_paste_history_exact':True,'native_project_reopen_exact':True,'native_CtrlV_diagnostic':'Windows-level paste delivers stale OS text in this controlled session, correctly rejected. Browser keyboard CtrlV delivers both current marker and PNG and creates a new editable label; explicit app Paste also passes.','cad_selected_entry_routes_to_workshop_and_text_is_inert':True,'cad_return_first_paint_sheet_then_explicit_annotation_selection':True,'sha256':hashes}
(out/'labels-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'verified_label_stages':len(hashes),'native_drags':len(pointer_checks),'pixel_attachment_states':len(pixel_checks)}))
