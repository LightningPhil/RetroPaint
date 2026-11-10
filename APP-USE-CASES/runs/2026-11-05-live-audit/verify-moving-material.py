"""Actual mouse transforms compared at one explicit main-window animation time."""
import copy,hashlib,io,json,math
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse'
downloads=Path.home()/'Downloads';hashes={}
def retain(name):
 data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(s):return json.loads(retain('mouse-audit-vector-water-'+s+'.retropaint'))
def png(s):return Image.open(io.BytesIO(retain('mouse-audit-vector-water-'+s+'.png'))).convert('RGBA')
before=doc('fixed-before');rotated=doc('fixed-rotated');scaled=doc('fixed-scaled');alpha_doc=doc('alpha-clear')
a,b,c=png('fixed-before'),png('fixed-rotated'),png('fixed-scaled');running=png('running');alpha=png('alpha-clear')
original=before['layers'][0]['objects'][1];m=original['matrix'];assert original['fill']['color']=='tex-water'
for d,expected in [(rotated,[0,m[0],-m[3],0,764,350]),(scaled,[0,m[0]*2,-m[3]*2,0,828,350])]:
 layer=d['layers'][0];assert layer['objects'][0]==before['layers'][0]['objects'][0]
 item=layer['objects'][1];assert all(abs(v-w)<1e-12 for v,w in zip(item['matrix'],expected))
 reference=copy.deepcopy(original);reference['matrix']=item['matrix'];assert reference==item
base=a.copy();patch=a.crop((100,100,228,164));base.paste((255,255,255,255),(100,100,228,164))
expected=base.copy();expected.paste(patch.transpose(Image.Transpose.ROTATE_270),(700,350))
assert expected.tobytes()==b.tobytes()
# Outside the independently transformed rectangle nothing changes at fixed time.
outside=c.copy();outside.paste((255,255,255,255),(700,350,828,606));assert outside.tobytes()==base.tobytes()
tile=c.crop((700,350,828,606))
def repeat_error(n):
 return ImageStat.Stat(ImageChops.difference(tile.crop((4,4,124,252-n)),tile.crop((4,4+n,124,252)))).mean[0]
period=64*scaled['layers'][0]['objects'][1]['matrix'][1]
assert abs(period-119.16355208333336)<1e-9 and repeat_error(119)<1.1 and repeat_error(60)>7
assert alpha.getchannel('A').getbbox()==(700,350,828,606)
assert alpha.crop((700,350,828,606)).tobytes()==tile.tobytes()
assert alpha.getchannel('A').histogram()[255]==128*256 and alpha.getchannel('A').histogram()[0]==960*640-128*256
assert a.crop((350,230,650,330)).tobytes()==c.crop((350,230,650,330)).tobytes()
assert running.crop((350,230,650,330)).tobytes()!=c.crop((350,230,650,330)).tobytes()
paper=copy.deepcopy(scaled['layers'][0]);paper['visible']=False
assert paper==alpha_doc['layers'][0]
assert len(alpha_doc['layers'][1]['objects'])==1
report={'controlled_main_window_time_ms':12345,'independent_quarter_turn_full_png_pixel_exact':True,
 'scale_matrix_exact_and_outside_transformed_bounds_unchanged':True,
 'material_period_after_double_scale_px':period,'period119_red_mae':repeat_error(119),'wrong_half_period60_red_mae':repeat_error(60),
 'alpha_mask_exact_rect':[700,350,128,256],
 'alpha_fixture_only_replaces_white_raster_backing_with_independent_transparent_png':True,
 'unchanged_other_live_object_at_fixed_time':True,
 'unrelated_live_object_changes_after_clock_resume':True,'all_source_and_ink_definitions_retained':True,'sha256':hashes}
(out/'moving-material-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
