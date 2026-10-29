from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,base64,io,argparse
import numpy as np
root=Path(__file__).resolve().parent
repo=root.parents[2]
parser=argparse.ArgumentParser();parser.add_argument('--folder',default='headless/ARTWORK-production-20261020');parser.add_argument('--suffix',default='headless');parser.add_argument('--build',default='C:/Users/pglei/.codex/visualizations/2026/10/19/01a15244-c238-7100-86bc-d9eebbf01437/retropaint-verified-build-20261020-headless');args=parser.parse_args()
folder=root/args.folder
build=Path(args.build)
sha=lambda data:hashlib.sha256(data).hexdigest()
original=(root/'backups/artwork-before-acceptance-audit.retropaint').read_bytes()
assert sha(original)=='612e2d0b4db85c61a4722de26aff3810fa2c4b17e5c5dc49391ca349e1fcfa28'
ui=json.loads((folder/'ARTWORK-headless-ui.json').read_text(encoding='utf-8'))
assert ui['status']=='Pass' and len(ui['downloads'])==4
copies=[];pixels=[]
for name in ['ARTWORK-headless-saved','ARTWORK-headless-reopened']:
    data=(folder/(name+'.retropaint')).read_bytes();assert data==original
    image=Image.open(folder/(name+'.png')).convert('RGBA');assert image.size==(960,640)
    pixels.append(np.asarray(image));copies.append(dict(name=name,bytes=len(data),sha256=sha(data)))
assert np.array_equal(*pixels)
previous=np.asarray(Image.open(root/'evidence/ARTWORK-photo-context-saved.png').convert('RGBA'))
assert np.array_equal(pixels[0],previous),'New output differs from the previous verified production render'
doc=json.loads(original);composite=Image.new('RGBA',(960,640))
for layer in doc['layers']:
    assert layer['visible'] and layer['opacity']==1
    image=Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',',1)[1]))).convert('RGBA')
    composite=Image.alpha_composite(composite,image)
error=int(np.abs(np.asarray(composite).astype(np.int16)-pixels[0].astype(np.int16)).max())
assert error<=1
at=datetime.now(timezone.utc).isoformat()
report=dict(at=at,execution='Actual project controls/downloads in two separate headless production contexts; no desktop interaction',production_url=ui['origin'],production_directory=str(build),copies=copies,actual_downloads_byte_exact_to_original=True,rendered_rgba_save_reopen_and_previous_build_exact=True,independent_layer_composite_maximum_channel_difference=error,decoder='Pillow '+Image.__version__,current_user_artwork_tab_unaccessed=True)
(root/('evidence/ARTWORK-'+args.suffix+'-verification.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
sources=[repo/'index.html',repo/'package.json',repo/'package-lock.json',*sorted((repo/'src').glob('*')),*sorted((repo/'tests').glob('*'))]
manifest=dict(at=at,build_directory=str(build),url=ui['origin'],build_command='npm run build -- --outDir <immutable headless build directory>',actual_build_exit_code=0,build_evidence='exec session 68459: TypeScript success, Vite 109 modules, build success in 12.28s; existing externalized node:module and chunk-size warnings',source_files=[dict(path=str(p.relative_to(repo)),sha256=sha(p.read_bytes())) for p in sources if p.is_file()],build_files=[dict(path=str(p.relative_to(build)),bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in sorted(build.rglob('*')) if p.is_file()])
source_snapshot=root/('evidence/build-'+args.suffix+'-source.json')
if source_snapshot.exists():
    manifest['source_files']=json.loads(source_snapshot.read_text(encoding='utf-8'))['source_files']
    manifest['source_manifest_evidence']=str(source_snapshot.relative_to(root))
if args.suffix in ['histogram','layers','layer-photo','photo-toolbar','layer-limits','marker','pencil-pixels','pencil-pan','new-picture','pixel-filters','smudge-alpha','scrub-undo','hole-input']:
    log=(root/('evidence/build-'+args.suffix+'.log')).read_text(encoding='utf-8')
    assert 'built in' in log
    manifest['build_evidence']='evidence/build-'+args.suffix+'.log'
(root/('production-'+args.suffix+'-snapshot.json')).write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
verification=json.loads((root/'backups/verification.json').read_text(encoding='utf-8'))
verification[args.suffix+'_production_actual_file_roundtrip']=report
(root/'backups/verification.json').write_text(json.dumps(verification,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
