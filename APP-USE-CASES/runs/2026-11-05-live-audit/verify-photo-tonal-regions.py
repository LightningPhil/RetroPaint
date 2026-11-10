"""Native highlight/shadow/endpoint masks and coverage-weighted clipping."""
from pathlib import Path
import base64,copy,hashlib,io,json,re
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(prefix,n):
    name=f'mouse-audit-photo{prefix}-{n}.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
baseline=doc(99,'tonal-baseline');source=np.array(Image.open(root/'test-results/audit-2026-11-05/fixtures/TONAL-alpha.png').convert('RGBA')).astype(int);xs=[123,315,507,699,891];patches=np.array([32,64,128,192,224]);deltas={};images={};ui=json.loads((out/'photo100-ui.json').read_text())
for name,key,value in [('highlights-minus50','highlights',-50),('shadows-plus50','shadows',50),('whites-plus100','whites',100),('blacks-minus100','blacks',-100),('endpoints-reset','blacks',0)]:
    d=doc(100,name);expected=copy.deepcopy(baseline);expected['layers'][0]['photo']=d['layers'][0]['photo'];assert expected==d
    for kind in ['settings','normal']:
        s=d['layers'][0]['photo'][kind];assert s[key]==value
        for k in ['highlights','shadows','whites','blacks']:assert s[k]==(value if k==key else 0)
    filename=f'mouse-audit-photo100-{name}.png';data=(Path.home()/'Downloads'/filename).read_bytes();(out/filename).write_bytes(data);hashes[filename]=hashlib.sha256(data).hexdigest();a=np.array(Image.open(out/filename).convert('RGBA')).astype(int);images[name]=a;assert np.array_equal(a[:,:,3],source[:,:,3]);deltas[name]=(a[192,xs,0]-patches).tolist()
    if name=='endpoints-reset':assert np.array_equal(a,source)
assert deltas['highlights-minus50'][4]<deltas['highlights-minus50'][2]<deltas['highlights-minus50'][0]
assert deltas['shadows-plus50'][0]>deltas['shadows-plus50'][2]>deltas['shadows-plus50'][4]
assert deltas['whites-plus100'][4]>deltas['whites-plus100'][2]>=deltas['whites-plus100'][0]
assert deltas['blacks-minus100'][0]<deltas['blacks-minus100'][2]<=deltas['blacks-minus100'][4]
assert np.unique(images['highlights-minus50'][16:144,1020:1024,:3]).size==1 # Clipped source stays uniform; no recovered information claim.
for row in ui:
    a=images[row['variant']];alpha=a[:,:,3]/255;count=alpha.sum();fractions=[np.sum(alpha[np.min(a[:,:,:3],axis=2)<=1])/count*100,np.sum(alpha[np.max(a[:,:,:3],axis=2)>=254])/count*100];shown=list(map(int,re.findall(r'(\d+)%',row['histogram'])));assert all(abs(x-y)<=1 for x,y in zip(shown,fractions)) # Preview downsampling and rounded percentages.
coverage=doc(101,'coverage');raw=np.array(Image.open(io.BytesIO(base64.b64decode(coverage['layers'][0]['image'].split(',')[1]))).convert('RGBA'));assert np.array_equal(raw,np.array(Image.open(root/'test-results/audit-2026-11-05/fixtures/tonal-coverage.png')))
shown=list(map(int,re.findall(r'(\d+)%',json.loads((out/'photo101-coverage-ui.json').read_text())['histogram'])));assert shown==[1,1]
report=dict(status='Pass',known_patch_deltas=deltas,tonal_regions_independent=True,all_source_and_other_document_data_exact=True,alpha_exact_every_variant=True,endpoint_group_reset_pixels_exact=True,clipping_percentages_agree_with_independent_visible_coverage_within_one_rounded_percentage_point=True,alpha1_padding_does_not_dominate=True,source_clipped_white_stays_uniform=True,sha256=hashes)
(out/'photo100-101-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native tonal regions, independent endpoint clipping, exact alpha/reset and faint-padding coverage')
