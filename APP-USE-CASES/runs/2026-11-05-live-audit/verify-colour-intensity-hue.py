"""Native saturation/vibrance/hue against known RGB relationships and HLS math."""
from pathlib import Path
import base64,colorsys,copy,hashlib,io,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def doc(n):
    name=f'mouse-audit-colour107-{n}.retropaint';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
def png(n):
    name=f'mouse-audit-colour107-{n}.png';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return np.array(Image.open(out/name).convert('RGBA')).astype(int)
baseline=doc('baseline');source=np.array(Image.open(io.BytesIO(base64.b64decode(baseline['layers'][0]['image'].split(',')[1]))).convert('RGBA')).astype(int);defaults=json.loads((downloads/'mouse-audit-photo98-full-reset.retropaint').read_text())['layers'][0]['photo']['settings'];images={}
variants=[('saturation-minus100','saturation',-100),('saturation-plus100','saturation',100),('saturation-plus50','saturation',50),('saturation-reset','saturation',0),('vibrance-plus50','vibrance',50),('vibrance-reset','vibrance',0),('hue-plus120','hue',120),('hue-plus180','hue',180),('hue-minus180','hue',-180),('hue-reset','hue',0)]
for name,key,value in variants:
    d=doc(name);a=png(name);images[name]=a;settings=copy.deepcopy(defaults);settings[key]=value;expected=copy.deepcopy(baseline);expected['layers'][0]['photo']=dict(settings=settings,normal=settings,look='custom',lookActive=False);assert expected==d
    assert np.array_equal(a[:,:,3],source[:,:,3]);assert np.array_equal(a[source[:,:,3]==0],source[source[:,:,3]==0])
    if name.endswith('reset'):assert np.array_equal(a,source)
    for x in [680,760,840]:assert len(set(a[72,x,:3]))==1
mono=images['saturation-minus100'];assert np.array_equal(mono[:,:,0],mono[:,:,1]) and np.array_equal(mono[:,:,1],mono[:,:,2]);opaque=source[:,:,3]==255;luma=np.rint(source[:,:,:3]@np.array([.2126,.7152,.0722]));assert np.max(abs(mono[:,:,0][opaque]-luma[opaque]))<=1;assert np.ptp(mono[:,:,0][opaque])==255
chroma=lambda a,x:int(np.ptp(a[456,x,:3]));base=[chroma(source,x) for x in [360,440]];sat=[chroma(images['saturation-plus50'],x) for x in [360,440]];vib=[chroma(images['vibrance-plus50'],x) for x in [360,440]];assert all(s>b for s,b in zip(sat,base));assert vib[0]-base[0]>vib[1]-base[1]>0;assert all(v<s for v,s in zip(vib,sat));assert not np.array_equal(images['vibrance-plus50'],images['saturation-plus50'])
assert np.array_equal(images['hue-plus180'],images['hue-minus180'])
mask=source[:,:,3]>0;unique,inverse=np.unique(source[:,:,:3][mask],axis=0,return_inverse=True);expected=[]
for rgb in unique:
    h,l,s=colorsys.rgb_to_hls(*(rgb/255));expected.append(np.rint(np.array(colorsys.hls_to_rgb((h+1/3)%1,l,s))*255))
expected=np.array(expected)[inverse];errors=np.max(abs(images['hue-plus120'][:,:,:3][mask]-expected),axis=1);bounds=np.ceil(255/(2*source[:,:,3][mask]));assert np.all(errors<=bounds)
assert [images['hue-plus120'][72,x,:3].tolist() for x in [40,280,440]]==[[0,255,0],[0,0,255],[255,0,0]]
report=dict(status='Pass',minus100_saturation_monochrome_and_independent_Rec709_luma=True,tonal_structure_retained=True,neutral_greys_exact=True,alpha_and_clear_margins_exact_every_variant=True,all_reset_RGBA_exact=True,dull_vivid_chroma={'baseline':base,'saturation50':sat,'vibrance50':vib},vibrance_gentler_and_controls_independent=True,no_hidden_look_or_other_adjustment=True,hue120_matches_independent_standard_HLS_with_declared_alpha_quantisation=True,hue180_endpoints_pixels_exact=True,whole_source_and_other_document_fields_exact=True,sha256=hashes)
(out/'colour107-intensity-hue-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native saturation/vibrance, independent HLS hue/wrap, alpha and exact resets')
