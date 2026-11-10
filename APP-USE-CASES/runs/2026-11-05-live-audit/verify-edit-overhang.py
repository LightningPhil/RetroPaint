"""Verify four native desk drags, full source recovery and exact centring."""
from pathlib import Path
from datetime import datetime
from PIL import Image
import base64,hashlib,io,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def image(b):return Image.open(io.BytesIO(b)).convert('RGBA')
def actual(suffix,ext='retropaint'):
 name=f'mouse-audit-edit-overhang38-{suffix}.{ext}';b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(suffix):return json.loads(actual(suffix))
src=image((out.parent/'fixtures/patch-labelled.png').read_bytes());before=doc('before');assert image(base64.b64decode(before['layers'][0]['image'].split(',',1)[1])).tobytes()==src.tobytes()
piece=src.crop((100,100,200,180));expected=src.copy();expected.paste((0,0,0,0),(100,100,200,180));expected.alpha_composite(piece,(430,280));e=json.loads((out/'edit-overhang38-evidence.json').read_bytes());assert {c['edge'] for c in e['cases']}=={'left','right','top','bottom'}
events=[]
for line in (out.parent/'fault-controls/requests.jsonl').read_text(encoding='utf-8').splitlines():
 if 'native pointer' not in line or 'pointerdown' not in line:continue
 event=json.loads(line)['event'];p=event.get('detail',{})
 if isinstance(p,dict) and p.get('phase')=='pointerdown':events.append((datetime.fromisoformat(event['at'].replace('Z','+00:00')).timestamp()*1000,p))
proof=[]
for c in e['cases']:
 edge=c['edge'];assert c['bringOffered'] and c['overlayVisible'] and c['returnedOutside'] and not c['afterDeskBring'] and not c['centredBring'];assert c['outsideSize']=='100 × 80 px · trims on Place' and c['afterDeskSize']==c['centredSize']=='100 × 80 px'
 assert image((out/f'mouse-audit-edit-overhang38-{edge}-recovered-copy.png').read_bytes()).tobytes()==piece.tobytes()
 downs=[p for at,p in events if c['deskDragStart']<=at<=c['deskDragEnd']];assert len(downs)==1;p=downs[0];assert p['target'] in ('canvasSlot','workspaceOverlay');r=p['paperRect'];point=[(p['clientX']-r['x'])/r['width']*960,(p['clientY']-r['y'])/r['height']*640];assert max(abs(a-b) for a,b in zip(point,c['deskPoint']))<1
 assert {'left':point[0]<0,'right':point[0]>960,'top':point[1]<0,'bottom':point[1]>640}[edge]
 after=doc(edge+'-placed');assert image(base64.b64decode(after['layers'][0]['image'].split(',',1)[1])).tobytes()==expected.tobytes()==image(actual(edge+'-placed','png')).tobytes();complete=json.loads(json.dumps(before));complete['layers'][0]['image']=after['layers'][0]['image'];assert complete==after and doc(edge+'-undone')==before and doc(edge+'-redone')==after
 proof.append({'edge':edge,'actual_desk_drag_source':point,'actual_target':p['target'],'complete_source_clipboard_RGBA_exact':True,'centred_placement_and_whole_history_exact':True})
assert doc('reopened')==after and image(actual('reopened','png')).tobytes()==expected.tobytes()
report={'status':'Pass','four_edges':proof,'native_project_png_reopen_exact':True,'sha256':hashes};(out/'edit-overhang38-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
