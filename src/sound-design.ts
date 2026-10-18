export type SoundName='pop'|'clunk'|'thwack'|'rip'|'splash'|'vwoop'|'squeak'|'rattle'|'shimmer'|'zip'|'snick'|'clack'|'squeegee'|'whir'|'motor-stop'|'undo'|'redo'|'save'|'place'|'delete'|'colour'|'pencil'|'swish';
export interface SoundPart {kind:'tone'|'noise';wave:OscillatorType;frequency:number;endFrequency:number;duration:number;level:number;delay:number;attack:number;q:number}
const tone=(wave:OscillatorType,frequency:number,endFrequency:number,duration:number,level:number,delay=0,attack=.004):SoundPart=>({kind:'tone',wave,frequency,endFrequency,duration,level,delay,attack,q:1});
const noise=(frequency:number,endFrequency:number,duration:number,level:number,delay=0,q=.7):SoundPart=>({kind:'noise',wave:'sine',frequency,endFrequency,duration,level,delay,attack:.005,q});

/** Small material sounds, with soft attacks rather than abrupt oscillator clicks. */
export function soundPatch(name:SoundName,pitch=1):SoundPart[] {
  const p=Math.max(.4,Math.min(2.5,pitch));
  switch(name){
    case 'pop':return [tone('sine',840*p,210,.095,.3,0,.002),tone('triangle',430*p,140,.04,.035,.002)];
    case 'clunk':return [tone('sine',240*p,160*p,.075,.23),tone('sine',435*p,310*p,.045,.075,.002),noise(1200,600,.022,.04)];
    case 'thwack':return [tone('triangle',190*p,64,.12,.3),noise(600,180,.06,.09),tone('sine',780*p,350,.025,.025)];
    case 'rip':return [noise(1600,700,.14,.15),...Array.from({length:3},(_,i)=>tone('triangle',330-i*30,150,.025,.07,i*.035))];
    case 'splash':return [noise(850,180,.2,.1),...Array.from({length:3},(_,i)=>tone('sine',(620+i*170)*p,(1100-i*180)*p,.09,.12,i*.045))];
    case 'vwoop':return [tone('sine',330*p,65,.4,.22),noise(450,110,.28,.05)];
    case 'squeak':return [tone('sine',640*p,940*p,.075,.1),tone('triangle',900*p,1300*p,.045,.025),noise(1400,2200,.06,.025,0,2)];
    case 'rattle':return [...Array.from({length:4},(_,i)=>noise(950+i*90,500,.035,.12-i*.015,i*.028,1.4)),tone('triangle',110,75,.1,.05)];
    case 'shimmer':return [tone('sine',1200*p,1190*p,.19,.055,0,.012),tone('sine',1500*p,1490*p,.22,.04,.025,.012),tone('sine',1800*p,1790*p,.25,.025,.05,.012)];
    case 'zip':return [noise(800*p,1400*p,.055,.08,0,1.2)];
    case 'snick':return [tone('sine',1000*p,450,.03,.13),noise(2000,800,.018,.035)];
    case 'clack':return [tone('triangle',240,140,.055,.15),tone('triangle',200,110,.06,.13,.085)];
    case 'squeegee':return [noise(500,1700,.52,.13),tone('triangle',140,200,.25,.025)];
    case 'whir':return [tone('triangle',160*p,230*p,.14,.035),tone('sine',320*p,460*p,.12,.012),noise(350,500,.1,.02)];
    case 'motor-stop':return [tone('sine',220,80,.14,.14),tone('triangle',420,200,.035,.05,.055)];
    case 'undo':return [tone('sine',660,620,.075,.12),tone('triangle',523,500,.095,.11,.055)];
    case 'redo':return [tone('triangle',523,530,.075,.11),tone('sine',660,680,.095,.12,.055)];
    case 'save':return [tone('triangle',784,784,.11,.1,0,.008),tone('sine',1047,1047,.15,.09,.065,.008),tone('sine',1318,1310,.19,.065,.13,.008)];
    case 'place':return [tone('triangle',300,180,.06,.15),tone('sine',880,850,.09,.06,.025,.008)];
    case 'delete':return [noise(900,400,.11,.1),tone('sine',190,90,.07,.08)];
    case 'colour':return [tone('sine',900*p,1200*p,.055,.09),tone('sine',1346*p,1340*p,.07,.025,.015)];
    case 'pencil':return [noise(1500*p,2200*p,.07,.055,0,.6)];
    case 'swish':return [noise(600*p,1200*p,.12,.065,0,.7)];
  }
}

const noiseBuffers=new WeakMap<BaseAudioContext,AudioBuffer>();
function noiseBuffer(ctx:BaseAudioContext):AudioBuffer {
  let buffer=noiseBuffers.get(ctx);if(buffer)return buffer;
  buffer=ctx.createBuffer(1,Math.ceil(ctx.sampleRate*1.5),ctx.sampleRate);const data=buffer.getChannelData(0);let seed=1739;
  for(let i=0;i<data.length;i++){seed=(Math.imul(seed,1664525)+1013904223)>>>0;data[i]=seed/2147483648-1;}
  noiseBuffers.set(ctx,buffer);return buffer;
}

export function scheduleSound(ctx:BaseAudioContext,output:AudioNode,parts:SoundPart[],at:number,register?:(source:AudioScheduledSourceNode,cleanup:()=>void)=>void):void {
  for(const [index,part] of parts.entries()){
    const start=at+part.delay,end=start+part.duration,gain=ctx.createGain();
    gain.gain.setValueAtTime(0,start);gain.gain.linearRampToValueAtTime(part.level,start+Math.min(part.attack,part.duration/4));gain.gain.exponentialRampToValueAtTime(.0001,end);gain.connect(output);
    let source:AudioBufferSourceNode|OscillatorNode,filter:BiquadFilterNode|null=null;
    if(part.kind==='noise'){
      source=ctx.createBufferSource();source.buffer=noiseBuffer(ctx);filter=ctx.createBiquadFilter();filter.type='bandpass';filter.frequency.setValueAtTime(part.frequency,start);filter.frequency.exponentialRampToValueAtTime(Math.max(20,part.endFrequency),end);filter.Q.value=part.q;source.connect(filter);filter.connect(gain);
    } else {
      source=ctx.createOscillator();source.type=part.wave;source.frequency.setValueAtTime(part.frequency,start);source.frequency.exponentialRampToValueAtTime(Math.max(8,part.endFrequency),end);source.connect(gain);
    }
    const cleanup=()=>{source.disconnect();filter?.disconnect();gain.disconnect();};source.onended=cleanup;register?.(source,cleanup);
    if(source instanceof AudioBufferSourceNode)source.start(start,(index*.137)%Math.max(.001,1.5-part.duration));else source.start(start);
    source.stop(end+.01);
  }
}
