from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from collections import Counter
from PIL import Image
import json,hashlib,base64,io,struct,sys,math
import numpy as np
root=Path(__file__).resolve().parent;kind=sys.argv[1];assert kind in ['palette','paint'];number='013' if kind=='palette' else '014';read_json=lambda file:json.loads(file.read_text(encoding='utf-8'))
first=root/('headless/LAYER-'+number+'-target-final');rest=root/('headless/LAYER-'+number+'-compact-final');a=read_json(first/('LAYER-'+number+'-ui.json'));b=read_json(rest/('LAYER-'+number+'-ui.json'))
assert a['status']=='Fail' and len(a['rows'])==2 and not a['errors'];assert ('cadSaveProject' in a['error']) if kind=='palette' else ('draftStatus' in a['error'])
assert b['status']=='Pass' and len(b['rows'])==6 and not b['errors'] and a['origin']==b['origin']=='http://127.0.0.1:8098/'
plan=read_json(root/'fixtures/CADMIX-pairwise-plan.json');completed=[*((first,r) for r in a['rows']),*((rest,r) for r in b['rows'])];assert {row['id'] for _,row in completed}=={row['id'] for row in plan['rows']}
source=read_json(root/'backups/artwork-before-acceptance-audit.retropaint');stl=(root/'headless/LAYER-007-cad-final/1280x720/source-solid.stl').read_bytes();triangle_count=struct.unpack_from('<I',stl,80)[0];assert len(stl)==84+50*triangle_count;edges=Counter();volume=0.
for index in range(triangle_count):
    values=struct.unpack_from('<12fH',stl,84+index*50);normal=np.asarray(values[:3]);tri=np.asarray(values[3:12]).reshape(3,3);cross=np.cross(tri[1]-tri[0],tri[2]-tri[0]);assert np.isfinite(tri).all() and np.linalg.norm(cross)>1e-10 and np.dot(normal,cross)>0;volume+=float(np.dot(tri[0],np.cross(tri[1],tri[2])))/6
    vertices=[tuple(round(float(x),5) for x in point) for point in tri]
    for j in range(3):edges[tuple(sorted((vertices[j],vertices[(j+1)%3])))]+=1
assert volume>0 and all(count==2 for count in edges.values());rows=[];downloads=[];camera_errors=[]
decode=lambda value:np.asarray(Image.open(io.BytesIO(base64.b64decode(value.split(',',1)[1]))).convert('RGBA'))
def compare(actual,expected,cache=False):
    expected=deepcopy(expected);current_view=actual['layers'][2]['cad']['view'];old_view=expected['layers'][2]['cad']['view'];assert current_view.keys()==old_view.keys() and current_view['projection']==old_view['projection'];errors=[]
    for key in ['position','target','up']:errors.extend(abs(float(x)-float(y)) for x,y in zip(current_view[key],old_view[key]))
    errors.append(abs(current_view['span']-old_view['span']));error=max(errors);assert error<=1e-9,'Saved camera drifted beyond floating-point roundtrip tolerance';camera_errors.append(error);expected['layers'][2]['cad']['view']=current_view
    if cache:
        image=decode(actual['layers'][2]['image']);assert image.shape==(640,960,4) and image[:,:,3].any();expected['layers'][2]['image']=actual['layers'][2]['image']
    assert actual==expected,'Document changed outside the explicitly declared scope'
