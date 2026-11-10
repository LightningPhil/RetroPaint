"""Decode actual native-workflow outputs and measure screen grid boundaries."""
import base64,hashlib,io,json,math,statistics
from pathlib import Path
from PIL import Image,ImageChops
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
fixture=Image.open(root/'APP-USE-CASES/runs/2026-10-19-full-audit/fixtures/PIXEL.png').convert('RGBA')
e=json.loads((out/'pixel-overlay-evidence.json').read_bytes())
def actual(stem,ext):
 name=stem+'.'+ext;data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(stem):return json.loads(actual('mouse-audit-pixel-overlay-'+stem,'retropaint'))
def image(stem):return Image.open(io.BytesIO(actual('mouse-audit-pixel-overlay-'+stem,'png'))).convert('RGBA')
def source(d):return Image.open(io.BytesIO(base64.b64decode(d['layers'][0]['image'].split(',',1)[1]))).convert('RGBA')
def equal(a,b):return a.size==b.size and a.tobytes()==b.tobytes()
before=doc('before');assert equal(source(before),fixture) and equal(image('before'),fixture)
assert doc('guides-before-fix')==before and equal(image('guides-before-fix'),fixture)
resized=doc('resized');expected=source(resized);assert expected.size==(64,48)
# Canvas and Pillow resolve exact halfway ties differently at the 1.5x Y
# scale. Check elementary nearest-neighbour sampling, permitting either
# equally distant source pixel only at an exact tie, never blended colours.
def nearest(value,limit):
 indices={min(limit-1,math.floor(value))}
 if math.isclose(value,round(value),abs_tol=1e-10) and value>0:indices.add(int(round(value))-1)
 return indices
for y in range(48):
 for x in range(64):
  allowed={fixture.getpixel((xx,yy)) for xx in nearest((x+.5)*32/64,32) for yy in nearest((y+.5)*32/48,32)}
  assert expected.getpixel((x,y)) in allowed,(x,y,'Not nearest-neighbour source sampling')
assert equal(image('resized'),expected)
assert doc('resized-undone')==before and doc('resized-redone')==resized and doc('resized-reopened')==resized
assert equal(image('resized-reopened'),expected)
def grid_contrasts(screen,row,original):
 p=row['paper'];g=row['guide']['rect'];sx=p['width']/original.width;sy=p['height']/original.height;gray=screen.convert('L');values=[]
 for y in range(original.height):
  cy=p['y']+(y+.5)*sy
  if not max(g['y']+3,p['y']+21)<=cy<g['y']+g['height']-3:continue
  for x in range(1,original.width):
   if original.getpixel((x-1,y))!=(255,255,255,255) or original.getpixel((x,y))!=(255,255,255,255):continue
   boundary=p['x']+x*sx;middle=boundary+sx/2
   if not max(g['x']+3,p['x']+21)<=boundary<middle<g['x']+g['width']-3:continue
   if any(r['x']-3<=xx<=r['x']+r['width']+3 and r['y']-3<=cy<=r['y']+r['height']+3 for r in row.get('exclusions',[]) for xx in [boundary,middle]):continue
   yy=round(cy);xx=round(boundary);mm=round(middle)
   edge=min(gray.getpixel((xx+delta,yy)) for delta in [-1,0,1]);centre=gray.getpixel((mm,yy));values.append(centre-edge)
 return values
results=[]
for row in e['rows']:
 label=row['label'];d=doc(label);assert d==(before if row['source']==[32,32] else resized)
 original=fixture if row['source']==[32,32] else expected;assert equal(image(label),original)
 g=row['guide'];assert g and not g['hidden'];assert g['size'][0]<=math.ceil(row['window'][0]*row['dpr']) and g['size'][1]<=math.ceil(row['window'][1]*row['dpr'])
 screen=Image.open(out/row.get('screenshot',f'pixel-overlay-{label}.png')).convert('RGB')
 # Chrome's 110% viewport emulation rounds screenshot edges independently
 # of innerWidth/innerHeight. Retain actual sizes; the edge differs by <=1px.
 assert all(abs(a-b)<=1 for a,b in zip(screen.size,row['window'])),(label,screen.size,row['window'])
 scale=row['paper']['width']/row['source'][0]
 if scale>=6:
  contrasts=grid_contrasts(screen,row,original);assert contrasts,(label,'No visible white-cell boundaries')
  fraction=sum(v>=3 for v in contrasts)/len(contrasts);assert fraction>.9,(label,fraction,contrasts[:20])
  assert statistics.median(contrasts)>=5,(label,statistics.median(contrasts))
  results.append({'label':label,'visible_white_cell_boundaries':len(contrasts),'fraction_aligned':fraction,'median_grid_contrast':statistics.median(contrasts),'export_source_exact':True})
 else:results.append({'label':label,'below_six_css_pixel_grid_threshold':True,'export_source_exact':True})
fit=next(row for row in e['rows'] if row['label']=='fit')
bad=grid_contrasts(Image.open(out/'pixel-overlay-before-fix.png').convert('RGB'),fit,fixture)
assert sum(v>=3 for v in bad)/len(bad)<.2,'Pre-fix fixture no longer reproduces missing grid'
assert next(row for row in e['rows'] if row['label']=='actual')['readout'].endswith('100%')
assert {tuple(row['window']) for row in e['rows']}>={(320,568),(390,844),(844,390),(1280,720),(2560,1215)}
maxrow=next(row for row in e['rows'] if row['label']=='maximum');panrow=next(row for row in e['rows'] if row['label']=='maximum-panned')
assert abs(panrow['paper']['x']-maxrow['paper']['x']+150)<.01 and abs(panrow['paper']['y']-maxrow['paper']['y']-100)<.01
assert maxrow['paper']['width']>14000 and maxrow['guide']['size'][0]<4000
report={'status':'Pass','live_defect':'LIVE-029','all_five_required_viewports':True,'native_max_zoom_pan_delta':[-150,100],'maximum_paper_width_css':maxrow['paper']['width'],'backing_store_bounded_to_visible_viewport':True,'view_only_projects_and_exported_pixels_exact':True,'independent_nearest_neighbour_resize_and_whole_history_native_reopen_exact':True,'pre_fix_aligned_fraction':sum(v>=3 for v in bad)/len(bad),'rows':results,'sha256':hashes}
(out/'pixel-overlays-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['sha256','rows']},indent=2))
