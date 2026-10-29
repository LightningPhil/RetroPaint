from pathlib import Path
from datetime import datetime,timezone
import json
root=Path(__file__).resolve().parent;file=root/'production-photo-toolbar-snapshot.json';original=json.loads(file.read_text(encoding='utf-8'));retained=root/'production-photo-toolbar-snapshot-initial-mispaired.json';assert not retained.exists()
retained.write_text(json.dumps(original,indent=2)+'\n',encoding='utf-8')
reg=json.loads((root/'headless/20261020-photo-toolbar-full/report.json').read_text(encoding='utf-8'))
original['source_files']=reg['source_files'];original['source_manifest_evidence']='headless/20261020-photo-toolbar-full/report.json'
original['source_pairing_correction']=dict(at=datetime.now(timezone.utc).isoformat(),reason='The artwork verifier originally sampled source after later D-015/curve edits, rather than at build time. No source-consistency Pass was recorded from that sampling. Replaced only source hashes with the contemporaneous full-regression manifest, captured after this build and before those edits. The failed regression status is retained and does not affect the correctness of those historical source hashes.',retained='production-photo-toolbar-snapshot-initial-mispaired.json')
file.write_text(json.dumps(original,indent=2)+'\n',encoding='utf-8');print('Corrected historical D-014 source pairing; original metadata retained.')
