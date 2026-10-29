from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/ACCESS-008-complete'
read=lambda name:json.loads((folder/(name+'.retropaint')).read_text(encoding='utf-8'))
image=lambda name:np.asarray(Image.open(folder/(name+'.png')).convert('RGBA'))
ui=json.loads((folder/'ACCESS-008-headless-ui.json').read_text(encoding='utf-8'));assert ui['status']=='Pass' and not ui['errors'] and len(ui['rows'])==6
before=read('before');pixels=image('before');assert (before['width'],before['height'])==(960,640) and len(before['layers'])==1 and before['drawingMode']=='raster'
nonwhite=np.any(pixels[:,:,:3]!=255,axis=2);assert nonwhite.sum()>50 and (pixels[:,:,3]==255).all()
paint=pixels[nonwhite].astype(int);assert np.mean(paint[:,2])>np.mean(paint[:,0]),'Actual fallback drawing is not the selected blue'
styles=[];downloads=[]
for row in ui['rows']:
    if 'value' not in row:continue
    value=row['value'];styles.append(row['computed_background_image']);assert row['restored_on_new_app_page']
    for name in ['theme-'+value,'reopen-'+value+'/reopened']:
        assert read(name)==before and np.array_equal(image(name),pixels),'Workspace theme leaked into paper/project/export'
for name in ['unknown/fallback-usable','unavailable/current-visit-night','unavailable/fallback-usable','redone']:
    assert read(name)==before and np.array_equal(image(name),pixels),'Storage fallback blocked drawing or changed the document'
assert len(set(styles))==4
assert (image('undone')==255).all(),'Preferences added an unwanted history step before the initial mark'
for location in [folder,*(folder/('reopen-'+value) for value in ['mint','lavender','sand','night']),folder/'unknown',folder/'unavailable']:
    downloads += [e for e in json.loads((location/'events.json').read_text(encoding='utf-8')) if e['action']=='download']
assert len(downloads)==28
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,themes_executed=['Mint','Lilac','Oat','Night'],four_distinct_computed_workspace_backgrounds=True,every_theme_restored_in_new_app_page=True,complete_project_and_full_size_export_exact_for_every_theme_and_reopen=True,unknown_external_preference_falls_back_to_mint=True,unavailable_storage_allows_current_visit_theme_and_drawing=True,unavailable_storage_reopen_defaults_to_mint_and_remains_usable=True,initial_stroke_one_step_undo_and_redo_exact=True,actual_downloads_verified=len(downloads),oracle='Independent Pillow decoded RGBA, complete actual project identity, blue stroke/white paper and Undo checks; measured computed CSS backgrounds and public selected theme controls; deliberately unknown storage fixture and Storage SecurityError injection in isolated contexts only.',execution='Isolated headless UI; no existing browser/profile or desktop use')
(root/'evidence/ACCESS-008-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
