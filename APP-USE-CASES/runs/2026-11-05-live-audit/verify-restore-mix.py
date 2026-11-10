"""Native recent-draft restoration and complete mixed editable Undo/Redo."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(stem):
 name='mouse-audit-'+stem+'.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data)
 hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
base=doc('target-final-caption');before=doc('restore-mix-before');green=doc('postfix-duplicate-before-refresh')
assert len(before['layers'])==5 and before['layers'][4]['cad']['bodies'][0]['script']['language']=='openscad'
assert before['layers'][:3]==base['layers'][:3] and before['layers'][4]==base['layers'][4]
a,b=base['layers'][3],before['layers'][3]
assert a['image']==b['image'] and a['objects']==b['objects'][:-1]
new=b['objects'][-1];assert new['kind']=='path' and new['stroke']['color']=='#E53935'
assert new['paths'][0]['closed'] and new['lineWidth']==22
points=[(p['x']+new['matrix'][4],p['y']+new['matrix'][5]) for p in new['paths'][0]['points']]
bounds=[min(x for x,y in points),min(y for x,y in points),max(x for x,y in points),max(y for x,y in points)]
# Native input was a56x40screen-pixel drag at0.8screen pixels per paper
# pixel. Its exact origin was not a fixture requirement; the initial750px
# screenshot estimate ignored the border/DPI offset. Verify its independent
# 70x50span and intended region, then require exact full-data restoration.
assert abs(bounds[2]-bounds[0]-70)<.01 and abs(bounds[3]-bounds[1]-50)<.01
assert 700<bounds[0]<800 and 300<bounds[1]<400
for stage in ['chosen','redone','original-store-unchanged']:assert doc('restore-mix-'+stage)==green,stage
for stage in ['undone','before-store-recheck','final-current']:assert doc('restore-mix-'+stage)==before,stage
pages=json.loads((out/'recent-draft-page-evidence.json').read_bytes())
assert len(pages)==3 and [len(p['cards']) for p in pages]==[3,3,2]
assert pages[0]['previousDisabled'] and not pages[0]['nextDisabled'] and pages[2]['nextDisabled'] and not pages[2]['previousDisabled']
result={'unsaved_mixed_edit_contains_new_red_path_and_existing_code_photo_live_stamp':True,
 'one_step_restore_undo_returns_whole_previous_document_exact':True,'redo_returns_requested_green_draft_exact':True,
 'original_older_green_entry_reselected_after_undo_is_unchanged':True,
 'final_undo_restores_current_work_exact':True,'all_eight_recent_entries_reached_across_three_pages':True,
 'independent_new_red_rectangle_bounds':bounds,'sha256':hashes}
(out/'restore-mix-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='sha256'},indent=2))
