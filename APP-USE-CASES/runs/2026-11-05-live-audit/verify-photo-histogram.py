"""Independent native graph peaks, clipping coverage, comparison and empty result."""
from pathlib import Path
import hashlib,json,re
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';u=json.loads((out/'photo106-ui.json').read_text());hashes={}
source=np.array(Image.open(root/'test-results/audit-2026-11-05/fixtures/TONAL-alpha.png').convert('RGBA')).astype(int);after=np.array(Image.open(out/'mouse-audit-photo99-exposure-plus1.png').convert('RGBA')).astype(int)
def clipping(a):
    weight=a[:,:,3]/255;count=weight.sum();return [np.sum(weight[np.min(a[:,:,:3],axis=2)<=1])/count*100,np.sum(weight[np.max(a[:,:,:3],axis=2)>=254])/count*100] if count else [0,0]
def shown(text):return list(map(int,re.findall(r'(\d+)%',text)))
for field,a in [('baseline',source),('before',source),('plus1',after),('after',after)]:assert all(abs(x-y)<=1 for x,y in zip(shown(u['desktop'][field]),clipping(a)))
assert shown(u['desktop']['empty'])==[0,0]
def graph(name,rect):
    a=np.array(Image.open(out/f'photo106-fixed-{name}.jpg')).astype(int);x=round(rect['x']);y=round(rect['y']);return a[y:y+79,x:x+round(rect['width'])] # Exclude the cosmetic bottom border.
r=u['desktop']['rect'];before=graph('baseline',r);assert np.array_equal(before,graph('before',r));bright=graph('plus1',r)
def height(a,value):
    x=round(value/256*a.shape[1]);ink=a.mean(axis=2)<245 # White plot background; bars darken it even after JPEG chroma subsampling.
    return int(ink[:,max(0,x-2):min(a.shape[1],x+3)].any(axis=1).sum())
baseline_peaks={v:height(before,v) for v in [32,64,128,192,224]};assert all(h>=75 for h in baseline_peaks.values());assert height(before,96)<25
exposed_peaks={v:height(bright,v) for v in [47,90,176,255]};assert all(exposed_peaks[v]>=30 for v in [47,90,176]) and exposed_peaks[255]>=75;assert height(bright,32)<15
assert not (graph('empty',u['desktop']['emptyRect']).mean(axis=2)<245).any()
for row,size in zip(u['compact'],[(320,568),(390,844),(844,390)]):
    assert row['viewport']==dict(width=size[0],height=size[1]);assert row['chart']['width']>=180 and row['chart']['height']>=60;assert shown(row['before'])==[1,1] and shown(row['after'])==[0,31]
for name in ['controls-cancelled','empty']:
    filename=f'mouse-audit-photo106-{name}.retropaint';data=(downloads/filename).read_bytes();(out/filename).write_bytes(data);hashes[filename]=hashlib.sha256(data).hexdigest()
assert json.loads((out/'mouse-audit-photo106-controls-cancelled.retropaint').read_text())==json.loads((downloads/'mouse-audit-photo99-tonal-baseline.retropaint').read_text())
empty=json.loads((out/'mouse-audit-photo106-empty.retropaint').read_text());assert (empty['width'],empty['height'])==(1024,256)
report=dict(status='Pass',independent_visible_coverage_clipping=True,baseline_known_neutral_peak_heights=baseline_peaks,plus_one_EV_peak_heights=exposed_peaks,white_endpoint_bin_full_height=True,Before_graph_pixels_exact_to_original=True,empty_plot_and_counts_zero=True,expanded_view_native_on_all_four_layouts=True,controls_cancel_whole_document_exact=True,excluded_initial_responsive_attempts='Viewport remained1757x909 after fresh tab closed; not counted. Current build reopened in original selected audit tab; exact CSS sizes verified.',sha256=hashes)
(out/'photo106-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native readable histogram, known shifted peaks, clipping counts, empty input and compact comparison')
