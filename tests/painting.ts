import { ArtworkAge, artwork } from '../src/artwork';
import { bindClearConfirmation } from '../src/clear-confirmation';
import { initInput, tickSpray } from '../src/input';
import { activeSector, insideSector, clipSegment, sliceAt, sliceCount, sectorPolygon } from '../src/symmetry-mask';
import { placeStamp } from '../src/stamps';
import { mirrorMotion, symmetryTransforms } from '../src/symmetry';
import { hexToRgb, neonColor } from '../src/color';
import { base, baseCtx, cloneCanvas, initCanvas, resetPaint, view, W, H } from '../src/canvas';
import { advect, advectMany, SmudgePath } from '../src/smudge';
import { paintStroke } from '../src/brush';
import { beginStrokeGeneration, mirrorPoints, segment, sprayCloud, dot } from '../src/draw';
import { splinePoints } from '../src/curves';
import { renderPaintPath } from '../src/stroke-renderer';
import { initMaterials } from '../src/materials';
import { state } from '../src/state';
import { paintFrame } from '../src/paint';
import { bakeStaticStrokes, clearLive, strokes, snapshotLive, restoreLive, renderLive } from '../src/live';
import { smudge, beginBake, invertAt, startHole, tickHole, startSqueegee, tickSqueegee } from '../src/effects';
import { pushHistory, undo } from '../src/history';
import { cancelSelection, commitSelection, copySelection, cutSelection, hasSelection, hitSelection, moveSelection, pasteSelection, rectangle, refreshTransparency, selectRegion, renderSelection } from '../src/selection';
import { drawShape, floodAt, floodMask, setShapePainter, getPending, cancelPending } from '../src/fill';
import { drawBetween, penPosition, setRingRadius } from '../src/spiro';

initCanvas(); initMaterials();
setShapePainter((x0,y0,x1,y1,w) => segment(x0,y0,x1,y1,w,0));
let failures = 0;
const check = (name: string, fn: () => void) => {
  const li = document.createElement('li');
  try { fn(); li.className = 'pass'; li.textContent = 'PASS ' + name; }
  catch (error) { failures++; li.className = 'fail'; li.textContent = 'FAIL ' + name + ': ' + error; }
  document.querySelector('#results')!.append(li);
};
function assert(value: unknown, message = 'Assertion failed'): asserts value { if (!value) throw new Error(message); }
function reset() {
  cancelSelection(); clearLive(); artwork.reset(); resetPaint(baseCtx);
  baseCtx.fillStyle = '#ffffff'; baseCtx.fillRect(0, 0, W, H);
  state.opacity = 1; state.symmetry = 'off'; state.symmetryMask=false; state.choosingSlice=false; state.symmetrySlice=0; state.tool = 'draw'; state.ink = '#E53935'; state.applicator = 'marker'; state.liveArmed = false;
}
function pixel(x: number, y: number) { return Array.from(baseCtx.getImageData(x, y, 1, 1).data).join(','); }
function block(x = 50, y = 50) { baseCtx.fillStyle = '#ff0000'; baseCtx.fillRect(x, y, 40, 40); }
function image() { return base.toDataURL(); }

