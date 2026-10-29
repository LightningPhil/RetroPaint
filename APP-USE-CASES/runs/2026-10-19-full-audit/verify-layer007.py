from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from collections import Counter
from PIL import Image
import json,hashlib,struct,math
import numpy as np
root=Path(__file__).resolve().parent;old=root/'headless/LAYER-007-paint';new=root/'headless/LAYER-007-paint-remaining-final';short=root/'headless/LAYER-007-short-final';cad=root/'headless/LAYER-007-cad-final'
read_json=lambda file:json.loads(file.read_text(encoding='utf-8'))
first=read_json(old/'LAYER-007-paint-ui.json');rest=read_json(new/'LAYER-007-paint-ui.json');last=read_json(short/'LAYER-007-paint-ui.json');cad_ui=read_json(cad/'LAYER-007-cad-ui.json')
assert first['status']=='Fail' and len(first['rows'])==1 and not first['errors'] and 'Show Character' in first['error']
assert rest['status']=='Fail' and len(rest['rows'])==2 and not rest['errors'] and 'objectDelete' in rest['error'] and 'element is not visible' in rest['error']
assert last['status']=='Pass' and len(last['rows'])==1 and not last['errors'] and cad_ui['status']=='Pass' and not cad_ui['errors']
assert first['origin']==rest['origin']==last['origin']==cad_ui['origin']=='http://127.0.0.1:8098/'
fixture=read_json(root/'headless/LAYER-007-fixture/fresh/fixture.retropaint');rows=[];downloads=[]
for evidence,row in [*( (old,r) for r in first['rows']),*((new,r) for r in rest['rows']),*((short,r) for r in last['rows'])]:
    location=evidence/f"{row['width']}x{row['height']}";read=lambda label:read_json(location/(label+'.retropaint'));image=lambda label:np.asarray(Image.open(location/(label+'.png')).convert('RGBA'))
    before=read('before');assert before==fixture;dup=read('duplicated');copy=dup['layers'][3];expected=deepcopy(before);expected['layers'].insert(3,copy);expected['active']=copy['id'];assert dup==expected
    equivalent=deepcopy(before['layers'][2]);equivalent['id']=copy['id'];equivalent['name']='Character copy';assert copy==equivalent and copy['id'] not in {l['id'] for l in before['layers']}
    only=deepcopy(dup);only['layers'][2]['visible']=False;assert read('copy-only')==only and np.array_equal(image('copy-only'),image('before'))
    for label in ['both-again','visibility-redone','photo-undone']:assert read(label)==dup and np.array_equal(image(label),image('duplicated'))
    assert read('visibility-undone')==only and np.array_equal(image('visibility-undone'),image('copy-only'))
    edited=deepcopy(dup);edited['layers'][3]['photo']['settings']['brightness']=20;edited['layers'][3]['photo']['normal']['brightness']=20
    for label in ['photo-edited','photo-redone','move-undone']:assert read(label)==edited and np.array_equal(image(label),image('photo-edited'))
    assert not np.array_equal(image('photo-edited'),image('duplicated'))
    moved=deepcopy(edited);moved['layers'][3]['objects'][1]['matrix'][4]+=20
    for label in ['text-moved','move-redone','delete-undone','final','fresh/reopened']:assert read(label)==moved and np.array_equal(image(label),image('text-moved'))
    deleted=deepcopy(moved);del deleted['layers'][3]['objects'][0]
    for label in ['copy-pixels-live-deleted','delete-redone']:assert read(label)==deleted and np.array_equal(image(label),image('copy-pixels-live-deleted'))
    assert not np.array_equal(image('text-moved'),image('photo-edited')) and not np.array_equal(image('copy-pixels-live-deleted'),image('text-moved'))
    assert copy['objects'][0]['live']['strokes'] and copy['objects'][0]['live']['fills'] and copy['objects'][1]['kind']=='text'
    for label in ['duplicated','copy-only','both-again','visibility-undone','visibility-redone','photo-edited','photo-undone','photo-redone','text-moved','move-undone','move-redone','copy-pixels-live-deleted','delete-undone','delete-redone','final']:
        actual=read(label)['layers'][2];expected_source=deepcopy(before['layers'][2]);expected_source['visible']=label not in ['copy-only','visibility-undone']
        assert actual==expected_source,'Source mutated during '+label
    for file in [location/'events.json',location/'fresh/events.json']:downloads += [e for e in read_json(file) if e['action']=='download']
    rows.append(dict(viewport=[row['width'],row['height']],new_sheet_identity_and_complete_initial_equivalence=True,isolated_copy_composition_exact=True,source_pixels_live_objects_and_photo_recipe_immutable_through_all_copy_edits=True,copy_photo_brightness_20_text_delta_x_20_and_raster_live_deletion_verified=True,each_edit_history_and_actual_fresh_project_rgba_exact=True))
