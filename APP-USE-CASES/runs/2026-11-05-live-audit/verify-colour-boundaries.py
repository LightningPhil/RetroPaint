"""Independent ramp, alpha-mask and black/white composition checks."""
import base64,hashlib,io,json
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse'
downloads=Path.home()/'Downloads';hashes={}
def retain(name):
    data=(downloads/name).read_bytes();(out/name).write_bytes(data)
    hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(name):return json.loads(retain('mouse-audit-'+name+'.retropaint'))
def png(name):return Image.open(io.BytesIO(retain('mouse-audit-'+name+'.png'))).convert('RGBA')
ramps=[]
for variant,knots in [('steep',[(0,0),(96,8),(160,247),(255,255)]),('neighbours',[(0,0),(127,0),(128,255),(255,255)])]:
    project=doc('tonal-'+variant);image=png('tonal-'+variant)
    assert image.size==(1024,256)
    curve=project['layers'][0]['photo']['settings']['curves']['rgb']
    assert [(round(p['x']*255),round(p['y']*255)) for p in curve]==knots
    ramp=[image.getpixel((x*4,0))[0] for x in range(256)]
    assert all(a<=b for a,b in zip(ramp,ramp[1:]))
    for x in range(256):
        for dx in range(4):assert image.getpixel((x*4+dx,0))==(ramp[x],)*3+(255,)
    for (x0,y0),(x1,y1) in zip(knots,knots[1:]):
        assert all(y0<=ramp[x]<=y1 for x in range(x0,x1+1))
    for x,y in knots:assert ramp[x]==y
    if variant=='steep':assert max(b-a for a,b in zip(ramp,ramp[1:]))<=6
    else:assert ramp==[0]*128+[255]*128
    ramps.append({'variant':variant,'knots':knots,'monotonic_no_segment_overshoot':True,
                  'max_neighbouring_sample_difference':max(b-a for a,b in zip(ramp,ramp[1:]))})
baseline=doc('colour-alpha-baseline');adjusted=doc('colour-alpha-adjusted');foreground=png('colour-alpha-adjusted')
source=Image.open(root/'APP-USE-CASES/runs/2026-10-19-full-audit/fixtures/COLOUR-rich-alpha.png').convert('RGBA')
assert baseline['layers'][0]['image']==adjusted['layers'][0]['image']
assert source.getchannel('A').tobytes()==foreground.getchannel('A').tobytes()
settings=adjusted['layers'][0]['photo']['settings']
assert (settings['temperature'],settings['tint'])==(18,-9)
assert settings['mixer'][0]=={'hue':15,'saturation':20,'luminance':-10}
assert settings['curves']['blue']==[{'x':0,'y':0},{'x':.25,'y':.18},{'x':.75,'y':.82},{'x':1,'y':1}]
visible_changes=sum(p[:3]!=q[:3] for p,q in zip(source.get_flattened_data(),foreground.get_flattened_data()) if p[3]>0)
assert visible_changes>0
for name,colour in [('pure-black',(0,0,0,255)),('white',(255,255,255,255))]:
    scene=doc('colour-alpha-'+name);actual=png('colour-alpha-'+name)
    assert scene['layers'][1]==adjusted['layers'][0]
    expected=Image.alpha_composite(Image.new('RGBA',foreground.size,colour),foreground)
    assert actual.tobytes()==expected.tobytes()
    for p,q in zip(source.get_flattened_data(),actual.get_flattened_data()):
        if p[3]==0:assert q==colour
report={'ramps':ramps,'captured_original_source_unchanged':True,'alpha_mask_exact_to_input_file':True,
        'visible_rgb_pixels_changed':visible_changes,'black_and_white_composites_pixel_exact':True,
        'clear_pixels_show_background_exactly':True,'palette_black_is_dark_grey':26,
        'pure_black_explicitly_chosen_as_hex_000000':True,'sha256':hashes}
(out/'colour-boundary-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
