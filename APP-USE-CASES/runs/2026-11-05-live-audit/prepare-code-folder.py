"""Independent local source/dependency/assets fixture for native folder chooser."""
import hashlib,json,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/fixtures/code-folder'
files={
'main.scad':'include <config.scad>\nuse <lib/pad.scad>\n// Native folder audit: centred D4 through hole.\npad(width,depth,height);\n',
'config.scad':'width=20;\ndepth=12;\nheight=6;\n',
'lib/pad.scad':'use <sub/drill.scad>\nmodule pad(w,d,h){difference(){cube([w,d,h]);translate([w/2,d/2,-1])drill(h+2);}}\n',
'lib/sub/drill.scad':'module drill(h){cylinder(d=4,h=h,$fn=64);}\n',
'alternate.scad':'include <config.scad>\nuse <lib/pad.scad>\npad(width+10,depth,height);\n',
'assets.scad':'translate([0,0,0])import("assets/box.stl");\ntranslate([10,0,0])linear_extrude(4)import("assets/outline.svg");\n',
'font.scad':'linear_extrude(2)text("Aa",size=10,font="Noto Sans");\n',
'mcad.scad':'use <MCAD/boxes.scad>\nroundedBox([20,12,6],1,true);\n',
'assets/outline.svg':'<svg xmlns="http://www.w3.org/2000/svg" width="20mm" height="12mm" viewBox="0 0 20 12"><path d="M0 0H20V12H0Z M8 4V8H12V4Z" fill-rule="evenodd"/></svg>\n',
}
points=[(0,0,0),(2,0,0),(2,3,0),(0,3,0),(0,0,4),(2,0,4),(2,3,4),(0,3,4)]
faces=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
stl='solid box\n'
for face in faces:
 stl+='facet normal 0 0 0\nouter loop\n'+''.join('vertex %s %s %s\n'%points[i] for i in face)+'endloop\nendfacet\n'
files['assets/box.stl']=stl+'endsolid box\n'
for name,text in files.items():
 p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8',newline='\n')
font=root/'test-results/audit-2026-11-05/production-seven-fixes/openscad/NotoSans-Regular.ttf'
shutil.copyfile(font,out/'assets/NotoSans-Regular.ttf')
manifest={str(p.relative_to(out)).replace('\\','/'):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.rglob('*')) if p.is_file()}
(out.parent/'code-folder-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'folder':str(out),'files':len(manifest),'bytes':sum(v['bytes'] for v in manifest.values())}))