location=cad/'1280x720';read=lambda label:read_json(location/(label+'.retropaint'));image=lambda label:np.asarray(Image.open(location/(label+'.png')).convert('RGBA'))
before=read('cad-before');dup=read('cad-duplicated');copy=dup['layers'][3];original=before['layers'][2];expected=deepcopy(before);expected['layers'].insert(3,copy);expected['active']=copy['id'];assert dup==expected
loaded=read('before');assert loaded==read_json(root/'backups/artwork-before-acceptance-audit.retropaint');loaded['layers'][2]['image']=before['layers'][2]['image'];assert loaded==before
equivalent=deepcopy(original);equivalent['id']=copy['id'];equivalent['name']='3D 1 copy'
assert len(copy['cad']['bodies'])==len(original['cad']['bodies'])>0
for source_body,copy_body,body in zip(original['cad']['bodies'],copy['cad']['bodies'],equivalent['cad']['bodies']):assert source_body['id']!=copy_body['id'];body['id']=copy_body['id']
assert equivalent==copy
ids=[body['id'] for layer in dup['layers'] if layer.get('cad') for body in layer['cad']['bodies']];assert len(ids)==len(set(ids))
assert read('cad-duplicate-undone')==before and read('cad-duplicate-redone')==dup and read('cad-edit-undone')==dup
edited=deepcopy(dup);edited['layers'][3]['cad']['bodies'][0]['name']='Copied shell only';assert read('cad-copy-edited')==edited and read('cad-edit-redone')==edited
final=deepcopy(edited);final['active']=before['layers'][0]['id'];assert read('final')==final and read('fresh/reopened')==final and np.array_equal(image('final'),image('fresh/reopened'))
source_stl=(location/'source-solid.stl').read_bytes();assert source_stl==(location/'copied-solid.stl').read_bytes()
count=struct.unpack_from('<I',source_stl,80)[0];assert len(source_stl)==84+50*count and count>0
edges=Counter();signed=0.;points=[]
for i in range(count):
    values=struct.unpack_from('<12fH',source_stl,84+50*i);normal=np.asarray(values[:3],dtype=float);tri=np.asarray(values[3:12],dtype=float).reshape(3,3);assert np.isfinite(tri).all();cross=np.cross(tri[1]-tri[0],tri[2]-tri[0]);assert np.linalg.norm(cross)>1e-10 and np.dot(normal,cross)>0
    vertices=[tuple(round(float(x),5) for x in point) for point in tri]
    for j in range(3):edges[tuple(sorted((vertices[j],vertices[(j+1)%3])))]+=1
    signed+=float(np.dot(tri[0],np.cross(tri[1],tri[2])))/6;points.extend(tri)
assert all(n==2 for n in edges.values()) and signed>0
for file in [location/'events.json',location/'fresh/events.json']:downloads += [e for e in read_json(file) if e['action']=='download']
assert len(downloads)==151
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,paint_rows=rows,CAD=dict(viewport=[1280,720],all_source_fields_immutable=True,all_top_level_body_ids_unique=True,source_recipes_retained_except_new_identity=True,copy_name_edit_only=True,history_and_fresh_project_rgba_exact=True,actual_source_and_copy_STL_byte_exact=True,triangles=count,independent_closed_oriented_edge_check=True,signed_volume_mm3=signed,bounds_mm=[np.min(points,axis=0).tolist(),np.max(points,axis=0).tolist()],edge_quantisation_mm=.00001),actual_downloads_verified=151,render_time_ms=10000,oracle='Explicit complete layer/object/photo mutations and known20px text translation; exact source invariance, copy-only full RGBA, every edit Undo/Redo and fresh actual saved-file input. CAD recipes and globally distinct top-level body IDs, exact original/copy binary STL, independent struct/NumPy orientation/manifold-edge/signed-volume checks.',coverage_chunks='Desktop paint completed in LAYER-007-paint before a compact palette reopening setup failure; the three remaining viewports completed in LAYER-007-paint-final. CAD layer duplication and body edit were exercised through the exposed desktop layer options, with actual two STL downloads. Failed attempts retained and excluded.',execution='Isolated headless production public UI; no desktop or existing user session access')
report['coverage_chunks']=[dict(folder='headless/LAYER-007-paint',completed_paint_viewports=['1280x720']),dict(folder='headless/LAYER-007-paint-remaining-final',completed_paint_viewports=['320x568','390x844']),dict(folder='headless/LAYER-007-short-final',completed_paint_viewports=['844x390']),dict(folder='headless/LAYER-007-cad-final',completed_CAD_viewports=['1280x720'])]
(root/'evidence/LAYER-007-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
