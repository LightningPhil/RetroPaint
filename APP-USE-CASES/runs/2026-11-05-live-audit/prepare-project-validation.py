"""Combine real editing definitions; mutate one validation category per copy."""
from pathlib import Path
import copy,hashlib,json
root=Path(__file__).resolve().parents[3];fixtures=root/'test-results/audit-2026-11-05/fixtures';folder=fixtures/'project-validation44';folder.mkdir(exist_ok=True);downloads=Path.home()/'Downloads'
photo=json.loads((downloads/'mouse-audit-save43-photo-before.retropaint').read_bytes());vector=json.loads((downloads/'mouse-audit-edit-vector-overhang38-before.retropaint').read_bytes());live=json.loads((fixtures/'mix-live-clear.retropaint').read_bytes());cad=json.loads((fixtures/'cadmix-trace-guide.retropaint').read_bytes())
base=copy.deepcopy(photo);base['drawingMode']='vector';base['active']=103;base['layers'][1]['live']=copy.deepcopy(live['layers'][1]['live']);base['layers'][2]['objects']=copy.deepcopy(vector['layers'][0]['objects']);manifest=[]
def write(label,d,change):
 path=folder/(label+'.retropaint');b=json.dumps(d,separators=(',',':'),ensure_ascii=False).encode();path.write_bytes(b);manifest.append({'label':label,'file':str(path),'sha256':hashlib.sha256(b).hexdigest(),'mutation':change});return path
valid=write('valid-mixed',base,'Validcontrol: realnativeMIXPhoto+1EVrecipe,realnativeWater/Conveyorbackdroplive,realnative9pieceVectorobjects,original4layers/CaptionDog. No invented migration producer.');manifest.pop()
def change(label,path,value):
 d=copy.deepcopy(base);p=d
 for key in path[:-1]:p=p[key]
 p[path[-1]]=value;write(label,d,{'path':path,'value':value})
change('malformed-layer-image',['layers',3,'image'],'data:image/png;base64,AAAA')
small=json.loads((downloads/'mouse-audit-import43-png-before.retropaint').read_bytes());change('layer-size-mismatch',['layers',3,'image'],small['layers'][0]['image'])
change('duplicate-layer-id',['layers',3,'id'],base['layers'][0]['id']);change('duplicate-object-id',['layers',2,'objects',8,'id'],base['layers'][2]['objects'][0]['id']);change('missing-active',['active'],999999);change('fractional-layer-id',['layers',3,'id'],104.5);change('numeric-string',['layers',3,'opacity'],'NaN');change('singular-object',['layers',3,'objects',0,'matrix'],[0,0,0,1,650,80]);change('crop-outside',['crop'],{'x':.8,'y':0,'width':.5,'height':1})
change('photo-exposure-type',['layers',1,'photo','settings','exposure'],'bright');change('photo-curve-order',['layers',1,'photo','settings','curves','rgb'],[{'x':0,'y':0},{'x':.8,'y':.8},{'x':.2,'y':.2},{'x':1,'y':1}]);change('photo-look-unknown',['layers',1,'photo','look'],'unknown-look')
change('ink-kind',['layers',1,'live','strokes',0,'spec','kind'],'unknown-ink');change('ink-mode',['layers',1,'live','strokes',0,'spec','mode'],'unknown-mode');change('brush-unknown',['layers',1,'live','strokes',0,'applicator'],'unknown-brush');change('width-limit',['width'],4097);change('height-limit',['height'],4097)
d=copy.deepcopy(base);d['layers']=[copy.deepcopy(base['layers'][0]) for _ in range(17)]
for i,l in enumerate(d['layers']):l['id']=i+1
d['active']=1;write('layers-seventeen',d,'Replace layerarray by17uniqueIDcopies, target1; exceeds16layerlimit.')
d=json.loads((fixtures/'limit-4096-one-sheet.retropaint').read_bytes());d['layers']=[copy.deepcopy(d['layers'][0]) for _ in range(4)]
for i,l in enumerate(d['layers']):l['id']=i+1
d['active']=1;write('pixels-over-budget',d,'Four4096squarelayers=67,108,864storedpixels>64,000,000. Rejected before image decode/allocation.')
change('future-version',['version'],999)
for label,mutate in [('cad-zero-scale',lambda body:body.update(scale=[0,1,1])),('cad-kind-unknown',lambda body:body['solid'].update(kind='unknown-construction'))]:
 d=copy.deepcopy(cad);mutate(d['layers'][2]['cad']['bodies'][0]);write(label,d,label+' in realnativeSHELLCADMIXbase')
d=copy.deepcopy(cad);d['layers'][2]['cad']['bodies'].append(copy.deepcopy(d['layers'][2]['cad']['bodies'][0]));write('cad-duplicate-id',d,'Duplicate firstCADbodyID')
d=copy.deepcopy(cad);view=d['layers'][2]['cad']['view'];view['position']=copy.deepcopy(view['target']);write('cad-camera-singular',d,'Set savedcamera position=target; direction haszero length')
d=copy.deepcopy(cad);d['layers'][2]['cad']['bodies'][0]['solid']={'kind':'extrude','points':[[-5,-5],[5,-5],[5,5],[-5,5]],'plane':{'origin':[0,0,0],'u':[1,0,0],'v':[1,0,0],'normal':[0,0,1]},'height':20,'taper':1,'twist':0};write('cad-workplane-parallel',d,'10mmrectangleextrude20mm otherwisevalid; workplaneu=v makes dot1, invalidbasis')
for label,b,desc in [('truncated',valid.read_bytes()[:300],'Truncate validmixedJSON at300bytes'),('renamed-png',(fixtures/'import-formats/source.png').read_bytes(),'ActualPNGbyteswithprojectextension'),('nan-json',valid.read_bytes().replace(b'"opacity":1',b'"opacity":NaN',1),'BareNaNinvalidJSONencoding')]:
 path=folder/(label+'.retropaint');path.write_bytes(b);manifest.append({'label':label,'file':str(path),'sha256':hashlib.sha256(b).hexdigest(),'mutation':desc})
report={'valid':{'file':str(valid),'sha256':hashlib.sha256(valid.read_bytes()).hexdigest()},'producers':['Downloads/mouse-audit-save43-photo-before.retropaint','Downloads/mouse-audit-edit-vector-overhang38-before.retropaint','fixtures/mix-live-clear.retropaint','fixtures/cadmix-trace-guide.retropaint'],'invalid':manifest,'plan':'EveryinvalidinputthroughnativeOpenproject; messageandentirebefore/afterprojectrecorded. Immediatelyopenvalidmixedcontrol,saveit,Undoopeningbacktounrelatedbaselineandcompareallsourceagain. Currentversion999isdeliberateinvalidinput, notalegacyfixture. Controlledliveframe12345msbefore/afterfreshsessionreopen; alternate23456msprovesstilllive.'};(folder/'manifest.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps({'invalid_cases':len(manifest),'valid_sha256':report['valid']['sha256']},indent=2))
