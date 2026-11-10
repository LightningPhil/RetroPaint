"""Independent radial wall, open bore and volume measurements from native STL."""
from pathlib import Path
import copy,hashlib,json,math,struct
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={};documents={};metrics={}
for wall in [2,3]:
    prefix=f'mouse-audit-solid159-tube-wall{wall}';raw=(downloads/(prefix+'.retropaint')).read_bytes();(out/(prefix+'.retropaint')).write_bytes(raw);d=json.loads(raw);documents[wall]=d;layer=next(l for l in d['layers'] if 'cad' in l);body=layer['cad']['bodies'][0];assert body['solid']['shape']=='tube' and body['solid']['size']==[40,40,30] and body['solid']['wall']==wall and body['scale']==[1,1,1]
    name=prefix+'-3d-mm.stl';raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();count=struct.unpack_from('<I',raw,80)[0];assert len(raw)==84+50*count;tri=np.array([struct.unpack_from('<12fH',raw,84+50*i)[3:12] for i in range(count)]).reshape(-1,3,3);radii=np.sqrt(np.sum(tri[:,:,:2]**2,axis=2));assert np.all(np.minimum(abs(radii-20),abs(radii-(20-wall)))<.00001);assert np.allclose(tri.max(axis=(0,1))-tri.min(axis=(0,1)),[40,40,30]);volume=float(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6);ideal=math.pi*(400-(20-wall)**2)*30;assert abs(volume/ideal-1)<.002
    # No horizontal cap triangle contains the central axis. An annulus may
    # legitimately triangulate some boundary wedges with three outer vertices.
    flat=np.ptp(tri[:,:,2],axis=1)<.00001;assert np.any(flat);cap=tri[flat,:,:2];following=np.roll(cap,-1,axis=1);cross=cap[:,:,0]*following[:,:,1]-cap[:,:,1]*following[:,:,0];assert not np.any(np.all(cross>=-1e-8,axis=1)|np.all(cross<=1e-8,axis=1))
    metrics[str(wall)]=dict(outer_diameter_mm=40,inner_diameter_mm=40-2*wall,wall_mm=wall,volume_mm3=volume,analytic_volume_mm3=ideal)
index=next(i for i,l in enumerate(documents[2]['layers']) if 'cad' in l);expected=copy.deepcopy(documents[2]);expected['layers'][index]['cad']['bodies'][0]['solid']['wall']=3;expected['layers'][index]['image']=documents[3]['layers'][index]['image'];assert expected==documents[3]
after=(downloads/'mouse-audit-solid160-after-invalid.retropaint').read_bytes();(out/'mouse-audit-solid160-after-invalid.retropaint').write_bytes(after);assert json.loads(after)==documents[3];ui=json.loads((out/'solid160-ui.json').read_text());assert all('must be' in r['status'] for r in ui['invalid']);report=dict(status='Pass',metrics=metrics,invalid_walls=[r['wall'] for r in ui['invalid']],whole_project_exact_after_rejection=True,other_source_fields_exact=True,hashes=hashes);(out/'solid160-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
