import { advancedEnabled } from './advanced-mode';
import { emit } from './bus';
import { editable, message, settle } from './editor';
import { download, exportCanvas } from './export';
import { icon } from './icons';
import { enhancementSize, SuperResolutionProcessor, type EnhancementScale } from './super-resolution';
import { EnhancementArea } from './super-resolution-area';

const field=<T extends HTMLElement=HTMLElement>(id:string)=>document.getElementById(id) as T;
export function initSuperResolution():void {
  const dialog=document.createElement('dialog');dialog.id='superResolutionDialog';dialog.setAttribute('aria-labelledby','superResolutionTitle');
  dialog.innerHTML=`<header class="enhance-heading"><strong id="superResolutionTitle">${icon('wand')} Super resolution</strong><button type="button" class="choice" id="enhanceClose" aria-label="Close super resolution">✕</button></header><p class="enhance-intro">Bring out detail in a larger copy. Your original and layers stay safe.</p><div class="enhance-settings"><div class="enhance-scales" aria-label="Enhancement scale"><button type="button" class="choice" data-enhance-scale="2" aria-pressed="true">2× <small>Twice the size</small></button><button type="button" class="choice" data-enhance-scale="4" aria-pressed="false">4× <small>Four times the size</small></button></div><output id="enhanceDimensions"></output><p class="hint">High-quality ESRGAN AI · processed on your device. First use loads a 29 MB model.</p></div><div class="enhance-view"><canvas id="enhancePreview" width="384" height="256" aria-label="Centre detail preview"></canvas><div class="enhance-compare"><button type="button" class="choice" id="enhanceBefore" aria-pressed="true">Before</button><button type="button" class="choice" id="enhanceAfter" aria-pressed="false" disabled>Enhanced</button></div></div><div class="enhance-feedback"><progress id="enhanceProgress" max="1" value="0" aria-label="Enhancement progress"></progress><output id="enhanceStatus" role="status" aria-live="polite">Preparing picture…</output></div><footer class="enhance-actions"><button type="button" class="choice" id="enhanceDetail">Preview detail</button><button type="button" class="choice" id="enhanceFull">Enhance whole image</button><button type="button" class="choice" id="enhanceSave" disabled>Save enhanced PNG</button></footer>`;
  document.body.append(dialog);
  field('enhancePreview').setAttribute('aria-label','Selected detail preview');
  const previewGrid=document.createElement('div');previewGrid.className='enhance-preview-grid';
  const view=dialog.querySelector<HTMLElement>('.enhance-view')!;view.before(previewGrid);
  const area=new EnhancementArea(()=>{detail=null;after=false;controls();paint();field('enhanceStatus').textContent='Area selected. Preview this detail or enhance the whole image.';});
  previewGrid.append(area.element,view);
  const processor=new SuperResolutionProcessor();
  let source:HTMLCanvasElement|null=null,full:Blob|null=null,detail:HTMLCanvasElement|null=null,scale:EnhancementScale=2,after=false,busy=false,revision=0;
  const region=()=>area.region;
  function paint():void {
    const canvas=field<HTMLCanvasElement>('enhancePreview'),ctx=canvas.getContext('2d')!;ctx.clearRect(0,0,canvas.width,canvas.height);if(!source)return;
    const r=region();canvas.width=r.width*scale;canvas.height=r.height*scale;
    ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';
    if(after&&detail)ctx.drawImage(detail,0,0);
    else ctx.drawImage(source,r.x,r.y,r.width,r.height,0,0,canvas.width,canvas.height);
    field('enhanceBefore').setAttribute('aria-pressed',String(!after));field('enhanceAfter').setAttribute('aria-pressed',String(after));
  }
  function controls():void {
    const available=!!source;
    let fullSizeAllowed=false;if(source){try{enhancementSize(source.width,source.height,scale);fullSizeAllowed=true;}catch{/* Keep the exact scale visible, never downsize silently. */}}
    for(const button of dialog.querySelectorAll<HTMLButtonElement>('[data-enhance-scale]')){
      let reason='';try{if(source)enhancementSize(source.width,source.height,Number(button.dataset.enhanceScale) as EnhancementScale);}catch(error){reason=(error as Error).message;}
      button.disabled=busy||!available||!!reason;button.title=reason;button.setAttribute('aria-pressed',String(Number(button.dataset.enhanceScale)===scale));
    }
    for(const id of ['enhanceDetail','enhanceFull'])field<HTMLButtonElement>(id).disabled=busy||!available;
    field<HTMLButtonElement>('enhanceFull').disabled=busy||!available||!fullSizeAllowed;
    field<HTMLButtonElement>('enhanceAfter').disabled=!detail;
    area.element.inert=busy;
    field<HTMLButtonElement>('enhanceSave').disabled=busy||!full;
    field<HTMLButtonElement>('enhanceClose').setAttribute('aria-label',busy?'Cancel enhancement':'Close super resolution');
    field('enhanceDimensions').textContent=source?`${source.width} × ${source.height} → ${source.width*scale} × ${source.height*scale} pixels`:'';
  }
  const close=()=>{revision++;processor.dispose();dialog.close();source=detail=null;full=null;area.setSource(null);busy=false;};
  field('enhanceClose').addEventListener('click',close);
  dialog.addEventListener('cancel',event=>{event.preventDefault();close();});
  for(const button of dialog.querySelectorAll<HTMLButtonElement>('[data-enhance-scale]'))button.addEventListener('click',()=>{
    scale=Number(button.dataset.enhanceScale) as EnhancementScale;full=null;detail=null;after=false;field<HTMLProgressElement>('enhanceProgress').value=0;field('enhanceStatus').textContent='Choose an area to preview, or enhance the whole picture.';controls();paint();
  });
  field('enhanceBefore').addEventListener('click',()=>{after=false;paint();});
  field('enhanceAfter').addEventListener('click',()=>{after=true;paint();});
  async function run(entire:boolean):Promise<void> {
    if(!source||busy)return;
    const token=++revision;busy=true;controls();field('enhanceStatus').textContent='Starting AI enhancement…';field<HTMLProgressElement>('enhanceProgress').value=0;
    try{
      const r=region(),ctx=source.getContext('2d')!,input=entire?ctx.getImageData(0,0,source.width,source.height):ctx.getImageData(r.x,r.y,r.width,r.height);
      const progress=(value:{message:string;fraction:number})=>{if(token!==revision)return;field('enhanceStatus').textContent=value.message;field<HTMLProgressElement>('enhanceProgress').value=value.fraction;};
      const response=entire?await processor.processPng(input,scale,r,progress):await processor.process(input,scale,progress);
      if(token!==revision)return;
      const result=response instanceof ImageData?response:response.preview;if(!(response instanceof ImageData))full=response.png;
      const canvas=document.createElement('canvas');canvas.width=result.width;canvas.height=result.height;canvas.getContext('2d')!.putImageData(result,0,0);
      detail=canvas;after=true;paint();field('enhanceStatus').textContent=entire?'Enhanced copy ready. Compare the detail, then save your PNG.':'Selected detail ready. Enhance the whole image when you’re happy.';
    }catch(error){if(token===revision)field('enhanceStatus').textContent=error instanceof Error?error.message:String(error);}
    finally{if(token===revision){busy=false;controls();}}
  }
  field('enhanceDetail').addEventListener('click',()=>void run(false));field('enhanceFull').addEventListener('click',()=>void run(true));
  field('enhanceSave').addEventListener('click',()=>{
    const result=full,savedScale=scale;if(!result)return;
    const filename=(field<HTMLInputElement>('fileName').value||'retropaint').replace(/[<>:"/\\|?*]/g,'-').replace(/\.[^.]+$/,'');
    download(result,`${filename}-${savedScale}x-enhanced.png`);message('Enhanced copy saved. Your editable original is still here.');
  });
  field('openSuperResolution').addEventListener('click',()=>{
    if(!advancedEnabled()||!editable())return;settle();emit('close-options');source=detail=null;full=null;area.setSource(null);after=false;busy=true;const token=++revision;
    field('enhanceStatus').textContent='Preparing picture…';field<HTMLProgressElement>('enhanceProgress').value=0;controls();dialog.showModal();
    void exportCanvas().then(canvas=>{
      if(token!==revision)return;source=canvas;area.setSource(canvas);scale=2;enhancementSize(canvas.width,canvas.height,scale);field('enhanceStatus').textContent='Move the yellow box onto detail, then preview or enhance the whole image.';paint();
    }).catch(error=>{if(token===revision)field('enhanceStatus').textContent=error instanceof Error?error.message:String(error);}).finally(()=>{if(token===revision){busy=false;controls();}});
  });
}
