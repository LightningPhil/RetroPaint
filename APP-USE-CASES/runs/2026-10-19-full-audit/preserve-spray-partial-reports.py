from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parent;rows=[]
for case,total in [('PAINT-010',240),('PAINT-011',240),('PAINT-012',300)]:
    file=root/f'evidence/{case}-independent-verification.json';report=json.loads(file.read_text(encoding='utf-8'));assert report['acceptance_status']=='Partial' and len(report['positive_rows'])==12 and len(report['cancellations'])==4 and report['actual_downloads_verified']==total;backup=root/f'evidence/{case}-earlier-Partial-verification.json';assert not backup.exists();backup.write_bytes(file.read_bytes());rows.append(dict(case=case,sha256=hashlib.sha256(backup.read_bytes()).hexdigest()))
print(json.dumps(dict(preserved_original_reports=rows,reason='Retain original Partial and all old observations before re-verifying the same780 raw downloads and closing only the previously missing genuine-blur rows. No old artifact or input changes.')))
