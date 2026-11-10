"""Independent phase/pigment checks and complete static/live preservation."""
from pathlib import Path
from PIL import Image
import base64,copy,hashlib,io,json,math,numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';plan=json.loads((root/'test-results/audit-2026-11-05/fixtures/conveyor46-plan.json').read_bytes());e=json.loads((out/'conveyor46-evidence.json').read_bytes());hashes={}
assert plan['recorded_before_new_matrix_execution'] and e['finalReopened']
def actual(label,ext='retropaint',version=46):
    name=f'mouse-audit-conveyor{version}-'+label+'.'+ext;b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(label,version=46):return json.loads(actual(label,version=version))
def raster(d):return np.array(Image.open(io.BytesIO(base64.b64decode(d['layers'][0]['image'].split(',',1)[1]))).convert('RGBA'))
def validate_additions(previous,rows,colours):
    for row in rows:
        current=doc(row['label']);stroke=current['layers'][0]['live']['strokes'][-1];scoped=copy.deepcopy(previous);scoped['layers'][0]['live']['strokes'].append(stroke);assert scoped==current
        assert stroke['spec']=={'kind':'conveyor','colors':colours,'speed':row['speed'],'mode':row['mode'],'along':True,'texture':None}
        assert stroke['opacity']==1 and stroke['applicator']=='marker' and len(stroke['points'])>20
        for a,b in zip([stroke['points'][0]['x'],stroke['points'][0]['y'],stroke['points'][-1]['x'],stroke['points'][-1]['y']],row['start']+row['end']):assert abs(a-b)<.01
        assert all(abs(p['y']-row['start'][1])<.01 and p['w']==22 for p in stroke['points']);previous=current
    return previous
after_six=validate_additions(doc('after-rapid-switches'),plan['rows'],plan['eight'])
red=doc('ordinary-red');scoped=copy.deepcopy(after_six);scoped['layers'][0]['image']=red['layers'][0]['image'];assert scoped==red
after_three=validate_additions(doc('one-reopened',47),plan['three_rows'],plan['three'])
final=doc('ordinary-green');scoped=copy.deepcopy(after_three);scoped['layers'][0]['image']=final['layers'][0]['image'];assert scoped==final
assert final==doc('final-time23456')==doc('final-reopened') and len(final['layers'][0]['live']['strokes'])==11
frames={t:np.array(Image.open(io.BytesIO(actual(f'final-time{t}','png'))).convert('RGBA')) for t in plan['controlled_frames']}
for t in frames:assert np.array_equal(frames[t],np.array(Image.open(io.BytesIO(actual(f'final-reopened-time{t}','png'))).convert('RGBA')))
def rgb(h):return [int(h[i:i+2],16) for i in [1,3,5]]
def end_colour(stroke,time):
    points=stroke['points'];distance=sum(math.hypot(b['x']-a['x'],b['y']-a['y']) for a,b in zip(points[:-2],points[1:-1]));spec=stroke['spec'];phase=(time*spec['speed']*.0015+distance*.02)%len(spec['colors']);index=math.floor(phase);a=rgb(spec['colors'][index]);b=rgb(spec['colors'][(index+1)%len(spec['colors'])]);return a if spec['mode']=='snap' else [math.floor(x+(y-x)*(phase-index)+.5) for x,y in zip(a,b)]
