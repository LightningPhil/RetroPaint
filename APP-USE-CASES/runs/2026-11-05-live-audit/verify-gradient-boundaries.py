"""Native gradient area oracle: exact modal stops, smoothness, scope and state."""
from pathlib import Path
from PIL import Image
from collections import Counter
import base64,copy,hashlib,io,json,math,numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';plan=json.loads((root/'test-results/audit-2026-11-05/fixtures/gradient50/plan.json').read_bytes());e=json.loads((out/'gradient50-evidence.json').read_bytes());hashes={}
def actual(label,ext='retropaint'):
    name='mouse-audit-gradient50-'+label+'.'+ext;b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(label):return json.loads(actual(label))
def pixels(d,i=1):return np.array(Image.open(io.BytesIO(base64.b64decode(d['layers'][i]['image'].split(',',1)[1]))).convert('RGBA'))
def rgb(s):return [int(s[i:i+2],16) for i in [1,3,5]]
def endpoint_area(a,wanted):
    colours=Counter(map(tuple,a.reshape(-1,4)));expected=tuple(wanted+[255]);assert colours.most_common(1)[0][0]==expected and colours[expected]>a.shape[0]*a.shape[1]//2
before=doc('before');base=pixels(before);mask=np.zeros((240,320),bool);mask[21:140,21:140]=True;results=[]
def scope(d,area=mask):
    scoped=copy.deepcopy(before);scoped['layers'][1]['image']=d['layers'][1]['image'];assert scoped==d
    a=pixels(d);assert np.array_equal(a[~area],base[~area]);assert np.all(a[area,3]==255);return a
def png_exact(label,d):
    a=np.array(Image.open(io.BytesIO(actual(label,'png'))).convert('RGBA'));expected=np.array(Image.alpha_composite(Image.fromarray(pixels(d,0)),Image.fromarray(pixels(d))));assert np.array_equal(a,expected);return a
assert len(e['presets'])==len(e['tiny'])==4
for name,hexes in plan['presets'].items():
    d=doc(name);a=scope(d);assert doc(name+'-undone')==before and doc(name+'-reopened')==d
    assert np.array_equal(png_exact(name,d),png_exact(name+'-reopened',d))
    modes=np.array([Counter(map(tuple,a[21:140,x,:3])).most_common(1)[0][0] for x in range(21,140)])
    stop_results=[];step=90//(len(hexes)-1)
    for i,h in enumerate(hexes):
        x=30+i*step;column=a[21:140,x,:3];counts=Counter(map(tuple,column));wanted=tuple(rgb(h));assert counts.most_common(1)[0][0]==wanted and counts[wanted]>len(column)//2
        stop_results.append({'x':x,'exact_RGB':list(wanted),'exact_pixels_in_119_pixel_column':counts[wanted]})
    # Dithering can make individual columns alternate by one byte even for
    # a channel changing only two bytes over thirty pixels. Compare thirds
    # of each segment as areas, plus the analytic bound on adjacent jumps.
    for i in range(len(hexes)-1):
        segment=modes[30+i*step-21:30+(i+1)*step-21+1].astype(int);delta=np.diff(segment,axis=0);difference=np.array(rgb(hexes[i+1]))-rgb(hexes[i])
        for c,diff in enumerate(difference):
            areas=[float(part.mean()) for part in np.array_split(a[21:140,30+i*step:30+(i+1)*step,c],3,axis=1)]
            if diff:assert np.all(np.diff(areas)*(1 if diff>0 else -1)>=0),(name,i,c,areas)
            else:assert np.all(segment[:,c]==rgb(hexes[i])[c]),(name,i,c)
            assert np.max(np.abs(delta[:,c]))<=math.ceil(abs(diff)/step)+1
    tiny=doc('tiny-'+name);area=np.zeros((240,320),bool);area[181,181]=True;tiny_pixels=scope(tiny,area);assert np.any(tiny_pixels[181,181]!=base[181,181]);assert doc('tiny-'+name+'-undone')==before
    results.append({'name':name,'exact_modal_stops':stop_results,'ordered_smooth_channel_progression':True,'untouched_mask_exterior_and_other_layer_exact':True,'one_pixel_region_successful':True,'native_project_PNG_reopen_exact':True})
assert doc('custom-cancelled')==before
settled=doc('custom-settled');a=scope(settled);assert doc('custom-undone')==before and doc('custom-redone')==settled==doc('custom-reopened')
assert np.array_equal(png_exact('custom-settled',settled),png_exact('custom-reopened',settled))
# Farther along the moved diagonal, both pure endpoints remain in the mask.
endpoint_area(a[21:26,21:26],rgb(plan['custom']['from']));endpoint_area(a[135:140,135:140],rgb(plan['custom']['to']))
tool=doc('toolchange-saved');b=scope(tool);assert doc('toolchange-undone')==before;png_exact('toolchange-saved',tool)
endpoint_area(b[21:140,21:30],rgb(plan['custom']['from']));endpoint_area(b[21:140,122:140],rgb(plan['custom']['to']));assert not np.array_equal(a,b)
zero=doc('zero-length');z=scope(zero);expected=base.copy();expected[mask]=rgb(plan['custom']['to'])+[255];assert np.array_equal(z,expected)
nextdoc=doc('zero-length-next');expected[40:80,220:260]=rgb(plan['custom']['to'])+[255];assert np.array_equal(pixels(nextdoc),expected);assert doc('zero-length-next-undone')==zero and doc('zero-length-undone')==before
report={'status':'Pass','presets':results,'custom_moved_pins_exact_modal_endpoint_colours_and_changed_direction':True,'Escape_whole_project_exact':True,'save_settles_once_Undo_Redo_exact':True,'tool_change_then_save_settles_one_visible_result_no_hidden_preview':True,'zero_length_defined_solid_Blue_fallback_next_gesture_and_Undo_exact':True,'dithering_oracle':'Retained initial single-row exact-stop failure. Declared stop RGB is exact unique modal colour and strict majority in each constant-gradient119pixelcolumn and each custom endpoint area. Third-segment area averages progress in the expected direction; constant-channel modes stayexact; analytic adjacent jump bound checks smoothness. Initial pointwise monotonic hypothesis also failed: OceanRchangesonly2bytesover30pixels, so dither alternates1byte. No widened colour equality; exact source/exterior/history/project/PNG comparisons remain rawRGBA.','sha256':hashes}
(out/'gradient50-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Pass: 4 full/tiny presets; exact modal stops, smooth order; custom pins/Escape/save/toolchange/zero-length/history/native reopens')
