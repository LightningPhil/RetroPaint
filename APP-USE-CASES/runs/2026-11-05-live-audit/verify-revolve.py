"""Analytic polygon-of-revolution volume, topology, cavities and saved profile oracle."""
from pathlib import Path
import copy,hashlib,json,math
import numpy as np
from stl_oracle import read_binary,measure
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-revolve194';hashes={}
def retain(name,mesh=False):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return read_binary(raw) if mesh else json.loads(raw)
ui=json.loads((out/'revolve194-ui.json').read_text(encoding='utf-8'));base=retain(prefix+'.retropaint');index=next(i for i,l in enumerate(base['layers']) if 'cad'in l)
profiles={
 'vase':[[0,0],[15,0],[18,5],[13,15],[10,30],[14,40],[12,40],[8,30],[11,15],[16,5],[13,2],[0,2]],
 'goblet':[[0,0],[15,0],[15,2],[4,4],[3,24],[14,27],[19,40],[17,42],[15,30],[2,27],[0,27]],
 'knob':[[0,0],[8,0],[8,6],[15,8],[18,12],[15,18],[0,18]],
 'annulus-half':[[10,0],[30,0],[30,40],[10,40]],
 'annulus-full-history':[[10,0],[30,0],[30,40],[10,40]],
 'custom-frustum':[[10,0],[30,0],[25,40],[10,40]]}
def canonical(doc):
 d=copy.deepcopy(doc);d.pop('active',None);d['layers'][index].pop('image',None);return d
def ray(tri,x,y):
 a,b,c=tri[:,0],tri[:,1],tri[:,2];den=(b[:,1]-c[:,1])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,1]-c[:,1]);valid=abs(den)>1e-9
 a,b,c,den=a[valid],b[valid],c[valid],den[valid];u=((b[:,1]-c[:,1])*(x-c[:,0])+(c[:,0]-b[:,0])*(y-c[:,1]))/den;v=((c[:,1]-a[:,1])*(x-c[:,0])+(a[:,0]-c[:,0])*(y-c[:,1]))/den;hit=(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)
 return sorted(set(np.round((u*a[:,2]+v*b[:,2]+(1-u-v)*c[:,2])[hit],6).tolist()))
results={};docs={}
for s in ui['samples']:
 stage=s['stage'];doc=retain(prefix+f" ({s['docIndex']}).retropaint");docs[stage]=doc;bodies=doc['layers'][index]['cad']['bodies'];assert len(bodies)==1;b=bodies[0];r=b['solid'];points=profiles[stage];angle=180 if stage=='annulus-half' else 360
 assert r['kind']=='revolve' and r['points']==points and r['degrees']==angle and r['plane']==dict(origin=[0,0,0],u=[1,0,0],v=[0,1,0],normal=[0,0,1])
 assert b['position']==b['rotation']==[0,0,0] and b['scale']==[1,1,1]
 expected=copy.deepcopy(base);expected['layers'][index]['cad']['bodies']=bodies;assert canonical(doc)==canonical(expected)
 suffix=f" ({s['stlIndex']})" if s['stlIndex'] else '';tri=retain(prefix+'-3d-mm'+suffix+'.stl',True);stats=measure(tri)
 continuous=abs(sum((a[0]**2+a[0]*b[0]+b[0]**2)*(b[1]-a[1]) for a,b in zip(points,points[1:]+points[:1]))*math.pi/3)*angle/360
 error=abs(stats['signed_volume_mm3']-continuous)/continuous;assert error<.001 and len(stats['components'])==1
 rays={}
 if stage in ['vase','goblet','knob']:
  hits=ray(tri,.31,.57);wanted=[0,2] if stage=='vase' else [0,27] if stage=='goblet' else [0,18];assert np.allclose(hits,wanted,atol=.00001);rays['near_axis']=hits
 if stage.startswith('annulus') or stage=='custom-frustum':
  assert ray(tri,.31,.57)==[];hits=ray(tri,15.31,3.57);assert np.allclose(hits,[0,40],atol=.00001);rays=dict(cavity=[],wall=hits)
 if stage=='annulus-half':
  caps=tri[np.max(abs(tri[:,:,1]),axis=1)<.00001];areas=np.linalg.norm(np.cross(caps[:,1]-caps[:,0],caps[:,2]-caps[:,0]),axis=1)/2;assert abs(areas.sum()-1600)<.001
 results[stage]=dict(mesh=stats,continuous_volume_mm3=continuous,relative_volume_error_percent=100*error,rays=rays)
assert canonical(retain(prefix+f" ({ui['angleUndoDoc']}).retropaint"))==canonical(docs['annulus-half'])
assert ui['drawn']=='10,0; 30,0; 30,40; 10,40' and ui['dragged']=='10,0; 30,0; 25,40; 10,40'
assert len(ui['invalid'])==7 and all(s['status'] and s['pieces']==('1 piece' if s['stage']=='history-zero-angle' else '0 pieces') for s in ui['invalid'])
assert len(ui['reopened'])==6
for item in ui['reopened']:
 actual=[[float(n) for n in p.split(',')] for p in item['points'].split(';')];assert actual==profiles[item['stage']] and item['plane']=='keep'
report=dict(status='Pass',all_three_presets_closed_and_independently_sectioned=True,hollow_vase_floor_2mm_and_goblet_cup_floor_27mm=True,mouse_points_drag_and_numeric_profile_agree=True,invalid_profiles_and_angles_reject_without_piece=True,half_turn_end_caps_total_area_mm2=1600,history_full_turn_and_single_undo_preserve_axis_profile=True,all_six_saved_projects_reopened_with_editable_original_profiles=True,original_paint_and_unrelated_source_exact=True,meshes=results,hashes=hashes)
(out/'revolve194-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['meshes','hashes']},indent=2))
