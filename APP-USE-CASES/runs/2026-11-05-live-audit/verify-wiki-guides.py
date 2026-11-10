"""Independent oracles for actual native wiki and guided-exercise worker output.

The disposable harness observes standard Worker input/output, retaining genuine
binary STL bytes. It does not read application state or manufacture geometry.
Dimensions/volumes below are independently calculated from each printed recipe.
"""
import base64,hashlib,json,math,struct,sys
from collections import Counter,defaultdict
from pathlib import Path
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse'
sys.path.insert(0,str(out.parent/'python-libs'))
from fontTools.ttLib import TTFont
from fontTools.pens.areaPen import AreaPen
plans=json.loads((out/'wiki-guided-plans.json').read_bytes())
live=json.loads((out/'wiki-guided-live-evidence.json').read_bytes())
raw=(Path.home()/'Downloads/mouse-audit-wiki-engine-evidence.json').read_bytes()
(out/'mouse-audit-wiki-engine-evidence.json').write_bytes(raw);engine=json.loads(raw)
assert len(plans)==len(live)==70
C=lambda n:n/2*math.sin(2*math.pi/n)
font=TTFont(root/'public/openscad/NotoSans-Regular.ttf');glyphs=font.getGlyphSet()
def text_area(text,size):
 area=0
 for char in text:
  pen=AreaPen(glyphs);glyphs[font.getBestCmap()[ord(char)]].draw(pen);area+=abs(pen.value)
 return area*(size*100/72/font['head'].unitsPerEm)**2
def parse(data):
 n=struct.unpack_from('<I',data,80)[0];assert len(data)==84+n*50
 points=[];edges=Counter();directions=Counter();adj=defaultdict(set);volume=0;tris=[];axis_degenerates=0
 for i in range(n):
  normal=struct.unpack_from('<3f',data,84+50*i)
  a,b,c=[struct.unpack_from('<3f',data,96+50*i+12*j) for j in range(3)]
  # Native rotate_extrude emits repeated vertices on the rotation axis.
  # These have zero surface area; the app's STL importer also removes them.
  if len({a,b,c})<3:
   assert all(p[0]==0 and p[1]==0 for p in [a,b,c] if [a,b,c].count(p)>1)
   axis_degenerates+=1;continue
  points.extend((a,b,c));tris.append((a,b,c))
  u=[b[j]-a[j] for j in range(3)];v=[c[j]-a[j] for j in range(3)]
  cross=[u[(j+1)%3]*v[(j+2)%3]-u[(j+2)%3]*v[(j+1)%3] for j in range(3)]
  length=math.sqrt(sum(x*x for x in cross));assert length>1e-12
  assert abs(sum(x*x for x in normal)-1)<1e-5
  assert sum(x*y for x,y in zip(normal,cross))/length>.99999
  volume+=sum(a[j]*(b[(j+1)%3]*c[(j+2)%3]-b[(j+2)%3]*c[(j+1)%3]) for j in range(3))/6
  for start,end in [(a,b),(b,c),(c,a)]:
   edge=tuple(sorted((start,end)));edges[edge]+=1;directions[edge]+=1 if start<end else -1;adj[start].add(end);adj[end].add(start)
 assert all(v==2 for v in edges.values()) and not any(directions.values())
 unseen=set(adj);components=[]
 while unseen:
  todo=[next(iter(unseen))];group=set()
  while todo:
   p=todo.pop()
   if p in group:continue
   group.add(p);todo.extend(adj[p]-group)
  unseen-=group;components.append(group)
 assert volume>0
 lo=[min(p[j] for p in points) for j in range(3)];hi=[max(p[j] for p in points) for j in range(3)]
 return {'raw_triangles':n,'triangles':len(tris),'zero_area_rotation_axis_triangles_omitted':axis_degenerates,'size_mm':[b-a for a,b in zip(lo,hi)],'min_mm':lo,'max_mm':hi,'volume_mm3':volume,'components':len(components)},tris,components
def near(actual,expected,tol=.003):assert abs(actual-expected)<tol,(actual,expected,tol)
def size(m,wanted,tol=.003):
 for a,b in zip(m['size_mm'],wanted):near(a,b,tol)
def vol(m,wanted,tol=.03):near(m['volume_mm3'],wanted,tol)
def polygon_area(points):return abs(sum(p[0]*points[(i+1)%len(points)][1]-p[1]*points[(i+1)%len(points)][0] for i,p in enumerate(points)))/2
def inside(p,tris):
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
def probes(t,items):
 for point,wanted in items:assert inside(point,t)==wanted,(point,wanted)
