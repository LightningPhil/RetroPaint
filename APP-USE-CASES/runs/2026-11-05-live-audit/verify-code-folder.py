"""Native folder/add-files, entry/helper and reopened-source geometry oracles."""
import base64,copy,hashlib,json,math,struct,sys
from collections import Counter
from pathlib import Path
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse'
sys.path.insert(0,str(root/'test-results/audit-2026-11-05/python-libs'))
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.areaPen import AreaPen
downloads=Path.home()/'Downloads';hashes={}
def retain(name):
 data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(s):return json.loads(retain('mouse-audit-folder-'+s+'.retropaint'))
def bodies(d):return next(l for l in d['layers'] if l.get('cad'))['cad']['bodies']
def source_files(body):
 s=body['script'];assert s['language']=='openscad'
 result={f['path']:base64.b64decode(f['data']) for f in s['files']}
 assert s['entry'] not in result;result[s['entry']]=s['source'].encode('utf-8');return result
fixture=root/'test-results/audit-2026-11-05/fixtures'
original={str(p.relative_to(fixture/'code-folder')).replace('\\','/'):p.read_bytes() for p in (fixture/'code-folder').rglob('*') if p.is_file()}
extra={p.name:p.read_bytes() for p in (fixture/'code-additions').iterdir() if p.is_file()}
courier_code=b'linear_extrude(2)text("Aa",size=10,font="Courier New");\n'
mcad_code=b'use <MCAD/boxes.scad>\n$fn=64;\necho("ERROR: quoted text, not an engine error");\nroundedCube([20,12,6],1,true,true);\n'
stages=['pad20','pad24','alternate34','assets','font-noto','font-courier','mcad','heightmap']
docs={name:doc(name) for name in stages}
for i,name in enumerate(stages):
 d=docs[name];items=bodies(d)
 assert d['layers'][:2]==docs['pad20']['layers'][:2]
 if i>=2:assert items[:-1]==bodies(docs[stages[i-1]])
 if i==1:assert items[0]==bodies(docs['pad20'])[0] and items[1]['id']==bodies(docs['pad20'])[1]['id']
 expected=copy.deepcopy(original)
 if i:expected['config.scad']=b'width=24;\ndepth=12;\nheight=6;\n'
 if i>=5:expected.update(extra);expected['font.scad']=courier_code
 if i>=6:expected['mcad.scad']=mcad_code
 assert source_files(items[-1])==expected,(name,set(source_files(items[-1]))^set(expected))
final=docs['heightmap'];assert final==doc('reopened')
edited=doc('pad28');undone=doc('pad28-undone');redone=doc('pad28-redone')
assert bodies(undone)==bodies(final) and bodies(edited)==bodies(redone)
for i,(a,b) in enumerate(zip(bodies(final),bodies(edited))):
 if i!=1:assert a==b
 else:
  expected=source_files(a);expected['config.scad']=b'width=28;\ndepth=12;\nheight=6;\n'
  assert source_files(b)==expected and a['id']==b['id'] and b['name']=='Folder pad 28'
for d in [edited,undone,redone]:assert d['layers'][:2]==final['layers'][:2]
assert retain('config.scad')==b'width=24;\ndepth=12;\nheight=6;\n'
assert retain('config (1).scad')==b'width=28;\ndepth=12;\nheight=6;\n'
def stl(name):
 data=retain('mouse-audit-folder-'+name+'-3d-mm.stl');n=struct.unpack_from('<I',data,80)[0]
 assert len(data)==84+n*50;edges=Counter();directions=Counter();volume=0;points=[]
 for i in range(n):
  a,b,c=[struct.unpack_from('<3f',data,96+50*i+j*12) for j in range(3)];points.extend([a,b,c])
  volume+=sum(a[j]*(b[(j+1)%3]*c[(j+2)%3]-b[(j+2)%3]*c[(j+1)%3]) for j in range(3))/6
  for start,end in [(a,b),(b,c),(c,a)]:
   edge=tuple(sorted([start,end]));edges[edge]+=1;directions[edge]+=1 if start<end else -1
 assert all(v==2 for v in edges.values()) and not any(directions.values()) and volume>0
 size=[max(p[j] for p in points)-min(p[j] for p in points) for j in range(3)]
 return {'triangles':n,'closed_outward':True,'size_mm':size,'volume_mm3':volume}
meshes={name:stl(name) for name in stages+['pad28-redone']}
hole_area=128*math.sin(2*math.pi/64)
for name,width in [('pad20',20),('pad24',24),('alternate34',34),('pad28-redone',28)]:
 m=meshes[name];assert m['size_mm']==[width,12,6] and abs(m['volume_mm3']-6*(12*width-hole_area))<.00001
assert meshes['assets']['size_mm']==[30,12,4] and meshes['assets']['volume_mm3']==24+(20*12-4*4)*4
assert meshes['heightmap']['size_mm']==[2,2,5] and abs(meshes['heightmap']['volume_mm3']-8)<1e-10
assert meshes['mcad']['size_mm']==[20,12,6] and abs(meshes['mcad']['volume_mm3']-6*(236+32*math.sin(2*math.pi/64)))<.00001
# Independent TrueType quadratic outlines and advance metrics, not app fonts.
font_oracles={}
for name,path in [('font-noto',fixture/'code-folder/assets/NotoSans-Regular.ttf'),('font-courier',fixture/'code-additions/AuditCourier.ttf')]:
 font=TTFont(path);glyphs=font.getGlyphSet();cmap=font.getBestCmap();x=0;area=0;bounds=[]
 for char in 'Aa':
  glyph=cmap[ord(char)];bp=BoundsPen(glyphs);glyphs[glyph].draw(bp);ap=AreaPen(glyphs);glyphs[glyph].draw(ap)
  a,b,c,d=bp.bounds;bounds.append((a+x,b,c+x,d));area+=abs(ap.value);x+=font['hmtx'].metrics[glyph][0]
 scale=10*(100/72)/font['head'].unitsPerEm
 size=[(max(b[2] for b in bounds)-min(b[0] for b in bounds))*scale,(max(b[3] for b in bounds)-min(b[1] for b in bounds))*scale,2]
 volume=area*scale**2*2;measured=meshes[name]
 assert max(abs(v-w) for v,w in zip(size,measured['size_mm']))<.001
 assert abs(volume-measured['volume_mm3'])<.15 # Native curved glyphs are polygonal.
 font_oracles[name]={'true_outline_size_mm':size,'quadratic_outline_volume_mm3':volume,'polygonal_volume_error_mm3':volume-measured['volume_mm3'],'allowed_polygonal_volume_error_mm3':.15}
report={'native_folder_and_additional_files_preserve_all_dependency_bytes':True,
 'entry_independent_of_open_helper_and_nested_paths_work':True,'same_path_helper_replacement_updates_only_target_model':True,
 'whole_native_reopen_exact':True,'source_and_geometry_undo_redo_exact':True,
 'native_save_scad_exports_open_helper_not_entry':True,'all_neighbour_models_and_non_cad_layers_retained':True,
 'independent_stl_oracles':meshes,'independent_true_type_oracles':font_oracles,'sha256':hashes}
(out/'code-folder-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['sha256','independent_stl_oracles','independent_true_type_oracles']},indent=2))
