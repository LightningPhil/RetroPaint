"""Independent saved-project and STL oracles for ten mouse-run code starters.

Expected dimensions, volumes and feature probes are derived from the published
recipes, not the application's mesh statistics. Twist volumes allow 2% for
finite sliced triangulation; the default low-resolution tower spheres allow a
0.2mm pole inset. Native STL coordinates are float32.
"""
import base64,copy,hashlib,io,json,math,struct
from collections import Counter,defaultdict
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[3]
out=root/'test-results/audit-2026-11-05/mouse'
downloads=Path.home()/'Downloads';hashes={}
thumbnail_differences=[]

def retain(name):
 data=(downloads/name).read_bytes();(out/name).write_bytes(data)
 hashes[name]=hashlib.sha256(data).hexdigest();return data

def doc(name):return json.loads(retain(name+'.retropaint'))
def bodies(d):return next(l for l in d['layers'] if l.get('cad'))['cad']['bodies']
def same_document(a,b,label):
 a,b=copy.deepcopy(a),copy.deepcopy(b)
 for la,lb in zip(a['layers'],b['layers']):
  if not la.get('cad'):continue
  pa,pb=[Image.open(io.BytesIO(base64.b64decode(l.pop('image').split(',')[1]))).convert('RGBA').tobytes() for l in (la,lb)]
  assert len(pa)==len(pb)
  differences=[(i,x,y) for i,(x,y) in enumerate(zip(pa,pb)) if x!=y]
  assert all(abs(x-y)<=1 and i%4!=3 for i,x,y in differences)
  pixels=len(set(i//4 for i,_,_ in differences));assert pixels<=3,(label,pixels)
  thumbnail_differences.append({'comparison':label,'changed_preview_pixels':pixels,'maximum_rgb_level_delta':max([abs(x-y) for _,x,y in differences],default=0)})
 assert a==b,label
def inside(p,tris):
 # X-ray, deduplicating hits on a shared triangulation edge.
 hits=[]
 for a,b,c in tris:
  den=(b[2]-c[2])*(a[1]-c[1])+(c[1]-b[1])*(a[2]-c[2])
  if abs(den)<1e-10:continue
  u=((b[2]-c[2])*(p[1]-c[1])+(c[1]-b[1])*(p[2]-c[2]))/den
  v=((c[2]-a[2])*(p[1]-c[1])+(a[1]-c[1])*(p[2]-c[2]))/den
  if min(u,v,1-u-v)<-1e-9:continue
  x=u*a[0]+v*b[0]+(1-u-v)*c[0]
  if x>p[0]+1e-8 and not any(abs(x-h)<1e-7 for h in hits):hits.append(x)
 return len(hits)%2==1

def mesh(name):
 data=retain(name+'-3d-mm.stl');n=struct.unpack_from('<I',data,80)[0]
 assert len(data)==84+n*50
 edges=Counter();directions=Counter();points=[];tris=[];volume=0;adj=defaultdict(set)
 for i in range(n):
  normal=struct.unpack_from('<3f',data,84+50*i)
  a,b,c=[struct.unpack_from('<3f',data,96+50*i+12*j) for j in range(3)]
  tris.append((a,b,c));points.extend((a,b,c))
  u=[b[j]-a[j] for j in range(3)];v=[c[j]-a[j] for j in range(3)]
  cross=[u[(j+1)%3]*v[(j+2)%3]-u[(j+2)%3]*v[(j+1)%3] for j in range(3)]
  length=math.sqrt(sum(x*x for x in cross));assert length>1e-12
  assert abs(sum(x*x for x in normal)-1)<1e-5
  assert sum(x*y for x,y in zip(normal,cross))/length>.99999
  volume+=sum(a[j]*(b[(j+1)%3]*c[(j+2)%3]-b[(j+2)%3]*c[(j+1)%3]) for j in range(3))/6
  for start,end in [(a,b),(b,c),(c,a)]:
   edge=tuple(sorted((start,end)));edges[edge]+=1;directions[edge]+=1 if start<end else -1
   adj[start].add(end);adj[end].add(start)
 assert all(v==2 for v in edges.values()) and not any(directions.values())
 seen=set();todo=[points[0]]
 while todo:
  p=todo.pop()
  if p in seen:continue
  seen.add(p);todo.extend(adj[p]-seen)
 assert len(seen)==len(adj),'Disconnected starter mesh'
 assert volume>0
 lo=[min(p[j] for p in points) for j in range(3)];hi=[max(p[j] for p in points) for j in range(3)]
 return {'triangles':n,'size_mm':[b-a for a,b in zip(lo,hi)],'volume_mm3':volume,'closed_connected_outward':True},tris,points

def size(m,expected,tolerance=.002):
 assert max(abs(a-b) for a,b in zip(m['size_mm'],expected))<tolerance,(m,expected)
def volume(m,expected,tolerance=.003):
 assert abs(m['volume_mm3']-expected)<tolerance,(m,expected)
def probes(tris,items):
 for p,expected in items:assert inside(p,tris)==expected,(p,expected)

evidence=json.loads((out/'starter-variation-evidence.json').read_bytes())
assert [e['index'] for e in evidence]==list(range(1,11))
initial=doc('mouse-audit-starters-r1-before');previous=[];report=[]
for e in evidence:
 i=e['index'];stem=f'mouse-audit-starters-r1-{i:02}'
 base=doc(stem+'-base');variant=doc(stem+'-variant');undone=doc(stem+'-undone');redone=doc(stem+'-redone')
 same_document(base,undone,stem+' Undo');same_document(variant,redone,stem+' Redo')
 assert bodies(base)[:-1]==bodies(variant)[:-1]==previous
 assert base['layers'][0]==variant['layers'][0]==initial['layers'][0]
 a,b=bodies(base)[-1],bodies(variant)[-1]
 assert a['script']['source']==e['base'] and b['script']['source']==e['variant']
 assert a['id']==b['id'] and a['name']==b['name']==e['name']
 for k in ['position','rotation','scale','color']:assert a[k]==b[k]
 pair=[]
 for changed,stage in [(False,'base'),(True,'redone')]:
  m,t,points=mesh(stem+'-'+stage);pair.append(m)
  if i==1:
   h=8 if changed else 7;size(m,[56,56,h])
   volume(m,32*math.sin(2*math.pi/64)*(28**2-8**2-6*2.5**2)*h,.02)
   probes(t,[([0,.17,2.31],False),([20,.17,2.31],False),([12,.17,2.31],True),([27,.17,2.31],True)])
  elif i==2:
   h=25 if changed else 24;size(m,[50,35,h]);volume(m,50*35*h-44*29*(h-3))
   probes(t,[([25,17.13,1.31],True),([25,17.13,4.31],False),([1,17.13,10.31],True)])
  elif i==3:
   radius=6 if changed else 5;size(m,[65,20,m['size_mm'][2]])
   assert 33+1.2*radius-.2<m['size_mm'][2]<=33+1.2*radius+.001
   probes(t,[([31.13,10.17,1.31],True),([10.13,10.17,8.31],True),([55.13,10.17,35.31],True),([65.5,10.17,2.31],False)])
  elif i==4:
   h=36 if changed else 35;size(m,[30,30,h],.02)
   poly=[[15,0],[5,4],[4,15],[-4,5],[-15,4],[-5,-4],[-4,-15],[4,-5]]
   area=abs(sum(p[0]*poly[(j+1)%8][1]-p[1]*poly[(j+1)%8][0] for j,p in enumerate(poly)))/2
   expected=area*h*(1+.6+.6**2)/3
   volume(m,expected,expected*.02);probes(t,[([.13,.17,h/2],True),([20,.17,h/2],False)])
  elif i==5:
   angle=300 if changed else 360
   angles=sorted(set(round(math.atan2(p[1],p[0])%(2*math.pi),6) for p in points if abs(p[2]-24)<1e-4 and abs(math.hypot(*p[:2])-25)<1e-4))
   segments=len(angles)-(1 if changed else 0)
   volume(m,segments/2*math.sin(math.radians(angle)/segments)*2924,.03)
   expectpoints=[(25*math.cos(math.radians(angle)*j/segments),25*math.sin(math.radians(angle)*j/segments)) for j in range(segments+1)]
   size(m,[max(p[0] for p in expectpoints)-min(p[0] for p in expectpoints),max(p[1] for p in expectpoints)-min(p[1] for p in expectpoints),24])
   probes(t,[([.13,1.17,1.31],True),([.13,.17,12.31],False),([.13,16,12],True)])
  elif i==6:
   h=62 if changed else 60;size(m,[56,56,h+4])
   probes(t,[([.13,.17,2.31],False),([25,.17,2.31],True),([24/math.sqrt(2),24/math.sqrt(2),2+h/2],True),([.13,.17,2+h/2],False)])
  elif i==7:
   r=26 if changed else 25;z=r+8.2;size(m,[2*(r+2.2),2*(r+2.2),2*r+10.4])
   probes(t,[([.13,.17,10.31],True),([.13,.17,z],True),([r+1.8,.17,z],True),([12,12,z],False)])
  elif i==8:
   h=66 if changed else 64;size(m,[57,57,h])
   probes(t,[([.13,.17,2.31],True),([.13,.17,5.31],False),([18,.17,h/2],False),([20.5,.17,h/2],True),([28,.17,1.31],True),([30,.17,1.31],False)])
  elif i==9:
   h=66 if changed else 64;size(m,[72,72,h+8])
   z=8+.55*h
   probes(t,[([.13,.17,10.31],True),([.13,.17,13.31],False),([18.5*math.cos(math.pi/3),18.5*math.sin(math.pi/3),z],False),([18.5*math.cos(math.radians(80)),18.5*math.sin(math.radians(80)),z],True),([38,.17,1.31],False)])
  elif i==10:
   h=33 if changed else 32;size(m,[94,74,h+8])
   probes(t,[([.13,.17,2.31],True),([.13,.17,10.31],False),([32.13,22.17,6.31],True),([32.13,22.17,12.31],False),([40.5,22.17,12.31],True),([.13,-22.17,10.31],False),([.13,22.17,10.31],True)])
 if i in [3,6,8]:assert pair[1]['volume_mm3']>pair[0]['volume_mm3']
 if i==3:assert 1.15<pair[1]['volume_mm3']/pair[0]['volume_mm3']<2
 report.append({'index':i,'title':e['title'],'baseline':pair[0],'variation':pair[1]})
 previous=bodies(variant)
same_document(doc('mouse-audit-starters-r1-reopened'),redone,'Native project reopen')
result={'ten_starters_baseline_and_one_controlled_edit_each':True,'exact_editable_data_undo_redo_and_whole_native_reopen':True,'sources_identity_transforms_and_neighbours_retained':True,'regenerated_cad_thumbnail_rounding':thumbnail_differences,'twenty_independent_closed_connected_stl_oracles':report,'sha256':hashes}
(out/'starter-variations-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='sha256'},indent=2))
