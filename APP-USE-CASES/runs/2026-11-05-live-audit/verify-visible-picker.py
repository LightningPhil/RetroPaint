"""Independent visible-composite sampling and exact no-paint/swatch scope checks."""
from pathlib import Path
from PIL import Image
import base64,copy,hashlib,io,json,math,numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';plan=json.loads((root/'test-results/audit-2026-11-05/fixtures/picker45-plan.json').read_bytes());e=json.loads((out/'picker45-evidence.json').read_bytes());hashes={}
assert plan['recorded_before_native_execution'] and len(e['rows'])==4
fixture=json.loads(Path(plan['fixture']).read_bytes());assert hashlib.sha256(Path(plan['fixture']).read_bytes()).hexdigest()==plan['sha256']
def actual(label,ext='retropaint'):
    name='mouse-audit-picker45-'+label+'.'+ext;b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(label):return json.loads(actual(label))
def pixels(layer):return np.array(Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',',1)[1]))).convert('RGBA'))
yy,xx=np.indices((640,960));distance=np.sqrt((xx-np.clip(xx,450,520))**2+(yy-520)**2);results=[]
for row,wanted in zip(e['rows'],plan['rows']):
    assert row['label']==wanted['label'];label=row['label'];before=doc(label+'-before');sampled=doc(label+'-sampled');marked=doc(label+'-marked')
    assert before==sampled==doc(label+'-undone') and marked==doc(label+'-redone')
    reopened=doc(label+'-reopened');normalized=copy.deepcopy(marked)
    # A brush above an existing editable stamp is retained as a Raster piece.
    # The runtime's inactive wet=False flag is omitted on project import.
    piece=normalized['layers'][3]['objects'][-1];assert piece['wet'] is False;del piece['wet'];assert normalized==reopened
    scoped=copy.deepcopy(fixture);scoped['active']=scoped['layers'][3]['id']
    if row['hide']:next(l for l in scoped['layers'] if l['name']==row['hide'])['visible']=False
    for a,b in zip(scoped['layers'],before['layers']):
        assert np.array_equal(pixels(a),pixels(b));a['image']=b['image']
        assert isinstance(a['paper'],bool) and b['paper'] is None;a['paper']=None
    assert scoped==before
    x,y=row['point'];composite=Image.new('RGBA',(1,1),(0,0,0,0))
    for layer in before['layers']:
        if not layer['visible']:continue
        # Sample points lie outside the Caption Dog object at x650,y80.
        for obj in layer.get('objects',[]):assert x<obj['matrix'][4]-2 or y<obj['matrix'][5]-2
        value=pixels(layer)[y,x].tolist();value[3]=math.floor(value[3]*layer['opacity']+.5)
        composite=Image.alpha_composite(composite,Image.new('RGBA',(1,1),tuple(value)))
    rgb=list(composite.getpixel((0,0))[:3]);hexcolour='#'+''.join(f'{v:02X}' for v in rgb)
    assert row['primary']=='Ink: '+hexcolour and row['secondary']=='Second colour: '+hexcolour
    if label=='hidden-backdrop':assert wanted['RGB']==[255,128,128] and rgb==[255,127,127]
    else:assert rgb==wanted['RGB']
    new_piece=marked['layers'][3]['objects'][-1];assert len(marked['layers'][3]['objects'])==len(before['layers'][3]['objects'])+1
    scoped=copy.deepcopy(before);scoped['layers'][3]['objects'].append(new_piece);assert scoped==marked
    assert new_piece['kind']=='raster' and new_piece['name']=='Brush stroke' and new_piece['matrix']==[1,0,0,1,439,509] and new_piece['width']==92 and new_piece['height']==22 and new_piece['opacity']==1
    assert np.all(pixels(before['layers'][3])[distance<=9]==[255,255,255,255])
    painted=np.zeros((640,960,4),dtype=np.uint8);painted[509:531,439:531]=pixels(new_piece)
    assert np.all(painted[distance<=9]==rgb+[255]) and not painted[distance>=13,3].any()
    p=np.array(Image.open(io.BytesIO(actual(label+'-marked','png'))).convert('RGBA'));q=np.array(Image.open(io.BytesIO(actual(label+'-reopened','png'))).convert('RGBA'));assert np.array_equal(p,q)
    results.append({'case':label,'independent_visible_RGBA':rgb+[255],'sampling_whole_document_unchanged':True,'visible_swatch_only_one_new_Caption_Raster_piece_capsule_exact':True,'whole_Undo_Redo_exact':True,'native_project_reopen_exact_except_inactive_wet_false_omission':True,'native_PNG_reopen_RGBA_exact':True})
report={'status':'Pass','rows':results,'magnifier_evidence':'Four native screenshots show seven-pixel magnifier, central sample square and matching displayed hex before left sampling switches back to marker. Initial no-card rightsampleprobe retained separately.','independent_alpha_oracle_correction':'Predeclaredhidden-backdropRGB255,128,128usedfloat50%intuition. Canonical8bitalphausesround(.5*255)=128, leaving127/255oftheWhitebacking, soindependentPillowovergives255,127,127exact. Originalplanretained; no productfailure or broadened tolerance claimed. Other3declaredRGBexact.','sha256':hashes}
(out/'picker45-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
