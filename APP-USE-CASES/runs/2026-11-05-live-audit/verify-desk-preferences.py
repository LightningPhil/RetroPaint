"""Decode real theme exports and check persistence/failure workflows."""
import base64, hashlib, io, json
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def file(stage,extension):
    name='mouse-audit-desk-'+stage+'.'+extension;data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(stage):return json.loads(file(stage,'retropaint'))
before=doc('before');assert (before['width'],before['height'])==(960,640) and len(before['layers'])==1
layer=before['layers'][0];source=Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',',1)[1]))).convert('RGBA')
expected=Image.alpha_composite(Image.new('RGBA',source.size,'white'),source)
for theme in ['before','mint','lavender','sand','night','denied']:
    exported=Image.open(io.BytesIO(file(theme,'png'))).convert('RGBA');assert exported.size==(960,640)
    assert exported.tobytes()==expected.tobytes(),theme+' exported art changed'
for theme in ['mint','lavender','sand','night','restored','reopened']:assert doc(theme)==before,theme+' project changed'
evidence=json.loads((out/'desk-evidence.json').read_bytes());assert len(evidence)==4
for e in evidence:assert e['selected']==e['reloaded']==e['value'] and e['pressed']=='true'
for mode in ['unknown','denied']:
    assert doc(mode+'-before')==doc(mode+'-chosen')==doc(mode+'-undone')==before
    changed=doc(mode+'-stroke');assert changed==doc(mode+'-redone')
    assert changed!=before
    for key in layer:
        if key!='image':assert layer[key]==changed['layers'][0][key]
    image=Image.open(io.BytesIO(base64.b64decode(changed['layers'][0]['image'].split(',',1)[1]))).convert('RGBA')
    assert image.getpixel((550,549))==(26,26,26,255),'Drawing blocked by '+mode+' preference'
    # The independently known new black line is confined to this lower strip.
    assert image.crop((0,0,960,530)).tobytes()==source.crop((0,0,960,530)).tobytes()
    assert image.crop((0,570,960,640)).tobytes()==source.crop((0,570,960,640)).tobytes()
faults=json.loads((out/'preference-fault-evidence.json').read_bytes());assert {e['mode'] for e in faults}=={'unknown','denied'}
for e in faults:assert e['initialDesk']=='mint' and e['chosenDesk']=='lavender'
assert next(e for e in faults if e['mode']=='denied')['reloadedDesk']=='mint'
rows=[json.loads(line) for line in (out.parent/'fault-controls/requests.jsonl').read_text(encoding='utf-8').splitlines()]
events=[r['event'] for r in rows if r.get('event')]
assert any(e['type']=='preference unknown' and e['detail']=='retropaint-desk' for e in events)
for key in ['retropaint-desk','retropaint-reduced-motion','retropaint-sound']:
    assert any(e['type']=='preference read denied' and e['detail']==key for e in events),key
assert any(e['type']=='preference write denied' and e['detail']=='retropaint-desk' for e in events)
report={'status':'Pass','all_four_themes_selected_and_persisted_across_real_reload':True,'six_actual_exported_pngs_match_independent_white_composition_pixel_for_pixel':True,'whole_projects_and_native_reopen_exact':True,'unknown_and_denied_preferences_fall_back_to_mint':True,'unpersistable_lilac_works_for_current_visit':True,'real_black_mouse_strokes_and_independent_undo_redo_work_after_both_faults':True,'sha256':hashes}
(out/'desk-preferences-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
