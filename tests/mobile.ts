import markup from '../index.html?raw';
const testSize = new URLSearchParams(location.search).get('frame');
if (testSize && window.top === window.self) {
  const [width, height] = testSize.split('x').map(Number);
  const iframe = document.createElement('iframe'); iframe.title = `RetroPaint ${width} × ${height} preview`;
  iframe.width = String(width); iframe.height = String(height); iframe.style.cssText = 'border:0;display:block;margin:20px auto;background:white';
  iframe.src = new URLSearchParams(location.search).has('preview') ? '../index.html?layout-preview' : new URLSearchParams(location.search).has('cad-only') ? './mobile.html?cad-only' : './mobile.html';
  document.body.style.cssText = 'margin:0;background:#dceee5'; document.body.append(iframe);
} else {
const parsed = new DOMParser().parseFromString(markup, 'text/html');
parsed.querySelectorAll('script').forEach(script => script.remove());
document.body.replaceChildren(...Array.from(parsed.body.childNodes));
function reportUnexpected(error:unknown):void {const output=document.getElementById('mobileUnexpected')??document.createElement('pre');output.id='mobileUnexpected';output.style.cssText='position:fixed;inset:8px;z-index:1000;background:#fff5ed;color:#8b3422;padding:12px;white-space:pre-wrap;overflow:auto';output.textContent=(output.textContent??'')+(error instanceof Error?error.stack??error.message:String(error))+'\n';document.body.append(output);}
window.addEventListener('error',event=>reportUnexpected(event.error??event.message));window.addEventListener('unhandledrejection',event=>reportUnexpected(event.reason));
await import('../src/main');
const { base, baseCtx, view, eventPos } = await import('../src/canvas');
const { state } = await import('../src/state');
const { bakeStaticStrokes } = await import('../src/live');
const { activeLayer, layers, resetLayers } = await import('../src/layers');
const { undo, redo } = await import('../src/history');
const photoModule = await import('../src/photo-session');
const { setAdvancedMode } = await import('../src/advanced-mode');
const results: string[] = [];
const frame = () => new Promise<void>(resolve => requestAnimationFrame(() => requestAnimationFrame(() => resolve())));
function assert(value: unknown, message: string): asserts value { if (!value) throw new Error(message); }
const el = (selector: string) => document.querySelector<HTMLElement>(selector)!;
const click = (selector: string) => el(selector).click();
function fits(element: HTMLElement, label: string) {
  const r = element.getBoundingClientRect();
  assert(r.left >= -1 && r.top >= -1 && r.right <= innerWidth+1 && r.bottom <= innerHeight+1, `${label} leaves viewport: ${JSON.stringify(r)}`);
  assert(element.scrollWidth <= element.clientWidth+1, `${label} overflows horizontally`);
}
async function run(name: string, fn: () => void | Promise<void>) {
  if(new URLSearchParams(location.search).has('cad-only')&&!name.startsWith('CAD '))return;
  document.body.dataset.currentCheck=name;
  try { await fn(); results.push('PASS '+name); }
  catch (error) { results.push('FAIL '+name+': '+String(error)); }
}
await frame();
await run('Toolbar and all twelve tools fit without overlap', () => {
  fits(el('#topBar'), 'Toolbar'); fits(el('#toolBin'),'Tools'); fits(el('#stage'),'Paper');
  const buttons = [...document.querySelectorAll<HTMLElement>('#topBar>*')];
  for (const [i,a] of buttons.entries()) for (const b of buttons.slice(i+1)) {
    const ar=a.getBoundingClientRect(),br=b.getBoundingClientRect();
    assert(Math.min(ar.right,br.right)-Math.max(ar.left,br.left)<1 || Math.min(ar.bottom,br.bottom)-Math.max(ar.top,br.top)<1,'Toolbar controls overlap');
  }
  for (const button of document.querySelectorAll<HTMLElement>('.tool-btn')) {
    if(!button.getClientRects().length)continue;
    fits(button,button.textContent!);
    assert(button.getBoundingClientRect().height>=44,'Tool is too short to tap');
  }
});
await run('Fitted paper sits at the bottom of its drawing space', () => {
  const paper=el('#stage').getBoundingClientRect(),slot=el('#canvasSlot').getBoundingClientRect();
  assert(Math.abs(paper.bottom-slot.bottom)<2,'Paper is still vertically centred');
});
await run('Tool menus fit and keep most of the picture visible', async () => {
  for (const tool of ['draw','shapes','spray','scissors','eraser','stamp','spiro']) {
    const paper=el('#stage').getBoundingClientRect().toJSON();
    click(`[data-tool="${tool}"]`); await frame();
    const drawer=el('.drawer.open'); fits(drawer,tool);
    assert(JSON.stringify(paper)===JSON.stringify(el('#stage').getBoundingClientRect().toJSON()),'Tool menu moved paper');
    const d=drawer.getBoundingClientRect();
    const covered=Math.max(0,Math.min(d.right,paper.right)-Math.max(d.left,paper.left))*Math.max(0,Math.min(d.bottom,paper.bottom)-Math.max(d.top,paper.top));
    assert(covered/(paper.width*paper.height)<0.5, `${tool} hides most of the picture`);
    assert(drawer.scrollHeight<=drawer.clientHeight+1, `${tool} scrolls vertically`);
    for(const button of drawer.querySelectorAll<HTMLElement>('button')) {
      if (!button.getClientRects().length) continue;
      fits(button,button.textContent!);
      assert(button.getBoundingClientRect().height>=43.5,`${tool}: ${button.textContent} too short`);
    }
    click('.drawer.open .drawer-close');
  }
  click('#symBtn'); await frame(); fits(el('.drawer.open'),'Symmetry'); click('.drawer.open .drawer-close');
});
await run('Stamp and Spiro settings remain accessible in compact panels', async () => {
  for(const tool of ['stamp','spiro']) {
    click(`[data-tool="${tool}"]`); click('.drawer.open .drawer-settings'); await frame();
    const drawer=el('.drawer.open'); fits(drawer,`${tool} settings`);
    assert(el(tool==='stamp'?'#stampScale':'#outerTeeth').getClientRects().length,'Settings did not open');
    click('.drawer.open .drawer-settings'); await frame();
    assert(el(tool==='stamp'?'#stampGrid':'#gearBox').getClientRects().length,'Chooser did not return');
    click('.drawer.open .drawer-close');
  }
});
await run('Tool choices also leave most of the zoomed drawing space visible', async () => {
  click('[aria-label="Zoom in"]'); click('[aria-label="Zoom in"]'); await frame();
  const slot=el('#canvasSlot').getBoundingClientRect(),paper=el('#view').getBoundingClientRect();
  const visible={left:Math.max(slot.left,paper.left),right:Math.min(slot.right,paper.right),top:Math.max(slot.top,paper.top),bottom:Math.min(slot.bottom,paper.bottom)};
  for(const tool of ['draw','shapes','spray','scissors','eraser','stamp','spiro']) {
    click(`[data-tool="${tool}"]`); await frame();
    const d=el('.drawer.open').getBoundingClientRect();
    const covered=Math.max(0,Math.min(d.right,visible.right)-Math.max(d.left,visible.left))*Math.max(0,Math.min(d.bottom,visible.bottom)-Math.max(d.top,visible.top));
    assert(covered/((visible.right-visible.left)*(visible.bottom-visible.top))<0.5,`${tool} covers most of the zoomed paper`);
    click('.drawer.open .drawer-close');
  }
  click('[aria-label="Fit whole picture"]');
});
await run('All palette tabs fit and opening them does not move paper', async () => {
  click('[data-tool="bucket"]');
  const before=el('#view').getBoundingClientRect().toJSON();
  click('#paletteToggle'); await frame();
  for (const id of ['tray-solids','tray-textures','tray-live','tray-gradients']) {
    click(`[data-target="${id}"]`); await frame(); fits(el('#trayContents'),id);
    for(const button of el('#'+id).querySelectorAll<HTMLElement>('button')) fits(button,button.textContent!);
  }
  assert(JSON.stringify(before)===JSON.stringify(el('#view').getBoundingClientRect().toJSON()),'Palette moved paper');
  click('#paletteToggle');
});
await run('Text, colour picker and every toolbox panel fit the viewport', async () => {
  for (const tool of ['text', 'picker']) {
    click(`[data-tool="${tool}"]`); await frame(); fits(el('.drawer.open'), tool); click('.drawer.open .drawer-close');
  }
  click('#studioBtn');
  for (const tab of ['file', 'image', 'layers', 'view']) {
    click(`[data-studio="${tab}"]`); await frame(); fits(el('#studioDrawer'), tab + ' toolbox');
    for (const field of el('#studioDrawer').querySelectorAll<HTMLElement>('button,input,select')) if (field.getClientRects().length) {
      const bounds = field.getBoundingClientRect();
      if (bounds.top < 0 || bounds.bottom > innerHeight) { field.scrollIntoView({ block: 'nearest' }); await frame(); }
      fits(field, field.textContent || field.id);
    }
  }
  click('.drawer.open .drawer-close');
});
await run('Colour wheel and exact colour controls remain usable on small screens', async () => {
  click('#paletteToggle'); click('[data-target="tray-solids"]'); click('#colourWheelBtn'); await frame();
  fits(el('#colourWheelDialog'), 'Colour dialog');
  for (const field of el('#colourWheelDialog').querySelectorAll<HTMLElement>('input,button')) fits(field, field.id || field.textContent!);
  const hex = el('#wheelHex') as HTMLInputElement; hex.value = '#123456'; hex.dispatchEvent(new Event('input', { bubbles: true }));
  click('.wheel-use'); assert(state.ink === '#123456', 'Exact colour did not apply'); click('#paletteToggle');
});
await run('Zoom and pan preserve artwork and keep drawing coordinates accurate', async () => {
  click('[data-tool="draw"]'); click('.drawer.open .drawer-close');
  state.ink='#E53935'; state.liveArmed=false;
  baseCtx.fillStyle='#118AB2'; baseCtx.fillRect(200,200,50,50);
  const before=base.toDataURL();
  click('[aria-label="Zoom in"]'); click('[aria-label="Zoom in"]');
  click('[aria-label="Move paper"]'); await frame();
  const capture=view.setPointerCapture; view.setPointerCapture=()=>{};
  try {
    const r=el('#canvasSlot').getBoundingClientRect();
    const send=(type:string,x:number,y:number)=>view.dispatchEvent(new PointerEvent(type,{pointerId:8,pointerType:'touch',button:0,clientX:x,clientY:y}));
    send('pointerdown',r.x+r.width/2,r.y+r.height/2);
    send('pointermove',r.x+r.width/2+50,r.y+r.height/2+20);
    send('pointerup',r.x+r.width/2+50,r.y+r.height/2+20);
    assert(base.toDataURL()===before,'Panning painted on picture');
    click('[aria-label="Move paper"]');
    const x=r.x+r.width/2,y=r.y+r.height/2;
    const p=eventPos({clientX:x,clientY:y});
    send('pointerdown',x,y); send('pointerup',x,y); bakeStaticStrokes(baseCtx);
    const pixel=baseCtx.getImageData(Math.round(p.x),Math.round(p.y),1,1).data;
    assert(pixel[0]===229 && pixel[1]===57,'Zoomed drawing missed the touched point');
    const painted=base.toDataURL(); click('[aria-label="Fit whole picture"]');
    assert(base.toDataURL()===painted,'Fitting changed artwork');
  } finally { view.setPointerCapture=capture; }
});
await run('Layers are easy to add, choose, hide and rename without covering the paper afterwards', async () => {
  setAdvancedMode(true);await frame();
  resetLayers(960, 640);
  const paper = activeLayer(), original = paper.canvas.toDataURL();
  click('#layersToggle'); await frame(); fits(el('#layersPanel'), 'Layer stack'); fits(el('#addLayer'), 'New layer');
  click('#addLayer'); await frame();
  assert(layers.length === 2 && activeLayer().paper === null, 'New sheet is not transparent');
  assert(el('#layersPanel').hidden, 'Stack did not close to allow painting');
  assert(paper.canvas.toDataURL() === original, 'Adding a layer changed the picture below');
  const ink = activeLayer().id;
  click('#layersToggle'); click('#addLayer'); await frame();
  assert(activeLayer().name === 'Layer 2', 'New layers do not have friendly names');
  click('#layersToggle'); click(`[data-layer-id="${ink}"] .layer-pick`); await frame();
  assert(activeLayer().id === ink && el('#layersPanel').hidden, 'Choosing a sheet did not return to drawing');
  click('#layersToggle');
  assert(el(`[data-layer-id="${ink}"] .layer-state`).textContent === 'Painting here', 'Selected layer is unclear');
  click(`[data-layer-id="${ink}"] .layer-eye`);
  assert(!activeLayer().visible && el(`[data-layer-id="${ink}"] .layer-state`).textContent === 'Hidden', 'Eye did not hide the layer');
  undo(); assert(activeLayer().visible, 'Undo did not restore visibility');
  click('#layerOptions > summary'); await frame(); fits(el('#layersPanel'), 'Layer options');
  for (const control of el('#layerOptions').querySelectorAll<HTMLElement>('input,button')) fits(control, control.id);
  assert(el('#layersPanel').scrollHeight <= el('#layersPanel').clientHeight + 1, 'Layer options require scrolling');
  const name = el('#layerName') as HTMLInputElement;
  name.focus(); name.value = 'My doodles'; name.dispatchEvent(new KeyboardEvent('keydown', { key:'Enter', bubbles:true }));
  assert(activeLayer().name === 'My doodles' && el('#activeLayerName').textContent === 'My doodles', 'Rename did not update the stack');
  const opacity = el('#layerOpacity') as HTMLInputElement; opacity.focus();
  for (const value of ['0.8','0.45']) { opacity.value = value; opacity.dispatchEvent(new Event('input', { bubbles: true })); }
  opacity.dispatchEvent(new Event('change', { bubbles: true }));
  assert(activeLayer().opacity === 0.45, 'Opacity did not preview');
  opacity.dispatchEvent(new KeyboardEvent('keydown', { key:'z', ctrlKey:true, bubbles:true }));
  assert(Number(activeLayer().opacity) === 1 && opacity.value === '1', 'Undo did not restore the entire opacity gesture while slider was focused');
  redo(); assert(activeLayer().opacity === 0.45, 'Redo did not restore opacity'); opacity.blur();
  click('#deleteLayer'); assert(layers.length === 2, 'Remove did not remove the sheet');
  undo(); assert(Number(layers.length) === 3 && activeLayer().id === ink && activeLayer().name === 'My doodles' && activeLayer().opacity === 0.45, 'Undo lost removed sheet settings');
  click('#layerOptions > summary'); await frame();
});
await run('Layer drag handles and keyboard moves reorder sheets and support Undo', async () => {
  const panel = el('#layersPanel'), before = layers.map(layer => layer.id).join(','), active = activeLayer().id;
  const grip = el(`[data-layer-id="${active}"] .layer-grip`), first = el('#layerList .layer-row');
  const capture = panel.setPointerCapture; panel.setPointerCapture = () => {};
  try {
    const from = grip.getBoundingClientRect(), to = first.getBoundingClientRect();
    grip.dispatchEvent(new PointerEvent('pointerdown', { bubbles:true, pointerId:14, button:0, clientX:from.x+10, clientY:from.y+20 }));
    panel.dispatchEvent(new PointerEvent('pointermove', { pointerId:14, clientX:to.x+20, clientY:to.y+4 }));
    panel.dispatchEvent(new PointerEvent('pointerup', { pointerId:14, clientX:to.x+20, clientY:to.y+4 }));
    assert(layers.at(-1)!.id === active, 'Dragging did not move sheet to the top');
    undo(); assert(layers.map(layer => layer.id).join(',') === before, 'Undo did not restore order');
    const keyboardGrip = el(`[data-layer-id="${active}"] .layer-grip`); keyboardGrip.focus();
    keyboardGrip.dispatchEvent(new KeyboardEvent('keydown', { key:'ArrowDown', altKey:true, bubbles:true }));
    assert(layers[0].id === active, 'Keyboard move did not lower sheet');
    assert(document.activeElement === keyboardGrip, 'Reordering lost keyboard focus');
    undo(); assert(layers.map(layer => layer.id).join(',') === before, 'Undo did not restore keyboard move');
  } finally { panel.setPointerCapture = capture; }
  click('#closeLayers'); resetLayers(960, 640);
});
await run('Every Photo lab category fits, including crop, curves and lens controls, without scrolling', async()=>{
  resetLayers(960,640);click('#layersToggle');await frame();const layerWidth=el('#layersPanel').getBoundingClientRect().width;click('#photoToggle');await frame();
  assert(Math.abs(el('#photoPanel').getBoundingClientRect().width-layerWidth)<1,'Photo lab is wider than the Layers palette');
  fits(el('#photoPanel'),'Photo lab');
  for(const category of ['light','colour','curves','detail','effects','geometry']){
    click(`[data-photo-category="${category}"]`);
    const select=el('#photoGroup') as HTMLSelectElement;
    for(const option of [...select.options]){
      if(option.parentElement instanceof HTMLOptGroupElement&&option.parentElement.label.toLowerCase()!==category)continue;
      select.value=option.value;select.dispatchEvent(new Event('change',{bubbles:true}));await frame();
      const panel=el('#photoPanel');fits(panel,option.text);
      assert(panel.scrollHeight<=panel.clientHeight+1,option.text+' requires scrolling');
      for(const control of panel.querySelectorAll<HTMLElement>('button,input,select,canvas'))if(control.getClientRects().length)fits(control,control.getAttribute('aria-label')||control.id||control.textContent!);
    }
  }
  assert([...el('#toolBin').querySelectorAll<HTMLButtonElement>('[data-tool],#symBtn')].every(button=>button.disabled),'Drawing tools can mutate a pending photo preview');click('#photoCancel');
  assert([...el('#toolBin').querySelectorAll<HTMLButtonElement>('[data-tool],#symBtn')].every(button=>!button.disabled)&&!photoModule.photoSession,'Cancel did not release drawing tools');
  click('#closeLayers');
});
await run('Photo sliders preview reversibly, curve points are editable and crop can be dragged',async()=>{
  const photoCanvas=activeLayer().canvas,photoCtx=photoCanvas.getContext('2d')!;photoCtx.fillStyle='#778899';photoCtx.fillRect(0,0,960,640);const before=photoCanvas.toDataURL();click('#photoToggle');
  click('[data-photo-category="light"]');
  const brightness=el('[data-photo-value="brightness"]') as HTMLInputElement;brightness.value='30';brightness.dispatchEvent(new Event('input',{bubbles:true}));await photoModule.refreshPhoto();
  assert(photoCanvas.toDataURL()===before,'Preview painted into the source');click('#photoCompare');assert(photoModule.photoSession?.compare,'Before comparison did not engage');click('#photoCompare');
  click('[data-photo-category="curves"]');await frame();
  const curve=el('#photoCurve') as HTMLCanvasElement,capture=curve.setPointerCapture;curve.setPointerCapture=()=>{};
  try{const r=curve.getBoundingClientRect();curve.dispatchEvent(new PointerEvent('pointerdown',{pointerId:19,button:0,clientX:r.x+r.width*.5,clientY:r.y+r.height*.3}));curve.dispatchEvent(new PointerEvent('pointerup',{pointerId:19}));assert(photoModule.photoSession!.settings.curves.rgb.length===3,'Tap did not add a curve point');
    const output=el('#curve-y') as HTMLInputElement;output.value='190';output.dispatchEvent(new Event('change',{bubbles:true}));assert(Math.round(photoModule.photoSession!.settings.curves.rgb[1].y*255)===190,'Exact curve output did not update');
  }finally{curve.setPointerCapture=capture;}
  click('[data-photo-category="geometry"]');await frame();
  const viewCapture=view.setPointerCapture;view.setPointerCapture=()=>{};
  try{const r=view.getBoundingClientRect(),send=(type:string,x:number,y:number)=>view.dispatchEvent(new PointerEvent(type,{pointerId:20,button:0,clientX:r.x+r.width*x,clientY:r.y+r.height*y}));
    send('pointerdown',.2,.2);send('pointermove',.8,.8);send('pointerup',.8,.8);assert(Math.abs(photoModule.photoSession!.settings.crop.width-.6)<.01,'Dragging did not set the crop');
  }finally{view.setPointerCapture=viewCapture;}
  const mini=el('#photoMiniCanvas') as HTMLCanvasElement;
  if(mini.getClientRects().length){
    click('#photoCropReset');const miniCapture=mini.setPointerCapture;mini.setPointerCapture=()=>{};
    try{const r=mini.getBoundingClientRect(),scale=Math.min(r.width/960,r.height/640),left=r.x+(r.width-960*scale)/2,top=r.y+(r.height-640*scale)/2,send=(type:string,x:number,y:number)=>mini.dispatchEvent(new PointerEvent(type,{pointerId:21,button:0,clientX:left+960*scale*x,clientY:top+640*scale*y}));
      send('pointerdown',.25,.25);send('pointermove',.75,.75);send('pointerup',.75,.75);assert(Math.abs(photoModule.photoSession!.settings.crop.width-.5)<.01,'Phone preview crop did not follow the image coordinates');
    }finally{mini.setPointerCapture=miniCapture;}
  }
  click('#photoReset');assert(photoModule.photoSession!.settings.brightness===0&&photoModule.photoSession!.settings.curves.rgb.length===2&&photoModule.photoSession!.settings.crop.width===1,'Reset did not clear every category');
  click('#photoCancel');assert(photoCanvas.toDataURL()===before,'Cancel changed the image');
});
await run('Look selection is persistent, Normal restores the pre-look image and manual changes show Custom across tabs',async()=>{
  click('#photoToggle');click('[data-photo-category="light"]');
  const set=(key:string,value:string)=>{const input=el(`[data-photo-value="${key}"]`) as HTMLInputElement;input.value=value;input.dispatchEvent(new Event('input',{bubbles:true}));};
  const look=el('#photoLook') as HTMLSelectElement,choose=(value:string)=>{look.value=value;look.dispatchEvent(new Event('change',{bubbles:true}));};
  set('brightness','17');assert(look.value==='custom','Manual adjustment is not Custom');
  choose('warm');choose('mono');assert(photoModule.photoSession!.settings.temperature===0&&photoModule.photoSession!.settings.grain===0,'Looks accumulated');
  click('[data-photo-category="colour"]');assert(look.value==='mono'&&el('#photoLook')===look,'Navigation lost the selected look');
  const tint=el('[data-photo-value="tint"]') as HTMLInputElement;tint.value='12';tint.dispatchEvent(new Event('input',{bubbles:true}));assert(look.value==='custom','Colour tweak did not mark Custom');
  choose('normal');assert(photoModule.photoSession!.settings.brightness===17&&photoModule.photoSession!.settings.tint===0&&photoModule.photoSession!.settings.saturation===0,'Normal did not restore the pre-look settings');
  await photoModule.applyPhoto();click('#photoToggle');assert(photoModule.photoSession!.settings.brightness===17&&look===el('#photoLook'),'Reopening lost saved controls');click('#photoCancel');
});
await run('Launching restores panel context and file-picker cancellation keeps the draft; a new photo opens directly in Photo lab',async()=>{
  click('#photoToggle');click('[data-photo-category="detail"]');const pop=el('[data-photo-value="pop"]') as HTMLInputElement;pop.value='20';pop.dispatchEvent(new Event('input',{bubbles:true}));
  const input=el('#imageInput') as HTMLInputElement,originalClick=input.click;input.click=()=>{};
  try{
    click('#photoOpen');input.dispatchEvent(new Event('cancel'));assert(photoModule.photoSession?.settings.pop===20&&!el('#photoPanel').hidden,'Cancelling a file picker lost the draft');
    click('#photoOpen');const fixture=document.createElement('canvas');fixture.width=32;fixture.height=24;fixture.getContext('2d')!.fillRect(0,0,32,24);const blob=await new Promise<Blob>(resolve=>fixture.toBlob(value=>resolve(value!)));
    await (await import('../src/editor')).importImage(blob);assert(photoModule.photoSession?.settings.pop===0&&!el('#photoPanel').hidden,'Imported photo did not reopen the lab with fresh settings');
  }finally{input.click=originalClick;click('#photoCancel');resetLayers(960,640);}
});
await run('Photo crop keeps source dimensions and preserves accurate drawing coordinates in the visible frame',async()=>{
  const framing=await import('../src/document-frame');click('#photoToggle');photoModule.photoSession!.settings.crop={x:.25,y:.25,width:.5,height:.5};await photoModule.applyPhoto();await frame();
  const stage=el('#stage').getBoundingClientRect(),point=eventPos({clientX:stage.x+stage.width/2,clientY:stage.y+stage.height/2});
  assert(Math.abs(point.x-480)<3&&Math.abs(point.y-320)<3,'Crop shifted canvas coordinates');assert(activeLayer().canvas.width===960&&framing.outputFrame(960,640).width===480,'Crop removed source margins');
  click('#photoToggle');click('#photoReset');await photoModule.applyPhoto();await frame();assert(framing.outputFrame(960,640).width===960,'Reset did not restore the full frame');
});
await run('Advanced mode owns the palette buttons, preserves saved work and remains usable while Photo lab is open',async()=>{
  resetLayers(960,640);setAdvancedMode(true);await frame();
  assert(el('#toolBin').contains(el('#layersToggle'))&&el('#toolBin').contains(el('#photoToggle')),'Advanced buttons are outside the tool palette');
  for(const button of document.querySelectorAll<HTMLElement>('#toolBin .tool-btn')){fits(button,'Advanced palette');assert(button.getBoundingClientRect().height>=43.5,'Advanced tool is too short');}
  click('#photoToggle');assert(!el('#photoPanel').hidden&&!el('#photoToggle').hasAttribute('disabled'),'Photo toggle cannot close its own panel');
  const draft=photoModule.photoSession!;draft.settings.brightness=12;await photoModule.applyPhoto();
  const original=activeLayer().canvas.toDataURL(),recipe=JSON.stringify(activeLayer().photo);
  click('#photoToggle');click('#studioBtn');await frame();assert(el('#studioDrawer').classList.contains('open'),'More is unavailable in Photo lab');
  const advanced=el('#advancedMode') as HTMLInputElement;advanced.checked=false;advanced.dispatchEvent(new Event('change',{bubbles:true}));await frame();
  assert(el('#photoPanel').hidden&&el('#layersPanel').hidden&&el('#layersToggle').hidden&&el('#photoToggle').hidden,'Turning off Advanced left a panel or button visible');
  assert(activeLayer().canvas.toDataURL()===original&&JSON.stringify(activeLayer().photo)===recipe,'Turning off Advanced changed saved artwork');
  setAdvancedMode(true);click('#studioBtn');click('#photoToggle');assert(photoModule.photoSession?.settings.brightness===12,'Enabling Advanced lost saved controls');click('#photoToggle');assert(el('#photoPanel').hidden,'Palette button did not turn off Photo lab');
});
await run('Super resolution offers both exact scales and a responsive, cancellable copy preview',async()=>{
  resetLayers(32,24);click('#studioBtn');click('[data-studio="layers"]');click('#openSuperResolution');await frame();await frame();
  const dialog=el('#superResolutionDialog') as HTMLDialogElement;assert(dialog.open,'Enhancement did not open');fits(dialog,'Super resolution');assert(dialog.scrollHeight<=dialog.clientHeight+1,'Super resolution scrolls');
  assert(el('#enhanceDimensions').textContent!.includes('64 × 48'),'2× output size is wrong');click('[data-enhance-scale="4"]');assert(el('#enhanceDimensions').textContent!.includes('128 × 96'),'4× output size is wrong');
  for(const button of dialog.querySelectorAll<HTMLElement>('button'))fits(button,'Enhancement control');
  const before=activeLayer().canvas.toDataURL();click('#enhanceDetail');assert((el('#enhanceFull') as HTMLButtonElement).disabled,'Full enhancement could start during preview');click('#enhanceClose');
  assert(!dialog.open&&activeLayer().canvas.toDataURL()===before,'Cancelling enhancement changed the original');resetLayers(960,640);
});
await run('Enhancement preview areas are selectable and normal large photos can enhance the whole image',async()=>{
  resetLayers(2048,1536);const sample=activeLayer().canvas.getContext('2d')!;sample.fillStyle='#99ddff';sample.fillRect(0,0,2048,1536);sample.fillStyle='#754522';sample.fillRect(1536,0,512,1536);click('#openSuperResolution');await frame();await frame();
  assert(!(el('#enhanceFull') as HTMLButtonElement).disabled,'2× enhancement is silently blocked for a normal photo');click('[data-enhance-scale="4"]');assert(!(el('#enhanceFull') as HTMLButtonElement).disabled,'4× enhancement is silently blocked');
  const area=el('#enhanceArea') as HTMLCanvasElement,before=area.dataset.region!,capture=area.setPointerCapture;area.setPointerCapture=()=>{};
  try{const r=area.getBoundingClientRect();area.dispatchEvent(new PointerEvent('pointerdown',{pointerId:29,button:0,clientX:r.x+r.width*.8,clientY:r.y+r.height*.3}));area.dispatchEvent(new PointerEvent('pointerup',{pointerId:29}));assert(area.dataset.region!==before,'Clicking the photo did not select a different preview area');
    const parts=area.dataset.region!.split(',').map(Number);assert(parts[0]>1000&&parts[1]<768,'Preview did not move to the chosen detail');
    const detail=el('#enhancePreview') as HTMLCanvasElement,pixel=detail.getContext('2d')!.getImageData(detail.width/2,detail.height/2,1,1).data;assert(pixel[0]===117&&pixel[1]===69&&pixel[2]===34,'Selected preview still shows the centre sky instead of the chosen detail');
    area.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowLeft',bubbles:true}));assert(Number(area.dataset.region!.split(',')[0])<parts[0],'Preview area cannot be moved with the keyboard');
  }finally{area.setPointerCapture=capture;click('#enhanceClose');resetLayers(960,640);}
});
await run('Advanced mode keeps the original tool dimensions unchanged',async()=>{
  setAdvancedMode(false);await frame();const before=[...document.querySelectorAll<HTMLElement>('#toolBin [data-tool]')].map(b=>b.getBoundingClientRect());setAdvancedMode(true);await frame();
  const after=[...document.querySelectorAll<HTMLElement>('#toolBin [data-tool]')].map(b=>b.getBoundingClientRect());assert(before.every((b,i)=>Math.abs(b.width-after[i].width)<.5&&Math.abs(b.height-after[i].height)<.5),'Advanced mode stretches the original buttons');
});
await run('Vector mode and exact piece controls fit the viewport and preserve artwork across mode switches',async()=>{
  resetLayers(960,640);click('#studioBtn');const mode=el('#drawingMode') as HTMLSelectElement;mode.value='vector';mode.dispatchEvent(new Event('change'));click('#studioBtn');
  const objects=await import('../src/objects');state.shapeFill='primary';state.shapeOutline='none';objects.addVectorShape('rect',200,200,500,400);const id=objects.selectedObjects()[0].id;click('[data-tool="scissors"]');await frame();fits(el('#selectionDrawer'),'Piece controls');assert(el('#objectPanel').getBoundingClientRect().height>0,'Piece controls are missing');
  click('#objectPanel summary');await frame();fits(el('#selectionDrawer'),'Exact size controls');assert(el('#selectionDrawer').scrollHeight<=el('#selectionDrawer').clientHeight+1,'Exact piece controls scroll');
  for(const tab of el('#objectPanel').querySelectorAll<HTMLButtonElement>('[data-object-tab]')){tab.click();await frame();fits(el('#selectionDrawer'),`${tab.textContent} controls`);assert(el('#selectionDrawer').scrollHeight<=el('#selectionDrawer').clientHeight+1,`${tab.textContent} controls scroll`);}
  click('[data-object-tab="position"]');(el('#objectX') as HTMLInputElement).value='-250';(el('#objectY') as HTMLInputElement).value='-50';click('#objectPosition');assert(objects.objectSelectionBounds()!.x===-250&&objects.objectSelectionBounds()!.y===-50,'Exact position clamps to the canvas');click('[data-object-tab="size"]');
  (el('#objectWidth') as HTMLInputElement).value='1800';(el('#objectHeight') as HTMLInputElement).value='1200';click('#objectResize');assert(objects.objectSelectionBounds()!.width===1800,'Exact size was not applied');objects.setDrawingMode('raster');assert(activeLayer().objects?.some(o=>o.id===id),'Switching to raster flattened the artwork');resetLayers(960,640);state.drawingMode='raster';
});
await run('Sound and desk preferences fit without scrolling and mute controls stay in sync',async()=>{
  const audio=await import('../src/audio'),before=audio.audioSettings(),raw=sessionStorage.getItem('retropaint-sound');
  try{
    click('#studioBtn');click('[data-studio="view"]');click('#openPreferences');await frame();const dialog=el('#preferencesDialog') as HTMLDialogElement;assert(dialog.open,'Preferences did not open');fits(dialog,'Sound preferences');assert(dialog.scrollHeight<=dialog.clientHeight+1,'Sound preferences scroll');
    for(const button of dialog.querySelectorAll<HTMLElement>('button'))if(button.getClientRects().length)fits(button,'Sound button');
    audio.setAudioSettings({enabled:false,volume:.25});assert(!(el('#soundEnabled') as HTMLInputElement).checked&&(el('#soundPreview') as HTMLButtonElement).disabled,'Mute is out of sync');assert(el('#soundToggle').getAttribute('aria-pressed')==='false','Quick mute did not update');
    click('[data-preference-tab="desk"]');await frame();fits(dialog,'Desk preferences');assert(dialog.scrollHeight<=dialog.clientHeight+1,'Desk preferences scroll');click('#preferencesDone');click('#studioBtn');
  }finally{audio.setAudioSettings(before);if(raw===null)sessionStorage.removeItem('retropaint-sound');else sessionStorage.setItem('retropaint-sound',raw);}
});
await run('Every keyboard help category fits without scrolling',async()=>{
  click('#studioBtn');click('[data-studio="view"]');click('#openShortcuts');await frame();const dialog=el('#shortcutsDialog') as HTMLDialogElement;assert(dialog.open,'Shortcut help did not open');
  for(const tab of dialog.querySelectorAll<HTMLButtonElement>('[data-shortcut-tab]')){tab.click();await frame();fits(dialog,'Shortcut help');assert(dialog.scrollHeight<=dialog.clientHeight+1,'Shortcut help scrolls');for(const row of dialog.querySelectorAll<HTMLElement>('.shortcut-grid>div'))if(row.getClientRects().length)fits(row,'Shortcut row');}
  const first=dialog.querySelector<HTMLButtonElement>('[data-shortcut-tab="tools"]')!;first.click();first.focus();first.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true,cancelable:true}));assert(dialog.querySelector('[data-shortcut-tab="edit"]')!.getAttribute('aria-selected')==='true','Arrow keys did not change category');assert(document.activeElement===dialog.querySelector('[data-shortcut-tab="edit"]'),'Keyboard focus did not follow the selected category');
  click('#shortcutsDone');click('#studioBtn');
});
await run('Placement controls stay usable when a raster or vector extends beyond the paper',async()=>{
  const objects=await import('../src/objects');resetLayers(960,640);objects.setDrawingMode('vector');state.shapeFill='primary';state.shapeOutline='none';objects.addVectorShape('rect',10,10,210,210);click('[data-tool="scissors"]');click('.drawer.open .drawer-close');objects.moveObjects(-80,-60);await frame();fits(el('#workspaceBar'),'Placement controls');
  assert(!el('#workspaceCentre').hidden,'Outside selection has no way back');assert(!el('#workspaceOverlay').hidden,'Outside geometry has no working preview');
  const paper=view.getBoundingClientRect(),slot=el('#canvasSlot').getBoundingClientRect(),point=[{x:-35,y:30},{x:60,y:-20}].map(p=>({x:paper.left+p.x/960*paper.width,y:paper.top+p.y/640*paper.height})).find(p=>p.x>slot.left&&p.x<slot.right&&p.y>slot.top&&p.y<slot.bottom),capture=view.setPointerCapture;assert(point,'No visible desk space for an overhang');view.setPointerCapture=()=>{};
  try{const options={pointerId:709,button:0,buttons:1,clientX:point.x,clientY:point.y};el('#canvasSlot').dispatchEvent(new PointerEvent('pointerdown',options));view.dispatchEvent(new PointerEvent('pointermove',{...options,clientX:point.x+30/960*paper.width,clientY:point.y+20/640*paper.height}));view.dispatchEvent(new PointerEvent('pointerup',{...options,buttons:0,clientX:point.x+30/960*paper.width,clientY:point.y+20/640*paper.height}));assert(Math.abs(objects.objectSelectionBounds()!.x+40)<.01&&Math.abs(objects.objectSelectionBounds()!.y+30)<.01,'The desk overhang could not be grabbed and moved');}finally{view.setPointerCapture=capture;}
  click('#workspacePlace');assert(activeLayer().objects!.length===1,'Placing removed an off-paper vector');
  objects.selectAllObjects();objects.moveObjects(-1800,0);await frame();click('#workspaceCentre');assert(Math.abs(objects.objectSelectionBounds()!.x-380)<.01,'Bring to paper did not centre the piece');objects.commitObjectSelection();resetLayers(960,640);state.drawingMode='raster';
  objects.setDrawingMode('vector');const image=document.createElement('canvas');image.width=image.height=40;image.getContext('2d')!.fillRect(0,0,40,40);objects.addRasterImage(image,{x:10,y:10});objects.moveObjects(-30,0);document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));assert(!objects.hasObjectSelection()&&activeLayer().objects![0].width===20,'Deselecting with Escape kept off-paper raster pixels');resetLayers(960,640);state.drawingMode='raster';
});
await run('Idle pictures avoid full repaints, cursors redraw independently and live ink keeps animating',async()=>{
  resetLayers(960,640);state.drawingMode='raster';state.cursor=null;state.liveArmed=false;click('[data-tool="draw"]');click('.drawer.open .drawer-close');await frame();await frame();
  const {viewCtx,uiCtx}=await import('../src/canvas'),clearView=viewCtx.clearRect,clearOverlay=uiCtx.clearRect;let pictures=0,overlays=0;
  viewCtx.clearRect=function(...args:Parameters<CanvasRenderingContext2D['clearRect']>){pictures++;clearView.apply(this,args);};uiCtx.clearRect=function(...args:Parameters<CanvasRenderingContext2D['clearRect']>){overlays++;clearOverlay.apply(this,args);};
  try{
    await frame();await frame();assert(pictures===0&&overlays===0,'An idle picture repaints constantly');const r=view.getBoundingClientRect();view.dispatchEvent(new PointerEvent('pointermove',{pointerId:555,clientX:r.left+r.width*.5,clientY:r.top+r.height*.5}));await frame();assert(pictures===0&&overlays>0,'Moving a cursor needlessly repaints the artwork');
    const objects=await import('../src/objects');objects.setDrawingMode('vector');state.liveArmed=true;state.conveyor=['#ff0000','#0000ff'];state.shapeFill='primary';state.shapeOutline='none';objects.addVectorShape('rect',200,200,400,400);await frame();pictures=0;await frame();await frame();assert(pictures>1,'Live vector ink stopped animating');
  }finally{viewCtx.clearRect=clearView;uiCtx.clearRect=clearOverlay;state.liveArmed=false;state.cursor=null;state.drawingMode='raster';resetLayers(960,640);}
});
await run('A brief stroke updates the visible layer thumbnail after painting stops',async()=>{
  resetLayers(960,640);setAdvancedMode(true);state.tool='draw';state.liveArmed=false;state.brushWidth=30;state.ink='#ff0000';click('[data-tool="draw"]');click('.drawer.open .drawer-close');if(el('#layersPanel').hidden)click('#layersToggle');await frame();
  const thumbnail=el('.layer-row.active canvas') as HTMLCanvasElement,before=thumbnail.toDataURL(),capture=view.setPointerCapture;view.setPointerCapture=()=>{};
  try{const r=view.getBoundingClientRect(),options={pointerId:625,button:0,clientX:r.left+r.width/2,clientY:r.top+r.height/2};view.dispatchEvent(new PointerEvent('pointerdown',options));view.dispatchEvent(new PointerEvent('pointerup',options));await new Promise(resolve=>setTimeout(resolve,300));await frame();assert(thumbnail.toDataURL()!==before,'The thumbnail kept an older frame after a brief stroke');}
  finally{view.setPointerCapture=capture;if(!el('#layersPanel').hidden)click('#closeLayers');resetLayers(960,640);}
});
await run('Recent drafts paginate without scrolling and keep picture previews readable',async()=>{
  const {RecoveryStore}=await import('../src/recovery-store'),store=new RecoveryStore(`RetroPaintDraftUiChecks-${innerWidth}x${innerHeight}`),thumbnail=document.createElement('canvas').toDataURL();
  try{for(let i=0;i<8;i++)await store.save({id:`layout-${i}`,name:`Picture ${i+1} with a long descriptive name`,width:960,height:640,savedAt:Date.now()+i,thumbnail,bytes:2,data:'{}'});}finally{await store.close();}
  click('#studioBtn');click('[data-studio="file"]');click('#openRecovery');await frame();await frame();const dialog=el('#recoveryDialog') as HTMLDialogElement;assert(dialog.open,'Recent drafts did not open');
  const pages=innerHeight<480?4:3;for(let i=0;i<pages;i++){fits(dialog,'Recent drafts');assert(dialog.scrollHeight<=dialog.clientHeight+1,'Draft dialog scrolls');for(const card of dialog.querySelectorAll<HTMLElement>('.recovery-card'))fits(card,'Draft preview');if(i<pages-1)click('#recoveryNext');}
  assert(el('#recoveryPage').textContent===`${pages} / ${pages}`&&(el('#recoveryNext') as HTMLButtonElement).disabled,'Draft pagination missed the final pictures');click('#recoveryPrevious');assert(el('#recoveryPage').textContent===`${pages-1} / ${pages}`);click('#recoveryDone');
});
const cadDoc=await import('../src/cad-document'),cadUi=await import('../src/cad-ui');
const waitCad=async(test:()=>boolean)=>{const started=performance.now();while(!test()){if(performance.now()-started>20000)throw new Error('3D workshop did not finish the action: '+el('#cadStatus')?.textContent);await new Promise(resolve=>setTimeout(resolve,30));}await frame();};
await run('CAD launches from More, shares one 3D layer and supports exact transforms with Undo',async()=>{
  resetLayers(960,640);if(!el('#studioDrawer').classList.contains('open'))click('#studioBtn');click('#openCad');await waitCad(()=>state.cad.open&&!!cadUi.cadWorkbench());fits(el('#cadWorkshop'),'CAD workspace');fits(el('.cad-panel'),'CAD panel');
  click('[data-cad-primitive="box"]');await waitCad(()=>cadDoc.currentBodies().length===1&&!el('#cadWorkshop').hasAttribute('aria-busy'));assert(layers.length===2&&activeLayer().cad,'Cube did not use a 3D layer');
  (el('#cadPos0') as HTMLInputElement).value='-12.5';(el('#cadRot2') as HTMLInputElement).value='30';click('#cadApplyTransform');await frame();assert(cadDoc.currentBodies()[0].position[0]===-12.5&&cadDoc.currentBodies()[0].rotation[2]===30,'Exact mm position or angle was not applied');click('#cadUndo');await frame();assert(cadDoc.currentBodies()[0].position[0]===0,'CAD Undo lost the original transform');
  click('[data-cad-tab="add"]');click('[data-cad-primitive="sphere"]');await waitCad(()=>cadDoc.currentBodies().length===2&&!el('#cadWorkshop').hasAttribute('aria-busy'));assert(layers.length===2,'Second primitive created another layer');
});
await run('CAD dragging the move handle keeps the gesture alive across history updates and commits one reversible move',async()=>{
  const {Vector3}=await import('three'),work=cadUi.cadWorkbench()!,cube=cadDoc.currentBodies()[0],canvas=el('#cadCanvas') as HTMLCanvasElement;cadDoc.selectBodies([cube.id]);state.cad.tool='translate';work.setTool();work.view('top');await frame();
  const rect=canvas.getBoundingClientRect(),project=(x:number)=>{const p=new Vector3(x,0,10).project(work.camera);return {clientX:rect.left+(p.x+1)/2*rect.width,clientY:rect.top+(1-p.y)/2*rect.height};},savedCapture=canvas.setPointerCapture,savedRelease=canvas.releasePointerCapture;canvas.setPointerCapture=()=>{};canvas.releasePointerCapture=()=>{};
  try{
    let start:ReturnType<typeof project>|undefined;
    for(const distance of Array.from({length:160},(_,i)=>.5+i*.5)){const p=project(distance);canvas.dispatchEvent(new PointerEvent('pointermove',{pointerId:994,pointerType:'mouse',button:-1,buttons:0,...p}));if(work.transform.axis==='X'){start=p;break;}}
    assert(start,'Move handle cannot be picked');canvas.dispatchEvent(new PointerEvent('pointerdown',{pointerId:994,pointerType:'mouse',button:0,buttons:1,...start}));await frame();assert(state.cad.gesture&&work.transform.dragging,'Starting history interrupted the drag');
    canvas.dispatchEvent(new PointerEvent('pointermove',{pointerId:994,pointerType:'mouse',button:-1,buttons:1,clientX:start.clientX+35,clientY:start.clientY}));canvas.dispatchEvent(new PointerEvent('pointerup',{pointerId:994,pointerType:'mouse',button:0,buttons:0,clientX:start.clientX+35,clientY:start.clientY}));await frame();assert(!state.cad.gesture&&Math.abs(cadDoc.currentBodies()[0].position[0])>.1,'Move handle did not commit a transform');assert(Math.abs(cadDoc.currentBodies()[0].position[1])<.01,'X handle moved the Y axis');undo();await frame();assert(cadDoc.currentBodies()[0].position[0]===0,'Drag move did not Undo in one step');
  }finally{canvas.setPointerCapture=savedCapture;canvas.releasePointerCapture=savedRelease;}
});
await run('CAD rotation rings and size handles transform geometry and Undo restores each gesture',async()=>{
  const {Vector3}=await import('three'),work=cadUi.cadWorkbench()!,cube=cadDoc.currentBodies()[0],canvas=el('#cadCanvas') as HTMLCanvasElement,capture=canvas.setPointerCapture,release=canvas.releasePointerCapture;
  canvas.setPointerCapture=()=>{};canvas.releasePointerCapture=()=>{};
  try{for(const [mode,axis]of [['rotate','Z'],['scale','X']] as const){cadDoc.selectBodies([cube.id]);click(`[data-cad-tool="${mode}"]`);work.view('top');await frame();const rect=canvas.getBoundingClientRect(),point=(x:number,y:number)=>{const p=new Vector3(x,y,10).project(work.camera);return{clientX:rect.left+(p.x+1)/2*rect.width,clientY:rect.top+(1-p.y)/2*rect.height};};let start:ReturnType<typeof point>|undefined,startWorld=[0,0];
    for(const angle of mode==='rotate'?[Math.PI/4,-Math.PI/4,Math.PI*3/4]:[0]){for(const d of Array.from({length:160},(_,i)=>.5+i*.5)){const x=d*Math.cos(angle),y=d*Math.sin(angle),p=point(x,y);canvas.dispatchEvent(new PointerEvent('pointermove',{pointerId:995,pointerType:'mouse',button:-1,buttons:0,...p}));if(work.transform.axis===axis){start=p;startWorld=[x,y];break;}}if(start)break;}
    assert(start,mode+' handle cannot be picked');canvas.dispatchEvent(new PointerEvent('pointerdown',{pointerId:995,pointerType:'mouse',button:0,buttons:1,...start}));await frame();const end=mode==='rotate'?point(-startWorld[1],-startWorld[0]):{clientX:start.clientX+25,clientY:start.clientY};canvas.dispatchEvent(new PointerEvent('pointermove',{pointerId:995,pointerType:'mouse',button:-1,buttons:1,...end}));const gestureDebug={startWorld,points:['pointStart','pointEnd','eye','worldPosition'].map(key=>{const value=Reflect.get(work.transform,key);return value instanceof Vector3?value.toArray():null;}),enabled:work.transform.enabled,mode:work.transform.mode,axis:work.transform.axis,angle:work.transform.rotationAngle,dragging:work.transform.dragging,gesture:state.cad.gesture,pivot:work.pivot.quaternion.toArray(),node:work.nodes.get(cube.id)!.mesh.quaternion.toArray()};canvas.dispatchEvent(new PointerEvent('pointerup',{pointerId:995,pointerType:'mouse',button:0,buttons:0,...end}));await frame();const changed=cadDoc.currentBodies()[0];assert(mode==='rotate'?Math.abs(changed.rotation[2])>1:Math.abs(changed.scale[0]-1)>.01,mode+' handle did not change geometry: '+JSON.stringify({gestureDebug,changed}));undo();await frame();assert(cadDoc.currentBodies()[0].rotation.every(v=>Math.abs(v)<.01)&&cadDoc.currentBodies()[0].scale.every(v=>Math.abs(v-1)<.01),mode+' gesture did not Undo');
  }}finally{canvas.setPointerCapture=capture;canvas.releasePointerCapture=release;state.cad.tool='translate';work.setTool();}
});
await run('CAD alignment, repeated pieces and moving pieces between 3D layers keep dimensions and are reversible',async()=>{
  const history=await import('../src/history'),before=history.captureHistory();
  try{const originalLayer=activeLayer().id,[cube,sphere]=cadDoc.currentBodies();cadDoc.selectBodies([cube.id,sphere.id]);click('[data-cad-tab="build"]');(el('#cadBuildPage') as HTMLSelectElement).value='align';el('#cadBuildPage').dispatchEvent(new Event('change'));(el('#cadAlignTarget') as HTMLSelectElement).value=cube.id;(el('#cadAlignMode') as HTMLSelectElement).value='after';click('#cadAlign');await frame();const work=cadUi.cadWorkbench()!;assert(Math.abs(work.bounds(cube.id)!.max.x-work.bounds(sphere.id)!.min.x)<.01,'Touch alignment did not snap the bounding edges');
    cadDoc.selectBodies([sphere.id]);(el('#cadBuildPage') as HTMLSelectElement).value='repeat';el('#cadBuildPage').dispatchEvent(new Event('change'));(el('#cadArrayCount') as HTMLInputElement).value='2';(el('#cadArrayStep0') as HTMLInputElement).value='0';(el('#cadArrayStep1') as HTMLInputElement).value='30';click('#cadLinearArray');await frame();assert(cadDoc.currentBodies().length===4,'Repeated pieces were not created');const copies=[...state.cad.selected];
    click('[data-cad-tab="layers"]');click('#cadNewLayer');const destination=activeLayer().id;(el('#cadLayerSelect') as HTMLSelectElement).value=String(originalLayer);el('#cadLayerSelect').dispatchEvent(new Event('change'));cadDoc.selectBodies(copies);(el('#cadDestinationLayer') as HTMLSelectElement).value=String(destination);click('#cadMoveLayer');await frame();assert(activeLayer().id===destination&&cadDoc.currentBodies().length===2&&layers.find(l=>l.id===originalLayer)!.cad!.bodies.length===2,'Moving pieces between 3D layers lost objects');undo();await frame();assert(activeLayer().id===originalLayer&&cadDoc.currentBodies().length===4,'Layer transfer did not Undo');
  }finally{history.restoreHistory(before);await frame();}
});
await run('CAD face snapping mates selected solid faces with opposite normals',async()=>{
  const history=await import('../src/history'),before=history.captureHistory(),canvas=el('#cadCanvas') as HTMLCanvasElement,capture=canvas.setPointerCapture,release=canvas.releasePointerCapture;canvas.setPointerCapture=()=>{};canvas.releasePointerCapture=()=>{};
  try{click('[data-cad-tab="add"]');click('[data-cad-primitive="box"]');await waitCad(()=>!el('#cadWorkshop').hasAttribute('aria-busy'));const pieces=cadDoc.currentBodies(),moving=pieces[0],target=pieces.at(-1)!,work=cadUi.cadWorkbench()!;cadDoc.selectBodies([moving.id]);click('[data-cad-tab="build"]');(el('#cadBuildPage') as HTMLSelectElement).value='align';el('#cadBuildPage').dispatchEvent(new Event('change'));click('#cadSnapFaces');work.view('top');await frame();const {Vector3}=await import('three');
    for(const item of [moving,target]){const p=new Vector3(item.position[0],item.position[1],item.position[2]+10).project(work.camera),r=canvas.getBoundingClientRect(),options={pointerId:996,pointerType:'mouse',button:0,clientX:r.left+(p.x+1)/2*r.width,clientY:r.top+(1-p.y)/2*r.height};canvas.dispatchEvent(new PointerEvent('pointerdown',{...options,buttons:1}));canvas.dispatchEvent(new PointerEvent('pointerup',{...options,buttons:0}));await frame();}
    await waitCad(()=>Math.abs(cadDoc.currentBodies().find(b=>b.id===moving.id)!.position[0]-target.position[0])<.01);assert(Math.abs(work.bounds(moving.id)!.min.z-work.bounds(target.id)!.max.z)<.01,'Mated faces do not touch');
  }finally{canvas.setPointerCapture=capture;canvas.releasePointerCapture=release;history.restoreHistory(before);await frame();}
});
await run('CAD every tool category and sketch stage fits without scrolling at this viewport',async()=>{
  if(el('.cad-panel').classList.contains('cad-tools-hidden'))click('#cadToolsToggle');await frame();const checkCad=()=>{const panel=el('.cad-panel'),page=el('[data-cad-panel]:not([hidden])');fits(panel,'CAD panel');assert(page.scrollHeight<=page.clientHeight+2,'CAD page scrolls: '+page.id);for(const child of page.querySelectorAll<HTMLElement>('button,input,select,textarea'))if(child.getClientRects().length){fits(child,'CAD '+child.id);const a=child.getBoundingClientRect(),b=page.getBoundingClientRect();assert(a.bottom<=b.bottom+2,'CAD control clipped: '+child.id);}};
  for(const category of ['add','move','sketch','build','layers','print']){click(`[data-cad-tab="${category}"]`);await frame();await frame();checkCad();}
  click('[data-cad-tab="move"]');click('[data-cad-edit="size"]');await frame();checkCad();click('[data-cad-edit="transform"]');
  click('[data-cad-tab="build"]');for(const value of ['combine','align','repeat','edges','shell','loft','sweep']){(el('#cadBuildPage') as HTMLSelectElement).value=value;el('#cadBuildPage').dispatchEvent(new Event('change'));await frame();checkCad();}
  click('[data-cad-tab="sketch"]');click('[data-cad-sketch-kind="revolve"]');await frame();checkCad();click('#cadNextFeature');await frame();checkCad();click('#cadBackSketch');click('[data-cad-sketch-kind="extrude"]');
  click('#cadHelp');await frame();const help=el('#cadHelpDialog') as HTMLDialogElement;assert(help.open,'Workshop help did not open');fits(help,'Workshop help');assert(help.scrollHeight<=help.clientHeight+1,'Workshop help scrolls');click('#cadHelpDone');assert((el('#topBar') as HTMLElement).inert,'Painting controls remain keyboard accessible behind the workshop');
});
await run('CAD flat-face picking, dimensioned sketches and inward circle cuts make real closed geometry',async()=>{
  const {Vector3}=await import('three'),work=cadUi.cadWorkbench()!;cadDoc.selectBodies([cadDoc.currentBodies()[0].id]);click('[data-cad-tab="sketch"]');click('#cadPickFace');work.view('top');await frame();
  const canvas=el('#cadCanvas') as HTMLCanvasElement,rect=canvas.getBoundingClientRect(),p=new Vector3(0,0,20).project(work.camera),x=rect.left+(p.x+1)/2*rect.width,y=rect.top+(1-p.y)/2*rect.height,capture=canvas.setPointerCapture,release=canvas.releasePointerCapture;canvas.setPointerCapture=()=>{};canvas.releasePointerCapture=()=>{};
  try{for(const type of ['pointerdown','pointerup'])canvas.dispatchEvent(new PointerEvent(type,{pointerId:987,button:0,buttons:type==='pointerdown'?1:0,clientX:x,clientY:y,bubbles:true}));await frame();assert((el('#cadPlane') as HTMLSelectElement).value==='face','Flat face was not picked');assert(Math.abs(work.getPlane().origin[2]-20)<.01,'Picked workplane is not on the cube face');}
  finally{canvas.setPointerCapture=capture;canvas.releasePointerCapture=release;}
  if(el('.cad-panel').classList.contains('cad-tools-hidden'))click('#cadToolsToggle');click('#cadCircleSketch');if(el('.cad-panel').classList.contains('cad-tools-hidden'))click('#cadToolsToggle');for(const[id,value]of [['cadSketchX','0'],['cadSketchY','0'],['cadSketchW','8'],['cadSketchH','8']]){(el('#'+id) as HTMLInputElement).value=value;}click('#cadUseDimensions');click('#cadNextFeature');(el('#cadFeatureAmount') as HTMLInputElement).value='25';(el('#cadFeatureOperation') as HTMLSelectElement).value='cut';click('#cadCreateFeature');await waitCad(()=>!el('#cadWorkshop').hasAttribute('aria-busy'));const cut=cadDoc.currentBodies().find(b=>b.solid.kind==='boolean');assert(cut,'Face sketch cut was not committed');const {cadCompute}=await import('../src/cad-engine'),result=await cadCompute([cut]);assert(result.mesh.volume<7100&&result.mesh.volume>6900,'Cut has the wrong physical volume');
});
await run('CAD feature edits preview safely, rebuild the final solid and Undo as one change',async()=>{
  const {projectData}=await import('../src/project'),root=cadDoc.currentBodies().find(b=>b.solid.kind==='boolean')!;cadDoc.selectBodies([root.id]);click('[data-cad-tab="history"]');await frame();assert(el('[role="tree"]')&&el('#cadTimeline'),'History tree or timeline is missing');
  click('[data-feature-key="0"]');click('#cadFeatureEdit');await waitCad(()=>state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));const saved=projectData();(el('#cadFeatureSize2') as HTMLInputElement).value='40';click('#cadFeaturePreview');await waitCad(()=>!!state.cad.preview&&!el('#cadWorkshop').hasAttribute('aria-busy'));assert(projectData()===saved,'Preview altered the project');assert(Math.abs(cadUi.cadWorkbench()!.nodes.get(root.id)!.data.bounds.max[2]-30)<.01,'Preview did not rebuild the earlier solid');
  click('#cadFeatureApply');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));const edited=cadDoc.currentBodies().find(b=>b.id===root.id)!;assert(edited.solid.kind==='boolean'&&edited.solid.children[0].solid.kind==='primitive'&&edited.solid.children[0].solid.size[2]===40,'Original dimensions were not applied beneath the cut');assert(edited.solid.children[1].solid.feature?.attachment,'Original face sketch lost its support dependency');click('#cadUndo');await frame();assert(JSON.stringify(cadDoc.currentBodies().find(b=>b.id===root.id))===JSON.stringify(root),'Parameter edit did not Undo in one step');click('#cadRedo');await frame();
});
await run('CAD original hole sketches and through depths edit without losing the solid',async()=>{
  const root=cadDoc.currentBodies().find(b=>b.solid.kind==='boolean')!;click('[data-feature-key="1:sketch"]');click('#cadFeatureEdit');await waitCad(()=>state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));(el('#cadFeatureSketchWidth') as HTMLInputElement).value='12';(el('#cadFeatureSketchHeight') as HTMLInputElement).value='12';click('#cadFeatureApply');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));
  click('[data-feature-key="1"]');click('#cadFeatureEdit');await waitCad(()=>state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));(el('#cadFeatureThrough') as HTMLInputElement).checked=true;click('#cadFeatureApply');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));const {cadCompute}=await import('../src/cad-engine'),mesh=(await cadCompute([cadDoc.currentBodies().find(b=>b.id===root.id)!])).mesh;assert(Math.abs(mesh.volume-(16000-Math.PI*36*40))<5,'Hole diameter or through depth was not regenerated');
  click('[data-feature-key="0"]');click('#cadFeatureEdit');await waitCad(()=>state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));const saved=JSON.stringify(cadDoc.currentBodies());(el('#cadFeatureSize2') as HTMLInputElement).value='0';click('#cadFeatureApply');await waitCad(()=>!el('#cadWorkshop').hasAttribute('aria-busy'));assert(state.cad.editing&&!el('#cadFeatureError').hidden&&JSON.stringify(cadDoc.currentBodies())===saved,'Invalid dimensions changed the solid or discarded the draft');
  const page=el('#cadPagehistory');assert(page.scrollHeight<=page.clientHeight+2,'Feature editor scrolls');for(const input of page.querySelectorAll<HTMLElement>('button,input,select,textarea'))if(input.getClientRects().length)fits(input,'Feature editor '+input.id);click('#cadFeatureCancel');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));assert(!state.cad.preview&&JSON.stringify(cadDoc.currentBodies())===saved,'Cancel did not restore the exact original solid');
});
await run('CAD timeline rollback and feature suppression preserve history and fit the viewport',async()=>{
  const {projectData}=await import('../src/project');cadUi.cadWorkbench()!.updatePreviews();const saved=projectData();click('[data-cad-step="0"]');await waitCad(()=>!!state.cad.preview&&!el('#cadWorkshop').hasAttribute('aria-busy'));assert(projectData()===saved&&el('#cadTimelinePosition').textContent?.includes('Viewing step 1'),'Timeline changed the project or failed to roll back');assert(!cadUi.cadWorkbench()!.transform.object,'Rollback allowed a destructive gizmo edit');fits(el('#cadTimeline'),'Feature timeline');assert(el('#cadCanvas').getBoundingClientRect().bottom<=el('#cadTimeline').getBoundingClientRect().top+1,'Timeline covers the 3D workbench');click('#cadTimelineLatest');await waitCad(()=>!state.cad.preview&&!el('#cadWorkshop').hasAttribute('aria-busy'));const returned=projectData();assert(returned===saved,'Return to latest altered geometry: '+(()=>{const a=JSON.parse(saved),b=JSON.parse(returned);return a.layers.map((l:{id:number;image:string;cad?:unknown},i:number)=>({layer:l.id,image:l.image===b.layers[i].image,cad:JSON.stringify(l.cad)===JSON.stringify(b.layers[i].cad)})).map((v:unknown)=>JSON.stringify(v)).join(',');})());
  click('[data-feature-key="root"]');click('#cadFeatureSuppress');await waitCad(()=>!el('#cadWorkshop').hasAttribute('aria-busy'));assert(cadDoc.currentBodies().find(b=>b.solid.kind==='boolean')!.solid.feature?.suppressed,'Cut was not suppressed');click('#cadFeatureSuppress');await waitCad(()=>!el('#cadWorkshop').hasAttribute('aria-busy'));assert(!cadDoc.currentBodies().find(b=>b.solid.kind==='boolean')!.solid.feature?.suppressed,'Feature did not resume');
  const page=el('#cadPagehistory');assert(page.scrollHeight<=page.clientHeight+2,'History tree scrolls');for(const input of page.querySelectorAll<HTMLElement>('button,input,select'))if(input.getClientRects().length)fits(input,'History tree '+input.id);
});
await run('CAD edge picking toggles real edges and applies editable fillets and chamfers with Undo',async()=>{
  const history=await import('../src/history'),snapshot=history.captureHistory(),{primitive}=await import('../src/cad-model'),cube=primitive('box');
  try{cadDoc.replaceBodies([cube]);cadDoc.selectBodies([cube.id]);const work=cadUi.cadWorkbench()!;await work.sync();work.fit();click('[data-cad-tab="build"]');(el('#cadBuildPage') as HTMLSelectElement).value='edges';el('#cadBuildPage').dispatchEvent(new Event('change'));click('#cadPickEdges');await waitCad(()=>work.edges.choices.length===12&&!el('#cadWorkshop').hasAttribute('aria-busy'));assert(state.cad.tool==='edge'&&!work.transform.object,'Edge selection kept the transform gizmo active');work.view('top');await frame();
    const {Vector3}=await import('three'),edge=work.edges.choices.find(e=>e.ref.center[2]>.99&&e.ref.center[1]<.01)!,point=new Vector3(...edge.points[0]).add(new Vector3(...edge.points[1])).multiplyScalar(.5).applyMatrix4(work.edges.group.matrixWorld).project(work.camera),canvas=el('#cadCanvas') as HTMLCanvasElement,rect=canvas.getBoundingClientRect(),capture=canvas.setPointerCapture,release=canvas.releasePointerCapture;canvas.setPointerCapture=()=>{};canvas.releasePointerCapture=()=>{};
    const tap=()=>{const options={pointerId:991,pointerType:'mouse',button:0,clientX:rect.left+(point.x+1)/2*rect.width,clientY:rect.top+(1-point.y)/2*rect.height,bubbles:true};for(const type of ['pointerdown','pointerup'])canvas.dispatchEvent(new PointerEvent(type,{...options,buttons:type==='pointerdown'?1:0}));};
    try{tap();assert(state.cad.edgeSelection.length===1,'Tapping the top edge did not select it');tap();assert(state.cad.edgeSelection.length===0,'Tapping a selected edge did not deselect it');tap();}finally{canvas.setPointerCapture=capture;canvas.releasePointerCapture=release;}
    if(el('.cad-panel').classList.contains('cad-tools-hidden'))click('#cadToolsToggle');const original=JSON.stringify(cadDoc.currentBodies());click('#cadPreviewFinish');await waitCad(()=>state.cad.editing&&!!state.cad.preview&&!el('#cadWorkshop').hasAttribute('aria-busy'));assert(JSON.stringify(cadDoc.currentBodies())===original,'Fillet preview changed the committed solid');click('#cadFeatureApply');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));const made=cadDoc.currentBodies()[0];assert(made.id===cube.id&&made.solid.kind==='finish'&&made.solid.mode==='fillet'&&made.solid.size===2,'Fillet was not added as an editable feature');
    click('[data-feature-key="root"]');click('#cadFeatureEdit');await waitCad(()=>state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));(el('#cadFeatureFinishSize') as HTMLInputElement).value='3';(el('#cadFeatureFinishMode') as HTMLSelectElement).value='chamfer';el('#cadFeatureFinishMode').dispatchEvent(new Event('change'));for(let i=0;i<2;i++){click('#cadFeaturePreview');await waitCad(()=>!el('#cadWorkshop').hasAttribute('aria-busy'));}click('#cadFeatureApply');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));const result=cadDoc.currentBodies()[0];assert(result.solid.kind==='finish'&&result.solid.mode==='chamfer'&&result.solid.size===3,'Chamfer settings were not editable');assert(!result.solid.feature?.label||result.solid.feature.label==='Chamfer','Previewing kept an incorrect automatic feature name');const {cadCompute}=await import('../src/cad-engine');assert(Math.abs((await cadCompute([result])).mesh.volume-7910)<.03,'The edited chamfer size is incorrect');click('#cadUndo');await frame();assert(cadDoc.currentBodies()[0].solid.kind==='finish'&&(cadDoc.currentBodies()[0].solid as {size:number}).size===2,'Feature edit did not Undo in one step');
  }finally{if(state.cad.editing){click('#cadFeatureCancel');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));}state.cad.tool='translate';cadUi.cadWorkbench()?.setTool();history.restoreHistory(snapshot);await frame();}
});
await run('CAD finish history reselects original edges and safely rejects impossible radii without scrolling',async()=>{
  const history=await import('../src/history'),snapshot=history.captureHistory(),{primitive}=await import('../src/cad-model'),{cadCompute}=await import('../src/cad-engine'),cube=primitive('box');
  try{const edges=(await cadCompute([{...cube,position:[0,0,0]}],'edges')).edges!;cadDoc.replaceBodies([cadDoc.finishedBody(cube,'fillet',2,[edges[0].ref])]);cadDoc.selectBodies([cube.id]);await cadUi.cadWorkbench()!.sync();click('[data-cad-tab="history"]');click('[data-feature-key="root"]');click('#cadFeatureEdit');await waitCad(()=>state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));click('#cadFeatureReselectEdges');await waitCad(()=>state.cad.tool==='edge'&&!el('#cadWorkshop').hasAttribute('aria-busy'));assert(cadUi.cadWorkbench()!.edges.choices.length===12,'Reselect did not expose the original sharp input');
    if(el('.cad-panel').classList.contains('cad-tools-hidden'))click('#cadToolsToggle');click('#cadFeatureNoEdges');assert(state.cad.edgeSelection.length===0,'Clear edges did not empty the selection');click('#cadFeatureAllEdges');assert(state.cad.edgeSelection.length===12,'Select all did not choose original edges');click('#cadFeaturePreview');await waitCad(()=>!el('#cadWorkshop').hasAttribute('aria-busy'));click('#cadFeatureApply');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));const result=cadDoc.currentBodies()[0];assert(result.solid.kind==='finish'&&result.solid.edges.length===12,'Reselected edges were not saved in the feature');
    click('#cadFeatureEdit');await waitCad(()=>state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));const saved=JSON.stringify(cadDoc.currentBodies());(el('#cadFeatureFinishSize') as HTMLInputElement).value='40';click('#cadFeatureApply');await waitCad(()=>!el('#cadWorkshop').hasAttribute('aria-busy'));assert(state.cad.editing&&!el('#cadFeatureError').hidden&&JSON.stringify(cadDoc.currentBodies())===saved,'An impossible radius changed the original or discarded the editor');await frame();const page=el('#cadPagehistory');assert(page.scrollHeight<=page.clientHeight+2,'Fillet editor scrolls');for(const input of page.querySelectorAll<HTMLElement>('button,input,select'))if(input.getClientRects().length)fits(input,'Fillet editor '+input.id);click('#cadFeatureCancel');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));assert(!state.cad.preview&&JSON.stringify(cadDoc.currentBodies())===saved,'Cancel did not restore the original finish');
  }finally{if(state.cad.editing){click('#cadFeatureCancel');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));}state.cad.tool='translate';cadUi.cadWorkbench()?.setTool();history.restoreHistory(snapshot);await frame();}
});
await run('CAD shell picks whole faces, previews safely and edits wall thickness with one-step Undo',async()=>{
  const history=await import('../src/history'),snapshot=history.captureHistory(),{primitive}=await import('../src/cad-model'),{cadCompute}=await import('../src/cad-engine'),cube=primitive('box');
  try{cadDoc.replaceBodies([cube]);cadDoc.selectBodies([cube.id]);const work=cadUi.cadWorkbench()!;await work.sync();work.fit();click('[data-cad-tab="build"]');(el('#cadBuildPage') as HTMLSelectElement).value='shell';el('#cadBuildPage').dispatchEvent(new Event('change'));click('#cadPickShellFaces');await waitCad(()=>work.faces.choices.length===6&&!el('#cadWorkshop').hasAttribute('aria-busy'));assert(state.cad.tool==='shellFace'&&!work.transform.object,'Shell picking kept the transform gizmo active');work.view('top');await frame();
    const {Vector3}=await import('three'),canvas=el('#cadCanvas') as HTMLCanvasElement,rect=canvas.getBoundingClientRect(),point=new Vector3(0,0,20).project(work.camera),capture=canvas.setPointerCapture,release=canvas.releasePointerCapture;canvas.setPointerCapture=()=>{};canvas.releasePointerCapture=()=>{};const tap=()=>{for(const type of ['pointerdown','pointerup'])canvas.dispatchEvent(new PointerEvent(type,{pointerId:992,pointerType:'mouse',button:0,buttons:type==='pointerdown'?1:0,clientX:rect.left+(point.x+1)/2*rect.width,clientY:rect.top+(1-point.y)/2*rect.height,bubbles:true}));};
    try{tap();assert(state.cad.faceSelection.length===1&&state.cad.faceSelection[0].normal[2]>.99,'Tapping the top did not select the whole face');tap();assert(state.cad.faceSelection.length===0,'Tapping an open face did not close it');tap();}finally{canvas.setPointerCapture=capture;canvas.releasePointerCapture=release;}
    if(el('.cad-panel').classList.contains('cad-tools-hidden'))click('#cadToolsToggle');const original=JSON.stringify(cadDoc.currentBodies());click('#cadPreviewShell');await waitCad(()=>state.cad.editing&&!!state.cad.preview&&!el('#cadWorkshop').hasAttribute('aria-busy'));assert(JSON.stringify(cadDoc.currentBodies())===original,'Shell preview changed the original solid');assert(Math.abs(work.nodes.get(cube.id)!.data.volume-3392)<.02,'Shell preview did not hollow the solid');click('#cadFeatureApply');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));const made=cadDoc.currentBodies()[0];assert(made.id===cube.id&&made.solid.kind==='shell'&&made.solid.thickness===2&&made.solid.faces.length===1,'Shell did not become an editable feature');
    click('#cadFeatureEdit');await waitCad(()=>state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));(el('#cadFeatureThickness') as HTMLInputElement).value='3';click('#cadFeaturePreview');await waitCad(()=>!el('#cadWorkshop').hasAttribute('aria-busy'));click('#cadFeatureApply');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));assert(Math.abs((await cadCompute([cadDoc.currentBodies()[0]])).mesh.volume-4668)<.02,'Edited wall thickness did not rebuild');click('#cadUndo');await frame();assert(JSON.stringify(cadDoc.currentBodies()[0])===JSON.stringify(made),'Shell thickness did not Undo in one step');
  }finally{if(state.cad.editing){click('#cadFeatureCancel');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));}state.cad.tool='translate';cadUi.cadWorkbench()?.setTool();history.restoreHistory(snapshot);await frame();}
});
await run('CAD shell reselects original faces and preserves editable drafts when walls are impossible',async()=>{
  const history=await import('../src/history'),snapshot=history.captureHistory(),{primitive}=await import('../src/cad-model'),{cadCompute}=await import('../src/cad-engine'),cube=primitive('box');
  try{const faces=(await cadCompute([{...cube,position:[0,0,0]}],'faces')).faces,top=faces.find(f=>f.ref.normal[2]>.99)!;cadDoc.replaceBodies([cadDoc.shelledBody(cube,2,[top.ref])]);cadDoc.selectBodies([cube.id]);const work=cadUi.cadWorkbench()!;await work.sync();click('[data-cad-tab="history"]');click('[data-feature-key="root"]');click('#cadFeatureEdit');await waitCad(()=>state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));click('#cadFeatureReselectFaces');await waitCad(()=>state.cad.tool==='shellFace'&&!el('#cadWorkshop').hasAttribute('aria-busy'));assert(work.faces.choices.length===6&&state.cad.faceSelection.length===1,'Reselect did not expose the intact original with its saved opening');assert(Math.abs(work.nodes.get(cube.id)!.data.volume-8000)<.02,'Reselect is picking faces on the hollow result');
    if(el('.cad-panel').classList.contains('cad-tools-hidden'))click('#cadToolsToggle');click('#cadFeatureNoFaces');assert(state.cad.faceSelection.length===0,'Clear openings left a selected face');await frame();const page=el('#cadPagehistory');assert(page.scrollHeight<=page.clientHeight+2,'Shell face editor scrolls');for(const input of page.querySelectorAll<HTMLElement>('button,input,select'))if(input.getClientRects().length)fits(input,'Shell editor '+input.id);click('#cadFeatureApply');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));const result=cadDoc.currentBodies()[0];assert(result.solid.kind==='shell'&&!result.solid.faces.length&&Math.abs((await cadCompute([result])).mesh.volume-3904)<.02,'Changing openings did not create an enclosed cavity');
    click('#cadFeatureEdit');await waitCad(()=>state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));const saved=JSON.stringify(cadDoc.currentBodies());(el('#cadFeatureThickness') as HTMLInputElement).value='40';click('#cadFeatureApply');await waitCad(()=>!el('#cadWorkshop').hasAttribute('aria-busy'));assert(state.cad.editing&&!el('#cadFeatureError').hidden&&JSON.stringify(cadDoc.currentBodies())===saved,'An impossible wall discarded the editor or changed the original');await frame();assert(page.scrollHeight<=page.clientHeight+2,'Shell error editor scrolls');click('#cadFeatureCancel');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));assert(!state.cad.preview&&JSON.stringify(cadDoc.currentBodies())===saved,'Cancel failed to restore the shell');
    click('#cadFeatureSuppress');await waitCad(()=>!el('#cadWorkshop').hasAttribute('aria-busy'));assert(Math.abs((await cadCompute([cadDoc.currentBodies()[0]])).mesh.volume-8000)<.02,'Shell suppression lost its source');click('#cadFeatureSuppress');await waitCad(()=>!el('#cadWorkshop').hasAttribute('aria-busy'));click('[data-cad-step="0"]');await waitCad(()=>!!state.cad.preview&&!el('#cadWorkshop').hasAttribute('aria-busy'));assert(Math.abs(work.nodes.get(cube.id)!.data.volume-8000)<.02,'Shell timeline lost its original solid');click('#cadTimelineLatest');await waitCad(()=>!state.cad.preview&&!el('#cadWorkshop').hasAttribute('aria-busy'));
  }finally{if(state.cad.editing){click('#cadFeatureCancel');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));}state.cad.tool='translate';cadUi.cadWorkbench()?.setTool();history.restoreHistory(snapshot);await frame();}
});
await run('CAD loft builder preserves ordered profiles and History edits them without changing previews or Undo',async()=>{
  const history=await import('../src/history'),snapshot=history.captureHistory();
  try{cadDoc.replaceBodies([]);const work=cadUi.cadWorkbench()!;await work.sync();click('[data-cad-tab="build"]');(el('#cadBuildPage') as HTMLSelectElement).value='loft';el('#cadBuildPage').dispatchEvent(new Event('change'));assert(el('#cadEmpty').hidden,'Empty workshop message covers profile guides');
    const select=(id:string,value:string)=>{(el(id) as HTMLSelectElement).value=value;el(id).dispatchEvent(new Event('change'));};
    for(const pane of ['outline','placement','draw','point','coordinates','copy','settings']){select('#cadLoftPane',pane);await frame();const page=el('#cadPagebuild');assert(page.scrollHeight<=page.clientHeight+2,'Loft '+pane+' page scrolls');for(const input of page.querySelectorAll<HTMLElement>('button,input,select,textarea,svg'))if(input.getClientRects().length)fits(input,'Loft '+pane+' '+input.id);}
    select('#cadLoftPane','outline');click('#cadLoftAddProfile');assert((el('#cadLoftProfile') as HTMLSelectElement).options.length===3,'Could not add a profile');click('#cadLoftUp');click('#cadLoftDown');select('#cadLoftProfile','2');(el('#cadLoftProfileName') as HTMLInputElement).value='Lid sketch';(el('#cadLoftWidth') as HTMLInputElement).value='10';(el('#cadLoftHeight') as HTMLInputElement).value='10';select('#cadLoftPane','placement');(el('#cadLoftOrigin2') as HTMLInputElement).value='40';select('#cadLoftPane','settings');select('#cadLoftSides','ruled');click('#cadLoftMake');await waitCad(()=>!el('#cadWorkshop').hasAttribute('aria-busy'));const made=cadDoc.currentBodies()[0];assert(made?.solid.kind==='loft'&&made.solid.profiles.length===3&&made.solid.ruled&&made.solid.profiles[2].name==='Lid sketch','Loft settings or original profiles were baked');assert(Math.abs(work.nodes.get(made.id)!.data.bounds.max[2]-40)<.01,'Loft profile placement was ignored');
    click('[data-feature-key="root:profile:2"]');click('#cadFeatureEdit');await waitCad(()=>state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));const before=JSON.stringify(cadDoc.currentBodies());(el('#cadFeatureFormWidth') as HTMLInputElement).value='14';click('#cadFeaturePreview');await waitCad(()=>!!state.cad.preview&&!el('#cadWorkshop').hasAttribute('aria-busy'));assert(JSON.stringify(cadDoc.currentBodies())===before,'Loft profile preview changed the project');click('#cadFeatureApply');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));assert(JSON.stringify(cadDoc.currentBodies())!==before,'Loft profile edit was not applied');click('#cadUndo');await frame();assert(JSON.stringify(cadDoc.currentBodies())===before,'Loft edit was not one Undo step');
    click('[data-feature-key="root:profile:2"]');click('#cadFeatureEdit');await waitCad(()=>state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));(el('#cadFeatureFormWidth') as HTMLInputElement).value='0';click('#cadFeatureApply');await waitCad(()=>!el('#cadWorkshop').hasAttribute('aria-busy'));assert(state.cad.editing&&!el('#cadFeatureError').hidden&&JSON.stringify(cadDoc.currentBodies())===before,'Invalid loft dimensions discarded the editable draft');await frame();assert(el('#cadPagehistory').scrollHeight<=el('#cadPagehistory').clientHeight+2,'Loft error editor scrolls');click('#cadFeatureCancel');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));assert(!state.cad.preview&&JSON.stringify(cadDoc.currentBodies())===before,'Loft Cancel changed the original');
  }finally{if(state.cad.editing){click('#cadFeatureCancel');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));}history.restoreHistory(snapshot);await frame();}
});
await run('CAD sweep path dragging, exact point edits and settings stay parametric and fit the panel',async()=>{
  const history=await import('../src/history'),snapshot=history.captureHistory();
  try{cadDoc.replaceBodies([]);const work=cadUi.cadWorkbench()!;await work.sync();click('[data-cad-tab="build"]');const select=(id:string,value:string)=>{(el(id) as HTMLSelectElement).value=value;el(id).dispatchEvent(new Event('change'));};select('#cadBuildPage','sweep');
    for(const pane of ['outline','draw','path','point','coordinates','copy','settings']){select('#cadSweepPane',pane);await frame();const page=el('#cadPagebuild');assert(page.scrollHeight<=page.clientHeight+2,'Sweep '+pane+' page scrolls');for(const input of page.querySelectorAll<HTMLElement>('button,input,select,textarea,svg'))if(input.getClientRects().length)fits(input,'Sweep '+pane+' '+input.id);}
    select('#cadSweepPane','outline');select('#cadSweepShape','rectangle');(el('#cadSweepWidth') as HTMLInputElement).value='4';(el('#cadSweepHeight') as HTMLInputElement).value='4';select('#cadSweepPane','coordinates');(el('#cadSweepCoordinates') as HTMLTextAreaElement).value='0,0,0; 0,0,20; 20,0,20';(el('#cadSweepPathName') as HTMLInputElement).value='My route';select('#cadSweepPane','settings');select('#cadSweepPathMode','polyline');click('#cadSweepMake');await waitCad(()=>!el('#cadWorkshop').hasAttribute('aria-busy'));const made=cadDoc.currentBodies()[0];assert(made?.solid.kind==='sweep'&&made.solid.path.name==='My route'&&!made.solid.path.smooth,'Sweep did not preserve its path and settings');assert(Math.abs(work.nodes.get(made.id)!.data.volume-640)<.05,'Sweep did not make real solid geometry');
    click('[data-feature-key="root:path"]');click('#cadFeatureEdit');await waitCad(()=>state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));const original=JSON.stringify(cadDoc.currentBodies()),svg=el('#cadFeatureFormPlot') as unknown as SVGSVGElement,matrix=svg.getScreenCTM()!,start=new DOMPoint(0,-20).matrixTransform(matrix),end=new DOMPoint(-5,-25).matrixTransform(matrix),capture=svg.setPointerCapture;svg.setPointerCapture=()=>{};
    try{svg.querySelector('[data-form-point="1"]')!.dispatchEvent(new PointerEvent('pointerdown',{pointerId:993,button:0,buttons:1,clientX:start.x,clientY:start.y,bubbles:true}));svg.dispatchEvent(new PointerEvent('pointermove',{pointerId:993,button:-1,buttons:1,clientX:end.x,clientY:end.y,bubbles:true}));svg.dispatchEvent(new PointerEvent('pointerup',{pointerId:993,button:0,buttons:0,clientX:end.x,clientY:end.y,bubbles:true}));}finally{svg.setPointerCapture=capture;}
    select('#cadFeatureFormPane','point');select('#cadFeatureFormPoint','1');assert(Number((el('#cadFeatureFormPoint0') as HTMLInputElement).value)===-5&&Number((el('#cadFeatureFormPoint2') as HTMLInputElement).value)===25,'Dragging did not edit the selected 3D path point');assert(JSON.stringify(cadDoc.currentBodies())===original,'Path dragging changed the committed model');click('#cadFeatureApply');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));const changed=cadDoc.currentBodies()[0];assert(changed.solid.kind==='sweep'&&changed.solid.path.points[1][0]===-5,'Path point edit was not saved');click('#cadUndo');await frame();assert(JSON.stringify(cadDoc.currentBodies())===original,'Sweep path did not Undo in one step');
    click('[data-feature-key="root"]');click('#cadFeatureEdit');await waitCad(()=>state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));select('#cadFeatureFormPathMode','smooth');(el('#cadFeatureFormRoll') as HTMLInputElement).value='25';click('#cadFeatureApply');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));const result=cadDoc.currentBodies()[0];assert(result.solid.kind==='sweep'&&result.solid.path.smooth&&result.solid.roll===25,'Sweep settings did not rebuild');click('[data-feature-key="root:path"]');click('#cadFeatureEdit');await waitCad(()=>state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));select('#cadFeatureFormPane','coordinates');const saved=JSON.stringify(cadDoc.currentBodies());(el('#cadFeatureFormCoordinates') as HTMLTextAreaElement).value='0,0,0;0,0,0';click('#cadFeatureApply');await waitCad(()=>!el('#cadWorkshop').hasAttribute('aria-busy'));assert(state.cad.editing&&!el('#cadFeatureError').hidden&&JSON.stringify(cadDoc.currentBodies())===saved,'Invalid path changed the original or discarded its editor');await frame();assert(el('#cadPagehistory').scrollHeight<=el('#cadPagehistory').clientHeight+2,'Sweep error editor scrolls');click('#cadFeatureCancel');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));
  }finally{if(state.cad.editing){click('#cadFeatureCancel');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));}history.restoreHistory(snapshot);await frame();}
});
await run('CAD loft can copy saved and newly drawn sketch outlines while preserving their sources',async()=>{
  const history=await import('../src/history'),snapshot=history.captureHistory(),model=await import('../src/cad-model'),plane=model.basePlane('xy'),source=model.body({kind:'extrude',points:model.sketchPoints('circle',0,0,12,12),plane,height:5,taper:1,twist:0,feature:{sketch:'circle'}},'Source outline');
  try{cadDoc.replaceBodies([source]);await cadUi.cadWorkbench()!.sync();const original=JSON.stringify(source),select=(id:string,value:string)=>{(el(id) as HTMLSelectElement).value=value;el(id).dispatchEvent(new Event('change'));};click('[data-cad-tab="build"]');select('#cadBuildPage','loft');select('#cadLoftProfile','0');select('#cadLoftPane','copy');click('#cadLoftCopy');assert(Number((el('#cadLoftWidth') as HTMLInputElement).value)===12,'Saved sketch outline was not copied');assert(JSON.stringify(cadDoc.currentBodies()[0])===original,'Copying changed the source solid');
    click('[data-cad-tab="sketch"]');click('[data-cad-sketch-kind="extrude"]');for(const [id,value]of [['cadSketchX','-4'],['cadSketchY','-6'],['cadSketchW','8'],['cadSketchH','12']]){(el('#'+id) as HTMLInputElement).value=value;}click('#cadUseDimensions');click('[data-cad-tab="build"]');select('#cadLoftPane','copy');assert(!(el('#cadLoftDrawing') as HTMLButtonElement).disabled,'Current sketch drawing is unavailable');click('#cadLoftDrawing');assert(Number((el('#cadLoftWidth') as HTMLInputElement).value)===8&&(el('#cadLoftShape') as HTMLSelectElement).value==='rectangle','Current drawing was not copied as a sketch');assert(JSON.stringify(cadDoc.currentBodies()[0])===original,'Copying a drawing changed existing geometry');
  }finally{history.restoreHistory(snapshot);await frame();}
});
await run('CAD sketch dimensions create solids and edit in History with safe Preview Apply Cancel and Undo',async()=>{
  const history=await import('../src/history'),snapshot=history.captureHistory(),work=cadUi.cadWorkbench()!,select=(id:string,value:string)=>{(el(id) as HTMLSelectElement).value=value;el(id).dispatchEvent(new Event('change'));};
  try{cadDoc.replaceBodies([]);await work.sync();click('[data-cad-tab="sketch"]');click('[data-cad-sketch-kind="extrude"]');state.cad.tool='rectangle';work.setTool();select('#cadPlane','xy');for(const[id,value]of [['cadSketchX','0'],['cadSketchY','0'],['cadSketchW','20'],['cadSketchH','10']])(el('#'+id) as HTMLInputElement).value=value;click('#cadUseDimensions');click('#cadSketchConstraints');(el('#cadSketchConstraintValue') as HTMLInputElement).value='32';click('#cadSketchConstraintAdd');assert(el('#cadSketchConstraintEditor').textContent?.includes('1 constraints · solved'),'New sketch dimension was not saved');await frame();assert(el('#cadPagesketch').scrollHeight<=el('#cadPagesketch').clientHeight+2,'Sketch dimension page scrolls');click('#cadNextFeature');select('#cadFeatureOperation','new');(el('#cadFeatureAmount') as HTMLInputElement).value='10';(el('#cadTaper') as HTMLInputElement).value='1';(el('#cadTwist') as HTMLInputElement).value='0';click('#cadCreateFeature');await waitCad(()=>cadDoc.currentBodies().length===1&&!el('#cadWorkshop').hasAttribute('aria-busy'));const made=cadDoc.currentBodies()[0];assert(made.solid.feature?.constraints?.length===1&&Math.abs(work.nodes.get(made.id)!.data.volume-3200)<.02,'New dimension was baked or ignored');
    click('[data-cad-tab="history"]');click('[data-feature-key="root:sketch"]');click('#cadFeatureEdit');await waitCad(()=>state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));const original=JSON.stringify(cadDoc.currentBodies());click('#cadFeatureConstraintSavedPage');(el('#cadFeatureConstraintValue') as HTMLInputElement).value='40';click('#cadFeatureConstraintUpdate');assert(JSON.stringify(cadDoc.currentBodies())===original,'Updating a dimension changed the committed recipe');await frame();for(const input of el('#cadPagehistory').querySelectorAll<HTMLElement>('button,input,select,svg'))if(input.getClientRects().length)fits(input,'Constraint history '+input.id);click('#cadFeaturePreview');await waitCad(()=>!!state.cad.preview&&!el('#cadWorkshop').hasAttribute('aria-busy'));assert(JSON.stringify(cadDoc.currentBodies())===original&&Math.abs(work.nodes.get(made.id)!.data.volume-4000)<.02,'Dimension preview was destructive or did not rebuild');click('#cadFeatureApply');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));assert(JSON.stringify(cadDoc.currentBodies())!==original,'Dimension edit was not committed');click('#cadUndo');await frame();assert(JSON.stringify(cadDoc.currentBodies())===original,'Dimension edit did not Undo in one step');
    click('[data-feature-key="root:sketch"]');click('#cadFeatureEdit');await waitCad(()=>state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));(el('#cadFeatureConstraintValue') as HTMLInputElement).value='20';click('#cadFeatureConstraintAdd');assert(!el('#cadFeatureConstraintError').hidden&&JSON.stringify(cadDoc.currentBodies())===original,'Conflicting dimension replaced a valid sketch');await frame();assert(el('#cadPagehistory').scrollHeight<=el('#cadPagehistory').clientHeight+2,'Constraint conflict scrolls');click('#cadFeatureConstraintSavedPage');(el('#cadFeatureConstraintValue') as HTMLInputElement).value='36';click('#cadFeatureConstraintUpdate');click('#cadFeatureCancel');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));assert(JSON.stringify(cadDoc.currentBodies())===original,'Cancel changed the saved dimension');
  }finally{if(state.cad.editing){click('#cadFeatureCancel');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));}history.restoreHistory(snapshot);await frame();}
});
await run('CAD clickable sketch lines add editable geometric relations and reject conflicting angles',async()=>{
  const history=await import('../src/history'),snapshot=history.captureHistory(),{body,basePlane}=await import('../src/cad-model'),work=cadUi.cadWorkbench()!,select=(id:string,value:string)=>{(el(id) as HTMLSelectElement).value=value;el(id).dispatchEvent(new Event('change'));};
  try{const source=body({kind:'extrude',points:[[0,0],[20,1],[21,12],[-1,10]],plane:basePlane('xy'),height:5,taper:1,twist:0,feature:{sketch:'polygon'}},'Relations');cadDoc.replaceBodies([source]);await work.sync();cadDoc.selectBodies([source.id]);click('[data-cad-tab="history"]');click('[data-feature-key="root:sketch"]');click('#cadFeatureEdit');await waitCad(()=>state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));select('#cadFeatureSketchMode','constraints');
    for(const[kind,edge,other]of [['horizontal','0','1'],['vertical','1','0'],['parallel','0','2'],['perpendicular','0','3']]){select('#cadFeatureConstraintKind',kind);el(`#cadFeatureConstraintPlot [data-line="${edge}"]`).dispatchEvent(new MouseEvent('click',{bubbles:true}));if(kind==='parallel'||kind==='perpendicular')el(`#cadFeatureConstraintPlot [data-line="${other}"]`).dispatchEvent(new MouseEvent('click',{bubbles:true,shiftKey:true}));assert((el('#cadFeatureConstraintEdge') as HTMLSelectElement).value===edge,'Tapping a line did not select it');click('#cadFeatureConstraintAdd');assert(el('#cadFeatureConstraintError').hidden,'Compatible '+kind+' failed');}
    select('#cadFeatureConstraintKind','angle');(el('#cadFeatureConstraintValue') as HTMLInputElement).value='45';click('#cadFeatureConstraintAdd');assert(!el('#cadFeatureConstraintError').hidden,'Conflicting angle was accepted');click('#cadFeatureConstraintSavedPage');click('#cadFeatureConstraintRemove');assert(el('#cadFeatureConstraints').textContent?.includes('3 constraints · solved'),'A saved relation could not be removed');click('#cadFeatureApply');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));assert(cadDoc.currentBodies()[0].solid.feature?.constraints?.length===3,'Relations were not saved in the feature recipe');
  }finally{if(state.cad.editing){click('#cadFeatureCancel');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));}history.restoreHistory(snapshot);await frame();}
});
await run('CAD loft and sweep profiles expose dimensions and retain them in the feature tree',async()=>{
  const history=await import('../src/history'),snapshot=history.captureHistory(),{body}=await import('../src/cad-model'),{defaultForm}=await import('../src/cad-profiles'),work=cadUi.cadWorkbench()!,select=(id:string,value:string)=>{(el(id) as HTMLSelectElement).value=value;el(id).dispatchEvent(new Event('change'));};
  try{for(const kind of ['loft','sweep'] as const){const form=defaultForm(kind);if(form.kind==='sweep')form.path.points=[[0,0,0],[0,0,30]];const source=body(form,'Dimensioned '+kind);cadDoc.replaceBodies([source]);await work.sync();cadDoc.selectBodies([source.id]);click('[data-cad-tab="history"]');click('[data-feature-key="root:profile:0"]');click('#cadFeatureEdit');await waitCad(()=>state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));select('#cadFeatureFormPane','constraints');assert((el('#cadFeatureFormConstraintKind') as HTMLSelectElement).value==='diameter','Circle profile is missing its diameter control');(el('#cadFeatureFormConstraintValue') as HTMLInputElement).value=kind==='loft'?'24':'8';click('#cadFeatureFormConstraintAdd');await frame();assert(el('#cadPagehistory').scrollHeight<=el('#cadPagehistory').clientHeight+2,'Profile dimension editor scrolls');click('#cadFeatureApply');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));const s=cadDoc.currentBodies()[0].solid;assert((s.kind==='loft'?s.profiles[0].constraints:s.kind==='sweep'?s.profile.constraints:[])?.length===1,'Profile constraints were baked');if(kind==='sweep')assert(Math.abs(work.nodes.get(source.id)!.data.volume-Math.PI*16*30)<1,'Sweep profile diameter was ignored');}}
  finally{if(state.cad.editing){click('#cadFeatureCancel');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));}history.restoreHistory(snapshot);await frame();}
});
await run('CAD revolving a hollow profile, making layers and checking STL size work through the controls',async()=>{
  click('[data-cad-tab="sketch"]');click('[data-cad-sketch-kind="revolve"]');click('#cadNextFeature');(el('#cadFeatureOperation') as HTMLSelectElement).value='new';click('#cadCreateFeature');await waitCad(()=>!el('#cadWorkshop').hasAttribute('aria-busy'));assert(cadDoc.currentBodies().some(b=>b.solid.kind==='revolve'),'Revolve did not create a solid');
  click('[data-cad-tab="history"]');click('[data-feature-key="root"]');click('#cadFeatureEdit');await waitCad(()=>state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));(el('#cadFeatureDegrees') as HTMLInputElement).value='180';click('#cadFeatureApply');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));const revolved=cadDoc.selectedBodies()[0];assert(revolved.solid.kind==='revolve'&&revolved.solid.degrees===180,'Revolve angle was not editable');click('[data-feature-key="root:sketch"]');click('#cadFeatureEdit');await waitCad(()=>state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));const originalProfile=JSON.stringify(cadDoc.currentBodies()),svg=el('#cadFeatureSketch') as unknown as SVGSVGElement,matrix=svg.getScreenCTM()!,start=new DOMPoint(15,0).matrixTransform(matrix),end=new DOMPoint(16,-1).matrixTransform(matrix),capture=svg.setPointerCapture;svg.setPointerCapture=()=>{};
  try{svg.querySelector('[data-feature-point="1"]')!.dispatchEvent(new PointerEvent('pointerdown',{pointerId:998,button:0,buttons:1,clientX:start.x,clientY:start.y,bubbles:true}));svg.dispatchEvent(new PointerEvent('pointermove',{pointerId:998,button:-1,buttons:1,clientX:end.x,clientY:end.y,bubbles:true}));svg.dispatchEvent(new PointerEvent('pointerup',{pointerId:998,button:0,buttons:0,clientX:end.x,clientY:end.y,bubbles:true}));assert(Math.abs(Number((el('#cadFeaturePointX') as HTMLInputElement).value)-16)<.02&&JSON.stringify(cadDoc.currentBodies())===originalProfile,'Dragging an original sketch point failed or changed the committed model');}finally{svg.setPointerCapture=capture;}
  (el('#cadFeaturePoints') as HTMLTextAreaElement).value='5,0;15,0;15,30;5,30';click('#cadFeatureApply');await waitCad(()=>!state.cad.editing&&!el('#cadWorkshop').hasAttribute('aria-busy'));const ring=cadDoc.selectedBodies()[0];assert(ring.solid.kind==='revolve'&&ring.solid.points.length===4&&ring.solid.degrees===180,'Original revolve profile was not regenerated');
  click('[data-cad-tab="layers"]');const before=layers.length;click('#cadNewLayer');await frame();assert(layers.length===before+1&&layers.filter(l=>l.cad).length===2&&activeLayer().cad?.bodies.length===0,'New 3D layer failed');click('[data-cad-tab="add"]');click('[data-cad-primitive="cylinder"]');await waitCad(()=>cadDoc.currentBodies().length===1&&!el('#cadWorkshop').hasAttribute('aria-busy'));
  click('[data-cad-tab="print"]');click('#cadCheckPrint');await waitCad(()=>!el('#cadWorkshop').hasAttribute('aria-busy'));assert(el('#cadPrintReport').textContent?.includes('Closed solid geometry'),'Print check did not build the export mesh');click('#cadClose');await frame();assert(!state.cad.open&&!activeLayer().cad,'Returning to Paint did not select a paint layer');assert(layers.filter(l=>l.cad).every(l=>l.canvas.getContext('2d')!.getImageData(0,0,l.canvas.width,l.canvas.height).data.some((v,i)=>i%4===3&&v>0)),'CAD layers have no painting preview');resetLayers(960,640);
});
const report=document.createElement('pre'); report.id='mobileResults';
report.style.cssText='position:fixed;inset:10px;z-index:100;background:white;color:#263047;overflow:auto;padding:16px;white-space:pre-wrap';
report.textContent=`${innerWidth} × ${innerHeight}\n`+results.join('\n');
document.body.append(report);
document.title=results.some(r=>r.startsWith('FAIL'))?'FAIL — Mobile checks':'PASS — Mobile checks';
document.body.dataset.currentCheck='Complete';
}
