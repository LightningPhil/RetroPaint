"""Independent analytic inward offset of the joined20mm cube/cylinder open-top shell."""
from pathlib import Path
import hashlib,json,math
import numpy as np
from stl_oracle import read_binary,measure
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';prefix='mouse-audit-delivery-cadmix';raw=(out/(prefix+'-3d-mm.stl')).read_bytes();tri=read_binary(raw);stats=measure(tri);doc=json.loads((out/(prefix+'.retropaint')).read_text(encoding='utf-8'));shell=next(l for l in doc['layers'] if 'cad'in l)['cad']['bodies'][0]['solid'];assert shell['kind']=='shell' and shell['thickness']==3 and len(shell['faces'])==1 and shell['faces'][0]['normal']==[0,0,1];children=shell['source']['solid']['children'];assert shell['source']['solid']['operation']=='union'
assert [(b['position'],b['scale'],b['solid']['shape'],b['solid']['size']) for b in children]==[([0,0,10],[1,1,1],'box',[20,20,20]),([15,0,10],[1,1,1],'cylinder',[20,20,20])]
# Cross-section: rectangle[-10,10]^2 union radius10 circle centred(15,0).
# The inward3mm offset has upper boundary y=7 until x0; then a radius3
# concave corner arc around(10,sqrt75); then radius7 circle centred(15,0).
# These meet at(x0,7) and(11.5,7sqrt3/2). Integrate the explicit arcs.
h=math.sqrt(75);x0=10-math.sqrt(9-(h-7)**2)
def integral(radius,u):return .5*(u*math.sqrt(max(0,radius**2-u**2))+radius**2*math.asin(u/radius))
outer_area=400+200*math.pi/3+25*math.sqrt(3)
inner_area=2*(7*(x0+7)+h*(11.5-x0)-(integral(3,1.5)-integral(3,x0-10))+(integral(7,7)-integral(7,-3.5)))
outer_volume=outer_area*20;removed=inner_area*17;expected=outer_volume-removed
assert abs(stats['signed_volume_mm3']-expected)<.6 and stats['bounds_mm']==[[-10,-10,0],[25,10,20]] and len(stats['components'])==1 and stats['components'][0]['euler']==2
def ray(x,y):
 a,b,c=tri[:,0],tri[:,1],tri[:,2];den=(b[:,1]-c[:,1])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,1]-c[:,1]);valid=np.abs(den)>1e-9;den=den[valid];a,b,c=a[valid],b[valid],c[valid];u=((b[:,1]-c[:,1])*(x-c[:,0])+(c[:,0]-b[:,0])*(y-c[:,1]))/den;v=((c[:,1]-a[:,1])*(x-c[:,0])+(a[:,0]-c[:,0])*(y-c[:,1]))/den;inside=(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7);z=u*a[:,2]+v*b[:,2]+(1-u-v)*c[:,2];return sorted(set(np.round(z[inside],5).tolist()))
rays={}
for point,wanted in [((.31,.57),[0,3]),((15.31,.57),[0,3]),((10.31,.57),[0,3]),((-8.31,.57),[0,20]),((23.31,.57),[0,20]),((10.31,5.9),[0,20]),((10.31,5.3),[0,3])]:
 actual=ray(*point);assert actual==wanted;rays[str(point)]=actual
report=dict(status='Pass',analytic_outer_volume_mm3=outer_volume,analytic_removed_volume_mm3=removed,analytic_material_volume_mm3=expected,actual_material_volume_mm3=stats['signed_volume_mm3'],tessellation_error_mm3=abs(stats['signed_volume_mm3']-expected),closed_outward_single_component_euler=2,cavity_opening_floor_and_walls=rays,bounds_mm=stats['bounds_mm'],mesh_sha256=hashlib.sha256(raw).hexdigest(),independent_method='Explicit rectangle/circle union area and piecewise inward-offset arc integrals; no application geometry kernel. Independent vertical triangle intersections check both lobes, bridge, curved corner, walls and3mm floor.')
(out/'joined-shell-delivery-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