check('Smudge preserves flat colour and pixels beyond the soft radius', () => {
  const src = new Uint8ClampedArray(40 * 40 * 4).fill(128);
  const out = advect(src, 40, 40, 20, 20, 2, 1, 12, 0.8);
  assert(out.every((v, i) => v === src[i]));
});
check('Smudge pulls colour in the direction of travel with no transparent gaps', () => {
  const src = new Uint8ClampedArray(40 * 40 * 4).fill(255);
  for (let y = 0; y < 40; y++) for (let x = 0; x < 20; x++) src[(y * 40 + x) * 4] = 0;
  const out = advect(src, 40, 40, 20, 20, 3, 0, 12, 0.9);
  assert(out[(20 * 40 + 21) * 4] < 255, 'Pigment must move right');
  assert(out[(1 * 40 + 21) * 4] === 255, 'Outside pixels must stay fixed');
  assert(out.every((v, i) => i % 4 !== 3 || v === 255), 'No alpha holes');
});
check('Smudge ignores jitter, resamples fast motion and finishes at the release point', () => {
  const dabs: number[][] = [];
  const path = new SmudgePath(0, 0, 30, (...p) => dabs.push(p));
  for (let i = 0; i < 50; i++) path.move(i % 2 ? 0.3 : -0.3, 0);
  assert(dabs.length === 0, 'Jitter must not stamp');
  path.move(120, 0); path.move(120, 0, true);
  assert(dabs.length >= 39 && dabs.length <= 41, 'Fast strokes must be evenly sampled');
  assert(Math.abs(dabs.at(-1)![0] - 120) < 0.25);
  assert(dabs.every(p => Math.hypot(p[2], p[3]) <= 3.01));
});
check('Selection is non-destructive until moved; Cancel restores the original exactly', () => {
  reset(); block(); const before = image();
  selectRegion(rectangle(40, 40, 100, 100));
  assert(image() === before);
  moveSelection(100, 0); assert(pixel(60, 60) === '255,255,255,255');
  cancelSelection(); assert(image() === before);
});
check('Move and place removes the source and supports Undo', () => {
  reset(); block(); const before = image();
  selectRegion(rectangle(40, 40, 100, 100)); moveSelection(100, 0); commitSelection();
  assert(pixel(160, 60) === '255,0,0,255'); assert(pixel(60, 60) === '255,255,255,255');
  undo(); assert(image() === before);
});
check('Copy retains source; transparent paste preserves coloured destination', () => {
  reset(); block(); state.transparentSelection = true;
  selectRegion(rectangle(40, 40, 100, 100)); copySelection(); commitSelection();
  baseCtx.fillStyle = '#0000ff'; baseCtx.fillRect(440, 280, 80, 80);
  pasteSelection(); commitSelection();
  assert(pixel(60, 60) === '255,0,0,255');
  assert(pixel(452, 292) === '0,0,255,255', 'White paper must be transparent');
  assert(pixel(475, 315) === '255,0,0,255', 'Artwork must remain opaque');
});
check('Opaque paste restores white paper and Cut is undoable', () => {
  reset(); block(); state.transparentSelection = false;
  selectRegion(rectangle(40, 40, 100, 100)); const before = image(); cutSelection();
  assert(!hasSelection()); assert(pixel(60, 60) === '255,255,255,255');
  undo(); assert(image() === before);
  baseCtx.fillStyle = '#0000ff'; baseCtx.fillRect(440, 280, 80, 80);
  pasteSelection(); refreshTransparency(); commitSelection();
  assert(pixel(452, 292) === '255,255,255,255');
});
check('Lasso hit testing follows its outline, not its bounding rectangle', () => {
  reset(); selectRegion([{x:40,y:40},{x:140,y:40},{x:40,y:140}]);
  assert(hitSelection(50, 50)); assert(!hitSelection(135, 135));
  cancelSelection();
});
check('Selection at the canvas edge remains in bounds', () => {
  reset(); block(0, 0); selectRegion(rectangle(-20, -20, 60, 60));
  moveSelection(-100, -100); commitSelection(); assert(pixel(5, 5) === '255,0,0,255');
});
check('6, 10 and 12-way symmetry produce unique, equally distant copies', () => {
  for (const mode of ['6', '10', '12'] as const) {
    state.symmetry = mode; const points = mirrorPoints(610, 340);
    assert(points.length === Number(mode));
    assert(new Set(points.map(p => p.x.toFixed(3) + ':' + p.y.toFixed(3))).size === Number(mode));
    assert(points.every(p => Math.abs(Math.hypot(p.x - 480, p.y - 320) - Math.hypot(130, 20)) < 0.001));
  }
  state.symmetry = 'off';
});
check('Spline interpolates knots and handles closed and duplicate points', () => {
  const knots = [{x:10,y:10},{x:50,y:100},{x:120,y:20},{x:160,y:80}];
  const points = splinePoints(knots);
  assert(knots.every(k => points.some(p => Math.hypot(p.x-k.x, p.y-k.y) < 0.001)));
  const closed = splinePoints(knots, true); assert(Math.hypot(closed[0].x-closed.at(-1)!.x,closed[0].y-closed.at(-1)!.y)<0.001);
  assert(splinePoints([knots[0],knots[0],knots[1]]).every(p => Number.isFinite(p.x) && Number.isFinite(p.y)));
});
check('Glitter is coloured opaque paint with fixed flecks, unchanged between frames', () => {
  reset(); state.ink = 'sparkle'; state.sparkleTint = '#FFD166';
  beginStrokeGeneration(); segment(100, 100, 350, 100, 36, 0); bakeStaticStrokes(baseCtx);
  const before = image(); paintFrame(100); paintFrame(99999); assert(image() === before);
  const strip = baseCtx.getImageData(130, 95, 100, 10).data;
  const colours = new Set<string>(); for (let i=0;i<strip.length;i+=4) colours.add(`${strip[i]},${strip[i+1]},${strip[i+2]}`);
  assert(colours.size > 50, 'Glitter needs textured pigment');
  const view = document.querySelector<HTMLCanvasElement>('#view')!;
  paintFrame(0); const frame = view.toDataURL(); paintFrame(60000); assert(frame === view.toDataURL(), 'Glitter must never animate');
});
check('Bucket uses the same glitter pigment', () => {
  reset(); state.ink = 'sparkle'; floodAt(0, 0, null);
  assert(pixel(20, 20) !== '255,255,255,255');
});
check('Neon keeps a coloured, lighter centre along the stroke and stays fixed', () => {
  reset(); state.ink = 'neon'; state.neonTint = '#9450EF'; beginStrokeGeneration();
  for (let x = 100; x < 400; x += 2) segment(x, 200, x + 2, 200, 28, 0);
  bakeStaticStrokes(baseCtx);
  const centre = baseCtx.getImageData(180, 200, 1, 1).data;
  const rim = baseCtx.getImageData(180, 207, 1, 1).data;
  assert(Math.max(centre[0],centre[1],centre[2])-Math.min(centre[0],centre[1],centre[2])>90, 'Core must retain colour, not become white');
  assert(rim[1] < centre[1], 'Coloured halo should surround the core');
  const before = image(); paintFrame(50000); assert(image() === before);
});
check('Spiro resize changes drawing radius without changing the picture', () => {
  reset(); block(); const before = image(); setRingRadius(100); const small = penPosition(0)!;
  setRingRadius(200); const large = penPosition(0)!;
  assert(Math.abs(Math.hypot(large.x-480,large.y-320)/Math.hypot(small.x-480,small.y-320)-2)<0.001);
  assert(image() === before);
});


function paintedNear(x: number, y: number): boolean {
  const data = baseCtx.getImageData(Math.max(0,Math.round(x)-1), Math.max(0,Math.round(y)-1),3,3).data;
  for(let i=0;i<data.length;i+=4) if(Math.min(data[i],data[i+1],data[i+2])<235) return true;
  return false;
}
for (const ink of ['#E53935','rainbow','neon','sparkle']) {
  check('Thin Spiro curves have no missing segments with ' + ink, () => {
    reset(); state.tool='spiro'; state.ink=ink; state.brushWidth=4; state.spiro.R=180;
    state.spiro.outerTeeth=96;state.spiro.innerTeeth=36;state.spiro.gearId='red';state.spiro.hole=3;
    beginStrokeGeneration(); drawBetween(0,Math.PI*6); bakeStaticStrokes(baseCtx);
    let missing=0;
    for(let i=0;i<=1500;i++) { const p=penPosition(i/1500*Math.PI*6)!; if(!paintedNear(p.x,p.y))missing++; }
    assert(missing === 0, missing + ' missing samples along the gear curve');
  });
}
check('Shape preview and committed neon use the same continuous rendering', () => {
  reset(); state.tool='shapes';state.ink='neon';state.brushWidth=18;
  const expected=cloneCanvas(base);drawShape('circle',280,260,420,260,expected.getContext('2d')!,false);
  beginStrokeGeneration();drawShape('circle',280,260,420,260,baseCtx,true);bakeStaticStrokes(baseCtx);
  assert(expected.toDataURL()===image(),'Preview differs from committed shape');
});
check('Shapes restore a brush after spray, including with live ink', () => {
  reset();state.applicator='mist';state.brushApplicator='marker';state.tool='shapes';state.liveArmed=true;
  beginStrokeGeneration();drawShape('line',100,200,500,200,baseCtx,true);
  assert(strokes.every(s=>s.applicator==='marker'),'Spray must not leak into line tools');
});
check('Low-opacity lines have uniform coverage, not repeated dark dabs', () => {
  reset();state.opacity=0.4;beginStrokeGeneration();
  for(let x=100;x<500;x+=3)segment(x,200,x+3,200,24,0);
  bakeStaticStrokes(baseCtx);
  const reference=pixel(150,200);
  for(let x=151;x<460;x++)assert(pixel(x,200)===reference,'Opacity band at '+x);
});
check('A long neon path remains one connected stroke beyond 4000 samples', () => {
  reset();state.ink='neon';beginStrokeGeneration();
  for(let i=0;i<5000;i++)segment(100+i*0.1,200,100+(i+1)*0.1,200,12,0);
  assert(strokes.length===1,'Premature stroke splitting causes seams');
  bakeStaticStrokes(baseCtx);assert(paintedNear(500,200));
});
check('Rainbow colour changes smoothly along a thin straight line', () => {
  reset();state.ink='rainbow';beginStrokeGeneration();
  for(let x=100;x<800;x+=2)segment(x,200,x+2,200,6,0);
  bakeStaticStrokes(baseCtx);
  const data=baseCtx.getImageData(120,200,650,1).data;
  for(let i=4;i<data.length;i+=4) {
    const change=Math.max(...[0,1,2].map(c=>Math.abs(data[i+c]-data[i-4+c])));
    assert(change<16,'Colour seam: '+change);
  }
});
check('Glitter has a dense centre and a patchy, stationary edge falloff', () => {
  const points=[{x:100,y:200,w:40},{x:700,y:200,w:40}];
  const paint={kind:'glitter' as const,color:'#FFD166',applicator:'marker' as const};
  const result=renderPaintPath(points,paint)!;
  const ctx=result.canvas.getContext('2d')!;
  const line=(yy:number)=>Array.from(ctx.getImageData(150-result.x,yy-result.y,500,1).data).filter((_,i)=>i%4===3);
  const centre=line(200),edge=line(219),outer=line(226);
  assert(centre.every(a=>a>250),'Centre should remain opaque');
  const average=(a:number[])=>a.reduce((s,v)=>s+v,0)/a.length;
  assert(average(edge)>average(outer) && average(edge)<average(centre),'Edge must fall away');
  assert(new Set(edge).size>5 && Math.max(...edge)-Math.min(...edge)>70,'Falloff must retain irregular pigment flecks');
  const repeated=renderPaintPath(points,paint)!.canvas.getContext('2d')!.getImageData(0,0,result.canvas.width,result.canvas.height).data;
  const first=ctx.getImageData(0,0,result.canvas.width,result.canvas.height).data;
  let maxChange=0;for(let i=0;i<first.length;i++)maxChange=Math.max(maxChange,Math.abs(first[i]-repeated[i]));
  // GPU/CPU premultiplied-alpha readback can round a channel by one level.
  assert(maxChange<=1,'Texture moved between identical renders: max channel change '+maxChange);
});

