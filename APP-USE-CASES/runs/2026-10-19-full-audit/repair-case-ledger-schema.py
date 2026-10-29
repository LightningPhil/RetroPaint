from pathlib import Path
from datetime import datetime,timezone
import json
root=Path(__file__).resolve().parent;file=root/'results.json';results=json.loads(file.read_text(encoding='utf-8'));entry=results['cases']['FILE-002'];assert entry['expanded_headless_recheck']==results['supplementary_checks']['image_open_four_layout_recheck'];entry.pop('expanded_headless_recheck');results['updated_at']=datetime.now(timezone.utc).isoformat();file.write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print('Removed only the duplicate non-column metadata from the case row; complete recheck data remains in supplementary_checks and its own checkpoint. Regenerate the interrupted CSV from intact results.json.')
