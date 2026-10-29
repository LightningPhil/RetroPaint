from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,base64,io
from PIL import Image,ImageChops

root=Path(__file__).resolve().parent
repo=root.parents[2]
build=Path('C:/Users/pglei/.codex/visualizations/2026/10/19/01a15244-c238-7100-86bc-d9eebbf01437/retropaint-verified-build-20261020-0920')
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
original=root/'backups/artwork-before-acceptance-audit.retropaint'
assert sha(original)=='612e2d0b4db85c61a4722de26aff3810fa2c4b17e5c5dc49391ca349e1fcfa28'
doc=json.loads(original.read_text(encoding='utf-8'))
copies=[]
for stem in ['ARTWORK-production-saved','ARTWORK-production-reopened']:
    path=root/'evidence'/(stem+'.retropaint')
    assert json.loads(path.read_text(encoding='utf-8'))==doc,stem
    copies.append(dict(file=str(path.relative_to(root)),bytes=path.stat().st_size,sha256=sha(path),all_project_fields_exact=True))
saved=Image.open(root/'evidence/ARTWORK-production-saved.png').convert('RGBA')
reopened=Image.open(root/'evidence/ARTWORK-production-reopened.png').convert('RGBA')
assert saved.size==reopened.size==(960,640) and saved.tobytes()==reopened.tobytes()
composed=Image.new('RGBA',saved.size)
for layer in doc['layers']:
    pixels=Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',',1)[1]))).convert('RGBA')
    assert pixels.size==saved.size and not layer.get('photo') and not layer.get('objects')
    if layer['visible']:
        if layer['opacity']!=1:pixels.putalpha(pixels.getchannel('A').point(lambda a:round(a*layer['opacity'])))
        composed=Image.alpha_composite(composed,pixels)
maximum=max(high for low,high in ImageChops.difference(composed,saved).getextrema())
assert maximum<=1,maximum
report=dict(at=datetime.now(timezone.utc).isoformat(),immutable_backup_sha256=sha(original),browser='Codex built-in Chromium',production_url='http://127.0.0.1:8088/?verified-artwork',production_build=str(build),copies=copies,full_project_save_and_actual_chooser_reopen_exact=True,rendered_rgba_save_reopen_exact=True,independent_layer_composite_maximum_channel_difference=maximum,decoder='Pillow '+Image.__version__,layers=[l['name'] for l in doc['layers']],active=doc['active'],dimensions=saved.size)
(root/'evidence/ARTWORK-production-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
verification=json.loads((root/'backups/verification.json').read_text(encoding='utf-8'))
verification['production_actual_chooser_roundtrip']=report
(root/'backups/verification.json').write_text(json.dumps(verification,indent=2)+'\n',encoding='utf-8')
sources=[p for directory in ['src','tests'] for p in (repo/directory).rglob('*') if p.is_file() and p.suffix in ['.ts','.css','.html']]
sources+=[repo/name for name in ['index.html','package.json','package-lock.json','vite.config.ts','tsconfig.json']]
manifest=dict(at=report['at'],build_directory=str(build),url=report['production_url'],source_files=[dict(path=str(p.relative_to(repo)),sha256=sha(p)) for p in sorted(sources)],build_files=[dict(path=str(p.relative_to(build)),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(build.rglob('*')) if p.is_file()])
(root/'production-snapshot.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