for(const mode of ['4','6','8','10','12'] as const) {
  check(mode+'-section symmetry alternates mirror images, including motion',()=>{
    state.symmetry=mode;
    const points=mirrorPoints(610,340),motion=mirrorMotion(610,340,3,7),sector=Math.PI*2/Number(mode);
    const transforms=symmetryTransforms();
    for(let i=0;i<points.length;i++) {
      const t=transforms[i];
      assert(Math.abs(t.a*t.d-t.b*t.c-(i%2?-1:1))<1e-9,'Adjacent sectors must have opposite handedness');
      const next=points[(i+1)%points.length],angle=2*(i+1)*sector;
      const x=points[i].x-480,y=points[i].y-320;
      assert(Math.hypot(480+Math.cos(angle)*x+Math.sin(angle)*y-next.x,320+Math.sin(angle)*x-Math.cos(angle)*y-next.y)<1e-8,'Neighbour is not a mirror');
      assert(Math.abs(Math.hypot(motion[i].dx,motion[i].dy)-Math.sqrt(58))<1e-8,'Push length changed');
    }
  });
  check('Smudge pushes paint in every '+mode+'-way mirror and Undo restores it',()=>{
    reset();state.symmetry=mode;
    const x=620,y=357;
    beginStrokeGeneration();segment(x,y,x,y,16,0);bakeStaticStrokes(baseCtx);
    const before=image();beginBake();
    const path=new SmudgePath(x,y,25,(px,py,dx,dy)=>smudge(px,py,dx,dy,25));
    for(let i=1;i<=18;i++)path.move(x+i,y+i*0.25);
    path.move(x+18,y+4.5,true);
    for(const p of mirrorPoints(x+17,y+4.25))assert(paintedNear(p.x,p.y),'A mirrored section was not smudged');
    assert(image()!==before);undo();assert(image()===before,'Smudge should undo as one action');
  });
}
check('Stamps reflect their artwork as well as their position',()=>{
  reset();state.symmetry='h';state.stampId='vec:triangle';state.stampSpin='fixed';state.stampScale=0.5;
  placeStamp(180,140);
  const upper=baseCtx.getImageData(158,115,44,50).data,lower=baseCtx.getImageData(158,475,44,50).data;
  let totalDifference=0,maxDifference=0;
  for(let y=0;y<50;y++)for(let x=0;x<44;x++)for(let c=0;c<4;c++) {
    const difference=Math.abs(upper[(y*44+x)*4+c]-lower[((49-y)*44+x)*4+c]);
    totalDifference+=difference;maxDifference=Math.max(maxDifference,difference);
  }
  // Mirrored vector edges can rasterize differently on GPU and CPU canvases.
  // Compare the whole silhouette with a small mean tolerance, not byte equality.
  assert(totalDifference/upper.length<2 && maxDifference<80,'Stamp orientation must reflect too: '+totalDifference+' total, '+maxDifference+' max');
});
check('Overlapping mirror smudges are independent of section order',()=>{
  const w=70,h=70,src=new Uint8ClampedArray(w*h*4);
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){const i=(y*w+x)*4;src[i]=x*3;src[i+1]=y*3;src[i+2]=80;src[i+3]=255;}
  const dabs=[{x:31,y:35,dx:3,dy:2},{x:39,y:35,dx:-3,dy:2},{x:35,y:31,dx:2,dy:3},{x:35,y:39,dx:2,dy:-3}];
  const a=advectMany(src,w,h,dabs,18,0.9),b=advectMany(src,w,h,[...dabs].reverse(),18,0.9);
  assert(a.every((v,i)=>Math.abs(v-b[i])<=1),'Overlaps must use the same source');
});
check('Neon lifts muted colours and shades the centre without a white stripe',()=>{
  for(const color of ['#E53935','#43A047','#118AB2','#9D4EDD','#845125']) {
    const rgb=hexToRgb(neonColor(color))!;
    assert(Math.max(rgb.r,rgb.g,rgb.b)===255 && Math.min(rgb.r,rgb.g,rgb.b)<40,'Neon should be bright and saturated');
    const result=renderPaintPath([{x:100,y:200,w:40},{x:700,y:200,w:40}],{kind:'neon',color,applicator:'marker'})!;
    const ctx=result.canvas.getContext('2d')!;
    const pixels=ctx.getImageData(300-result.x,200-result.y,1,28).data;
    const core=[pixels[0],pixels[1],pixels[2]];
    assert(Math.max(...core)-Math.min(...core)>100,'Core lost its hue');
    for(let y=1;y<11;y++)for(let c=0;c<3;c++)assert(Math.abs(pixels[y*4+c]-pixels[(y-1)*4+c])<24,'Hard interior colour edge');
    assert(pixels[25*4+3]>0 && pixels[25*4+3]<pixels[0*4+3],'Glow should bleed softly outside');
  }
});


