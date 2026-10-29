from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys
root=Path(__file__).resolve().parent;repo=root.parents[2];suffix=sys.argv[1];output=root/('evidence/build-'+suffix+'-source.json');assert not output.exists(),'Do not replace a build source snapshot'
sources=[repo/'index.html',repo/'package.json',repo/'package-lock.json',*sorted((repo/'src').glob('*')),*sorted((repo/'tests').glob('*'))]
report=dict(at=datetime.now(timezone.utc).isoformat(),source_files=[dict(path=str(p.relative_to(repo)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sources if p.is_file()],scope='Captured immediately before the immutable production build; subsequent verification must reuse these hashes.')
output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Captured',len(report['source_files']),'source hashes before build.')
