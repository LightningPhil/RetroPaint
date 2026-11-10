"""Decode actual native neural and transparent large streamed PNG outputs."""
import hashlib,json,struct,zlib
from pathlib import Path
from PIL import Image,ImageChops
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse'
downloads=Path.home()/'Downloads';hashes={}
def retain(name):
 data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(s):return json.loads(retain('mouse-audit-'+s+'.retropaint'))
assert doc('cpu-source')==doc('cpu-after-missing-model')==doc('cpu-after-success')
gpu=Image.open(downloads/'mouse-audit-gpu-detail16-2x-enhanced.png').convert('RGBA')
cpu=Image.open(downloads/'mouse-audit-cpu-after-missing-model-2x-enhanced.png').convert('RGBA')
for name in ['gpu-detail16','cpu-after-missing-model']:retain('mouse-audit-'+name+'-2x-enhanced.png')
assert gpu.size==cpu.size==(32,32) and gpu.tobytes()==cpu.tobytes()
source=Image.open(root/'test-results/audit-2026-11-05/fixtures/cpu-detail-16.png').convert('RGBA')
assert gpu.tobytes()!=source.resize((32,32),Image.Resampling.LANCZOS).tobytes()
assert doc('transparent-limit')==doc('transparent-limit-after')
streamed=[]
for scale,edge in [(2,8192),(4,16384)]:
 name=f'mouse-audit-transparent-limit-{scale}x-enhanced.png';data=retain(name)
 assert data[:8]==b'\x89PNG\r\n\x1a\n';pos=8;compressed=[];kinds=[]
 while pos<len(data):
  n=struct.unpack_from('>I',data,pos)[0];kind=data[pos+4:pos+8];body=data[pos+8:pos+8+n]
  assert zlib.crc32(kind+body)&0xffffffff==struct.unpack_from('>I',data,pos+8+n)[0]
  kinds.append(kind)
  if kind==b'IHDR':assert struct.unpack('>IIBBBBB',body)==(edge,edge,8,6,0,0,0)
  if kind==b'IDAT':compressed.append(body)
  pos+=n+12
 assert pos==len(data) and kinds[-1]==b'IEND'
 # Bounded independent zlib/PNG row decoder; avoids a 1 GiB oracle canvas.
 decoder=zlib.decompressobj();pending=b'';rows=0;stride=1+edge*4
 for block in compressed:
  chunk=block
  while chunk:
   pending+=decoder.decompress(chunk,1024*1024);chunk=decoder.unconsumed_tail
   while len(pending)>=stride:
    row,pending=pending[:stride],pending[stride:]
    assert row[0] in [0,1] and not any(row[1:]);rows+=1
 assert decoder.eof and not pending and rows==edge
 streamed.append({'scale':scale,'dimensions':[edge,edge],'pixels':edge*edge,'all_rgba_zero':True,'crc_and_zlib_complete':True,'bytes':len(data)})
report={'native_cpu_and_gpu_same_neural_model_pixel_exact':[32,32],
 'neural_result_differs_from_lanczos':True,'source_project_exact_after_failure_cancel_and_success':True,
 'transparent_large_source_project_unchanged':True,'transparent_fast_path_not_opaque_neural_inference':True,
 'independently_decoded_streams':streamed,'sha256':hashes}
(out/'enhancement-boundary-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