check('Every symmetry slice can be chosen and contains its own centre line',()=>{
  for(const mode of ['v','h','4','6','8','10','12'] as const) {
    state.symmetry=mode;state.symmetryMask=true;
    for(let slice=0;slice<sliceCount();slice++) {
      state.symmetrySlice=slice;
      const a=(mode==='v'?-Math.PI/2:0)+(slice+0.5)*Math.PI*2/sliceCount();
      const x=480+Math.cos(a)*120,y=320+Math.sin(a)*120;
      assert(sliceAt(x,y)===slice && insideSector(x,y));
      assert(!insideSector(960-x,640-y));
      assert(sectorPolygon(activeSector()!).length>=3);
    }
  }
  reset();
});
check('Mask clips a crossing stroke at the seam and rejects an outside stroke',()=>{
  reset();state.symmetry='4';state.symmetryMask=true;
  const clipped=clipSegment({x:600,y:350},{x:660,y:290})!;
  assert(Math.abs(clipped[1].x-630)<0.001 && Math.abs(clipped[1].y-320)<0.001);
  assert(!clipSegment({x:600,y:250},{x:660,y:290}));
});
check('Tools whose footprints do not reach the working slice leave the picture unchanged',()=>{
  reset();block(560,180);state.symmetry='4';state.symmetryMask=true;
  const before=image();beginStrokeGeneration();dot(580,200,48);sprayCloud(580,200,0);placeStamp(580,200);floodAt(580,200,null);smudge(580,200,8,2,30);bakeStaticStrokes(baseCtx);
  assert(image()===before,'An inactive slice accepted an action');
});
for(const ink of ['#E53935','neon','sparkle'])check('Masked '+ink+' brush edges do not overpaint the working slice',()=>{
  reset();state.ink=ink;state.opacity=0.5;beginStrokeGeneration();segment(600,324,660,336,32,0);bakeStaticStrokes(baseCtx);
  const expected=baseCtx.getImageData(585,325,90,30).data;
  reset();state.ink=ink;state.opacity=0.5;state.symmetry='4';state.symmetryMask=true;
  beginStrokeGeneration();segment(600,324,660,336,32,0);bakeStaticStrokes(baseCtx);
  const actual=baseCtx.getImageData(585,325,90,30).data;
  assert(actual.every((v,i)=>Math.abs(v-expected[i])<=2),'A reflected brush tip spilled back across the seam');
});
check('Masked eraser makes mirrored edge cuts and leaves unrelated paper intact',()=>{
  reset();baseCtx.fillStyle='#446688';baseCtx.fillRect(0,0,W,H);const before=image();
  state.symmetry='4';state.symmetryMask=true;state.tool='eraser';state.eraserMode='scrub';beginBake();beginStrokeGeneration();
  segment(620,340,660,280,20,0);
  assert(pixel(620,340)==='255,255,255,255' && pixel(339,299)==='255,255,255,255','Cuts should mirror');
  assert(pixel(670,280)==='68,102,136,255','Slip outside the active wedge drew another cut');
  undo();assert(image()===before);
});
check('Live ink remembers its mask after toggling the mask off and restoring Undo data',()=>{
  reset();state.symmetry='4';state.symmetryMask=true;state.liveArmed=true;
  beginStrokeGeneration();segment(600,324,660,336,32,0);
  assert(strokes.length===4 && strokes.every(s=>s.clip?.length));
  const snapshot=snapshotLive();state.symmetryMask=false;restoreLive(snapshot);
  assert(strokes.every(s=>s.clip?.length),'Saved clips were lost');
});
check('Masked bucket uses the slice boundary as a fill barrier',()=>{
  reset();state.symmetry='4';state.symmetryMask=true;
  const pixels=baseCtx.getImageData(0,0,W,H).data;
  const mask=floodMask(pixels,600,400,(x,y)=>insideSector(x+0.5,y+0.5))!;
  assert(mask[400*W+600]===1 && mask[200*W+600]===0 && mask[400*W+200]===0);
  floodAt(600,400,null);
  assert(pixel(600,400)==='229,57,53,255' && pixel(359,239)==='229,57,53,255');
});
reset();


// Exercise the real input handlers in a sized, invisible canvas fixture.
initInput();
const inputStage=document.querySelector<HTMLElement>('#stage')!;
const oldStageStyle=inputStage.style.cssText,oldViewStyle=view.style.cssText;
const oldCapture=view.setPointerCapture;
inputStage.style.cssText='display:block;position:fixed;left:0;top:0;width:960px;height:640px;opacity:0;pointer-events:none';
view.style.cssText='width:960px;height:640px;border:0';
view.setPointerCapture=()=>{}; // Synthetic test pointers have no native capture target.
function pointer(type:string,x:number,y:number) {
  const r=view.getBoundingClientRect();
  view.dispatchEvent(new PointerEvent(type,{pointerId:77,button:0,buttons:type==='pointerup'?0:1,clientX:r.left+x,clientY:r.top+y}));
}
check('The first click chooses the slice; the next stroke can start outside and paint on entry',()=>{
  reset();state.symmetry='8';state.symmetryMask=true;state.choosingSlice=true;
  const before=image();pointer('pointerdown',600,360);pointer('pointerup',600,360);
  assert(!state.choosingSlice && state.symmetrySlice===0 && image()===before);
  pointer('pointerdown',600,200);pointer('pointermove',650,370);pointer('pointerup',650,370);
  assert(image()!==before && paintedNear(650,370),'A stroke starting outside did not enter the slice');
  assert(pixel(600,200)==='255,255,255,255','The masked-away start was painted');
});
check('A brush can leave and re-enter while the mask clips the hidden part of its path',()=>{
  reset();state.symmetry='4';state.symmetryMask=true;state.brushWidth=8;
  pointer('pointerdown',600,360);pointer('pointermove',640,360);pointer('pointermove',640,290);
  pointer('pointermove',700,280);pointer('pointermove',700,360);pointer('pointerup',740,360);
  assert(paintedNear(610,360) && paintedNear(725,360));
  assert(pixel(670,360)==='255,255,255,255','Re-entry bridged the skipped portion');
});
check('Spray held beyond reach of the selected slice leaves it untouched',()=>{
  reset();state.symmetry='4';state.symmetryMask=true;state.tool='spray';state.applicator='mist';
  pointer('pointerdown',630,350);pointer('pointermove',630,280);
  const before=image();tickSpray();tickSpray();pointer('pointerup',630,280);
  assert(image()===before,'Spray kept firing at the last boundary point');
});

