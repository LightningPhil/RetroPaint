"""Close live draft retention and distinct large-document cutoffs."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import json
folder=Path(__file__).resolve().parent;root=folder.parents[2];assert json.loads((root/'test-results/audit-2026-11-05/mouse/recovery45-retention-verification.json').read_bytes())['status']=='Pass'
lp=folder/'execution.json';ledger=json.loads(lp.read_text(encoding='utf-8-sig'));c=next(c for c in ledger['cases'] if c['id']=='FILE-024');c['status']='Pass'
note='Dedicated65487audit-origin recovery DB, predeclared16fileplan: ten32square nativeprojectopenings individuallyreachDraftsaved; allthreeRecentdraftspages contain exactlyCount10..03, count01/02evicted. Four2048square opaque randomRGBprojects eachactual19241350characters/38482700UTF16bytes; fourthforces128Mbudgeteviction ofBudget01 whileBudget04..02plusCount10..06remain8. Threebig+smallfit; fourbigexceed128M independentlycomputed. Separate4096square one-layernoise16777216pixels yields76957842characters>50M andautomaticdraftsizemessage; two4096white layers33554432pixels<1Mcharactersyield24Mstored-pixelmessage. BothstatusbuttonsproduceactualeditableSaveprojectdownloads, allsourceRGBAexact, bothmanualfilesnative-reopen/resavewholeJSONexact. Neitherineligibleopeningchangespreexisting8draftcards/order. LatestvalidBudget04nativeResume/resavewholeprojectexact, provingprotectedcontentnotjustcardretention.'
if note not in c['observations']:c['observations'].append(note)
for name in ['recovery45-retention-verification.json','recovery45-evidence.json','recovery45-count-last-page.jpg','recovery45-latest-protected.jpg','recovery45-recovered.jpg']:
    path='test-results/audit-2026-11-05/mouse/'+name
    if path not in c['evidence']:c['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();lp.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');counts=Counter(c['status'] for c in ledger['cases']);assert counts=={'Pass':97,'Partial':248,'Blocked':4}
rp=folder/'README.md';text=rp.read_text(encoding='utf-8').replace('**96 Pass, 249 Partial','**97 Pass, 248 Partial')
if '## FILE-024: native recovery retention and cutoffs' not in text:text+='\n## FILE-024: native recovery retention and cutoffs\n\n'+note+'\n'
rp.write_text(text,encoding='utf-8');print(counts)
