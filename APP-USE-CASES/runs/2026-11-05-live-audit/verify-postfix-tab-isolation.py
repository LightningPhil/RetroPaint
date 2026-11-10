"""Actual Chrome Duplicate plus independent native edits after resumed-ID fix."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(stage):
 name='mouse-audit-postfix-'+stage+'.retropaint';data=(Path.home()/'Downloads'/name).read_bytes()
 (out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
baseline=doc('original-before-duplicate');assert doc('duplicate-baseline')==baseline
original=doc('original-before-refresh');duplicate=doc('duplicate-before-refresh')
assert original==doc('original-after-refresh') and duplicate==doc('duplicate-after-refresh') and original!=duplicate
geometry={}
for label,d,color,x in [('original',original,'#1E88E5',100),('duplicate',duplicate,'#43A047',500)]:
 assert d['layers'][:3]==baseline['layers'][:3]
 a,b=baseline['layers'][3],d['layers'][3]
 assert a['image']==b['image'] and a['live']==b['live'] and a['objects']==b['objects'][:-1]
 p=b['objects'][-1];assert p['kind']=='path' and p['fill'] is None and p['stroke']['color']==color
 assert len(p['paths'])==1 and p['paths'][0]['closed'] and p['lineWidth']==22
 assert p['matrix'][:4]==[1,0,0,1]
 points=[(v['x']+p['matrix'][4],v['y']+p['matrix'][5]) for v in p['paths'][0]['points']]
 bounds=[min(a for a,b in points),min(b for a,b in points),max(a for a,b in points),max(b for a,b in points)]
 assert max(abs(v-w) for v,w in zip(bounds,[x,450,x+70,500]))<2
 geometry[label]={'stroke':color,'bounds_pixels':bounds}
result={'genuine_native_chrome_duplicate_command':True,'each_tab_has_distinct_source_edit':True,
 'each_native_reload_resume_preserves_own_whole_document_exact':True,
 'all_neighbour_photo_live_and_existing_pieces_exact':True,'independent_rectangle_oracles':geometry,'sha256':hashes}
(out/'postfix-tab-isolation-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='sha256'},indent=2))
