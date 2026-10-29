from pathlib import Path
from datetime import datetime,timezone
import json
root=Path(__file__).resolve().parent;file=root/'results.json';results=json.loads(file.read_text(encoding='utf-8'));assert results['cases']['FILE-001']['status']=='Fail'
for name in ['browser_regressions','production_build','desktop_layout','phone_390_layout','phone_320_layout','phone_844_layout','artwork_production_roundtrip','source_consistency']:
    item=results['supplementary_checks'][name];item['previous_status']=item['status'];item['status']='Pending';item['current_source_note']='D-020 New picture dimensions/acceptance repair and meaningful failing-before/passing-after four-layout regression added. Prior evidence is historical until the complete current-source suite, immutable build and original artwork roundtrip are verified.'
results['updated_at']=datetime.now(timezone.utc).isoformat();file.write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
