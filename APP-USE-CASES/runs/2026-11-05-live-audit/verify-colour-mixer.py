"""Independent Python HLS oracle for every native single-range control export."""
from pathlib import Path
import base64,colorsys,copy,hashlib,io,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def load(name,ext='retropaint'):
    filename=f'mouse-audit-mixer117-{name}.{ext}';data=(downloads/filename).read_bytes();(out/filename).write_bytes(data);hashes[filename]=hashlib.sha256(data).hexdigest()
    return json.loads(data) if ext=='retropaint' else np.array(Image.open(io.BytesIO(data)).convert('RGBA')).astype(int)
baseline=load('baseline');raw=np.array(Image.open(io.BytesIO(base64.b64decode(baseline['layers'][0]['image'].split(',')[1]))).convert('RGBA')).astype(int)
defaults=json.loads((downloads/'mouse-audit-photo98-full-reset.retropaint').read_text())['layers'][0]['photo']['settings'];centres=[0,30,60,120,180,240,270,300];manifest=json.loads((root/'test-results/audit-2026-11-05/fixtures/colour107-manifest.json').read_text());details=[]
for band,centre in enumerate(centres):
    for key,value in [('hue',29),('saturation',-49),('luminance',29)]:
        name=f'{band}-{key}';d=load(name);a=load(name,'png');s=copy.deepcopy(defaults);s['mixer'][band][key]=value;expected=copy.deepcopy(baseline);expected['layers'][0]['photo']=dict(settings=s,normal=s,look='custom',lookActive=False);assert d==expected,name
        assert np.array_equal(a[:,:,3],raw[:,:,3]) and np.array_equal(a[raw[:,:,3]==0],raw[raw[:,:,3]==0])
        for patch in manifest['patches']:
            x,y=patch['centre'];rgb=raw[y,x,:3];h,l,sat=colorsys.rgb_to_hls(*(rgb/255));distance=min(abs(h-centre/360),1-abs(h-centre/360));weight=max(0,1-distance/(1/9))*min(1,sat*4)
            if key=='hue':h+=value/360*weight
            elif key=='saturation':sat=np.clip(sat*(1+value/100*weight),0,1)
            else:l=np.clip(l+value/100*.35*weight,0,1)
            predicted=np.array(colorsys.hls_to_rgb(h%1,l,sat))*255;bound=1+np.ceil(255/(2*patch['alpha']));assert np.max(abs(a[y,x,:3]-predicted))<=bound,(name,patch['name'],predicted,a[y,x,:3])
        target=manifest['patches'][band];distant=manifest['patches'][(band+4)%8];tx,ty=target['centre'];dx,dy=distant['centre'];target_delta=np.max(abs(a[ty,tx,:3]-raw[ty,tx,:3]));distant_delta=np.max(abs(a[dy,dx,:3]-raw[dy,dx,:3]));assert target_delta>10 and target_delta>distant_delta+5,(name,target_delta,distant_delta)
        details.append(dict(band=band,key=key,value=value,target_change=int(target_delta),distant_change=int(distant_delta)))
        # Paired known boundary samples, including red across359/0degrees,
        # have no large output discontinuity. Opaque pairs use exact8bitRGB.
        boundary=[p for p in manifest['patches'] if p['name'].startswith('hue') and p['alpha']==255]
        for left,right in zip(boundary[::2],boundary[1::2]):
            x,y=left['centre'];xx,yy=right['centre'];assert np.max(abs(a[y,x,:3]-a[yy,xx,:3]))<45,(name,left['name'],right['name'])
report=dict(status='Pass',all_eight_ranges_times_three_native_mouse_controls=True,all_known_boundary_and_skin_patches_match_independent_Python_HLS=True,target_changes_more_than_distant_colour=True,red_wrap_and_paired_hue_boundaries_no_seam=True,each_record_and_unrelated_settings_whole_document_exact=True,source_alpha_clear_gutters_exact=True,details=details,sha256=hashes)
(out/'mixer117-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS all24 native HSL controls, independent HLS, boundaries, wrap, source and alpha')
