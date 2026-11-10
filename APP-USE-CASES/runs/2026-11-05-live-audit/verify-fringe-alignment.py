"""Spatial RGB edge coincidence, untouched Green/alpha and editable saved value."""
from pathlib import Path
import copy,hashlib,json
import numpy as np
from PIL import Image
from geometry_oracle import verify_geometry,project_source
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={};metrics={}
def load(n,ext='retropaint'):
    name=f'mouse-audit-fringe143-{n}.{ext}';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data) if ext=='retropaint' else np.array(Image.open(out/name).convert('RGBA')).astype(int)
base=load('baseline');raw=project_source(base);defaults=json.loads((downloads/'mouse-audit-photo98-full-reset.retropaint').read_text())['layers'][0]['photo']['settings'];ui=json.loads((out/'fringe143-ui.json').read_text());assert ui==dict(corrected=100,opposite=-100,reopened=100,refined=49);images={}
for name,value in [('corrected',100),('opposite',-100),('reset',0),('refined',49)]:
    d=load(name);s=copy.deepcopy(defaults);s['aberration']=value;expected=copy.deepcopy(base);expected['layers'][0]['photo']=dict(settings=s,normal=s,look='custom',lookActive=False);assert d==expected
    if name!='refined':
        a=load(name,'png');images[name]=a;metrics[name]=verify_geometry(a,raw,s);assert np.array_equal(a[:,:,3],raw[:,:,3]) and np.array_equal(a[:,:,1],raw[:,:,1])
assert np.array_equal(images['reset'],raw) and np.array_equal(load('reopened','png'),images['corrected'])
def edge_positions(a):
    result=[]
    for axis,lo,hi in [('x',80,120),('x',160,200),('x',760,800),('x',840,880),('y',80,112),('y',528,560)]:
        positions=[]
        for channel in range(3):
            profile=a[320,lo:hi+1,channel] if axis=='x' else a[lo:hi+1,140,channel];gradient=abs(np.diff(profile.astype(float)));assert gradient.sum()>200;positions.append(float(np.sum((np.arange(lo,hi)+.5)*gradient)/gradient.sum()))
        result.append(positions)
    return np.array(result)
positions={n:edge_positions(a) for n,a in [('source',raw),('corrected',images['corrected']),('opposite',images['opposite'])]};spread={n:np.ptp(p,axis=1) for n,p in positions.items()};assert np.all(spread['source']>2) and np.all(spread['corrected']<.1);assert np.all(spread['opposite']>spread['source']*1.8)
assert np.array_equal(images['corrected'][200:440,300:660],raw[200:440,300:660]);assert np.array_equal(images['corrected'][160:480,112:168],raw[160:480,112:168])
report=dict(status='Pass',known_horizontal_and_vertical_RGB_edge_offsets_corrected_spatially=True,all_six_edge_channel_spreads={n:p.tolist() for n,p in spread.items()},opposite_direction_makes_separation_worse=True,every_Green_pixel_exact_source_no_global_blur=True,flat_black_and_grey_regions_exact_no_global_hue_shift=True,alpha_every_pixel_exact=True,actual_saved_reopen_PNG_exact_value100_editable_to49=True,source_frame_other_recipe_fields_exact=True,reset_every_RGBA_exact=True,metrics=metrics,sha256=hashes)
(out/'fringe143-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native spatial RGB fringe alignment, unchanged Green/alpha, saved refinement and exact reset')
