"""Independent whole-image layer sampling, object transforms and limit guards."""
from pathlib import Path
from PIL import Image
import base64,hashlib,io,json,math
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def image(b):return Image.open(io.BytesIO(b)).convert('RGBA')
def decode(s):return np.array(image(base64.b64decode(s.split(',',1)[1])))
def actual(scene,suffix,ext='retropaint'):
 name=f'mouse-audit-edit-resize-image39-{scene}-{suffix}.{ext}';b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(scene,suffix):return json.loads(actual(scene,suffix))
def nearest(src,dest):
 h,w=dest.shape[:2];sh,sw=src.shape[:2];xs=(np.arange(w)+.5)*sw/w-.5;ys=(np.arange(h)+.5)*sh/h-.5;ix=np.floor(xs+.5).astype(int).clip(0,sw-1);iy=np.floor(ys+.5).astype(int).clip(0,sh-1)
 match=np.all(dest==src[iy[:,None],ix[None,:]],axis=2);xtie=np.abs(xs-np.floor(xs)-.5)<1e-12;ytie=np.abs(ys-np.floor(ys)-.5)<1e-12;lx=np.floor(xs).astype(int).clip(0,sw-1);ly=np.floor(ys).astype(int).clip(0,sh-1)
 if xtie.any():match|=np.all(dest==src[iy[:,None],lx[None,:]],axis=2)&xtie[None,:]
 if ytie.any():match|=np.all(dest==src[ly[:,None],ix[None,:]],axis=2)&ytie[:,None]
 if xtie.any() and ytie.any():match|=np.all(dest==src[ly[:,None],lx[None,:]],axis=2)&ytie[:,None]&xtie[None,:]
 assert match.all(),'non-nearest layer pixel'
def composite8(layers):
 height,width=layers[0].shape[:2];p=np.zeros((height,width,3),np.uint32);a=np.zeros((height,width,1),np.uint32)
 for layer in layers:
  s=layer.astype(np.uint32);sa=s[:,:,3:4];sp=(s[:,:,:3]*sa+127)//255;p=sp+(p*(255-sa)+127)//255;a=sa+(a*(255-sa)+127)//255
 rgb=(p*255+a//2)//np.maximum(a,1);return np.concatenate((rgb,a),axis=2).clip(0,255).astype('uint8')
def stamp_box(obj,width,height):
 m=obj['matrix'];w,h=obj['width'],obj['height'];angle=obj['angle'];c,s=math.cos(angle),math.sin(angle);points=[]
 for x,y in [(0,0),(w,0),(w,h),(0,h)]:
  u=w/2+c*(x-w/2)-s*(y-h/2);v=h/2+s*(x-w/2)+c*(y-h/2);points.append((m[0]*u+m[2]*v+m[4],m[1]*u+m[3]*v+m[5]))
 xs,ys=zip(*points);return max(0,math.floor(min(xs))-2),max(0,math.floor(min(ys))-2),min(width,math.ceil(max(xs))+2),min(height,math.ceil(max(ys))+2)
e=json.loads((out/'edit-resize-image39-evidence.json').read_bytes());assert len(e['cases'])==7 and len(e['invalid'])==10;before={scene:doc(scene,'before') for scene in ('patch','mix')};assert len(before['mix']['layers'])==4 and doc('patch','rejected')==before['patch'] and doc('mix','rejected')==before['mix']
assert decode(before['patch']['layers'][0]['image']).tobytes()==image((out.parent/'fixtures/patch-labelled.png').read_bytes()).tobytes()
for bad in e['invalid']:assert 'between 1 and 4096' in bad['status'] and bad['dimensions']=='960 × 640 pixels · 1 layer'
assert e['budget']['pixels']==67108864 and 'too many pixels across its layers' in e['budget']['status'] and e['budget']['dimensions']=='960 × 640 pixels · 4 layers';assert 'between 1 and 4096' in e['percentEdgeReject']['status'] and e['percentEdgeReject']['dimensions']=='960 × 640 pixels · 4 layers'
results=[]
for case in e['cases']:
 scene,label=case['scene'],case['label'];old=before[scene];after=doc(scene,label);width,height=case['entered']
 if case['units']=='percent':width=round(old['width']*width/100);height=round(old['height']*height/100)
 assert not case['scopeSelection'] and (after['width'],after['height'])==(width,height);sx,sy=width/old['width'],height/old['height'];expected=json.loads(json.dumps(old));expected['width']=width;expected['height']=height;arrays=[];objects=[]
 for i,layer in enumerate(old['layers']):
  new=after['layers'][i];src=decode(layer['image']);dest=decode(new['image']);assert dest.shape==(height,width,4);nearest(src,dest);expected['layers'][i]['image']=new['image'];arrays.append(dest);assert layer['opacity']==1
  for j,o in enumerate(layer.get('objects',[])):
   m=o['matrix'];want=[sx*m[0],sy*m[1],sx*m[2],sy*m[3],sx*m[4],sy*m[5]];actual_m=new['objects'][j]['matrix'];assert max(abs(a-b) for a,b in zip(actual_m,want))<1e-9;expected['layers'][i]['objects'][j]['matrix']=actual_m;objects.append(new['objects'][j])
 assert after==expected and doc(scene,label+'-undone')==old and doc(scene,label+'-redone')==after
 png=np.array(image(actual(scene,label,'png')));assert png.shape==(height,width,4);expected_png=composite8(arrays);uncovered=np.ones((height,width),bool)
 for obj in objects:
  assert obj['kind']=='stamp';left,top,right,bottom=stamp_box(obj,width,height);uncovered[top:bottom,left:right]=False
 assert np.array_equal(png[uncovered],expected_png[uncovered]),(scene,label,'composite outside retained stamp changed')
 if objects and label in ('pixels','percent'):assert np.any(png[~uncovered]!=expected_png[~uncovered]),'Retained stamp did not render'
 if scene=='patch':
  factor=sx;assert sx==sy
  for x,y,colour in [(100,100,(255,0,0,255)),(400,100,(0,0,255,255)),(100,300,(0,255,0,255)),(400,300,(255,0,0,128))]:
   patch=png[round(y*factor):round((y+80)*factor),round(x*factor):round((x+100)*factor)];assert np.all(patch==colour)
 results.append({'scene':scene,'label':label,'dimensions':[width,height],'layers_sample_nearest_source_exactly':len(arrays),'retained_stamp_matrix_and_definition_preserved':bool(objects),'composite_outside_stamp_RGBA_exact':True,'whole_undo_redo_exact':True})
for scene in ('patch','mix'):assert doc(scene,'reopened')==doc(scene,'percent-redone') and image(actual(scene,'reopened','png')).tobytes()==image(actual(scene,'percent','png')).tobytes()
report={'status':'Pass','cases':results,'ten_invalid_axis_entries_and_percent_limit_preserve_project':True,'four_layer_total_pixel_budget_rejects_without_document_change':True,'native_project_png_reopens_exact':True,'sha256':hashes};(out/'edit-resize-image39-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