yy,xx=np.indices((640,960));allowed=np.zeros((640,960),dtype=bool);initial_allowed=np.zeros((640,960),dtype=bool);results=[]
# Live Marker draws a 1.2x halo around a 1.06x slow-speed stroke. The first
# radius13 hypothesis omitted that intentional brush footprint. Retain its result
# separately, then use the analytic outer radius plus one antialias pixel.
marker_radius=22*1.06*1.2/2+1
for row in plan['rows']+plan['three_rows']:
    stroke=next(s for s in final['layers'][0]['live']['strokes'] if abs(s['points'][0]['x']-row['start'][0])<.01 and abs(s['points'][0]['y']-row['start'][1])<.01)
    x,y=row['end'];row_result={'label':row['label'],'speed':row['speed'],'mode':row['mode'],'opaque_end_cap_RGB':{}}
    for t,frame in frames.items():
        expected=end_colour(stroke,t);patch=frame[y-2:y+3,x-2:x+3];assert np.all(patch==expected+[255]),(row['label'],t,expected,patch[2,2].tolist());row_result['opaque_end_cap_RGB'][str(t)]=expected
    distance=np.sqrt((xx+.5-np.clip(xx+.5,row['start'][0],row['end'][0]))**2+(yy+.5-y)**2);mask=distance<=marker_radius
    changed=int(np.any(frames[12345][mask]!=frames[23456][mask],axis=1).sum());row_result['changed_pixels_between_times']=changed
    if row['speed']==0:assert changed==0
    else:assert changed>5000;allowed|=mask;initial_allowed|=distance<=13
    values=frames[12345][y,row['start'][0]+15:row['end'][0]-15,:3];palette=plan['three'] if row in plan['three_rows'] else plan['eight']
    if row['speed']==0 and row['mode']=='snap':assert all(np.any(np.all(values==rgb(c),axis=1)) for c in palette)
    if row['mode']=='ooze':assert sum(not any(np.array_equal(v,rgb(c)) for c in palette) for v in values)>50
    results.append(row_result)
initial_changed=int(np.any(frames[12345][~initial_allowed]!=frames[23456][~initial_allowed],axis=1).sum())
(out/'conveyor46-initial-footprint-hypothesis.json').write_text(json.dumps({'hypothesis':'Radius13boundsallvisibleLiveMarkerchanges','outside_changed_pixels':initial_changed,'hypothesis_failed':initial_changed>0,'independent_style_correction':'brush.ts paintMarker: width22 * slow pace1.06 * halo1.2 /2 =13.992radius, plus1pixelAA=14.992. This is a geometry-model correction, not a product pixel error or broadened colour tolerance. Exact end-cap pigments already pass at both times.','analytic_radius_including_AA':marker_radius},indent=2)+'\n',encoding='utf-8')
assert np.array_equal(frames[12345][~allowed],frames[23456][~allowed])
normal=[np.array(Image.open(io.BytesIO(actual(label,'png'))).convert('RGBA')) for label in ['walltime-a','walltime-b']]
assert int(np.any(normal[0]!=normal[1],axis=2).sum())>5000 and np.array_equal(normal[0][~allowed],normal[1][~allowed])
assert doc('normal-clock-unchanged')==final and e['normalFrames'][1]['observedAt']>e['normalFrames'][0]['observedAt']
for row in [plan['ordinary_before_live'],plan['ordinary_after_live']]:
    x0,y=row['start'];x1,_=row['end'];mask=np.sqrt((xx-np.clip(xx,x0,x1))**2+(yy-y)**2)<=9;assert np.all(raster(final)[mask]==row['RGB']+[255]);assert np.all(frames[12345][mask]==row['RGB']+[255]) and np.all(frames[23456][mask]==row['RGB']+[255])
assert [x['count'] for x in e['build']]==list(range(9)) and [x['remaining'] for x in e['removals']]==list(range(7,-1,-1))
for c in e['build']:assert sum(s['index'] is not None for s in c['slots'])==c['count']
for c in e['removals']:assert sum(s['index'] is not None for s in c['slots'])==c['remaining']
report={'status':'Pass','eight_stop_speed_mode_matrix_and_three_stop_modes':results,'all_zero_speed_bands_and_static_marks_RGBA_identical_between_times':True,'only_declared_nonzero_speed_capsules_change':True,'normal_clock_animates_without_drawing_while_whole_project_and_other_RGBA_remain_unchanged':True,'ordinary_Red_before_live_and_Green_after_disarming_remain_exact':True,'disarming_and_slot_removal_keep_all_eleven_existing_live_definitions':True,'all_counts_zero_through_eight_added_and_removed_natively':True,'whole_final_project_and_both_controlled_RGBA_frames_native_reopen_exact':True,'Live_marker_footprint_oracle':'Initialradius13/integer-gridmodelreported1916outsidechanges; retainedhypothesisfile. ActualpaintMarkerouterhalois22*1.06*1.2/2=13.992radius. Analyticboundsusepixelcentresplus1AApixel; alloutsidebytesexact. ExactRGBcaporacleneverrelaxed.','sha256':hashes}
(out/'conveyor46-matrix-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['sha256','eight_stop_speed_mode_matrix_and_three_stop_modes']},indent=2));print(json.dumps(results,indent=2))
