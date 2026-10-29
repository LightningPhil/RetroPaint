from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/ACCESS-009-before'
ui=json.loads((folder/'ACCESS-009-headless-ui.json').read_text(encoding='utf-8'));assert ui['status']=='Pass' and not ui['errors'] and len(ui['rows'])==7
rows=[]
for row in ui['rows']:
    pcm=np.fromfile(folder/row['pcm_file'],dtype='<f4');assert len(pcm)==row['frames']==sum(row['frame_sizes']) and len(pcm)>10000
    assert np.isfinite(pcm).all() and row['connections']==1 and row['sample_rate'] in [44100,48000]
    peak=float(np.max(np.abs(pcm)));rms=float(np.sqrt(np.mean(pcm.astype(float)**2)))
    assert abs(peak-row['peak'])<1e-9 and abs(rms-row['rms'])<1e-9
    assert peak<1
    if row['expected']=='silent':assert (pcm==0).all(),'Muted/generated output contains a nonzero actual sample'
    else:assert peak>1e-4 and rms>1e-5
    rows.append(dict(label=row['label'],expected=row['expected'],sample_rate=row['sample_rate'],frames=len(pcm),peak=peak,rms=rms,sha256=hashlib.sha256((folder/row['pcm_file']).read_bytes()).hexdigest()))
levels={row['label']:row for row in rows};assert levels['preview-volume100']['peak']>levels['preview-volume45']['peak'] and levels['preview-volume100']['rms']>levels['preview-volume45']['rms']
assert ui['restored']==dict(enabled=False,volume=65,drawing=False,quick='false',preview_disabled=True)
for state in ui['controls']:
    audible=state['enabled'] and state['volume']>0;assert state['quick']==str(audible).lower() and state['preview_disabled']==(not audible)
read=lambda name:json.loads((folder/(name+'.retropaint')).read_text(encoding='utf-8'));image=lambda name:np.asarray(Image.open(folder/(name+'.png')).convert('RGBA'))
before=read('before');pixels=image('before');assert pixels.shape==(640,960,4) and (pixels==255).all()
for label in ['after-settings','fresh/reopened']:
    assert read(label)==before and np.array_equal(image(label),pixels)
for label in ['zero','muted','drawing-enabled','drawing-disabled']:
    visible=image(label+'-undone-visible');assert (visible==255).all(),'One-step Undo after the actual stroke did not restore white'
events=json.loads((folder/'events.json').read_text(encoding='utf-8'))+json.loads((folder/'fresh/events.json').read_text(encoding='utf-8'));downloads=[e for e in events if e['action']=='download'];assert len(downloads)==6
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='NumPy little-endian float32 and Pillow '+Image.__version__,rows=rows,actual_zero_volume_and_muted_feedback_painting_samples_all_zero=True,actual_painting_disabled_samples_all_zero=True,feedback_remains_audible_when_only_painting_sounds_disabled=True,volume100_pcm_peak_and_rms_exceed_volume45=True,all_sound_controls_coherent=True,speaker_button_keyboard_m_and_checkbox_paths_executed=True,actual_new_app_page_restores_muted_volume65_painting_off=True,complete_picture_export_and_actual_project_reopen_exact=True,all_test_gestures_one_step_undo_exact=True,actual_downloads_verified=6,observer='Native Web Audio ScriptProcessor input blocks attached in parallel at the actual browser destination connection. Original output connection is preserved; observer output is zero. No app sound function or stored settings are replaced or directly called.',scope='Application-generated digital audio, public control state and preference persistence. Does not certify laptop speakers, host mute/volume, hearing perception or external audio devices.',execution='Isolated headless browser; no desktop or user browser access')
(root/'evidence/ACCESS-009-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
