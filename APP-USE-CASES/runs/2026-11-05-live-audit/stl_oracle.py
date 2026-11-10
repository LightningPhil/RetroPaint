"""Independent binary STL topology and oriented connected-component measurements."""
import struct
import numpy as np

def read_binary(raw):
    assert len(raw)>=84
    count=struct.unpack_from('<I',raw,80)[0]
    assert len(raw)==84+50*count
    tri=np.array([struct.unpack_from('<12fH',raw,84+50*i)[3:12] for i in range(count)]).reshape(-1,3,3)
    assert np.isfinite(tri).all()
    return tri

def measure(tri):
    parents=list(range(len(tri)));edges={}
    def find(i):
        while parents[i]!=i:
            parents[i]=parents[parents[i]];i=parents[i]
        return i
    for i,triangle in enumerate(np.round(tri,6)):
        for a,b in zip(triangle,np.roll(triangle,-1,axis=0)):
            aa,bb=tuple(a),tuple(b);assert aa!=bb
            edges.setdefault(tuple(sorted((aa,bb))),[]).append((i,1 if aa<bb else -1))
    for entries in edges.values():
        assert len(entries)==2 and entries[0][1]+entries[1][1]==0
        parents[find(entries[0][0])]=find(entries[1][0])
    groups={}
    for i in range(len(tri)):groups.setdefault(find(i),[]).append(i)
    components=[]
    for indexes in groups.values():
        part=tri[indexes];vertices=set(map(tuple,np.round(part.reshape(-1,3),6)));index_set=set(indexes);edge_count=sum(entries[0][0] in index_set for entries in edges.values());volume=float(np.einsum('ij,ij->i',part[:,0],np.cross(part[:,1],part[:,2])).sum()/6)
        components.append(dict(triangles=len(part),signed_volume_mm3=volume,bounds_mm=[part.min(axis=(0,1)).tolist(),part.max(axis=(0,1)).tolist()],euler=len(vertices)-edge_count+len(part)))
    return dict(triangles=len(tri),bounds_mm=[tri.min(axis=(0,1)).tolist(),tri.max(axis=(0,1)).tolist()],signed_volume_mm3=sum(c['signed_volume_mm3'] for c in components),closed_consistently_oriented=True,components=components)


def ray_y(tri,x,z):
    p=tri[:,:,[0,2,1]]; a,b,c=p[:,0],p[:,1],p[:,2]; den=(b[:,1]-c[:,1])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,1]-c[:,1]); valid=abs(den)>1e-9
    a,b,c,den=a[valid],b[valid],c[valid],den[valid]; u=((b[:,1]-c[:,1])*(x-c[:,0])+(c[:,0]-b[:,0])*(z-c[:,1]))/den; v=((c[:,1]-a[:,1])*(x-c[:,0])+(a[:,0]-c[:,0])*(z-c[:,1]))/den
    hit=(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7); return sorted(set(np.round((u*a[:,2]+v*b[:,2]+(1-u-v)*c[:,2])[hit],6).tolist()))
