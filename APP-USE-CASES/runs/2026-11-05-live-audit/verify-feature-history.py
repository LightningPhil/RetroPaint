"""Independent named nested recipes, complete transactions and precision-mesh checks."""
from pathlib import Path
import copy,hashlib,json,math
import numpy as np
from stl_oracle import read_binary,measure
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-feature196';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
docs=[json.loads(retain(prefix+(f' ({i})' if i else '')+'.retropaint')) for i in range(12)];index=next(i for i,l in enumerate(docs[0]['layers']) if l['name']=='Trace plate')
def canonical(doc):
 d=copy.deepcopy(doc);d.pop('active',None);d['layers'][index].pop('image',None);return d
def recipe(doc):return doc['layers'][index]['cad']['bodies'][0]['solid']
def named(doc):
 d=copy.deepcopy(doc);r=recipe(d);r['feature']={'label':'Entry round'};cut=r['source']['solid'];cut['feature']={'label':'Drilled plate'}
 for b,label,sketch in zip(cut['children'],['Plate pull','Through hole'],['Plate outline','Hole circle']):b['solid']['feature'].update(label=label,sketchName=sketch)
 return d
assert canonical(named(docs[0]))==canonical(docs[2])==canonical(docs[3])==canonical(docs[5])
edited=copy.deepcopy(docs[2]);recipe(edited)['source']['solid']['children'][0]['solid']['height']=7
assert canonical(edited)==canonical(docs[4])==canonical(docs[6])
suppressed=copy.deepcopy(edited);recipe(suppressed)['feature']['suppressed']=True
assert canonical(suppressed)==canonical(docs[7])==canonical(docs[9])
enabled=copy.deepcopy(edited);recipe(enabled)['feature']['suppressed']=False
assert canonical(enabled)==canonical(docs[8])==canonical(docs[10])==canonical(docs[11])
ui=json.loads((out/'feature196-ui.json').read_text(encoding='utf-8'));raws=[];results=[]
for item,height,suppressed in zip(ui['meshes'],[5,7,7,7],[False,False,True,False]):
 n=item['stlIndex'];raw=retain(prefix+'-3d-mm'+(f' ({n})' if n else '')+'.stl');raws.append(raw);tri=read_binary(raw);stats=measure(tri)
 assert len(stats['components'])==1 and stats['components'][0]['euler']==0 and np.max(abs(np.array(stats['bounds_mm'])-[[-10,-5,0],[10,5,height]]))<.001
 radius,size=2,.5;removed=math.pi*(2*radius*size**2+5/3*size**3-math.pi/2*(radius+size)*size**2)
 expected=200*height-4*math.pi*height-(0 if suppressed else removed)
 # Precision circular tessellation: preexisting circular-finish oracle budget0.03mm3; suppressed96gon hole budget0.10mm3.
 tolerance=.10 if suppressed else .03
 assert abs(stats['signed_volume_mm3']-expected)<tolerance
 a,b,c=tri[:,0],tri[:,1],tri[:,2];den=(b[:,1]-c[:,1])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,1]-c[:,1]);valid=abs(den)>1e-9;a,b,c,den=a[valid],b[valid],c[valid],den[valid]
 for x,y,wanted in [(.31,.57,[]),(5.31,2.57,[0,height])]:
  u=((b[:,1]-c[:,1])*(x-c[:,0])+(c[:,0]-b[:,0])*(y-c[:,1]))/den;v=((c[:,1]-a[:,1])*(x-c[:,0])+(a[:,0]-c[:,0])*(y-c[:,1]))/den;hit=(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7);hits=sorted(set(np.round((u*a[:,2]+v*b[:,2]+(1-u-v)*c[:,2])[hit],5).tolist()));assert hits==wanted
 results.append(dict(stage=item['stage'],mesh=stats,analytic_volume_mm3=expected,absolute_volume_tolerance_mm3=tolerance))
assert raws[0]==(out/'mouse-audit-hole-fillet05-3d-mm.stl').read_bytes() and raws[1]==raws[3]
labels={x['key']:x['name'] for x in ui['renames']};assert len(labels)==6
for key in labels:
 row=next(x for x in ui['reopenedPage1']+ui['reopenedPage2'] if x['key']==key);assert labels[key] in row['text']
assert 'Apply or cancel'in ui['previewSaveGuard'] and 'disappeared'in ui['missingSupport']['status'] and ui['invalidPreview']['editorOpen'] and ui['invalidPreview']['depth']=='0' and ui['invalidPreview']['status']
report=dict(status='Pass',six_independent_feature_and_sketch_names_saved_reopened=True,rename_and_two_preview_cancel_mesh_byte_exact=True,complete_depth7_apply_single_undo_redo_exact=True,attached_through_hole_and_fillet_follow_actual_depth7_mesh=True,suppression_retains_recipe_and_passes_source_through=True,reenable_restores_byte_exact_finished_mesh=True,suppression_undo_and_missing_support_error_atomic=True,invalid_preview_retains_editor_and_original=True,unrelated_model_photo_annotation_and_layer_stack_exact=True,meshes=results,hashes=hashes)
(out/'feature196-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['meshes','hashes']},indent=2))
