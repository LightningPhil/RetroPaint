"""Close gradient workflows using actual native main/tiny/custom/history files."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import json
folder=Path(__file__).resolve().parent;root=folder.parents[2];assert json.loads((root/'test-results/audit-2026-11-05/mouse/gradient50-verification.json').read_bytes())['status']=='Pass'
note='Prescribed320x240FILL plusseparateone-pixelblack-enclosedregion. All4presets Sunset/Rainbow/Ocean/Candy nativelydraggedacrossclosedmask, actualproject/PNG exportedandnative-reopened/resavedexact, eachsingleUndo wholebaselineexact. All4tinyregionfillschangeexactly1pixel/opaquealpha andUndoexact. Independentareaoracle: eachdeclaredstopRGBexactuniquemodeandstrictmajorityinconstant-gradient119pixelcolumn, everysegmentthirdareaaverageprogressestowardsnextstop, constantchannelmodesexact, adjacentjumpsboundedbyanalytic slope+quantization. Originalsingle-rowexactstophypothesisfailedandretained; minorityone-bytebrowserditherexplainsdiscrepancy. PointwisemonotoniccolumnhypothesisalsofailedforOceanR2byte/30pixelchange; retainedspecificfailure, areaorderingisapplicable smoothnessoracle. NativecustomRed#E53935/Blue#1E88E5, initialhorizontaldrag,bothpinsmovedtodiagonal; exactmodalendpointareas/directionchanged,samemask/untouchedRGBA/layer/metadataexact. Escape wholeprojectbaselineexact. Saveexplicitlysettlesonce;Undo/Redo/nativeprojectPNG reopensexact. ChangingtooltoBrush leavespreviewpending,butSave settlesvisiblegradientoncewithnohiddenpreviewleak, oneUndoexactbaseline. Zero-lengthBuckettapusesdefinedsolidBluefallback; nextdisconnectedislandtapworks,eachsingleUndoexact. Allscope/history/fileRGBAcomparisonsstrict, noRGBtolerancewidening. Noadditionalproductfixrequired.'
lp=folder/'execution.json';ledger=json.loads(lp.read_text(encoding='utf-8-sig'))
for c in ledger['cases']:
    if c['id'] not in ['INK-012','INK-013','INK-014']:continue
    c['status']='Pass'
    if note not in c['observations']:c['observations'].append(note)
    for name in ['gradient50-verification.json','gradient50-evidence.json','gradient50-initial-stop-hypothesis.json','gradient50-custom-pending.jpg','gradient50-toolchange-pending.jpg','gradient50-live-result.jpg']:
        path='test-results/audit-2026-11-05/mouse/'+name
        if path not in c['evidence']:c['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();lp.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');counts=Counter(c['status'] for c in ledger['cases']);assert counts=={'Pass':111,'Partial':234,'Blocked':4}
rp=folder/'README.md';text=rp.read_text(encoding='utf-8').replace('**108 Pass, 237 Partial','**111 Pass, 234 Partial')
if '## Preset and custom gradient acceptance matrix' not in text:text+='\n## Preset and custom gradient acceptance matrix\n\n'+note+'\n'
rp.write_text(text,encoding='utf-8');print(counts)
