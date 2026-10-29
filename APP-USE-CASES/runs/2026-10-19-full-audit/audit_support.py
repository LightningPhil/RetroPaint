from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import base64, csv, hashlib, io, json, platform, subprocess, struct, math, zipfile
from PIL import Image, ImageDraw, ImageOps, ImageChops

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]

def sha(data): return hashlib.sha256(data).hexdigest()
def save_json(path,value): path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def verify_backup():
    path=ROOT/'backups/artwork-before-acceptance-audit.retropaint'
    raw=path.read_bytes(); doc=json.loads(raw)
    assert doc['format']=='RetroPaint' and doc['version']==10
    assert (doc['width'],doc['height'])==(960,640)
    assert len(doc['layers'])==4
    records=[]
    for layer in doc['layers']:
        encoded=layer['image']; assert encoded.startswith('data:image/png;base64,')
        binary=base64.b64decode(encoded.split(',',1)[1],validate=True)
        image=Image.open(io.BytesIO(binary));image.load()
        assert image.size==(960,640)
        rgba=image.convert('RGBA')
        records.append(dict(id=layer['id'],name=layer['name'],size=image.size,encoded_sha256=sha(binary),decoded_rgba_sha256=sha(rgba.tobytes()),visible=layer['visible'],opacity=layer['opacity'],cad=layer.get('cad')))
    report=dict(saved_at=datetime.now(timezone.utc).isoformat(),source='Actual download from live RetroPaint CAD Project button',file=str(path),bytes=len(raw),sha256=sha(raw),format=doc['format'],version=doc['version'],dimensions=[doc['width'],doc['height']],active=doc['active'],layers=records,independent_decoder='Pillow '+Image.__version__,reopen_status='Pending actual app input round trip')
    save_json(ROOT/'backups/verification.json',report)
    print(json.dumps({k:v for k,v in report.items() if k!='layers'},indent=2))