check('A brush outside the slice can paint with its edge and mirror only the clipped footprint',()=>{
  reset();state.symmetry='4';state.symmetryMask=true;state.brushWidth=32;
  pointer('pointerdown',600,310);pointer('pointermove',640,310);pointer('pointerup',680,310);
  assert(paintedNear(640,323),'Brush edge did not reach into the working slice');
  assert(paintedNear(320,317),'Clipped edge was not mirrored');
  assert(pixel(640,305)==='255,255,255,255','Masked centre left paint behind');
  assert(pixel(640,340)==='255,255,255,255','Brush footprint was projected into the slice');
});
check('Spray can start in a masked region and spray across the boundary',()=>{
  reset();state.symmetry='4';state.symmetryMask=true;state.tool='spray';state.applicator='mist';state.brushWidth=20;
  const random=Math.random;Math.random=()=>0.25;
  try{pointer('pointerdown',600,305);tickSpray();pointer('pointerup',600,305);}finally{Math.random=random;}
  assert(paintedNear(600,340),'Outside spray nozzle was blocked');
  assert(pixel(600,305)==='255,255,255,255','Spray escaped its mask');
});
check('A shape can begin outside the slice and use its stroke edge inside it',()=>{
  reset();state.symmetry='4';state.symmetryMask=true;state.tool='shapes';state.shape='line';state.brushWidth=32;
  pointer('pointerdown',600,310);pointer('pointermove',680,310);pointer('pointerup',680,310);
  assert(paintedNear(640,323),'Shape edge was clipped by its centre line');
  assert(pixel(640,300)==='255,255,255,255');
});
check('Selection can start outside the slice and captures only its interior intersection',()=>{
  reset();block(600,330);state.symmetry='4';state.symmetryMask=true;state.tool='scissors';state.selectionMode='rect';
  pointer('pointerdown',590,290);pointer('pointermove',650,380);pointer('pointerup',650,380);
  assert(hasSelection() && hitSelection(620,350) && !hitSelection(620,310));cancelSelection();
});
check('A held bucket can enter the selected slice from outside',()=>{
  reset();state.symmetry='4';state.symmetryMask=true;state.tool='bucket';state.gradientDrag=false;
  pointer('pointerdown',600,200);assert(pixel(600,400)==='255,255,255,255');
  pointer('pointermove',600,400);pointer('pointerup',600,400);
  assert(pixel(600,400)==='229,57,53,255','Bucket did not enter the slice');
});

check('A gradient drag can enter the selected slice from outside',()=>{
  reset();state.symmetry='4';state.symmetryMask=true;state.tool='bucket';state.gradientDrag=true;
  pointer('pointerdown',600,280);pointer('pointermove',600,400);pointer('pointerup',600,400);
  assert(getPending(),'Gradient did not find a seed inside the mask');
  cancelPending();state.gradientDrag=false;
});
inputStage.style.cssText=oldStageStyle;view.style.cssText=oldViewStyle;view.setPointerCapture=oldCapture;

check('Stamps outside the slice still contribute the portion that crosses its boundary',()=>{
  reset();state.symmetry='4';state.symmetryMask=true;state.stampId='vec:star';state.stampScale=1;state.stampSpin='fixed';
  placeStamp(620,310);
  assert(paintedNear(620,328),'Stamp edge was discarded with its centre');
  assert(pixel(620,270)==='255,255,255,255','Stamp leaked outside the mirrored footprint');
});
check('Smudge centred outside the slice can push pigment along its inner edge',()=>{
  reset();baseCtx.fillStyle='#ff0000';baseCtx.fillRect(590,320,30,30);
  state.symmetry='4';state.symmetryMask=true;smudge(620,312,8,0,30);
  const p=baseCtx.getImageData(622,324,1,1).data;
  assert(p[1]<250,'Outside smudge did not push interior pigment');
  assert(pixel(622,280)==='255,255,255,255');
});


check('Eraser filters centred outside the mask affect only their clipped mirrored footprint',()=>{
  reset();state.symmetry='4';state.symmetryMask=true;state.brushWidth=24;
  baseCtx.fillStyle='#204060';baseCtx.fillRect(0,0,W,H);
  invertAt(620,310);
  assert(pixel(620,325)==='223,191,159,255','Filter did not cross into the slice');
  assert(pixel(340,315)==='223,191,159,255','Filter was not mirrored');
  assert(pixel(620,280)==='32,64,96,255','Filter leaked outside its mirrored footprint');
});
check('Black-hole eraser can cut in from outside without leaking past the mask',()=>{
  reset();state.symmetry='4';state.symmetryMask=true;
  baseCtx.fillStyle='#204060';baseCtx.fillRect(0,0,W,H);const before=image();
  startHole(620,300);tickHole(700);
  assert(pixel(620,330)==='255,255,255,255','Outside hole did not cut into the slice');
  assert(pixel(620,260)==='32,64,96,255','Hole escaped its clipped footprint');
  undo();assert(image()===before);
});

check('Masked smudge does not pull pigment from the inactive side of a seam',()=>{
  reset();baseCtx.fillStyle='#0000ff';baseCtx.fillRect(0,0,W,H);baseCtx.fillStyle='#ff0000';baseCtx.fillRect(480,320,480,320);
  state.symmetry='4';state.symmetryMask=true;
  smudge(620,324,0,7,20);
  const p=baseCtx.getImageData(620,321,1,1).data;
  assert(p[0]>230 && p[2]<25,'Inactive blue pigment entered the working slice');
});
reset();

check('Masked shape preview matches the clipped committed outline',()=>{
  reset();state.symmetry='4';state.symmetryMask=true;state.tool='shapes';state.ink='neon';state.brushWidth=18;
  const expected=cloneCanvas(base);drawShape('circle',620,325,675,325,expected.getContext('2d')!,false);
  beginStrokeGeneration();drawShape('circle',620,325,675,325,baseCtx,true);bakeStaticStrokes(baseCtx);
  const a=expected.getContext('2d')!.getImageData(0,0,W,H).data,b=baseCtx.getImageData(0,0,W,H).data;
  assert(a.every((v,i)=>Math.abs(v-b[i])<=2),'Clipped preview differs from the drawing');
});
reset();


