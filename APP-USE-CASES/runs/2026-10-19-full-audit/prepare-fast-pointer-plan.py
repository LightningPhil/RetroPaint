from pathlib import Path
from datetime import datetime,timezone
import math,json
root=Path(__file__).resolve().parent;file=root/'fixtures/PAINT-020-plan.json';assert not file.exists()
rows=[]
for i,viewport in enumerate([[1280,720],[320,568],[390,844],[844,390]]):
    for device in ['mouse','browser-emulated-pen']:
        for api in ['available','absent-fallback']:
            for load in ['normal','busy']:
                rows.append(dict(id=f'v{i+1}-{device}-{api}-{load}',viewport=viewport,device=device,api=api,load=load))
points=[[round(450+140*math.cos(2*math.pi*i/96),6),round(350+90*math.sin(2*math.pi*i/96),6)] for i in range(97)]
plan=dict(at=datetime.now(timezone.utc).isoformat(),case='PAINT-020',status='Pre-execution software scope plan; physical pen unavailable',rows=rows,points=points,size=22,strength=1,colour=[229,57,53],maximum_footprint_radius=24,load_busy_ms_per_frame=12,expected_downloads_per_row=10,oracle='32 actual UI software workflows: four layouts x native mouse/browser-emulated pen x available/removed coalesced API x normal/deliberately busy main thread. Busy fixture consumes12ms each real RAF during the gesture only and records actual busy intervals; no fixed clock or fabricated DOM input. Native browser pen pressures vary0.1..0.9 while source remains960x640 at unchanged scale. The predefined closed elliptic loop must remain continuous, changed pixels remain within24 source pixels of the recorded native ordinary/coalesced sample polyline, earlier/reopened source and exact complete Undo/Redo remain unchanged. Every actual saved project/PNG is hashed and independently decoded. Available coalesced sample arrays are recorded with source coordinates, pressure, timestamps and trust; any actually delivered intermediate sample must intersect the saved painted footprint. API absence is injected before app load via removal of the browser method; ordinary native events must still paint safely. Software-emulated pen and loaded scheduling never certify physical pen pressure, hardware scale or physical coalescing. Physical branch stays Partial, not Pass. Independent Python/Pillow/NumPy oracle uses no application paint/input/serializer kernel.')
file.write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8');print('Recorded32 software workflows/320 actual downloads; physical pen explicitly unavailable.')