for evidence,row in completed:
    expected_row=next(r for r in plan['rows'] if r['id']==row['id']);assert all(row[key]==value for key,value in expected_row.items());location=evidence/row['id'];read=lambda label:read_json(location/(label+'.retropaint'));image=lambda label:np.asarray(Image.open(location/(label+'.png')).convert('RGBA'));events=read_json(location/'events.json')
    fixture=read_json(root/'headless/CADMIX-fixtures'/row['fixture']/'fresh/fixture.retropaint');before=read('before');assert before==fixture and before['layers'][2]['cad']['bodies']==source['layers'][2]['cad']['bodies'];source_pixels=image('before');assert source_pixels.shape==((480,760,4) if row['crop'] else (640,960,4));assert row['basic_start'] and row['workshop_layers_open_interactive'] and row['paint_background_inert']
    assert (location/'retained-solid.stl').read_bytes()==stl,'Camera, picture crop or caption changed the actual exported solid'
    if kind=='palette':
        opened=read('opened');expected=deepcopy(before);expected['active']=2;compare(opened,expected,True)
        hidden=deepcopy(opened);hidden['layers'][1]['visible']=False
        for label,reference in [('guide-hidden',hidden),('guide-undone',opened),('guide-redone',hidden),('guide-shown',opened)]:compare(read(label),reference)
        returned=read('returned');expected=deepcopy(opened);expected['active']=4;compare(returned,expected,True);assert np.array_equal(image('returned'),source_pixels)
        picked=read('picked');expected=deepcopy(returned);expected['active']=3;compare(picked,expected);assert np.array_equal(image('picked'),source_pixels)
        assert read('fresh/reopened')==picked and np.array_equal(image('fresh/reopened'),source_pixels)
        tabs=[e['tab'] for e in events if e['action']=='actual-workshop-tool'];assert tabs==['add','move','sketch','build','layers','print','history','inspect','print'];assert all(e['working_layer']=='2' for e in events if e['action']=='actual-workshop-tool')
        strip=row['layer_strip_before']
        if strip['scrollWidth']>strip['width']+1:assert row['layer_strip_after']['left']>0
        assert row['workshop_target_after_guide']=='2' and row['palette_remains_open_on_return'] and row['another_paint_sheet_selectable']
        detail=dict(guide_visibility_only_mutation_and_complete_history_verified=True,active_CAD_target_retained=True,all_eight_tool_categories_operated=True,phone_overflow_strip_scrolled_when_required=True,normal_palette_open_and_another_paint_sheet_selectable=True,returned_and_fresh_picture_RGBA_exact_to_original=True)
    else:
        selected=read('paint-selected');compare(selected,before,True);assert np.array_equal(image('paint-selected'),source_pixels)
        caption=read('caption');paint=caption['layers'][3];assert len(paint['objects'])==2 and not decode(paint['image']).any();existing,text=paint['objects'];assert existing['kind']=='raster' and existing['matrix']==[1,0,0,1,0,0] and existing['opacity']==1 and np.array_equal(decode(existing['image']),decode(selected['layers'][3]['image']))
        assert text['kind']=='text' and text['font']=='24px "Arial"' and text['size']==24 and text['width']==200 and text['height']==40 and text['color']=='#FDD835' and text['opacity']==1 and text['matrix'][:4]==[1,0,0,1] and [line['text'] for line in text['lines']]==['Layer caption']
        anchor=row['caption_source_anchor'];assert anchor in [[620,460],[620,340]] and max(abs(x-y) for x,y in zip(text['matrix'][4:],anchor))<=2
        placed=[e for e in events if e['action']=='positioned-and-placed-caption'];assert len(placed)==1 and placed[0]['source_anchor']==anchor
        expected=deepcopy(selected);expected['drawingMode']='vector';expected['layers'][3]['image']=paint['image'];expected['layers'][3]['objects']=paint['objects'];compare(caption,expected)
        converted=deepcopy(caption);converted['layers'][3]['objects'].pop();compare(read('caption-undone'),converted);assert np.array_equal(image('caption-undone'),source_pixels);assert read('caption-redone')==caption and np.array_equal(image('caption-redone'),image('caption'))
        after_pixels=image('caption');changed=(after_pixels!=source_pixels).any(axis=2);allowed=np.zeros(changed.shape,dtype=bool);cropx=100 if row['crop'] else 0;cropy=80 if row['crop'] else 0;x,y=text['matrix'][4:];left=max(0,math.floor(x)-cropx-2);top=max(0,math.floor(y)-cropy-2);right=min(changed.shape[1],math.ceil(x+200)-cropx+2);bottom=min(changed.shape[0],math.ceil(y+40)-cropy+2);allowed[top:bottom,left:right]=True;assert changed.any() and not (changed&~allowed).any();yellow=(np.abs(after_pixels[:,:,:3].astype(int)-[253,216,53]).max(axis=2)<=1)&changed;assert yellow.sum()>10
        returned=read('returned-to-solid');expected=deepcopy(caption);expected['active']=2;compare(returned,expected,True)
        closed=read('closed');expected=deepcopy(caption);expected['active']=1;compare(closed,expected,True);assert np.array_equal(image('closed'),image('caption'))
        assert read('fresh/reopened')==closed and np.array_equal(image('fresh/reopened'),image('caption'))
        assert row['paint_pick_closes_workshop_with_palette_open'] and row['close_without_pick_returns_valid_paint_target']=='Paper'
        detail=dict(paint_pick_closes_workshop_and_keeps_palette_open=True,original_annotations_preserved_in_editable_raster=True,new_yellow_caption_only_on_requested_paint_sheet=True,source_anchor=anchor,saved_text_matrix=text['matrix'],changed_glyph_pixels=int(changed.sum()),fully_yellow_changed_pixels=int(yellow.sum()),caption_history_and_returned_editable_solid_verified=True,close_without_pick_has_valid_Paper_target=True,closed_and_actual_fresh_project_RGBA_exact=True)
    for file in [location/'events.json',location/'fresh/events.json']:downloads += [e for e in read_json(file) if e['action']=='download']
    assert row['actual_fresh_reopen_complete'];rows.append(dict(id=row['id'],viewport=row['viewport'],fixture=row['fixture'],projection=row['projection'],photo=row['photo'],crop=row['crop'],all_original_body_IDs_and_recipes_exact=True,actual_exported_STL_exact_to_original_solid=True,**detail))
assert len(downloads)==(112 if kind=='palette' else 128)
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,kind=kind,rows=rows,actual_downloads_verified=len(downloads),pairwise_plan='fixtures/CADMIX-pairwise-plan.json',all8_planned_projection_photo_crop_triples_and_all_factor_pairs_executed=True,maximum_saved_camera_roundtrip_error=max(camera_errors),camera_tolerance_mm=1e-9,STL=dict(triangles=triangle_count,closed_oriented_edges=True,edge_quantisation_mm=.00001,signed_volume_mm3=volume,all_actual_exports_byte_identical=True),oracle='Complete expected layer/visibility/active/object mutations, literal original solid recipes/IDs and source images, independent Pillow RGBA crop/glyph bounds and known yellow ink, full history and real fresh file inputs. Only derived CAD preview cache may regenerate at workshop transitions; every final picture is pixel exact to its expected prior state. Saved camera Float64 roundtrip tolerance1e-9 applies only to camera fields. Actual STL bytes independently checked for oriented triangles, closed edges and signed volume, then exact equality across all eight native exports.',coverage_chunks=[dict(folder=str(first.relative_to(root)),completed_rows=['v1','v2'],unfinished_setup_excluded=True),dict(folder=str(rest.relative_to(root)),completed_rows=['v3','v4','v5','v6','v7','v8'])],execution='Isolated headless production UI; no computer-use runtime or existing user browser/profile access')
(root/('evidence/LAYER-'+number+'-independent-verification.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(case='LAYER-'+number,rows=len(rows),downloads=len(downloads),maximum_camera_error=max(camera_errors),STL_volume=volume),indent=2))
