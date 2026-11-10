"""Analytic per-operation oracles for native OpenSCAD language acceptance."""
import hashlib,json,math,struct,sys
from collections import Counter
from pathlib import Path
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
sys.path.insert(0,str(out.parent/'python-libs'))
from fontTools.ttLib import TTFont
from fontTools.pens.areaPen import AreaPen
def retain(name):
 data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(stage):return json.loads(retain('mouse-audit-language-'+stage+'.retropaint'))
def bodies(d):return next(l for l in d['layers'] if l.get('cad'))['cad']['bodies']
before=doc('before');added=doc('added');undone=doc('undone');redone=doc('redone');reopened=doc('reopened')
assert added==redone==reopened
assert bodies(before)==bodies(undone) and bodies(added)[:-1]==bodies(before)
for d in [added,undone,redone,reopened]:assert d['layers'][:4]==before['layers'][:4]
source=retain('main (2).scad').decode('utf-8');assert bodies(added)[-1]['script']['source']==source
for token in ['function twice','children()','for(p=[for(i=','minkowski()','text("Aa"','difference()','intersection()','rotate(','scale(','mirror(']:assert token in source
data=retain('mouse-audit-language-reopened-3d-mm.stl');n=struct.unpack_from('<I',data,80)[0];assert len(data)==84+n*50
edges=Counter();directions=Counter();points=[];volumes={key:0 for key in ['function_children','comprehension_1','comprehension_2','comprehension_3','minkowski','text','difference','intersection','transforms']}
for i in range(n):
 normal=struct.unpack_from('<3f',data,84+50*i);a,b,c=[struct.unpack_from('<3f',data,96+50*i+12*j) for j in range(3)];points.extend([a,b,c])
 u=[b[j]-a[j] for j in range(3)];v=[c[j]-a[j] for j in range(3)];cross=[u[(j+1)%3]*v[(j+2)%3]-u[(j+2)%3]*v[(j+1)%3] for j in range(3)]
 length=math.sqrt(sum(v*v for v in cross));assert length>0
 assert abs(sum(x*x for x in normal)-1)<1e-5 and sum(x*y for x,y in zip(cross,normal))/length>.99999
 volume=sum(a[j]*(b[(j+1)%3]*c[(j+2)%3]-b[(j+2)%3]*c[(j+1)%3]) for j in range(3))/6
 x=sum(p[0] for p in [a,b,c])/3
 key='function_children' if x<10 else 'comprehension_1' if x<30 else 'comprehension_2' if x<50 else 'comprehension_3' if x<80 else 'minkowski' if x<120 else 'text' if x<180 else 'difference' if x<220 else 'intersection' if x<250 else 'transforms'
 volumes[key]+=volume
 for start,end in [(a,b),(b,c),(c,a)]:
  edge=tuple(sorted([start,end]));edges[edge]+=1;directions[edge]+=1 if start<end else -1
assert all(count==2 for count in edges.values()) and not any(directions.values())
expected={'function_children':4*3*2,'comprehension_1':1*2*3,'comprehension_2':2*2*3,'comprehension_3':3*2*3,'minkowski':(2+1)*(3+2)*(4+3),'difference':10**3-4*4*10,'intersection':5*10*10,'transforms':(2*2)*3*4}
for key,value in expected.items():assert abs(volumes[key]-value)<1e-5,(key,volumes[key],value)
font=TTFont(out.parent/'fixtures/code-folder/assets/NotoSans-Regular.ttf');glyphs=font.getGlyphSet();area=0
for char in 'Aa':
 pen=AreaPen(glyphs);glyphs[font.getBestCmap()[ord(char)]].draw(pen);area+=abs(pen.value)
text_volume=2*area*(10*(100/72)/font['head'].unitsPerEm)**2
assert abs(volumes['text']-text_volume)<.15
size=[max(p[j] for p in points)-min(p[j] for p in points) for j in range(3)]
assert size==[270,14,10]
report={'actual_source_export_and_native_project_reopen_exact':True,'add_undo_redo_retains_sources_and_neighbour_layers':True,
 'closed_oppositely_paired_edges_and_unit_outward_stl_normals':True,'triangles':n,'size_mm':size,
 'independent_analytic_volumes_mm3':expected,'measured_per_operation_volumes_mm3':volumes,
 'independent_true_type_outline_text_volume_mm3':text_volume,'text_polygonal_tolerance_mm3':.15,'sha256':hashes}
(out/'language-operations-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
