"""Native mouse phone crop flows; physical touch is explicitly unverified."""
from pathlib import Path
import copy,hashlib,json
import numpy as np
from PIL import Image
from geometry_oracle import project_source
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={};ui=json.loads((out/'phone146-ui.json').read_text(encoding='utf-8'));assert len(ui)==16
def load(source,width,ext='retropaint'):
    name=f'mouse-audit-phone146-{source}{width}.{ext}';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data) if ext=='retropaint' else np.array(Image.open(out/name).convert('RGBA')).astype(int)
defaults=json.loads((downloads/'mouse-audit-photo98-full-reset.retropaint').read_text())['layers'][0]['photo']['settings'];images={}
for source in ['wide','natural']:
    baseline='mouse-audit-phone145-wide-baseline.retropaint' if source=='wide' else 'mouse-audit-ratio130-landscape-baseline.retropaint';base=json.loads((downloads/baseline).read_text());raw=project_source(base);h,w,_=raw.shape
    for width in [320,390]:
        rows=[r for r in ui if r['sourceName']==source and r['width']==width];assert [r['stage'] for r in rows]==['new','move','resize-nw','resize-se'];assert all(r['hit']=='photoMiniCanvas' and r['map']['touchAction']=='none' and r['input']=='mouse' and r['scrollBefore']==r['scrollAfter']==dict(x=0,y=0) for r in rows)
        for r in rows:
            actual=r['crop'];expected=r['expected'];assert all(abs(actual[k]-expected[i]*([w,h,w,h][i]))<=1 for i,k in enumerate(['x','y','width','height']))
        assert rows[0]['crop']['width']==rows[1]['crop']['width'] and rows[0]['crop']['height']==rows[1]['crop']['height']
        d=load(source,width);a=load(source,width,'png');images[source+str(width)]=a;c=d['crop'];norm=[c[k] for k in ['x','y','width','height']];target=[.2,.15,.7,.65] if source=='wide' else [.25,.2,.7,.65];assert np.allclose(np.array(norm)*[w,h,w,h],np.array(target)*[w,h,w,h],atol=.005,rtol=0)
        x,y,cw,ch=[round(v*scale) for v,scale in zip(norm,[w,h,w,h])];assert np.array_equal(a,raw[y:y+ch,x:x+cw]);s=copy.deepcopy(defaults);s['crop']=c;expected=copy.deepcopy(base);expected['crop']=c;expected['layers'][0]['photo']=dict(settings=s,normal=s,look='custom',lookActive=False);assert d==expected
for source in ['wide','natural']:assert np.array_equal(images[source+'320'],images[source+'390'])
report=dict(status='Partial',native_mouse_flow_status='Pass',sixteen_native_draw_move_NW_SE_gestures_on_wide_and_natural_sources=True,both_exact_phone_layouts320x568_390x844=True,double_letterboxing_maps_to_expected_source_pixels=True,move_keeps_size_and_resizes_choose_correct_corner=True,both_source_PNGs_identical_across_phone_widths=True,all_exports_every_RGBA_exact_independent_source_slice=True,source_objects_other_recipe_document_fields_exact=True,mouse_scroll_positions_unchanged_and_touch_action_none=True,physical_touch_gesture_and_browser_scroll_arbitration='Unverified: mouse input only; do not count as physical touch acceptance.',sha256=hashes)
(out/'phone146-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native mouse phone matrix/source/PNG; physical touch remains explicitly Partial')
