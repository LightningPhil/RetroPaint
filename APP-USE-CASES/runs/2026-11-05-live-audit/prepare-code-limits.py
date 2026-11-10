"""Disposable exact accepted/rejected import boundaries; no user source files."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/fixtures/code-limits'
source=b'cube([2,3,4]);\n'
for count in [2000,2001]:
 folder=out/f'files-{count}';folder.mkdir(parents=True,exist_ok=True);(folder/'main.scad').write_bytes(source)
 for i in range(count-1):(folder/f'asset-{i:04}.dat').write_bytes(b'')
folder=out/'bytes-20000000';folder.mkdir(exist_ok=True);(folder/'main.scad').write_bytes(source)
(folder/'padding.bin').write_bytes(bytes(20_000_000-len(source)))
(out/'oversized.bin').write_bytes(bytes(20_000_001))
(out/'combined-too-large.bin').write_bytes(bytes(19_500_000))
for size in [2_000_000,2_000_001]:
 data=source+b'//'+b'x'*(size-len(source)-3)+b'\n';assert len(data)==size
 (out/f'script-{size}.scad').write_bytes(data)
(out/'unicode-図形.scad').write_text('// Café — 日本語 🖌️\nside=7;\ncube([side,5,3]);\n',encoding='utf-8',newline='\n')
(out/'invalid.scad').write_text('// Deliberately invalid source\ncube([);\n',encoding='utf-8',newline='\n')
manifest={str(p.relative_to(out)).replace('\\','/'):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.rglob('*')) if p.is_file()}
(out.parent/'code-limits-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'fixture_files':len(manifest),'total_bytes':sum(v['bytes'] for v in manifest.values()),'accepted_source_bytes':len(source)}))
