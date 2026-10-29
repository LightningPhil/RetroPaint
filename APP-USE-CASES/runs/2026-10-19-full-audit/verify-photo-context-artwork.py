from pathlib import Path
from datetime import datetime,timezone
import base64,hashlib,io,json
from PIL import Image,ImageChops

root=Path(__file__).resolve().parent
repo=root.parents[2]
e=root/'evidence'
build=Path('C:/Users/pglei/.codex/visualizations/2026/10/19/01a15244-c238-7100-86bc-d9eebbf01437/retropaint-verified-build-20261020-photo-context')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original=root/'backups/artwork-before-acceptance-audit.retropaint'
assert sha(original)=='612e2d0b4db85c61a4722de26aff3810fa2c4b17e5c5dc49391ca349e1fcfa28'
doc=json.loads(original.read_text(encoding='utf-8'))
copies=[]
for suffix in ['saved','reopened']:
    p=e/('ARTWORK-photo-context-'+suffix+'.retropaint')
    assert p.read_bytes()==original.read_bytes()
    copies.append(dict(file=str(p.relative_to(root)),bytes=p.stat().st_size,sha256=sha(p)))
saved=Image.open(e/'ARTWORK-photo-context-saved.png').convert('RGBA')
reopened=Image.open(e/'ARTWORK-photo-context-reopened.png').convert('RGBA')
previous=Image.open(e/'ARTWORK-production-saved.png').convert('RGBA')
assert saved.size==reopened.size==(960,640) and saved.tobytes()==reopened.tobytes()==previous.tobytes()
composed=Image.new('RGBA',saved.size)
for layer in doc['layers']:
    pixels=Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',',1)[1]))).convert('RGBA')
    assert pixels.size==saved.size and not layer.get('photo') and not layer.get('objects')
    if layer['visible']:
        if layer['opacity']!=1:pixels.putalpha(pixels.getchannel('A').point(lambda a:round(a*layer['opacity'])))
        composed=Image.alpha_composite(composed,pixels)
maximum=max(hi for lo,hi in ImageChops.difference(composed,saved).getextrema())
assert maximum<=1
at=datetime.now(timezone.utc).isoformat()
report=dict(at=at,immutable_backup_sha256=sha(original),production_url='http://127.0.0.1:8090/',production_build=str(build),copies=copies,actual_downloads_byte_exact_to_original=True,rendered_rgba_save_reopen_and_previous_build_exact=True,independent_layer_composite_maximum_channel_difference=maximum,decoder='Pillow '+Image.__version__,layers=[l['name'] for l in doc['layers']],active=doc['active'],dimensions=saved.size,user_facing_artwork_tab_8088_untouched=True)
(e/'ARTWORK-photo-context-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
verification=json.loads((root/'backups/verification.json').read_text(encoding='utf-8'))
verification['photo_context_production_actual_chooser_roundtrip']=report
(root/'backups/verification.json').write_text(json.dumps(verification,indent=2)+'\n',encoding='utf-8')
sources=[p for directory in ['src','tests'] for p in (repo/directory).rglob('*') if p.is_file() and p.suffix in ['.ts','.css','.html']]
sources+=[repo/name for name in ['index.html','package.json','package-lock.json','vite.config.ts','tsconfig.json']]
manifest=dict(at=at,build_directory=str(build),url=report['production_url'],source_files=[dict(path=str(p.relative_to(repo)),sha256=sha(p)) for p in sorted(sources)],build_files=[dict(path=str(p.relative_to(build)),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(build.rglob('*')) if p.is_file()])
(root/'production-photo-context-snapshot.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
