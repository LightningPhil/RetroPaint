from pathlib import Path
import json
from PIL import Image
from datetime import datetime,timezone

root=Path(__file__).resolve().parent
folder=root/'evidence'
read=lambda name:json.loads((folder/name).read_text(encoding='utf-8'))
inventory=read('START-002-tool-inventory.json')
assert len(inventory)==12 and all(row['name'] and row['graphic'] for row in inventory)
rows=read('START-002-controls.json')
expected={row['name'] for row in inventory}
assert {row['name'] for row in rows}==expected
latest={row['name']:row for row in rows}
for row in rows:
    assert row['name'] in row['active'] and not row['redoDisabled']
    if row['name']!='Symmetry':assert row['workspace']==row['name']
    assert row['view']==rows[0]['view'],row['name']+' moved the picture'
for name,choice in [('Brushes','Biro'),('Shapes','Circle'),('Spray','Confetti'),('Eraser','Invert'),('Stamps','Stamp 🐸'),('Symmetry','4-way'),('Spiro','Square'),('Select','Lasso')]:assert choice in latest[name]['pressed'],(name,choice)
assert next(v['value'] for v in latest['Text']['fields'] if v['id']=='textFont')=='Georgia'
assert next(v['value'] for v in latest['Spiro']['fields'] if v['id']=='innerTeeth')=='54'
before=read('START-002-before-navigation.retropaint')
assert before==read('START-002-after-navigation.retropaint')
assert (before['width'],before['height'])==(960,640) and before['drawingMode']=='raster'
assert len(before['layers'])==1 and before['layers'][0]['paper']=='#ffffff' and not before['layers'][0].get('photo')
assert before['crop']=={'x':0,'y':0,'width':1,'height':1}
blank=Image.open(folder/'START-002-before-navigation.png').convert('RGBA')
after=Image.open(folder/'START-002-after-navigation.png').convert('RGBA')
assert blank.getextrema()==((255,255),)*4 and blank.tobytes()==after.tobytes()
reference=Image.open(folder/'START-002-redo-reference.png').convert('RGBA')
redo=Image.open(folder/'START-002-after-redo.png').convert('RGBA')
assert reference.tobytes()==redo.tobytes() and reference.getpixel((200,100))[2]>200
phones=[]
for width,height in [(320,568),(390,844),(844,390)]:
    prefix=f'START-002-phone{width}'
    tool_inventory=read(prefix+'-inventory.json')
    assert all(any((r['name'] or r['text'])==name and r['graphic'] for r in tool_inventory) for name in expected)
    phone_rows=read(prefix+'-controls.json')
    assert len(phone_rows)==12 and {r['name'] for r in phone_rows}==expected
    choices={r['name']:r for r in phone_rows}
    for row in phone_rows:
        assert row['name'] in row['active'] and not row['redoDisabled']
        if row['name']!='Symmetry':assert row['workspace']==row['name']
        assert row['view']==phone_rows[0]['view']
    for name,choice in [('Brushes','Biro'),('Shapes','Circle'),('Spray','Confetti'),('Select','Lasso'),('Eraser','Invert'),('Stamps','Stamp 🐸'),('Symmetry','4-way')]:assert choice in choices[name]['pressed']
    assert choices['Smudge']['size']=='23'
    assert choices['Bucket']['inkPreview']=='background: rgb(253, 216, 53);'
    assert choices['Pick colour']['inkPreview']=='background: rgb(255, 255, 255);'
    assert next(v['value'] for v in choices['Text']['fields'] if v['id']=='textFont')=='Georgia'
    spiro=read(prefix+'-spiro-retained.json')
    assert 'Square' in spiro['pressed'] and next(v['value'] for v in spiro['fields'] if v['id']=='innerTeeth')=='54'
    # Independent fresh sessions allocate Paper ID 1; the desktop new-picture
    # session allocated ID 2. Require each complete saved document to preserve
    # its own identity, plus the same declared PLAY preconditions.
    phone_before=read(prefix+'-before-navigation.retropaint')
    assert phone_before==read(prefix+'-after-navigation.retropaint')
    assert (phone_before['width'],phone_before['height'])==(960,640) and phone_before['drawingMode']=='raster'
    assert len(phone_before['layers'])==1 and phone_before['layers'][0]['paper']=='#ffffff'
    assert phone_before['active']==phone_before['layers'][0]['id'] and phone_before['crop']==before['crop']
    first=Image.open(folder/(prefix+'-before-navigation.png')).convert('RGBA')
    last=Image.open(folder/(prefix+'-after-navigation.png')).convert('RGBA')
    assert first.tobytes()==last.tobytes()==blank.tobytes()
    original=Image.open(folder/(prefix+'-redo-reference.png')).convert('RGBA')
    restored=Image.open(folder/(prefix+'-after-redo.png')).convert('RGBA')
    assert original.tobytes()==restored.tobytes() and original.getpixel((200,100))==(30,136,229,255)
    phones.append(dict(width=width,height=height,tools=12,project_identity=True,pixels_exact=True,redo_exact=True))
result=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,illustrated_named_tools=12,tool_settings_retained_on_reopen=True,non_colour_workspace_names=True,all_paper_rectangles_exact=True,full_saved_project_identity=True,white_paper_pixels_exact=True,redo_branch_preserved_and_restored_exactly=True,phones=phones,scope='Real desktop CUA controls at 1280x720 and Chrome frames at 320x568,390x844,844x390. Mouse input; physical touch and pen are not certified by this case.')
(folder/'START-002-independent-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
