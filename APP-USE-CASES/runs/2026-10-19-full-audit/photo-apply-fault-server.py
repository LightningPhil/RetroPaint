"""Disposable, loopback-only production UI fault fixture.

Serves the immutable tested production bytes unchanged except for an appended
photo worker message wrapper. Preview jobs run normally. The first full-size
apply receives a delayed error; its next retry executes the original worker.
This is controlled failure injection, not a claim that production fails itself.
"""
from pathlib import Path
from datetime import datetime,timezone
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import hashlib,json

root=Path(__file__).resolve().parent
build=Path('C:/Users/pglei/.codex/visualizations/2026/10/19/01a15244-c238-7100-86bc-d9eebbf01437/retropaint-verified-build-20261020-photo-context')
workers=list((build/'assets').glob('photo-worker-*.js'))
assert len(workers)==1
worker=workers[0]
original=worker.read_bytes()
wrapper=b'''
// Acceptance-only protocol fault: the source worker above remains unchanged.
const auditOriginalPhotoHandler=self.onmessage;
let auditRejectFirstFullSize=true;
self.onmessage=event=>{
  const image=event.data?.image;
  if(image && Math.max(image.width,image.height)>720){
    if(auditRejectFirstFullSize){
      auditRejectFirstFullSize=false;
      setTimeout(()=>self.postMessage({id:event.data.id,error:'Audit injected apply failure; the draft should remain available.'}),1500);
    }else setTimeout(()=>auditOriginalPhotoHandler(event),1500);
  }else auditOriginalPhotoHandler(event);
};
'''
served=original+wrapper
manifest=dict(at=datetime.now(timezone.utc).isoformat(),url='http://127.0.0.1:8092/',build=str(build),worker=worker.name,original_sha256=hashlib.sha256(original).hexdigest(),served_sha256=hashlib.sha256(served).hexdigest(),behavior='Append wrapper only; normal <=720 preview jobs; first full-size job delayed 1500ms then explicit error; subsequent full-size job delayed 1500ms then original handler. No application state injection.',source_worker_unchanged=worker.read_bytes()==original)
(root/'evidence/PHOTO-005-fault-worker.js').write_bytes(served)
(root/'evidence/PHOTO-005-fault-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(build),**kwargs)
    def do_GET(self):
        if self.path.split('?',1)[0]=='/assets/'+worker.name:
            self.send_response(200);self.send_header('Content-Type','text/javascript');self.send_header('Content-Length',str(len(served)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(served)
        else:super().do_GET()
    def log_message(self,format,*args):
        with (root/'evidence/PHOTO-005-fault-server.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(dict(at=datetime.now(timezone.utc).isoformat(),message=format%args))+'\n')
print(json.dumps(manifest),flush=True)
ThreadingHTTPServer(('127.0.0.1',8092),Handler).serve_forever()
