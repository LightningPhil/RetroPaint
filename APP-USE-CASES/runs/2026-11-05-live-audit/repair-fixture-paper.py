"""Correct synthetic fixture paper metadata; retain original historical bytes."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
root=Path(__file__).resolve().parents[3];audit=root/'test-results/audit-2026-11-05';fixtures=audit/'fixtures'
out=fixtures/'corrected-paper';out.mkdir(exist_ok=True);records=[]
for source in sorted(set(fixtures.glob('mix-*.retropaint'))|set(fixtures.glob('cadmix*.retropaint'))):
    original=source.read_bytes();d=json.loads(original);changes=[]
    for l in d['layers']:
        if isinstance(l.get('paper'),bool):
            old=l['paper'];l['paper']='#ffffff' if old else None;changes.append({'layer':l['name'],'before':old,'after':l['paper']})
    if not changes:continue
    data=(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n').encode();target=out/source.name;target.write_bytes(data)
    records.append({'original':str(source),'original_sha256':hashlib.sha256(original).hexdigest(),'corrected':str(target),'sha256':hashlib.sha256(data).hexdigest(),'changes':changes})
kit=audit/'manual-blockers';target=out/'mix-half-character.retropaint';data=target.read_bytes();(kit/'MIX.retropaint').write_bytes(data)
p=kit/'manifest.json';manifest=json.loads(p.read_bytes())
for f in manifest['files']:
    if f['path']=='MIX.retropaint':f.update(source=str(target),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
manifest['paper_metadata_corrected']=datetime.now(timezone.utc).isoformat();p.write_text(json.dumps(manifest,indent=2)+'\n')
(out/'manifest.json').write_text(json.dumps({'reason':'Synthetic fixtures used boolean paper metadata. Current schema requires a hex colour or null. Original files retained; image and editable object content unchanged.','files':records},indent=2)+'\n')
print('Corrected',len(records),'synthetic fixtures and updated the manual MIX pack')