check('Masked rectangle copying excludes pixels across the boundary',()=>{
  reset();state.transparentSelection=false;
  baseCtx.fillStyle='#0000ff';baseCtx.fillRect(600,280,100,40);
  baseCtx.fillStyle='#ff0000';baseCtx.fillRect(600,320,100,60);
  state.symmetry='4';state.symmetryMask=true;
  selectRegion(rectangle(610,290,690,370));
  assert(!hitSelection(650,310) && hitSelection(650,340));
  copySelection();cancelSelection();state.symmetryMask=false;state.symmetry='off';
  baseCtx.fillStyle='#ffffff';baseCtx.fillRect(0,0,W,H);pasteSelection();commitSelection();
  const pixels=baseCtx.getImageData(0,0,W,H).data;
  let red=0,blue=0;for(let i=0;i<pixels.length;i+=4){if(pixels[i]>240&&pixels[i+2]<10)red++;if(pixels[i]<10&&pixels[i+2]>240)blue++;}
  assert(red>3000 && blue===0,'Clipboard included the inactive side');
});
check('Masked lasso cut reflects the source outline, preserves neighbours and supports Undo',()=>{
  reset();baseCtx.fillStyle='#2468bb';baseCtx.fillRect(0,0,W,H);const before=image();
  state.symmetry='4';state.symmetryMask=true;
  selectRegion([{x:600,y:290},{x:700,y:350},{x:600,y:380}]);cutSelection();
  for(const p of mirrorPoints(620,345))assert(pixel(Math.round(p.x),Math.round(p.y))==='255,255,255,255');
  assert(pixel(690,280)==='36,104,187,255','An inactive lasso fragment was cut');
  undo();assert(image()===before);
});
check('Masked paste previews and commits identically in every symmetry mode and source slice',()=>{
  for(const mode of ['v','h','4','6','8','10','12'] as const)for(let slice=0;slice<sliceCount(mode);slice++){
    reset();state.transparentSelection=true;block(50,50);selectRegion(rectangle(50,50,90,90));copySelection();cancelSelection();
    baseCtx.fillStyle='#ffffff';baseCtx.fillRect(0,0,W,H);
    state.symmetry=mode;state.symmetryMask=true;state.symmetrySlice=slice;
    pasteSelection();
    const expected=cloneCanvas(base);renderSelection(expected.getContext('2d')!);
    const polygon=sectorPolygon(activeSector()!);
    const center=polygon.reduce((sum,p)=>({x:sum.x+p.x/polygon.length,y:sum.y+p.y/polygon.length}),{x:0,y:0});
    assert(hitSelection(center.x,center.y),'Paste not inside chosen slice '+mode+':'+slice);
    assert(!hitSelection(W-center.x,H-center.y),'Inactive mirror is draggable');
    commitSelection();assert(image()===expected.toDataURL(),'Preview changed at commit');
    for(const p of mirrorPoints(center.x,center.y))if(p.x>1&&p.x<W-1&&p.y>1&&p.y<H-1){
      const rgba=baseCtx.getImageData(Math.round(p.x),Math.round(p.y),1,1).data;
      assert(rgba[0]>240&&rgba[1]<10,'Missing pasted mirror '+mode+':'+slice);
    }
  }
});
check('Moving and copying a masked selection cannot include its hidden overhang',()=>{
  reset();state.transparentSelection=false;block(600,340);state.symmetry='4';state.symmetryMask=true;
  selectRegion(rectangle(600,340,640,380));moveSelection(0,-40);copySelection();commitSelection();
  assert(pixel(620,330)==='255,0,0,255' && pixel(620,290)==='255,255,255,255');
  state.symmetryMask=false;state.symmetry='off';baseCtx.fillStyle='#ffffff';baseCtx.fillRect(0,0,W,H);
  pasteSelection();commitSelection();
  assert(pixel(480,310)==='255,255,255,255' && pixel(480,330)==='255,0,0,255','Hidden overhang survived copy');
});
check('Rainbow watercolour blends smoothly where a path doubles back over earlier pigment',()=>{
  const points=[{x:100,y:200,w:48},{x:400,y:200,w:48},{x:400,y:250,w:48},{x:150,y:250,w:48}];
  const bitmap=renderPaintPath(points,{kind:'rainbow',color:'#ff0000',applicator:'watercolor'})!;
  const canvas=cloneCanvas(base),ctx=canvas.getContext('2d')!;
  ctx.fillStyle='#4964a4';ctx.fillRect(0,0,W,H);ctx.drawImage(bitmap.canvas,bitmap.x,bitmap.y);
  const data=ctx.getImageData(130,185,210,45).data;
  let jump=0;for(let y=0;y<45;y++)for(let x=1;x<210;x++)for(let c=0;c<3;c++)jump=Math.max(jump,Math.abs(data[(y*210+x)*4+c]-data[(y*210+x-1)*4+c]));
  assert(jump<12,'Hard colour step of '+jump+' levels away from brush');
});
check('Rainbow watercolour is stable across sparse and dense pointer samples',()=>{
  const paint={kind:'rainbow' as const,color:'#ff0000',applicator:'watercolor' as const};
  const sparse=renderPaintPath([{x:100,y:200,w:40},{x:700,y:200,w:40}],paint)!;
  const dense=renderPaintPath(Array.from({length:601},(_,i)=>({x:100+i,y:200,w:40})),paint)!;
  const a=sparse.canvas.getContext('2d')!.getImageData(0,0,sparse.canvas.width,sparse.canvas.height).data;
  const b=dense.canvas.getContext('2d')!.getImageData(0,0,dense.canvas.width,dense.canvas.height).data;
  let difference=0;
  for(let i=0;i<a.length;i+=4){
    difference=Math.max(difference,Math.abs(a[i+3]-b[i+3]));
    for(let c=0;c<3;c++)difference=Math.max(difference,Math.abs(a[i+c]*a[i+3]/255-b[i+c]*b[i+3]/255));
  }
  assert(difference<=3,'Visible pigment differs by '+difference+' levels with event frequency');
});
reset();