report=[]
for plan,entry in zip(plans,live):
 i=plan['index'];assert entry['index']==i and entry['title']==plan['title']
 assert entry['copiedExact'] and entry['draftPreserved'] and entry['originalStatus'].startswith('Ready')
 assert entry['variant']['source']==plan['variant']
 pair=[];triangles=[]
 for changed,source in [(False,plan['code']),(True,plan['variant'])]:
  matches=[e for e in engine if e.get('input',{}).get('source')==source]
  assert matches,(i,changed,'No genuine worker result')
  if i==55 and changed:
   assert any('Wall must fit' in e.get('error','') for e in matches);assert entry['variant']['addDisabled'];continue
  e=next(e for e in matches if e.get('stl') and e['input']['label']==(f'Wiki {i:02} variation' if changed else plan['title']));data=base64.b64decode(e['stl'])
  expected_files=plan.get('files',{})
  if not changed:
   assert {f['path']:base64.b64decode(f['data']).decode() for f in e['input']['files']}==expected_files
  else:
   supplied={f['path']:base64.b64decode(f['data']).decode() for f in e['input']['files']}
   for name,text in expected_files.items():assert supplied[name]==text
  name=f'wiki-guide-{i:02}-'+('variant.stl' if changed else 'baseline.stl');(out/name).write_bytes(data)
  m,t,components=parse(data);pair.append(m);triangles.append(t)
  if i==1:
   r=6 if changed else 4;size(m,[30,20,8]);vol(m,4800-C(48)*r*r*8)
   probes(t,[([15,10.13,4.31],False),([1,1.13,4.31],True),([20,10.13,4.31],not changed)])
  elif i==2:
   h=20 if changed else 12;size(m,[8,8,h]);vol(m,C(32)*16*h)
  elif i==3:
   h=12 if changed else 8;size(m,[30,20,h+5]);vol(m,3000+C(40)*25*h)
  elif i==4:
   size(m,[30,18,6]);vol(m,3240);assert m['min_mm']==([0,0,0] if changed else [-15,-9,-3])
  elif i==5:size(m,[30,20,20 if changed else 14],.07)
  elif i==6:
   r=12 if changed else 8;size(m,[24,24,20]);vol(m,C(48)*(20/3*(144+12*r+r*r)-25*20))
  elif i==7:
   h=28 if changed else 18;size(m,[20,20,h]);vol(m,400*h/3)
  elif i==8:
   h=8 if changed else 4;size(m,[30,18,h]);vol(m,540*h)
  elif i==9:
   n=8 if changed else 6;size(m,[20,20 if changed else 20*math.sin(math.pi/3),6]);vol(m,(C(n)*100-C(40)*16)*6)
  elif i==10:
   h=10 if changed else 5;size(m,[12*(1+math.cos(math.pi/5)),24*math.sin(2*math.pi/5),h]);vol(m,C(5)*144*h)
  elif i==11:
   size(m,[36,18,4.5]);vol(m,1944+1.5*text_area('LID' if changed else 'BOX',8),.3)
  elif i==12:size(m,[20,20,3] if changed else [16,16,3],.15)
  elif i==13:
   near(m['size_mm'][2],30);expected=96*30*(1+.65+.65**2)/3;vol(m,expected,expected*.02)
   if changed:size(m,[12,8,30])
  elif i==14:
   size(m,[50,50,24]);segments=48 if changed else 64;vol(m,segments/2*math.sin(2*math.pi/64)*2924,.04)
  elif i==15:
   r=22 if changed else 16;size(m,[2*(r+3),2*(r+3),6]);vol(m,64*math.sin(2*math.pi/64)*r*C(24)*9,.04)
  elif i==16:
   r=8 if changed else 6;size(m,[30,20,12.9]);vol(m,3000+C(40)*r*r*7.9)
  elif i==17:
   w=8 if changed else 12;size(m,[40,24,8]);vol(m,7680-C(40)*16*8-w*8*8)
  elif i==18:
   size(m,[18,18,18]);probes(t,[([.13,.17,.31],True),([8.9,8.9,.31],changed)])
  elif i==19:
   near(m['size_mm'][2],8)
   if not changed:size(m,[32/math.sqrt(3),16,8]);vol(m,6*64*math.tan(math.pi/6)*8)
   else:size(m,[30,30*math.sin(math.pi/3)+8,8])
  elif i==20:
   d=18 if changed else 12;size(m,[2*d+12,12,5]);vol(m,(2*d*12+C(32)*36)*5)
  elif i==21:size(m,[28,18,8] if changed else [30,20,10],.025)
  elif i==22:
   size(m,[44 if changed else 32,8,12]);vol(m,2*C(32)*16*12);assert m['components']==2
  elif i==23:
   size(m,[22,18,18]);vol(m,22*18*18-C(40)*25*(18 if changed else 22))
   probes(t,[([0,.17,.31],False),([8,.17,.31],changed),([.13,7,.31],not changed)])
  elif i==24:
   s=1 if changed else 1.6;size(m,[20*s,20,6]);vol(m,C(48)*100*6*s)
  elif i==25:
   s=40 if changed else 30;size(m,[s,s,s]);assert m['components']==1
  elif i==26:
   gap=5 if changed else 3;size(m,[2*(gap+12),8,4]);vol(m,768);assert m['components']==2
   probes(t,[([0,3.17,2.31],False),([4,3.17,2.31],not changed),([6,3.17,2.31],True)])
  elif i==27:
   shift=4 if changed else 8;size(m,[15+shift,12,20]);vol(m,3600)
   near(min(p[0] for group in components for p in group if p[2]==20),shift)
  elif i==28:size(m,[20,12,6]);vol(m,1440)
  elif i==29:
   size(m,[24,24,3]);vol(m,(C(48)*144-(C(32)*25 if changed else 0))*3)
   probes(t,[([.13,.17,1.31],not changed),([10,.17,1.31],True)])
  elif i==30:
   h=8 if changed else 5;size(m,[30,20,h]);area=(24*14+2*3*(24+14)+math.pi*9)-(22*12+2*(22+12)+math.pi)
   vol(m,area*h,area*h*.006);probes(t,[([.13,.17,2.31],False),([14,.17,2.31],True)])
  elif i==31:
   n=8 if changed else 16;size(m,[66,18,6]);vol(m,6*81*(C(6)+C(n)+C(48)));assert m['components']==3
  elif i==32:
   w=40 if changed else 32;size(m,[w,w*.6,5]);vol(m,w*w*.6*5)
  elif i==33:
   w=18 if changed else 32;size(m,[w,w/2,4]);vol(m,w*w*2)
  elif i==34:
   heights=[8,12,18]+([24] if changed else []);size(m,[50 if changed else 36,8,max(heights)]);vol(m,C(24)*16*sum(heights));assert m['components']==len(heights)
  elif i==35:
   r=3 if changed else 2.5;size(m,[48,48,6]);vol(m,6*(C(64)*576-6*C(24)*r*r))
  elif i==36:
   size(m,[24,24,6]);vol(m,3456-(0 if changed else C(32)*16*6));probes(t,[([.13,.17,.31],changed),([10,.17,.31],True)])
  elif i==37:
   step=2 if changed else 4;size(m,[41.5,7,6+3*step]);vol(m,C(24)*sum((2+j/2)**2*(6+j*step) for j in range(4)));assert m['components']==4
  elif i==38:
   inner=5 if changed else 4;size(m,[12,12,18]);vol(m,C(32)*(36-inner**2)*18);probes(t,[([.13,.17,8.31],False),([4.5,.17,8.31],not changed),([5.5,.17,8.31],True)])
  elif i==39:
   n=8 if changed else 6;size(m,[34,34 if changed else 2*(14*math.sin(math.pi/3)+3),6]);vol(m,n*C(24)*9*6);assert m['components']==n
  elif i==40:
   inner=10 if changed else 7;poly=[[(14 if j%2==0 else inner)*math.cos(j*math.pi/5),(14 if j%2==0 else inner)*math.sin(j*math.pi/5)] for j in range(10)]
   vol(m,polygon_area(poly)*5);size(m,[max(p[0] for p in poly)-min(p[0] for p in poly),max(p[1] for p in poly)-min(p[1] for p in poly),5])
  elif i==41:
   angles=[a for a in range(0,360,30) if changed or a not in [90,270]];poly=[[12*math.cos(math.radians(a)),12*math.sin(math.radians(a))] for a in angles]
   size(m,[24,24 if changed else 24*math.sin(math.pi/3),4]);vol(m,polygon_area(poly)*4)
  elif i==42:
   w=2 if changed else 4;size(m,[24,18,10]);vol(m,4320-(24-2*w)*(18-2*w)*(10-w))
  elif i==43:
   rise=30*math.tan(math.radians(40 if changed else 25));size(m,[30,rise,10]);vol(m,150*rise)
  elif i in [44,46]:
   by=20 if i==46 and changed else 12;length=math.hypot(20,by);angle=math.atan2(by,20)
   size(m,[20+4*math.sin(angle),by+4*math.cos(angle),4]);vol(m,length*16)
   if i==44:near(m['min_mm'][1],-12 if changed else 0)
  elif i==45:
   n=5 if changed else 3;size(m,[12*(n-1)+6,6,8]);vol(m,n*6*6*8);assert m['components']==n
  elif i==47:
   a=math.radians(60 if changed else 30);size(m,[18*math.sin(a)+8*math.cos(a),8,18*math.cos(a)+8*math.sin(a)]);vol(m,C(32)*16*18)
  elif i==48:
   assert m['components']==5;size(m,[46,6,m['size_mm'][2]])
   heights=[]
   for group in components:
    near(max(p[0] for p in group)-min(p[0] for p in group),6)
    height=max(p[2] for p in group);assert 6<=height<=18;heights.append(height)
   vol(m,C(20)*9*sum(heights))
  elif i==49:
   tip=18 if changed else 12;size(m,[12+tip,16,4]);vol(m,(192+tip*8)*4)
  elif i==50:
   mid=16 if changed else 12;size(m,[2*mid,2*mid,20]);vol(m,C(48)*10/3*(64+8*mid+mid**2+mid**2+6*mid+36))
  elif i==51:
   r=7 if changed else 5;size(m,[2*r,2*r,8]);vol(m,C(32)*r*r*8)
  elif i==52:
   near(m['size_mm'][2],2);vol(m,2*text_area('M8' if changed else 'M6',12),.35);assert m['components']==2
  elif i==53:
   w=30 if changed else 20;size(m,[w,12,5]);vol(m,w*60)
  elif i==54:
   near(m['size_mm'][2],3.1);assert m['components']==1
   assert m['size_mm'][0]>40 if changed else m['size_mm'][0]>30
  elif i==55:size(m,[24,24,12]);vol(m,24*24*12-18*18*9)
  elif i==56:
   r=10 if changed else 8;size(m,[2*r,2*r,6]);vol(m,C(32)*r*r*6)
  elif i==57:
   size(m,[32,12,100 if changed else 8]);vol(m,C(32)*76/3*(108 if changed else 16));assert m['components']==2
  elif i==58:
   h=8 if changed else 4;size(m,[24,16,h]);vol(m,320*h);probes(t,[([12,8.17,h/2],False),([2,2.17,h/2],True)])
  elif i==59:
   scale=4 if changed else 2;near(m['size_mm'][0],18);near(m['size_mm'][1],18);near(m['max_mm'][2],5*scale)
   # Independently supplied 4x4 DAT grid: peak sample at x=2,y=2.
   assert any(abs(p[0]-3)<.001 and abs(p[1]-3)<.001 and abs(p[2]-5*scale)<.001 for group in components for p in group)
  elif i==60:
   h=8 if changed else 4;size(m,[16,12,h]);vol(m,192*h);assert any('ECHO:' in line for line in e['logs'])
  elif i==61:
   a=math.radians(90 if changed else 25);size(m,[30*abs(math.cos(a))+8*abs(math.sin(a)),30*abs(math.sin(a))+8*abs(math.cos(a)),5]);vol(m,1200)
  elif i==62:
   h=16 if changed else 10;size(m,[24,20,h]);vol(m,240*h)
  elif i==63:
   n=8 if changed else 6;size(m,[56,56,6]);vol(m,C(48)*(784-49-n*6.25)*6,.05)
  elif i==64:
   w=3 if changed else 2;size(m,[40,28,18]);vol(m,40*28*18-(40-2*w)*(28-2*w)*(18-w))
  elif i==65:
   depth=2 if changed else 3;size(m,[44,28,16]);vol(m,44*28*6+C(40)*49*10-18*20*depth-C(32)*9*16)
   probes(t,[([10,10.17,3.5],changed),([32,14.17,8.31],False),([37,14.17,8.31],True)])
  elif i==66:
   size(m,[40,24,8],.04);probes(t,[([14.5,.17,.31],changed),([7.5,.17,.31],not changed)])
  elif i==67:
   inner=14 if changed else 15;size(m,[36,36,24]);vol(m,C(64)*(324*24-inner**2*21))
   probes(t,[([.13,.17,1.31],True),([.13,.17,5.31],False),([14.5,.17,5.31],changed)])
  elif i==68:
   size(m,[52,20,4]);vol(m,4160-(.6 if changed else 1.2)*text_area('PART 1',9),.3)
  elif i==69:
   # The unchanged bundled helper uses default $fa=12/$fs=2. Radius3
   # therefore has ceil(min(360/12,2*pi*3/2))=10 facets. Its Y and
   # sphere-pole extrema lie at cos(18deg), inside the ideal radius.
   inset=6*(1-math.cos(math.pi/10));size(m,[30,20-inset,8-inset if changed else 8])
  elif i==70:
   size(m,[20,20,8]);radius=(15 if changed else 11.5)/2+.0001
   rim=[p for group in components for p in group if abs(p[2]-4)<.0001 and abs(p[0])<9 and abs(p[1])<9]
   near(max(p[0] for p in rim),radius);near(min(p[0] for p in rim),-radius)
   near(max(p[1] for p in rim),radius*math.sin(math.pi/3))
   probes(t,[([.13,.17,3.5],False),([6.5,.17,3.5],not changed),([.13,.17,-3.5],True)])
  else:raise AssertionError('Missing independent oracle')
 if len(pair)==2:
  a,b=pair
  if i in [5,12,18,19,25,34,40,41,45,54,63,65,68]:
   assert b['volume_mm3']>a['volume_mm3'] if i!=63 else b['volume_mm3']<a['volume_mm3']
  if i in [21,42,69,70]:assert b['volume_mm3']<a['volume_mm3']
  if i in [22,27,28,44,47,66]:near(a['volume_mm3'],b['volume_mm3'],.03)
  if i==30:near(b['volume_mm3']/a['volume_mm3'],8/5,.00001)
  if i==59:near(b['volume_mm3']/a['volume_mm3'],2,.00001)
  if i==48:assert a['volume_mm3']!=b['volume_mm3']
 report.append({'index':i,'title':plan['title'],'baseline':pair[0],'variation':pair[1] if len(pair)>1 else {'expected_assertion':True}})
