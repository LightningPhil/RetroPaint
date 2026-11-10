"""Native parameter edits, transformed updates and real workshop Join/Cut oracles."""
import hashlib,json,struct
from collections import Counter
from pathlib import Path
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse'
downloads=Path.home()/'Downloads';hashes={}
def retain(name):
 data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(stage):return json.loads(retain('mouse-audit-code-'+stage+'.retropaint'))
def bodies(d):return next(l for l in d['layers'] if l.get('cad'))['cad']['bodies']
base=doc('reopened');numeric=doc('numeric')
source='// width=999; fake=123;\n/* depth=888; */\nwidth = 2.5e1; // keep this comment\ndepth=5;\nheight=3;\nrepeat=1;\nrepeat=2;\ntext="width=999; quoted=42;";\nexpr=2+3;\nmodule block(){local=8;cube([width,depth,height]);}\nblock();\n'
assert retain('main (1).scad')==source.encode()
assert bodies(numeric)[:-1]==bodies(base) and bodies(numeric)[-1]['script']['source']==source
before=doc('transform-before');updated=doc('transform-updated')
assert bodies(before)==bodies(doc('transform-undone'))
assert bodies(updated)==bodies(doc('transform-redone'))
a,b=bodies(before)[-1],bodies(updated)[-1]
assert a['script']['source']==source and b['script']['source']==source.replace('2.5e1','30')
assert a['id']==b['id']
for k,v in {'name':'Numeric parameters','position':[37,-11,8],'rotation':[0,0,90],'scale':[2,2,2],'color':'#9f89dc'}.items():assert a[k]==b[k]==v
assert bodies(before)[:-1]==bodies(updated)[:-1]==bodies(base)
boolean_before=doc('boolean-before');assert bodies(boolean_before)[:-1]==bodies(updated)
for stage,operation in [('joined','union'),('cut','subtract')]:
 d=doc(stage);assert bodies(d)[:-1]==bodies(base)
 solid=bodies(d)[-1]['solid'];assert solid['kind']=='boolean' and solid['operation']==operation
 assert solid['children']==bodies(boolean_before)[-2:]
 undone=doc('join-undone' if stage=='joined' else 'cut-undone')
 redone=doc('join-redone' if stage=='joined' else 'cut-redone')
 assert bodies(undone)==bodies(boolean_before) and bodies(redone)==bodies(d)
 for x in [d,undone,redone]:assert x['layers'][:2]==base['layers'][:2]
assert doc('boolean-reopened')==doc('cut-redone')

def mesh(stage):
 data=retain('mouse-audit-code-'+stage+'-3d-mm.stl');n=struct.unpack_from('<I',data,80)[0];assert len(data)==84+50*n
 tris=[];points=[];edges=Counter();directions=Counter();volume=0
 for i in range(n):
  a,b,c=[struct.unpack_from('<3f',data,96+50*i+12*j) for j in range(3)];tris.append((a,b,c));points.extend([a,b,c])
  volume+=sum(a[j]*(b[(j+1)%3]*c[(j+2)%3]-b[(j+2)%3]*c[(j+1)%3]) for j in range(3))/6
  for start,end in [(a,b),(b,c),(c,a)]:
   edge=tuple(sorted([start,end]));edges[edge]+=1;directions[edge]+=1 if start<end else -1
 assert all(v==2 for v in edges.values()) and not any(directions.values())
 return {'triangles':n,'size_mm':[max(p[j] for p in points)-min(p[j] for p in points) for j in range(3)],'volume_mm3':volume,'closed_outward':True},tris
meshes={};triangles={}
for name,size,volume in [('numeric',[25,5,3],375),('transform-redone',[10,60,6],3600),('boolean-before',[22,69,10],8592),('join-redone',[10,60,6],2592)]:
 m,t=mesh(name);assert max(abs(a-b) for a,b in zip(m['size_mm'],size))<1e-5 and abs(m['volume_mm3']-volume)<1e-5,(name,m)
 meshes[name]=m;triangles[name]=t
def inside(point,tris):
 # Ray along X; intersect triangle in YZ projection. Probe coordinates avoid edges.
 hits=[]
 for a,b,c in tris:
  den=(b[2]-c[2])*(a[1]-c[1])+(c[1]-b[1])*(a[2]-c[2])
  if abs(den)<1e-10:continue
  u=((b[2]-c[2])*(point[1]-c[1])+(c[1]-b[1])*(point[2]-c[2]))/den
  v=((c[2]-a[2])*(point[1]-c[1])+(a[1]-c[1])*(point[2]-c[2]))/den
  if min(u,v,1-u-v)<-1e-9:continue
  x=u*a[0]+v*b[0]+(1-u-v)*c[0]
  if x>point[0]+1e-8 and not any(abs(x-h)<1e-7 for h in hits):hits.append(x)
 return len(hits)%2==1
cut=triangles['join-redone']
probes=[([33,0.37,2.71],False),([28,0.37,2.71],True),([33,30.37,2.71],True),([40,30.37,2.71],False)]
for point,expected in probes:assert inside(point,cut)==expected
report={'parameter_download_changes_only_numeric_literal':True,'ambiguous_comments_strings_expressions_and_module_locals_preserved':True,
 'update_retains_identity_placement_rotation_scale_colour':True,'source_geometry_undo_redo_exact':True,
 'join_cut_retain_exact_child_sources_and_transforms':True,'neighbour_models_and_paint_photo_layers_exact':True,
 'whole_native_reopen_exact':True,'independent_stl_oracles':meshes,'cut_inside_outside_ray_probes':probes,'sha256':hashes}
(out/'code-workshop-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
