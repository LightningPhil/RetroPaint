import { base, baseCtx, cloneCanvas, initCanvas, resetPaint, W, H } from '../src/canvas';
import { advect, SmudgePath } from '../src/smudge';
import { paintStroke } from '../src/brush';
import { beginStrokeGeneration, mirrorPoints, segment, sprayCloud } from '../src/draw';
import { splinePoints } from '../src/curves';
import { renderPaintPath } from '../src/stroke-renderer';
import { initMaterials } from '../src/materials';
import { state } from '../src/state';
import { paintFrame } from '../src/paint';
import { bakeStaticStrokes, clearLive, strokes } from '../src/live';
import { smudge } from '../src/effects';
import { undo } from '../src/history';
import { cancelSelection, commitSelection, copySelection, cutSelection, hasSelection, hitSelection, moveSelection, pasteSelection, rectangle, refreshTransparency, selectRegion } from '../src/selection';
import { drawShape, floodAt, setShapePainter } from '../src/fill';
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
  cancelSelection(); clearLive(); resetPaint(baseCtx);
  baseCtx.fillStyle = '#ffffff'; baseCtx.fillRect(0, 0, W, H);
  state.opacity = 1; state.symmetry = 'off'; state.tool = 'draw'; state.ink = '#E53935'; state.applicator = 'marker'; state.liveArmed = false;
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
check('Neon keeps a bright core along the entire stroke and stays fixed', () => {
  reset(); state.ink = 'neon'; state.neonTint = '#9450EF'; beginStrokeGeneration();
  for (let x = 100; x < 400; x += 2) segment(x, 200, x + 2, 200, 28, 0);
  bakeStaticStrokes(baseCtx);
  const centre = baseCtx.getImageData(180, 200, 1, 1).data;
  const rim = baseCtx.getImageData(180, 207, 1, 1).data;
  assert(centre[0] > 230 && centre[1] > 230, 'Core should be bright behind the brush tip');
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
