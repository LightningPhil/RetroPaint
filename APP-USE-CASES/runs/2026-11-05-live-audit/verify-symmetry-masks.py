"""Independent raster oracle for native mask boundaries, fills and sector changes."""
from pathlib import Path
import base64,copy,hashlib,io,json,math
import numpy as np
from PIL import Image
from shape_oracle import path_distances
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
def doc(i):return json.loads(retain('mouse-audit-mask227'+(f' ({i})'if i else '')+'.retropaint'))
def pixels(d):return np.array(Image.open(io.BytesIO(base64.b64decode(d['layers'][0]['image'].split(',')[1]))).convert('RGBA')).reshape(-1,4)
def group(mode):
 if mode=='v':return [np.eye(2),np.diag([-1,1])]
 if mode=='h':return [np.eye(2),np.diag([1,-1])]
 result=[]
 for k in range(int(mode)//2):
  a=4*math.pi*k/int(mode);r=np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]]);result.extend([r,r@np.diag([1,-1])])
 return result
def transformed(p,matrices):return [(np.array(p)-[480,320])@m.T+[480,320]for m in matrices]
yy,xx=np.mgrid[:640,:960];points=np.column_stack([xx.ravel()+.5,yy.ravel()+.5]);blue=[30,136,229,255];red=[229,57,53,255];green=[67,160,71,255]
def colour_equal(pixels,colour):return np.all(np.abs(pixels.astype(int)-colour)<=1) # Raster rotation/resampling rounds RGB by at most1channel level.
def distances(lines):return np.min([path_distances(points,line)for line in lines],axis=0)
def rectangle_inside(matrices):
 interior=np.zeros(len(points),dtype=bool);deep=interior.copy();near=interior.copy()
 for m in matrices:
  p=(points-[480,320])@m+[480,320];inside=(p[:,0]>580)&(p[:,0]<620)&(p[:,1]>340)&(p[:,1]<355);interior|=inside;deep|=(p[:,0]>583)&(p[:,0]<617)&(p[:,1]>343)&(p[:,1]<352);near|=(p[:,0]>577)&(p[:,0]<623)&(p[:,1]>337)&(p[:,1]<358)
 return interior,deep,near
base=doc(1);assert base['drawingMode']=='raster'and np.all(pixels(base)==255);results=[]
for j,mode in enumerate(['v','h','4','6','8','10','12']):
 ds=[doc(i)for i in range(2+7*j,9+7*j)];line,outline,filled,undo,redo,changed,off=map(pixels,ds);assert ds[1]==ds[3]and ds[2]==ds[4]
 for d in ds:
  a=copy.deepcopy(d);b=copy.deepcopy(base);a['layers'][0].pop('image');b['layers'][0].pop('image');assert a==b
 matrices=group(mode)
 # Exterior3.5px allows1.5px half-stroke, antialiasing and a rotated-raster resampling footprint.
 # Analytic segment intersection with the selected half-plane: all outside travel is discarded.
 segment=[[500,420],[480,420+20*20/70]]if mode=='v'else[[580,340],[580+40/3,320]]
 # A slanted clipping boundary has partial coverage even on the stroke centreline.
 # Exclude its2.5px band from solid-colour assertions, retaining the full exterior check.
 if mode=='v':seam=np.abs(points[:,0]-480)
 elif mode=='h':seam=np.abs(points[:,1]-320)
 else:
  angles=np.arange(int(mode))*2*math.pi/int(mode);seam=np.min([np.abs((points-[480,320])@np.array([-math.sin(a),math.cos(a)]))for a in angles],axis=0)
 line_distance=distances(transformed(segment,matrices));safe=line_distance>3.5;core=(line_distance<.4)&(seam>2.5);assert np.all(line[safe]==255);assert colour_equal(line[core],blue)
 rectangle=np.array([[580,340],[620,340],[620,355],[580,355],[580,340]]);rect_distance=distances(transformed(rectangle,matrices));edges=np.minimum(line_distance,rect_distance);assert np.all(outline[edges>3.5]==255);assert colour_equal(outline[(edges<.4)&(seam>2.5)],blue)
 interior,deep,near=rectangle_inside(matrices);assert colour_equal(filled[deep],red);assert np.array_equal(filled[~near],outline[~near]);assert np.all(filled[(edges>3.5)&~interior]==255)
 # Sector1 is chosen explicitly; this motif lies wholly inside it.
 n=2 if mode in ['v','h']else int(mode);sector=2*math.pi/n;offset=-math.pi/2 if mode=='v'else 0
 p=lambda r,a:[480+r*math.cos(a),320+r*math.sin(a)]
 green_segments=transformed([p(200,offset+1.3*sector),p(170,offset+1.5*sector)],matrices);gd=distances(green_segments);assert np.array_equal(changed[gd>3.5],filled[gd>3.5]);assert colour_equal(changed[gd<.4],green)
 ordinary=np.array([[800,500],[880,510]])if mode=='h'else np.array([[800,100],[880,110]]);od=path_distances(points,ordinary);assert np.array_equal(off[od>2.5],changed[od>2.5]);assert colour_equal(off[od<.4],green)
 for k,expected in enumerate([filled,changed,off]):
  idx=3*j+k;name='mouse-audit-mask227'+(f' ({idx})'if idx else '')+'.png';retain(name);assert np.array_equal(np.array(Image.open(out/name).convert('RGBA')).reshape(-1,4),expected)
 results.append(dict(mode=mode,working_boundary_clips_without_teleport=True,all_enclosure_fills_red=True,fill_undo_redo_exact=True,changed_sector_all_green_copies=True,symmetry_off_one_mark_only=True,earlier_pixels_preserved=True,all3pngs_equal_saved_raster=True))
assert doc(50)==doc(51);retain('mouse-audit-mask227 (21).png');assert np.array_equal(np.array(Image.open(out/'mouse-audit-mask227 (20).png')),np.array(Image.open(out/'mouse-audit-mask227 (21).png')))
report=dict(status='Pass',case='PLAY-013',modes=results,final_actual_project_reopen_exact=True,final_reopened_png_exact=True,hashes=hashes)
(out/'mask227-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items()if k!='hashes'},indent=2))
