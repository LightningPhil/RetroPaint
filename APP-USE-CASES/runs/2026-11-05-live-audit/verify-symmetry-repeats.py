"""Independent centre/reflection-group oracle for native asymmetric gestures."""
from pathlib import Path
import copy,hashlib,json,math
import numpy as np
from PIL import Image
from shape_oracle import path_distances
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
def doc(i):return json.loads(retain('mouse-audit-symmetry226'+(f' ({i})'if i else '')+'.retropaint'))
def group(mode):
 if mode=='v':return [np.eye(2),np.diag([-1,1])]
 if mode=='h':return [np.eye(2),np.diag([1,-1])]
 result=[]
 for k in range(int(mode)//2):
  a=4*math.pi*k/int(mode);r=np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
  result.extend([r,r@np.diag([1,-1])])
 return result
base=doc(0);results=[];yy,xx=np.mgrid[:640,:960];pixels=np.column_stack([xx.ravel()+.5,yy.ravel()+.5]);motif=np.array([[668,388],[640,391]])
for j,mode in enumerate(['v','h','4','6','8','10','12']):
 full,undo,redo=map(doc,[1+3*j,2+3*j,3+3*j]);assert undo==base and full==redo
 objects=full['layers'][0]['objects'];assert len(objects)==1;obj=objects[0];assert len(obj['paths'])==len(group(mode));assert obj['opacity']==1 and obj['lineWidth']==3 and obj['fill']is None and obj['stroke']['color'].lower()=='#1e88e5'
 a,b,c,d,e,f=obj['matrix'];actual=[]
 for path in obj['paths']:
  assert not path.get('clip') and not path['closed'];p=np.array([[p['x'],p['y']]for p in path['points']])@np.array([[a,b],[c,d]])+[e,f];actual.append(p)
 expected=[(motif-[480,320])@m.T+[480,320]for m in group(mode)];remaining=list(range(len(actual)))
 for segment in expected:
  found=[k for k in remaining if np.max(path_distances(actual[k],segment))<.001 and max(np.min(np.linalg.norm(actual[k]-end,axis=1))for end in segment)<.001];assert len(found)==1;(remaining.remove(found[0]))
 clean=copy.deepcopy(full);clean['layers'][0].pop('objects');bc=copy.deepcopy(base);bc['layers'][0].pop('objects',None);assert clean==bc
 name='mouse-audit-symmetry226'+(f' ({j})'if j else '')+'.png';retain(name);im=np.array(Image.open(out/name).convert('RGBA')).reshape(-1,4);distance=np.min([path_distances(pixels,seg)for seg in expected],axis=0);outside=distance>2.5;core=distance<.5
 assert np.all(im[outside]==255);assert np.all(im[core]==[30,136,229,255])
 if mode.isdigit():
  angles=np.mod([math.atan2(*(seg[0]-[480,320])[::-1])for seg in expected],2*math.pi);assert len(set(np.floor(angles/(2*math.pi/int(mode))).astype(int)))==int(mode)
 results.append(dict(mode=mode,distinct_copies=len(expected),all_paths_independently_transformed=True,one_undo_restores_exact_blank=True,redo_exact=True,png_safe_pixels=int(outside.sum()+core.sum())))
assert doc(21)==doc(22)
retain('mouse-audit-symmetry226 (7).png');assert np.array_equal(np.array(Image.open(out/'mouse-audit-symmetry226 (6).png')),np.array(Image.open(out/'mouse-audit-symmetry226 (7).png')))
report=dict(status='Pass',radial_case='PLAY-012',mirror_main_flow='PLAY-011 main flow only; deferred axis-opacity finding remains',results=results,twelve_part_actual_project_reopen_exact=True,twelve_part_reopened_png_exact=True,hashes=hashes)
(out/'symmetry226-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items()if k!='hashes'},indent=2))
