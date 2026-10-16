import markup from '../index.html?raw';
const testSize = new URLSearchParams(location.search).get('frame');
if (testSize && window.top === window.self) {
  const [width, height] = testSize.split('x').map(Number);
  const iframe = document.createElement('iframe'); iframe.title = `RetroPaint ${width} × ${height} preview`;
  iframe.width = String(width); iframe.height = String(height); iframe.style.cssText = 'border:0;display:block;margin:20px auto;background:white';
  iframe.src = new URLSearchParams(location.search).has('preview') ? '../index.html' : './mobile.html';
  document.body.style.cssText = 'margin:0;background:#dceee5'; document.body.append(iframe);
} else {
const parsed = new DOMParser().parseFromString(markup, 'text/html');
parsed.querySelectorAll('script').forEach(script => script.remove());
document.body.replaceChildren(...Array.from(parsed.body.childNodes));
await import('../src/main');
const { base, baseCtx, view, eventPos } = await import('../src/canvas');
const { state } = await import('../src/state');
const { bakeStaticStrokes } = await import('../src/live');
const { activeLayer, layers, resetLayers } = await import('../src/layers');
const { undo, redo } = await import('../src/history');
const photoModule = await import('../src/photo-session');
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
  resetLayers(960,640);click('#photoToggle');await frame();
  fits(el('#photoPanel'),'Photo lab');
  for(const category of ['light','colour','curves','detail','effects','geometry']){
    click(`[data-photo-category="${category}"]`);
    const select=el('#photoGroup') as HTMLSelectElement;
    for(const option of [...select.options]){
      select.value=option.value;select.dispatchEvent(new Event('change',{bubbles:true}));await frame();
      const panel=el('#photoPanel');fits(panel,option.text);
      assert(panel.scrollHeight<=panel.clientHeight+1,option.text+' requires scrolling');
      for(const control of panel.querySelectorAll<HTMLElement>('button,input,select,canvas'))if(control.getClientRects().length)fits(control,control.getAttribute('aria-label')||control.id||control.textContent!);
    }
  }
  assert(el('#toolBin').inert,'Drawing tools can mutate a pending photo preview');click('#photoCancel');
  assert(!el('#toolBin').inert&&!photoModule.photoSession,'Cancel did not release drawing tools');
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
const report=document.createElement('pre'); report.id='mobileResults';
report.style.cssText='position:fixed;inset:10px;z-index:100;background:white;color:#263047;overflow:auto;padding:16px;white-space:pre-wrap';
report.textContent=`${innerWidth} × ${innerHeight}\n`+results.join('\n');
document.body.append(report);
document.title=results.some(r=>r.startsWith('FAIL'))?'FAIL — Mobile checks':'PASS — Mobile checks';
}
