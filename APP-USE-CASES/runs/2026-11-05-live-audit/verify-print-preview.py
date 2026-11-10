"""Compare the actual print iframe image and whole project after native Cancel."""
from pathlib import Path
from PIL import Image
import hashlib,json,numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def actual(s,ext='retropaint'):
    name='mouse-audit-print45-mix-'+s+'.'+ext;b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
before=json.loads(actual('before'));assert before==json.loads(actual('cancelled'));assert len(before['layers'])==4
actual('before','png');export=np.array(Image.open(out/'mouse-audit-print45-mix-before.png').convert('RGBA'));printed=np.array(Image.open(out/'print45-iframe-image.png').convert('RGBA'));assert export.shape==(100,200,4) and np.array_equal(export,printed)
assert np.all(printed[10:90,10:100]==[255,0,0,255]) and np.all(printed[:,130:]==[30,136,229,255])
shot=np.array(Image.open(out/'print45-native-preview-clean.png').convert('RGB'))
# Native preview page has a 70x35px rendered picture, surrounded by white paper.
blue=(shot[:,:,0]<70)&(shot[:,:,1]>90)&(shot[:,:,1]<180)&(shot[:,:,2]>180);blue[:100]=False;blue[200:]=False;blue[:,:420]=False;blue[:,600:]=False
y,x=np.where(blue);assert len(x)>800 and 65<=x.max()-x.min()+1<=73 and 32<=y.max()-y.min()+1<=37
report={'status':'Pass','native_print_preview_one_page_crop_aspect_2_to_1':True,'actual_print_frame_RGBA_matches_export_exactly':True,'native_cancel_whole_four_layer_project_exact':True,'preview_editor_overlays_absent':'Native screenshot shows only cropped red/blue composition on white print page plus browser-generated print headers/footer. No editor toolbar/layers/cursor/selection overlay in printed image.','physical_printer':'External integration not performed; case explicitly excludes inferring it from preview.','sha256':hashes}
(out/'print45-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