def fixture_files():
    folder=ROOT/'fixtures';folder.mkdir(exist_ok=True)
    p=Image.new('RGBA',(960,640),(0,0,0,0));d=ImageDraw.Draw(p)
    for box,colour in [((100,100,199,179),(255,0,0,255)),((400,100,499,179),(0,0,255,255)),((100,300,199,379),(0,255,0,255)),((400,300,499,379),(255,0,0,128))]:d.rectangle(box,fill=colour)
    p.save(folder/'PATCH.png')
    p.save(folder/'PATCH-rgba.tif',compression='raw')
    p.convert('RGB').save(folder/'PATCH-rgb.tif',compression='raw')
    p.convert('L').save(folder/'PATCH-grey.tif',compression='raw')
    background=Image.new('RGB',p.size,'white');background.paste(p,mask=p.getchannel('A'))
    for name,fmt in [('PATCH.jpg','JPEG'),('PATCH.bmp','BMP'),('PATCH.gif','GIF')]:background.save(folder/name,format=fmt)
    p.save(folder/'PATCH.webp',lossless=True)
    px=Image.new('RGBA',(32,32),'white');dd=ImageDraw.Draw(px)
    for n in range(2,16):dd.point((n,n),fill='black')
    dd.line((20,2,20,25),fill='red',width=1)
    for y in range(4):
        for x in range(4):dd.point((x+2,y+24),fill='blue' if (x+y)%2 else 'white')
    px.save(folder/'PIXEL.png')
    fill=Image.new('RGBA',(320,240),'white');fd=ImageDraw.Draw(fill);fd.rectangle((20,20,140,140),fill='#e8e8e8',outline='black',width=1);fd.rectangle((220,40,259,79),fill='#e8e8e8');fill.save(folder/'FILL-closed.png')
    fill.putpixel((80,20),(255,255,255,255));fill.save(folder/'FILL-gap.png')
    tone=Image.new('RGBA',(1024,256))
    for x in range(1024): ImageDraw.Draw(tone).line((x,0,x,255),fill=(x//4,x//4,x//4,255))
    tone.save(folder/'TONAL.png')
    palette=['#ff0000','#ff8000','#ffff00','#00ff00','#00ffff','#0000ff','#8000ff','#ff00ff','#202020','#808080','#e0e0e0']
    colour=Image.new('RGBA',(880,240),'white');cd=ImageDraw.Draw(colour)
    for n,c in enumerate(palette):cd.rectangle((n*80,0,n*80+79,239),fill=c)
    colour.save(folder/'COLOUR.png')
    grid=Image.new('RGBA',(960,640),'white');gd=ImageDraw.Draw(grid)
    for x in range(0,960,40):gd.line((x,0,x,639),fill='#506070',width=1)
    for y in range(0,640,40):gd.line((0,y,959,y),fill='#506070',width=1)
    for label,pos,c in [('TL',(0,0),'red'),('TR',(900,0),'blue'),('BL',(0,580),'green'),('BR',(900,580),'purple')]:gd.rectangle((pos[0],pos[1],pos[0]+59,pos[1]+59),fill=c);gd.text((pos[0]+5,pos[1]+5),label,fill='white')
    gd.line((100,250,800,320),fill='black',width=3);grid.save(folder/'GEOMETRY.png')
    noise=Image.new('RGBA',(1024,768),'white');nd=ImageDraw.Draw(noise);nd.rectangle((512,0,1023,767),fill='black');seed=12345
    for y in range(100,500):
        for x in range(50,450):
            seed=(1664525*seed+1013904223)&0xffffffff;v=128+((seed>>24)%41-20);noise.putpixel((x,y),(v,v,v,255))
    noise.save(folder/'DETAIL.png')
    manifest=[]
    for path in sorted(folder.iterdir()):
        if path.is_file():
            data=path.read_bytes();im=Image.open(path);im.load();manifest.append(dict(file=path.name,bytes=len(data),sha256=sha(data),size=list(im.size),mode=im.mode,format=im.format))
    save_json(folder/'manifest.json',dict(generator='audit_support.py fixture_files',images=manifest,limitations=['Natural photograph not included','Legacy project fixtures not yet collected','Lens distortion variants not yet generated','Limit and fault injection fixtures are prepared per test']))
    print('Generated',len(manifest),'independently encoded image fixtures')

def snapshot():
    files=[]
    for path in sorted([REPO/'index.html']+list((REPO/'src').glob('*'))+list((REPO/'tests').glob('*'))):
        if path.is_file():files.append(dict(path=path.relative_to(REPO).as_posix(),sha256=sha(path.read_bytes())))
    save_json(ROOT/'baseline.json',dict(at=datetime.now(timezone.utc).isoformat(),head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),dirty=subprocess.check_output(['git','status','--short'],cwd=REPO,text=True),files=files,host=platform.platform(),python=platform.python_version()))
    print('Captured',len(files),'baseline file hashes')

def import_fixtures():
    folder=ROOT/'fixtures'
    image=Image.open(folder/'GEOMETRY.png').convert('RGB')
    for suffix,fmt in [('png','PNG'),('jpg','JPEG'),('webp','WEBP'),('bmp','BMP'),('gif','GIF')]:
        image.save(folder/('ORIENT.'+suffix),format=fmt)
    for mode in ['RGB','RGBA','L']:
        image.convert(mode).save(folder/('ORIENT-'+mode+'.tif'),compression='raw')
    exif=Image.Exif();exif[274]=6
    image.save(folder/'ORIENT-exif6.jpg',exif=exif)
    image.save(folder/'unsupported-lzw.tif',compression='tiff_lzw')
    (folder/'corrupt.png').write_bytes(b'\x89PNG\r\n\x1a\nnot a valid image')
    (folder/'truncated.tif').write_bytes((folder/'ORIENT-RGBA.tif').read_bytes()[:100])
    original=(folder/'ORIENT-RGB.tif').read_bytes()
    little=original[:2]==b'II';order='<' if little else '>'
    directory=struct.unpack_from(order+'I',original,4)[0]
    entries={struct.unpack_from(order+'H',original,directory+2+n*12)[0]:directory+2+n*12 for n in range(struct.unpack_from(order+'H',original,directory)[0])}
    for name,tag,value in [('zero-width',256,0),('oversize-width',256,4097),('missing-last-strip',278,320),('zero-rows',278,0),('outside-strip',273,len(original)-1),('short-strip',279,1)]:
        data=bytearray(original);at=entries[tag];kind=struct.unpack_from(order+'H',data,at+2)[0];struct.pack_into(order+('H' if kind==3 else 'I'),data,at+8,value);(folder/(name+'.tif')).write_bytes(data)
    data=bytearray(original);struct.pack_into(order+'I',data,4,len(data)-1);(folder/'outside-directory.tif').write_bytes(data)
    records=[]
    for path in sorted(folder.glob('ORIENT*')):
        im=ImageOps.exif_transpose(Image.open(path));im.load()
        records.append(dict(file=path.name,sha256=sha(path.read_bytes()),decoded_size=im.size,decoded_rgba_sha256=sha(im.convert('RGBA').tobytes())))
    photos=[]
    for path in sorted((REPO/'Example_Images').iterdir()):
        if path.is_file():
            im=Image.open(path);im.load();photos.append(dict(file=path.name,sha256=sha(path.read_bytes()),size=im.size,mode=im.mode,exif_orientation=im.getexif().get(274)))
    save_json(folder/'import-manifest.json',dict(images=records,user_supplied_photographs=photos,encoder='Pillow '+Image.__version__))
    print('Prepared orientation, corrupt, truncated and unsupported TIFF fixtures; inventoried',len(photos),'user photographs')

def compare_imports():
    records=[]
    for before in sorted((ROOT/'evidence').glob('FILE-002-*-before.png')):
        name=before.name.removeprefix('FILE-002-').removesuffix('-before.png')
        expected=ImageOps.exif_transpose(Image.open(ROOT/'fixtures'/name)).convert('RGBA')
        actual=Image.open(before).convert('RGBA')
        assert expected.size==actual.size,(name,expected.size,actual.size)
        diff=ImageChops.difference(expected,actual)
        extrema=diff.getextrema();max_error=max(hi for lo,hi in extrema)
        after=Image.open(before.with_name(before.name.replace('-before','-draw'))).convert('RGBA')
        undo=Image.open(before.with_name(before.name.replace('-before','-undo'))).convert('RGBA')
        redo=Image.open(before.with_name(before.name.replace('-before','-redo'))).convert('RGBA')
        changed=sum(a!=b for a,b in zip(actual.getdata(),after.getdata()))
        row=dict(fixture=name,size=actual.size,maximum_channel_error=max_error,changed_pixels=changed,undo_exact=actual.tobytes()==undo.tobytes(),redo_exact=after.tobytes()==redo.tobytes(),source_sha256=sha((ROOT/'fixtures'/name).read_bytes()),before_sha256=sha(before.read_bytes()))
        records.append(row)
    save_json(ROOT/'evidence/FILE-002-independent-comparison.json',dict(decoder='Pillow '+Image.__version__,results=records))
    print(json.dumps(records,indent=2))

def verify_tiff_run():
    evidence=ROOT/'evidence'
    negative=[json.loads((evidence/('FILE-010-negative-'+suffix+'.retropaint')).read_text(encoding='utf-8')) for suffix in ['before','middle','after']]
    assert negative[0]==negative[1]==negative[2],'A rejected TIFF changed the saved document'
    before=json.loads((evidence/'FILE-010-roundtrip-before.retropaint').read_text(encoding='utf-8'))
    after=json.loads((evidence/'FILE-010-roundtrip-after.retropaint').read_text(encoding='utf-8'))
    assert before==after,'Project file roundtrip changed TIFF artwork'
    a=Image.open(evidence/'FILE-010-roundtrip-before.png').convert('RGBA')
    b=Image.open(evidence/'FILE-010-roundtrip-after.png').convert('RGBA')
    assert a.size==b.size and a.tobytes()==b.tobytes(),'Reopened composition changed'
    report=dict(at=datetime.now(timezone.utc).isoformat(),negative_documents_equal=True,project_documents_equal=True,reopened_pixels_equal=True,decoder='Pillow '+Image.__version__,dimensions=a.size,document_sha256=sha((evidence/'FILE-010-roundtrip-before.retropaint').read_bytes()))
    save_json(evidence/'FILE-010-independent-verification.json',report)
    print(json.dumps(report,indent=2))

def verify_exports():
    evidence=ROOT/'evidence';source=Image.open(ROOT/'fixtures/PATCH.png').convert('RGBA')
    baseline=json.loads((evidence/'EXPORT-alpha-baseline.retropaint').read_text(encoding='utf-8'))
    after=json.loads((evidence/'EXPORT-alpha-after.retropaint').read_text(encoding='utf-8'))
    assert baseline==after,'Export changed the editable document'
    for name in ['EXPORT-source-restored','FILE-011-after']:
        assert baseline==json.loads((evidence/(name+'.retropaint')).read_text(encoding='utf-8')),name+' changed the source'
    assert baseline['layers'][0]['name']=='Paper' and baseline['layers'][0]['visible'] is False
    assert baseline['layers'][1]['name']=='Alpha patches' and baseline['layers'][1]['paper'] is None
    white=Image.new('RGBA',source.size,'white');white.alpha_composite(source)
    black=Image.new('RGBA',source.size,'black');black.alpha_composite(source)
    results=[]
    for extension,fmt in [('png','PNG'),('webp','WEBP'),('tif','TIFF'),('jpg','JPEG'),('bmp','BMP'),('gif','GIF')]:
        name={'tif':'tiff','jpg':'jpeg'}.get(extension,extension)
        path=evidence/('EXPORT-alpha-'+name+'.'+extension);im=Image.open(path);im.load()
        assert im.format==fmt and im.size==source.size,(path.name,im.format,im.size)
        rgba=im.convert('RGBA');row=dict(file=path.name,format=im.format,size=im.size,bytes=path.stat().st_size,sha256=sha(path.read_bytes()))
        reopened=Image.open(evidence/('EXPORT-reopened-'+name+'.png')).convert('RGBA')
        assert reopened.size==im.size
        comparison=[]
        for colour in ['white','black']:
            expected_composite=Image.alpha_composite(Image.new('RGBA',im.size,colour),rgba)
            actual_composite=Image.alpha_composite(Image.new('RGBA',im.size,colour),reopened)
            maximum=max(hi for lo,hi in ImageChops.difference(expected_composite,actual_composite).getextrema());comparison.append(dict(backing=colour,maximum_channel_error=maximum));assert maximum<=(1 if fmt=='JPEG' else 0)
        row['actual_chooser_reopen']=comparison
        if fmt in ['PNG','WEBP','TIFF']:
            row['alpha_exact']=rgba.getchannel('A').tobytes()==source.getchannel('A').tobytes();assert row['alpha_exact']
            composites=[]
            for colour,reference in [('white',white),('black',black)]:
                composite=Image.new('RGBA',source.size,colour);composite.alpha_composite(rgba)
                composite.save(evidence/('EXPORT-'+name+'-on-'+colour+'.png'))
                difference=ImageChops.difference(reference,composite);maximum=max(hi for lo,hi in difference.getextrema());composites.append(dict(backing=colour,maximum_channel_error=maximum));assert maximum<=(4 if fmt=='WEBP' else 0)
            row['composites']=composites
        elif fmt in ['JPEG','BMP']:
            expected=white.convert('RGB');rgb=im.convert('RGB');diff=ImageChops.difference(expected,rgb);squares=sum(sum(n*n*count for n,count in enumerate(diff.histogram()[c*256:(c+1)*256])) for c in range(3));rmse=math.sqrt(squares/(3*rgb.width*rgb.height));row['rmse']=rmse
            row['clear_region_rgb']=rgb.getpixel((5,5));row['partial_alpha_patch_rgb']=rgb.getpixel((450,340));assert row['clear_region_rgb']==(255,255,255)
            assert rmse<=(5 if fmt=='JPEG' else 0)
        else:
            row['palette_entries']=len(im.getpalette())//3;row['frames']=getattr(im,'n_frames',1);row['alpha_levels']=sorted(set(rgba.getchannel('A').tobytes()));assert row['palette_entries']<=256 and row['frames']==1 and row['alpha_levels']==[0,255]
        results.append(row)
    report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,project_unchanged=True,jpeg_threshold='RGB RMSE <=5/255 and exact white clear-region centre',results=results)
    save_json(evidence/'EXPORT-independent-verification.json',report);print(json.dumps(report,indent=2))

