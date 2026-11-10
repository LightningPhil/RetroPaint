"""Independent snapshot/storage/failed encoder outputs from native workflows."""
import base64,hashlib,io,json
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse'
downloads=Path.home()/'Downloads';hashes={}
def retain(name):
 data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(s):return json.loads(retain('mouse-audit-'+s+'.retropaint'))
before=doc('storage-blocked-before');after=doc('storage-blocked-after')
captured=doc('snapshot-captured');later=doc('snapshot-later-working');reopened=doc('snapshot-reopened')
assert before!=after and after==captured==reopened and later!=captured
assert later==doc('encoder-retry') and captured==doc('encoder-fixed-retry')
for i in [0,1,3]:assert before['layers'][i]==after['layers'][i]==later['layers'][i]
assert after['layers'][2]['opacity']==later['layers'][2]['opacity']==.5
def flatten(d):
 result=Image.new('RGBA',(d['width'],d['height']))
 for l in d['layers']:
  if not l['visible']:continue
  image=Image.open(io.BytesIO(base64.b64decode(l['image'].split(',')[1]))).convert('RGBA')
  image.putalpha(image.getchannel('A').point(lambda a:round(a*l['opacity'])))
  result=Image.alpha_composite(result,image)
 return result
for name,d in [('encoder-retry',later),('encoder-fixed-retry',captured)]:
 image=Image.open(io.BytesIO(retain('mouse-audit-'+name+'.png'))).convert('RGBA')
 # Canvas opacity applies premultiplied alpha; half-opacity rounding can differ by one.
 expected=flatten(d);assert image.size==expected.size
 errors=[]
 for index,(a,b) in enumerate(zip(image.get_flattened_data(),expected.get_flattened_data())):
  # The unchanged editable caption stamp is drawn from its glyph definition,
  # independently of the raster backing. Exclude its known transformed box.
  x,y=index%image.width,index//image.width
  if 649<=x<=734 and 78<=y<=164:continue
  errors.append(abs(a[3]-b[3]))
  errors.extend(abs(a[c]*a[3]/255-b[c]*b[3]/255) for c in range(3))
 assert max(errors)<=1.01
assert len(list(downloads.glob('mouse-audit-snapshot-captured*.retropaint')))==1
timeout_before=doc('timeout-before');timeout_after=doc('timeout-after')
timeout_before['layers'][2]['image']=timeout_after['layers'][2]['image']
assert timeout_before==timeout_after
cpu_before=doc('cpu-source');assert cpu_before==doc('cpu-after-missing-model')
report={'storage_denial_drawing_changes_only_working_layer':True,
 'captured_save_whole_document_exact_to_before_later_edit':True,
 'native_reopened_snapshot_exact':True,'later_working_edit_retained':True,
 'rapid_disabled_save_clicks_produced_one_file':True,
 'old_and_corrected_error_retries_decode_and_raster_regions_match_within_canvas_rounding':True,
 'unchanged_editable_stamp_box_excluded_from_raster_composition_oracle':[649,78,734,164],
 'real_45_second_timeout_preserved_entire_document_except_regenerated_cad_preview':True,
 'missing_model_download_preserved_whole_document':True,'sha256':hashes}
(out/'fault-file-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
