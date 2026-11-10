"""Independent real-file decoders, alpha/matte budgets, GIF palette, main Save."""
from pathlib import Path
from PIL import Image,ImageDraw
import base64,copy,hashlib,io,json,math
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
e=json.loads((out/'format43-evidence.json').read_bytes());plan=json.loads((root/'test-results/audit-2026-11-05/fixtures/format-plan43.json').read_bytes());assert plan['recorded_before_execution'] and len(e['cases'])==8 and len(e['reimports'])==6
def actual(name):
 b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(name):return json.loads(actual(name+'.retropaint'))
def image(b):return Image.open(io.BytesIO(b)).convert('RGBA')
def source(layer):return image(base64.b64decode(layer['image'].split(',')[1]))
def same(a,b):assert a.size==b.size and a.tobytes()==b.tobytes()
before=doc('mouse-audit-format43-patch-before');assert len(before['layers'])==2 and not before['layers'][0]['visible'] and before['layers'][1]['visible'];patch=source(before['layers'][1]);s=np.array(patch).astype(int);white=Image.new('RGBA',patch.size,'white');white.alpha_composite(patch);w=np.array(white).astype(int);results=[];decoded={}
exts={'png':'png','webp':'webp','tiff':'tif','jpeg':'jpg','bmp':'bmp','gif':'gif'}
for fmt,ext in exts.items():
 b=actual(f'mouse-audit-format43-patch-{fmt}.{ext}');opened=Image.open(io.BytesIO(b));assert opened.format=={'png':'PNG','webp':'WEBP','tiff':'TIFF','jpeg':'JPEG','bmp':'BMP','gif':'GIF'}[fmt] and opened.size==(960,640)
 im=opened.convert('RGBA');a=np.array(im).astype(int);decoded[fmt]=im;assert doc(f'mouse-audit-format43-patch-{fmt}-after')==before
 stats={'format':fmt,'decoded_type':opened.format,'dimensions':[960,640],'editable_project_unchanged':True}
 if fmt in ('png','tiff','webp'):
  assert np.array_equal(a[:,:,3],s[:,:,3]);stats['alpha_every_pixel_exact']=True
  if fmt in ('png','tiff'):same(im,patch);stats['all_RGBA_exact']=True
  else:
   stats['actual_all_RGBA_exact']=np.array_equal(a,s);stats['bitstream_chunk']=b[12:16].decode('ascii');assert np.array_equal(a,s)
 if fmt in ('jpeg','bmp'):
  assert np.all(a[:,:,3]==255);error=abs(a[:,:,:3]-w[:,:,:3]);stats['RGB_MAE']=float(error.mean());stats['RGB_max_error']=int(error.max())
  if fmt=='bmp':same(im,white);assert opened.mode=='RGB'
  else:
   mse=float((error*error).mean());stats['PSNR_dB']=10*math.log10(255**2/mse);assert stats['RGB_MAE']<=3 and stats['PSNR_dB']>=32;assert np.all(abs(a[500,600,:3]-255)<=2)
 if fmt in ('jpeg','webp'):
  interior=[]
  for x,y in [(100,100),(400,100),(100,300),(400,300)]:
   target=w if fmt=='jpeg' else s;error=abs(a[y+8:y+72,x+8:x+92,:3]-target[y+8:y+72,x+8:x+92,:3]);assert error.mean()<=3 and error.max()<=8;interior.append({'at':[x,y],'MAE':float(error.mean()),'max':int(error.max())})
  stats['patch_interiors']=interior
 if fmt=='gif':
  assert opened.n_frames==1 and len(opened.getpalette())//3<=256 and set(np.unique(a[:,:,3]))<={0,255};assert np.array_equal(a[:,:,3],np.where(s[:,:,3]<128,0,255));stats.update(still_frames=1,palette_entries=len(opened.getpalette())//3,binary_alpha_threshold=128)
 re=doc('mouse-audit-format43-reimport-'+fmt);assert (re['width'],re['height'],len(re['layers']))==(960,640,1);ri=source(re['layers'][0]);rendered=image(actual('mouse-audit-format43-reimport-'+fmt+'.png'))
 if fmt=='jpeg':
  diff=abs(np.array(ri).astype(int)-a);assert diff[:,:,:3].mean()<=1 and diff[:,:,:3].max()<=5;stats['native_decode_RGB_MAE']=float(diff[:,:,:3].mean());stats['native_decode_RGB_max']=int(diff[:,:,:3].max());same(ri,rendered)
 else:same(ri,im);same(ri,rendered)
 stats['native_open_image_roundtrip_verified']=True;results.append(stats)
