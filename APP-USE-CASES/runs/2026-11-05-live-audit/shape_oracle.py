"""Independent polygon-boundary and non-antialiased pixel-interior helpers."""
import math
import numpy as np

def world_points(obj):
    a,b,c,d,e,f=obj['matrix'];p=np.array([[p['x'],p['y']]for p in obj['paths'][0]['points']]);return p@np.array([[a,b],[c,d]])+np.array([e,f])

def geometric_vertices(kind,first,last):
    x,y=np.minimum(first,last);w,h=np.abs(np.array(last)-first)
    if kind=='triangle':v=np.array([[.5,0],[1,1],[0,1]])
    elif kind=='rightTriangle':v=np.array([[0,0],[1,1],[0,1]])
    elif kind=='diamond':v=np.array([[.5,0],[1,.5],[.5,1],[0,.5]])
    else:
        n={'pentagon':5,'hexagon':6}[kind];theta=np.arange(n)*2*math.pi/n-math.pi/2;v=np.column_stack([.5+.5*np.cos(theta),.5+.5*np.sin(theta)])
    return v*np.array([w,h])+[x,y]

def decoration_vertices(kind,first,last):
    x,y=np.minimum(first,last);w,h=np.abs(np.array(last)-first)
    if kind.startswith('star'):
        n=int(kind[4:]);theta=np.arange(2*n)*math.pi/n-math.pi/2;radius=np.where(np.arange(2*n)%2,.42,1);return np.column_stack([x+w/2+w/2*radius*np.cos(theta),y+h/2+h/2*radius*np.sin(theta)])
    if kind=='lightning':return np.array([[.55,0],[.1,.55],[.45,.55],[.35,1],[.95,.35],[.6,.35]])*[w,h]+[x,y]
    # Classic parametric heart: two lobes, central notch and one lower point.
    t=np.arange(100)*2*math.pi/100;xx=16*np.sin(t)**3;yy=13*np.cos(t)-5*np.cos(2*t)-2*np.cos(3*t)-np.cos(4*t);return np.column_stack([x+w/2+xx*w/32,y+(12-yy)*h/29])

def arrow_rounded_vertices(kind,first,last):
    x,y=np.minimum(first,last);w,h=np.abs(np.array(last)-first)
    if kind=='roundRect':
        r=min(w,h)/5;vertices=[]
        for centre,start in [([w-r,r],-math.pi/2),([w-r,h-r],0),([r,h-r],math.pi/2),([r,r],math.pi)]:
            theta=np.linspace(start,start+math.pi/2,13);vertices.extend(np.column_stack([centre[0]+r*np.cos(theta),centre[1]+r*np.sin(theta)]))
        return np.array(vertices)+[x,y]
    v=np.array([[0,.3],[.6,.3],[.6,0],[1,.5],[.6,1],[.6,.7],[0,.7]])
    if kind=='arrowLeft':v[:,0]=1-v[:,0]
    elif kind=='arrowUp':v=np.column_stack([v[:,1],1-v[:,0]])
    elif kind=='arrowDown':v=v[:,::-1]
    return v*[w,h]+[x,y]

def boundary_distances(points,vertices):
    return path_distances(points,vertices,True)

def bubble_vertices(kind,first,last):
    x,y=np.minimum(first,last);w,h=np.abs(np.array(last)-first)
    if kind=='callout':return np.array([[0,0],[1,0],[1,.75],[.45,.75],[.15,1],[.25,.75],[0,.75]])*[w,h]+[x,y]
    rx,ry=(w/2.2,h/2.2)if kind=='cloud'else(w/2,h*.4)
    count=max(32,math.ceil(max(rx,ry)*2*math.pi/12)*4);theta=np.arange(count+1)*2*math.pi/count
    radius=1+.1*np.cos(10*theta)if kind=='cloud'else np.ones(count+1)
    centre=[x+w/2,y+h/2 if kind=='cloud'else y+.4*h]
    v=np.column_stack([rx*radius*np.cos(theta),ry*radius*np.sin(theta)])+centre
    if kind=='ovalCallout':v=np.insert(v,math.floor(len(v)*.31),[x+.15*w,y+h],axis=0)
    return v

def path_distances(points,vertices,closed=False):
    a=vertices if closed else vertices[:-1];b=np.roll(vertices,-1,axis=0)if closed else vertices[1:];v=b-a;valid=np.einsum('ki,ki->k',v,v)>1e-20;a,v=a[valid],v[valid]
    if not len(v):return np.linalg.norm(points-vertices[0],axis=1)
    result=[]
    for start in range(0,len(points),4096):
        delta=points[start:start+4096,None,:]-a;t=np.clip(np.einsum('nki,ki->nk',delta,v)/np.einsum('ki,ki->k',v,v),0,1);result.extend(np.linalg.norm(delta-t[:,:,None]*v,axis=2).min(axis=1))
    return np.array(result)

def assert_boundary(points,vertices,tolerance=.001):
    assert boundary_distances(points,vertices).max()<tolerance
    assert max(np.linalg.norm(points-v,axis=1).min()for v in vertices)<tolerance

def polygon_pixels(vertices,width,height,margin=2):
    lo=np.maximum(np.floor(vertices.min(0)-margin).astype(int),0);hi=np.minimum(np.ceil(vertices.max(0)+margin).astype(int),[width,height]);yy,xx=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]];points=np.column_stack([xx.ravel()+.5,yy.ravel()+.5]);inside=np.zeros(len(points),dtype=bool)
    for a,b in zip(vertices,np.roll(vertices,-1,axis=0)):
        if abs(b[1]-a[1])<1e-12:continue
        inside^=((a[1]>points[:,1])!=(b[1]>points[:,1]))&(points[:,0]<(b[0]-a[0])*(points[:,1]-a[1])/(b[1]-a[1])+a[0])
    shape=xx.shape;return (slice(lo[1],hi[1]),slice(lo[0],hi[0])),inside.reshape(shape),boundary_distances(points,vertices).reshape(shape)
