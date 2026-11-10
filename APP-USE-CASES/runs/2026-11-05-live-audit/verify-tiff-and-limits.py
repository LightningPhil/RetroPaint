"""Decode native TIFF imports and compare rejected imports and layer boundaries."""
import base64,hashlib,io,json
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse'
fixtures=root/'APP-USE-CASES/runs/2026-10-19-full-audit/fixtures';downloads=Path.home()/'Downloads';hashes={}
def retain(name):
    data=(downloads/name).read_bytes();(out/name).write_bytes(data)
    hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(name):return json.loads(retain('mouse-audit-'+name+'.retropaint'))
def raster(layer):return Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',')[1]))).convert('RGBA')
tiffs=[]
for mode in ['rgb','rgba','grey']:
    project=doc('tiff-'+mode);png=Image.open(io.BytesIO(retain('mouse-audit-tiff-'+mode+'.png'))).convert('RGBA')
    reference=Image.open(fixtures/f'PATCH-{mode}.tif').convert('RGBA')
    assert reference.size==png.size and reference.tobytes()==png.tobytes()
    assert raster(project['layers'][0]).tobytes()==reference.tobytes()
    tiffs.append({'variant':mode,'pixels_exact':True,'size':list(png.size)})
baseline=doc('tiff-grey')
rejections=['lzw','zero-width','outside-directory','outside-strip','short-strip','zero-rows','oversize-width','missing-last-strip','truncated']
for rejected in rejections:assert doc('tiff-reject-'+rejected)==baseline,rejected
sixteen=doc('layer-limit16');retry=doc('layer-limit16-retry')
assert len(sixteen['layers'])==len(retry['layers'])==16
assert sixteen['layers'][:15]==retry['layers'][:15]
assert sixteen['layers'][0]==baseline['layers'][0]
boundaries=[]
for name,edge,count in [('4000-four',4000,4),('4000-retry',4000,4),('4096-three',4096,3)]:
    project=doc('pixel-limit'+name)
    assert (project['width'],project['height'],len(project['layers']))==(edge,edge,count)
    first=raster(project['layers'][0]);assert first.size==(edge,edge)
    assert first.getpixel((0,0))==(229,57,53,255) and first.getpixel((edge-1,edge-1))==(255,255,255,255)
    for layer in project['layers'][1:]:
        image=raster(layer);assert image.size==(edge,edge) and image.getchannel('A').getextrema()==(0,0)
    boundaries.append({'variant':name,'edge':edge,'sheets':count,'stored_pixels':edge*edge*count,
                       'next_sheet_pixels':edge*edge*(count+1),'original_corner_patch_preserved':True})
assert doc('pixel-limit4000-four')['layers'][:3]==doc('pixel-limit4000-retry')['layers'][:3]
report={'tiff_imports':tiffs,'rejected_imports_whole_document_exact':rejections,
        'sixteen_sheet_limit_and_remove_retry_preserved_existing_sheets':True,
        'pixel_budget_boundaries':boundaries,'sha256':hashes}
(out/'tiff-limit-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
