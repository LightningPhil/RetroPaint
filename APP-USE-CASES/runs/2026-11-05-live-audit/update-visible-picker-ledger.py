"""Close visible-composite picker with hidden-layer and no-dot proof."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import json
folder=Path(__file__).resolve().parent;root=folder.parents[2];assert json.loads((root/'test-results/audit-2026-11-05/mouse/picker45-verification.json').read_bytes())['status']=='Pass'
lp=folder/'execution.json';ledger=json.loads(lp.read_text(encoding='utf-8-sig'));c=next(c for c in ledger['cases'] if c['id']=='INK-002');c['status']='Pass'
note='Four actualMIX halfCharacter cases: plainBlue#1E88E5, halfRedoverBlue#8F4472, hiddenCharacterBlue#1E88E5, hiddenBackdropRedoverWhite#FF7F7F. IndependentPillow8bitopacity/source-overderivation exact; originalplan float50%Whitechannel128hypothesisretainedandcorrectedto127becausealpha128leaves127/255White, no tolerancewideningorproductbugclaim. NativeRightpickretainsmagnifierwithcentralpixel/hex, leftpickreturnsmarker; bothsampleswholeprojectunchanged, no dot. VisibleWhite180x80testcardaddedonlytoseparateMIXcopyawayfromsamplepoints. Fournew22pxswatchcapsulesmatchindependentRGB/alpha; sourceRaster/otherlayers/Dog/metadataunchanged, oneCaptionRasterpieceaddedabovestamp. WholeUndo/Redoexact, nativeprojectreopenonlyomitsinactivewet:falseflag, allotherdefinition/imagefields exact; allfouractualPNG-reopenRGBAexact. Rawfixturebooleanpaperflagsnormalizetonullasnon-colourvalues, sourceRGBAexact; documentedinitialno-cardpreviewandWindowsforwardslashpathcorrectionnotcountedascompletedvariant.'
if note not in c['observations']:c['observations'].append(note)
for name in ['picker45-verification.json','picker45-evidence.json']+[f'picker45-{x}-magnifier.jpg' for x in ['plain-blue-v2','half-red-over-blue','hidden-character','hidden-backdrop']]:
    path='test-results/audit-2026-11-05/mouse/'+name
    if path not in c['evidence']:c['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();lp.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');counts=Counter(c['status'] for c in ledger['cases']);assert counts=={'Pass':99,'Partial':246,'Blocked':4}
rp=folder/'README.md';text=rp.read_text(encoding='utf-8').replace('**98 Pass, 247 Partial','**99 Pass, 246 Partial')
if '## INK-002: visible composite sampling' not in text:text+='\n## INK-002: visible composite sampling\n\n'+note+'\n'
rp.write_text(text,encoding='utf-8');print(counts)
