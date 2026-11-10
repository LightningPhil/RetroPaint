"""Close font acceptance and retain the LIVE-041 preview correction evidence."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import hashlib,json,re
folder=Path(__file__).resolve().parent;root=folder.parents[2];evidence=root/'test-results/audit-2026-11-05';report=json.loads((evidence/'all-forty-one-fixes/report.json').read_bytes());assert report['status']=='Pass' and all(hashlib.sha256((root/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in report['source_files']);assert json.loads((evidence/'mouse/caption-font41-verification.json').read_bytes())['status']=='Pass'
note='LIVE-041: flattened bitmap previews differed from directly rendered vector captions, especially at50%Strength with opaque paper (native paired screenshot maxchannel76). Plain vector previews now cache a non-mutating TextObject layout and use the placement renderer. Nine native vector font/alignment/style rows and the50%opaque stress caption now have identical preview/placed screenshot pixels; all nine raster rows already matched. New48-combination regression (sixfonts,twofontsizes,twoStrengths,twoBackgrounds) fails before and passes after on four layouts. Full696checks, TypeScript/build and diffcheck pass.'
fontnote='Eighteen native two-line captions cover all six installed font families and three alignments, Raster/Vector,18/24/36.5px,180/260/360widths,transparent/secondaryYellowpaper, and all21factor pairs of font/alignment/mode/fourstyleflags. Independently verified font metadata/hashes, actualUIvalues, sourceTextObject properties/line breaks, nativepointer placement/move, exactRasterRGBA, unchangedneighbours, completeUndoRedo, and all18nativeproject/PNG reopens. Contact sheet visually confirms readable words and coherent styling. Impact bold/italic may be synthesized; unavailablefont fallback not triggered on this platform. This is pairwise coverage, not a full Cartesian product.'
lp=folder/'execution.json';ledger=json.loads(lp.read_text(encoding='utf-8-sig'))
for case in ledger['cases']:
 if case['id'] not in ('EDIT-021','EDIT-022','EDIT-023'):continue
 if note not in case['observations']:case['observations'].append(note)
 if case['id'] in ('EDIT-021','EDIT-022') and fontnote not in case['observations']:case['observations'].append(fontnote)
 if case['id']=='EDIT-022':case['status']='Pass'
 for name in ('caption-font41-verification.json','caption-font40-evidence.json','caption-font-plan40.json','caption-font40-contact-sheet.png','caption-preview41-evidence.json','caption-preview41-before-preview.jpg','caption-preview41-before-placed.jpg'):
  path='test-results/audit-2026-11-05/mouse/'+name
  if path not in case['evidence']:case['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();lp.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');counts=Counter(c['status'] for c in ledger['cases']);assert counts=={'Pass':81,'Partial':265,'Blocked':3}
rp=folder/'README.md';text=rp.read_text(encoding='utf-8').replace('**80 Pass, 266 Partial','**81 Pass, 265 Partial').replace('after all forty fixes passes **692 checks','after all forty-one fixes passes **696 checks').replace('(`all-forty-fixes/report.json`)','(`all-forty-one-fixes/report.json`)')
if '## LIVE-041:' not in text:text+='\n## LIVE-041: vector text preview and font matrix\n\n'+note+'\n\n'+fontnote+'\n'
rp.write_text(text,encoding='utf-8');ep=evidence/'environment.json';env=json.loads(ep.read_text(encoding='utf-8-sig'))
for f in env['dirty_source']:f['sha256']=hashlib.sha256((root/f['path']).read_bytes()).hexdigest()
env['recorded']=ledger['updated'];env['fix_count']=41;env['latest_regression']={'report':'test-results/audit-2026-11-05/all-forty-one-fixes/report.json','passed':sum(s['passed'] for s in report['suites'])+1,'failed':0,'page_errors':0};assert env['latest_regression']['passed']==696
production=evidence/'production-seven-fixes';index=(production/'index.html').read_bytes();entry=re.search(rb'<script[^>]+src="([^"]+)"',index).group(1).decode();env['production_build']={'fixes':41,'index_sha256':hashlib.sha256(index).hexdigest(),'entry':entry,'entry_sha256':hashlib.sha256((production/entry.removeprefix('./').lstrip('/')).read_bytes()).hexdigest()};ep.write_text(json.dumps(env,indent=2)+'\n',encoding='utf-8');print(counts);print(env['latest_regression'])
