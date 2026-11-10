"""Verify actual keyboard-save output and scene preservation across live key tests."""
import hashlib,json
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def retain(name):
    data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(stem):return json.loads(retain('mouse-audit-'+stem+'.retropaint'))
assert doc('mix-transparent-half')==doc('mix-after-keyboard-tabs')
baseline=doc('keyboard-cad');shortcut=doc('keyboard-cad (1)');piece=doc('keyboard-cad-and-piece-after');final=doc('keyboard-all-final')
assert baseline['layers']==shortcut['layers']==piece['layers']==final['layers']
assert piece==final
assert shortcut['format']=='RetroPaint' and len(shortcut['layers'])==5
cad=shortcut['layers'][3]['cad']['bodies'];assert len(cad)==1
assert cad[0]['name']=='Keyboard cube' and cad[0]['position']==[0,0,10]
assert cad[0]['solid']['size']==[20,20,20] and cad[0]['rotation']==[0,0,0] and cad[0]['scale']==[1,1,1]
# Retain the uniquely timestamped Ctrl+S result observed immediately after the
# native Paint shortcut; use its exact name rather than a future newest-file query.
name='retropaint - 2026-11-05T134250.883.png'
png=Image.open(downloads/name).convert('RGBA');reference=Image.open(downloads/'mouse-audit-mix-transparent-half.png').convert('RGBA')
assert png.tobytes()==reference.tobytes();retain(name)
report={'paint_ctrl_s_png_pixel_exact':True,'paint_ctrl_s_filename':name,'cad_ctrl_s_genuine_project':True,
 'all_five_layer_data_exact':True,'cad_model_recipe_and_transform_exact':True,
 'paint_tabs_modal_and_cancelled_curve_project_exact':True,'piece_and_modal_shortcut_project_exact':True,'sha256':hashes}
(out/'keyboard-preservation-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
