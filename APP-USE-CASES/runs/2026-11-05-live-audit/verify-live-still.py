"""Independent conveyor/water phases in a multilayer Photo-adjusted PNG frame."""
from pathlib import Path
from PIL import Image
import base64,hashlib,io,json,math,numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';viewer=json.loads((out/'still47-viewer-evidence.json').read_bytes());hashes={}
def actual(label,ext='retropaint'):
    name='mouse-audit-still47-'+label+'.'+ext;b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
before=json.loads(actual('before'));assert before==json.loads(actual('after'))==json.loads((downloads/'mouse-audit-project44-mixed-before.retropaint').read_bytes());assert len(before['layers'])==4 and all(l['visible'] for l in before['layers'])
frames={}
for time in [12345,23456]:
    image=Image.open(io.BytesIO(actual('time'+str(time),'png')));assert image.format=='PNG' and not getattr(image,'is_animated',False) and getattr(image,'n_frames',1)==1;assert image.size==(960,640);frames[time]=np.array(image.convert('RGBA'))
    reference=np.array(Image.open(downloads/f'mouse-audit-project44-mixed-time{time}.png').convert('RGBA'));assert np.array_equal(frames[time],reference)
layer=before['layers'][1];assert layer['photo']['settings']['exposure']==1 and layer['opacity']==1;assert len(layer['live']['strokes'])==1 and len(layer['live']['fills'])==2
def exposure(rgb):
    result=[]
    for c in rgb:
        s=c/255;linear=s/12.92 if s<=.04045 else ((s+.055)/1.055)**2.4;linear=min(1,linear*2);encoded=12.92*linear if linear<=.0031308 else 1.055*linear**(1/2.4)-.055;result.append(math.floor(encoded*255+.5))
    return result
def nearest_water_line(x,y,time):
    shift=time*.04%64;best=(1e6,None)
    for row in range(0,64,8):
        for left in range(0,64,4):
            top=row+math.sin((left+shift)*.2)*3;dy=math.sin((left+4+shift)*.2)*3+row-top;t=max(0,min(1,((x-left)*4+(y-top)*dy)/(16+dy*dy)));distance=math.hypot(x-left-t*4,y-top-t*dy)
            if distance<best[0]:best=(distance,row)
    return best
# Select an unambiguous flat stroke/background pair using only wave geometry,
# before consulting any rendered pixels. The two fills have disjoint masks here.
point=None
for x in range(780,890):
    for y in range(472,498):
        a=nearest_water_line(x%64+.5,y%64+.5,12345);b=nearest_water_line(x%64+.5,y%64+.5,23456)
        if a[0]<.6 and b[0]>2.3:point=(x,y,a,b);break
    if point:break
assert point;x,y,a,b=point;line_rgb=[202,240,248] if a[1]%16==0 else [72,202,228];water=[]
for index,py in [(0,y),(1,y+64)]:
    for j,fill in enumerate(layer['live']['fills']):
        assert fill['spec']['kind']=='texture' and fill['spec']['texture']=='water' and fill['opacity']==1 and fill['gradient'] is None
        mask=Image.open(io.BytesIO(base64.b64decode(fill['mask'].split(',',1)[1]))).convert('RGBA');assert mask.getpixel((x,py))[3]==(255 if index==j else 0)
    for time,colour in [(12345,exposure(line_rgb)),(23456,exposure([0,119,182]))]:assert list(frames[time][py,x])==colour+[255]
    water.append({'fill':index,'point':[x,py],'RGB_at12345':exposure(line_rgb),'RGB_at23456':exposure([0,119,182])})
stroke=layer['live']['strokes'][0];assert stroke['spec']['kind']=='conveyor' and stroke['spec']['speed']==3 and stroke['spec']['mode']=='ooze';points=stroke['points'];distance=sum(math.hypot(b['x']-a['x'],b['y']-a['y']) for a,b in zip(points[:-2],points[1:-1]));colours=[[int(h[i:i+2],16) for i in [1,3,5]] for h in stroke['spec']['colors']];caps={}
for time,frame in frames.items():
    phase=(time*3*.0015+distance*.02)%len(colours);i=math.floor(phase);rgb=[math.floor(a+(b-a)*(phase-i)+.5) for a,b in zip(colours[i],colours[(i+1)%len(colours)])];expected=exposure(rgb);assert np.all(frame[383:388,798:803]==expected+[255]);caps[time]=expected
assert viewer['nativeAddressObserved'] and viewer['viewerClosed'] and viewer['tab']['url'].startswith('file:///') and '(960×640)' in viewer['tab']['title']
screens=[np.array(Image.open(out/f'still47-native-viewer-{s}.png').convert('RGB'))[284:924,399:1359] for s in ['a','b']];assert screens[0].shape==(640,960,3) and np.array_equal(screens[0],screens[1])
report={'status':'Pass','four_layer_project_all_editing_fields_unchanged_by_two_still_exports':True,'both_decoded_full_RGBA_frames_match_preserved_reference_exactly':True,'two_independently_masked_Water_fills_match_same_time_plus_1EV_oracle':water,'conveyor_end_cap_RGB_matches_same_time_plus_1EV_oracle':caps,'PNG_single_frame_not_animated':True,'native_separate_Chrome_image_viewer_shows_same_static_composition':True,'native_viewer_image_area_unchanged_between_two_captures':True,'only_temporary_viewer_tab_closed':True,'screen_scope':'Screen captures establish visible composition and lack of animation; independently decoded PNG bytes, not rescaled GUI pixels, are the colour oracle.','sha256':hashes}
(out/'still47-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
