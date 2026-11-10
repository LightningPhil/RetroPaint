"""Find the actual visible drawing holes in retained browser screenshots."""
import hashlib,json,math,statistics,sys
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse'
def measure(file,paper,controls):
 opened=Image.open(out/file);format=opened.format;im=opened.convert('RGB');sx=paper['width']/960;sy=paper['height']/640
 radius=controls['radius']*controls['inner']/controls['outer'];cx=480+controls['radius']-radius;cy=320
 samples={}
 for y in range(max(0,math.floor(paper['y']+(cy-radius)*sy)),min(im.height,math.ceil(paper['y']+(cy+radius)*sy))):
  for x in range(max(0,math.floor(paper['x']+(cx-radius)*sx)),min(im.width,math.ceil(paper['x']+(cx+radius)*sx))):
   px=(x+.5-paper['x'])/sx;py=(y+.5-paper['y'])/sy
   if math.hypot(px-cx,py-cy)>.94*radius:continue
   rgb=im.getpixel((x,y));samples[x,y]=.299*rgb[0]+.587*rgb[1]+.114*rgb[2]
 # The browser screenshot API supplies JPEG bytes, including chroma
 # subsampling around tiny white dots. Use luminance above the independently
 # measured gear interior, rather than exact white RGB channel values.
 background=statistics.median(samples.values());threshold=min(245,background+35)
 candidates={point:'white' if value>threshold else 'black' for point,value in samples.items() if value>threshold or value<70}
 components=[]
 while candidates:
  seed,color=candidates.popitem();todo=[seed];points=[]
  while todo:
   x,y=todo.pop();points.append((x,y))
   for adjacent in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
    if candidates.get(adjacent)==color:del candidates[adjacent];todo.append(adjacent)
  x=sum(p[0]+.5 for p in points)/len(points);y=sum(p[1]+.5 for p in points)/len(points)
  components.append({'colour':color,'pixels':len(points),'screen':[x,y],'source':[(x-paper['x'])/sx,(y-paper['y'])/sy],'distance_from_gear_centre':math.hypot((x-paper['x'])/sx-cx,(y-paper['y'])/sy-cy)})
 components.sort(key=lambda c:c['distance_from_gear_centre'])
 return {'screenshot':file,'actual_image_format':format,'interior_median_luminance':background,'white_hole_luminance_threshold':threshold,'sha256':hashlib.sha256((out/file).read_bytes()).hexdigest(),'centre_source':[cx,cy],'radius_source':radius,'observed_holes':len(components),'selected_holes':sum(c['colour']=='black' for c in components),'holes':components}
if __name__=='__main__':
 gear=sys.argv[1]
 if gear=='before':
  e=json.loads((out/'spiro-holes-evidence.json').read_bytes())['before'];result=measure(e['screenshot'],e['ui']['paper'],e['controls']);assert result['observed_holes']==8 and result['selected_holes']==1;name='spiro-orange-holes-before-measurement.json'
 else:
  e=next(b for b in json.loads((out/'spiro-holes33-evidence.json').read_bytes())['banks'] if b['gear']==gear);result=measure('spiro-holes33-'+gear+'.png',e['ui']['paper'],e['controls']);assert result['observed_holes']==e['expectedHoles'] and result['selected_holes']==1,(gear,result);name='spiro-gear-'+gear+'-hole-centres.json'
 (out/name).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({'gear':gear,'holes':result['observed_holes'],'selected':result['selected_holes'],'result':name}))