// Compare successive frames, not just the smoothness of a finished picture.
for (const applicator of ['marker','watercolor'] as const) {
  check('Extending rainbow '+applicator+' cannot recolour pixels outside the new brush footprint',()=>{
    const paint={kind:'rainbow' as const,color:'#ff0000',applicator};
    const prefix=[{x:120,y:200,w:40},{x:720,y:200,w:40},{x:720,y:236,w:40},{x:660,y:236,w:40}];
    const end={x:160,y:236,w:40};
    function frame(points:typeof prefix, paper:boolean){
      const c=document.createElement('canvas');c.width=W;c.height=H;const ctx=c.getContext('2d')!;
      if(paper){ctx.fillStyle='#4964a4';ctx.fillRect(0,0,W,H);}
      const b=renderPaintPath(points,paint)!;ctx.drawImage(b.canvas,b.x,b.y);
      return ctx.getImageData(0,0,W,H).data;
    }
    const before=frame(prefix,true),after=frame([...prefix,end],true);
    const footprint=frame([prefix.at(-1)!,end],false);
    let drift=0,checked=0;
    for(let y=180;y<=215;y++)for(let x=210;x<580;x++){
      const i=(y*W+x)*4;
      if(footprint[i+3]>1)continue;
      checked++;
      for(let c=0;c<3;c++)drift=Math.max(drift,Math.abs(after[i+c]-before[i+c]));
    }
    assert(checked>1000,'Must check previously painted pixels beyond the new tip');
    assert(drift<=2,'Previously painted pixels changed by '+drift+' levels outside the brush');
  });
  check('Closing a rainbow '+applicator+' loop does not recolour the rest of the stroke',()=>{
    const paint={kind:'rainbow' as const,color:'#ff0000',applicator};
    const points=[{x:150,y:150,w:24},{x:650,y:150,w:24},{x:650,y:450,w:24},{x:150,y:450,w:24},{x:150,y:160,w:24}];
    const a=renderPaintPath(points,paint)!,b=renderPaintPath([...points,{x:150,y:150,w:24}],paint)!;
    const before=a.canvas.getContext('2d')!.getImageData(450-a.x,145-a.y,100,10).data;
    const after=b.canvas.getContext('2d')!.getImageData(450-b.x,145-b.y,100,10).data;
    assert(before.every((v,i)=>Math.abs(v-after[i])<=2),'Closing the loop changed earlier colours');
  });
}


for(const applicator of ['marker','watercolor','biro','gouache','callig'] as const){
  check('Incremental rainbow '+applicator+' matches a single render, including opacity and crossings',()=>{
    reset();state.ink='rainbow';state.applicator=applicator;state.opacity=0.4;
    const points=Array.from({length:241},(_,i)=>({x:200+i*1.6,y:260+Math.sin(i/20)*65,w:24}));
    const expected=cloneCanvas(base),expectedCtx=expected.getContext('2d')!;
    const bitmap=renderPaintPath(points,{kind:'rainbow',color:'#ff0000',applicator})!;
    expectedCtx.globalAlpha=0.4;expectedCtx.drawImage(bitmap.canvas,bitmap.x,bitmap.y);
    beginStrokeGeneration();
    const scratch=cloneCanvas(base),ctx=scratch.getContext('2d')!;
    for(let i=1;i<points.length;i++){
      const a=points[i-1],b=points[i];segment(a.x,a.y,b.x,b.y,24,0);
      if(i%7===0){ctx.clearRect(0,0,W,H);renderLive(ctx,0);}
    }
    assert(strokes.length===1 && strokes[0].points.length===1,'Retained a growing point history');
    bakeStaticStrokes(baseCtx);
    const actual=baseCtx.getImageData(0,0,W,H).data,reference=expectedCtx.getImageData(0,0,W,H).data;
    let difference=0;for(let i=0;i<actual.length;i++)difference=Math.max(difference,Math.abs(actual[i]-reference[i]));
    assert(difference<=3,'Frame batching changed pigment by '+difference+' levels');
  });
}
check('A prolonged rainbow gesture keeps one point and Undo restores the whole gesture',()=>{
  reset();state.ink='rainbow';state.applicator='marker';const before=image();pushHistory();beginStrokeGeneration();
  let x=400,y=320;
  for(let i=1;i<=60000;i++){
    const nx=480+Math.sin(i/80)*160,ny=320+Math.cos(i/107)*100;
    segment(x,y,nx,ny,12,0);x=nx;y=ny;
  }
  assert(strokes.length===1 && strokes[0].points.length===1 && !!strokes[0].rainbow,'Rainbow history grew with duration');
  bakeStaticStrokes(baseCtx);assert(image()!==before);undo();assert(image()===before);
});
check('An active rainbow snapshot restores both its pixels and continuing hue without retained history',()=>{
  reset();state.ink='rainbow';state.applicator='watercolor';beginStrokeGeneration();
  segment(100,200,480,200,32,0);const snapshot=snapshotLive();
  segment(480,200,720,300,32,0);const expected=cloneCanvas(base);renderLive(expected.getContext('2d')!,0);
  restoreLive(snapshot);segment(480,200,720,300,32,0);
  const actual=cloneCanvas(base);renderLive(actual.getContext('2d')!,0);
  assert(actual.toDataURL()===expected.toDataURL(),'Restored snapshot lost pigment, spacing or hue phase');
  assert(snapshot.strokes[0].points.length===1 && strokes[0].points.length===1);
});
check('A long masked rainbow stroke retains one point per lane and bakes without changing its preview',()=>{
  reset();state.ink='rainbow';state.symmetry='12';state.symmetryMask=true;beginStrokeGeneration();
  let x=620,y=350;
  for(let i=1;i<=1500;i++){
    const nx=650+Math.sin(i/30)*30,ny=360+Math.sin(i/47)*9;
    segment(x,y,nx,ny,10,0);x=nx;y=ny;
  }
  assert(strokes.length===12 && strokes.every(stroke=>stroke.points.length===1),'Symmetry retained gesture history');
  const preview=cloneCanvas(base);renderLive(preview.getContext('2d')!,0);bakeStaticStrokes(baseCtx);
  assert(preview.toDataURL()===image(),'Release changed masked pigment');
});
reset();


