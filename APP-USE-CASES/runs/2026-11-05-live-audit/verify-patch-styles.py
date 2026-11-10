"""All raster outline/fill combinations over genuine known RGBA patches."""
from pathlib import Path
import base64,copy,hashlib,io,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-patch-styles232';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
def doc(i):return json.loads(retain(prefix+(f' ({i})'if i else '')+'.retropaint'))
def pixels(layer):return np.array(Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',')[1]))).convert('RGBA'))
base=doc(2);fixture=json.loads((root/'test-results/audit-2026-11-05/fixtures/patch-alpha-paper.retropaint').read_text());assert all(np.array_equal(pixels(a),pixels(b))for a,b in zip(base['layers'],fixture['layers']));bc,fc=copy.deepcopy(base),copy.deepcopy(fixture)
for a,b in zip(bc['layers'],fc['layers']):a.pop('image');b.pop('image')
assert bc==fc
assert all(not l.get('objects')for l in base['layers']);assert base['drawingMode']=='raster'
raw_base=pixels(base['layers'][1]);assert np.array_equal(raw_base[120,120],[255,0,0,255])and np.array_equal(raw_base[320,420],[255,0,0,128])
def png(i):
 name=prefix+(f' ({i})'if i else '')+'.png';retain(name);return np.array(Image.open(out/name).convert('RGBA'))
base_png=png(1);yy,xx=np.mgrid[:640,:960];inside=(xx>=90)&(xx<510)&(yy>=90)&(yy<390);outer=(xx<69)|(xx>=531)|(yy<69)|(yy>=411);styles=[(o,f)for o in ['brush','solid','none']for f in ['none','primary','secondary']];results=[];images=[]
for j,(outline,fill)in enumerate(styles):
 full,undo,redo=map(doc,[3+3*j,4+3*j,5+3*j]);assert undo==base and full==redo;assert full['layers'][0]==base['layers'][0]
 c=copy.deepcopy(full);c['layers'][1]['image']=base['layers'][1]['image'];assert c==base
 raw=pixels(full['layers'][1]);im=png(2+j);images.append(im);assert np.array_equal(raw[outer],raw_base[outer])and np.array_equal(im[outer],base_png[outer])
 if fill=='none':assert np.array_equal(raw[inside],raw_base[inside])and np.array_equal(im[inside],base_png[inside])
 else:
  colour=[30,136,229,255]if fill=='primary'else[229,57,53,255];assert np.all(raw[inside]==colour)and np.all(im[inside]==colour)
 if outline=='none'and fill=='none':assert full==base and np.array_equal(im,base_png)
 if outline=='none'and fill!='none':
  outside=(xx<80)|(xx>=520)|(yy<80)|(yy>=400);assert np.array_equal(raw[outside],raw_base[outside])
 if outline!='none':assert np.any(np.any(im[72:88,300,:3]!=255,axis=1))and np.any(np.any(im[240,72:88,:3]!=255,axis=1))
 results.append(dict(outline=outline,fill=fill,inside_source_and_png_correct=True,external_source_and_png_exact=True,one_undo_and_redo_exact=True))
# Independently sampled cross-sections: shaped nib anisotropic; uniform solid line12px.
def spans(im):return [int(np.count_nonzero(np.any(im[60:100,300,:3]!=255,axis=1))),int(np.count_nonzero(np.any(im[240,60:100,:3]!=255,axis=1)))]
brush_span,solid_span=spans(images[0]),spans(images[3]);assert brush_span[0]!=brush_span[1]and solid_span==[12,12]and not np.array_equal(images[0],images[3])
assert doc(29)==doc(30)and np.array_equal(png(10),png(11))
report=dict(status='Pass',case='PLAY-003',original_fixture_genuine_raster_and_RGBA_exact=True,all9combinations=results,current_brush_calligraphy_spans_px=brush_span,solid_line_spans_px=solid_span,none_none_whole_project_and_png_exact=True,known_half_alpha_preserved_when_no_fill=True,actual_final_project_and_png_reopen_exact=True,initial_vector_converted_setup_excluded=True,hashes=hashes)
(out/'patch-styles232-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items()if k!='hashes'},indent=2))