extras=json.loads((out/'wiki-guide-extras.json').read_bytes())
assert len(extras)==5
for extra in extras:
 matching=[e for e in engine if e.get('input',{}).get('label')==extra['label'] and e['input']['source']==extra['source']]
 assert matching
 if extra['label']=='Wiki checked negative':
  assert not extra['addEnabled'] and 'Width must be positive' in extra['status']
  assert 'Width must be positive' in matching[0]['error'];continue
 assert extra['addEnabled']
 mesh,_,_=parse(base64.b64decode(matching[0]['stl']))
 if extra['label']=='Wiki clamp minimum':size(mesh,[24,18,10]);vol(mesh,4320-22*16*9)
 elif extra['label']=='Wiki checked recovered':size(mesh,[30,12,5]);vol(mesh,1800)
 elif extra['label']=='Wiki wall restored':size(mesh,[24,24,12]);vol(mesh,3996)
 elif extra['label']=='Wiki seed repeated':
  original=next(e for e in engine if e.get('input',{}).get('label')=='Wiki 48 variation');assert original['stl']==matching[0]['stl']
before,after=[(Path.home()/f'Downloads/mouse-audit-wiki-guided-{stage}.retropaint').read_bytes() for stage in ['before','after']]
assert before==after
cancel=json.loads((out/'wiki-preview-cancel-evidence.json').read_bytes())
assert cancel['during']=='Rendering example with OpenSCAD\u2026'
assert cancel['closed']=={'previewOpen':False,'wikiOpen':True}
assert cancel['retry'].startswith('Ready') and cancel['before']==cancel['after']
for stage,data in [('before',before),('after',after)]:(out/f'mouse-audit-wiki-guided-{stage}.retropaint').write_bytes(data)
result={'all70_original_and_guided_variations_completed':True,'exact_copy_and_draft_isolation':True,'supplied_asset_bytes_exact':True,'minimum_clamp_negative_assertion_recoveries_and_seeded_stl_repeat_exact':True,'cancel_active_isolated_preview_then_retry_preserves_draft':True,'applied_project_before_after_byte_identical':True,'mesh_oracles':report,'worker_evidence_sha256':hashlib.sha256(raw).hexdigest()}
(out/'wiki-guides-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'verified':len(report)}))
