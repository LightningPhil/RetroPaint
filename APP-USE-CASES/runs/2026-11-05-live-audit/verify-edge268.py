"""Independently inspect refined drilled circular chamfer export."""
import json,math,hashlib
from pathlib import Path
from stl_oracle import read_binary,measure
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';dl=Path.home()/'Downloads';names=['mouse-audit-edge268.retropaint','mouse-audit-edge268-3d-mm.stl','mouse-audit-edge268-3d-mm (1).stl'];hashes={}
for n in names:
 raw=(dl/n).read_bytes();(out/n).write_bytes(raw);hashes[n]=hashlib.sha256(raw).hexdigest()
a=json.loads((out/'mouse-audit-edge207-drilled (1).retropaint').read_text());b=json.loads((out/names[0]).read_text());bodies=lambda d:next(l['cad']['bodies'] for l in d['layers'] if 'cad'in l);assert bodies(a)==bodies(b)
raw=(out/names[1]).read_bytes();assert raw==(out/names[2]).read_bytes();tri=read_binary(raw);stats=measure(tri);assert len(stats['components'])==1 and stats['components'][0]['euler']==0
expected=8000-80*math.pi-math.pi*(2*.5**2+.5**3/3);error=stats['signed_volume_mm3']-expected;assert abs(error)<.03
report={'case':'FEATURE-009','status':'Pass','full_regression':'all-seventy-nine-fixes/report.json','source_cad_bodies_exact':True,'reopened_stl_byte_exact':True,'mesh':stats,'analytic_volume_mm3':expected,'volume_error_mm3':error,'original_tolerance_mm3':.03,'original_error_mm3':.040126378940,'sha256':hashes};(out/'edge268-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['sha256','mesh']},indent=2))
