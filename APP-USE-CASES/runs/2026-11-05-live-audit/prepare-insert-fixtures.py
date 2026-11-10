"""Independent valid maximum and rejected image dimensions for Insert image."""
from pathlib import Path
from PIL import Image
import hashlib,json
root=Path(__file__).resolve().parents[3];folder=root/'test-results/audit-2026-11-05/fixtures/insert-limits';folder.mkdir(exist_ok=True);files=[]
for label,size in [('maximum',(4096,4096)),('maximum-width',(4096,1)),('maximum-height',(1,4096)),('over-width',(4097,1)),('over-height',(1,4097))]:
 path=folder/(label+'.png');Image.new('RGBA',size,(124,58,237,255)).save(path);files.append({'label':label,'dimensions':size,'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'accepted':max(size)<=4096})
(folder/'plan.json').write_text(json.dumps({'source_RGBA':[124,58,237,255],'files':files,'small_source':'fixtures/import-formats/source.png','small_native_move_delta':[150,100],'expected_small_anchor':[470,300],'scope':'AlloriginalMIXlayerdata/objectsunchangedexceptaddition/activeCharactercomposite; rejectedoversizessaveexactwholeproject; validmaxcanPlaceandUndo.'},indent=2)+'\n',encoding='utf-8');print(len(files))
