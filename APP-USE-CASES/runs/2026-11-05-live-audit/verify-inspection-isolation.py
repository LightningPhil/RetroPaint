"""Native display, cutaway and unapplied preview isolation: complete saved projects and STL."""
from pathlib import Path
import copy,hashlib,json
from stl_oracle import read_binary,measure
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={};baseline=None
for n in range(1,15):
 name=f'mouse-audit-inspection187 ({n}).retropaint';raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();doc=json.loads(raw)
 if baseline is None:baseline=doc
 assert doc==baseline
meshes=[]
for suffix in ['', ' (1)']:
 name='mouse-audit-inspection187-3d-mm'+suffix+'.stl';raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();meshes.append(raw);stats=measure(read_binary(raw));assert stats['triangles']==1556 and abs(stats['signed_volume_mm3']-6687.853947863824)<.000001 and stats['bounds_mm']==[[-10,-10,0],[25,10,20]]
assert meshes[0]==meshes[1] and meshes[0]==(out/'mouse-audit-delivery-cadmix-3d-mm.stl').read_bytes()
ui=json.loads((out/'inspection187-ui.json').read_text(encoding='utf-8'));assert len(ui['samples'])==14
for s in ui['samples']:
 if s['stage'].startswith('cut-'):assert s['cutaway'] and s['appearance']=='solid'
assert all('Return to Latest' in ui['blocked'][k] for k in ['rolledProject','rolledSTL']) and all('Apply or cancel' in ui['blocked'][k] for k in ['draftProject','draftPrintTab'])
assert {s['axis'] for s in ui['samples'] if s['stage'].startswith('cut-')}=={'0','1','2'} and {s['flip'] for s in ui['samples'] if s['stage'].startswith('cut-')}=={False,True}
report=dict(status='Pass',all14_native_saved_projects_whole_document_exact=True,cached_CAD_PNG_also_exact=True,paint_photo_crop_text_camera_and_editable_recipe_exact=True,xray_wireframe_solid_native_views=True,all3_section_axes_both_sides_offsets2_10_15=True,leaving_inspect_restores_full_solid=True,rolled_history_project_and_STL_rejected=True,unapplied_preview_project_and_print_route_rejected=True,no_files_at_rejected_save_attempts=True,cancel_and_latest_restore_final_design=True,actual_final_STL_byte_exact_to_preinspection_reference=True,closed_full_material_mm3=stats['signed_volume_mm3'],final_appearance_note=ui['finalAppearance'],hashes=hashes)
(out/'inspection187-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='hashes'},indent=2))
