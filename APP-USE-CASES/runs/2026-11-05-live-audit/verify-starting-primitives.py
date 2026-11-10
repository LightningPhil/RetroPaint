"""Eight native starting solids: independent bounds, volume, manifold and genus."""
from pathlib import Path
import hashlib,json,math,struct
import numpy as np
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';ui=json.loads((out/'solid158-ui.json').read_text());expected=[8000,4*math.pi*1000/3,math.pi*100*20,math.pi*100*20/3,2*math.pi**2*5.5*4.5*10,math.pi*(100-64)*20,8000/6,4000];metrics={};sheet=Image.new('RGB',(1080,8*138),'white');draw=ImageDraw.Draw(sheet)
for i,item in enumerate(ui):
    name=item['name'];suffix=f' ({i})' if i else '';filename=f'mouse-audit-solid158-primitives-3d-mm{suffix}.stl';data=(downloads/filename).read_bytes();(out/filename).write_bytes(data);count=struct.unpack_from('<I',data,80)[0];assert len(data)==84+50*count;tri=np.array([struct.unpack_from('<12fH',data,84+50*j)[3:12] for j in range(count)]).reshape(-1,3,3);lo=tri.min(axis=(0,1));hi=tri.max(axis=(0,1));assert np.allclose(hi-lo,[20,20,20],atol=.05) and abs(lo[2])<.0001;volume=float(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6);assert abs(volume/expected[i]-1)<.02
    edges={};vertices=set()
    for triangle in np.round(tri,5):
        for a,b in zip(triangle,np.roll(triangle,-1,axis=0)):
            aa,bb=tuple(a),tuple(b);assert aa!=bb;vertices.add(aa);vertices.add(bb);key=tuple(sorted((aa,bb)));edges[key]=edges.get(key,0)+1
    assert set(edges.values())=={2};euler=len(vertices)-len(edges)+count;assert euler==(0 if name in ['Tube','Torus'] else 2);assert item['emptyAfterUndo'] and len(item['views'])==4 and 'Closed solid geometry' in item['print']
    metrics[name]=dict(bounds_mm=(hi-lo).tolist(),volume_mm3=volume,analytic_volume_mm3=expected[i],triangles=count,euler=euler,sha256=hashlib.sha256(data).hexdigest())
    for col,view in enumerate(['Top','Front','Right','3D']):
        image=Image.open(out/f'solid158-{name}-{view}.png').convert('RGB').crop((300,140,1380,580)).resize((270,110),Image.Resampling.LANCZOS);sheet.paste(image,(270*col,138*i+25));draw.text((270*col+5,138*i+5),f'{name} — {view}',fill='black')
before=(downloads/'mouse-audit-solid158-primitives.retropaint').read_bytes();after=(downloads/'mouse-audit-solid158-after-all.retropaint').read_bytes();assert before==after;document=json.loads(before);assert not next(l for l in document['layers'] if 'cad' in l)['cad']['bodies'];(out/'mouse-audit-solid158-after-all.retropaint').write_bytes(after);sheet.save(out/'solid158-views.png');report=dict(status='Pass',all_additions_one_step_undo=True,empty_document_byte_exact_after_all=True,metrics=metrics,remaining='Collapsed numeric size rejection is tested separately in SOLID-008; this report covers the eight valid starting primitives.');(out/'solid158-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
