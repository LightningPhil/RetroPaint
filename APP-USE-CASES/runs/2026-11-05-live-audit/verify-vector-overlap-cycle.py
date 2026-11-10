"""Correlate native Alt-click target names with saved scene identities."""
from pathlib import Path
import copy,hashlib,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(n):
    name='mouse-audit-vector82-'+n+'.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
stack=doc('stack');objects=stack['layers'][0]['objects'];assert len(objects)==19
cycle=json.loads((out/'vector82-cycle.json').read_bytes());assert [v['value']for v in cycle]==[objects[18]['id'],objects[17]['id'],objects[0]['id'],objects[18]['id']]
assert [v['label']for v in cycle]==['19. Rectangle','18. Rectangle','1. Rectangle','19. Rectangle']
for name,left,top in [('offpaper',-400,100),('recovered',80,100)]:
    d=doc(name);expected=copy.deepcopy(stack);expected['layers'][0]['objects'][18]['matrix']=d['layers'][0]['objects'][18]['matrix'];assert expected==d
    o=d['layers'][0]['objects'][18];a,b,c,z,e,f=o['matrix'];pts=[(a*x+c*y+e,b*x+z*y+f)for x,y in [(0,0),(o['width'],0),(0,o['height']),(o['width'],o['height'])]];assert abs(min(p[0]for p in pts)-left)<1e-8 and abs(min(p[1]for p in pts)-top)<1e-8
    if name=='offpaper':assert max(p[0]for p in pts)<0
recovery=json.loads((out/'vector82-recovery.json').read_bytes());assert recovery==cycle[0]
report={'status':'Pass','native_Alt_cycle_three_distinct_IDs_and_wrap':cycle,'fully_offpaper_named_recovery':recovery,'all_other_geometry_and_pixels_exact':True,'sha256':hashes};(out/'vector82-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS three-object Alt cycle and named fully-offpaper recovery with all scene data preserved')
