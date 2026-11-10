"""Correlate actual sound UI actions with standard Web Audio events."""
import hashlib,json
from datetime import datetime
from pathlib import Path
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads'
phases=json.loads((out/'sound-evidence.json').read_bytes());by_name={p['label']:p for p in phases}
rows=[json.loads(line) for line in (out.parent/'fault-controls/requests.jsonl').read_text(encoding='utf-8').splitlines()]
events=[r['event'] for r in rows if r.get('event',{}).get('type','').startswith('audio')]
def when(e):return datetime.fromisoformat(e['at'].replace('Z','+00:00')).timestamp()*1000
def ui(p):return {e['id']:e for e in p['ui']}
def settings(name):
    p=ui(by_name[name]);return p['soundEnabled']['checked'],int(p['soundVolume']['value']),p['drawingSounds']['checked']
starts={};targets={}
for p in phases:
    current=ui(p);audible=current['soundEnabled']['checked'] and int(current['soundVolume']['value'])>0
    assert current['soundToggle']['pressed']==str(bool(audible)).lower(),p['label']
    assert current['soundPreview']['disabled']==(not audible),p['label']
    assert current['soundVolumeValue']['text'].strip()==current['soundVolume']['value']+'%',p['label']
    if 'start' not in p:continue
    within=[e for e in events if p['start']<=when(e)<=p['end']]
    sources=[e for e in within if e['type']=='audio source start'];starts[p['label']]=len(sources)
    assert all(e['detail']['contextState']=='running' for e in sources)
    targets[p['label']]=[e['detail']['value'] for e in within if e['type']=='audio gain target' and e['detail']['id']==1]
for name in ['maximum-preview','drawing-enabled','feedback-with-painting-disabled']:assert starts[name]>0,name
for name in ['drawing-disabled','zero-volume','zero-preview-disabled-click','zero-painting','zero-feedback-other-workflow','mute-switch','muted-preview-disabled-click','muted-tool-feedback','muted-painting','M-mute','speaker-mute']:
    assert starts[name]==0,name
assert targets['maximum-volume'][-1]==1 and targets['zero-volume'][-1]==0 and targets['mute-switch'][-1]==0
assert targets['restore-intermediate-volume'][-1]==.45
assert settings('maximum-volume')==(True,100,True)
assert settings('zero-volume')==(True,0,True)
assert settings('reloaded-muted45-painting-off')==(False,45,False)
assert settings('reloaded-zero-enabled-painting-on')==(True,0,True)
assert settings('M-unmute')==(True,45,True) and settings('M-mute')==(False,45,True)
assert settings('speaker-unmute')==(True,45,True) and settings('speaker-mute')==(False,45,True)
assert settings('restored-original')==settings('original')==(True,45,True)
hashes={};documents=[]
for stage in ['before','after']:
    name='mouse-audit-sound-'+stage+'.retropaint';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();documents.append(json.loads(data))
assert documents[0]==documents[1],'Sound workflows changed the painting'
report={'status':'Pass','all_sound_controls_coherent':True,'volume_0_45_100_and_mute_gain_targets_verified':True,'no_audio_sources_start_for_muted_or_zero_preview_feedback_and_painting':True,'painting_off_retains_explicit_feedback':True,'M_and_speaker_controls_synchronise_preferences':True,'mute_and_zero_settings_persist_after_real_reload':True,'intentional_speaker_reenable_recovers45_percent':True,'original_settings_and_whole_document_restored':True,'audio_evidence':'Standard Web Audio graph/source events; no physical speaker or hearing certification','source_starts_by_live_phase':starts,'sha256':hashes}
(out/'sound-controls-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['sha256','source_starts_by_live_phase']},indent=2))
