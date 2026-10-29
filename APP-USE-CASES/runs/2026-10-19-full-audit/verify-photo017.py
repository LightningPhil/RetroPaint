from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,base64,io,re,math
import numpy as np
root=Path(__file__).resolve().parent
folder=root/'headless/PHOTO-017-complete'
read=lambda name:json.loads((folder/name).read_text(encoding='utf-8'))
image=lambda name:np.asarray(Image.open(folder/name).convert('RGBA'))
decode=lambda layer:np.asarray(Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',',1)[1]))).convert('RGBA'))
ui=read('PHOTO-017-headless-ui.json')
assert ui['status']=='Pass' and not ui['errors'] and ui['fresh_reopen_complete']
assert len(ui['rows'])==6
labels=lambda value:tuple(map(int,re.search(r'(\d+)% shadow clipping; (\d+)% highlight clipping',value).groups()))
rows=[]
for row in ui['rows']:
    name=row['name'];fixture=root/'fixtures'/('TONAL.png' if name=='tonal-ramp' else 'HIST-'+name+'.png')
    source=np.asarray(Image.open(fixture).convert('RGBA'))
    before=read(name+'-before.retropaint');cancelled=read(name+'-cancelled.retropaint')
    assert before==cancelled and len(before['layers'])==1
    assert np.array_equal(decode(before['layers'][0]),source)
    assert np.array_equal(image(name+'-cancelled.png'),source)
    expected=(1,1) if name=='tonal-ramp' else (0,0)
    assert labels(row['states'][0]['label'])==expected
    rows.append(dict(name=name,source_rgba_exact=True,complete_cancelled_project_exact=True,full_size_cancelled_export_exact=True,original_clipping_percent=expected))
for name in ['nearly-black','nearly-white']:
    # Equal areas have alpha weights 255:1. The nearly clear extreme has
    # 1/256 of the total visible coverage, not half the content.
    assert math.floor(100/256+.5)==0
    before_ui=json.loads((root/'headless/PHOTO-017-before/PHOTO-017-headless-ui.json').read_text(encoding='utf-8'))
    failed=next(row for row in before_ui['rows'] if row['name']==name)
    assert labels(failed['states'][0]['label'])==((50,0) if name=='nearly-black' else (0,50))
assert not image('empty-histogram.png')[:,:,3].any(),'Empty histogram plotted nonzero bins'

def peak_positions(name,levels):
    chart=image(name+'.png');assert chart.shape==(48,256,4)
    sums=chart[:,:,3].sum(axis=0);positions=[]
    mask=np.zeros(256,dtype=bool)
    for channel,level in enumerate(levels):
        expected=level*256/255
        lo=max(0,math.floor(expected)-2);hi=min(256,math.ceil(expected)+3)
        x=lo+int(sums[lo:hi].argmax());assert abs(x-expected)<=2.01,(name,channel,x,expected)
        assert sums[x]>1000,'Expected histogram peak is absent'
        candidates=chart[:,lo:hi];pixel=candidates.reshape(-1,4)[int(candidates[:,:,3].argmax())]
        assert int(pixel[:3].argmax())==channel,'Histogram peak has the wrong channel colour'
        positions.append(x);mask[lo:hi]=True
    assert sums[~mask].sum()==0,'Unexpected bins were plotted for a uniform RGB source'
    return positions
source_levels=np.array([64,128,192],dtype=np.float64)
encoded=source_levels/255;light=np.where(encoded<=.04045,encoded/12.92,((encoded+.055)/1.055)**2.4)*2
light=np.clip(light,0,1);exposed=np.rint(np.where(light<=.0031308,12.92*light,1.055*light**(1/2.4)-.055)*255).astype(int)
original_peaks=peak_positions('rgb-flat-histogram',source_levels)
after_peaks=peak_positions('rgb-flat-after',exposed)
assert np.array_equal(image('rgb-flat-histogram.png'),image('rgb-flat-before-comparison.png'))
assert np.array_equal(image('rgb-flat-after.png'),image('rgb-flat-after-comparison.png'))
rgb=next(row for row in ui['rows'] if row['name']=='rgb-flat')
assert [labels(state['label']) for state in rgb['states']]==[(0,0),(0,100),(0,0),(0,100)]

tonal=next(row for row in ui['rows'] if row['name']=='tonal-ramp')
source=np.asarray(Image.open(root/'fixtures/TONAL.png').convert('RGBA'))
output=image('tonal-ramp-exposure-1.png')
encoded=source[:,:,:3].astype(np.float64)/255
light=np.clip(np.where(encoded<=.04045,encoded/12.92,((encoded+.055)/1.055)**2.4)*2,0,1)
expected=np.rint(np.where(light<=.0031308,12.92*light,1.055*light**(1/2.4)-.055)*255).astype(np.uint8)
error=int(np.abs(output[:,:,:3].astype(np.int16)-expected.astype(np.int16)).max());assert error<=1
assert np.array_equal(output[:,:,3],source[:,:,3])
counts=(math.floor(100*np.mean(np.min(output[:,:,:3],axis=2)<=1)+.5),math.floor(100*np.mean(np.max(output[:,:,:3],axis=2)>=254)+.5))
actual=labels(tonal['full_export_preview_label'])
# A 720px preview samples a 1024px ramp. One source bin occupies 0.39%;
# allow a declared one percentage point difference at a clipping boundary.
assert all(abs(a-b)<=1 for a,b in zip(actual,counts)),(actual,counts)
before=read('tonal-ramp-before.retropaint');committed=read('tonal-ramp-exposure-1.retropaint')
assert committed['layers'][0]['photo']['settings']['exposure']==1
assert np.array_equal(decode(committed['layers'][0]),source)
assert before==read('tonal-ramp-undone.retropaint')
assert np.array_equal(image('tonal-ramp-undone.png'),source)
assert committed==read('tonal-ramp-redone.retropaint')==read('fresh/tonal-ramp-reopened.retropaint')
assert np.array_equal(output,image('tonal-ramp-redone.png')) and np.array_equal(output,image('fresh/tonal-ramp-reopened.png'))
events=read('events.json')+read('fresh/events.json')
downloads=[event for event in events if event['action']=='download'];assert len(downloads)==26
result=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,execution='Isolated headless production UI; actual file inputs, controls, public histogram canvas pixels and downloads',rows=rows,nearly_transparent_clipping_before_percent=50,nearly_transparent_clipping_after_percent=0,opacity_weighted_expected_percent=100/256,original_rgb_levels=source_levels.tolist(),original_peak_columns=original_peaks,exposed_rgb_levels=exposed.tolist(),exposed_peak_columns=after_peaks,peak_position_tolerance_pixels=2.01,before_after_histogram_restoration_exact=True,empty_histogram_and_warnings_zero=True,full_size_exposure_oracle_max_error_255=error,full_size_clipping_percent=counts,preview_clipping_percent=actual,declared_preview_clipping_percent_tolerance=1,undo_redo_and_fresh_project_reopen_exact=True,actual_downloads_verified=len(downloads),original_source_and_complete_cancelled_documents_exact=True,transfer_equation_source='https://www.w3.org/TR/2026/CRD-css-color-4-20261009/#predefined-sRGB')
(root/'evidence/PHOTO-017-independent-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
