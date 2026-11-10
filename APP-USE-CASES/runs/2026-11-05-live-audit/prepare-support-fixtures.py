"""Declared modern cube/sphere and independent rotated/scaled opposite-face fixtures."""
from pathlib import Path
import copy,hashlib,json,math,uuid
import numpy as np
root=Path(__file__).resolve().parents[3];downloads=Path.home()/'Downloads';out=root/'test-results/audit-2026-11-05/fixtures/support204';out.mkdir(parents=True,exist_ok=True)
template=downloads/'mouse-audit-units174.retropaint';native=downloads/'mouse-audit-solid163-boolean165-baseline.retropaint';base=json.loads(template.read_text());cube=copy.deepcopy(json.loads(native.read_text())['layers'][1]['cad']['bodies'][0]);cube['name']='Support cube';cube['position']=[0,0,10]
index=next(i for i,l in enumerate(base['layers']) if 'cad'in l);manifest={'kind':'Declared modern native-schema fixtures; not historical producers','templates':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [template,native]},'fixtures':{}}
angles=np.radians([20,30,40]);cx,cy,cz=np.cos(angles);sx,sy,sz=np.sin(angles);rx=np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]]);ry=np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]]);rz=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]]);rotation=rz@ry@rx
for name in ['cube','sphere','transformed-top','transformed-bottom']:
 d=copy.deepcopy(base);b=copy.deepcopy(cube);layer=d['layers'][index];layer['name']='Support test'
 if name=='sphere':b['id']=str(uuid.uuid5(uuid.NAMESPACE_URL,'retropaint-audit-support204-sphere'));b['name']='Curved sphere';b['solid']['shape']='sphere'
 if name.startswith('transformed'):
  b['position']=[-12,7,4];b['rotation']=[20,30,40];b['scale']=[1.5,.75,2];sign=1 if name.endswith('top') else -1;normal=rotation@np.array([0,0,sign]);centre=np.array(b['position']);up=rotation@np.array([0,1,0]);layer['cad']['view']={'position':(centre+normal*150).tolist(),'target':centre.tolist(),'up':up.tolist(),'projection':'orthographic','span':100}
  info={'face_normal':normal.tolist(),'face_centre':(centre+normal*20).tolist(),'expected_cube_volume_mm3':18000,'expected_with_10x10x7_pad_mm3':18700,'after_local_height30_cube_volume_mm3':27000,'after_height30_with_pad_volume_mm3':27700}
 else:info={'cube_volume_mm3':8000} if name=='cube' else {'sphere_radius_mm':10,'curve_pick_should_reject':True}
 layer['cad']['bodies']=[b];p=out/(name+'.retropaint');p.write_text(json.dumps(d,separators=(',',':')),encoding='utf-8');manifest['fixtures'][name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'body':b,**info}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:{x:y for x,y in v.items() if x!='body'} for k,v in manifest['fixtures'].items()},indent=2))
