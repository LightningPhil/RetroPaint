"""Independent saved-profile, Undo/Redo and STL oracles for native CAD forms."""
from collections import Counter
import copy,hashlib,json,struct
from pathlib import Path
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse'
downloads=Path.home()/'Downloads';hashes={}
def retain(name):
    data=(downloads/name).read_bytes();(out/name).write_bytes(data)
    hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(name):return json.loads(retain('mouse-audit-'+name+'.retropaint'))
def bodies(p):return next(l['cad']['bodies'] for l in p['layers'] if l['name']=='3D 1')
def named(p,name):return next(b for b in bodies(p) if b['name']==name)
def models(p):return {l['id']:l['cad']['bodies'] for l in p['layers'] if l.get('cad')}
def dims(points):return [round(max(p[j] for p in points)-min(p[j] for p in points),9) for j in range(2)]
def unchanged_except(a,b,name):
    assert [x for x in bodies(a) if x['name']!=name]==[x for x in bodies(b) if x['name']!=name]
def stl(name,expected_volume,expected_size):
    data=retain('mouse-audit-'+name+'-3d-mm.stl');count=struct.unpack_from('<I',data,80)[0]
    assert len(data)==84+50*count
    edges=Counter();directions=Counter();points=[];volume=0
    for i in range(count):
        q=struct.unpack_from('<12f',data,84+i*50);a,b,c=[tuple(q[j:j+3]) for j in [3,6,9]]
        points.extend([a,b,c]);volume+=sum(a[j]*(b[(j+1)%3]*c[(j+2)%3]-b[(j+2)%3]*c[(j+1)%3]) for j in range(3))/6
        for start,end in [(a,b),(b,c),(c,a)]:
            edge=tuple(sorted([start,end]));edges[edge]+=1;directions[edge]+=1 if start<end else -1
    assert all(n==2 for n in edges.values()) and not any(directions.values())
    size=[max(p[j] for p in points)-min(p[j] for p in points) for j in range(3)]
    assert all(abs(a-b)<.002 for a,b in zip(size,expected_size)) and abs(volume-expected_volume)<.05
    return {'name':name,'triangles':count,'closed_outward':True,'size_mm':size,'volume_mm3':volume,'analytic_volume_mm3':expected_volume}
baseline=doc('copied-loft-baseline');source_changed=doc('copied-loft-source-edited')
loft_name='Independent copied loft'
assert dims(named(baseline,'XY block')['solid']['points'])==[20,10]
assert dims(named(source_changed,'XY block')['solid']['points'])==[22,10]
assert named(baseline,loft_name)==named(source_changed,loft_name)
unchanged_except(baseline,source_changed,'XY block')
profiles=named(baseline,loft_name)['solid']['profiles']
assert profiles[0]['points']==named(baseline,'XY block')['solid']['points']
assert dims(profiles[0]['points'])==[20,10] and dims(profiles[1]['points'])==[25,10]
assert profiles[1]['plane']['origin']==[5,0,30]
assert retain('mouse-audit-copied-loft-baseline-3d-mm.stl')==retain('mouse-audit-copied-loft-source-edited-3d-mm.stl')
current=doc('copied-current-loft');drawn=named(current,'Current drawing copied loft')['solid']['profiles']
assert dims(drawn[1]['points'])==[33,11] and drawn[1]['plane']['origin']==[5,0,30]
assert bodies(current)[:13]==bodies(source_changed)
loft=doc('loft-constrained35');loft_undo=doc('loft-constrained35-undone');loft_redo=doc('loft-constrained35-redone')
assert models(loft_undo)==models(current) and models(loft_redo)==models(loft)
unchanged_except(current,loft,loft_name)
before=named(current,loft_name)['solid']['profiles'];after=named(loft,loft_name)['solid']['profiles']
assert before[0]==after[0] and dims(after[1]['points'])==[35,10]
constraints=after[1]['constraints'];assert len(constraints)==2
assert [(c['kind'],c.get('value'),c['edge']) for c in constraints]==[('length',35,0),('horizontal',None,0)]
assert after[1]['plane']==before[1]['plane']
sweep=doc('sweep-constrained12');sweep_undo=doc('sweep-constrained12-undone');sweep_redo=doc('sweep-constrained12-redone')
assert models(sweep_undo)==models(loft_redo) and models(sweep_redo)==models(sweep)
unchanged_except(loft_redo,sweep,'Rectangular sweep')
s=named(sweep,'Rectangular sweep')['solid'];old=named(loft_redo,'Rectangular sweep')['solid']
assert dims(s['profile']['points'])==[12,4] and s['path']==old['path']
assert [(c['kind'],c.get('value'),c['edge']) for c in s['profile']['constraints']]==[('length',12,0),('horizontal',None,0)]
reopened=doc('constrained-forms-reopened');assert models(reopened)==models(sweep_redo)
results=[stl('copied-loft-baseline',30*10*(20+25)/2,[27.5,10,30]),
         stl('copied-current-loft',30*(20*10+(20*1+13*10)/2+13*1/3),[33,11,30]),
         stl('loft-constrained35',30*10*(20+35)/2,[35,10,30]),
         stl('sweep-constrained12',12*4*(20+30),[36,4,26])]
report={'saved_source_copy_stays_independent_after_original_width20_to22':True,
        'copied_loft_stl_byte_exact_after_source_edit':True,
        'current_drawing_copy_retains33x11_and_own_placement':True,
        'loft_and_sweep_dimensions_relations_undo_redo_models_exact':True,
        'conflicting_loft_dimension_not_retained_and_other_profile_exact':True,
        'native_fresh_reopen_all_model_definitions_exact':True,'stls':results,'sha256':hashes}
(out/'copied-constrained-forms-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
