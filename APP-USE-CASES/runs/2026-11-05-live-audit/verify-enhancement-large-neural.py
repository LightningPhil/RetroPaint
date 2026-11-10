"""Validate a real 47MP neural stream independently, with bounded zlib row decoding."""
from pathlib import Path
import hashlib,json,struct,zlib
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';name='mouse-audit-enhance154-grid-4x-enhanced (1).png';data=(downloads/name).read_bytes();(out/name).write_bytes(data);assert data[:8]==b'\x89PNG\r\n\x1a\n';pos=8;blocks=[];kinds=[]
while pos<len(data):
    n=struct.unpack_from('>I',data,pos)[0];kind=data[pos+4:pos+8];body=data[pos+8:pos+8+n];assert zlib.crc32(kind+body)&0xffffffff==struct.unpack_from('>I',data,pos+8+n)[0];kinds.append(kind)
    if kind==b'IHDR':assert struct.unpack('>IIBBBBB',body)==(8400,5592,8,6,0,0,0)
    if kind==b'IDAT':blocks.append(body)
    pos+=n+12
assert pos==len(data) and kinds[-1]==b'IEND';decoder=zlib.decompressobj();pending=b'';rows=0;stride=1+8400*4
for block in blocks:
    chunk=block
    while chunk:
        pending+=decoder.decompress(chunk,1024*1024);chunk=decoder.unconsumed_tail
        while len(pending)>=stride:
            assert pending[0] in [0,1];pending=pending[stride:];rows+=1
assert decoder.eof and not pending and rows==5592
image=Image.open(out/name);image.load();assert image.size==(8400,5592) and image.getchannel('A').getextrema()==(255,255)
reference=Image.open(downloads/'mouse-audit-photo98-full-reset.png').convert('RGB');a=np.array(image.convert('RGB').resize(reference.size,Image.Resampling.BOX)).astype(float);b=np.array(reference).astype(float);error=float(abs(a-b).mean());correlation=float(np.corrcoef(a.ravel(),b.ravel())[0,1]);assert error<12 and correlation>.98,(error,correlation)
before=(downloads/'mouse-audit-photo98-full-reset.retropaint').read_bytes();after=(downloads/'mouse-audit-enhance156-after.retropaint').read_bytes();(out/'mouse-audit-enhance156-after.retropaint').write_bytes(after);assert before==after
report=dict(status='Pass',dimensions=list(image.size),pixels=8400*5592,bytes=len(data),crc_zlib_all_rows_complete=True,decoded_rows=rows,alpha_opaque=True,source_mean_RGB_error=error,source_correlation=correlation,original_project_byte_exact=True,sha256=hashlib.sha256(data).hexdigest(),filename_note='App retained the previous grid filename, so Chrome appended (1). This file is the actual large neural export; original grid remains separately retained.');(out/'enhance156-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
