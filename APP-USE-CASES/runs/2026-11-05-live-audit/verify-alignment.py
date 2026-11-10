"""Fifteen native world-bound alignments, exact source isolation and locked atomicity."""
from pathlib import Path
import copy,hashlib,itertools,json
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={};results=[]
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
base=retain('mouse-audit-alignment176-normal.retropaint');index=next(i for i,l in enumerate(base['layers']) if 'cad'in l)
def canonical(d):
 d=copy.deepcopy(d);d.pop('active');d['layers'][index].pop('image');return d
local=np.vstack([np.array([[-10,-5,-5],[10,-5,-5],[-10,-5,25],[-10,5,-5],[10,5,-5],[-10,5,25]]),np.array(list(itertools.product([-2,2],repeat=3)))+[15,8,22]])
x,y,z=np.deg2rad([20,30,40]);rx=np.array([[1,0,0],[0,np.cos(x),-np.sin(x)],[0,np.sin(x),np.cos(x)]]);ry=np.array([[np.cos(y),0,np.sin(y)],[0,1,0],[-np.sin(y),0,np.cos(y)]]);rz=np.array([[np.cos(z),-np.sin(z),0],[np.sin(z),np.cos(z),0],[0,0,1]])
world=(local*[1.5,.75,2])@(rz@ry@rx).T+[-13,8,-7];low=world.min(axis=0);high=world.max(axis=0);ref_low=np.array([95,40,15]);ref_high=np.array([105,60,45]);ui=json.loads((out/'alignment176-ui.json').read_text(encoding='utf-8'))
assert len(ui['samples'])==15
for s in ui['samples']:
 axis=s['axis'];mode=s['mode'];gap=s['gap'];delta={'center':(ref_low[axis]+ref_high[axis]-low[axis]-high[axis])/2,'min':ref_low[axis]-low[axis],'max':ref_high[axis]-high[axis],'after':ref_high[axis]+gap-low[axis],'before':ref_low[axis]-gap-high[axis]}[mode]
 doc=retain(f"mouse-audit-alignment176-normal ({s['index']}).retropaint");expected=copy.deepcopy(base);wanted=expected['layers'][index]['cad']['bodies'][0]['position'];wanted[axis]+=delta;actual=doc['layers'][index]['cad']['bodies'][0]['position'];assert np.max(np.abs(np.array(actual)-wanted))<.000002
 expected['layers'][index]['cad']['bodies'][0]['position']=actual;assert canonical(doc)==canonical(expected);results.append(dict(axis=axis,mode=mode,gap_mm=gap,position_mm=actual))
assert canonical(retain('mouse-audit-alignment176-normal (16).retropaint'))==canonical(base)
before=retain('mouse-audit-alignment176.retropaint');bad=retain('mouse-audit-alignment176 (1).retropaint');a=before['layers'][index]['cad']['bodies'];b=bad['layers'][index]['cad']['bodies'];assert a[0]['position']!=b[0]['position'] and a[1:]==b[1:]
fixed=retain('mouse-audit-alignment176-fixed.retropaint');after=retain('mouse-audit-alignment176-fixed (1).retropaint');assert canonical(fixed)==canonical(after) and 'Unlock' in ui['fixedLockedAttempt']
report=dict(status='Pass',fifteen_axis_mode_combinations=results,positive_gap_and_negative_overlap_consistent=True,target_and_other_source_exact=True,undo_source_exact=True,locked_group_atomic_after_fix=True,native_before_partial_move_confirmed=True,excluded=ui['excluded'],hashes=hashes)
(out/'alignment176-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['hashes','fifteen_axis_mode_combinations']},indent=2))
