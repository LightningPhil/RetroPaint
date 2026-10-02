import markup from '../index.html?raw';
const parsed = new DOMParser().parseFromString(markup, 'text/html');
parsed.querySelectorAll('script').forEach(script => script.remove());
document.body.replaceChildren(...Array.from(parsed.body.childNodes));
await import('../src/main');
const { base, baseCtx, view, eventPos } = await import('../src/canvas');
const { state } = await import('../src/state');
const { bakeStaticStrokes } = await import('../src/live');
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
await run('Toolbar and all ten tools fit without overlap', () => {
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
const report=document.createElement('pre'); report.id='mobileResults';
report.style.cssText='position:fixed;inset:10px;z-index:100;background:white;color:#263047;overflow:auto;padding:16px;white-space:pre-wrap';
report.textContent=`${innerWidth} × ${innerHeight}\n`+results.join('\n');
document.body.append(report);
document.title=results.some(r=>r.startsWith('FAIL'))?'FAIL — Mobile checks':'PASS — Mobile checks';
