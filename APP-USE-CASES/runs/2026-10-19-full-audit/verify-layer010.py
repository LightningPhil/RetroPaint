from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
import json,hashlib
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/LAYER-010-complete'
ui=json.loads((folder/'LAYER-010-ui.json').read_text(encoding='utf-8'))
assert ui['status']=='Pass' and not ui['errors'] and len(ui['rows'])==4
fixture=json.loads((root/'headless/MIX-final/MIX-enriched.retropaint').read_text(encoding='utf-8'));rows=[];downloads=[]
for row in ui['rows']:
    location=folder/f"{row['width']}x{row['height']}";read=lambda name:json.loads((location/(name+'.retropaint')).read_text(encoding='utf-8'));image=lambda name:np.asarray(Image.open(location/(name+'.png')).convert('RGBA'))
    before=read('before');assert before==fixture
    source=image('before');assert source.shape==(640,960,4)
    one=deepcopy(before);one['layers'][0]['visible']=False
    assert read('paper-hidden')==one and np.array_equal(image('paper-hidden'),source)
    both=deepcopy(one);both['layers'][1]['visible']=False
    assert read('both-hidden')==both and read('source-after-exports')==both
    png_file=Image.open(location/'both-hidden.png');assert png_file.format=='PNG' and png_file.mode=='RGBA'
    png=image('both-hidden');assert (png[580:630,850:940,3]==0).all(),'UI checker or opaque paper leaked into export'
    assert png[140,150,3]==128
    assert int(np.abs(png[140,150,:3].astype(int)-[229,57,53]).max())<=1
    jpeg_file=Image.open(location/'transparent-flattened.jpeg');assert jpeg_file.format=='JPEG' and jpeg_file.mode=='RGB' and jpeg_file.size==(960,640)
    jpeg=np.asarray(jpeg_file);alpha=png[:,:,3:4].astype(float)/255
    white=png[:,:,:3]*alpha+255*(1-alpha)
    rmse=float(np.sqrt(np.mean((jpeg.astype(float)-white)**2)))
    assert rmse<=5 and (jpeg[580:630,850:940]==255).all(),rmse
    for state,reference in {'backdrop-hide-undone':'paper-hidden','paper-hide-undone':'before','paper-hide-redone':'paper-hidden','backdrop-hide-redone':'both-hidden'}.items():
        assert read(state)==read(reference) and np.array_equal(image(state),image(reference)),state
    reopened=image('fresh-png/reopened');assert np.array_equal(reopened[:,:,3],png[:,:,3])
    composite_errors=[]
    for background in [0,255]:
        expected=png[:,:,:3]*alpha+background*(1-alpha)
        actual=reopened[:,:,:3]*alpha+background*(1-alpha)
        error=float(np.abs(actual-expected).max());assert error<=1;composite_errors.append(error)
    jpeg_error=int(np.abs(image('fresh-jpeg/reopened')[:,:,:3].astype(int)-jpeg.astype(int)).max());assert jpeg_error<=1
    assert (image('fresh-jpeg/reopened')[:,:,3]==255).all()
    assert read('fresh-project/reopened')==both and np.array_equal(image('fresh-project/reopened'),png)
    for path in [location/'events.json',*[location/('fresh-'+kind)/'events.json' for kind in ['png','jpeg','project']]]:
        downloads += [e for e in json.loads(path.read_text(encoding='utf-8')) if e['action']=='download']
    rows.append(dict(viewport=[row['width'],row['height']],paper_alone_hidden_preserves_opaque_backdrop=True,both_backings_hidden_gives_true_transparency=True,red_half_opacity_rgba=png[140,150].tolist(),jpeg_white_flattening_rgb_rmse=rmse,jpeg_fresh_decode_max_error=jpeg_error,png_fresh_composite_max_errors=composite_errors,full_source_history_and_fresh_project_exact=True))
assert len(downloads)==88
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,rows=rows,actual_downloads_verified=88,render_time_ms=10000,oracle='Complete expected visibility-only JSON mutations; independently decoded RGBA, clear region and known half-opacity red; JPEG composited over white with predeclared RGB RMSE<=5, fresh PNG alpha exact and black/white composites <=1, JPEG fresh decoder <=1. Actual exports, full history and fresh editable-project reopen.',execution='Isolated headless production controls and real downloaded files; no desktop interaction')
(root/'evidence/LAYER-010-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
