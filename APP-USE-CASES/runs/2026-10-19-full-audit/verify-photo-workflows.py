from pathlib import Path
import base64,io,json
from datetime import datetime,timezone
from PIL import Image

root=Path(__file__).resolve().parent
folder=root/'evidence'
read=lambda name:json.loads((folder/name).read_text(encoding='utf-8'))
image=lambda name:Image.open(folder/name).convert('RGBA')
before=read('PHOTO-004-saved-before.retropaint')
assert (before['width'],before['height'])==(3896,2586) and len(before['layers'])==2
photo,paint=before['layers']
assert before['active']==photo['id']
source=read('PHOTO-source-Laukka.retropaint')
assert photo['image']==source['layers'][0]['image']
assert photo['photo']['settings']['exposure']==1 and photo['photo']['settings']['brightness']==7
neighbour=Image.open(io.BytesIO(base64.b64decode(paint['image'].split(',',1)[1]))).convert('RGBA')
assert neighbour.getpixel((1500,1000))==(67,160,71,255),neighbour.getpixel((1500,1000))
assert neighbour.getpixel((100,100))==(0,0,0,0)
reference=image('PHOTO-004-saved-before.png')
rows=[]
for branch in ['cancel','close','escape']:
    after=read('PHOTO-004-'+branch+'-after.retropaint')
    assert before==after,branch+' changed saved data'
    rendered=image('PHOTO-004-'+branch+'-after.png')
    assert rendered.size==reference.size and rendered.tobytes()==reference.tobytes(),branch+' changed rendered pixels'
    draft=read('PHOTO-004-'+branch+'-inflight.json')
    assert draft['status']=='Updating preview…',branch+' was not exercised during an outstanding preview'
    if branch!='cancel':
        values=draft['restoredBefore'+branch.title()]
        assert {v['name']:v['value'] for v in values}=={'Exposure':'1','Brightness':'7','Contrast':'0'}
    rows.append(dict(branch=branch,outstanding_preview_observed=True,saved_project_exact=True,full_size_rgba_exact=True,original_and_neighbour_preserved=True))
assert before==read('PHOTO-004-reopened.retropaint')
reopened=image('PHOTO-004-reopened.png')
assert reopened.size==reference.size and reopened.tobytes()==reference.tobytes()
result=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,source='User-supplied Laukka sunset.jpg, recorded in import-manifest.json',dimensions=reference.size,source_pixels_preserved=True,distinct_neighbour_green_rgba=[67,160,71,255],rows=rows,actual_file_save_and_fresh_tab_reopen_exact=True)
(folder/'PHOTO-004-independent-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
navigation=read('PHOTO-002-before-navigation.retropaint')
assert navigation==read('PHOTO-002-after-navigation.retropaint')==read('PHOTO-002-reopened.retropaint')
reference=image('PHOTO-002-before-navigation.png')
for name in ['PHOTO-002-after-navigation.png','PHOTO-002-reopened.png']:
    output=image(name);assert output.size==reference.size and output.tobytes()==reference.tobytes()
navigation_report=read('PHOTO-002-independent-verification.json')
short_rows=read('PHOTO-002-short-resumed-groups.json')
desktop_rows=read('PHOTO-002-desktop-groups.json')
assert len(short_rows)==15 and {r['value'] for r in short_rows}=={r['value'] for r in desktop_rows}
for row in short_rows:
    assert row['group']==row['value'] and (row['width'],row['height'])==(844,390) and not row['tabsVisible']
    assert row['controls'] and all(c['name'] and c['rect']['left']>=0 and c['rect']['top']>=0 and c['rect']['right']<=844 and c['rect']['bottom']<=390 for c in row['controls'])
assert {v['name']:v['value'] for v in read('PHOTO-002-short-resumed-values.json')}=={'Exposure':'1','Brightness':'7','Contrast':'0'}
for suffix in ['before','after','reopened']:
    assert read('PHOTO-002-short-resumed-'+suffix+'.retropaint')==navigation
    output=image('PHOTO-002-short-resumed-'+suffix+'.png')
    assert output.size==reference.size and output.tobytes()==reference.tobytes()
portrait_rows=read('PHOTO-002-portrait-groups.json')
assert len(portrait_rows)==15 and {r['value'] for r in portrait_rows}=={r['value'] for r in desktop_rows}
for row in portrait_rows:
    assert row['group']==row['value'] and (row['width'],row['height'])==(390,844) and row['tabsVisible']
    assert row['controls'] and all(c['name'] and c['rect']['left']>=0 and c['rect']['top']>=0 and c['rect']['right']<=390 and c['rect']['bottom']<=844 for c in row['controls'])
assert {v['name']:v['value'] for v in read('PHOTO-002-portrait-values.json')}=={'Exposure':'1','Brightness':'7','Contrast':'0'}
for suffix in ['before','after','reopened']:
    assert read('PHOTO-002-portrait-'+suffix+'.retropaint')==navigation
    output=image('PHOTO-002-portrait-'+suffix+'.png')
    assert output.size==reference.size and output.tobytes()==reference.tobytes()
navigation_report.update(at=datetime.now(timezone.utc).isoformat(),actual_file_save_and_fresh_tab_reopen_exact=True,short_screen=dict(width=844,height=390,combined_selector_groups=15,all_controls_named_and_inside_viewport=True,exposure_and_brightness_retained=True,complete_project_identity=True,full_size_rgba_exact=True,actual_downloaded_project_fresh_tab_reopen_exact=True),portrait_screen=dict(width=390,height=844,category_groups=15,all_groups_verified=True,all_controls_named_and_inside_viewport=True,complete_project_identity=True,full_size_rgba_exact=True,actual_downloaded_project_fresh_tab_reopen_exact=True),remaining_variants=[])
(folder/'PHOTO-002-independent-verification.json').write_text(json.dumps(navigation_report,indent=2)+'\n',encoding='utf-8')
print('PHOTO-002 actual saved single-sheet project and full-size image reopen exactly')
