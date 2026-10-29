import { importStl } from './cad-stl';
import { readCadLayer, type CadBody, type CadScriptFile } from './cad-model';

export function renderOpenSCAD(source:string,entry='main.scad',files:CadScriptFile[]=[],signal?:AbortSignal):Promise<{body:CadBody;logs:string[]}>{
  return new Promise((resolve,reject)=>{
    let worker:Worker|undefined;
    const stop=()=>{clearTimeout(timer);worker?.terminate();signal?.removeEventListener('abort',abort);};
    const abort=()=>{stop();reject(new Error('OpenSCAD render cancelled.'));};
    const timer=setTimeout(()=>{stop();reject(new Error('OpenSCAD exceeded the five-minute render limit. Simplify the model or reduce $fn.'));},300000);
    try{
      // Validate imported project paths and sizes before they enter the virtual filesystem.
      const placeholder:CadBody={id:'script-check',name:'Script',color:'#efbf53',visible:true,locked:false,position:[0,0,0],rotation:[0,0,0],scale:[1,1,1],solid:{kind:'primitive',shape:'box',size:[1,1,1],wall:1},script:{language:'openscad',source,entry,files}};
      const script=readCadLayer({units:'mm',bodies:[placeholder]})!.bodies[0].script!;
      if(signal?.aborted){abort();return;}signal?.addEventListener('abort',abort,{once:true});
      worker=new Worker(new URL('openscad/worker.js',new URL(import.meta.env.BASE_URL,location.href)),{type:'module'});
      worker.onerror=event=>{stop();reject(new Error(event.message||'OpenSCAD engine failed to load.'));};
      worker.onmessage=({data})=>{stop();if(data.error){reject(new Error(data.error));return;}try{const body=importStl(data.bytes.buffer,'OpenSCAD model.stl','mm',true);body.script=script;resolve({body,logs:data.logs});}catch(error){reject(error);}};
      worker.postMessage({source:script.source,entry:script.entry,files:script.files});
    }catch(error){stop();reject(error);}
  });
}
