"""Loopback-only production byte server with visible acceptance fault controls."""
from datetime import datetime,timezone
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit
import argparse,hashlib,json,threading

folder=Path(__file__).resolve().parent;root=folder.parents[2]
build=root/'test-results/audit-2026-11-05/production-84'
out=root/'test-results/audit-2026-11-05/fault-controls281';out.mkdir(exist_ok=True)
state={'stall':False,'block':False};lock=threading.Lock()
def log(value):
 with lock:
  with (out/'requests.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({'at':datetime.now(timezone.utc).isoformat(),**value})+'\n')
worker_prelude=b'''
const auditNativeFetch=self.fetch.bind(self);
self.fetch=(input,options)=>{const u=typeof input==='string'?input:input.url||String(input);if(!u.startsWith('data:')&&!u.startsWith('blob:'))void auditNativeFetch('/audit-event',{method:'POST',body:JSON.stringify({type:'worker fetch',detail:(options?.method||'GET')+' '+u})});return auditNativeFetch(input,options);};
const auditNativePost=self.postMessage.bind(self);
self.postMessage=(message,options)=>{if(message.image||message.error)for(const r of performance.getEntriesByType('resource'))if(!r.name.includes('/audit-'))void auditNativeFetch('/audit-event',{method:'POST',body:JSON.stringify({type:'worker resource',detail:{url:r.name,transferSize:r.transferSize,encodedBodySize:r.encodedBodySize,decodedBodySize:r.decodedBodySize}})});return auditNativePost(message,options);};
'''
cpu=b'''
if(typeof OffscreenCanvas!=='undefined'){const native=OffscreenCanvas.prototype.getContext;OffscreenCanvas.prototype.getContext=function(type,...args){return /webgl/i.test(type)?null:native.call(this,type,...args);};}
'''
cad=b'''
const auditAddListener=self.addEventListener.bind(self);
self.addEventListener=(type,listener,options)=>auditAddListener(type,type==='message'?async(event)=>{
const control=await(await auditNativeFetch('/audit-consume-cad')).json();
if(control.stall){self.postMessage({id:event.data.id,started:true});return;}
listener(event);
}:listener,options);
'''
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(build),**kwargs)
 def send_response(self,code,message=None):
  log({'response_path':self.path,'status':code});super().send_response(code,message)
 def send(self,data,kind='text/javascript',status=200):
  self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
 def do_POST(self):
  data=self.rfile.read(int(self.headers.get('Content-Length',0)))
  if self.path=='/audit-command':
   command=data.decode();state['stall']=True if command=='stall-cad' else state['stall']
   if command in ['block-model','allow-model']:state['block']=command=='block-model'
   log({'command':command});self.send(b'{}','application/json')
  elif self.path=='/audit-event':
   log({'event':json.loads(data)});self.send(b'{}','application/json')
  else:log({'unexpected_post':self.path,'bytes':len(data)});self.send(b'{}','application/json',404)
 def do_GET(self):
  path=urlsplit(self.path).path
  if path=='/audit-consume-cad':
   stall=state['stall'];state['stall']=False;log({'cad_stall_consumed':stall});self.send(json.dumps({'stall':stall}).encode(),'application/json');return
  log({'method':'GET','path':self.path})
  if path=='/audit-controls.js':
   data=(folder/'fault-controls259.js').read_bytes();digest=hashlib.sha256(data).hexdigest()
   (out/('controls-'+digest+'.js')).write_bytes(data);log({'controls_served_sha256':digest});self.send(data);return
  if path=='/':
   data=(build/'index.html').read_bytes().replace(b'<head>',b'<head><script src="/audit-controls.js"></script>');self.send(data,'text/html');return
  if '/models/super-resolution/' in path and state['block']:self.send(b'Audit controlled missing model','text/plain',503);return
  if path.startswith('/assets/') and 'worker-' in path:
   data=(build/path.lstrip('/')).read_bytes();pre=worker_prelude
   if 'super-resolution-worker' in path and 'cpu=1' in self.path:pre+=cpu
   if 'cad-worker' in path:pre+=cad
   self.send(pre+data);return
  super().do_GET()
 def log_message(self,*args):pass

parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=0);args=parser.parse_args()
server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
manifest={'origin':f'http://127.0.0.1:{server.server_port}/','build':str(build),
          'controls_sha256':hashlib.sha256((folder/'fault-controls259.js').read_bytes()).hexdigest(),
          'seams':'Explicit visible controls; canvas encoder gate/null; disposable storage denial; worker fetch log/WebGL denial; single stalled CAD request with real production timeout. Original production files unchanged.'}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest),flush=True);server.serve_forever()
