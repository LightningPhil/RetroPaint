"""Independent invalid STL variants and genuine closed200000triangle/20MB acceptance fixtures."""
from pathlib import Path
import hashlib,json,math,struct
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/fixtures/stl180';out.mkdir(exist_ok=True);hollow=root/'test-results/audit-2026-11-05/fixtures/hollow173';raw=(hollow/'canonical.stl').read_bytes();files={}
def save(name,data,expect):
 p=out/name;p.write_bytes(data);files[name]=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),expect=expect)
save('truncated.stl',raw[:100],'not a binary or ASCII STL')
save('count-mismatch.stl',raw[:84],'not a binary or ASCII STL')
for name,value in [('nan',float('nan')),('infinity',float('inf')),('coordinate-overflow',10001)]:
 b=bytearray(raw);struct.pack_into('<f',b,96,value);save(name+'.stl',b,'coordinates must fit')
b=bytearray(raw);struct.pack_into('<I',b,80,47);save('open-edge.stl',b[:84]+b[134:],'open edges')
b=bytearray(raw);struct.pack_into('<I',b,80,49);save('non-manifold.stl',b+b[84:134],'non-manifold')
b=bytearray(raw);b[96:108]=b[108:120];save('collapsed.stl',b,'collapsed triangles')
save('incomplete-ascii.stl',b'solid incomplete\nfacet normal 0 0 1\nouter loop\nvertex 0 0 0\nvertex 1 0 0\nendloop\nendfacet\nendsolid\n','incomplete triangles')
save('unsupported-obj.stl',b'# Wavefront OBJ disguised as STL\nv 0 0 0\nv 1 0 0\nf 1 2 3\n','not a binary or ASCII STL')
save('over20MB.stl',b'\0'*20_000_001,'smaller than 20 MB')
ascii_raw=(hollow/'canonical-ascii.stl').read_bytes();save('exact20MB-ascii.stl',ascii_raw+b' '*(20_000_000-len(ascii_raw)),'accepted 48triangle nested shell')
# A50000-sided prism:50000triangles on each cap and100000side triangles.
# Explicit ring coordinates and face ordering, independent of the application.
n=50000;theta=np.arange(n)*2*math.pi/n;bottom=np.column_stack([1000*np.cos(theta),1000*np.sin(theta),np.zeros(n)]);top=bottom+[0,0,10];following=np.roll(np.arange(n),-1);tri=np.empty((4*n,3,3),dtype=np.float32)
tri[0:n]=np.stack([np.zeros_like(bottom),bottom[following],bottom],axis=1)
tri[n:2*n]=np.stack([np.tile([0,0,10],(n,1)),top,top[following]],axis=1)
tri[2*n:3*n]=np.stack([bottom,bottom[following],top[following]],axis=1)
tri[3*n:4*n]=np.stack([bottom,top[following],top],axis=1)
records=np.zeros(4*n,dtype=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attribute','<u2')]))
records['vertices']=tri;binary=b'Independent STL180 closed50000gon prism'.ljust(80,b'\0')+struct.pack('<I',4*n)+records.tobytes()
save('exact200000.stl',binary,'accepted closed200000triangle prism')
save('over200000.stl',binary[:80]+struct.pack('<I',200001)+binary[84:]+binary[84:134],'at most 200,000 triangles')
manifest=dict(provenance=__doc__,prism=dict(sides=n,radius=1000,height=10,triangles=200000,analytic_volume=n/2*1000**2*math.sin(2*math.pi/n)*10),files=files);(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(dict(fixtures=len(files),prism=manifest['prism']),indent=2))
