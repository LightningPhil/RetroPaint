"""Verify live compact article navigation, async loading and real clipboard data."""
import base64,copy,hashlib,io,json
from collections import Counter
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse'
layouts=json.loads((out/'wiki-compact-level-evidence.json').read_bytes())
assert len(layouts)==660
for width,height in [(320,568),(390,844),(844,390)]:
 rows=[x for x in layouts if (x['width'],x['height'])==(width,height)]
 assert len(rows)==220 and len(set(x['topic'] for x in rows))==110
 assert Counter(x['focus'] for x in rows)=={'cadWiki-beginner':110,'cadWiki-deeper':110}
 for row in rows:
  assert row['scrollWidth']<=row['client']+2
  assert row['articleTop']-1<=row['headingTop']<=row['articleBottom']-10
async_load=json.loads((out/'wiki-async-load-evidence.json').read_bytes())
a,b=async_load['before'],async_load['after'];assert a['count']=='68 of 68 topics' and b['count']=='110 of 110 topics'
for k in ['topic','scroll','focus']:assert a[k]==b[k]
assert a['scroll']>0 and a['focus']=='cadWiki-deeper'
clip=json.loads((out/'wiki-copy-evidence.json').read_bytes())
expected='''// Keep the first shape; subtract every later shape.
difference() {
  cube([30,20,8]); // Stock: width, depth, height in millimetres.
  // Centre the drill in X/Y; start 1 mm below the stock.
  translate([15,10,-1])
    cylinder(h=10, r=4, $fn=48); // Pass through both faces.
}'''
for k in ['expected','success','manualPasted','normalNativePasted']:assert clip[k]==expected
assert clip['denied']['selected']==expected
assert clip['denied']['status']=='Code selected. Press Ctrl/Cmd+C to copy.'
assert clip['draftBefore']==clip['draftAfterReading'] and clip['closeFocus']=='cadScriptHelp'
docs=[];hashes={}
for stage in ['before','after']:
 name='mouse-audit-wiki-r2-'+stage+'.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();docs.append(json.loads(data))
original=copy.deepcopy(docs)
rounding=[]
for a,b in zip(docs[0]['layers'],docs[1]['layers']):
 if not a.get('cad'):continue
 pa,pb=[Image.open(io.BytesIO(base64.b64decode(d.pop('image').split(',')[1]))).convert('RGBA').tobytes() for d in (a,b)]
 differences=[(i,x,y) for i,(x,y) in enumerate(zip(pa,pb)) if x!=y]
 assert len(pa)==len(pb) and all(abs(x-y)<=1 and i%4!=3 for i,x,y in differences)
 count=len(set(i//4 for i,_,_ in differences));assert count<=3;rounding.append(count)
assert docs[0]==docs[1]
result={'all_110_topics_both_levels_at_three_exact_compact_sizes':True,'reading_checks':660,'no_horizontal_article_overflow':True,'delayed_real_mcad_load_preserves_article_focus_and_scroll':True,'exact_commented_source_normal_and_denied_manual_native_paste':True,'wiki_close_restores_help_opener_focus':True,'whole_editable_project_and_paint_unchanged':True,'cad_thumbnail_rounding_pixel_counts':rounding,'sha256':hashes}
(out/'wiki-reading-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
