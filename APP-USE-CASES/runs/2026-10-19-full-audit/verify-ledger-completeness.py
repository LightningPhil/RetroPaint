from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import csv,json,hashlib
root=Path(__file__).resolve().parent;folder=root.parents[1];file=folder/'EXECUTION-LEDGER.csv';rows=list(csv.DictReader(file.open(encoding='utf-8-sig',newline='')));index=list(csv.DictReader((folder/'CASE-INDEX.csv').open(encoding='utf-8-sig',newline='')));results=json.loads((root/'results.json').read_text(encoding='utf-8'));assert len(rows)==len(index)==349 and len({r['case_id'] for r in rows})==349 and [r['case_id'] for r in rows]==[r['id'] for r in index];expected=Counter(r['status'] for r in results['cases'].values());expected['Not run']+=349-len(results['cases']);assert Counter(r['status'] for r in rows)==expected
for row in rows:
    case=results['cases'].get(row['case_id']);assert row['status']==(case['status'] if case else 'Not run')
    if case and 'headless/' in case['evidence_paths']:assert 'headless' in row['browser_and_os'] and 'via CUA' not in row['input_device']
report=dict(at=datetime.now(timezone.utc).isoformat(),canonical_ids_and_order_exact=True,rows=349,unique_ids=349,status_counts=dict(expected),all_recorded_statuses_match_authoritative_results=True,headless_execution_not_mislabelled_as_CUA=True,ledger_sha256=hashlib.sha256(file.read_bytes()).hexdigest(),notes='Recovered full inventory from untouched CASE-INDEX, retaining intact results/evidence. Ledger output now prevalidates schema/counts and replaces atomically. No acceptance status was inferred from document structure.');(root/'evidence/ledger-completeness-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(rows=349,status_counts=dict(expected))))
