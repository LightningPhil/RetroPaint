"""Exact transforms, invalid-input rejection and off-paper vector recovery."""
from pathlib import Path
import copy,hashlib,json,math
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(prefix,n):
    name=f'mouse-audit-vector{prefix}-{n}.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
before=doc('79','field-arrow');sized=doc('80','exact-size-position');turned=doc('80','turned');original=before['layers'][0]['objects'][0]
def bbox(o):
    a,b,c,d,e,f=o['matrix'];pts=[(a*x+c*y+e,b*x+d*y+f)for x,y in [(0,0),(o['width'],0),(0,o['height']),(o['width'],o['height'])]];xs,ys=zip(*pts);return [min(xs),min(ys),max(xs)-min(xs),max(ys)-min(ys)]
def only_matrix(doc1,doc2):
    a=copy.deepcopy(doc1);b=copy.deepcopy(doc2);a['layers'][0]['objects'][0]['matrix']=b['layers'][0]['objects'][0]['matrix'];assert a==b
only_matrix(before,sized);assert max(abs(a-b)for a,b in zip(bbox(sized['layers'][0]['objects'][0]),[-20,30,200,160]))<1e-8
only_matrix(sized,turned);c=math.cos(math.pi/6);s=math.sin(math.pi/6);expected=[c*200/original['width'],s*200/original['width'],-s*160/original['height'],c*160/original['height'],80-100*c+80*s,110-100*s-80*c]
assert max(abs(a-b)for a,b in zip(turned['layers'][0]['objects'][0]['matrix'],expected))<1e-8
for n in ['zero-rejected','empty-rejected','overflow-rejected']:assert doc('80',n)==turned
for n,left,top in [('escape',-80,100),('desk',-100,120),('recovered',80,100)]:
    d=doc('81',n);only_matrix(turned,d);bounds=bbox(d['layers'][0]['objects'][0]);assert abs(bounds[0]-left)<1e-8 and abs(bounds[1]-top)<1e-8
assert json.loads((out/'vector81-recovery.json').read_bytes())=={'piece':'1. Rectangle','left':'-100','top':'120'}
report={'status':'Pass','exact_negative_position_and_size':[-20,30,200,160],'rotation30_matrix_independently_verified':True,'zero_empty_overflow_rejected_entire_project_exact':True,'Escape_and_desk_settle_keep_full_vector_and_all_neighbours':True,'piece_list_recovery_exact':True,'sha256':hashes};(out/'vector80-81-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS exact size/position/rotation, invalid inputs, off-paper settle and recovery')
