"""Independently verify actual native downloads at import boundaries."""
import base64, hashlib, json, struct
from collections import Counter
from pathlib import Path

root=Path(__file__).resolve().parents[3]
out=root/'test-results/audit-2026-11-05/mouse'
fixtures=root/'test-results/audit-2026-11-05/fixtures/code-limits'
downloads=Path.home()/'Downloads'
hashes={}
def retain(name):
    data=(downloads/name).read_bytes()
    (out/name).write_bytes(data)
    hashes[name]=hashlib.sha256(data).hexdigest()
    return data
def doc(stage):return json.loads(retain('mouse-audit-code-'+stage+'.retropaint'))
def bodies(d):return next(l for l in d['layers'] if l.get('cad'))['cad']['bodies']
def files(b):
    s=b['script'];result={f['path']:base64.b64decode(f['data']) for f in s.get('files',[])}
    assert s['entry'] not in result
    result[s['entry']]=s['source'].encode('utf-8')
    return result

stages=['limit-2000','limit-20mb','limit-2mb','unicode']
docs={s:doc(s) for s in stages}
names=['Limit 2000 files','Limit 20 MB files','Limit 2 MB source','Unicode source']
expected=[{str(p.relative_to(fixtures/'files-2000')).replace('\\','/'):p.read_bytes() for p in (fixtures/'files-2000').rglob('*') if p.is_file()},
          {p.name:p.read_bytes() for p in (fixtures/'bytes-20000000').iterdir()},
          {'script-2000000.scad':(fixtures/'script-2000000.scad').read_bytes()},
          {'unicode-図形.scad':(fixtures/'unicode-図形.scad').read_bytes()}]
baseline=json.loads(retain('mouse-audit-chooser-after-fix-document.retropaint'))
prev=baseline
for i,s in enumerate(stages):
    d=docs[s];assert d['layers'][:2]==baseline['layers'][:2]
    assert bodies(d)[:-1]==bodies(prev)
    b=bodies(d)[-1];assert b['name']==names[i]
    assert files(b)==expected[i],s
    prev=d
assert len(expected[0])==2000
assert sum(map(len,expected[1].values()))==20_000_000
assert len(expected[2]['script-2000000.scad'])==2_000_000
for name in ['script-2000000.scad','unicode-図形.scad']:
    assert retain(name)==(fixtures/name).read_bytes()
assert doc('after-errors')==docs['unicode'], 'Preview/cancel/import errors modified applied document'
assert doc('reopened')==docs['unicode'], 'Actual native reopen changed source, assets or scene'
assert doc('after-shortcuts')==docs['unicode'], 'Preview shortcuts/orbit/fit modified applied document'

meshes={}
for stage,size,volume in [(s,[2,3,4],24) for s in stages[:3]]+[('unicode',[7,5,3],105)]:
    suffix=' (1)' if stage=='limit-2000' else ''
    data=retain('mouse-audit-code-'+stage+'-3d-mm'+suffix+'.stl')
    n=struct.unpack_from('<I',data,80)[0];assert len(data)==84+n*50
    points=[];edges=Counter();directions=Counter();v=0
    for i in range(n):
        a,b,c=[struct.unpack_from('<3f',data,96+50*i+12*j) for j in range(3)]
        points.extend([a,b,c]);v+=sum(a[j]*(b[(j+1)%3]*c[(j+2)%3]-b[(j+2)%3]*c[(j+1)%3]) for j in range(3))/6
        for start,end in [(a,b),(b,c),(c,a)]:
            edge=tuple(sorted([start,end]));edges[edge]+=1;directions[edge]+=1 if start<end else -1
    bounds=[max(p[j] for p in points)-min(p[j] for p in points) for j in range(3)]
    assert n==12 and bounds==size and abs(v-volume)<1e-8
    assert all(count==2 for count in edges.values()) and not any(directions.values())
    meshes[stage]={'triangles':n,'size_mm':bounds,'volume_mm3':v,'closed_outward':True}
report={'native_2000_files_exact':True,'native_20MB_dependencies_exact':True,
        'native_2MB_source_exact':True,'native_unicode_filename_and_source_bytes_exact':True,
        'all_previous_models_and_non_cad_layers_exact':True,'whole_native_reopen_exact':True,
        'preview_failures_cancel_and_retry_leave_applied_document_exact':True,
        'scoped_stl_oracles':meshes,
        'diagnostic':'First limit-2000 STL used All visible scope; corrected native Selected visible export is (1).stl.',
        'sha256':hashes}
(out/'code-limits-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
