import { emit } from './bus';
import { scheduleSound, soundPatch, type SoundName } from './sound-design';
import { readPreference,writePreference } from './preferences-store';
export type { SoundName } from './sound-design';

export interface AudioSettings {enabled:boolean;volume:number;drawing:boolean}
const settings:AudioSettings={enabled:true,volume:.45,drawing:true};
try{const stored=JSON.parse(readPreference('retropaint-sound')??'null') as Partial<AudioSettings>|null;if(stored&&typeof stored==='object'){if(typeof stored.enabled==='boolean')settings.enabled=stored.enabled;if(typeof stored.drawing==='boolean')settings.drawing=stored.drawing;if(typeof stored.volume==='number'&&Number.isFinite(stored.volume))settings.volume=Math.max(0,Math.min(1,stored.volume));}}catch{/* Sound is optional, including in private browsing. */}
let audioCtx:AudioContext|null=null,master:GainNode|null=null,unlocked=false,silenceTimer=0,lastVolume=settings.volume||.45;
const lastAt=new Map<string,number>(),voices=new Map<AudioScheduledSourceNode,()=>void>();
const drawingSounds=new Set<SoundName>(['squeak','zip','shimmer','whir','pencil','swish','rattle','thwack']);

function context():AudioContext|null {
  if(audioCtx)return audioCtx;
  const Ctor=window.AudioContext||(window as unknown as {webkitAudioContext?:typeof AudioContext}).webkitAudioContext;
  if(!Ctor)return null;
  try{
    const ctx=new Ctor(),gain=ctx.createGain(),filter=ctx.createBiquadFilter(),limiter=ctx.createDynamicsCompressor();
    gain.gain.value=settings.enabled?settings.volume:0;filter.type='lowpass';filter.frequency.value=6500;filter.Q.value=.45;
    limiter.threshold.value=-14;limiter.knee.value=18;limiter.ratio.value=4;limiter.attack.value=.003;limiter.release.value=.12;
    gain.connect(filter);filter.connect(limiter);limiter.connect(ctx.destination);audioCtx=ctx;master=gain;return ctx;
  }catch{return null;}
}
function stopVoices():void {for(const [source,cleanup] of voices){try{source.stop();}catch{/* The node may already have ended. */}cleanup();}voices.clear();}
export function audioSettings():AudioSettings {return {...settings};}
export function setAudioSettings(value:Partial<AudioSettings>):void {
  if(typeof value.enabled==='boolean')settings.enabled=value.enabled;if(typeof value.drawing==='boolean')settings.drawing=value.drawing;
  if(typeof value.volume==='number'&&Number.isFinite(value.volume)){settings.volume=Math.max(0,Math.min(1,value.volume));if(settings.volume>0)lastVolume=settings.volume;}
  clearTimeout(silenceTimer);if(audioCtx&&master){master.gain.cancelScheduledValues(audioCtx.currentTime);master.gain.setTargetAtTime(settings.enabled?settings.volume:0,audioCtx.currentTime,.006);if(!settings.enabled||settings.volume===0)silenceTimer=window.setTimeout(stopVoices,35);}
  writePreference('retropaint-sound',JSON.stringify(settings));
  emit('sound-settings');
}
export function unlockAudio():void {
  if(!settings.enabled)return;unlocked=true;const ctx=context();if(ctx?.state==='suspended')void ctx.resume().catch(()=>{});
}
export function toggleSounds():void {const audible=settings.enabled&&settings.volume>0;setAudioSettings({enabled:!audible,volume:audible?settings.volume:settings.volume||lastVolume});}
export function playMarkerPop():void {if(unlocked)play('pop');}
export function play(name:SoundName,pitch=1):boolean {
  if(!settings.enabled||settings.volume===0||document.hidden||!unlocked)return false;
  const ctx=context();if(!ctx||ctx.state!=='running'||!master)return false;
  scheduleSound(ctx,master,soundPatch(name,pitch),ctx.currentTime,(source,cleanup)=>{
    while(voices.size>=24){const oldest=voices.entries().next().value as [AudioScheduledSourceNode,()=>void]|undefined;if(!oldest)break;try{oldest[0].stop();}catch{/* Already ended. */}oldest[1]();voices.delete(oldest[0]);}
    voices.set(source,cleanup);source.onended=()=>{cleanup();voices.delete(source);};
  });return true;
}
export function playThrottled(name:SoundName,gapMs:number,pitch=1):void {
  if(!settings.drawing&&drawingSounds.has(name))return;
  const now=performance.now(),previous=lastAt.get(name)??-Infinity;if(now-previous<gapMs)return;
  if(play(name,pitch))lastAt.set(name,now);
}
export function playDrawing(name:SoundName,pitch=1):boolean {return settings.drawing&&play(name,pitch);}
document.addEventListener('visibilitychange',()=>{
  if(document.hidden){stopVoices();if(audioCtx?.state==='running')void audioCtx.suspend().catch(()=>{});}
  else if(unlocked&&settings.enabled&&audioCtx?.state==='suspended')void audioCtx.resume().catch(()=>{});
});
document.addEventListener('keydown',()=>{if(!unlocked)unlockAudio();},{capture:true});