colour=doc('mouse-audit-format43-colour-before');assert colour==doc('mouse-audit-format43-colour-gif-after')==doc('mouse-audit-format43-colour-png-after');cs=np.array(source(colour['layers'][0])).astype(int)
b=actual('mouse-audit-format43-colour-gif.gif');gif=Image.open(io.BytesIO(b));cg=gif.convert('RGBA');g=np.array(cg).astype(int);assert gif.n_frames==1 and len(gif.getpalette())//3==256 and np.array_equal(g[:,:,3],np.where(cs[:,:,3]<128,0,255));opaque=cs[:,:,3]==255;error=abs(g[:,:,:3]-cs[:,:,:3]);maximum=error[opaque].max(axis=0);assert np.all(maximum<=[37,37,85]);assert len(np.unique(cs[:,:,:3][opaque],axis=0))>256
re=doc('mouse-audit-format43-reimport-colour-gif');same(source(re['layers'][0]),cg);same(image(actual('mouse-audit-format43-reimport-colour-gif.png')),cg)
gif_stats={'palette_entries':256,'frames':1,'binary_alpha_exact':True,'opaque_max_RGB_error':maximum.tolist(),'opaque_RGB_MAE':error[opaque].mean(axis=0).tolist(),'changed_opaque_pixels':int(np.any(error!=0,axis=2)[opaque].sum()),'limitation':'Still GIF with a256entry8x8x4palette andbinaryalpha. Partialalpha becomesclearoropaque; no truecolour, exactblack, oranimation promise.'}
main_before=doc('mouse-audit-save43-mix-before');assert main_before==doc('mouse-audit-save43-mix-after') and len(main_before['layers'])==4 and main_before['layers'][2]['opacity']==.5
main=image((out/'save43-main-button.png').read_bytes());same(main,image(actual('mouse-audit-save43-main-reopened.png')));same(source(doc('mouse-audit-save43-main-reopened')['layers'][0]),main)
composite=Image.new('RGBA',(960,640));stamp=None
for layer in main_before['layers']:
 if not layer['visible']:continue
 part=source(layer)
 if layer['opacity']!=1:part.putalpha(part.getchannel('A').point(lambda a:math.floor(a*layer['opacity']+.5)))
 composite.alpha_composite(part)
 if layer.get('objects'):assert len(layer['objects'])==1;stamp=layer['objects'][0]
assert stamp and stamp['kind']=='stamp' and stamp['emoji']=='🐶';mask=np.ones((640,960),bool);m=stamp['matrix'];left=math.floor(m[4])-2;top=math.floor(m[5])-2;right=math.ceil(m[4]+stamp['width'])+2;bottom=math.ceil(m[5]+stamp['height'])+2;mask[top:bottom,left:right]=False
expected=np.array(composite);shown=np.array(main);assert np.array_equal(expected[mask],shown[mask]);assert np.any(expected[~mask]!=shown[~mask]);assert tuple(shown[140,150])==(143,68,114,255) and tuple(shown[340,150])==(15,196,114,255)
assert e['mainSave']['overlays']=={'rulers':True,'pixelGrid':True,'selection':True}
photo=doc('mouse-audit-save43-photo-before');assert photo==doc('mouse-audit-save43-photo-after')==doc('mouse-audit-save43-photo-reopened');assert photo['layers'][1]['photo']['settings']['exposure']==1
scope=copy.deepcopy(main_before);scope['active']=photo['active'];scope['layers'][1]['photo']=photo['layers'][1]['photo'];assert scope==photo
photo_composite=Image.new('RGBA',(960,640))
for i,layer in enumerate(photo['layers']):
 part=source(layer)
 if i==1:
  arr=np.array(part);v=arr[:,:,:3]/255;linear=np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)*2;linear=np.clip(linear,0,1);v=np.where(linear<=.0031308,linear*12.92,1.055*linear**(1/2.4)-.055);arr[:,:,:3]=np.floor(v*255+.5).clip(0,255).astype('uint8');part=Image.fromarray(arr)
 if layer['opacity']!=1:part.putalpha(part.getchannel('A').point(lambda a:math.floor(a*layer['opacity']+.5)))
 photo_composite.alpha_composite(part)
photo_png=image((out/'save43-photo-main-button.png').read_bytes());same(photo_png,image(actual('mouse-audit-save43-photo-reopened.png')));pa=np.array(photo_png);pe=np.array(photo_composite);assert np.array_equal(pa[mask],pe[mask]);assert tuple(pa[500,500])==(45,186,255,255)
sheet=Image.new('RGB',(840,1240),'#ddd');draw=ImageDraw.Draw(sheet)
for row,(name,im) in enumerate([('PNG',decoded['png']),('WebP',decoded['webp']),('TIFF',decoded['tiff']),('GIF binary alpha',decoded['gif'])]):
 for col,bg in enumerate(['black','white']):
  canvas=Image.new('RGBA',im.size,bg);canvas.alpha_composite(im);canvas=canvas.convert('RGB').resize((400,267));x=10+col*420;y=10+row*310;draw.text((x,y),name+' over '+bg,fill='black');sheet.paste(canvas,(x,y+24))
sheet.save(out/'format43-contrasting-backgrounds.png')
report={'status':'Pass','formats':results,'colour_rich_GIF':gif_stats,'main_toolbar_Save':'ActualdownloadPNG960x640.4layerMIXhalfCharacter composite exactoutsideanalyticDogstampbounds; correctRed/Greenopacitypixels. Rulers,selectionhandles,desk/cursorabsent. Projectunchanged; actualOpenimagePNG roundtrip exact. Dogdefinition/geometryretainedandvisuallyverifiedseparately.','saved_Photo_lab_exposure_in_export':'Backdrop+1EV gives45,186,255 fromindependentlinear-sRGBdoubling. FullcompositeexactoutsideanalyticDogbounds; rawsourcepixels/otherlayersunchanged; sourceprojectbefore/afterSave/nativeprojectreopenexact; PNGbefore/afterreopenexact.','predeclared_plan':'fixtures/format-plan43.json','sha256':hashes};(out/'format43-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['sha256','formats']},indent=2))
