"""Known hue, grey, skin, cast, saturation and alpha samples with clear gutters."""
from pathlib import Path
import colorsys,hashlib,json
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/fixtures'
main=[('red',(255,0,0)),('orange',(255,128,0)),('yellow',(255,255,0)),('green',(0,255,0)),('aqua',(0,255,255)),('blue',(0,0,255)),('purple',(128,0,255)),('magenta',(255,0,255)),('grey32',(32,32,32)),('grey128',(128,128,128)),('grey224',(224,224,224)),('skin',(192,142,118))]
angles=[358,2,28,32,58,62,118,122,178,182,238,242,268,272,298,302]
boundary=[(f'hue{h}',tuple(round(c*255) for c in colorsys.hls_to_rgb(h/360,.5,1))) for h in angles]
extra=[('cast-grey',(154,123,109)),('dull-green',(100,140,105)),('vivid-green',(20,220,40)),('dull-blue',(100,110,150)),('vivid-blue',(20,40,230)),('dull-red',(160,110,105)),('vivid-red',(230,20,25)),('skin',(192,142,118))]
rows=[main,main,boundary[:12],boundary[12:]+extra,main[:3]+extra+main[9:10]]
image=Image.new('RGBA',(960,640));draw=ImageDraw.Draw(image);patches=[]
for row,(values,alpha) in enumerate(zip(rows,[255,128,255,64,192])):
    for col,(name,rgb) in enumerate(values):
        x=col*80+4;y=32+row*96;box=[x,y,x+71,y+79];draw.rectangle(box,fill=(*rgb,alpha));patches.append(dict(name=name,row=row,alpha=alpha,rgb=rgb,box=box,centre=[x+36,y+40]))
for i,(name,rgb) in enumerate([('black',(0,0,0)),('white',(255,255,255)),('cast-grey',(154,123,109)),('skin',(192,142,118))]):
    x=16+i*96;draw.rectangle((x,544,x+63,607),fill=(*rgb,255));patches.append(dict(name=name,row=5,alpha=255,rgb=rgb,box=[x,544,x+63,607],centre=[x+32,576]))
path=out/'colour107-patches.png';image.save(path)
cast=Image.new('RGBA',(960,640),(154,123,109,255));d=ImageDraw.Draw(cast)
for i,(name,rgb) in enumerate(main[:8]):d.rectangle((i*120,0,i*120+119,79),fill=(*rgb,255))
d.rectangle((0,608,959,639),fill=(0,0,0,0));castpath=out/'colour107-cast.png';cast.save(castpath)
report=dict(size=[960,640],patches=patches,alpha_levels=[0,64,128,192,255],files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,castpath]},cast_scene='Dominant known154,123,109grey with eight saturated colour strips at top80px and32pxclearbottom; no objective correction expected for every artistic scene.',input_oracle='Known opaque samples exact. On semi-transparent import/export, per-channel premultiplied8bit quantisation bound ceil(255/(2*alpha)); alpha exact. All subsequent source-document comparisons use actual canonical baseline bytes.')
(out/'colour107-manifest.json').write_text(json.dumps(report,indent=2)+'\n');print('Prepared known colour/skin/cast/hue-boundary samples, alpha copies and cast-dominant scene')
