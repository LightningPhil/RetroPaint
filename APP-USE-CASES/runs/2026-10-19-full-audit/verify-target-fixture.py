from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from collections import Counter
from PIL import Image
import json,hashlib,struct
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/TARGET-fixture';read=lambda file:json.loads(file.read_text(encoding='utf-8'));ui=read(folder/'target-fixture-ui.json');assert ui['status']=='Pass' and not ui['errors']
source=read(root/'headless/MIX-final/MIX-enriched.retropaint');assert read(folder/'producer/before.retropaint')==source;made=read(folder/'producer/fixture.retropaint');fresh=read(folder/'fresh/fixture.retropaint');assert made==fresh
new=made['layers'][3];expected=deepcopy(source);expected['layers'].insert(3,new);assert made==expected and new['id']==5 and new['name']=='3D 1' and new['visible'] and new['opacity']==1 and new['paper'] is None and not any(new['live'].values()) and not new.get('objects') and not new.get('photo')
body=new['cad']['bodies'][0];assert len(new['cad']['bodies'])==1 and body['solid']==dict(kind='primitive',shape='box',size=[20,20,20],wall=2) and body['position']==[0,0,10] and body['rotation']==[0,0,0] and body['scale']==[1,1,1]
stl=(folder/'producer/cube.stl').read_bytes();count=struct.unpack_from('<I',stl,80)[0];assert count==12 and len(stl)==84+50*count;edges=Counter();volume=0.;points=[]
for index in range(count):
    values=struct.unpack_from('<12fH',stl,84+index*50);tri=np.asarray(values[3:12]).reshape(3,3);normal=np.asarray(values[:3]);assert np.dot(normal,np.cross(tri[1]-tri[0],tri[2]-tri[0]))>0;volume+=float(np.dot(tri[0],np.cross(tri[1],tri[2])))/6;points.extend(tri)
    vertices=[tuple(p) for p in tri]
    for i in range(3):edges[tuple(sorted((vertices[i],vertices[(i+1)%3])))]+=1
assert all(value==2 for value in edges.values()) and abs(volume-8000)<1e-6 and np.array_equal(np.min(points,axis=0),[-10,-10,0]) and np.array_equal(np.max(points,axis=0),[10,10,20])
assert np.array_equal(np.asarray(Image.open(folder/'producer/fixture.png')),np.asarray(Image.open(folder/'fresh/fixture.png')))
events=[e for file in [folder/'producer/events.json',folder/'fresh/events.json'] for e in read(file) if e['action']=='download'];assert len(events)==6
for event in events:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),project=str(folder/'fresh/fixture.retropaint'),sha256=hashlib.sha256((folder/'fresh/fixture.retropaint').read_bytes()).hexdigest(),all_original_MIX_layer_fields_pixels_live_objects_photo_exact=True,only_added_sheet=dict(id=5,position_in_stack=3,name='3D 1'),independent_cube_STL=dict(triangles=12,closed_oriented=True,volume_mm3=volume,bounds_mm=[[-10,-10,0],[10,10,20]]),actual_fresh_input_data_and_rgba_exact=True,actual_downloads_verified=6,scope='Fixture preparation only, no acceptance Pass inferred. Actual primitive UI and native file workflows; independent elementary STL math/Pillow.')
(root/'fixtures/TARGET-manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Verified full MIX plus independent20mm cube and real file reopen.')
