"""Independent homogeneous-coordinate geometry and vectorized alpha sampler."""
import numpy as np
def project_source(document,index=0):
    import base64,io
    from PIL import Image
    layer=document['layers'][index];decode=lambda url:np.array(Image.open(io.BytesIO(base64.b64decode(url.split(',')[1]))).convert('RGBA')).astype(int);canvas=decode(layer['image']);objects=layer.get('objects',[])
    if not objects:return canvas
    assert len(objects)==1 and np.all(canvas[:,:,3]==0);obj=objects[0];assert obj['kind']=='raster' and obj['matrix']==[1,0,0,1,0,0] and obj['opacity']==1 and not obj.get('live');return decode(obj['image'])
def expected_geometry(source,settings):
    h,w,_=source.shape;y,x=np.mgrid[:h,:w];unit=min(w,h)/2;zoom=settings.get('zoom',100)/100
    p=np.stack([(x+.5-w/2)/unit/zoom,(y+.5-h/2)/unit/zoom,np.ones_like(x)],axis=0).reshape(3,-1)
    perspective=np.array([[1,0,0],[0,1,0],[-settings.get('horizontal',0)/250,-settings.get('vertical',0)/250,1]])@p;valid=perspective[2]>=.1;q=perspective[:2]/perspective[2]
    t=np.deg2rad(-settings.get('angle',0));rotation=np.array([[np.cos(t),-np.sin(t)],[np.sin(t),np.cos(t)]]);q=np.diag([-1 if settings.get('flipX') else 1,-1 if settings.get('flipY') else 1])@rotation@q;qx,qy=q.reshape(2,h,w);radial=1+settings.get('distortion',0)/350*(qx*qx+qy*qy);sx=qx*radial*unit+w/2-.5;sy=qy*radial*unit+h/2-.5
    def sample(xx,yy):
        inside=(xx>=-.5)&(xx<=w-.5)&(yy>=-.5)&(yy<=h-.5);xx=np.clip(xx,0,w-1);yy=np.clip(yy,0,h-1);ix=np.floor(xx).astype(int);iy=np.floor(yy).astype(int);fx=xx-ix;fy=yy-iy;alpha=np.zeros((h,w));rgb=np.zeros((h,w,3))
        for dx,dy,weight in [(0,0,(1-fx)*(1-fy)),(1,0,fx*(1-fy)),(0,1,(1-fx)*fy),(1,1,fx*fy)]:
            value=source[np.minimum(iy+dy,h-1),np.minimum(ix+dx,w-1)].astype(float);coverage=value[:,:,3]*weight;alpha+=coverage;rgb+=value[:,:,:3]*coverage[:,:,None]
        np.divide(rgb,alpha[:,:,None],out=rgb,where=alpha[:,:,None]>0);rgb[~inside]=0;alpha[~inside]=0;return np.dstack([rgb,alpha]),inside
    result,inside=sample(sx,sy);fringe=settings.get('aberration',0)/20000
    if fringe:
        red,_=sample(sx+qx*unit*fringe,sy+qy*unit*fringe);blue,_=sample(sx-qx*unit*fringe,sy-qy*unit*fringe);result[:,:,0]=red[:,:,0];result[:,:,2]=blue[:,:,2]
    valid=valid.reshape(h,w);result[~valid]=0;result=np.rint(np.clip(result,0,255)).astype(int);result[result[:,:,3]==0]=0
    return result,inside&valid
def verify_geometry(actual,source,settings,crop=None):
    predicted,inside=expected_geometry(source,settings)
    if crop is not None:
        x,y,w,h=crop;predicted=predicted[y:y+h,x:x+w];inside=inside[y:y+h,x:x+w]
    assert actual.shape==predicted.shape;error=abs(actual.astype(int)-predicted);assert error[:,:,3].max()<=1;opaque=(actual[:,:,3]==255)&(predicted[:,:,3]==255);opaque_error=int(error[:,:,:3][opaque].max()) if np.any(opaque) else 0;assert opaque_error<=1,opaque_error
    visible=actual[:,:,3]>0;bound=1+np.ceil(255/(2*np.maximum(1,actual[:,:,3])));assert np.all(error[:,:,:3].max(axis=2)[visible]<=bound[visible]);assert np.all(actual[~inside]==0) and np.all(actual[actual[:,:,3]==0]==0)
    return dict(opaque_max_RGB_error=opaque_error,alpha_max_error=int(error[:,:,3].max()),outside_source_clear_pixels=int(np.count_nonzero(~inside)))
