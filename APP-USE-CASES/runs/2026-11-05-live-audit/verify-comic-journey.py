"""Check actual independent character duplication and targeted comic revision."""
import copy,hashlib,io,json,math
from pathlib import Path
from PIL import Image,ImageChops
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse'
downloads=Path.home()/'Downloads';hashes={}
def retain(name):
    data=(downloads/name).read_bytes();(out/name).write_bytes(data)
    hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(name):return json.loads(retain('mouse-audit-comic-'+name+'.retropaint'))
def png(name):return Image.open(io.BytesIO(retain('mouse-audit-comic-'+name+'.png'))).convert('RGBA')
def canonical(p):
    p=copy.deepcopy(p)
    for l in p['layers']:
        for o in l.get('objects',[]):
            if o.get('wet') is False:o.pop('wet')
            if o['kind']=='raster' and not o.get('live'):o.pop('liveSize',None)
    return p
first=doc('first-character');final=doc('final');reopened=doc('reopened')
assert canonical(final)==canonical(reopened)
assert len(final['layers'])==2 and final['layers'][1]['name']=='Comic panels'
assert final['layers'][0]==first['layers'][0]
objects=final['layers'][1]['objects'];assert len(objects)==7
assert objects[3]==first['layers'][1]['objects'][3]
a,b=copy.deepcopy(objects[3]),copy.deepcopy(objects[4]);assert a['id']!=b['id'] and a['matrix']!=b['matrix']
assert a['kind']==b['kind']=='stamp' and a['width']==b['width']==123
a.pop('id');b.pop('id');a.pop('matrix');matrix=b.pop('matrix');assert a==b
scale=110/123;assert abs(matrix[0]-scale*math.cos(math.pi/12))<1e-8
assert abs(matrix[1]+scale*math.sin(math.pi/12))<1e-8
assert objects[5]['callout'] and objects[6]['callout']
assert all(o['kind']=='text' and o['size']==26 and 'Comic Sans MS' in o['font'] for o in objects[5:])
wrong=doc('wrong-piece');undone=doc('wrong-piece-undone')
assert wrong!=reopened and undone==reopened
revised=doc('revised');assert revised['layers'][0]==reopened['layers'][0]
assert revised['layers'][1]['objects'][:6]==reopened['layers'][1]['objects'][:6]
old=reopened['layers'][1]['objects'][6];new=revised['layers'][1]['objects'][6]
for field in ['id','matrix','kind','font','size','align','color','paper']:
    assert old[field]==new[field],field
assert {k:v for k,v in old['callout'].items() if k!='text'}=={k:v for k,v in new['callout'].items() if k!='text'}
assert [x['text'] for x in new['lines']]==['Treats packed.',"Let's go!"]
a,b,c=png('final'),png('reopened'),png('revised')
assert a.size==b.size==c.size==(960,640) and a.tobytes()==b.tobytes()
assert b.crop((77,77,434,564)).tobytes()==c.crop((77,77,434,564)).tobytes()
difference=ImageChops.difference(b,c);box=difference.convert('RGB').getbbox()
assert box and box[0]>=560 and box[1]>=170 and box[2]<=850 and box[3]<=355
report={'native_comic_reopen_semantically_exact':True,'native_comic_reopen_png_pixel_exact':True,
        'original_character_and_mixed_sheet_unchanged':True,'duplicate_identity_and_pose_independent':True,
        'wrong_piece_move_undo_whole_project_exact':True,'revision_only_second_label':True,
        'revised_label_identity_style_and_arrow_tip_preserved':True,'first_panel_pixels_exact':True,
        'changed_pixel_bounds':box,'sha256':hashes}
(out/'comic-journey-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
