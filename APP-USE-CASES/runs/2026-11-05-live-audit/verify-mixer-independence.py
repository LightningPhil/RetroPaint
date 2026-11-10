"""Actual all-eight-record reopen and mixer resets preserve unrelated controls."""
from pathlib import Path
import copy,hashlib,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def doc(n):
    name=f'mouse-audit-mixer118-{n}.retropaint';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
mixed=doc('mixed');assert doc('reopened')==mixed
ui=json.loads((out/'mixer118-ui.json').read_text());assert ui['before']==ui['reopened'] and len(ui['before'])==8 and len({tuple(x.values()) for x in ui['before']})==8
s=mixed['layers'][0]['photo']['settings'];assert s['mixer']==ui['before'];assert s['temperature']==ui['temperature']!=0 and s['tint']==ui['tint']!=0
assert s['curves']['rgb']==[dict(x=0,y=0),dict(x=.25,y=.18),dict(x=.75,y=.82),dict(x=1,y=1)]
base=json.loads((downloads/'mouse-audit-mixer117-baseline.retropaint').read_text());defaults=json.loads((downloads/'mouse-audit-photo98-full-reset.retropaint').read_text())['layers'][0]['photo']['settings'];settings=copy.deepcopy(defaults);settings.update(temperature=ui['temperature'],tint=ui['tint'],mixer=ui['before']);settings['curves']=s['curves'];expected=copy.deepcopy(base);expected['layers'][0]['photo']=dict(settings=settings,normal=settings,look='custom',lookActive=False);assert expected==mixed
reset=doc('reset');expected=copy.deepcopy(mixed)
for key in ['settings','normal']:expected['layers'][0]['photo'][key]['mixer']=copy.deepcopy(defaults['mixer'])
assert reset==expected
report=dict(status='Pass',eight_distinct_range_records_native_save_reopen_UI_and_project_exact=True,all_records_independent=True,reset_all_ranges_preserves_temperature_tint_RGB_curve_every_source_and_other_document_field=True,sha256=hashes)
(out/'mixer118-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native eight-record independence/reopen and isolated mixer resets')
