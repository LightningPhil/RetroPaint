/* Visible, disposable acceptance controls. No application objects are accessed. */
(() => {
  const events=[]; let gate=false,fail=false,failPhoto=false,holdPhotoReply=false,releaseCadCapture=false,heldPhotoReplies=[],held=[],panel;
  const wikiFaults=new URLSearchParams(location.search).has('wiki-faults');
  const recoveryFaults=new URLSearchParams(location.search).has('recovery-faults');
  const clipboardFaults=new URLSearchParams(location.search).has('clipboard-faults');
  const preferenceFault=new URLSearchParams(location.search).get('preference-fault');
  if(new URLSearchParams(location.search).has('audio-observe')){
    const gainParams=new WeakMap();let nextGain=0;
    const createGain=BaseAudioContext.prototype.createGain;
    BaseAudioContext.prototype.createGain=function(...args){const gain=createGain.apply(this,args);gainParams.set(gain.gain,++nextGain);record('audio gain created',{id:nextGain,value:gain.gain.value});return gain;};
    const target=AudioParam.prototype.setTargetAtTime;
    AudioParam.prototype.setTargetAtTime=function(value,...args){if(gainParams.has(this))record('audio gain target',{id:gainParams.get(this),value});return target.call(this,value,...args);};
    for(const ctor of [OscillatorNode,AudioBufferSourceNode])for(const method of ['start','stop']){
      const native=ctor.prototype[method];ctor.prototype[method]=function(...args){record('audio source '+method,{kind:ctor.name,contextState:this.context.state});return native.apply(this,args);};
    }
  }
  if(preferenceFault){
    const keys=new Set(['retropaint-desk','retropaint-reduced-motion','retropaint-sound']);
    const get=Storage.prototype.getItem,set=Storage.prototype.setItem;
    Storage.prototype.getItem=function(key){
      if(keys.has(key)&&preferenceFault==='denied'){record('preference read denied',key);throw new DOMException('Audit: preferences unavailable','SecurityError');}
      if(key==='retropaint-desk'&&preferenceFault==='unknown'){record('preference unknown',key);return 'unrecognised-audit-theme';}
      return get.call(this,key);
    };
    Storage.prototype.setItem=function(key,value){
      if(keys.has(key)&&preferenceFault==='denied'){record('preference write denied',key);throw new DOMException('Audit: preferences unavailable','SecurityError');}
      return set.call(this,key,value);
    };
  }
  let nextDraftRead=null;
  let denyFullscreen=false;
  const nativeFullscreen=Element.prototype.requestFullscreen;
  if(nativeFullscreen)Element.prototype.requestFullscreen=function(...args){
    record('fullscreen request',{target:this.tagName,denied:denyFullscreen});
    if(denyFullscreen){denyFullscreen=false;return Promise.reject(new DOMException('Audit: full screen denied','NotAllowedError'));}
    return nativeFullscreen.apply(this,args).then(value=>{record('fullscreen result','resolved');return value;},error=>{record('fullscreen result',String(error));throw error;});
  };
  document.addEventListener('fullscreenchange',()=>record('fullscreen change',{active:document.fullscreenElement?.tagName??null}));
  document.addEventListener('fullscreenerror',()=>record('fullscreen error','browser event'));
  if(recoveryFaults){
    const nativeGet=IDBObjectStore.prototype.get;
    IDBObjectStore.prototype.get=function(key){
      const request=nativeGet.call(this,key);
      if(this.name!=='pictures'||!nextDraftRead)return request;
      const fault=nextDraftRead;nextDraftRead=null;record('draft read fault',{fault,key});
      // Degrade one standard API result only. Stored bytes are never changed.
      return new Proxy(request,{get(target,property){
        if(property==='result'){
          const value=Reflect.get(target,property,target);
          if(fault==='missing')return undefined;
          if(!value)return value;
          if(fault==='json')return {...value,data:'{"version":13,"layers":['};
          const data=JSON.parse(value.data);data.layers[0].image='data:image/png;base64,YnJva2Vu';return {...value,data:JSON.stringify(data)};
        }
        const value=Reflect.get(target,property,target);return typeof value==='function'?value.bind(target):value;
      }});
    };
  }
  let holdMcad=wikiFaults,mcadHeld=[],denyClipboard=false,denyClipboardAll=false;
  const nativeWriteText=navigator.clipboard.writeText.bind(navigator.clipboard);
  navigator.clipboard.writeText=text=>denyClipboard||denyClipboardAll?Promise.reject(new DOMException('Audit: clipboard write denied','NotAllowedError')):nativeWriteText(text);
  if(clipboardFaults)for(const method of ['read','readText','write']){
    const native=navigator.clipboard[method].bind(navigator.clipboard);
    navigator.clipboard[method]=(...args)=>{
      if(denyClipboardAll){record('clipboard API denied',method);return Promise.reject(new DOMException('Audit: clipboard '+method+' denied','NotAllowedError'));}
      return native(...args);
    };
  }
  if(wikiFaults){
    const nativeWrite=navigator.clipboard.write.bind(navigator.clipboard);
    navigator.clipboard.write=items=>{record('clipboard write requested',items.map(item=>item.types));return nativeWrite(items).then(value=>{record('clipboard write resolved','Standard browser write completed');return value;},error=>{record('clipboard write rejected',error.name+': '+error.message);throw error;});};
    document.addEventListener('paste',event=>{const text=event.clipboardData?.getData('text/plain')??'';record('native paste observed',{target:event.target?.id,types:[...(event.clipboardData?.types??[])],textLength:text.length,ownMarker:text.startsWith('RetroPaint editable pieces ')?text:null,files:[...(event.clipboardData?.files??[])].map(f=>({type:f.type,size:f.size}))});},true);
  }
  const canvasCalls={};
  const nativeNow=performance.now.bind(performance),nativeFrame=requestAnimationFrame.bind(window),nativeCancelFrame=cancelAnimationFrame.bind(window);let frozen=null;
  const activeFrames=new Set(),activeTimeouts=new Set(),activeIntervals=new Set(),timerTotals={timeouts:0,intervals:0,frames:0,stringTimeouts:0};
  const nativeTimeout=setTimeout.bind(window),nativeInterval=setInterval.bind(window),nativeClearTimeout=clearTimeout.bind(window),nativeClearInterval=clearInterval.bind(window);
  window.setTimeout=function(callback,delay,...args){
    timerTotals.timeouts++;if(typeof callback!=='function'){timerTotals.stringTimeouts++;return nativeTimeout(callback,delay,...args);}
    let id;id=nativeTimeout(function(...values){activeTimeouts.delete(id);return callback.apply(this,values);},delay,...args);activeTimeouts.add(id);return id;
  };
  window.clearTimeout=id=>{activeTimeouts.delete(id);activeIntervals.delete(id);return nativeClearTimeout(id);};
  window.setInterval=function(callback,delay,...args){timerTotals.intervals++;const id=nativeInterval(callback,delay,...args);activeIntervals.add(id);return id;};
  window.clearInterval=id=>{activeTimeouts.delete(id);activeIntervals.delete(id);return nativeClearInterval(id);};
  performance.now=()=>frozen??nativeNow();
  window.requestAnimationFrame=callback=>{timerTotals.frames++;let id;id=nativeFrame(time=>{activeFrames.delete(id);return callback(frozen??time);});activeFrames.add(id);return id;};
  window.cancelAnimationFrame=id=>{activeFrames.delete(id);return nativeCancelFrame(id);};
  for(const name of ['clearRect','drawImage','fillRect','putImageData']){
    const native=CanvasRenderingContext2D.prototype[name];
    CanvasRenderingContext2D.prototype[name]=function(...args){
      const id=this.canvas.id||'(offscreen)';canvasCalls[id]=(canvasCalls[id]||0)+1;
      return native.apply(this,args);
    };
  }
  const originalFetch=window.fetch.bind(window);
  function record(type,detail){
    const item={at:new Date().toISOString(),type,detail};events.push(item);
    if(panel)panel.querySelector('pre').textContent=events.slice(-8).map(e=>e.type+': '+(typeof e.detail==='string'?e.detail:JSON.stringify(e.detail))).join('\n');
    void originalFetch('/audit-event',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(item)});
  }
  window.fetch=(input,options)=>{const u=typeof input==='string'?input:input.url||String(input);if(!u.startsWith('data:')&&!u.startsWith('blob:'))record('window fetch',(options?.method||'GET')+' '+u);if(holdMcad&&u.includes('/openscad/mcad.json')){record('MCAD held','Real response deferred until visible Release MCAD button');return new Promise((resolve,reject)=>mcadHeld.push(()=>originalFetch(input,options).then(resolve,reject)));}return originalFetch(input,options);};
  const xhrOpen=XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open=function(method,url,...rest){record('XHR',method+' '+url);return xhrOpen.call(this,method,url,...rest);};
  const beacon=navigator.sendBeacon.bind(navigator);
  navigator.sendBeacon=(url,data)=>{record('beacon',String(url)+' bytes '+(data?.size||data?.length||0));return beacon(url,data);};
  if(new URLSearchParams(location.search).has('storage-blocked')){
    IDBFactory.prototype.open=function(){throw new DOMException('Audit: draft storage unavailable','SecurityError');};
    Storage.prototype.setItem=function(){throw new DOMException('Audit: storage quota unavailable','QuotaExceededError');};
    Storage.prototype.getItem=function(){throw new DOMException('Audit: storage unavailable','SecurityError');};
    record('fault','IndexedDB and preference/session storage denied in this disposable page');
  }
  const toBlob=HTMLCanvasElement.prototype.toBlob;
  HTMLCanvasElement.prototype.toBlob=function(callback,...args){
    if(fail){fail=false;record('fault','one canvas encoder returned null');queueMicrotask(()=>callback(null));return;}
    if(gate&&document.querySelector('#saveProject')?.disabled){
      held.push(()=>toBlob.call(this,callback,...args));record('snapshot held','canvas '+this.width+'x'+this.height+'; production snapshot already captured');return;
    }
    return toBlob.call(this,callback,...args);
  };
  const WorkerOriginal=window.Worker,lateMessages=new URLSearchParams(location.search).has('late-messages');
  const retired={openscad:null,cad:null};let currentCadId;
  const openScadEvidence=[];
  window.Worker=class extends WorkerOriginal{
    set onmessage(listener){super.onmessage=typeof listener==='function'?event=>{
      if(this.auditPhoto&&holdPhotoReply){holdPhotoReply=false;heldPhotoReplies.push(()=>listener.call(this,event));record('photo reply held',{request:event.data.id});}
      else listener.call(this,event);
    }:listener;}
    constructor(url,options){
      const u=new URL(url,location.href);
      if(new URLSearchParams(location.search).has('cpu')&&u.pathname.includes('super-resolution-worker'))u.searchParams.set('cpu','1');
      record('worker',u.href);super(u,options);
      this.auditKind=u.pathname.includes('/openscad/')?'openscad':u.pathname.includes('cad-worker')?'cad':null;
      this.auditPhoto=u.pathname.includes('photo-worker');
      this.auditListeners=[];
      this.addEventListener('message',e=>{if(e.data.progress?.message)record('progress',e.data.progress.message);if(e.data.error)record('worker error',e.data.error);});
      if(wikiFaults&&this.auditKind==='openscad')this.addEventListener('message',e=>{
        const item={input:this.auditInput,logs:e.data.logs,error:e.data.error};
        if(e.data.bytes){const bytes=e.data.bytes;let binary='';for(let i=0;i<bytes.length;i+=8192)binary+=String.fromCharCode(...bytes.subarray(i,i+8192));item.stl=btoa(binary);}
        openScadEvidence.push(item);record('OpenSCAD evidence',{title:this.auditInput?.label,bytes:e.data.bytes?.length,error:e.data.error});
      });
    }
    addEventListener(type,listener,options){if(lateMessages&&this.auditListeners&&['message','error'].includes(type))this.auditListeners.push({type,listener});return super.addEventListener(type,listener,options);}
    postMessage(data,...rest){if(failPhoto&&this.auditPhoto){failPhoto=false;record('photo failure injected',{request:data.id});throw new Error('Audit: photo processing unavailable. Please try again.');}if(this.auditKind==='cad')currentCadId=data.id;if(wikiFaults&&this.auditKind==='openscad')this.auditInput={...structuredClone(data),label:document.querySelector('#cadWikiPreview[open] h2')?.textContent||document.querySelector('#cadScriptName')?.value};return super.postMessage(data,...rest);}
    terminate(){if(lateMessages&&this.auditKind){retired[this.auditKind]={worker:this,listeners:[...this.auditListeners],onmessage:this.onmessage,onerror:this.onerror};record('retired worker',this.auditKind);}return super.terminate();}
  };
  document.addEventListener('DOMContentLoaded',()=>{
    // Authentic lostpointercapture after a real mouse move, using only the
    // standard capture API. No application objects are accessed.
    document.addEventListener('pointermove',event=>{
      const target=event.target;
      if(!releaseCadCapture||!event.buttons||!(target instanceof HTMLCanvasElement)||target.id!=='cadCanvas'||!target.hasPointerCapture(event.pointerId))return;
      releaseCadCapture=false;
      queueMicrotask(()=>{const held=target.hasPointerCapture(event.pointerId);record('CAD capture release',{pointerId:event.pointerId,held,clientX:event.clientX,clientY:event.clientY});if(held)target.releasePointerCapture(event.pointerId);});
    },true);
    if(new URLSearchParams(location.search).has('pointer')){
      for(const phase of ['pointerdown','pointerup','pointercancel','gotpointercapture','lostpointercapture','pointermove'])document.addEventListener(phase,event=>{
        if(!(event.target instanceof HTMLElement)||!['view','ui','cadCanvas','photoMiniCanvas','canvasSlot','workspaceOverlay'].includes(event.target.id)||phase==='pointermove'&&!event.buttons)return;
        const r=event.target.getBoundingClientRect(),paper=document.getElementById('view')?.getBoundingClientRect();record('native pointer',{phase,target:event.target.id,pointerType:event.pointerType,pointerId:event.pointerId,buttons:event.buttons,shiftKey:event.shiftKey,ctrlKey:event.ctrlKey,altKey:event.altKey,metaKey:event.metaKey,clientX:event.clientX,clientY:event.clientY,rect:{x:r.x,y:r.y,width:r.width,height:r.height},canvas:{width:event.target.width,height:event.target.height},paperRect:paper&&{x:paper.x,y:paper.y,width:paper.width,height:paper.height}});
      },true);
      for(const phase of ['blur','focus'])window.addEventListener(phase,()=>record('native window',{phase,focused:document.activeElement?.id}));
      document.addEventListener('visibilitychange',()=>record('native visibility',{hidden:document.hidden}));
    }
    panel=document.createElement('details');panel.id='auditControls';panel.open=true;
    panel.style.cssText='position:fixed;right:8px;bottom:8px;z-index:999999;background:#fffbe8;color:#151515;border:2px solid #876;padding:8px;max-width:340px;font:12px Arial;max-height:240px;overflow:auto';
    // Keep the collapsed test panel off the phone's Photo lab action buttons.
    const phoneStyle=document.createElement('style');
    phoneStyle.textContent='@media(max-width:600px){#auditControls:not([open]){top:228px;bottom:auto!important}} @media(max-height:550px){#auditControls:not([open]){left:8px;right:auto;top:auto;bottom:8px!important}}';
    document.head.append(phoneStyle);
    const summary=document.createElement('summary');summary.textContent='Disposable audit controls';panel.append(summary);
    const status=document.createElement('pre');status.style.cssText='white-space:pre-wrap;max-height:100px;overflow:auto';
    function button(label,fn){const b=document.createElement('button');b.textContent=label;b.style.margin='3px';b.onclick=fn;panel.append(b);}
    button('Release next CAD capture on drag',()=>{releaseCadCapture=true;record('armed','release real CAD pointer capture after a native drag move');});
    button('Hold next project encoding',()=>{gate=true;record('armed','hold next explicit project save after snapshot');});
    button('Release encoding',()=>{gate=false;const work=held;held=[];record('release',work.length+' encoding callbacks');work.forEach(f=>f());});
    button('Fail next encoding',()=>{fail=true;record('armed','one null encoder result');});
    button('Fail next photo processing request',()=>{failPhoto=true;record('armed','one standard photo Worker.postMessage failure');});
    button('Hold next photo reply',()=>{holdPhotoReply=true;record('armed','defer one real photo Worker onmessage callback');});
    button('Release held photo replies',()=>{const work=heldPhotoReplies;heldPhotoReplies=[];record('photo replies released',{count:work.length});work.forEach(f=>f());});
    button('Hide audit controls',()=>{panel.hidden=true;record('audit controls hidden','Reload restores the disposable panel');});
    button('Stall next CAD job',async()=>{await originalFetch('/audit-command',{method:'POST',body:'stall-cad'});record('armed','one CAD request stalls after started; real 45-second production timer');});
    button('Block model download',async()=>{await originalFetch('/audit-command',{method:'POST',body:'block-model'});record('armed','model requests return503');});
    button('Allow model download',async()=>{await originalFetch('/audit-command',{method:'POST',body:'allow-model'});record('armed','normal model bytes restored');});
    if(recoveryFaults)for(const [fault,label] of [['missing','missing'],['json','truncated JSON'],['image','damaged PNG']])button('Next draft read: '+label,()=>{nextDraftRead=fault;record('armed','One '+label+' recovery result; original stored bytes untouched');});
    if(clipboardFaults){
      button('Deny clipboard access',()=>{denyClipboardAll=true;record('clipboard','Explicit read/write API denial armed; browser permissions unchanged');});
      button('Restore clipboard access',()=>{denyClipboardAll=false;record('clipboard','Normal clipboard APIs restored');});
    }
    if(wikiFaults){
      button('Release MCAD catalogue',()=>{holdMcad=false;const work=mcadHeld;mcadHeld=[];record('MCAD release',work.length+' genuine fetch requests');work.forEach(fn=>fn());});
      button('Release MCAD in five seconds',()=>{record('MCAD release scheduled','Five seconds to focus and scroll before genuine response');setTimeout(()=>{holdMcad=false;const work=mcadHeld;mcadHeld=[];record('MCAD release',work.length+' genuine fetch requests');work.forEach(fn=>fn());},5000);});
      button('Deny clipboard writes',()=>{denyClipboard=true;record('clipboard','Explicit test API denial armed; browser permissions unchanged');});
      button('Allow clipboard writes',()=>{denyClipboard=false;record('clipboard','Normal clipboard API restored');});
      button('Download OpenSCAD evidence',()=>{const a=document.createElement('a');a.download='mouse-audit-wiki-engine-evidence.json';a.href=URL.createObjectURL(new Blob([JSON.stringify(openScadEvidence)],{type:'application/json'}));a.click();});
    }
    if(lateMessages)for(const kind of ['openscad','cad'])button('Deliver retired '+kind+' error',()=>{
      const old=retired[kind];if(!old){record('late delivery','no retired '+kind+' worker');return;}
      const data={error:'Audit stale '+kind+' response must be ignored',id:currentCadId};
      const event=new MessageEvent('message',{data});
      for(const item of old.listeners)if(item.type==='message')typeof item.listener==='function'?item.listener.call(old.worker,event):item.listener.handleEvent(event);
      if(old.onmessage)old.onmessage.call(old.worker,event);
      record('late delivery',kind+' obsolete message handler invoked; current CAD request '+currentCadId);
      const error=new ErrorEvent('error',{message:'Audit obsolete '+kind+' worker error'});
      for(const item of old.listeners)if(item.type==='error')typeof item.listener==='function'?item.listener.call(old.worker,error):item.listener.handleEvent(error);
      if(old.onerror)old.onerror.call(old.worker,error);
      record('late delivery',kind+' obsolete error handler invoked');
    });
    button('Record resources',()=>{performance.getEntriesByType('resource').filter(r=>!r.name.includes('/audit-')).forEach(r=>record('resource',r.name+' transfer '+r.transferSize));});
    button('Record timer counts',()=>record('timer counts',{pendingFrames:activeFrames.size,pendingTimeouts:activeTimeouts.size,activeIntervals:activeIntervals.size,created:{...timerTotals}}));
      button('Deny next full-screen request',()=>{denyFullscreen=true;record('fullscreen fault','next request denied');});
    button('Pause art clock now',()=>{frozen=nativeNow();record('clock','paused at current native time to preserve active animation state without a time jump');});
    button('Freeze art clock at 12345 ms',()=>{frozen=12345;record('clock','frozen at12345ms for main-window rAF and performance.now; worker inference unchanged');});
    button('Freeze art clock at 23456 ms',()=>{frozen=23456;record('clock','frozen at23456ms for main-window rAF and performance.now; worker inference unchanged');});
    button('Resume art clock',()=>{frozen=null;record('clock','normal main-window clock restored');});
    button('Measure canvas calls for five seconds',()=>{
      const start={...canvasCalls};record('canvas measurement','started; five seconds');
      setTimeout(()=>{const delta={};for(const [key,n] of Object.entries(canvasCalls))delta[key]=n-(start[key]||0);record('canvas measurement',JSON.stringify(delta));},5000);
    });
    button('Sample view after 3 and 6 seconds',()=>{for(const delay of [3000,6000])setTimeout(()=>{const canvas=document.getElementById('view'),data=canvas.getContext('2d').getImageData(0,0,canvas.width,canvas.height).data;let hash=2166136261,count=0;for(let i=0;i<data.length;i+=4){const x=(i/4)%canvas.width;for(let j=0;j<4;j++)hash=Math.imul(hash^data[i+j],16777619);if(data[i]!==255||data[i+1]!==255||data[i+2]!==255)count++;}record('view sample',{delay,hash:hash>>>0,nonwhite:count,excludedColumns:[]});},delay);record('view samples scheduled','3s and 6s; entire view');});
    button('Download audit log',()=>{const a=document.createElement('a');a.download='mouse-audit-fault-log.json';a.href=URL.createObjectURL(new Blob([JSON.stringify(events,null,2)],{type:'application/json'}));a.click();});
    panel.append(status);document.body.append(panel);
    if(lateMessages){
      // Keep the explicitly labelled harness reachable inside modal/workshop
      // isolation; this moves only our controls, never application controls.
      const place=()=>{const workshop=document.querySelector('#cadWorkshop');const host=document.querySelector('#cadWikiPreview[open]')||document.querySelector('#cadWiki[open]')||document.querySelector('#cadScriptStudio[open]')||(workshop&&!workshop.hidden?workshop:document.body);if(panel.parentElement!==host)host.append(panel);if(panel.inert)panel.inert=false;if(panel.hasAttribute('aria-hidden'))panel.removeAttribute('aria-hidden');};
      new MutationObserver(place).observe(document.body,{subtree:true,attributes:true,attributeFilter:['class','hidden','open','inert']});place();
    }
    record('ready','production bytes with explicit audit API wrappers; no app state injection');
  });
})();