def verify_gif_and_names():
    evidence=ROOT/'evidence';source=Image.open(ROOT/'fixtures/COLOUR-rich-alpha.png').convert('RGBA');gif=Image.open(evidence/'FILE-009-colour-rich.gif');gif.load();rgba=gif.convert('RGBA')
    assert gif.format=='GIF' and gif.size==source.size and gif.n_frames==1 and len(gif.getpalette())//3<=256
    expected_alpha=source.getchannel('A').point(lambda a:255 if a>=128 else 0)
    assert expected_alpha.tobytes()==rgba.getchannel('A').tobytes(),'GIF alpha did not use its binary threshold'
    reopened=Image.open(evidence/'FILE-009-reopened.png').convert('RGBA')
    for colour in ['white','black']:
        assert Image.alpha_composite(Image.new('RGBA',source.size,colour),reopened).tobytes()==Image.alpha_composite(Image.new('RGBA',source.size,colour),rgba).tobytes(),'Actual GIF reopen changed visible palette pixels'
    before=json.loads((evidence/'FILE-009-source-before.retropaint').read_text(encoding='utf-8'));after=json.loads((evidence/'FILE-009-source-after.retropaint').read_text(encoding='utf-8'));assert before==after
    diffs=[tuple(abs(a[c]-b[c]) for c in range(3)) for a,b in zip(source.getdata(),rgba.getdata()) if a[3]>=128]
    events={event['label']:event for event in [json.loads(line) for line in (ROOT/'export-events.jsonl').read_text(encoding='utf-8').splitlines()]}
    expected={'FILE-011-existing-extension':('A picture.jpg','JPEG'),'FILE-011-reserved-characters':('bad---------.tif','TIFF'),'FILE-011-empty':('retropaint.bmp','BMP'),'FILE-011-uppercase-extension':('PHOTO.webp','WEBP')}
    names=[]
    for label,(filename,fmt) in expected.items():
        event=events[label];actual=Path(event['download_path']).name;assert actual==filename,(actual,filename)
        extension=Path(filename).suffix;im=Image.open(evidence/(label+extension));im.load();assert im.format==fmt and im.size==(960,640);names.append(dict(entered=event['entered_name'],download=actual,decoded_format=im.format))
    report=dict(decoder='Pillow '+Image.__version__,gif=dict(size=gif.size,palette_entries=len(gif.getpalette())//3,frames=gif.n_frames,alpha_threshold_exact=True,actual_chooser_reopen_exact=True,source_project_unchanged=True,maximum_rgb_quantisation_error=[max(d[c] for d in diffs) for c in range(3)],rgb_quantisation_rmse=math.sqrt(sum(sum(n*n for n in d) for d in diffs)/(3*len(diffs)))),filenames=names)
    save_json(evidence/'FILE-009-011-independent-verification.json',report);print(json.dumps(report,indent=2))

def verify_start():
    evidence=ROOT/'evidence';read=lambda name:Image.open(evidence/(name+'.png')).convert('RGBA')
    pairs=[('START-004-stroke-2','START-004-undo-1'),('START-004-stroke-1','START-004-undo-2'),('START-004-stroke-2','START-004-redo-1'),('START-004-stroke-3','START-004-redo-2'),('START-004-new-branch','START-004-abandoned-redo'),('START-004-new-branch','START-004-after-reopen'),('START-003-before-navigation','START-003-after-navigation'),('START-003-fixed-before-outside','START-003-fixed-after-outside'),('START-005-aged-before','START-005-keep'),('START-005-aged-before','START-005-escape'),('START-005-aged-before','START-006-aged-undo'),('START-006-aged-clear','START-006-aged-redo')]
    results=[]
    for a,b in pairs:
        left,right=read(a),read(b);same=left.size==right.size and left.tobytes()==right.tobytes();assert same,(a,b);results.append(dict(before=a,after=b,exact_rgba=True))
    for a,b in [('START-003-before-navigation','START-003-after-navigation'),('START-003-before-outside','START-003-fixed-after-outside'),('START-004-before-reopen','START-004-after-reopen'),('START-005-aged-before','START-005-aged-after')]:
        assert json.loads((evidence/(a+'.retropaint')).read_text(encoding='utf-8'))==json.loads((evidence/(b+'.retropaint')).read_text(encoding='utf-8')),(a,b)
    assert read('START-004-blank').getextrema()==((255,255),)*4
    colours=[]
    for n,(y,channel) in enumerate([(100,0),(200,2),(300,1)],1):
        image=read('START-004-stroke-'+str(n));assert image.size==(960,640)
        rgba=image.getpixel((175,y));assert rgba[channel]>max(rgba[c] for c in range(3) if c!=channel);colours.append(dict(stroke=n,centre=[175,y],rgba=rgba))
        assert image.getpixel((700,600))==(255,255,255,255)
    branch=read('START-004-new-branch');assert branch.getpixel((175,300))==(255,255,255,255);assert branch.getpixel((175,100))==read('START-004-stroke-2').getpixel((175,100));assert branch.getpixel((175,200))==read('START-004-stroke-2').getpixel((175,200))
    assert read('START-003-fixed-next-gesture').tobytes()!=read('START-003-fixed-after-outside').tobytes()
    assert read('START-006-aged-clear').getextrema()==((255,255),)*4
    report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,exact_comparisons=results,stroke_colours=colours,project_comparisons_exact=True,history_branch_replaced=True,next_gesture_draws=True,clear_timing=json.loads((evidence/'START-005-timing.json').read_text(encoding='utf-8')))
    save_json(evidence/'START-independent-verification.json',report);print('Verified',len(results),'exact pixel pairs, project comparisons, colour identities and aged Clear timing')

def rich_colour():
    image=Image.new('RGBA',(320,240))
    for y in range(240):
        for x in range(320):
            alpha=0 if y<40 else 64 if y<80 else 128 if y<120 else 192 if y<160 else 255
            image.putpixel((x,y),(round(x*255/319),round(y*255/239),(x*3+y*5)%256,alpha))
    path=ROOT/'fixtures/COLOUR-rich-alpha.png';image.save(path)
    save_json(ROOT/'fixtures/COLOUR-rich-alpha.json',dict(generator='audit_support.py rich_colour',sha256=sha(path.read_bytes()),size=image.size,alpha_levels=[0,64,128,192,255]))
    print('Created independently encoded colour and alpha ramp')

def corrupt_projects():
    import copy
    folder=ROOT/'fixtures';valid=json.loads((ROOT/'evidence/CORRUPT-vector-reference.retropaint').read_text(encoding='utf-8'));assert valid['layers'][0]['objects']
    cases=[]
    def changed(name,edit,source=valid):
        doc=copy.deepcopy(source);edit(doc);path=folder/(name+'.retropaint');path.write_text(json.dumps(doc,separators=(',',':')),encoding='utf-8');cases.append(dict(file=path.name,sha256=sha(path.read_bytes()),changed_property=name))
    changed('missing-active-layer',lambda d:d.update(active=999999))
    changed('singular-object-transform',lambda d:d['layers'][0]['objects'][0].update(matrix=[0,0,0,0,0,0]))
    changed('malformed-layer-image',lambda d:d['layers'][0].update(image='data:image/png;base64,AAAA'))
    changed('invalid-number',lambda d:d.update(width='not-a-number'))
    changed('invalid-crop',lambda d:d.update(crop={'x':0,'y':0,'width':2,'height':1}))
    changed('unknown-future-version',lambda d:d.update(version=999))
    two=json.loads((ROOT/'evidence/EXPORT-alpha-baseline.retropaint').read_text(encoding='utf-8'))
    changed('duplicate-layer-ids',lambda d:d['layers'][1].update(id=d['layers'][0]['id']),two)
    changed('fractional-inactive-id',lambda d:d['layers'][0].update(id=d['layers'][0]['id']+.5),two)
    cad=json.loads((ROOT/'backups/artwork-before-acceptance-audit.retropaint').read_text(encoding='utf-8'))
    changed('singular-cad-scale',lambda d:next(l for l in d['layers'] if l.get('cad'))['cad']['bodies'][0].update(scale=[0,1,1]),cad)
    changed('unknown-solid-recipe',lambda d:next(l for l in d['layers'] if l.get('cad'))['cad']['bodies'][0]['solid'].update(kind='not-a-solid'),cad)
    raw=json.dumps(valid,separators=(',',':'))
    for name,data in [('truncated-project',raw[:len(raw)//2]),('invalid-nan-json',raw.replace('"width":960','"width":NaN',1))]:
        path=folder/(name+'.retropaint');path.write_text(data,encoding='utf-8');cases.append(dict(file=path.name,sha256=sha(path.read_bytes()),changed_property=name))
    save_json(folder/'corrupt-project-manifest.json',dict(source='Real UI project downloads, preserved independently; copied inputs only',files=cases))
    print('Prepared',len(cases),'corrupt project inputs from actual saved projects')

def verify_corrupt_projects():
    evidence=ROOT/'evidence';original=json.loads((evidence/'FILE-016-unsaved-before.retropaint').read_text(encoding='utf-8'))
    manifest=json.loads((ROOT/'fixtures/corrupt-project-manifest.json').read_text(encoding='utf-8'))
    results=[]
    for fixture in manifest['files']:
        name=Path(fixture['file']).stem;path=evidence/('FILE-016-fixed-'+name+'.retropaint');after=json.loads(path.read_text(encoding='utf-8'));assert after==original,name+' changed current document'
        state=(evidence/('FILE-016-fixed-'+name+'.txt')).read_text(encoding='utf-8');results.append(dict(fixture=fixture['file'],sha256=fixture['sha256'],saved_document_exact=True,evidence=str(path.relative_to(ROOT))))
    before=Image.open(evidence/'FILE-016-unsaved-before.png').convert('RGBA');after=Image.open(evidence/'FILE-016-fixed-after.png').convert('RGBA');assert before.size==after.size and before.tobytes()==after.tobytes()
    save_json(evidence/'FILE-016-independent-verification.json',dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,results=results,final_composition_exact=True,valid_project_opened_after_each_rejection=True,remaining_variants=[] if len(results)>=20 else ['Broken CAD workplanes','Invalid saved photo recipes','Unsupported live ink recipe kinds']))
    print('Verified all',len(results),'rejected project snapshots and the final composition unchanged')

def corrupt_recipe_projects():
    import copy
    folder=ROOT/'fixtures';manifest=json.loads((folder/'corrupt-project-manifest.json').read_text(encoding='utf-8'))
    def changed(name,source,edit,property_path):
        doc=copy.deepcopy(source);edit(doc);path=folder/(name+'.retropaint');save_json(path,doc)
        manifest['files']=[row for row in manifest['files'] if row['file']!=path.name]
        manifest['files'].append(dict(file=path.name,sha256=sha(path.read_bytes()),changed_property=property_path))
    photo=json.loads((ROOT/'evidence/LEGACY-v2-migrated-current.retropaint').read_text(encoding='utf-8'))
    assert photo['layers'][0]['photo']['settings']['exposure']==1
    changed('photo-exposure-type',photo,lambda d:d['layers'][0]['photo']['settings'].update(exposure='one'),'layers[0].photo.settings.exposure')
    changed('photo-unordered-curve',photo,lambda d:d['layers'][0]['photo']['settings']['curves'].update(red=[{'x':0,'y':0},{'x':.7,'y':.7},{'x':.4,'y':.4},{'x':1,'y':1}]),'layers[0].photo.settings.curves.red')
    changed('photo-unknown-look',photo,lambda d:d['layers'][0]['photo'].update(look='unrecognised-look'),'layers[0].photo.look')
    live=json.loads((ROOT/'evidence/CORRUPT-live-reference.retropaint').read_text(encoding='utf-8'))
    assert len(live['layers'][0]['live']['strokes'])==1
    changed('live-unknown-kind',live,lambda d:d['layers'][0]['live']['strokes'][0]['spec'].update(kind='unrecognised-ink'),'layers[0].live.strokes[0].spec.kind')
    changed('live-unknown-mode',live,lambda d:d['layers'][0]['live']['strokes'][0]['spec'].update(mode='unrecognised-mode'),'layers[0].live.strokes[0].spec.mode')
    changed('live-unknown-brush',live,lambda d:d['layers'][0]['live']['strokes'][0].update(applicator='unrecognised-brush'),'layers[0].live.strokes[0].applicator')
    cad=json.loads((ROOT/'evidence/LEGACY-v9-migrated-current.retropaint').read_text(encoding='utf-8'))
    target=next(l for l in cad['layers'] if l.get('cad'))['cad']['bodies'][0]
    # Analytic 10 x 10 x 10 prism, with one deliberately invalid basis below.
    target['solid']={'kind':'extrude','points':[[0,0],[10,0],[10,10],[0,10]],'height':10,'taper':1,'twist':0,'plane':{'origin':[0,0,0],'u':[1,0,0],'v':[0,1,0],'normal':[0,0,1]}}
    def axes(doc,**values):next(l for l in doc['layers'] if l.get('cad'))['cad']['bodies'][0]['solid']['plane'].update(values)
    changed('cad-parallel-workplane',cad,lambda d:axes(d,v=[1,0,0]),'CAD prism workplane v parallel to u')
    changed('cad-left-handed-workplane',cad,lambda d:axes(d,normal=[0,0,-1]),'CAD prism workplane normal opposite u cross v')
    save_json(folder/'corrupt-project-manifest.json',manifest)
    print('Prepared eight additional malformed recipe inputs; retained prior twelve fixtures')

def legacy_sources():
    folder=ROOT/'legacy';folder.mkdir(exist_ok=True);records=[]
    for version,revision in [(1,'3916c24'),(2,'5ae1169'),(9,'c85f751')]:
        commit=subprocess.check_output(['git','rev-parse',revision],cwd=REPO,text=True).strip();name='v'+str(version)+'-'+revision
        archive=folder/(name+'.zip');target=folder/name
        if not archive.exists():
            subprocess.run(['git','archive','--format=zip','--output='+str(archive),commit,'index.html','package.json','package-lock.json','tsconfig.json','vite.config.ts','src','public'],cwd=REPO,check=True)
        target.mkdir(exist_ok=True)
        with zipfile.ZipFile(archive) as bundle:
            for entry in bundle.infolist():
                if not (target/entry.filename).resolve().is_relative_to(target.resolve()):raise ValueError('Archive entry leaves its dedicated source directory')
            bundle.extractall(target)
        records.append(dict(version=version,producing_revision=commit,source_archive=archive.name,source_archive_sha256=sha(archive.read_bytes()),source_directory=str(target.relative_to(ROOT)),execution='Not run; authentic saved fixture still to be produced through that version UI'))
    save_json(folder/'producer-manifest.json',dict(producers=records,unlocated_producing_versions=[3,4,5,6,7,8],notes='Only three project-producing revisions exist in current git history. Archive search found no further project serializer. These are unchanged historical sources; no current project version numbers are relabelled. Current installed dependencies will be reused and recorded.'))
    print('Extracted',len(records),'historical producers without modifying their source')

def inspect_stl(path):
    data=path.read_bytes();count=struct.unpack_from('<I',data,80)[0];assert len(data)==84+count*50
    edges=Counter();directions=Counter();points=[];volume=0
    def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
    def dot(a,b):return sum(x*y for x,y in zip(a,b))
    for i in range(count):
        values=struct.unpack_from('<12fH',data,84+i*50);normal=values[:3];a,b,c=[tuple(values[start:start+3]) for start in [3,6,9]];points.extend([a,b,c]);volume+=dot(a,cross(b,c))/6
        face=cross(tuple(y-x for x,y in zip(a,b)),tuple(y-x for x,y in zip(a,c)));assert dot(face,face)>0 and dot(face,normal)>0,'Degenerate or reversed STL normal'
        for left,right in [(a,b),(b,c),(c,a)]:
            key=tuple(sorted([left,right]));edges[key]+=1;directions[key]+=1 if left<right else -1
    assert all(n==2 for n in edges.values()) and all(n==0 for n in directions.values()),'STL is not a closed consistently oriented surface'
    return dict(file=path.name,sha256=sha(data),triangles=count,vertices=len(set(points)),bounds_min=[min(p[c] for p in points) for c in range(3)],bounds_max=[max(p[c] for p in points) for c in range(3)],signed_volume_mm3=volume,closed_oriented_edges=True)

def verify_legacy():
    evidence=ROOT/'evidence';manifest=json.loads((ROOT/'legacy/producer-manifest.json').read_text(encoding='utf-8'));results=[]
    def subset(before,after,path=''):
        if isinstance(before,dict):
            assert isinstance(after,dict),path
            for key,value in before.items():
                assert key in after,path+'.'+key
                if key=='image' and isinstance(value,str) and value.startswith('data:image/png;base64,'):
                    decode=lambda encoded:Image.open(io.BytesIO(base64.b64decode(encoded.split(',',1)[1]))).convert('RGBA')
                    a,b=decode(value),decode(after[key]);assert a.size==b.size and a.tobytes()==b.tobytes(),path+'.image'
                else:subset(value,after[key],path+'.'+key)
        elif isinstance(before,list):
            assert len(before)==len(after),path
            for i,(a,b) in enumerate(zip(before,after)):subset(a,b,path+'['+str(i)+']')
        else:assert before==after,(path,before,after)
    for producer in manifest['producers']:
        version=producer['version'];stem='LEGACY-v'+str(version)
        original=json.loads((evidence/(stem+'-authentic.retropaint')).read_text(encoding='utf-8'));current=json.loads((evidence/(stem+'-migrated-current.retropaint')).read_text(encoding='utf-8'));reopened=json.loads((evidence/(stem+'-migrated-reopened.retropaint')).read_text(encoding='utf-8'))
        assert original['version']==version and current['version']==10 and current==reopened
        for field in ['width','height','active','layers']:subset(original[field],current[field],field)
        for field in ['crop','drawingMode']:
            if field in original:subset(original[field],current[field],field)
        before=Image.open(evidence/(stem+'-before.png')).convert('RGBA');now=Image.open(evidence/(stem+'-reopened-current.png')).convert('RGBA');again=Image.open(evidence/(stem+'-migrated-reopened.png')).convert('RGBA')
        assert before.size==now.size==again.size and before.tobytes()==now.tobytes()==again.tobytes(),stem+' rendered appearance changed'
        row=dict(version=version,producing_revision=producer['producing_revision'],source_sha256=producer['source_archive_sha256'],fixture_sha256=sha((evidence/(stem+'-authentic.retropaint')).read_bytes()),layers=len(original['layers']),render_dimensions=before.size,original_fields_preserved=True,render_pixels_exact=True,current_save_reopen_exact=True)
        if version==2:
            assert (original['width'],original['height'])==(1024,256) and before.size==(768,192)
            assert original['layers'][0]['photo']['settings']['exposure']==1
            assert original['crop']=={'x':.125,'y':.125,'width':.75,'height':.75}
            source=Image.open(ROOT/'fixtures/TONAL.png').convert('RGBA');saved=Image.open(io.BytesIO(base64.b64decode(original['layers'][0]['image'].split(',',1)[1]))).convert('RGBA');assert source.tobytes()==saved.tobytes();row['uncropped_original_pixels_preserved']=True
        if version==9:
            meshes=[inspect_stl(evidence/(stem+'-'+suffix+'.stl')) for suffix in ['original','current']]
            for mesh in meshes:assert mesh['triangles']==12 and mesh['vertices']==8 and mesh['bounds_min']==[-10,-10,0] and mesh['bounds_max']==[10,10,20] and abs(mesh['signed_volume_mm3']-8000)<1e-6
            row['independent_stl_inspection']=meshes
        results.append(row);producer.update(execution='Actual historical UI download, current UI migration and upgraded UI roundtrip verified',fixture_sha256=row['fixture_sha256'],fixture='fixtures/legacy-v'+str(version)+'-'+producer['producing_revision'][:7]+'.retropaint',runtime='Unmodified archived application sources served by current Vite 6.4.3 and installed dependencies via current serving config; no serializer changes')
    save_json(ROOT/'legacy/producer-manifest.json',manifest)
    save_json(evidence/'LEGACY-independent-verification.json',dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,stl_oracle='Independent Python struct/math edge, normal, bounds and signed-volume inspection; analytic 20mm cube',results=results,unlocated_versions=manifest['unlocated_producing_versions']))
    print(json.dumps(results,indent=2))

def sync_ledger():
    import tempfile
    result=json.loads((ROOT/'results.json').read_text(encoding='utf-8'))
    path=REPO/'APP-USE-CASES/EXECUTION-LEDGER.csv'
    with path.open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f);fields=reader.fieldnames;existing={row['case_id']:row for row in reader}
    with (REPO/'APP-USE-CASES/CASE-INDEX.csv').open(encoding='utf-8-sig',newline='') as f:
        index=list(csv.DictReader(f))
    assert len(index)==349 and len({row['id'] for row in index})==349
    rows=[]
    for case in index:
        row=existing.get(case['id'],dict.fromkeys(fields,''))
        row.update(case_id=case['id'],title=case['title'])
        if not row['status']:row['status']='Not run'
        rows.append(row)
    for case_id,recorded in result['cases'].items():
        assert case_id in {row['id'] for row in index},case_id
        assert not set(recorded)-set(fields),'Unknown case CSV fields: '+str(set(recorded)-set(fields))
    for row in rows:
        recorded=result['cases'].get(row['case_id'])
        if recorded:
            previous_status=row['status'];previous_time=row['executed_at']
            row.update(recorded)
            evidence=recorded.get('evidence_paths','');headless='headless/' in evidence;historical=any(marker in evidence for marker in ['ui-events','export-events','NATIVE-'])
            browser='Historical native browser and isolated headless Chrome' if headless and historical else 'Isolated headless Chrome' if headless else 'Historical native browser; exact browser per linked execution report'
            device='Trusted browser mouse/keyboard in isolated headless contexts; protocol emulation only where explicitly recorded' if headless and not historical else 'Historical native and/or isolated headless inputs as identified in the linked per-run reports'
            timestamp=recorded.get('executed_at') or (previous_time if previous_status==recorded['status'] else '')
            # Use an actual matching UI workflow's completion time where present;
            # unknown historical times stay blank rather than being invented now.
            completion_times=[]
            for reference in evidence.split('; '):
                file=ROOT/reference
                if reference.startswith('headless/') and reference.endswith('-ui.json') and file.is_file():
                    ui=json.loads(file.read_text(encoding='utf-8'))
                    if ui.get('case')==row['case_id'] and ui.get('finished'):completion_times.append(ui['finished'])
            if completion_times:timestamp=max(completion_times)
            row.update(run_id=result['run_id'],app_revision_and_dirty_snapshot='runs/'+ROOT.name+'/baseline.json; per-run pinned manifests and source-delta.json',browser_and_os=browser+'; '+baseline_host(),viewport='Per-step screenshot and source canvas dimensions retained',input_device=device,fixture_hashes='Per-case plans/manifests and actual source hashes in linked evidence',tester='Codex',executed_at=timestamp)
            row['evidence_paths']='runs/'+ROOT.name+'/'+row['evidence_paths'].replace('; ','; runs/'+ROOT.name+'/')
    expected=Counter(item['status'] for item in result['cases'].values());expected['Not run']+=349-len(result['cases'])
    assert Counter(row['status'] for row in rows)==expected,'CSV and authoritative case results disagree'
    # Validate/serialize a complete canonical ledger before replacing the old
    # file; a schema error must not leave a partially written case inventory.
    with tempfile.NamedTemporaryFile('w',encoding='utf-8',newline='',dir=path.parent,prefix='.execution-ledger-',suffix='.tmp',delete=False) as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows);temporary=Path(f.name)
    temporary.replace(path)
    baseline=json.loads((ROOT/'baseline.json').read_text(encoding='utf-8'))
    delta=[]
    for item in baseline['files']:
        path=REPO/item['path']
        if not path.exists():delta.append(dict(path=item['path'],baseline_sha256=item['sha256'],current_sha256=None,change='deleted'))
        elif sha(path.read_bytes())!=item['sha256']:
            delta.append(dict(path=item['path'],baseline_sha256=item['sha256'],current_sha256=sha(path.read_bytes()),change='modified'))
    previous={item['path'].replace('\\','/') for item in baseline['files']}
    for path in [REPO/'index.html',REPO/'package.json',REPO/'package-lock.json',*sorted((REPO/'src').glob('*')),*sorted((REPO/'tests').glob('*'))]:
        name=path.relative_to(REPO).as_posix()
        if path.is_file() and name not in previous:delta.append(dict(path=name,baseline_sha256=None,current_sha256=sha(path.read_bytes()),change='added'))
    save_json(ROOT/'source-delta.json',dict(at=datetime.now(timezone.utc).isoformat(),changed_files=delta))
    counts=Counter(row['status'] for row in rows)
    print(json.dumps(counts,indent=2))

def baseline_host():
    return json.loads((ROOT/'baseline.json').read_text(encoding='utf-8'))['host']

if __name__=='__main__':
    import sys
    {'backup':verify_backup,'fixtures':fixture_files,'snapshot':snapshot,'import-fixtures':import_fixtures,'compare-imports':compare_imports,'verify-tiff':verify_tiff_run,'verify-exports':verify_exports,'verify-gif-names':verify_gif_and_names,'verify-start':verify_start,'rich-colour':rich_colour,'corrupt-projects':corrupt_projects,'corrupt-recipes':corrupt_recipe_projects,'verify-corrupt-projects':verify_corrupt_projects,'legacy-sources':legacy_sources,'verify-legacy':verify_legacy,'ledger':sync_ledger}[sys.argv[1]]()