check('Clear confirmation ages the picture from its first edit, not from opening the app',()=>{
  let now=500000;const age=new ArtworkAge(()=>now);
  assert(!age.needsClearConfirmation(),'An idle blank page should not warn');
  age.markWork();now+=120000;assert(!age.needsClearConfirmation());
  now++;assert(age.needsClearConfirmation(),'Work older than two minutes needs confirmation');
  age.markWork();assert(age.needsClearConfirmation(),'More edits restarted the timer');
  age.reset();assert(!age.needsClearConfirmation());
});
check('Clear dialog defaults to keeping the picture, and only confirmation clears older work',()=>{
  let now=0,clears=0;const age=new ArtworkAge(()=>now);
  const trigger=document.createElement('button');document.body.append(trigger);
  const dialog=bindClearConfirmation(trigger,()=>{clears++;age.reset();},age);
  age.markWork();now=120001;trigger.click();
  assert(dialog.open && clears===0);
  assert(document.activeElement===dialog.querySelector('.keep-picture'),'Keep drawing should receive focus');
  (dialog.querySelector('.keep-picture') as HTMLButtonElement).click();
  assert(!dialog.open && clears===0 && age.needsClearConfirmation(),'Cancel changed the picture age');
  trigger.click();(dialog.querySelector('.clear-picture') as HTMLButtonElement).click();
  assert(!dialog.open && Number(clears)===1 && !age.needsClearConfirmation());
  trigger.click();assert(Number(clears)===2 && !dialog.open,'Fresh work should clear directly');
  dialog.remove();trigger.remove();
});
check('Undo after Clear restores the picture age as well as its pixels',()=>{
  reset();block();const before=image();artwork.restore(performance.now()-130000);
  startSqueegee();tickSqueegee(1100);assert(!artwork.needsClearConfirmation());
  undo();assert(image()===before && artwork.needsClearConfirmation());
});
for(const applicator of ['mist','splatter','confetti'] as const){
  check('Rainbow '+applicator+' produces many colours while spraying in one place',()=>{
    reset();state.ink='rainbow';state.applicator=applicator;state.brushWidth=32;
    const random=Math.random;let seed=137;
    Math.random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
    try{beginStrokeGeneration();for(let i=0;i<16;i++)sprayCloud(480,320,0);}finally{Math.random=random;}
    const data=baseCtx.getImageData(340,180,280,280).data;
    const hues=new Set<number>();
    for(let i=0;i<data.length;i+=4){
      const r=data[i],g=data[i+1],b=data[i+2],hi=Math.max(r,g,b),lo=Math.min(r,g,b),delta=hi-lo;
      if(delta<20)continue;
      const hue=hi===r?((g-b)/delta+6)%6:hi===g?(b-r)/delta+2:(r-g)/delta+4;
      hues.add(Math.floor(hue));
    }
    assert(hues.size>=5,'Spray did not span the rainbow: '+[...hues]);
    const before=image();paintFrame(100);paintFrame(10000);assert(image()===before,'Sprayed pigment animated');
  });
}
reset();

// A persistent sample sheet for inspecting pigment and smudge quality.
reset();
baseCtx.font = '18px system-ui'; baseCtx.fillStyle = '#263047';
for (const [text, y] of [['Poster paint',35],['Neon',145],['Glitter',255],['Smudge — a soft directional push',365],['Confetti',535]] as const) baseCtx.fillText(text, 30, y);
for (let x=50;x<880;x+=3) paintStroke(baseCtx,x,80+Math.sin(x/70)*12,x+3,80+Math.sin((x+3)/70)*12,32,'#DA4467',1,'gouache',false);
state.neonTint = '#9450EF';
state.ink = 'neon'; beginStrokeGeneration();
for (let x=50;x<880;x+=3) segment(x,190+Math.sin(x/70)*12,x+3,190+Math.sin((x+3)/70)*12,28,0);
bakeStaticStrokes(baseCtx);
state.ink = 'sparkle'; state.sparkleTint='#FFD166'; beginStrokeGeneration();
for (let x=50;x<880;x+=3) segment(x,300+Math.sin(x/70)*12,x+3,300+Math.sin((x+3)/70)*12,32,0);
bakeStaticStrokes(baseCtx);
baseCtx.fillStyle='#287DCE'; baseCtx.fillRect(50,395,400,85); baseCtx.fillStyle='#F39F54'; baseCtx.fillRect(450,395,430,85);
const path = new SmudgePath(425,435,42,(x,y,dx,dy)=>smudge(x,y,dx,dy,42));
for(let x=425;x<640;x+=2)path.move(x,435+Math.sin((x-425)/60)*15);path.move(640,430,true);
state.applicator='confetti'; state.brushWidth=22; state.ink='rainbow';
for(let x=70;x<860;x+=20)sprayCloud(x,580,0);
document.querySelector('#gallery')!.append(cloneCanvas(base));

// Thin line and gear samples expose gaps that a thick straight brush sample hides.
reset();state.brushWidth=5;state.spiro.R=175;state.spiro.cx=250;state.spiro.cy=285;
state.ink='rainbow';state.tool='spiro';beginStrokeGeneration();drawBetween(0,Math.PI*6);bakeStaticStrokes(baseCtx);
state.ink='neon';state.neonTint='#0A9BAA';state.spiro.cx=710;beginStrokeGeneration();drawBetween(0,Math.PI*6);bakeStaticStrokes(baseCtx);
state.tool='shapes';state.ink='rainbow';state.brushWidth=12;beginStrokeGeneration();drawShape('rect',70,480,435,595,baseCtx,true);bakeStaticStrokes(baseCtx);
state.ink='neon';state.neonTint='#A844D1';beginStrokeGeneration();drawShape('rect',530,480,895,595,baseCtx,true);bakeStaticStrokes(baseCtx);
baseCtx.fillStyle='#263047';baseCtx.font='20px system-ui';baseCtx.fillText('Rainbow — continuous gear curve',50,40);baseCtx.fillText('Neon — continuous gear curve',515,40);
document.querySelector('#gallery')!.append(cloneCanvas(base));
document.title = failures ? `${failures} FAIL — RetroPaint checks` : 'PASS — RetroPaint checks';

reset();
baseCtx.font='20px system-ui';baseCtx.fillStyle='#263047';baseCtx.fillText('Neon — coloured centres and soft glow',30,35);
for(const [i,tint] of ['#E53935','#43A047','#118AB2','#9D4EDD','#FFD166'].entries()) {
 state.ink='neon';state.neonTint=tint;beginStrokeGeneration();
 for(let x=45;x<440;x+=3)segment(x,85+i*106+Math.sin(x/65)*12,x+3,85+i*106+Math.sin((x+3)/65)*12,32,0);
 bakeStaticStrokes(baseCtx);
}
state.symmetry='10';state.ink='rainbow';beginStrokeGeneration();
for(let i=0;i<60;i++){const a=i/60*Math.PI;segment(620+Math.cos(a)*26,328+Math.sin(a)*22,620+Math.cos(a+Math.PI/60)*26,328+Math.sin(a+Math.PI/60)*22,5,0);}
bakeStaticStrokes(baseCtx);
document.querySelector('#gallery')!.append(cloneCanvas(base));
state.symmetry='off';
