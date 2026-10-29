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
// Component coverage includes advanced vector and CAD authoring. Workspace
// gating is exercised separately through the application UI.
state.workspaceMode = 'advanced';
import { paintFrame } from '../src/paint';
import { bakeStaticStrokes, clearLive, strokes, snapshotLive, restoreLive, renderLive } from '../src/live';
import { smudge, beginBake, invertAt, pixelateAt, embossAt, startHole, tickHole, startSqueegee, tickSqueegee, isBusy } from '../src/effects';
import { pushHistory, undo } from '../src/history';
import { cancelSelection, commitSelection, copySelection, cutSelection, hasSelection, hitSelection, moveSelection, pasteSelection, rectangle, refreshTransparency, selectRegion, renderSelection } from '../src/selection';
import { drawShape, floodAt, floodMask, setShapePainter, getPending, cancelPending } from '../src/fill';
import { drawBetween, penPosition, setRingRadius } from '../src/spiro';
import { activeLayer, addLayer, drawLayerThumbnail, layers, moveLayer, renderFullPicture, renderLayers, resetLayers, switchLayer, mergeLayerDown, transformLayers } from '../src/layers';
import { redo } from '../src/history';
import { flipSelection, invertSelection, resizeSelection, rotateSelection, selectPixelMask, selectionBounds } from '../src/selection';
import { resizePicture, rotatePicture, flipPicture, cropPicture, removeEdgeBackground, decodeImage, importImage } from '../src/editor';
import { addFill, blankMask } from '../src/live';
import { makeTextBitmap } from '../src/text-tool';
import { imageBlob } from '../src/export';
import { encodeTiff, decodeTiff } from '../src/image-codecs';
import { loadProjectData, projectData, projectDataAsync } from '../src/project';
import { bus } from '../src/bus';
import { addDrip, tickDrips } from '../src/effects';
import { autoPhoto, autoWhiteBalance, curveTable, defaultPhotoSettings, histogram, neutralBalance, processPhoto } from '../src/photo-engine';
import { applyPhoto, beginPhoto, cancelPhoto, comparePhoto, photoSession, refreshPhoto } from '../src/photo-session';
import { documentCrop, outputFrame } from '../src/document-frame';
import { choosePhotoLook, newPhotoRecipe, photoManualChange, readPhotoRecipe } from '../src/photo-recipe';
import { enhancementSize, enhancementRegion, SuperResolutionProcessor } from '../src/super-resolution';
import { PngStream } from '../src/png-stream';
import { addRasterImage, addVectorShape, beginObjectPixelEdit, beginObjectStroke, clearObjectSelection, commitObjectSelection, deleteObjects, duplicateObjects, ensureObjectLayer, finishObjectStroke, hasObjectCapture, hitObject, moveObjects, objectSelectionBounds, resizeObjects, rotateObjects, selectObjects, selectedObjects } from '../src/objects';
import { trimRasterToPaper } from '../src/selection-commit';
import { objectBounds, type RasterObject } from '../src/object-scene';
import { crankStart, crankMove, finishSpiroStroke, gearCenter, resetKit, tickMotor } from '../src/spiro';
import { RecoveryStore } from '../src/recovery-store';
import { scheduleSound,soundPatch,type SoundName } from '../src/sound-design';
import { audioSettings,setAudioSettings,toggleSounds,play } from '../src/audio';
import { renderToolCursor } from '../src/cursor-renderer';
import { drawObject } from '../src/object-scene';
import { defaultForm, newProfile, pathBeziers } from '../src/cad-profiles';
import { primitive, body as cadBody, basePlane, readCadLayer, sketchPoints, type CadMesh, type Primitive } from '../src/cad-model';
import { initKernel, solidMesh, printMesh, binaryStl, solidEdges, solidFaces } from '../src/cad-kernel';
import { ensureCadLayer, addBody as addCadBody, currentBodies, replaceBodies, combinedBody, finishedBody, shelledBody } from '../src/cad-document';
import { cadCompute } from '../src/cad-engine';
import { duplicateLayer } from '../src/layers';
import { mateBody } from '../src/cad-mate';
import { captureAttachment } from '../src/cad-attachment';
import { attachedPlane } from '../src/cad-attachment';
import { editFeature, featureAt, featureTimeline, featureTree, historyStage, prepareFeatureHistory, resizeSketch } from '../src/cad-features';
import { solveSketch } from '../src/cad-sketch-constraints';
import { importStl } from '../src/cad-stl';
import type { CadSketchConstraint, V2 } from '../src/cad-model';

initCanvas(); initMaterials();
setShapePainter((x0,y0,x1,y1,w) => segment(x0,y0,x1,y1,w,0));
let failures = 0;
const requestedCheck = new URLSearchParams(location.search).get('check');
function includesCheck(name: string): boolean {
  return (!requestedCheck || name.includes(requestedCheck)) && (!new URLSearchParams(location.search).has('cad-only') || name.startsWith('CAD '));
}
const check = (name: string, fn: () => void) => {
  if(!includesCheck(name))return;
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
check('Smudge acceptance preserves pure pigment while feathering transparent edges',()=>{
  const source=new Uint8ClampedArray([255,0,0,255,0,0,0,0]);
  const moved=advect(source,2,1,1.5,.5,1,0,10,.5);
  assert(moved[4]===255&&moved[5]===0&&moved[6]===0&&moved[7]===128,'Transparent Red acquired a dark fringe: '+Array.from(moved.slice(4)));
  assert(source[4]===0&&source[7]===0,'Immutable input was modified');
});
check('Smudge acceptance ignores colour hidden in fully transparent neighbours',()=>{
  const source=new Uint8ClampedArray([255,0,0,255,0,255,0,0]);
  const moved=advect(source,2,1,1.5,.5,1,0,10,.5);
  assert(moved[4]===255&&moved[5]===0&&moved[6]===0&&moved[7]===128,'Invisible Green contaminated visible Red: '+Array.from(moved.slice(4)));
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
check('Raster selections can leave the canvas completely and commit only the visible pixels', () => {
  reset(); block(0, 0); selectRegion(rectangle(-20, -20, 60, 60));
  moveSelection(-100, -100);assert(selectionBounds()!.x===-100&&selectionBounds()!.y===-100,'Movement was clamped to the paper');commitSelection();assert(pixel(5,5)==='255,255,255,255','Off-canvas pixels snapped back into the picture');undo();assert(pixel(5,5)==='255,0,0,255','Undo did not recover the original section');
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
  check('Tiny round Marker taps keep their nib area and remain visible at minimum Strength',()=>{
    for(const [x,y] of [[19.9999718569885,20],[20,20],[20.25,20.25],[20.5,20.5],[20.75,20.25],[20.001,20.499]])for(const mode of ['repeat','single','tiny-move']){
      const first={x,y,w:1},points=mode==='single'?[first]:mode==='repeat'?[first,{...first},{...first}]:[first,{x:x+.01,y,w:1}];
      const result=renderPaintPath(points,{kind:'solid',color:'#E53935',applicator:'marker'},{width:64,height:64})!;
      const rgba=result.canvas.getContext('2d')!.getImageData(0,0,result.canvas.width,result.canvas.height).data;let area=0;for(let i=3;i<rgba.length;i+=4)area+=rgba[i]/255;
      assert(area>=.5&&area<=1.1,`1px ${mode} tap at ${x},${y} has ${area} covered pixels instead of a round nib`);
      const output=document.createElement('canvas');output.width=output.height=64;const ctx=output.getContext('2d')!;ctx.fillStyle='#fff';ctx.fillRect(0,0,64,64);ctx.globalAlpha=.15;ctx.drawImage(result.canvas,result.x,result.y);const pixels=ctx.getImageData(0,0,64,64).data;let greenDeficit=0;for(let i=1;i<pixels.length;i+=4)greenDeficit+=255-pixels[i];
      assert(greenDeficit>=10,'Minimum-Strength tap vanished after compositing onto paper');
    }
  });
check('One-pixel Pencil writes exact opaque source cells without antialiasing',()=>{
  const points=[{x:3.5,y:18.5,w:1}];for(let i=0;i<11;i++)points.push({x:4.5+i,y:18.5+i,w:1},{x:4.5+i,y:19.5+i,w:1});
  for(const path of [points,[{x:28.5,y:4.5,w:1}],[{x:28.00001,y:4.99999,w:1}]]){
    const result=renderPaintPath(path,{kind:'solid',color:'#1A1A1A',applicator:'pencil'},{width:32,height:32})!;
    const output=document.createElement('canvas');output.width=output.height=32;const ctx=output.getContext('2d')!;ctx.fillStyle='#fff';ctx.fillRect(0,0,32,32);ctx.drawImage(result.canvas,result.x,result.y);
    const rgba=ctx.getImageData(0,0,32,32).data,expected=new Set(path.map(p=>Math.floor(p.x)+','+Math.floor(p.y)));
    for(let y=0;y<32;y++)for(let x=0;x<32;x++){const i=(y*32+x)*4,value=expected.has(x+','+y)?26:255;assert(rgba[i]===value&&rgba[i+1]===value&&rgba[i+2]===value&&rgba[i+3]===255,`Pencil cell ${x},${y} is ${Array.from(rgba.slice(i,i+4))}, expected ${value}`);}
  }
  for(const width of [22,96]){
    const result=renderPaintPath([{x:120.25,y:120.75,w:width}],{kind:'solid',color:'#1A1A1A',applicator:'pencil'},{width:256,height:256})!;
    const data=result.canvas.getContext('2d')!.getImageData(0,0,result.canvas.width,result.canvas.height).data;let occupied=0;
    for(let i=0;i<data.length;i+=4)if(data[i+3]){occupied++;assert(data[i]===26&&data[i+1]===26&&data[i+2]===26&&data[i+3]===255,'Wide Pencil introduces antialiased colour/alpha');}
    assert(occupied>=Math.PI*(width/2-1)**2&&occupied<=Math.PI*(width/2+1)**2,'Wide Pencil loses its requested circular footprint');
  }
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
check('Smudge acceptance keeps live Water until pigment actually moves',()=>{
  const send=(type:string,x:number,y:number)=>{const r=view.getBoundingClientRect();view.dispatchEvent(new PointerEvent(type,{pointerId:1313,pointerType:'mouse',button:0,buttons:type==='pointerup'?0:1,clientX:r.left+x/W*r.width,clientY:r.top+y/H*r.height}));};
  try{
    resetLayers(160,96,null);reset();baseCtx.clearRect(0,0,W,H);baseCtx.fillStyle='#ff0000';baseCtx.fillRect(40,40,80,40);const mask=blankMask();mask.getContext('2d')!.fillRect(80,40,40,40);addFill(mask,{kind:'texture',colors:[],speed:1,mode:'snap',along:false,texture:'water'},1,null);state.tool='sponge';state.brushWidth=22;
    const before=projectData();send('pointerdown',60,60);assert(projectData()===before,'Pressing without movement froze Water or changed the source');send('pointerup',60,60);assert(projectData()===before,'Releasing without movement changed live definitions');
    send('pointerdown',60,60);send('pointermove',100,60);send('pointerup',100,60);assert(snapshotLive().fills.length===0&&projectData()!==before,'Meaningful movement failed to commit the live source');undo();assert(projectData()===before,'Undo did not restore complete live source');
  }finally{send('pointercancel',60,60);resetLayers(960,640);reset();}
});
check('Smudge acceptance in empty space preserves the previous Undo action and guide',()=>{
  const send=(type:string,x:number,y:number)=>{const r=view.getBoundingClientRect();view.dispatchEvent(new PointerEvent(type,{pointerId:1314,pointerType:'mouse',button:0,buttons:type==='pointerup'?0:1,clientX:r.left+x/W*r.width,clientY:r.top+y/H*r.height}));};
  try{
    resetLayers(160,96,null);reset();baseCtx.fillStyle='#43a047';baseCtx.fillRect(0,0,W,H);addLayer();baseCtx.fillStyle='#ff0000';baseCtx.fillRect(40,60,80,30);state.tool='sponge';state.brushWidth=22;const original=projectData();pushHistory();activeLayer().name='Previous rename';const renamed=projectData();send('pointerdown',10,20);send('pointermove',60,20);send('pointerup',60,20);assert(projectData()===renamed,'Clear-only movement changed the source or sampled the lower guide');undo();assert(projectData()===original,'Empty Smudge added a hidden Undo step');redo();assert(projectData()===renamed,'Redo lost the previous rename');
  }finally{send('pointercancel',60,20);resetLayers(960,640);reset();}
});
check('Losing touch capture stops spraying immediately', () => {
  reset(); state.tool='spray'; state.applicator='mist';
  pointer('pointerdown',400,300); tickSpray();
  pointer('lostpointercapture',0,0);
  const stopped=image(); tickSpray(); tickSpray();
  assert(image()===stopped, 'An interrupted pointer kept spraying');
});
check('Cancelled touch strokes keep pigment without a line to the origin', () => {
  reset(); pointer('pointerdown',400,300); pointer('pointermove',500,300);
  pointer('pointercancel',0,0);
  assert(pixel(450,300)!=='255,255,255,255');
  assert(pixel(200,150)==='255,255,255,255');
  const stopped=image(); pointer('pointermove',600,300); pointer('pointerup',600,300);
  assert(image()===stopped, 'Cancelled drawing resumed');
});
check('Switching away from the app stops held spray pointers', () => {
  reset(); state.tool='spray'; state.applicator='mist';
  pointer('pointerdown',400,300); tickSpray(); window.dispatchEvent(new Event('blur'));
  const stopped=image(); tickSpray(); assert(image()===stopped);
});
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

// Paint editing checks share this existing browser harness; no runner or CI is needed.
check('Layer opacity applies to a whole layer; drawing and erasing leave lower layers intact', () => {
  resetLayers(96, 64); state.symmetry = 'off'; clearLive();
  baseCtx.fillStyle = '#0000ff'; baseCtx.fillRect(0, 0, W, H); const lower = activeLayer().id;
  addLayer(); baseCtx.fillStyle = '#ff0000'; baseCtx.fillRect(10, 10, 20, 20); activeLayer().opacity = 0.5;
  const canvas = cloneCanvas(base); renderLayers(canvas.getContext('2d')!, 0);
  const p = canvas.getContext('2d')!.getImageData(15, 15, 1, 1).data;
  assert(p[0] >= 127 && p[2] >= 127 && p[3] === 255, 'Layer alpha did not composite correctly');
  switchLayer(lower); assert(pixel(15, 15) === '0,0,255,255', 'Upper layer modified lower pixels');
});
check('Undo and Redo restore dimensions, active layer, transparency and hidden layers', () => {
  resetLayers(96, 64); block(10, 10); const original = image(), paper = activeLayer().id;
  pushHistory(); addLayer(); activeLayer().name = 'Ink'; activeLayer().visible = false;
  transformLayers(48, 32, [0.5, 0, 0, 0.5, 0, 0]);
  undo(); assert(W === 96 && H === 64 && layers.length === 1 && activeLayer().id === paper && image() === original);
  redo(); assert(Number(W) === 48 && Number(H) === 32 && Number(layers.length) === 2 && activeLayer().name === 'Ink' && !activeLayer().visible && activeLayer().paper === null);
});
check('Image resize transforms live ink and crop is reversible', () => {
  resetLayers(96, 64); reset(); state.liveArmed = true; state.conveyor = ['#ff0000', '#0000ff'];
  beginStrokeGeneration(); segment(20, 20, 40, 20, 4, 0);
  resizePicture(48, 32); assert(strokes.length === 1 && strokes[0].points[0].x === 10 && strokes[0].points[0].w === 2, 'Resize flattened live ink');
  selectRegion(rectangle(5, 5, 35, 25)); cropPicture(); assert(W === 30 && H === 20 && strokes[0].points[0].x === 5);
  undo(); assert(Number(W) === 48 && Number(H) === 32 && strokes[0].points[0].x === 10);
  state.liveArmed = false;
});
check('Whole-image rotate and flip use correct dimensions and pixel positions', () => {
  resetLayers(40, 20, null); baseCtx.fillStyle = '#ff0000'; baseCtx.fillRect(2, 3, 4, 4);
  rotatePicture(90); assert(W === 20 && H === 40 && pixel(14, 4) === '255,0,0,255');
  flipPicture(true); assert(pixel(5, 4) === '255,0,0,255'); undo(); assert(pixel(14, 4) === '255,0,0,255');
});
check('Selection transforms float the piece; Cancel and Undo restore its original source', () => {
  resetLayers(96, 64); state.transparentSelection = false; baseCtx.fillStyle = '#ff0000'; baseCtx.fillRect(10, 10, 10, 20); const before = image();
  selectRegion(rectangle(10, 10, 20, 30)); resizeSelection(20, 40); rotateSelection(90); flipSelection(true);
  assert(selectionBounds()?.width === 40 && selectionBounds()?.height === 20); cancelSelection(); assert(image() === before);
  selectRegion(rectangle(10, 10, 20, 30)); moveSelection(30, 0); commitSelection(); undo(); assert(image() === before); redo(); assert(pixel(45, 15) === '255,0,0,255');
});
check('Invert selection preserves the hole, and a second inversion restores the original region', () => {
  resetLayers(96, 64); selectRegion(rectangle(10, 10, 30, 30)); invertSelection();
  assert(hitSelection(3, 3) && !hitSelection(20, 20)); invertSelection(); assert(!hitSelection(3, 3) && hitSelection(20, 20)); cancelSelection();
});
check('Colour wand masks delete only connected pixels on a transparent layer', () => {
  resetLayers(40, 30, null); baseCtx.fillStyle = '#ff0000'; baseCtx.fillRect(2, 2, 8, 8); baseCtx.fillRect(20, 2, 8, 8);
  const mask = floodMask(baseCtx.getImageData(0, 0, W, H).data, 4, 4)!; selectPixelMask(mask); assert(hitSelection(4, 4) && !hitSelection(24, 4)); cutSelection();
  assert(pixel(4, 4) === '0,0,0,0' && pixel(24, 4) === '255,0,0,255'); undo(); assert(pixel(4, 4) === '255,0,0,255');
});
check('Filled shapes use the second colour, and ovals stay within their dragged bounds', () => {
  resetLayers(96, 64); reset(); state.shapeFill = 'secondary'; state.shapeOutline = 'none'; state.secondaryInk = '#0000ff';
  drawShape('ellipse', 10, 10, 70, 50, baseCtx, true); assert(pixel(40, 30) === '0,0,255,255'); assert(pixel(8, 30) === '255,255,255,255');
  state.shapeFill = 'none'; state.shapeOutline = 'brush'; state.secondaryInk = '#FFFFFF';
});
check('Text wraps and preserves font styles and an opaque second-colour background', () => {
  const canvas = makeTextBitmap({ text: 'Hello RetroPaint\nHave fun!', font: 'Arial', size: 20, width: 90, bold: true, italic: true, underline: true, strike: false, align: 'center', opaque: true }, '#ff0000', '#0000ff');
  assert(canvas.width === 90 && canvas.height > 60); const pixels = canvas.getContext('2d')!.getImageData(0, 0, canvas.width, canvas.height).data;
  assert(pixels[2] === 255 && pixels[3] === 255); assert(pixels.some((n, i) => i % 4 === 0 && n > 150), 'Text was not painted');
});
check('Background removal respects a closed foreground region and is undoable', () => {
  resetLayers(48, 32); baseCtx.fillStyle = '#ff0000'; baseCtx.fillRect(10, 10, 20, 12); const before = image();
  removeEdgeBackground(); assert(pixel(0, 0) === '0,0,0,0' && pixel(15, 15) === '255,0,0,255' && activeLayer().paper === null);
  undo(); assert(image() === before && activeLayer().paper === '#ffffff');
});
check('Merge down preserves the visible composite', () => {
  resetLayers(48, 32); addLayer(); baseCtx.fillStyle = '#ff0000'; baseCtx.fillRect(10, 10, 20, 10); activeLayer().opacity = 0.5;
  const before = cloneCanvas(base); renderLayers(before.getContext('2d')!, 0); mergeLayerDown();
  const after = cloneCanvas(base); renderLayers(after.getContext('2d')!, 0); assert(before.toDataURL() === after.toDataURL() && layers.length === 1);
});
check('Moving sheets changes the composite and Undo restores order, active sheet and live ink', () => {
  resetLayers(48, 32); const paper = activeLayer().id;
  addLayer(); const red = activeLayer().id; baseCtx.fillStyle = '#ff0000'; baseCtx.fillRect(0, 0, W, H);
  addLayer(); const blue = activeLayer().id;
  const mask = blankMask(); mask.getContext('2d')!.fillRect(0, 0, W, H);
  addFill(mask, { kind:'conveyor', colors:['#0000ff'], speed:3, mode:'ooze', along:false, texture:null }, 1, null);
  const output = cloneCanvas(base), ctx = output.getContext('2d')!;
  renderLayers(ctx, 0); assert(ctx.getImageData(10, 10, 1, 1).data[2] === 255);
  pushHistory(); assert(moveLayer(red, blue, true)); renderLayers(ctx, 0);
  assert(ctx.getImageData(10, 10, 1, 1).data[0] === 255, 'Sheet order did not change visible pixels');
  undo(); assert(layers.map(layer => layer.id).join(',') === [paper,red,blue].join(',') && activeLayer().id === blue && snapshotLive().fills.length === 1);
  assert(!moveLayer(blue, red, true) && !moveLayer(blue, blue, false), 'No-op moves changed order');
  switchLayer(red); assert(pixel(10, 10) === '255,0,0,255', 'Reorder modified the drawing');
});
check('Layer thumbnails preserve aspect ratio, opacity and transparent areas and sample active and inactive live ink', () => {
  resetLayers(48, 24, null); const liveLayer = activeLayer(), mask = blankMask(); mask.getContext('2d')!.fillRect(0, 0, W, H);
  addFill(mask, { kind:'conveyor', colors:['#ff0000','#0000ff'], speed:3, mode:'ooze', along:false, texture:null }, 1, null);
  liveLayer.opacity = 0.5;
  const thumb = document.createElement('canvas'); thumb.width = thumb.height = 48; const ctx = thumb.getContext('2d')!;
  drawLayerThumbnail(ctx, liveLayer, 0); const before = thumb.toDataURL(), p = ctx.getImageData(20, 20, 1, 1).data;
  assert(p[3] >= 127 && p[3] <= 128, 'Preview ignored sheet opacity');
  assert(ctx.getImageData(20, 2, 1, 1).data[3] === 0, 'Preview stretched the picture instead of fitting it');
  drawLayerThumbnail(ctx, liveLayer, 1000); assert(thumb.toDataURL() !== before, 'Preview did not sample animation');
  addLayer(); drawLayerThumbnail(ctx, liveLayer, 0); assert(thumb.toDataURL() === before, 'Inactive sheet lost its live preview');
  drawLayerThumbnail(ctx, activeLayer(), 0); assert(ctx.getImageData(20, 20, 1, 1).data[3] === 0, 'Empty sheet preview retained previous pixels');
});
check('Right-click painting uses the second colour without changing the primary ink', () => {
  resetLayers(96, 64); reset(); state.applicator = 'brush'; state.brushWidth = 6; state.secondaryInk = '#0000ff';
  const stageStyle = inputStage.style.cssText; inputStage.style.display = 'block';
  const capture = view.setPointerCapture; view.setPointerCapture = () => {};
  const send = (type: string, x: number, y: number, button: number) => {
    const r = view.getBoundingClientRect(); view.dispatchEvent(new PointerEvent(type, { pointerId: 105, button, clientX: r.left + x / W * r.width, clientY: r.top + y / H * r.height }));
  };
  try {
    send('pointerdown', 20, 20, 0); send('pointerup', 20, 20, 0);
    send('pointerdown', 50, 20, 2); send('pointerup', 50, 20, 2);
    assert(pixel(20, 20) === '229,57,53,255' && pixel(50, 20) === '0,0,255,255', `Primary ${pixel(20, 20)}, secondary ${pixel(50, 20)}, view ${JSON.stringify(view.getBoundingClientRect())}`); assert(state.ink === '#E53935');
    state.tool = 'picker'; const choose = (event: Event) => { state.ink = (event as CustomEvent).detail.colour; };
    bus.addEventListener('pick-colour', choose); send('pointerdown', 50, 20, 0); bus.removeEventListener('pick-colour', choose);
    assert(state.ink.toLowerCase() === '#0000ff', 'Picker colour was reverted by pointer cleanup');
  } finally { view.setPointerCapture = capture; inputStage.style.cssText = stageStyle; }
});
check('Semi-transparent erasing preserves lower layers and erases live ink with the chosen strength', () => {
  resetLayers(96, 64); baseCtx.fillStyle = '#0000ff'; baseCtx.fillRect(0, 0, W, H); const lower = activeLayer().id;
  addLayer(); baseCtx.fillStyle = '#ff0000'; baseCtx.fillRect(10, 10, 50, 30); state.tool = 'eraser'; state.eraserMode = 'scrub'; state.opacity = 0.5; state.brushWidth = 6;
  const stageStyle = inputStage.style.cssText; inputStage.style.display = 'block';
  const capture = view.setPointerCapture; view.setPointerCapture = () => {};
  try {
    const r = view.getBoundingClientRect(), event = { pointerId: 106, button: 0, clientX: r.left + 30 / W * r.width, clientY: r.top + 25 / H * r.height };
    view.dispatchEvent(new PointerEvent('pointerdown', event)); view.dispatchEvent(new PointerEvent('pointerup', event));
    const alpha = baseCtx.getImageData(30, 25, 1, 1).data[3]; assert(alpha >= 125 && alpha <= 130, 'Eraser strength was ignored: ' + alpha);
    switchLayer(lower); assert(pixel(30, 25) === '0,0,255,255');
  } finally { view.setPointerCapture = capture; state.opacity = 1; inputStage.style.cssText = stageStyle; }
});
for(const strength of [1,.15])check('Scrub hidden-sheet Undo restores original visibility and neighbour at Strength '+strength,()=>{
  const capture=view.setPointerCapture,stageStyle=inputStage.style.cssText;view.setPointerCapture=()=>{};inputStage.style.display='block';
  const send=(type:string,x:number,y:number)=>{const r=view.getBoundingClientRect();view.dispatchEvent(new PointerEvent(type,{pointerId:1414,pointerType:'mouse',button:0,buttons:type==='pointerup'?0:1,clientX:r.left+x/W*r.width,clientY:r.top+y/H*r.height}));};
  try{
    resetLayers(160,96,null);reset();baseCtx.fillStyle='#0000ff';baseCtx.fillRect(0,0,W,H);const neighbour=activeLayer().canvas.toDataURL();addLayer();baseCtx.fillStyle='#ff0000';baseCtx.fillRect(20,20,100,60);activeLayer().visible=false;state.tool='eraser';state.eraserMode='scrub';state.brushWidth=22;state.opacity=strength;const before=projectData();send('pointerdown',60,48);send('pointerup',60,48);const after=projectData();assert(activeLayer().visible&&baseCtx.getImageData(60,48,1,1).data[3]<255,'Scrub did not erase the selected hidden sheet');assert(layers[0].canvas.toDataURL()===neighbour,'Scrub erased a visible neighbour');undo();assert(projectData()===before,'Undo restores pixels but leaves the original hidden working sheet visible');redo();assert(projectData()===after,'Redo fails to restore complete erase/reveal state');
  }finally{send('pointercancel',60,48);view.setPointerCapture=capture;inputStage.style.cssText=stageStyle;resetLayers(960,640);reset();}
});
function eraserLifecycleFixture(action:(send:(type:string,x:number,y:number)=>void)=>void):void {
  const capture=view.setPointerCapture,stageStyle=inputStage.style.cssText,drawingMode=state.drawingMode;view.setPointerCapture=()=>{};inputStage.style.display='block';
  const send=(type:string,x:number,y:number)=>{const r=view.getBoundingClientRect();view.dispatchEvent(new PointerEvent(type,{pointerId:1515,pointerType:'mouse',button:0,buttons:type==='pointerup'||type==='pointercancel'?0:1,clientX:r.left+x/W*r.width,clientY:r.top+y/H*r.height}));};
  try{resetLayers(180,100);reset();baseCtx.fillStyle='#ff0000';baseCtx.fillRect(0,0,W,H);state.drawingMode='raster';state.tool='eraser';state.eraserMode='blackhole';state.brushWidth=22;action(send);}
  finally{send('pointercancel',60,50);tickHole(1000);view.setPointerCapture=capture;inputStage.style.cssText=stageStyle;state.drawingMode=drawingMode;resetLayers(960,640);reset();}
}
check('Eraser lifecycle Black Hole follows a held pointer and remains one edit',()=>eraserLifecycleFixture(send=>{
  const before=projectData();send('pointerdown',30,50);tickHole(80);send('pointermove',140,50);tickHole(120);assert(pixel(140,50)==='255,255,255,255','Black Hole ignored movement to a fresh painted footprint');send('pointerup',140,50);const after=projectData();undo();assert(projectData()===before,'A moved Black Hole is not one complete undoable gesture');redo();assert(projectData()===after,'Moved Black Hole Redo changed source');
}));
for(const stop of ['pointerup','pointercancel','blur'] as const)check('Eraser lifecycle Black Hole '+stop+' stops future writes and releases busy state',()=>eraserLifecycleFixture(send=>{
  send('pointerdown',60,50);tickHole(80);if(stop==='blur')window.dispatchEvent(new Event('blur'));else send(stop,60,50);const stopped=image();tickHole(240);tickHole(400);assert(image()===stopped,'Black Hole kept changing source after '+stop);assert(!isBusy()&&!state.busy,'Black Hole left the editor busy after '+stop);
}));
check('Eraser lifecycle Black Hole keeps clear pixels clear and never samples the guide',()=>eraserLifecycleFixture(send=>{
  resetLayers(180,100,null);baseCtx.fillStyle='#43a047';baseCtx.fillRect(0,0,W,H);const guide=activeLayer().canvas.toDataURL();addLayer();baseCtx.fillStyle='#ff0000';baseCtx.fillRect(20,20,100,60);send('pointerdown',20,50);tickHole(120);assert(baseCtx.getImageData(5,50,1,1).data[3]===0,'Transparent pixels acquired opaque paint');assert(baseCtx.getImageData(20,50,1,1).data[3]===0,'Clear-sheet hole painted a matte instead of removing alpha');assert(layers[0].canvas.toDataURL()===guide,'Black Hole changed the guide');
}));
check('Eraser lifecycle hidden Black Hole Undo restores the original hidden state',()=>eraserLifecycleFixture(send=>{
  activeLayer().visible=false;const before=projectData();send('pointerdown',60,50);tickHole(80);send('pointerup',60,50);const after=projectData();assert(activeLayer().visible,'Edited hidden target was not revealed');undo();assert(projectData()===before,'Black Hole Undo leaves the original hidden target visible');redo();assert(projectData()===after,'Black Hole Redo changed complete source');
}));
for(const mode of ['invert','pixelate','emboss'] as const)check('Eraser lifecycle hidden '+mode+' restores visibility and neighbour in history',()=>eraserLifecycleFixture(send=>{
  resetLayers(180,100,null);baseCtx.fillStyle='#0000ff';baseCtx.fillRect(0,0,W,H);const guide=activeLayer().canvas.toDataURL();addLayer();const data=new ImageData(W,H);for(let y=0;y<H;y++)for(let x=0;x<W;x++){const v=(Math.floor(x/2)+Math.floor(y/2))%2?224:32;data.data.set([v,v,v,255],(y*W+x)*4);}baseCtx.putImageData(data,0,0);activeLayer().visible=false;state.eraserMode=mode;const before=projectData();send('pointerdown',60,50);send('pointerup',60,50);const after=projectData();assert(activeLayer().visible&&layers[0].canvas.toDataURL()===guide,'Hidden filter chose or changed its neighbour');undo();assert(projectData()===before,'Hidden '+mode+' Undo leaves the working sheet visible');redo();assert(projectData()===after,'Hidden '+mode+' Redo changes source');
}));
check('Eraser lifecycle completed Black Hole preserves bounding-box corners',()=>eraserLifecycleFixture(send=>{
  const corner=pixel(5,2);send('pointerdown',60,50);tickHole(700);assert(pixel(5,2)===corner,'Completed hole cleared outside its circular footprint');send('pointerup',60,50);
}));
check('Eraser lifecycle Black Hole uses the defined Paper colour',()=>eraserLifecycleFixture(send=>{
  activeLayer().paper='#43a047';send('pointerdown',60,50);tickHole(120);assert(pixel(60,50)==='67,160,71,255','Hole ignored the defined Paper colour');send('pointerup',60,50);
}));
check('Eraser lifecycle Black Hole remains held after its first animation and recovers from outside',()=>eraserLifecycleFixture(send=>{
  send('pointerdown',30,50);tickHole(700);assert(isBusy(),'Held hole finished before release');send('pointermove',-200,50);tickHole(100);send('pointermove',140,50);tickHole(120);assert(pixel(140,50)==='255,255,255,255','Held hole failed to resume on painted material');send('pointercancel',140,50);const stopped=image();tickHole(700);assert(image()===stopped&&!isBusy());
}));
check('Eraser lifecycle masked Black Hole clears alpha without leaking across the seam',()=>{
  try{resetLayers(960,640,null);reset();state.symmetry='4';state.symmetryMask=true;baseCtx.fillStyle='#ff0000';baseCtx.fillRect(0,0,W,H);startHole(620,300);tickHole(700);assert(baseCtx.getImageData(620,330,1,1).data[3]===0,'Masked clear-sheet hole retained an opaque matte');assert(pixel(620,260)==='255,0,0,255','Masked hole leaked past its slice');}
  finally{tickHole(1000);resetLayers(960,640);reset();}
});
check('Pixel filter Strength blends one Invert contribution and preserves alpha',()=>{
  try{
    resetLayers(128,96,null);reset();baseCtx.clearRect(0,0,W,H);baseCtx.fillStyle='rgb(40,80,160)';baseCtx.fillRect(0,0,64,96);baseCtx.fillStyle='rgba(200,40,120,0.5)';baseCtx.fillRect(64,0,48,96);const before=baseCtx.getImageData(0,0,W,H).data;state.tool='eraser';state.eraserMode='invert';state.brushWidth=22;state.opacity=.15;invertAt(64,48);const after=baseCtx.getImageData(0,0,W,H).data;
    assert(pixel(60,48)==='66,94,150,255','Invert ignored the selected15% Strength: '+pixel(60,48));for(let i=3;i<before.length;i+=4)assert(after[i]===before[i],'Weak Invert changed source alpha');
  }finally{resetLayers(960,640);reset();}
});
check('Pixel filter Invert covers dense movement and applies each whole gesture once',()=>{
  const capture=view.setPointerCapture,stageStyle=inputStage.style.cssText;view.setPointerCapture=()=>{};inputStage.style.display='block';
  try{
    resetLayers(160,96,null);reset();baseCtx.fillStyle='rgb(40,80,160)';baseCtx.fillRect(0,0,160,96);const before=image();state.tool='eraser';state.eraserMode='invert';state.brushWidth=22;state.opacity=1;
    const send=(type:string,x:number)=>{const r=view.getBoundingClientRect();view.dispatchEvent(new PointerEvent(type,{pointerId:1741,pointerType:'mouse',button:0,buttons:type==='pointerup'?0:1,clientX:r.left+x/160*r.width,clientY:r.top+48/96*r.height}));};
    const gesture=()=>{send('pointerdown',30);for(let x=34;x<=130;x+=4)send('pointermove',x);send('pointerup',130);};gesture();for(let x=30;x<=130;x++)assert(pixel(x,48)==='215,175,95,255','Dense Invert leaves or repeatedly toggles its swept core at'+x+': '+pixel(x,48));gesture();assert(image()===before,'Two identical full Invert gestures do not restore the complete source');
  }finally{view.setPointerCapture=capture;inputStage.style.cssText=stageStyle;resetLayers(960,640);reset();}
});
check('Pixel filter covers release movement and bounds captured travel outside the paper',()=>{
  const capture=view.setPointerCapture,stageStyle=inputStage.style.cssText;view.setPointerCapture=()=>{};inputStage.style.display='block';
  try{
    const prepare=()=>{resetLayers(160,96,null);reset();baseCtx.fillStyle='rgb(40,80,160)';baseCtx.fillRect(0,0,160,96);state.tool='eraser';state.eraserMode='invert';state.brushWidth=22;state.opacity=1;};
    const send=(type:string,x:number)=>{const r=view.getBoundingClientRect();view.dispatchEvent(new PointerEvent(type,{pointerId:1742,pointerType:'mouse',button:0,buttons:type==='pointerup'?0:1,clientX:r.left+x/160*r.width,clientY:r.top+48/96*r.height}));};
    prepare();send('pointerdown',30);send('pointerup',130);for(let x=30;x<=130;x++)assert(pixel(x,48)==='215,175,95,255','Release-only movement leaves the covered core unchanged at'+x);
    prepare();const started=performance.now();send('pointerdown',-1_000_000);send('pointerup',1_000_000);assert(performance.now()-started<1000,'Captured movement was not clipped before sampling');for(let x=0;x<160;x++)assert(pixel(x,48)==='215,175,95,255','Clipping lost the segment crossing the paper at'+x);
  }finally{view.setPointerCapture=capture;inputStage.style.cssText=stageStyle;resetLayers(960,640);reset();}
});
for(const [mode,apply] of [['pixelate',pixelateAt],['emboss',embossAt]] as const)check('Pixel filter '+mode+' respects the selected weak contribution bound',()=>{
  try{
    resetLayers(128,96,null);reset();const source=new ImageData(128,96);for(let y=0;y<96;y++)for(let x=0;x<128;x++){const i=(y*128+x)*4,v=mode==='pixelate'&&(x+y)%2?255:0;source.data.set([v,v,v,255],i);}baseCtx.putImageData(source,0,0);state.tool='eraser';state.eraserMode=mode;state.brushWidth=22;state.opacity=.15;apply(64,48);const sample=baseCtx.getImageData(64,48,1,1).data;
    assert(sample[0]>0&&sample[0]<=39&&sample[0]===sample[1]&&sample[1]===sample[2]&&sample[3]===255,mode+' ignores15% Strength or changes neutral alpha: '+Array.from(sample));
  }finally{resetLayers(960,640);reset();}
});
check('Wet spray drips continue on their own layer after switching layers', () => {
  resetLayers(96, 64); addDrip(10, 5, 3, '#ff0000'); const original = baseCtx; addLayer(); tickDrips(100);
  assert(baseCtx.getImageData(10, 11, 1, 1).data[3] === 0, 'Drip leaked onto the new layer'); assert(original.getImageData(10, 11, 1, 1).data[1] < 100);
  tickDrips(2000);
});
async function asyncCheck(name: string, action: () => Promise<void>): Promise<void> {
  if(!includesCheck(name))return;
  let error: unknown; try { await action(); } catch (caught) { error = caught; }
  check(name, () => { if (error) throw error; });
}

await asyncCheck('Code wiki covers the core registry and links every topic',async()=>{
 const {WIKI_TOPICS}=await import('../src/cad-wiki-content');const {searchWiki,mcadTopics}=await import('../src/cad-wiki');
 const ids=new Set(WIKI_TOPICS.map(topic=>topic.id)),symbols=new Set(WIKI_TOPICS.flatMap(topic=>topic.symbols));assert(ids.size===WIKI_TOPICS.length,'Duplicate wiki id');
 const core='abs sign rands min max sin cos asin acos tan atan atan2 round ceil floor pow sqrt exp len log ln str chr textmetrics fontmetrics ord concat lookup search version version_num norm cross parent_module is_undef is_list is_num is_bool is_string is_function is_object object has_key import cube sphere cylinder polyhedron square circle polygon linear_extrude rotate_extrude surface translate rotate scale resize mirror multmatrix color offset hull minkowski fill union difference intersection group projection children echo assert for let intersection_for if render roof'.split(' ');for(const name of core)assert(symbols.has(name),'Missing core topic: '+name);
 for(const topic of WIKI_TOPICS){assert(topic.summary.length>20&&topic.body.length>0,'Thin article '+topic.id);assert(topic.lesson.beginner.length>=2&&topic.lesson.beginner.every(text=>text.length>80)&&topic.lesson.deeper.length>100,'Missing learning levels '+topic.id);for(const id of topic.related)assert(ids.has(id),'Broken related link '+id);for(const example of topic.examples){assert(example.result.length>20&&example.experiment.length>30,'Missing example guidance '+example.title);assert(example.code.split('\n').filter(line=>line.includes('//')).length>=2,'Missing code commentary '+example.title);for(const [path,source] of Object.entries(example.files??{}))if(path.endsWith('.scad'))assert(source.includes('//'),'Uncommented helper '+path);}}
 assert(searchWiki(WIKI_TOPICS,'rotate_extrude').some(topic=>topic.id==='rotate-extrude'),'Function search failed');assert(searchWiki(WIKI_TOPICS,'nonsense-zzzz').length===0,'Empty search failed');
 assert(searchWiki(WIKI_TOPICS,'potter').some(topic=>topic.id==='rotate-extrude'),'Beginner explanations are not searchable');assert(searchWiki(WIKI_TOPICS,'indentations').some(topic=>topic.id==='functions'),'Example exercises are not searchable');
 const files=await (await fetch('/openscad/mcad.json')).json(),library=mcadTopics(files);assert(library.length===files.filter((file:{path:string})=>file.path.endsWith('.scad')).length,'Missing MCAD source file');assert(library.some(topic=>topic.symbols.includes('roundedBox'))&&library.some(topic=>topic.symbols.includes('gear')),'MCAD symbols not indexed');
 for(const topic of library)assert(topic.lesson.beginner.length>=2&&topic.lesson.deeper.length>100,'Library learning levels missing '+topic.id);assert(library.find(topic=>topic.title==='MCAD / units.scad')?.syntax.startsWith('include'),'Constants loading guidance uses the wrong directive');
});
await asyncCheck('Code wiki runnable examples all render closed native OpenSCAD solids',async()=>{
 const {WIKI_TOPICS}=await import('../src/cad-wiki-content');const {renderOpenSCAD}=await import('../src/openscad-engine');const failures:string[]=[];let count=0;
 for(const topic of WIKI_TOPICS)for(const example of topic.examples){if(example.preview===false)continue;count++;try{const files=Object.entries(example.files??{}).map(([path,source])=>{let binary='';for(const byte of new TextEncoder().encode(source))binary+=String.fromCharCode(byte);return{path,data:btoa(binary)};});const result=await renderOpenSCAD(example.code,'main.scad',files);const warnings=result.logs.filter(line=>/^WARNING:/i.test(line));assert(warnings.length===0,'Warnings: '+warnings.join(' | '));const mesh=(await cadCompute([result.body])).mesh;closedCadMesh(mesh);assert(mesh.volume>0,'No material');}catch(error){failures.push(topic.id+' / '+example.title+': '+String(error));}}
 assert(count>=50,'Too few runnable examples');assert(!failures.length,failures.join('\n'));
});
await asyncCheck('OpenSCAD parameters ignore locals comments strings and ambiguous reassignments',async()=>{
 const {numericScriptParameters,openSCADLocation}=await import('../src/cad-script-editor');
 const source='// comment=2;\n/* hidden=8; */\ntext="fake=9;";\nmodule part(){\n local=6;\n}\nsize=2e1; // width\nrepeated=2; repeated=4;\nother=8;\nother=10;\nfunction fn(x=2)=x;\nheight = -3.5;';
 const params=numericScriptParameters(source);assert(params.map(p=>p.name).join(',')==='size,height','Unsafe parameters exposed');for(const p of params)assert(source.slice(p.start,p.end)===p.value,'Wrong source range');assert(openSCADLocation('ERROR: Parser error in file /project/lib/part.scad, line 3')?.file==='lib/part.scad','Native diagnostic path');
});
await asyncCheck('OpenSCAD diagnostics bound echo output preserve errors and explain 2D output',async()=>{
 const {renderOpenSCAD}=await import('../src/openscad-engine');
 const result=await renderOpenSCAD('echo("ERROR: this is only text"); for(i=[0:10000]) echo(i); cube(2);');assert((await cadCompute([result.body])).mesh.volume===8,'Echo was treated as an error');assert(result.logs.join('\n').length<68000&&result.logs.some(line=>line.includes('Output truncated')),'Unbounded diagnostics');
 let message='';try{await renderOpenSCAD('cube(2); import("missing.stl");');}catch(error){message=String(error);}assert(/missing.stl/.test(message)&&message.split('missing.stl').length===2,'Missing asset diagnostic duplicated or lost');
 try{await renderOpenSCAD('circle(3);');throw new Error('2D accepted as a solid');}catch(error){assert(/Extrude 2D/.test(String(error)),'2D error gives no recovery instruction');}
 const files=[{path:'lib.scad',data:btoa('module part(){cube(2);}')}];const pending=renderOpenSCAD('use <lib.scad> part();','main.scad',files);files[0].data=btoa('module part(){cube(20);}');const snapshot=await pending;assert(snapshot.body.script!.files![0].data!==files[0].data&&(await cadCompute([snapshot.body])).mesh.volume===8,'Render source snapshot mutated');
});
await asyncCheck('OpenSCAD engine supports real language, fonts and dependencies',async()=>{
  const {renderOpenSCAD}=await import('../src/openscad-engine');
  const files=[{path:'lib/part.scad',data:btoa('function twice(n)=n*2; module part(){children();}')}];
  const result=await renderOpenSCAD('use <lib/part.scad>\npart() mirror([1,0,0]) cube([twice(3),4,5]);','main.scad',files);
  const mesh=(await cadCompute([result.body])).mesh;assert(Math.abs(mesh.volume-120)<.01,'native module/functions/children/mirror volume');
  assert(result.body.script?.language==='openscad'&&result.body.script.files?.length===1,'source and files retained');
  const mcad=await renderOpenSCAD('use <MCAD/boxes.scad> roundedBox([10,10,10],2,true);');assert((await cadCompute([mcad.body])).mesh.volume>0,'Bundled MCAD library');
  const letters=await renderOpenSCAD('linear_extrude(2) text("ABC",size=8);');assert((await cadCompute([letters.body])).mesh.volume>0,'font rendering');
  let rejected=false;try{await renderOpenSCAD('include <missing.scad> cube(2);');}catch{rejected=true;}assert(rejected,'missing include must not silently render');
});

await asyncCheck('OpenSCAD engine renders upstream files and formerly unsupported operations',async()=>{
 const {renderOpenSCAD}=await import('../src/openscad-engine');
 const {LEGACY_SCRIPT_EXAMPLES}=await import('../src/cad-script');for(const [name,source] of Object.entries(LEGACY_SCRIPT_EXAMPLES)){try{const result=await renderOpenSCAD(source);const mesh=(await cadCompute([result.body])).mesh;closedCadMesh(mesh);assert(mesh.volume>0,'Native starter: '+name);}catch(error){throw new Error(name+': '+String(error));}}
 for(const name of ['CSG.scad','rotate_extrude.scad']){const source=await (await fetch('/openscad/examples/'+name)).text();const result=await renderOpenSCAD(source,name);const mesh=(await cadCompute([result.body])).mesh;closedCadMesh(mesh);assert(mesh.volume>0,'Upstream '+name);}
 for(const source of ['minkowski(){cube(3);sphere(1,$fn=12);}', 'linear_extrude(3) offset(r=1) polygon([for(i=[0:4]) [cos(i*72)*8,sin(i*72)*8]]);','rotate(a=35,v=[1,1,0]) scale([-1,2,1]) cube(4);','n=2; cube(n); n=5;']){const result=await renderOpenSCAD(source);const mesh=(await cadCompute([result.body])).mesh;closedCadMesh(mesh);assert(mesh.volume>0,'Native geometry');if(source.startsWith('n='))assert(Math.abs(mesh.volume-125)<.01,'Declarative reassignment differs from OpenSCAD');}
});
await asyncCheck('OpenSCAD advanced starters remain connected solids after parameter changes',async()=>{
 const {ADVANCED_SCRIPT_EXAMPLES}=await import('../src/cad-script-examples'),{renderOpenSCAD}=await import('../src/openscad-engine');
 const changes:Record<string,[string,string]>={'Spiral lattice lantern':['twist=90;','twist=120;'],'Orbital sculpture':['orbit_radius=25;','orbit_radius=30;'],'Twisted wave pen pot':['height=64;','height=80;'],'Rocket desk organiser':['fins=3;','fins=4;'],'Castle gatehouse':['tower_height=32;','tower_height=42;']};
 for(const [name,source] of Object.entries(ADVANCED_SCRIPT_EXAMPLES)){
  const [before,after]=changes[name];assert(source.includes(before),'Missing editable parameter '+name);let originalVolume=0;
  for(const [version,code] of [source,source.replace(before,after)].entries()){
   try{const result=await renderOpenSCAD(code);assert(!result.logs.some(line=>/^WARNING:/i.test(line)),result.logs.join('\n'));const mesh=(await cadCompute([result.body])).mesh;closedCadMesh(mesh);assert(mesh.bounds.min[2]>=-.001,'Below print bed');
    // Weld equal STL coordinates, then count connected surface components.
    const parents=new Map<string,string>(),key=(i:number)=>Array.from(mesh.positions.subarray(i*3,i*3+3)).map(v=>Math.round(v*1e5)).join(',');
    const root=(id:string):string=>{if(!parents.has(id))parents.set(id,id);let node=id;while(parents.get(node)!==node)node=parents.get(node)!;while(id!==node){const next=parents.get(id)!;parents.set(id,node);id=next;}return node;};
    for(let i=0;i<mesh.indices.length;i+=3){const a=root(key(mesh.indices[i]));for(let j=1;j<3;j++)parents.set(root(key(mesh.indices[i+j])),root(a));}
    assert(new Set([...parents.keys()].map(root)).size===1,'Detached features or sealed internal shells');
    if(version===0)originalVolume=mesh.volume;else assert(Math.abs(mesh.volume-originalVolume)>1,'Parameter did not alter geometry');
   }catch(error){throw new Error(name+(version?' (edited)':' (default)')+': '+String(error));}
  }
 }
});
await asyncCheck('OpenSCAD engine imports SVG, heightmaps and STL and saves complete projects',async()=>{
 const {renderOpenSCAD}=await import('../src/openscad-engine');
 const cube=await renderOpenSCAD('cube(4);');const stl=(await cadCompute([cube.body],'print')).stl!;
 let binary='';for(const b of new Uint8Array(stl))binary+=String.fromCharCode(b);
 const files=[{path:'parts/block.stl',data:btoa(binary)},{path:'profiles/box.svg',data:btoa('<svg xmlns="http://www.w3.org/2000/svg" width="10mm" height="10mm" viewBox="0 0 10 10"><rect width="10" height="10"/></svg>')},{path:'data/grid.dat',data:btoa('1 2 1\n2 3 2\n1 2 1\n')},{path:'config.scad',data:btoa('height=3;')}];
 const source='include <../config.scad> union(){import("../parts/block.stl"); translate([15,0,0]) linear_extrude(height) import("../profiles/box.svg"); translate([30,0,0]) surface("../data/grid.dat");}';
 const result=await renderOpenSCAD(source,'src/main.scad',files);closedCadMesh((await cadCompute([result.body])).mesh);
 resetLayers(160,120);ensureCadLayer();addCadBody(result.body);const saved=projectData();assert(JSON.parse(saved).version===13,'Native project version');resetLayers(10,10);await loadProjectData(saved);const script=currentBodies()[0].script!;assert(script.entry==='src/main.scad'&&script.files?.length===4,'Dependencies lost');const rebuilt=await renderOpenSCAD(script.source,script.entry,script.files);assert((await cadCompute([rebuilt.body])).mesh.volume>300,'Restored project does not render');resetLayers(960,640);
});
await asyncCheck('OpenSCAD native cut solids join workshop shapes and export closed STL',async()=>{
 const {renderOpenSCAD}=await import('../src/openscad-engine');const {importStl}=await import('../src/cad-stl');const rendered=await renderOpenSCAD('difference(){cube([20,20,10],center=true);cylinder(h=20,r=3,center=true,$fn=64);}');const sphere=primitive('sphere',[12,12,12]);sphere.position=[10,0,0];const original=(await cadCompute([rendered.body])).mesh.volume,joined=combinedBody('union',[rendered.body,sphere]),result=await cadCompute([joined],'print');closedCadMesh(result.mesh);assert(result.mesh.volume>original&&result.mesh.volume<original+910,'Join failed to fuse native mesh');const roundtrip=importStl(result.stl!,'native-joined.stl');const printed=(await cadCompute([roundtrip])).mesh;closedCadMesh(printed);assert(Math.abs(printed.volume-result.mesh.volume)<.1,'STL changed material volume');
});
await asyncCheck('OpenSCAD engine cancels and rejects unsafe project paths',async()=>{
 const {renderOpenSCAD}=await import('../src/openscad-engine');const controller=new AbortController();const pending=renderOpenSCAD('sphere(100,$fn=1000);','main.scad',[],controller.signal);controller.abort();let cancelled=false;try{await pending;}catch(error){cancelled=/cancelled/.test(String(error));}assert(cancelled,'Render cannot be cancelled');
 let conflict=false;try{await renderOpenSCAD('cube(1);','main.scad',[{path:'parts',data:''},{path:'parts/part.scad',data:''}]);}catch(error){conflict=/both a file and a folder/.test(String(error));}assert(conflict,'File/directory conflict was not explained');
 for(const path of ['../escape.scad','/absolute.scad','C:/file.scad']){let rejected=false;try{await renderOpenSCAD('cube(1);',path);}catch{rejected=true;}assert(rejected,'Unsafe path accepted');}
});

await asyncCheck('Script CAD examples build closed printable solids',async()=>{
  const {compileCadScript,LEGACY_SCRIPT_EXAMPLES}=await import('../src/cad-script');
  for(const [name,source] of Object.entries(LEGACY_SCRIPT_EXAMPLES)){const item=compileCadScript(source),mesh=await solidMesh(item);try{closedCadMesh(mesh);}catch(error){throw new Error(name+': '+String(error));}assert(mesh.volume>1,name+' has no volume');}
});
await asyncCheck('Script CAD boolean volumes, centres, ordered transforms and profile holes',async()=>{
  const {compileCadScript}=await import('../src/cad-script');
  for(const [source,volume] of [
    ['difference(){cube(10);translate([2,2,-1])cube([6,6,12]);}',640],
    ['intersection(){cube(10);translate([5,0,0])cube(10);}',500],
    ['linear_extrude(height=5)difference(){square(10);translate([2,2])square(6);}',320],
    ['module block(s=2){cube(s);} for(i=[0:2])translate([i*4,0,0])block();',24],
    ['if(sin(90)==1) cube([2,3,4]); else cube(1);',24],
    ['intersection(){translate([0,0,0]){cube(10);translate([10,0,0])cube(10);}cube([20,10,10]);}',2000]
  ] as const){const mesh=await solidMesh(compileCadScript(source));closedCadMesh(mesh);assert(Math.abs(mesh.volume-volume)<.01,'Incorrect script volume: '+source+' = '+mesh.volume);}
  const moved=await solidMesh(compileCadScript('rotate([0,0,90])translate([10,0,0])cube([2,4,6],center=true);'));assert(Math.abs(moved.bounds.min[1]-9)<.01&&Math.abs(moved.bounds.max[0]-2)<.01,'Transform order or centering changed');
  for(const source of ['cylinder(h=10,r1=5,r2=0);','cylinder(h=10,r1=0,r2=5,center=true);']){const mesh=await solidMesh(compileCadScript(source));closedCadMesh(mesh);assert(Math.abs(mesh.volume-Math.PI*25*10/3)<1,'Cone volume wrong');}
});
await asyncCheck('Script CAD errors and limits reject bad code without executing it',async()=>{
  const {compileCadScript}=await import('../src/cad-script');
  for(const source of ['cube([1,2]);','cube(10); fetch("https://example.com");','for(i=[0:100000])cube(1);','module again(){again();} again();','cube(1/0);','import("file.stl");','cube(2,wrong=true);','translate([1,2,3]) circle(3);','/* unclosed','cube(3)']){let failed=false;try{compileCadScript(source);}catch(error){failed=error instanceof Error&&error.message.length>0;}assert(failed,'Invalid script accepted: '+source);}
});
await asyncCheck('Script CAD project roundtrip keeps editable source and undo',async()=>{
  const {compileCadScript,SCRIPT_EXAMPLES}=await import('../src/cad-script');resetLayers(160,120);ensureCadLayer();const item=compileCadScript(SCRIPT_EXAMPLES['Drilled flange']);addCadBody(item);const saved=projectData();assert(JSON.parse(saved).version===12,'Script project needs format 12');resetLayers(10,10);await loadProjectData(saved);assert(currentBodies()[0].script?.source===item.script?.source,'Source lost on reopen');const mesh=await solidMesh(currentBodies()[0]);closedCadMesh(mesh);assert(mesh.volume>10000,'Flange geometry lost');resetLayers(960,640);
});
await asyncCheck('Script CAD solids join existing workshop pieces and export a closed STL',async()=>{
  const {compileCadScript}=await import('../src/cad-script');const scripted=compileCadScript('cube([20,20,10],center=true);'),sphere=primitive('sphere',[12,12,12]);sphere.position=[0,0,5];const joined=combinedBody('union',[scripted,sphere]);const result=await cadCompute([joined],'print');closedCadMesh(result.mesh);assert(result.mesh.volume>4000&&result.mesh.volume<4905,'Join did not fuse the overlapping solids');assert(result.stl?.byteLength===84+result.mesh.triangles*50,'STL triangle count incorrect');
});
check('Neutral photo adjustments preserve every pixel and alpha; exposure and saturation behave independently', () => {
  const source=new ImageData(new Uint8ClampedArray([90,120,160,255,180,90,70,128,10,20,30,0]),3,1),settings=defaultPhotoSettings();
  const neutral=processPhoto(source,settings);assert(neutral.data.every((v,i)=>v===source.data[i]),'Neutral edit changed pixels');
  settings.exposure=1;const exposed=processPhoto(source,settings);assert(exposed.data[0]>source.data[0]&&exposed.data[2]>source.data[2]&&exposed.data[7]===128,'Exposure changed alpha or failed to brighten');
  settings.exposure=0;settings.saturation=-100;const mono=processPhoto(source,settings);assert(mono.data[0]===mono.data[1]&&mono.data[1]===mono.data[2]&&mono.data[7]===128,'Monochrome changed transparency or retained colour');
});
check('Photo shadows and highlights target their own tonal ranges',()=>{
  const source=new ImageData(new Uint8ClampedArray([40,40,40,255,210,210,210,255]),2,1),s=defaultPhotoSettings();
  s.shadows=50;const shadow=processPhoto(source,s);assert(shadow.data[0]-40>shadow.data[4]-210,'Shadow control affects highlights more than shadows');
  s.shadows=0;s.highlights=-50;const highlight=processPhoto(source,s);assert(210-highlight.data[4]>40-highlight.data[0],'Highlight control affects shadows more than highlights');
});
check('RGB curves and individual channels are editable without cross-channel leakage',()=>{
  const source=new ImageData(new Uint8ClampedArray([100,100,100,160]),1,1),s=defaultPhotoSettings();
  s.curves.red=[{x:0,y:0},{x:.4,y:.7},{x:1,y:1}];const out=processPhoto(source,s);
  assert(out.data[0]>160&&out.data[1]===100&&out.data[2]===100&&out.data[3]===160,'Red curve changed another channel');
  const table=curveTable([{x:0,y:0},{x:.25,y:.2},{x:.7,y:.8},{x:1,y:1}]);assert(table.every((v,i)=>v>=0&&v<=1&&(!i||v>=table[i-1])),'Smooth curve introduced a reversal');
});
check('White balance neutralises a sampled cast and auto balance ignores clear pixels',()=>{
  const source=new ImageData(new Uint8ClampedArray([160,130,100,255,250,0,0,0]),2,1),s=defaultPhotoSettings();
  s.balance=neutralBalance([160,130,100]);const out=processPhoto(source,s);assert(Math.max(...out.data.slice(0,3))-Math.min(...out.data.slice(0,3))<=1,'Sample did not become neutral');
  const auto=autoWhiteBalance(source);assert(auto[0]<1&&auto[2]>1,'Auto WB followed transparent colour');
  assert(Object.values(autoPhoto(new ImageData(2,2))).every(Number.isFinite),'Auto light fails on empty images');
});
check('Vibrance protects vivid colour while the colour mixer can target a single hue',()=>{
  const source=new ImageData(new Uint8ClampedArray([255,0,0,255,130,150,180,255,0,0,255,255]),3,1),s=defaultPhotoSettings();s.vibrance=70;
  const vibrant=processPhoto(source,s);assert(vibrant.data[0]===255&&vibrant.data[1]===0&&vibrant.data[2]===0,'Vibrance damaged a fully vivid red');assert(vibrant.data[4]!==130||vibrant.data[6]!==180,'Vibrance failed to enrich muted colour');
  s.vibrance=0;s.mixer[0].saturation=-100;const mixed=processPhoto(source,s);assert(mixed.data[0]===mixed.data[1]&&mixed.data[1]===mixed.data[2]&&mixed.data[10]===255,'Red mixer changed unrelated blue');
});
check('Photo sharpening, Pop and noise reduction alter detail while preserving alpha and strong edges',()=>{
  const source=new ImageData(40,20);for(let y=0;y<20;y++)for(let x=0;x<40;x++){const i=(y*40+x)*4,v=(x<20?70:180)+((x+y)%2?8:-8);source.data.set([v,v,v,x===0?0:200],i);}
  const s=defaultPhotoSettings();s.sharpness=100;const sharp=processPhoto(source,s);assert(sharp.data[(10*40+19)*4]<source.data[(10*40+19)*4],'Sharpening did not enhance an edge');assert(sharp.data.every((v,i)=>i%4!==3||v===source.data[i]),'Sharpening changed alpha');
  s.sharpness=0;s.noise=80;const smooth=processPhoto(source,s);assert(Math.abs(smooth.data[(10*40+9)*4]-smooth.data[(10*40+10)*4])<16,'Noise reduction did not smooth speckles');assert(smooth.data[(10*40+21)*4]-smooth.data[(10*40+18)*4]>90,'Denoise blurred a strong edge');
  s.noise=0;s.pop=60;const pop=processPhoto(source,s);assert(pop.data.some((v,i)=>i%4!==3&&v!==source.data[i]),'Pop did not change local contrast');
});
check('Vignette follows the crop, grain is deterministic, and lens corrections preserve clear margins',()=>{
  const source=new ImageData(40,20);for(let i=0;i<source.data.length;i+=4)source.data.set([150,150,150,255],i);
  const s=defaultPhotoSettings();s.vignette=-75;const vignette=processPhoto(source,s);assert(vignette.data[0]<vignette.data[(10*40+20)*4],'Vignette did not darken corners');
  s.vignette=0;s.grain=30;const grain=processPhoto(source,s),sameGrain=processPhoto(source,s);assert(grain.data.every((v,i)=>v===sameGrain.data[i]),'Grain changes between renders');
  s.grain=0;s.distortion=100;const lens=processPhoto(source,s);assert(lens.data[3]===0&&lens.data[(10*40+20)*4+3]===255,'Lens correction failed to map edges');
  const flipped=defaultPhotoSettings();flipped.flipX=true;source.data.set([255,0,0,255],0);assert(processPhoto(source,flipped).data[(39)*4]===255,'Flip did not mirror pixels');
  const hist=histogram(new ImageData(new Uint8ClampedArray([0,0,0,255,255,255,255,255,255,0,0,0]),3,1));assert(hist.count===2&&hist.clipped[0]===.5&&hist.clipped[1]===.5,'Histogram counted transparent pixels');
});
check('Photo histogram weights translucent pixels by visible opacity',()=>{
  const source=new ImageData(new Uint8ClampedArray([128,128,128,255,0,0,0,1,255,255,255,1,255,0,0,0]),4,1),result=histogram(source);
  assert(Math.abs(result.count-257/255)<1e-12,'Nearly invisible pixels dominate the histogram count');
  assert(Math.abs(result.clipped[0]-1/257)<1e-12&&Math.abs(result.clipped[1]-1/257)<1e-12,'Clipping does not follow visible opacity');
  for(const channel of result.rgb){assert(channel[128]===1&&Math.abs(channel[0]-1/255)<1e-12&&Math.abs(channel[255]-1/255)<1e-12,'Histogram bins lost alpha weighting');}
  const partial=histogram(new ImageData(new Uint8ClampedArray([128,128,128,255,255,255,255,127]),2,1));
  assert(partial.clipped[0]===0&&Math.abs(partial.clipped[1]-127/382)<1e-12,'Partially visible highlights are counted as opaque');
  const faint=histogram(new ImageData(new Uint8ClampedArray([255,255,255,1]),1,1));assert(faint.clipped[0]===0&&faint.clipped[1]===1,'A fractional total opacity was rounded up to one opaque pixel');
  const empty=histogram(new ImageData(3,2));assert(empty.count===0&&empty.clipped.every(n=>n===0)&&empty.rgb.every(channel=>channel.every(n=>n===0)),'Empty histogram is not a defined zero result');
});
await asyncCheck('Photo preview, saved adjustments and crop preserve every source pixel and live ink; Undo restores the recipe and frame',async()=>{
  resetLayers(48,32);const paper=activeLayer().id;addLayer();baseCtx.fillStyle='#557799';baseCtx.fillRect(0,0,W,H);
  const mask=blankMask();mask.getContext('2d')!.fillRect(2,2,5,5);addFill(mask,{kind:'conveyor',colors:['#ff0000','#0000ff'],speed:3,mode:'ooze',along:false,texture:null},1,null);
  const original=image(),live=snapshotLive().fills.length,layer=activeLayer().id;
  beginPhoto().settings.brightness=25;await refreshPhoto();assert(image()===original&&snapshotLive().fills.length===live,'Preview changed stored artwork');
  comparePhoto(true);cancelPhoto();assert(image()===original&&snapshotLive().fills.length===live&&!photoSession,'Cancel changed the source');
  const session=beginPhoto();session.settings.brightness=25;session.settings.crop={x:.25,y:.25,width:.5,height:.5};await applyPhoto();
  assert(W===48&&H===32&&outputFrame(W,H).width===24&&outputFrame(W,H).height===16&&snapshotLive().fills.length===live,'Crop removed original dimensions or live ink');
  assert(layers.find(l=>l.id===paper)!.canvas.width===48&&image()===original&&activeLayer().photo?.settings.brightness===25,'Saving adjustments changed original pixels');
  assert((await renderFullPicture(0)).toDataURL()!==(await renderFullPicture(1000)).toDataURL(),'Saving photo adjustments froze animated ink');
  const exported=await decodeImage(await imageBlob('png'));assert(exported.width===24&&exported.height===16&&exported.getContext('2d')!.getImageData(10,10,1,1).data[0]>85,'Export did not apply the recipe and frame');
  const reopened=beginPhoto();assert(reopened.settings.brightness===25&&reopened.settings.crop.width===.5,'Reopening lost settings');cancelPhoto();
  undo();assert(outputFrame(W,H).width===48&&activeLayer().id===layer&&image()===original&&snapshotLive().fills.length===live&&!activeLayer().photo,'Undo did not restore recipe and frame together');
  redo();assert(outputFrame(W,H).width===24&&activeLayer().photo?.settings.brightness===25,'Redo did not restore photo edit');
});
await asyncCheck('PNG, JPEG, WebP, BMP and GIF exports decode at the actual picture dimensions', async () => {
  resetLayers(32, 24, null); baseCtx.fillStyle = '#ff0000'; baseCtx.fillRect(5, 5, 12, 10);
  for (const format of ['png', 'jpeg', 'webp', 'bmp', 'gif']) {
    const blob = await imageBlob(format), decoded = await decodeImage(blob); assert(decoded.width === 32 && decoded.height === 24, format + ' dimensions changed');
    const p = decoded.getContext('2d')!.getImageData(10, 10, 1, 1).data; assert(p[0] > 220 && p[1] < 25 && p[2] < 25, format + ' colours changed');
    if (format === 'png' || format === 'gif' || format === 'webp') assert(decoded.getContext('2d')!.getImageData(0, 0, 1, 1).data[3] === 0, format + ' lost transparency');
  }
});
await asyncCheck('Imported JPEG photo edits render at full resolution, export correctly and cancel safely during processing',async()=>{
  const fixture=document.createElement('canvas');fixture.width=1600;fixture.height=1000;const ctx=fixture.getContext('2d')!,gradient=ctx.createLinearGradient(0,0,1600,1000);
  gradient.addColorStop(0,'#336688');gradient.addColorStop(.5,'#bb9977');gradient.addColorStop(1,'#88aabb');ctx.fillStyle=gradient;ctx.fillRect(0,0,1600,1000);ctx.fillStyle='#eecc66';ctx.fillRect(400,250,300,200);
  const jpeg=await new Promise<Blob>(resolve=>fixture.toBlob(blob=>resolve(blob!),'image/jpeg',.9));await importImage(jpeg);const original=image();
  const first=beginPhoto();first.settings.pop=35;first.settings.sharpness=40;first.settings.noise=20;first.settings.vignette=-15;await applyPhoto();
  assert(W===1600&&H===1000&&image()===original&&activeLayer().photo?.settings.pop===35,'Full-size edit changed the source');
  const expected=document.createElement('canvas');expected.width=W;expected.height=H;expected.getContext('2d')!.putImageData(processPhoto(baseCtx.getImageData(0,0,W,H),first.settings),0,0);
  const exported=await decodeImage(await imageBlob('png'));assert(exported.width===1600&&exported.height===1000&&exported.toDataURL()===expected.toDataURL()&&exported.toDataURL()!==original,'Photo export differs from the full-resolution recipe');
  undo();assert(image()===original,'Undo lost the imported JPEG');
  beginPhoto().settings.distortion=30;const pending=applyPhoto();cancelPhoto();assert(!await pending&&image()===original,'Cancel during processing changed pixels');
});
check('Normal restores the exact pre-look settings, presets do not accumulate, and manual edits are Custom',()=>{
  const recipe=newPhotoRecipe();recipe.settings.brightness=17;recipe.settings.temperature=-12;recipe.settings.curves.red=[{x:0,y:0},{x:.5,y:.6},{x:1,y:1}];photoManualChange(recipe);
  assert(recipe.look==='custom');const before=JSON.stringify(recipe.settings);
  choosePhotoLook(recipe,'warm');assert(recipe.look==='warm'&&recipe.settings.grain===12);
  choosePhotoLook(recipe,'mono');assert(recipe.settings.temperature===-12&&recipe.settings.grain===0&&recipe.settings.saturation===-100,'Looks accumulated');
  recipe.settings.brightness=30;photoManualChange(recipe);assert(recipe.look==='custom');choosePhotoLook(recipe,'normal');
  assert(JSON.stringify(recipe.settings)===before&&recipe.look==='normal','Normal lost the pre-look baseline');
});
await asyncCheck('Photo reset restores originals and uncropped margins after more edits than Undo retains; project files preserve editable recipes',async()=>{
  resetLayers(40,30,null);baseCtx.fillStyle='#345678';baseCtx.fillRect(0,0,W,H);baseCtx.fillStyle='#ff0000';baseCtx.fillRect(0,0,5,5);const original=image();
  const edit=beginPhoto();Object.assign(edit.settings,{exposure:.3,brightness:5,contrast:12,highlights:-20,shadows:15,whites:7,blacks:-8,temperature:18,tint:-4,saturation:8,vibrance:12,hue:5,sharpness:30,radius:1.5,threshold:3,texture:12,clarity:8,pop:5,dehaze:7,noise:10,colourNoise:10,vignette:-20,midpoint:40,feather:60,roundness:30,grain:5,distortion:10,aberration:8,vertical:5,horizontal:-3,angle:3,zoom:110,flipX:true,crop:{x:.25,y:.2,width:.5,height:.6}});
  edit.settings.curves.blue=[{x:0,y:0},{x:.5,y:.6},{x:1,y:1}];edit.settings.mixer[2].saturation=-15;photoManualChange(edit);choosePhotoLook(edit,'warm');await applyPhoto();
  const saved=projectData();resetLayers(10,10);await loadProjectData(saved);
  assert(image()===original&&documentCrop().width===.5&&activeLayer().photo?.look==='warm','Project did not retain originals, frame and look');
  const reopened=beginPhoto();assert(reopened.settings.angle===3&&reopened.settings.curves.blue.length===3&&reopened.normal.temperature===18,'Project lost editable controls or Normal baseline');cancelPhoto();
  const bad=JSON.parse(saved);bad.layers[0].photo.settings.curves.red=[{x:0,y:0},{x:0,y:1}];const beforeBad=projectData();let rejected=false;try{await loadProjectData(JSON.stringify(bad));}catch{rejected=true;}assert(rejected&&projectData()===beforeBad,'Invalid photo data changed the document');
  for(let i=0;i<22;i++){const s=beginPhoto();s.settings.brightness=i+1;await applyPhoto();assert(image()===original,'Repeated edits modified source pixels');}
  const reset=beginPhoto();Object.assign(reset,newPhotoRecipe());await applyPhoto();
  assert(image()===original&&outputFrame(W,H).width===40&&outputFrame(W,H).height===30,'Reset failed without relying on Undo');
  assert((await decodeImage(await imageBlob('png'))).toDataURL()===original,'Reset export did not recover original margins');
  const legacy=JSON.parse(saved);legacy.version=1;delete legacy.crop;for(const l of legacy.layers)delete l.photo;await loadProjectData(JSON.stringify(legacy));assert(image()===original&&outputFrame(W,H).width===40,'Legacy projects no longer load');
});
await asyncCheck('TIFF round-trips RGBA pixels through the local encoder and decoder', async () => {
  const before = baseCtx.getImageData(0, 0, W, H), decoded = decodeTiff(await encodeTiff(before).arrayBuffer());
  assert(decoded.toDataURL() === image(), 'TIFF pixels did not round-trip');
});
await asyncCheck('WebP export preserves high contrast colour boundaries and exact alpha',async()=>{
  resetLayers(32,24,null);
  for(let y=0;y<24;y++)for(let x=0;x<32;x++){baseCtx.fillStyle=x%2?'#ff0000':'#0000ff';baseCtx.globalAlpha=y<12?1:.5;baseCtx.fillRect(x,y,1,1);}baseCtx.globalAlpha=1;
  const expected=baseCtx.getImageData(0,0,W,H).data,decoded=await decodeImage(await imageBlob('webp')),actual=decoded.getContext('2d')!.getImageData(0,0,W,H).data;
  for(let i=0;i<expected.length;i+=4){assert(actual[i+3]===expected[i+3],'WebP changed alpha');for(let c=0;c<3;c++)assert(Math.abs(actual[i+c]-expected[i+c])<=4,'WebP colour boundary changed by '+Math.abs(actual[i+c]-expected[i+c]));}
});
// Independent two-strip fixture: do not use the encoder under test as the oracle.
function stripTiff(little = true): ArrayBuffer {
  const bytes = new Uint8Array(168), data = new DataView(bytes.buffer);
  const tags = [[256,4,1,2],[257,4,1,2],[258,3,3,134],[259,3,1,1],[262,3,1,2],[273,4,2,140],[277,3,1,3],[278,4,1,1],[279,4,2,148],[284,3,1,1]];
  bytes.set(little ? [73,73,42,0] : [77,77,0,42]);data.setUint32(4,8,little);data.setUint16(8,tags.length,little);
  tags.forEach(([tag,type,count,value],i)=>{const at=10+i*12;data.setUint16(at,tag,little);data.setUint16(at+2,type,little);data.setUint32(at+4,count,little);if(type===3&&count===1)data.setUint16(at+8,value,little);else data.setUint32(at+8,value,little);});
  for(let i=0;i<3;i++)data.setUint16(134+i*2,8,little);
  data.setUint32(140,156,little);data.setUint32(144,162,little);data.setUint32(148,6,little);data.setUint32(152,6,little);
  bytes.set([255,0,0,0,255,0,0,0,255,255,255,255],156);return bytes.buffer;
}
check('TIFF independent multi-strip RGB fixture decodes both byte orders',()=>{
  for(const little of [true,false]){const canvas=decodeTiff(stripTiff(little));assert(canvas.width===2&&canvas.height===2);assert(Array.from(canvas.getContext('2d')!.getImageData(0,0,2,2).data).join(',')==='255,0,0,255,0,255,0,255,0,0,255,255,255,255,255,255','Multi-strip pixels or byte order changed');}
});
check('TIFF damaged headers and directory offsets explain recovery',()=>{
  const broken=[...Array.from({length:8},(_,length)=>stripTiff().slice(0,length)),stripTiff().slice(0,100)];
  for(const at of [4,10+2*12+8]){const buffer=stripTiff();new DataView(buffer).setUint32(at,buffer.byteLength-1,true);broken.push(buffer);}
  for(const buffer of broken){let error='';try{decodeTiff(buffer);}catch(caught){error=String(caught);}assert(/damaged|incomplete/i.test(error)&&/another copy|PNG/i.test(error),'No actionable damaged-file explanation: '+error);}
});
await asyncCheck('TIFF incomplete strip tables and pixel data are rejected without changing the document',async()=>{
  resetLayers(24,16,null);baseCtx.fillStyle='#d92772';baseCtx.fillRect(2,3,8,6);const before=projectData();
  const edits=[(v:DataView)=>v.setUint32(10+5*12+4,1,true),(v:DataView)=>v.setUint32(10+8*12+4,1,true),(v:DataView)=>v.setUint16(10+7*12+8,0,true),(v:DataView)=>v.setUint32(144,167,true),(v:DataView)=>v.setUint32(152,100,true)];
  const broken=edits.map(edit=>{const buffer=stripTiff();edit(new DataView(buffer));return buffer;});broken.push(stripTiff().slice(0,167));
  for(const buffer of broken){let error='';try{await importImage(new Blob([buffer],{type:'image/tiff'}));}catch(caught){error=String(caught);}assert(/damaged|incomplete/i.test(error),'Incomplete TIFF was accepted or exposed a raw exception: '+error);assert(projectData()===before,'Rejected TIFF changed the complete document');}
});
await asyncCheck('Projects round-trip layers, visibility, opacity and live fills; invalid projects leave artwork intact', async () => {
  resetLayers(48, 32); addLayer(); activeLayer().name = 'Dancing ink'; activeLayer().opacity = 0.65;
  const mask = blankMask(); mask.getContext('2d')!.fillRect(5, 5, 20, 10);
  addFill(mask, { kind: 'conveyor', colors: ['#ff0000', '#0000ff'], speed: 3, mode: 'ooze', along: false, texture: null }, 1, null);
  const source = projectData(); resetLayers(20, 20); await loadProjectData(source);
  assert(W === 48 && H === 32 && layers.length === 2 && activeLayer().name === 'Dancing ink' && activeLayer().opacity === 0.65 && snapshotLive().fills.length === 1);
  const before = projectData(); let rejected = false; try { await loadProjectData('{"format":"RetroPaint","version":1,"width":-10}'); } catch { rejected = true; }
  assert(rejected && projectData() === before, 'A corrupt project damaged the drawing');
});
await asyncCheck('Project validation rejects missing active layers and fractional layer IDs atomically',async()=>{
  resetLayers(24,16,null);baseCtx.fillStyle='#ff0000';baseCtx.fillRect(2,3,8,6);addLayer();baseCtx.fillStyle='#0000ff';baseCtx.fillRect(10,4,6,8);const valid=JSON.parse(projectData());
  resetLayers(18,12,null);baseCtx.fillStyle='#00ff00';baseCtx.fillRect(1,1,12,8);const before=projectData();
  const variants=[(p:typeof valid)=>{p.active=999999;},(p:typeof valid)=>{p.active+=.5;},(p:typeof valid)=>{p.layers[0].id+=.5;},(p:typeof valid)=>{p.layers[0].id=p.layers[1].id;}];
  for(const change of variants){const invalid=structuredClone(valid);change(invalid);let rejected=false;try{await loadProjectData(JSON.stringify(invalid));}catch{rejected=true;}assert(rejected,'Invalid layer reference or ID was accepted');assert(projectData()===before,'Invalid layer metadata replaced unsaved artwork');}
  await loadProjectData(JSON.stringify(valid));assert(W===24&&H===16&&layers.length===2,'Valid opening after rejection failed');
});
await asyncCheck('Project validation explains incomplete JSON without changing artwork',async()=>{
  resetLayers(24,16,null);baseCtx.fillStyle='#f53674';baseCtx.fillRect(1,1,8,8);const before=projectData();
  for(const source of ['', '{', before.slice(0,-12), before.replace('"width":24','"width":NaN')]){let error='';try{await loadProjectData(source);}catch(caught){error=String(caught);}assert(/project file.*damaged or incomplete/i.test(error)&&/another saved copy/i.test(error),'Raw or unactionable parser error: '+error);assert(projectData()===before,'Incomplete JSON changed the document');}
});
await asyncCheck('Project validation identifies a newer version and preserves the current document',async()=>{
  resetLayers(24,16,null);const before=projectData(),source=JSON.parse(before);
  for(const version of [14,999]){let error='';try{await loadProjectData(JSON.stringify({...source,version}));}catch(caught){error=String(caught);}assert(/newer RetroPaint version/i.test(error)&&/Update RetroPaint/i.test(error),'Future version was not explained: '+error);assert(projectData()===before,'Future project changed the current document');}
});
cancelSelection(); resetLayers(960, 640); state.shapeFill = 'none'; state.shapeOutline = 'brush'; state.liveArmed = false;

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
check('Super resolution checks exact 2× and 4× dimensions before allocating memory',()=>{
  assert(enhancementSize(37,29,2).width===74&&enhancementSize(37,29,4).height===116,'Enhancement size is incorrect');
  assert(enhancementSize(4096,3072,4).width===16384,'A normal imported photo cannot use 4× enhancement');
  for(const [w,h,s] of [[8192,8192,4],[0,24,2],[10,10,3]]){let rejected=false;try{enhancementSize(w,h,s as 2|4);}catch{rejected=true;}assert(rejected,'Invalid enhancement was accepted');}
});
await asyncCheck('Both neural super-resolution models produce full-size pixels, preserve alpha and report progress',async()=>{
  const processor=new SuperResolutionProcessor(),source=new ImageData(8,6);
  for(let y=0;y<6;y++)for(let x=0;x<8;x++){const p=(y*8+x)*4;source.data.set([x*30,y*40,(x+y)%2?180:60,x===0?0:x===1?128:255],p);}
  try{for(const scale of [2,4] as const){
    const progress:number[]=[],result=await processor.process(new ImageData(source.data.slice(),8,6),scale,value=>progress.push(value.fraction));
    assert(result.width===8*scale&&result.height===6*scale,'Neural output dimensions are wrong');assert(progress.at(-1)===1,'Enhancement progress did not finish');
    let variation=false;for(let i=0;i<result.data.length;i+=4){if(result.data[i+3]===0)assert(result.data[i]===0&&result.data[i+1]===0&&result.data[i+2]===0,'Transparent pixels carry a matte');if(result.data[i+3]===255&&result.data[i]>10&&result.data[i]<240)variation=true;}
    assert(variation,'Neural output lost the image');assert(result.data[3]===0&&result.data[(result.width-1)*4+3]===255,'Alpha endpoints changed');
    assert(result.data.some((n,i)=>i%4===3&&n>0&&n<255),'Translucent edges were lost');
    if(scale===2){
      const streamed=await processor.processPng(new ImageData(source.data.slice(),8,6),scale,{x:2,y:1,width:3,height:3},()=>{}),bitmap=await createImageBitmap(streamed.png);
      assert(bitmap.width===16&&bitmap.height===12,'Neural PNG has the wrong full-image dimensions');bitmap.close();
      for(let y=0;y<6;y++)for(let x=0;x<6;x++)for(let c=0;c<4;c++)assert(streamed.preview.data[(y*6+x)*4+c]===result.data[((y+2)*16+x+4)*4+c],'Export detail does not match the selected area');
    }
  }}finally{processor.dispose();}
});
await asyncCheck('Cancelling neural inference releases the worker and leaves the document intact',async()=>{
  const before=projectData(),processor=new SuperResolutionProcessor(),pending=processor.process(new ImageData(16,12),4,()=>{});processor.dispose();let cancelled=false;try{await pending;}catch{cancelled=true;}
  assert(cancelled&&projectData()===before,'Cancellation changed the picture or left inference pending');
});
await asyncCheck('Streamed PNG row bands decode exactly, including alpha and the last row',async()=>{
  const source=new ImageData(7,5);for(let i=0;i<source.data.length;i++)source.data[i]=(i*53)%256;
  const png=new PngStream(7,5);await png.write(source.data.slice(0,7*2*4),2);await png.write(source.data.slice(7*2*4),3);const blob=await png.finish(),bitmap=await createImageBitmap(blob),canvas=document.createElement('canvas');canvas.width=7;canvas.height=5;canvas.getContext('2d')!.drawImage(bitmap,0,0);bitmap.close();
  const actual=canvas.getContext('2d')!.getImageData(0,0,7,5).data;
  for(let i=0;i<actual.length;i++)assert(i%4===3?actual[i]===source.data[i]:Math.abs(actual[i]-source.data[i])<=Math.ceil(255/source.data[i-i%4+3]),'PNG row filtering or alpha changed');
});
await asyncCheck('Large enhanced copies stream beyond the former 32-megapixel limit without a giant output canvas',async()=>{
  const processor=new SuperResolutionProcessor();try{
    const region=enhancementRegion(2048,1024,.85,.2),result=await processor.processPng(new ImageData(2048,1024),4,region,()=>{}),header=new DataView(await result.png.slice(0,24).arrayBuffer());
    assert(header.getUint32(16)===8192&&header.getUint32(20)===4096,'Large tiled PNG dimensions are incorrect');assert(result.preview.width===512&&result.preview.height===512&&result.preview.data.every(n=>n===0),'Selected detail preview does not match the exported area');
  }finally{processor.dispose();}
});
check('Photographic grain is deterministic, neutral, structured, adjustable and preserves source pixels',()=>{
  const legacy=JSON.parse(JSON.stringify(newPhotoRecipe()));delete legacy.settings.grainSize;delete legacy.settings.grainRoughness;delete legacy.normal.grainSize;delete legacy.normal.grainRoughness;
  assert(readPhotoRecipe(legacy)?.settings.grainSize===1.2,'Older editable photo projects no longer load');
  const source=new ImageData(384,256);for(let i=0;i<source.data.length;i+=4)source.data.set([128,128,128,i%28===0?0:255],i);
  const s=defaultPhotoSettings();s.grain=65;s.grainSize=2;s.grainRoughness=75;const a=processPhoto(source,s),b=processPhoto(source,s);
  assert(a.data.every((value,i)=>value===b.data[i]),'Grain changes between renders');let sum=0,count=0,change=0;
  for(let i=0;i<a.data.length;i+=4){assert(a.data[i+3]===source.data[i+3],'Grain changed alpha');if(a.data[i+3]){assert(a.data[i]===a.data[i+1]&&a.data[i]===a.data[i+2],'Grain adds coloured noise');sum+=a.data[i];count++;if(i>4)change+=Math.abs(a.data[i]-a.data[i-4]);}}
  assert(Math.abs(sum/count-128)<2&&change/count>1,'Grain washed out the picture or has no texture');s.grainSize=.5;s.grainRoughness=0;assert(processPhoto(source,s).data.some((value,i)=>value!==a.data[i]),'Size and roughness do not change the texture');assert(source.data[4]===128,'Grain modified the source');
});
check('Spiro radius scales with large paper and accepts sizes outside the old limits',()=>{
  resetLayers(4096,3072);resetKit();assert(state.spiro.R===1024,'Large paper still starts with a tiny ring');setRingRadius(1800);assert(state.spiro.R===1800,'Large rings are capped');setRingRadius(4);assert(state.spiro.R===4,'Small rings are capped');resetLayers(160,120);
});
function objectTestReset(){resetLayers(160,120);reset();state.drawingMode='vector';state.shapeFill='primary';state.shapeOutline='none';state.brushWidth=4;ensureObjectLayer();}
function objectPixel(x:number,y:number){const output=document.createElement('canvas');output.width=W;output.height=H;renderLayers(output.getContext('2d')!,0);return Array.from(output.getContext('2d')!.getImageData(x,y,1,1).data).join(',');}
check('Vector pieces resize from geometry without touching overlapping neighbours',()=>{
  objectTestReset();addVectorShape('rect',10,10,30,30);const first=selectedObjects()[0];state.ink='#0000ff';addVectorShape('rect',20,20,60,60);const second=selectedObjects()[0];
  selectObjects([first.id]);resizeObjects(80,80);assert(selectedObjects()[0].kind==='path'&&selectedObjects()[0].width===20,'Resizing rasterised the vector');assert(objectPixel(50,50)==='0,0,255,255','Resizing changed the front piece');moveObjects(50,0);assert(objectPixel(25,25)==='0,0,255,255','Moving lifted neighbouring pixels');deleteObjects();assert(activeLayer().objects?.length===1&&activeLayer().objects?.[0].id===second.id,'Delete removed a neighbour');undo();assert(activeLayer().objects?.length===2,'Undo did not restore the piece');redo();assert(activeLayer().objects?.length===1,'Redo did not remove the piece');
});
check('Each brush stroke is a cropped raster piece, with independent alpha and reusable source pixels',()=>{
  objectTestReset();state.tool='draw';state.shapeFill='none';pushHistory();beginObjectStroke();beginStrokeGeneration();segment(15,30,90,30,8,0);finishObjectStroke();const first=selectedObjects()[0];assert(first.kind==='raster'&&first.image.width<160&&first.image.height<40,'Stroke is not stored as a compact raster piece');
  state.ink='#0000ff';pushHistory();beginObjectStroke();beginStrokeGeneration();segment(50,15,50,80,8,0);finishObjectStroke();const second=selectedObjects()[0];selectObjects([first.id]);moveObjects(0,40);assert(objectPixel(50,30)==='0,0,255,255','Moving a crossing stroke damaged its neighbour');resizeObjects(130,30);resizeObjects(30,5);assert(selectedObjects()[0].kind==='raster'&&(selectedObjects()[0] as typeof first).image===first.image,'Repeated resizing degraded the source');deleteObjects();assert(activeLayer().objects?.[0].id===second.id);
});
check('Curved vector shapes stay smooth after extreme enlargement and support precise hit testing',()=>{
  objectTestReset();addVectorShape('ellipse',10,10,18,18);const object=selectedObjects()[0];assert(object.kind==='path'&&object.paths[0].svg,'Ellipse lost its analytic curve');resizeObjects(1000,1000);assert(hitObject(20,20)===null,'Transparent object corners intercept clicks');assert(hitObject(150,400)?.id===object.id,'Visible part of resized ellipse cannot be selected');
});
check('Groups duplicate, turn, resize beyond the paper and stay within their normal layer',()=>{
  objectTestReset();addVectorShape('rect',20,20,40,40);const first=selectedObjects()[0];addVectorShape('rect',60,20,80,40);selectObjects([first.id,selectedObjects()[0].id]);const count=layers.length;duplicateObjects();assert(activeLayer().objects?.length===4&&layers.length===count,'Pieces became public layers');rotateObjects(90);resizeObjects(7000,4000);assert(Math.abs(objectSelectionBounds()!.width-7000)<.01,'Object size is limited to the paper');
});
check('Manual Spiro produces an editable vector path at the selected ring size',()=>{
  objectTestReset();state.tool='spiro';state.spiro.R=70;state.spiro.cx=80;state.spiro.cy=60;state.spiro.gearId='red';crankStart(120,60);crankMove(80,100);finishSpiroStroke();const object=selectedObjects()[0];assert(object.kind==='path'&&object.name==='Spiro'&&object.paths[0].points.length>30,'Spiro was flattened');resizeObjects(3000,2000);assert(objectSelectionBounds()!.width>2999,'Spiro cannot be resized');
});
await asyncCheck('Project files preserve vector geometry, raster pieces, live ink, transforms and photo recipes',async()=>{
  objectTestReset();addVectorShape('ellipse',5,5,35,35);resizeObjects(70,45);const shape=selectedObjects()[0];state.tool='draw';state.liveArmed=true;state.conveyor=['#ff0000','#0000ff'];beginObjectStroke();beginStrokeGeneration();segment(45,70,100,70,5,0);finishObjectStroke();const stroke=selectedObjects()[0];const recipe=newPhotoRecipe();recipe.settings.brightness=12;activeLayer().photo=recipe;
  const before=projectData(),saved=JSON.parse(before);assert(saved.version===10&&saved.layers[0].objects.length===2,'Project omitted the pieces');resetLayers(10,10);await loadProjectData(before);assert(W===160&&H===120&&state.drawingMode==='vector'&&activeLayer().photo?.settings.brightness===12,'Project lost its drawing mode or recipe');
  assert(activeLayer().objects?.[0].kind==='path'&&JSON.stringify(activeLayer().objects?.[0].matrix)===JSON.stringify(shape.matrix),'Vector transform changed');assert(activeLayer().objects?.[1].kind==='raster'&&activeLayer().objects?.[1].live?.strokes.length&&activeLayer().objects?.[1].id===stroke.id,'Live raster stroke did not survive');selectObjects([shape.id]);resizeObjects(100,50);assert(selectedObjects()[0].kind==='path','Reopened vector no longer edits');const exported=await imageBlob('png');assert(exported.size>0,'Objects cannot export');
  state.liveArmed=false;state.drawingMode='raster';clearObjectSelection();resetLayers(960,640);
});
check('Existing artwork converts without a visual change, and later raster strokes keep their stacking order',()=>{
  resetLayers(160,120);reset();block(10,10);const before=objectPixel(15,15);state.drawingMode='vector';ensureObjectLayer();assert(objectPixel(15,15)===before&&activeLayer().objects?.length===1,'Existing artwork changed');state.drawingMode='raster';beginObjectStroke();state.ink='#0000ff';beginStrokeGeneration();segment(15,15,70,15,8,0);finishObjectStroke();assert(objectPixel(25,15)==='0,0,255,255','Raster stroke appeared under existing vectors');state.drawingMode='raster';resetLayers(960,640);
});
check('Pointer gestures create vector shapes, move them, resize with handles and keep each brush stroke separate',()=>{
  objectTestReset();state.tool='shapes';state.shape='rect';const savedStyle=inputStage.style.cssText,savedCapture=view.setPointerCapture;inputStage.style.display='block';view.setPointerCapture=()=>{};
  const send=(type:string,x:number,y:number)=>{const r=view.getBoundingClientRect();view.dispatchEvent(new PointerEvent(type,{pointerId:310,button:0,buttons:type==='pointerup'?0:1,clientX:r.left+x/W*r.width,clientY:r.top+y/H*r.height}));};
  try{
    send('pointerdown',10,10);send('pointermove',90,60);send('pointerup',90,60);assert(activeLayer().objects?.length===1&&selectedObjects()[0].kind==='path','Shape gesture did not retain geometry');
    state.tool='scissors';send('pointerdown',50,35);send('pointermove',70,65);send('pointerup',70,65);assert(Math.abs(objectSelectionBounds()!.x-30)<.01&&Math.abs(objectSelectionBounds()!.y-40)<.01,'Dragging did not move the shape');
    send('pointerdown',110,90);send('pointermove',150,110);send('pointerup',150,110);assert(Math.abs(objectSelectionBounds()!.width-120)<.01,'Handle dragging did not resize the shape');
    state.tool='draw';send('pointerdown',20,100);send('pointermove',60,100);send('pointerup',90,100);send('pointerdown',20,115);send('pointerup',90,115);assert(activeLayer().objects?.length===3&&activeLayer().objects?.slice(1).every(o=>o.kind==='raster'),'Separate pointer strokes were merged or vectorised');assert(!hasObjectCapture(),'A released pointer retained its capture surface');
  }finally{view.setPointerCapture=savedCapture;inputStage.style.cssText=savedStyle;state.drawingMode='raster';resetLayers(960,640);}
});
check('Transparent eraser strokes stay movable and reversible while preserving underlying objects',()=>{
  resetLayers(160,120,null);resetPaint(baseCtx);state.drawingMode='vector';state.tool='shapes';state.ink='#ff0000';state.opacity=1;state.shapeFill='primary';state.shapeOutline='none';ensureObjectLayer();addVectorShape('rect',10,10,120,100);
  state.tool='eraser';state.eraserMode='scrub';pushHistory();beginObjectStroke('Eraser stroke','destination-out');beginStrokeGeneration();segment(40,20,40,90,12,0);finishObjectStroke();const eraser=selectedObjects()[0];assert(objectPixel(40,50)==='0,0,0,0','Eraser did not cut through the object');moveObjects(40,0);assert(objectPixel(40,50)==='255,0,0,255'&&objectPixel(80,50)==='0,0,0,0','Eraser stroke cannot be moved independently');deleteObjects();assert(objectPixel(80,50)==='255,0,0,255','Deleting the eraser failed to restore underlying artwork');assert(eraser.kind==='raster','Eraser became vector geometry');state.drawingMode='raster';resetLayers(960,640);
});
check('Auto Spiro retains its raster capture until the motor has completed after pointer release',()=>{
  objectTestReset();addVectorShape('rect',5,5,10,10);state.drawingMode='raster';state.tool='spiro';state.spiro.drive='auto';state.spiro.R=45;state.spiro.cx=80;state.spiro.cy=60;state.spiro.theta=0;state.brushWidth=2;const center=gearCenter()!;
  const savedStyle=inputStage.style.cssText,savedCapture=view.setPointerCapture;inputStage.style.display='block';view.setPointerCapture=()=>{};
  try{const r=view.getBoundingClientRect(),event={pointerId:311,button:0,clientX:r.left+center.x/W*r.width,clientY:r.top+center.y/H*r.height};view.dispatchEvent(new PointerEvent('pointerdown',event));view.dispatchEvent(new PointerEvent('pointerup',event));assert(hasObjectCapture(),'Pointer release prematurely flattened the motor stroke');tickMotor(performance.now()+5000);assert(!hasObjectCapture()&&activeLayer().objects?.length===2&&activeLayer().objects?.at(-1)?.name==='Spiro','Motor drawing was not retained as one editable piece');}
  finally{view.setPointerCapture=savedCapture;inputStage.style.cssText=savedStyle;state.drawingMode='raster';state.spiro.drive='manual';resetLayers(960,640);}
});
check('Pixel effects preserve the selected piece’s depth beneath overlapping neighbours, including during the gesture',()=>{
  objectTestReset();addVectorShape('rect',10,10,100,100);const lower=selectedObjects()[0];state.ink='#0000ff';addVectorShape('rect',40,40,80,80);const upper=selectedObjects()[0];selectObjects([lower.id]);assert(beginObjectPixelEdit(),'Could not edit one piece');baseCtx.fillStyle='#00ff00';baseCtx.fillRect(10,10,90,90);assert(objectPixel(60,60)==='0,0,255,255','Preview jumped in front of a neighbouring piece');finishObjectStroke();assert(activeLayer().objects?.[1].id===upper.id&&objectPixel(60,60)==='0,0,255,255','Effect changed stacking order');assert(objectPixel(20,20)==='0,255,0,255','Effect did not edit the selected piece');undo();assert(activeLayer().objects?.[0].kind==='path','Undo lost the original geometry');state.drawingMode='raster';resetLayers(960,640);
});
check('A floating raster can cross every paper edge, return intact before placement and clip on placement',()=>{
  resetLayers(160,120);reset();block(10,10);selectRegion(rectangle(10,10,50,50));moveSelection(-35,-30);assert(selectionBounds()!.x===-25&&selectionBounds()!.y===-20);moveSelection(35,30);assert(selectionBounds()!.x===10&&selectionBounds()!.y===10,'Returning before placement lost the position');moveSelection(140,100);commitSelection();assert(pixel(155,115)==='255,0,0,255','Visible corner was not placed');assert(pixel(159,119)==='255,0,0,255');selectRegion(rectangle(150,110,160,120));moveSelection(-100,-80);commitSelection();assert(pixel(55,35)==='255,0,0,255'&&pixel(65,35)==='255,255,255,255','Trimmed pixels reappeared when the section moved back');resetLayers(960,640);
});
function twoColourPiece():HTMLCanvasElement {const canvas=document.createElement('canvas');canvas.width=40;canvas.height=40;const ctx=canvas.getContext('2d')!;ctx.fillStyle='#ff0000';ctx.fillRect(0,0,20,40);ctx.fillStyle='#0000ff';ctx.fillRect(20,0,20,40);return canvas;}
check('Editable raster placement discards hidden pixels without snapping and combines with move Undo',()=>{
  objectTestReset();addRasterImage(twoColourPiece(),{x:10,y:10});const id=selectedObjects()[0].id;moveObjects(-40,0);moveObjects(40,0);assert(objectPixel(15,15)==='255,0,0,255','An uncommitted move discarded its source');moveObjects(-40,0);commitObjectSelection();const clipped=activeLayer().objects!.find(o=>o.id===id)!;assert(clipped.kind==='raster'&&clipped.image.width===10&&objectBounds(clipped).x===0,'Raster pixels were not physically trimmed');assert(objectPixel(5,15)==='0,0,255,255','Placement moved the visible portion');undo();const restored=activeLayer().objects!.find(o=>o.id===id)!;assert(restored.kind==='raster'&&restored.image.width===40&&objectBounds(restored).x===10,'Move and trim require separate Undo steps');redo();selectObjects([id]);moveObjects(60,0);assert(objectPixel(65,15)==='0,0,255,255'&&objectPixel(45,15)==='255,255,255,255','Off-paper pixels returned after placement');state.drawingMode='raster';resetLayers(960,640);
});
check('Fully off-paper raster pieces are removed on Place while vectors retain all of their geometry',()=>{
  objectTestReset();addRasterImage(twoColourPiece(),{x:10,y:10});moveObjects(500,0);commitObjectSelection();assert(activeLayer().objects!.length===0,'Off-paper raster was kept');undo();assert(activeLayer().objects!.length===1,'Undo did not restore discarded raster');clearObjectSelection();addVectorShape('ellipse',20,20,60,60);const object=selectedObjects()[0];moveObjects(-500,400);commitObjectSelection();assert(activeLayer().objects!.some(o=>o.id===object.id&&o.kind==='path'),'Vector was clipped or removed');selectObjects([object.id]);moveObjects(500,-400);assert(objectPixel(40,40)==='229,57,53,255','Vector could not return intact');state.drawingMode='raster';resetLayers(960,640);
});
check('Rotated, skewed and flipped raster trimming preserves source resolution and visible placement',()=>{
  const image=twoColourPiece(),baseObject:RasterObject={id:'test',name:'test',kind:'raster',image,width:40,height:40,opacity:1,matrix:[1,0,0,1,0,0]};
  for(const matrix of [[-1,0,0,1,20,10],[.8,.6,-.6,.8,5,-10],[1,.2,.5,1,-30,8]] as RasterObject['matrix'][]){const object={...baseObject,matrix},trimmed=trimRasterToPaper(object,60,60);assert(trimmed,'Visible raster was removed');const b=objectBounds(trimmed);assert(b.x>=-1e-6&&b.y>=-1e-6&&b.x+b.width<=60.000001&&b.y+b.height<=60.000001,'A clip mask still includes off-paper geometry');assert(trimmed.image.width<=40&&trimmed.image.height<=40,'Trimming upsampled the bitmap');assert(trimRasterToPaper(trimmed,60,60)===trimmed,'Repeated placement keeps resampling the piece');}
});
await asyncCheck('Trimmed raster clips and complete off-paper vectors survive project saving and reopening',async()=>{
  objectTestReset();addRasterImage(twoColourPiece(),{x:10,y:10});moveObjects(-40,0);commitObjectSelection();addVectorShape('rect',10,70,50,100);const id=selectedObjects()[0].id;moveObjects(300,0);commitObjectSelection();const source=projectData();resetLayers(10,10);await loadProjectData(source);const raster=activeLayer().objects!.find(o=>o.kind==='raster')!;assert(raster.kind==='raster'&&raster.image.width===10&&raster.clip?.length,'Project lost the permanent raster trim');selectObjects([id]);moveObjects(-300,0);assert(objectPixel(20,80)==='229,57,53,255','Project discarded off-paper vector geometry');state.drawingMode='raster';resetLayers(960,640);
});
check('Coalesced pen samples preserve the curve between pointer events rather than drawing a shortcut',()=>{
  resetLayers(160,120);reset();state.brushWidth=6;state.tool='draw';const savedStyle=inputStage.style.cssText,savedCapture=view.setPointerCapture;inputStage.style.display='block';view.setPointerCapture=()=>{};
  const make=(type:string,x:number,y:number)=>{const r=view.getBoundingClientRect();return new PointerEvent(type,{pointerId:612,pointerType:'pen',button:0,buttons:type==='pointerup'?0:1,clientX:r.left+x/W*r.width,clientY:r.top+y/H*r.height});};
  try{view.dispatchEvent(make('pointerdown',20,90));const move=make('pointermove',120,90);Object.defineProperty(move,'getCoalescedEvents',{value:()=>[make('pointermove',40,20),make('pointermove',90,20),make('pointermove',120,90)]});view.dispatchEvent(move);view.dispatchEvent(make('pointerup',120,90));bakeStaticStrokes(baseCtx);assert(pixel(65,20)!=='255,255,255,255','Intermediate pen samples were lost');assert(pixel(65,90)==='255,255,255,255','The curve was replaced by a straight shortcut');}
  finally{view.setPointerCapture=savedCapture;inputStage.style.cssText=savedStyle;resetLayers(960,640);}
});
check('Trimming a transformed raster keeps the visible interior pixels and does not resample its source',()=>{
  const image=twoColourPiece(),object:RasterObject={id:'clip-pixels',name:'Clip',kind:'raster',image,width:40,height:40,opacity:.75,matrix:[1.4,.3,-.2,1.1,-18,-10]},before=document.createElement('canvas'),after=document.createElement('canvas');before.width=after.width=60;before.height=after.height=60;
  drawObject(before.getContext('2d')!,object,0);const clipped=trimRasterToPaper(object,60,60);assert(clipped);drawObject(after.getContext('2d')!,clipped,0);const a=before.getContext('2d')!.getImageData(0,0,60,60).data,b=after.getContext('2d')!.getImageData(0,0,60,60).data;
  for(let y=3;y<57;y++)for(let x=3;x<57;x++)for(let c=0;c<4;c++){const i=(y*60+x)*4+c;assert(Math.abs(a[i]-b[i])<=1,`Placement changed an interior pixel at ${x},${y}`);}
});
check('Stamp ghosts and the colour magnifier are previews and never change the picture',()=>{
  resetLayers(160,120);reset();block();paintFrame(0);const before=image(),savedStyle=inputStage.style.cssText;inputStage.style.display='block';const overlay=document.createElement('canvas');overlay.width=W;overlay.height=H;
  try{state.cursor={x:80,y:60};state.tool='stamp';state.stampId='vec:heart';state.stampFlipH=true;renderToolCursor(overlay.getContext('2d')!);assert(overlay.getContext('2d')!.getImageData(0,0,W,H).data.some((v,i)=>i%4===3&&v>0),'Stamp has no placement preview');state.tool='picker';renderToolCursor(overlay.getContext('2d')!);assert(image()===before,'A cursor preview changed source pixels');}
  finally{state.stampFlipH=false;state.stampId='🐶';state.cursor=null;inputStage.style.cssText=savedStyle;state.tool='draw';resetLayers(960,640);}
});
check('Animated raster strokes retain their live recipe but discarded overhang cannot return',()=>{
  objectTestReset();state.tool='draw';state.liveArmed=true;state.conveyor=['#ff0000','#0000ff'];beginObjectStroke();beginStrokeGeneration();segment(20,40,90,40,10,0);finishObjectStroke();const id=selectedObjects()[0].id;moveObjects(-50,0);commitObjectSelection();const clipped=activeLayer().objects!.find(o=>o.id===id)!;assert(clipped.kind==='raster'&&clipped.live?.strokes.length,'Trimming baked the animated ink');selectObjects([id]);moveObjects(50,0);
  for(const now of [0,2000]){const output=document.createElement('canvas');output.width=W;output.height=H;renderLayers(output.getContext('2d')!,now);const ctx=output.getContext('2d')!,gone=ctx.getImageData(25,40,1,1).data,kept=ctx.getImageData(70,40,1,1).data;assert(gone[0]===255&&gone[1]===255&&gone[2]===255,'Hidden animated pixels reappeared');assert(kept[1]<100,'Visible animated pixels were lost');}
  state.liveArmed=false;state.drawingMode='raster';resetLayers(960,640);
});
check('Placing after Undo records a fresh raster trim instead of reusing a previous gesture',()=>{
  objectTestReset();const image=twoColourPiece(),object:RasterObject={id:'undo-clip',name:'Clip',kind:'raster',image,width:40,height:40,opacity:1,matrix:[1,0,0,1,-10,10]};activeLayer().objects=[object];selectObjects([object.id]);moveObjects(-100,0);commitObjectSelection();undo();selectObjects([object.id]);commitObjectSelection();assert(activeLayer().objects![0].width===30,'The fresh placement did not trim');undo();assert(activeLayer().objects![0].width===40&&objectBounds(activeLayer().objects![0]).x===-10,'Undo lost the fresh placement history');state.drawingMode='raster';resetLayers(960,640);
});
await asyncCheck('Asynchronous project encoding captures a stable editable picture while drawing can continue',async()=>{
  objectTestReset();addRasterImage(twoColourPiece(),{x:10,y:10});const piece=selectedObjects()[0];assert(piece.kind==='raster');const expected=projectData(),pending=projectDataAsync();
  piece.image.getContext('2d')!.clearRect(0,0,40,40);moveObjects(30,0);baseCtx.fillStyle='#00ff00';baseCtx.fillRect(0,0,20,20);
  const saved=await pending;assert(saved===expected,'Async encoding mixed pixels from later edits into the saved frame');await loadProjectData(saved);assert(objectPixel(15,15)==='255,0,0,255','Async project did not restore the original raster');state.drawingMode='raster';resetLayers(960,640);
});
await asyncCheck('Local recovery writes picture and preview together, isolates documents and round-trips editable pieces',async()=>{
  const databaseName=`RetroPaintRecoveryChecks-${crypto.randomUUID()}`,store=new RecoveryStore(databaseName);
  try{
    objectTestReset();addVectorShape('rect',10,10,40,40);moveObjects(-30,0);const data=await projectDataAsync(),draft={id:'first',name:'First',width:160,height:120,savedAt:1,thumbnail:'data:image/png;base64,preview',bytes:data.length*2,data};
    await store.save(draft);await store.save({...draft,id:'second',name:'Second',savedAt:2});let list=await store.list();assert(list.length===2&&list[0].id==='second','Separate documents overwrote each other');assert(!('data' in list[0]),'Listing previews unnecessarily loads full pictures');
    await store.save({...draft,name:'First revised',savedAt:3});list=await store.list();const restored=await store.read('first');assert(restored?.name==='First revised'&&list[0].name===restored.name&&restored.data===data,'Preview and content were not updated together');assert(await store.read('missing')===null,'A missing draft returned another picture');
    resetLayers(10,10);await loadProjectData(restored.data);const piece=activeLayer().objects![0];assert(piece.kind==='path'&&objectBounds(piece).x===-20,'Recovery discarded off-paper vectors');
    for(let i=3;i<=11;i++)await store.save({...draft,id:`picture-${i}`,savedAt:i});assert((await store.list()).length===8,'Automatic recovery does not keep a bounded recent history');
  }finally{await store.close();await new Promise<void>((resolve,reject)=>{const request=indexedDB.deleteDatabase(databaseName);request.onsuccess=()=>resolve();request.onerror=()=>reject(request.error);});state.drawingMode='raster';resetLayers(960,640);}
});
await asyncCheck('Every redesigned sound has a soft attack, finite unclipped samples and a silent tail',async()=>{
  const names:SoundName[]=['pop','clunk','thwack','rip','splash','vwoop','squeak','rattle','shimmer','zip','snick','clack','squeegee','whir','motor-stop','undo','redo','save','place','delete','colour','pencil','swish'];
  const fingerprints=new Set<string>();
  for(const name of names){
    const ctx=new OfflineAudioContext(1,44100,44100);scheduleSound(ctx,ctx.destination,soundPatch(name),.02);const output=await ctx.startRendering(),data=output.getChannelData(0);let peak=0,energy=0;
    for(const sample of data){assert(Number.isFinite(sample),`${name} has invalid audio`);peak=Math.max(peak,Math.abs(sample));energy+=sample*sample;}
    assert(peak>.005&&peak<.85&&energy>0,`${name} is silent or clips: ${peak}`);assert(data.slice(0,882).every(value=>Math.abs(value)<.00001),`${name} starts abruptly`);assert(data.slice(42000).every(value=>Math.abs(value)<.00001),`${name} leaves a stuck sound`);
    fingerprints.add(`${peak.toFixed(5)}:${energy.toFixed(5)}`);
  }
  assert(fingerprints.size===names.length,'Sound actions all use the same feedback');
});
check('Audio settings clamp safely, persist volume and make mute effective immediately',()=>{
  const before=audioSettings(),raw=sessionStorage.getItem('retropaint-sound');
  try{setAudioSettings({volume:4,enabled:false,drawing:false});assert(audioSettings().volume===1&&!play('save'),'Mute still plays sounds');setAudioSettings({volume:-2});assert(audioSettings().volume===0);setAudioSettings({volume:Number.NaN});assert(audioSettings().volume===0,'Invalid volume leaked into audio');const stored=JSON.parse(sessionStorage.getItem('retropaint-sound')!);assert(stored.volume===0&&stored.enabled===false&&stored.drawing===false,'Sound settings were not saved');setAudioSettings({volume:.25});setAudioSettings({volume:0});toggleSounds();assert(audioSettings().enabled&&audioSettings().volume===.25,'Quick unmute cannot recover from zero volume');}
  finally{setAudioSettings(before);if(raw===null)sessionStorage.removeItem('retropaint-sound');else sessionStorage.setItem('retropaint-sound',raw);}
});

function closedCadMesh(mesh:CadMesh):void{
  const edges=new Map<string,number>(),point=(i:number)=>Array.from(mesh.positions.subarray(i*3,i*3+3)).map(v=>Math.round(v*1e5)).join(',');
  for(let i=0;i<mesh.indices.length;i+=3){const p=[0,1,2].map(j=>point(mesh.indices[i+j]));for(let j=0;j<3;j++){const key=[p[j],p[(j+1)%3]].sort().join('|');edges.set(key,(edges.get(key)??0)+1);}}
  assert([...edges.values()].every(count=>count===2),'Mesh has an open edge or a non-manifold seam');assert(mesh.volume>0&&mesh.triangles>0,'Solid has no positive volume');
}
await asyncCheck('CAD all eight primitives are closed positive-volume solids in millimetres',async()=>{
  for(const shape of ['box','sphere','cylinder','cone','torus','tube','pyramid','wedge'] as Primitive[]){const mesh=await solidMesh(primitive(shape));closedCadMesh(mesh);assert(mesh.bounds.min[2]>-0.001,shape+' starts below the bed');assert(mesh.bounds.max[0]-mesh.bounds.min[0]>10,shape+' has wrong units');if(shape==='box')assert(Math.abs(mesh.volume-8000)<0.001,'20 mm cube has wrong volume');}
});
await asyncCheck('CAD resized tubes keep the same cavity in display and precision feature history',async()=>{
  for(const scale of [[2,1,1],[-2,1,1],[1,2,.5]] as [number,number,number][]){
    const tube=primitive('tube');tube.scale=scale;
    // A suppressed finish must return its source, including the original hole.
    const source=await solidMesh(tube),precision=await solidMesh(cadBody({kind:'finish',mode:'chamfer',size:.2,edges:[],source:tube,feature:{suppressed:true}},'Suppressed finish'));
    const expected=Math.PI*(100-64)*20*Math.abs(scale[0]*scale[1]*scale[2]);
    closedCadMesh(source);closedCadMesh(precision);
    assert(Math.abs(source.volume-expected)<expected*.002,'Display tube has an incorrect cavity');
    assert(Math.abs(precision.volume-expected)<expected*.002,'Precision reconstruction changed the tube cavity: '+precision.volume+' versus '+expected);
  }
});
await asyncCheck('CAD boolean cuts remove real volume, joins eliminate internal overlap and empty intersections fail safely',async()=>{
  const a=primitive('box'),b=primitive('box');b.position[0]=10;
  const joined=await solidMesh(combinedBody('union',[a,b])),cut=await solidMesh(combinedBody('subtract',[a,b])),overlap=await solidMesh(combinedBody('intersect',[a,b]));
  closedCadMesh(joined);closedCadMesh(cut);closedCadMesh(overlap);assert(Math.abs(joined.volume-12000)<.01&&Math.abs(cut.volume-4000)<.01&&Math.abs(overlap.volume-4000)<.01,'Boolean volumes are incorrect');
  b.position[0]=100;let failed=false;try{await solidMesh(combinedBody('intersect',[a,b]));}catch{failed=true;}assert(failed,'An empty intersection became a broken printable shape');
});
await asyncCheck('CAD face sketches extrude outward, cut inward and remain closed on rotated workplanes',async()=>{
  const plane=basePlane('yz');plane.origin=[10,0,10];const sketch=cadBody({kind:'extrude',points:sketchPoints('rectangle',-4,-4,8,8),plane,height:5,taper:1,twist:0},'Face boss');
  const boss=await solidMesh(sketch);closedCadMesh(boss);assert(Math.abs(boss.volume-320)<.01&&Math.abs(boss.bounds.min[0]-10)<.001&&Math.abs(boss.bounds.max[0]-15)<.001,'Face extrusion uses the wrong axis');
  sketch.solid={...sketch.solid,kind:'extrude',points:sketchPoints('circle',0,0,8,8),plane,height:-25,taper:1,twist:0};const result=await solidMesh(combinedBody('subtract',[primitive('box'),sketch]));closedCadMesh(result);assert(result.volume<7100&&result.volume>6900,'Circle cut did not pass through the cube');
});
await asyncCheck('CAD revolve preserves hollow profiles, partial turns and exact height',async()=>{
  const solid=cadBody({kind:'revolve',points:[[8,0],[10,0],[10,20],[8,20]],degrees:360,plane:basePlane('xy')},'Hollow revolved tube');
  const full=await solidMesh(solid);closedCadMesh(full);assert(Math.abs(full.bounds.max[2]-20)<.001&&Math.abs(full.volume-Math.PI*36*20)<4,'Revolve lost the hollow centre or mm height');
  solid.solid={...solid.solid,kind:'revolve',points:[[8,0],[10,0],[10,20],[8,20]],degrees:180,plane:basePlane('xy')};const half=await solidMesh(solid);closedCadMesh(half);assert(Math.abs(half.volume/full.volume-.5)<.002,'Partial revolve is not half the full solid');
});
await asyncCheck('CAD sketches drawn in either direction and clockwise revolve profiles produce the same solid',async()=>{
  for(const points of [sketchPoints('rectangle',10,10,-20,10),sketchPoints('rectangle',10,10,20,-10)]){const mesh=await solidMesh(cadBody({kind:'extrude',points,plane:basePlane('xy'),height:10,taper:1,twist:0},'Reverse-drawn rectangle'));closedCadMesh(mesh);assert(Math.abs(mesh.volume-2000)<.01,'A reverse-drawn sketch disappeared');}
  const mesh=await solidMesh(cadBody({kind:'revolve',points:[[0,0],[0,20],[10,20],[10,0]],degrees:360,plane:basePlane('xy')},'Clockwise profile'));closedCadMesh(mesh);assert(Math.abs(mesh.volume-Math.PI*2000)<3,'Clockwise revolve profile was discarded');
});
await asyncCheck('CAD twisted tapered sketches and mirrored solids export with outward normals',async()=>{
  const twisted=cadBody({kind:'extrude',points:sketchPoints('rectangle',-5,-5,10,10),plane:basePlane('xy'),height:30,taper:.5,twist:90},'Twisted tower');twisted.scale=[-1,1,1];
  const mesh=await printMesh([twisted]);closedCadMesh(mesh);const stl=binaryStl(mesh),data=new DataView(stl);assert(stl.byteLength===84+mesh.triangles*50&&data.getUint32(80,true)===mesh.triangles,'STL facet count or byte size is invalid');
  let signed=0;for(let i=0;i<mesh.triangles;i++){const start=84+i*50+12,p=Array.from({length:9},(_,j)=>data.getFloat32(start+j*4,true));signed+=(p[0]*(p[4]*p[8]-p[5]*p[7])-p[1]*(p[3]*p[8]-p[5]*p[6])+p[2]*(p[3]*p[7]-p[4]*p[6]))/6;}assert(Math.abs(signed-mesh.volume)<.1,'STL winding or coordinates are incorrect');
});
await asyncCheck('CAD print export unions overlapping bodies and places the assembly on the bed without changing originals',async()=>{
  const a=primitive('box'),b=primitive('box');a.position=[0,0,45];b.position=[10,0,45];const before=JSON.stringify([a,b]),mesh=await printMesh([a,b]);closedCadMesh(mesh);assert(Math.abs(mesh.volume-12000)<.01&&Math.abs(mesh.bounds.min[2])<.001,'Print export left internal overlapping shells or floated above the bed');assert(JSON.stringify([a,b])===before,'STL export changed editable pieces');
});
await asyncCheck('CAD geometry worker builds solids and transfers printable binary STL',async()=>{
  const mesh=await cadCompute([primitive('sphere')]);closedCadMesh(mesh.mesh);const result=await cadCompute([primitive('box')],'print');assert(result.stl?.byteLength===684&&result.mesh.volume===8000,'Worker STL export failed');
});
check('CAD face mating opposes normals and preserves physical dimensions',()=>{
  const cube=primitive('box');const moving=basePlane('xy'),target=basePlane('xy');moving.origin=[0,0,20];target.origin=[35,0,20];const result=mateBody(cube,moving,target);assert(result.scale.join(',')==='1,1,1','Mating changed dimensions');assert(Math.abs(result.position[0]-35)<1e-6&&Math.abs(result.position[2]-30)<1e-6,'Mating did not place the face on the target');
});
await asyncCheck('CAD 3D layers share by default, retain recipes through Undo and project round-trip, and duplicate with unique IDs',async()=>{
  resetLayers(160,120);const paintId=activeLayer().id,layer=ensureCadLayer();addCadBody(primitive('box'));assert(ensureCadLayer()===layer&&layers.length===2,'Adding solids keeps making new 3D layers');const original=currentBodies()[0];replaceBodies([{...original,position:[-25,3,40]}]);undo();assert(currentBodies()[0].position[0]===0,'Undo lost CAD state');redo();
  duplicateLayer();assert(currentBodies()[0].id!==original.id,'Duplicating a 3D layer reused scene object IDs');const source=projectData();resetLayers(10,10);await loadProjectData(source);assert(layers.length===3&&layers.find(l=>l.id===paintId)&&currentBodies()[0].position[0]===-25,'Project lost painting or editable CAD');const mesh=await solidMesh(currentBodies()[0]);assert(Math.abs(mesh.volume-8000)<.01,'Reopened CAD no longer builds');resetLayers(960,640);
});
await asyncCheck('CAD invalid saved solid geometry leaves the currently open artwork intact',async()=>{
  resetLayers(160,120);const layer=ensureCadLayer();addCadBody(primitive('box'));const valid=projectData(),data=JSON.parse(valid),first=primitive('box'),other=primitive('box');other.position[0]=100;data.layers.find((l:{id:number})=>l.id===layer.id).cad.bodies=[combinedBody('intersect',[first,other])];let failed=false;try{await loadProjectData(JSON.stringify(data));}catch{failed=true;}assert(failed&&projectData()===valid,'Opening an invalid CAD solid replaced the document');resetLayers(960,640);
});
check('CAD sketch drafts cannot mutate a previously created solid through shared profile points',()=>{
  const points:[number,number][]=[[0,0],[10,0],[10,20],[0,20]],plane=basePlane('xy'),solid=cadBody({kind:'revolve',points,plane,degrees:360},'Saved revolution');points[1][0]=25;plane.origin[2]=100;assert(solid.solid.kind==='revolve'&&solid.solid.points[1][0]===10&&solid.solid.plane.origin[2]===0,'Editing a new sketch changed an existing solid');
});
check('CAD project validation rejects invalid workplanes, singular transforms and excessive recipes',()=>{
  const valid={units:'mm',bodies:[primitive('box')]};assert(readCadLayer(valid)?.bodies.length===1);for(const invalid of [{...valid,bodies:[{...valid.bodies[0],scale:[0,1,1]}]},{...valid,bodies:[{...valid.bodies[0],solid:{kind:'extrude',points:[[0,0],[10,0],[0,10]],plane:{...basePlane('xy'),normal:[0,0,0]},height:10,taper:1,twist:0}}]},{units:'in',bodies:[]}]){let failed=false;try{readCadLayer(invalid);}catch{failed=true;}assert(failed,'Invalid CAD data was accepted');}
});

async function parametricFixture(){
  const base=cadBody({kind:'extrude',points:sketchPoints('rectangle',-20,-15,40,30),plane:basePlane('xy'),height:20,taper:1,twist:0,feature:{label:'Base pad',sketch:'rectangle'}},'Base');
  const hole=async(support:typeof base,x:number,diameter:number)=>{const plane=basePlane('xy');plane.origin=[x,0,20];const local=await solidMesh({...support,position:[0,0,0],rotation:[0,0,0],scale:[1,1,1]});const tool=cadBody({kind:'extrude',points:sketchPoints('circle',0,0,diameter,diameter),plane,height:-5,taper:1,twist:0,feature:{label:'Hole '+diameter,sketch:'circle',through:true,attachment:captureAttachment(support,local.bounds,plane)}},'Hole tool');return combinedBody('subtract',[support,tool]);};
  return hole(await hole(base,-10,8),10,6);
}
await asyncCheck('CAD feature history edits an original pad and regenerates two dependent through holes',async()=>{
  const original=await parametricFixture(),before=JSON.stringify(original),next=editFeature(original,[0,0],item=>{assert(item.solid.kind==='extrude');item.solid.height=40;});const mesh=await solidMesh(next);closedCadMesh(mesh);assert(Math.abs(mesh.bounds.max[2]-40)<.01,'Original extrusion depth was not rebuilt');assert(Math.abs(mesh.volume-(1200-Math.PI*25)*40)<5,'Later holes did not follow the taller pad or cut through it');assert(JSON.stringify(original)===before&&next.id===original.id,'Editing mutated the original or replaced the selected solid ID');assert(featureAt(next,[0,1]).solid.feature?.through,'The earlier hole recipe was lost');
});
await asyncCheck('CAD original sketch width and hole diameters remain editable beneath later cuts',async()=>{
  const root=await parametricFixture(),next=editFeature(editFeature(root,[0,0],item=>resizeSketch(item.solid,-25,-15,50,30)),[0,1],item=>resizeSketch(item.solid,0,0,12,12));const mesh=await solidMesh(next);assert(Math.abs(mesh.bounds.max[0]-mesh.bounds.min[0]-50)<.01,'Base sketch dimensions were baked in');assert(Math.abs(mesh.volume-(1500-Math.PI*45)*20)<5,'Editing a hole sketch discarded a later feature');
});
await asyncCheck('CAD suppression bypasses a cut and restores it without deleting its sketch or later features',async()=>{
  const root=await parametricFixture(),off=editFeature(root,[0],item=>{item.solid.feature={suppressed:true};}),on=editFeature(off,[0],item=>{item.solid.feature!.suppressed=false;});const disabled=await solidMesh(off),enabled=await solidMesh(on),original=await solidMesh(root);assert(Math.abs(disabled.volume-(1200-Math.PI*9)*20)<3,'Suppressing the earlier cut also lost the later hole');assert(Math.abs(enabled.volume-original.volume)<.001&&featureTree(off).length===featureTree(root).length,'Enabling did not restore the original feature inputs');
});
await asyncCheck('CAD timeline rollback preserves the project and final printable geometry',async()=>{
  resetLayers(160,120);ensureCadLayer();const root=await parametricFixture();addCadBody(root);const saved=projectData(),entries=featureTimeline(root),first=historyStage(root,0),mesh=await solidMesh(first);assert(mesh.volume===24000&&first.id===root.id,'The first timeline step is not the original pad');state.cad.preview=first;assert(projectData()===saved,'A history preview entered the saved project');const printed=await cadCompute([root],'print');assert(printed.mesh.volume<23000,'STL used the rollback preview instead of final features');state.cad.preview=null;assert(entries.length===5&&featureTree(root).filter(e=>e.sketch).length===3,'Tree or timeline omitted construction features');resetLayers(960,640);
});
await asyncCheck('CAD revolve profiles, angles and axis remain parametric after a later union',async()=>{
  const spun=cadBody({kind:'revolve',points:[[5,0],[10,0],[10,20],[5,20]],degrees:360,plane:basePlane('xy')},'Ring');const cap=primitive('box',[4,4,4]);cap.position=[8,0,2];const root=combinedBody('union',[spun,cap]),edited=editFeature(root,[0],item=>{assert(item.solid.kind==='revolve');item.solid.degrees=180;item.solid.points=[[4,0],[12,0],[12,25],[4,25]];});const mesh=await solidMesh(edited);closedCadMesh(mesh);assert(mesh.bounds.max[2]===25&&featureAt(edited,[0]).solid.kind==='revolve','Revolve history was discarded');assert(mesh.volume>4900&&mesh.volume<5100,'Changed revolve angle/profile was not rebuilt');
});
await asyncCheck('CAD older face recipes acquire stable references before original dimensions change',async()=>{
  const cube=primitive('box'),plane=basePlane('xy');plane.origin=[0,0,20.02];const tool=cadBody({kind:'extrude',points:sketchPoints('circle',0,0,8,8),plane,height:-25.04,taper:1,twist:0},'Old hole');const legacy=combinedBody('subtract',[cube,tool]),prepared=await prepareFeatureHistory(legacy),next=editFeature(prepared,[0],item=>{assert(item.solid.kind==='primitive');item.solid.size[2]=40;});const mesh=await solidMesh(next);assert(featureAt(prepared,[1]).solid.feature?.attachment,'Earlier face sketches were not upgraded');assert(Math.abs(mesh.volume-(16000-Math.PI*16*25))<4,'The older hole did not follow its resized support');assert(!featureAt(legacy,[1]).solid.feature,'Upgrading mutated the saved source recipe');
});
await asyncCheck('CAD parametric history, dependencies and suppression survive project save and reopen',async()=>{
  resetLayers(160,120);ensureCadLayer();const root=await parametricFixture();root.solid.feature={label:'Two drilled holes'};addCadBody(root);const saved=projectData();assert(JSON.parse(saved).version===10);resetLayers(10,10);await loadProjectData(saved);assert(currentBodies()[0].solid.feature?.label==='Two drilled holes'&&featureAt(currentBodies()[0],[0,1]).solid.feature?.attachment,'Project discarded feature metadata');const mesh=await solidMesh(currentBodies()[0]);assert(Math.abs(mesh.volume-(1200-Math.PI*25)*20)<3);const old=JSON.parse(saved);old.version=4;await loadProjectData(JSON.stringify(old));assert(featureTimeline(currentBodies()[0]).length===5,'Version 4 projects no longer open');resetLayers(960,640);
});
await asyncCheck('CAD a lost supporting face fails safely and leaves its original recipe intact',async()=>{
  const root=await parametricFixture(),before=JSON.stringify(root),bad=editFeature(root,[0,0],item=>{assert(item.solid.kind==='extrude');item.solid.points=[[-20,-15],[20,-15],[-20,15]];});let failed=false;try{await solidMesh(bad);}catch(error){failed=String(error).includes('supporting flat face');}assert(failed&&JSON.stringify(root)===before,'Lost face silently moved the hole or changed the original');
});
await asyncCheck('CAD face dependencies preserve millimetre hole diameters on rotated and scaled supports',async()=>{
  const support=primitive('box');support.rotation=[20,35,10];support.scale=[1.2,.8,1.3];support.position=[25,-15,30];const bounds={min:[-10,-10,-10] as [number,number,number],max:[10,10,10] as [number,number,number]},plane=attachedPlane(support,bounds,{reference:support.id,anchor:[.5,.5,1],normal:[0,0,1],u:[1,0,0]});const tool=cadBody({kind:'extrude',points:sketchPoints('circle',0,0,6,6),plane,height:-5,taper:1,twist:0,feature:{attachment:captureAttachment(support,bounds,plane),through:true,sketch:'circle'}},'Angled hole');const root=combinedBody('subtract',[support,tool]),next=editFeature(root,[0],item=>{assert(item.solid.kind==='primitive');item.solid.size[2]=30;});const mesh=await solidMesh(next);closedCadMesh(mesh);assert(Math.abs(mesh.volume-(12000*1.2*.8*1.3-Math.PI*9*39))<4,'Attached hole changed diameter or failed to follow an angled support');
});
await asyncCheck('CAD long feature chains rebuild with every later through hole intact',async()=>{
  let root=cadBody({kind:'extrude',points:sketchPoints('rectangle',-60,-15,120,30),plane:basePlane('xy'),height:10,taper:1,twist:0},'Long plate');
  for(let i=0;i<10;i++){const plane=basePlane('xy');plane.origin=[-45+i*10,0,10];const {bounds}=await solidMesh(root);const tool=cadBody({kind:'extrude',points:sketchPoints('circle',0,0,4,4),plane,height:-5,taper:1,twist:0,feature:{attachment:captureAttachment(root,bounds,plane),through:true}},'Hole '+i);root=combinedBody('subtract',[root,tool]);}
  const next=editFeature(root,Array(10).fill(0),item=>{assert(item.solid.kind==='extrude');item.solid.height=15;});const mesh=await solidMesh(next);assert(Math.abs(mesh.volume-(3600-Math.PI*40)*15)<4&&featureTimeline(next).length===21,'A later feature was lost in a long rebuild');
});

await asyncCheck('CAD native edge selection exposes twelve cube edges without triangulation seams',async()=>{
  const edges=await solidEdges(primitive('box'));assert(edges.length===12,'Expected 12 cube edges, got '+edges.length);assert(edges.every(e=>Math.abs(e.length-20)<.001&&e.points.length===2),'Cube edges are not straight 20 mm edges');
});
await asyncCheck('CAD native edge tools recognize curved rims and exclude sphere seams',async()=>{
  for(const[shape,count]of [['cylinder',2],['tube',4],['pyramid',8],['wedge',9],['cone',1],['sphere',0],['torus',0]] as const){const edges=await solidEdges(primitive(shape));assert(edges.length===count,shape+' exposed '+edges.length+' edges instead of '+count);}
});
await asyncCheck('CAD selected-edge fillets and chamfers have real printable geometry and exact editable sizes',async()=>{
  const cube=primitive('box'),edges=await solidEdges({...cube,position:[0,0,0]}),before=JSON.stringify(cube);assert(edges.length);const rounded=finishedBody(cube,'fillet',2,[edges[0].ref]),beveled=finishedBody(cube,'chamfer',2,[edges[0].ref]),round=await solidMesh(rounded),bevel=await solidMesh(beveled);closedCadMesh(round);closedCadMesh(bevel);assert(Math.abs(round.volume-(8000-20*(4-Math.PI)))<.12,'Fillet volume is not a 2 mm circular radius: '+round.volume);assert(Math.abs(bevel.volume-7960)<.02,'Chamfer is not a 2 mm equal-distance bevel: '+bevel.volume);assert(JSON.stringify(cube)===before,'Edge finishing altered its source');const larger=editFeature(rounded,[],item=>{assert(item.solid.kind==='finish');item.solid.size=3;});assert((await solidMesh(larger)).volume<round.volume,'Editing the fillet radius did not rebuild');
});
await asyncCheck('CAD all-edge fillets form corner blends and remain editable after changing the original cube',async()=>{
  const cube=primitive('box'),edges=await solidEdges({...cube,position:[0,0,0]}),rounded=finishedBody(cube,'fillet',2,edges.map(e=>e.ref)),mesh=await solidMesh(rounded);closedCadMesh(mesh);assert(Math.abs(mesh.volume-(16**3+6*16**2*2+12*16*Math.PI+4*Math.PI*8/3))<1,'The corner blends have the wrong volume: '+mesh.volume);const edited=editFeature(rounded,[0],item=>{assert(item.solid.kind==='primitive');item.solid.size[0]=30;});const rebuilt=await solidMesh(edited);assert(Math.abs(rebuilt.bounds.max[0]-rebuilt.bounds.min[0]-30)<.01&&featureTimeline(edited).length===2,'Original cube dimensions did not regenerate the fillet');const off=editFeature(rounded,[],item=>{item.solid.feature={suppressed:true};});assert(Math.abs((await solidMesh(off)).volume-8000)<.01,'Suppressing the fillet lost its original input');
});
await asyncCheck('CAD circular rim fillets and hole chamfers stay closed and printable',async()=>{
  const cylinder=primitive('cylinder'),rims=await solidEdges({...cylinder,position:[0,0,0]}),round=await solidMesh(finishedBody(cylinder,'fillet',1,rims.map(e=>e.ref)));closedCadMesh(round);assert(round.volume<Math.PI*2000&&round.volume>6200,'Cylinder rim fillets did not remove the corners');const plate=primitive('box',[30,30,10]),cutter=primitive('cylinder',[8,8,20]);cutter.position[2]=5;const drilled=combinedBody('subtract',[plate,cutter]),edges=await solidEdges(drilled),hole=edges.filter(e=>e.ref.closed&&e.ref.center[2]>.99);assert(hole.length===1,'The hole rim is not one selectable edge');const beveled=await solidMesh(finishedBody(drilled,'chamfer',1,hole.map(e=>e.ref)));closedCadMesh(beveled);assert(beveled.volume<9000-Math.PI*160,'The hole entrance did not widen when beveled');
});
await asyncCheck('CAD oversized finishes fail without changing the source and save projects retain editable edges',async()=>{
  resetLayers(160,120);ensureCadLayer();const cube=primitive('box'),edges=await solidEdges({...cube,position:[0,0,0]}),rounded=finishedBody(cube,'chamfer',2,[edges[0].ref]);addCadBody(rounded);const before=projectData();let failed=false;try{await solidMesh(finishedBody(cube,'fillet',40,edges.map(e=>e.ref)));}catch{failed=true;}assert(failed&&projectData()===before,'An invalid finish changed the project');resetLayers(10,10);await loadProjectData(before);const saved=currentBodies()[0];assert(saved.solid.kind==='finish'&&saved.solid.size===2&&saved.solid.edges.length===1&&saved.solid.source.solid.kind==='primitive','Project lost the original solid or edge references');const mesh=await solidMesh(saved),printed=await cadCompute([saved],'print');assert(Math.abs(mesh.volume-7960)<.02&&printed.stl!.byteLength>84,'Saved chamfer no longer prints correctly');resetLayers(960,640);
});
await asyncCheck('CAD concentric inner and outer rims keep separate editable edge references',async()=>{
  const tube=primitive('tube'),edges=await solidEdges({...tube,position:[0,0,0]}),inner=edges.filter(e=>e.ref.center[2]>.99&&e.ref.rank===0);assert(inner.length===1&&inner[0].ref.groupSize===2,'Concentric rims cannot be distinguished: '+JSON.stringify(edges.map(e=>e.ref)));const finished=finishedBody(tube,'fillet',.5,inner.map(e=>e.ref)),mesh=await solidMesh(finished);closedCadMesh(mesh);const changed=editFeature(finished,[0],item=>{assert(item.solid.kind==='primitive');item.solid.wall=3;});const rebuilt=await solidMesh(changed);closedCadMesh(rebuilt);assert(rebuilt.volume>mesh.volume+800,'Changing tube wall thickness lost the selected inner rim');
});
await asyncCheck('CAD face sketches, through holes and earlier extrusion depths rebuild beneath a fillet',async()=>{
  const plate=await parametricFixture(),edges=await solidEdges(plate),front=edges.filter(e=>!e.ref.closed&&e.ref.center[2]>.99&&e.ref.center[1]<.01);assert(front.length===1,'The plate edge was not found');const rounded=finishedBody(plate,'fillet',1,front.map(e=>e.ref)),edited=editFeature(rounded,[0,0,0],item=>{assert(item.solid.kind==='extrude');item.solid.height=30;});const mesh=await solidMesh(edited);closedCadMesh(mesh);assert(Math.abs(mesh.bounds.max[2]-30)<.01&&Math.abs(mesh.volume-((1200-Math.PI*25)*30-40*(1-Math.PI/4)))<1,'The earlier extrusion or dependent holes did not regenerate beneath the fillet: '+mesh.volume);
});
await asyncCheck('CAD later cuts and chamfers rebuild on a previously filleted solid',async()=>{
  const cube=primitive('box'),edges=await solidEdges({...cube,position:[0,0,0]}),rounded=finishedBody(cube,'fillet',2,edges.map(e=>e.ref)),cutter=primitive('cylinder',[6,6,40]);cutter.position[2]=10;const drilled=combinedBody('subtract',[rounded,cutter]),rims=(await solidEdges(drilled)).filter(e=>e.ref.closed);assert(rims.length===2,'Tangent fillet boundaries were incorrectly exposed as new sharp edges');const beveled=finishedBody(drilled,'chamfer',.5,rims.map(e=>e.ref)),mesh=await solidMesh(beveled);closedCadMesh(mesh);const edited=editFeature(beveled,[0,0,0],item=>{assert(item.solid.kind==='primitive');item.solid.size[0]=30;});const rebuilt=await solidMesh(edited);closedCadMesh(rebuilt);assert(rebuilt.volume>mesh.volume+3500&&featureTimeline(edited).length===5,'The complete fillet → cut → chamfer history did not rebuild');
});

await asyncCheck('CAD shell face selection exposes complete planar and curved surfaces',async()=>{
  const cube=await solidFaces(primitive('box'));assert(cube.length===6&&cube.every(f=>f.ref.surface==='PLANE'&&f.indices.length===6),'Cube faces were split or lost');
  const cylinder=await solidFaces(primitive('cylinder'));assert(cylinder.length===3&&cylinder.filter(f=>f.ref.surface==='PLANE').length===2,'Cylinder did not expose two caps and one curved face');
  const worker=await cadCompute([primitive('box')],'faces');assert(worker.faces.length===6,'Worker did not transfer face choices');
});
await asyncCheck('CAD shell creates exact inward walls and selectable openings with unchanged outside dimensions',async()=>{
  const cube=primitive('box'),local={...cube,position:[0,0,0] as [number,number,number]},faces=await solidFaces(local),top=faces.find(f=>f.ref.normal[2]>.99)!,before=JSON.stringify(cube),shell=shelledBody(cube,2,[top.ref]),mesh=await solidMesh(shell);closedCadMesh(mesh);assert(Math.abs(mesh.volume-(8000-16*16*18))<.02,'Shell walls have incorrect physical volume: '+mesh.volume);assert(mesh.bounds.max[2]===20&&mesh.bounds.min[2]===0,'Shell changed the outside size');assert(JSON.stringify(cube)===before,'Shell changed its original solid');
  const tunnel=await solidMesh(shelledBody(cube,2,faces.filter(f=>Math.abs(f.ref.normal[2])>.99).map(f=>f.ref)));closedCadMesh(tunnel);assert(Math.abs(tunnel.volume-(8000-16*16*20))<.02,'Two opposite openings did not produce a through shell');
});
await asyncCheck('CAD shell thickness and original dimensions remain editable and suppression restores the source',async()=>{
  const cube=primitive('box'),top=(await solidFaces({...cube,position:[0,0,0]})).find(f=>f.ref.normal[2]>.99)!,shell=shelledBody(cube,2,[top.ref]),thicker=editFeature(shell,[],item=>{assert(item.solid.kind==='shell');item.solid.thickness=3;}),wider=editFeature(thicker,[0],item=>{assert(item.solid.kind==='primitive');item.solid.size[0]=30;});const mesh=await solidMesh(wider);closedCadMesh(mesh);assert(Math.abs(mesh.volume-(12000-24*14*17))<.02,'Upstream size or thickness was baked into shell geometry');const off=editFeature(wider,[],item=>{item.solid.feature={suppressed:true};});assert(Math.abs((await solidMesh(off)).volume-12000)<.02&&featureTimeline(wider).map(e=>e.label).join(',')==='Cube,Shell','Shell suppression or timeline lost its source');
});
await asyncCheck('CAD cylinder and enclosed shells keep real curved walls',async()=>{
  const cylinder=primitive('cylinder',[20,20,30]),top=(await solidFaces({...cylinder,position:[0,0,0]})).find(f=>f.ref.normal[2]>.99)!,mesh=await solidMesh(shelledBody(cylinder,2,[top.ref]));closedCadMesh(mesh);assert(Math.abs(mesh.volume-Math.PI*(100*30-64*28))<2,'Cylindrical shell has the wrong thickness: '+mesh.volume);
  const sealed=await solidMesh(shelledBody(primitive('box'),2,[]));closedCadMesh(sealed);assert(Math.abs(sealed.volume-(8000-16**3))<.02,'Enclosed shell does not contain a cavity: '+sealed.volume);
});
await asyncCheck('CAD shell invalid thickness and lost faces fail without modifying original recipes',async()=>{
  const cube=primitive('box'),top=(await solidFaces({...cube,position:[0,0,0]})).find(f=>f.ref.normal[2]>.99)!,original=shelledBody(cube,2,[top.ref]),before=JSON.stringify(original);let invalid=false,lost=false;try{await solidMesh(shelledBody(cube,40,[top.ref]));}catch{invalid=true;}try{const bad=structuredClone(original);assert(bad.solid.kind==='shell');bad.solid.faces[0].center[0]=.1;await solidMesh(bad);}catch(error){lost=String(error).includes('reselect');}assert(invalid&&lost&&JSON.stringify(original)===before,'Invalid shell applied a partial result or silently reassigned an opening');
});
await asyncCheck('CAD shell and later hole and edge features rebuild together',async()=>{
  const cube=primitive('box',[30,30,20]),local={...cube,position:[0,0,0] as [number,number,number]},faces=await solidFaces(local),top=faces.find(f=>f.ref.normal[2]>.99)!,shell=shelledBody(cube,2,[top.ref]),cutter=primitive('cylinder',[6,6,30]);cutter.position[2]=10;const drilled=combinedBody('subtract',[shell,cutter]),edges=await solidEdges(drilled),rim=edges.filter(e=>e.ref.closed&&e.ref.center[2]<.01);assert(rim.length===1,'Bottom hole rim not found');const chamfered=finishedBody(drilled,'chamfer',.5,rim.map(e=>e.ref)),thicker=editFeature(chamfered,[0,0],item=>{assert(item.solid.kind==='shell');item.solid.thickness=3;});const a=await solidMesh(chamfered),b=await solidMesh(thicker);closedCadMesh(a);closedCadMesh(b);assert(b.volume>a.volume+1900&&featureTimeline(thicker).length===5,'Later hole or chamfer was lost after changing the wall');
});
await asyncCheck('CAD shell preserves mm wall thickness on rotated resized sources and hollows spheres',async()=>{
  const cube=primitive('box');cube.scale=[1.5,1,.5];cube.rotation=[20,30,15];cube.position=[30,-20,40];const top=(await solidFaces({...cube,position:[0,0,0],rotation:[0,0,0]})).find(f=>f.ref.normal[2]>.99)!,mesh=await solidMesh(shelledBody(cube,2,[top.ref]));closedCadMesh(mesh);assert(Math.abs(mesh.volume-(6000-26*16*8))<.03,'Body scaling changed the requested wall thickness: '+mesh.volume);const sphere=await solidMesh(shelledBody(primitive('sphere'),2,[]));closedCadMesh(sphere);assert(Math.abs(sphere.volume-4/3*Math.PI*(1000-512))<3,'Sphere cavity is not a 2 mm inward offset: '+sphere.volume);
});
await asyncCheck('CAD shell saves editable faces and walls and exports closed binary STL',async()=>{
  resetLayers(160,120);ensureCadLayer();const cube=primitive('box'),top=(await solidFaces({...cube,position:[0,0,0]})).find(f=>f.ref.normal[2]>.99)!;addCadBody(shelledBody(cube,2,[top.ref]));const saved=projectData();resetLayers(10,10);await loadProjectData(saved);const result=currentBodies()[0];assert(result.solid.kind==='shell'&&result.solid.thickness===2&&result.solid.faces.length===1&&result.solid.source.solid.kind==='primitive','Project lost shell inputs');const printed=await cadCompute([result],'print');closedCadMesh(printed.mesh);assert(printed.stl?.byteLength===84+printed.mesh.triangles*50&&Math.abs(printed.mesh.volume-3392)<.02,'Shell STL omitted the cavity');resetLayers(960,640);
});

await asyncCheck('CAD loft builds closed solid geometry between editable sketch profiles',async()=>{
  const form=defaultForm('loft');assert(form.kind==='loft');const source=cadBody(form,'Loft'),before=JSON.stringify(source),mesh=await solidMesh(source);closedCadMesh(mesh);assert(Math.abs(mesh.volume-Math.PI*1960)<5,'Circle loft has the wrong physical volume: '+mesh.volume);assert(Math.abs(mesh.bounds.max[2]-30)<.01&&JSON.stringify(source)===before,'Loft changed its source sketches');const changed=editFeature(source,[],item=>{assert(item.solid.kind==='loft');item.solid.profiles[1].plane.origin[2]=40;});assert(Math.abs((await solidMesh(changed)).volume-Math.PI*1960*4/3)<6,'Loft did not follow the edited profile placement');assert(featureTree(source).filter(e=>e.sketch).length===2,'Loft profiles are missing from the feature tree');
});
await asyncCheck('CAD ruled and smooth lofts support multiple profiles and mixed outlines',async()=>{
  const form=defaultForm('loft');assert(form.kind==='loft');form.profiles=[newProfile('Bottom'),newProfile('Waist',15,8),newProfile('Top',30,16)];form.ruled=true;const ruled=await solidMesh(cadBody(form,'Ruled loft'));closedCadMesh(ruled);form.ruled=false;const smooth=await solidMesh(cadBody(form,'Smooth loft'));closedCadMesh(smooth);assert(Math.abs(smooth.volume-ruled.volume)>10,'Smooth and ruled settings have no effect');form.profiles[0]={...form.profiles[0],shape:'rectangle',points:sketchPoints('rectangle',-10,-10,20,20)};const mixed=await solidMesh(cadBody(form,'Mixed loft'));closedCadMesh(mixed);
});
await asyncCheck('CAD sweep builds exact cross sections along straight and corner paths',async()=>{
  const form=defaultForm('sweep');assert(form.kind==='sweep');form.path.points=[[0,0,0],[0,0,30]];const source=cadBody(form,'Sweep'),mesh=await solidMesh(source);closedCadMesh(mesh);assert(Math.abs(mesh.volume-Math.PI*270)<.7,'Straight sweep has the wrong section or length: '+mesh.volume);form.profile.shape='rectangle';form.profile.points=sketchPoints('rectangle',-2,-2,4,4);form.path.points=[[0,0,0],[0,0,20],[20,0,20]];form.path.smooth=false;const corner=await solidMesh(cadBody(form,'Miter sweep'));closedCadMesh(corner);assert(Math.abs(corner.volume-640)<.05,'Miter sweep did not follow the path at constant section: '+corner.volume);
});
await asyncCheck('CAD smooth 3D sweeps follow editable interpolation points and print closed geometry',async()=>{
  const form=defaultForm('sweep');assert(form.kind==='sweep');form.path.points[2][1]=6;const source=cadBody(form,'Curved sweep'),before=JSON.stringify(source),mesh=await solidMesh(source);closedCadMesh(mesh);let length=0;for(const controls of pathBeziers(form.path.points)){let last=controls[0];for(let i=1;i<=100;i++){const t=i/100,p=controls[0].map((_,k)=>(1-t)**3*controls[0][k]+3*(1-t)**2*t*controls[1][k]+3*(1-t)*t*t*controls[2][k]+t**3*controls[3][k]);length+=Math.hypot(...p.map((v,k)=>v-last[k]));last=p as [number,number,number];}}assert(Math.abs(mesh.volume-Math.PI*9*length)<5,'Smooth path or cross-section changed unexpectedly: '+mesh.volume);assert(JSON.stringify(source)===before&&featureTree(source).some(e=>e.sweepPath),'Sweep did not retain an editable path');const printed=await cadCompute([source],'print');assert(printed.stl?.byteLength===84+50*printed.mesh.triangles,'Sweep STL is incomplete');
});

await asyncCheck('CAD loft profile edits regenerate later cuts and edge finishing',async()=>{
  const form=defaultForm('loft');assert(form.kind==='loft');form.ruled=true;const source=cadBody(form,'Loft'),hole=primitive('cylinder',[4,4,80]);hole.position[2]=30;const cut=combinedBody('subtract',[source,hole]),rims=(await solidEdges(cut)).filter(e=>e.ref.closed&&e.ref.center[2]>.99&&e.length<15),finished=finishedBody(cut,'chamfer',.5,rims.map(e=>e.ref));assert(rims.length===1,'Hole edge missing on a loft');const next=editFeature(finished,[0,0],item=>{assert(item.solid.kind==='loft');item.solid.profiles[1].plane.origin[2]=40;});const a=await solidMesh(finished),b=await solidMesh(next);closedCadMesh(b);assert(b.volume>a.volume+1900&&featureTree(next).some(e=>e.profile===1),'A profile edit lost later cut or finish history');
});
await asyncCheck('CAD changing sweep profiles and path settings retains later solid operations',async()=>{
  const form=defaultForm('sweep');assert(form.kind==='sweep');form.path.points=[[0,0,0],[0,0,30]];const source=cadBody(form,'Sweep'),block=primitive('box',[10,10,5]);block.position[2]=2.5;const joined=combinedBody('union',[source,block]),changed=editFeature(joined,[0],item=>{assert(item.solid.kind==='sweep');item.solid.profile.points=sketchPoints('circle',0,0,8,8);item.solid.path.points[1][2]=40;item.solid.roll=30;});const mesh=await solidMesh(changed);closedCadMesh(mesh);assert(mesh.bounds.max[2]===40&&mesh.volume>2200&&featureTree(changed).some(e=>e.sweepPath),'Sweep path or profile edits lost a later solid operation');
});
await asyncCheck('CAD invalid lofts and sweep paths fail safely without replacing saved artwork',async()=>{
  resetLayers(160,120);ensureCadLayer();addCadBody(primitive('box'));const saved=projectData(),loft=defaultForm('loft'),sweep=defaultForm('sweep');assert(loft.kind==='loft'&&sweep.kind==='sweep');loft.profiles[1].plane.origin[2]=0;sweep.path.points=[[0,0,0],[0,0,0]];
  for(const form of [loft,sweep]){let failed=false;try{await cadCompute([cadBody(form,'Invalid')]);}catch{failed=true;}assert(failed&&projectData()===saved,'Invalid construction changed the document');}
  const malformed=JSON.parse(saved);malformed.layers.find((l:{cad?:unknown})=>l.cad).cad.bodies=[cadBody(sweep,'Invalid')];let failed=false;try{await loadProjectData(JSON.stringify(malformed));}catch{failed=true;}assert(failed&&projectData()===saved,'Invalid saved sweep replaced the document');resetLayers(960,640);
});
await asyncCheck('CAD loft and sweep projects retain profiles, paths and settings and reopen as printable solids',async()=>{
  resetLayers(160,120);ensureCadLayer();const loft=defaultForm('loft'),sweep=defaultForm('sweep');assert(loft.kind==='loft'&&sweep.kind==='sweep');loft.ruled=true;loft.profiles[0].name='Editable lower sketch';sweep.roll=25;sweep.path.name='Editable curved path';const a=cadBody(loft,'Loft'),b=cadBody(sweep,'Sweep');b.position[0]=50;replaceBodies([a,b]);const saved=projectData();assert(JSON.parse(saved).version===10);resetLayers(10,10);await loadProjectData(saved);const [first,second]=currentBodies();assert(first.solid.kind==='loft'&&first.solid.ruled&&first.solid.profiles[0].name==='Editable lower sketch','Loft profile or setting was baked');assert(second.solid.kind==='sweep'&&second.solid.roll===25&&second.solid.path.name==='Editable curved path','Sweep path or setting was baked');const result=await cadCompute(currentBodies(),'print');closedCadMesh(result.mesh);assert(result.stl!.byteLength>84);const old=JSON.parse(saved);old.version=7;await loadProjectData(JSON.stringify(old));assert(currentBodies().length===2,'Older projects stopped opening');resetLayers(960,640);
});

await asyncCheck('CAD loft profile turns and plane offsets change the solid without baking sketches',async()=>{
  const form=defaultForm('loft');assert(form.kind==='loft');form.ruled=true;for(const profile of form.profiles){profile.shape='rectangle';profile.points=sketchPoints('rectangle',-8,-5,16,10);}const original=await solidMesh(cadBody(form,'Straight loft'));form.profiles[1].rotation=35;form.profiles[1].plane.origin[0]=8;const angled=await solidMesh(cadBody(form,'Turned loft'));closedCadMesh(angled);assert(angled.bounds.max[0]>original.bounds.max[0]+5&&Math.abs(angled.volume-original.volume)>50,'Profile turn or placement did not affect the loft');
});
await asyncCheck('CAD sweep rounded corner transitions generate closed solids',async()=>{
  const form=defaultForm('sweep');assert(form.kind==='sweep');form.path.smooth=false;form.path.points=[[0,0,0],[0,0,20],[20,0,20]];form.transition='round';const round=(await cadCompute([cadBody(form,'Round corner sweep')])).mesh;closedCadMesh(round);assert(round.volume>1000&&round.volume<1200,'Rounded corner sweep has unexpected volume: '+round.volume);
});

await asyncCheck('CAD binary STL imports keep real solid volume and support later editable cuts',async()=>{
  const original=await solidMesh(primitive('box')),source=importStl(binaryStl(original),'Cube.stl'),before=JSON.stringify(source),mesh=await solidMesh(source);closedCadMesh(mesh);assert(Math.abs(mesh.volume-8000)<.01&&source.solid.kind==='mesh'&&source.solid.sourceName==='Cube.stl','STL import lost its volume or source');const cutter=primitive('cylinder',[6,6,30]),cut=combinedBody('subtract',[source,cutter]),result=await solidMesh(cut);closedCadMesh(result);assert(result.volume<7500&&result.volume>7400&&JSON.stringify(source)===before,'STL cuts changed the original source or ignored the cutter');
});
await asyncCheck('CAD ASCII STL imports repair winding and honour mm cm and inch units',async()=>{
  const mesh=await solidMesh(primitive('box',[2,2,2])),ascii='solid test\n'+Array.from({length:mesh.indices.length/3},(_,face)=>'facet normal 0 0 0\nouter loop\n'+[0,1,2].map(k=>{const index=mesh.indices[face*3+(face%2?2-k:k)];return'vertex '+Array.from(mesh.positions.slice(index*3,index*3+3)).join(' ');}).join('\n')+'\nendloop\nendfacet').join('\n')+'\nendsolid test',bytes=new TextEncoder().encode(ascii).buffer;
  for(const [unit,size]of [['mm',2],['cm',20],['in',50.8]] as const){const result=await solidMesh(importStl(bytes,'Ascii.stl',unit));closedCadMesh(result);assert(Math.abs(result.bounds.max[0]-result.bounds.min[0]-size)<.001&&Math.abs(result.volume-size**3)<.1,'STL units or inconsistent face winding were not handled');}
});
await asyncCheck('CAD STL imports preserve enclosed cavities and reject broken open surfaces',async()=>{
  const cube=primitive('box'),hollow=shelledBody(cube,2,[]),original=await solidMesh(hollow),imported=await solidMesh(importStl(binaryStl(original),'Hollow.stl'));closedCadMesh(imported);assert(Math.abs(imported.volume-original.volume)<.02,'STL import filled the enclosed cavity');const bytes=binaryStl(await solidMesh(cube)),incomplete=bytes.slice(0,bytes.byteLength-50);new DataView(incomplete).setUint32(80,11,true);let failed=false;try{importStl(incomplete,'Broken.stl');}catch{failed=true;}assert(failed,'An open STL became a printable solid');
});
await asyncCheck('CAD STL winding repair preserves nested cavities islands and disconnected solids in binary and ASCII files',async()=>{
  const hollow=shelledBody(primitive('box'),2,[]),island=primitive('box',[4,4,4]),outside=primitive('box',[4,4,4]);island.position=[0,0,10];outside.position=[40,0,10];
  const original=await printMesh([hollow,island,outside]),bytes=binaryStl(original),count=original.triangles;
  for(const mode of ['first','alternating','all','reordered'] as const){
    const damaged=bytes.slice(0),view=new DataView(damaged);
    for(let face=0;face<count;face++)if(mode==='all'||mode==='alternating'&&face%2===0||mode==='first'&&face===0)for(let k=0;k<3;k++){const a=84+face*50+24+k*4,b=a+12,x=view.getFloat32(a,true);view.setFloat32(a,view.getFloat32(b,true),true);view.setFloat32(b,x,true);}
    if(mode==='reordered'){const copy=new Uint8Array(damaged.slice(0));for(let face=0;face<count;face++)new Uint8Array(damaged,84+face*50,50).set(copy.subarray(84+(count-1-face)*50,134+(count-1-face)*50));}
    const ascii='solid nested\n'+Array.from({length:count},(_,face)=>'facet normal 0 0 0\nouter loop\n'+[0,1,2].map(j=>'vertex '+[0,1,2].map(k=>view.getFloat32(96+face*50+j*12+k*4,true)).join(' ')).join('\n')+'\nendloop\nendfacet').join('\n')+'\nendsolid nested';
    for(const [format,input]of [['binary',damaged],['ASCII',new TextEncoder().encode(ascii).buffer]] as const){const imported=await solidMesh(importStl(input,'Nested.stl'));closedCadMesh(imported);assert(Math.abs(imported.volume-4032)<.03,`${format} ${mode} winding changed cavity or island volume: ${imported.volume}`);}
  }
});
await asyncCheck('CAD imported repaired cavity meshes and later cuts retain original data and picture view through project reopening',async()=>{
  resetLayers(160,120);const layer=ensureCadLayer(),bytes=binaryStl(await solidMesh(shelledBody(primitive('box'),2,[]))),view=new DataView(bytes);for(let k=0;k<3;k++){const x=view.getFloat32(108+k*4,true);view.setFloat32(108+k*4,view.getFloat32(120+k*4,true),true);view.setFloat32(120+k*4,x,true);}
  const imported=importStl(bytes,'Repaired cavity.stl'),original=JSON.stringify(imported.solid),cutter=primitive('box',[4,4,40]);cutter.position=[0,0,10];addCadBody(combinedBody('subtract',[imported,cutter]));layer.cad!.view={position:[100,-150,100],target:[0,0,10],up:[0,0,1],projection:'orthographic',span:80};const placement=JSON.stringify(layer.cad!.view),saved=await projectDataAsync();resetLayers(10,10);await loadProjectData(saved);
  const reopened=currentBodies()[0];assert(reopened.solid.kind==='boolean'&&JSON.stringify(reopened.solid.children[0].solid)===original,'Reopening lost the original imported mesh beneath a later cut');assert(JSON.stringify(activeLayer().cad!.view)===placement,'Reopening lost saved picture placement');const mesh=await printMesh([reopened]);closedCadMesh(mesh);assert(Math.abs(mesh.volume-3840)<.03,'Reopened imported cavity or later cut changed volume');resetLayers(960,640);
});
await asyncCheck('CAD complex joined cylinder and cube faces shell with exact walls and reopen with editable history',async()=>{
  const cylinder=primitive('cylinder'),cube=primitive('box');cylinder.position=[15,0,10];const joined=combinedBody('union',[cylinder,cube]),before=JSON.stringify(joined),faces=await solidFaces(joined),top=faces.find(f=>f.ref.normal[2]>.99)!;
  assert(top.indices.length>6,'Fixture did not expose the combined non-rectangular cap');const shell=shelledBody(joined,3,[top.ref]),mesh=await solidMesh(shell);closedCadMesh(mesh);assert(Math.abs(mesh.volume-6688.252)<3,'Complex shell did not remove the correct cavity: '+mesh.volume);assert(Math.abs(mesh.bounds.min[0]+10)<.001&&Math.abs(mesh.bounds.max[0]-25)<.001&&mesh.bounds.min[2]===0&&mesh.bounds.max[2]===20,'Shell changed exterior dimensions');assert(JSON.stringify(joined)===before,'Shell mutated its joined source');
  const wasm=await initKernel(),solid=new wasm.Manifold(new wasm.Mesh({numProp:3,vertProperties:mesh.positions,triVerts:mesh.indices}));try{const xs=solid.rayCast([-20,0,10],[35,0,10]).map(h=>h.position[0]).sort((a,b)=>a-b),floor=solid.rayCast([0,0,-10],[0,0,30]).map(h=>h.position[2]).sort((a,b)=>a-b);assert(xs.length===4&&xs.every((x,i)=>Math.abs(x-[-10,-7,22,25][i])<.01),'Side walls are not 3mm: '+xs);assert(floor.length===2&&Math.abs(floor[0])<.001&&Math.abs(floor[1]-3)<.001,'Floor is not 3mm or the opening was capped: '+floor);}finally{solid.delete();}
  const thinner=editFeature(shell,[],item=>{assert(item.solid.kind==='shell');item.solid.thickness=2;});assert((await solidMesh(thinner)).volume<mesh.volume-1000,'Wall thickness edit did not rebuild the complex shell');const off=editFeature(shell,[],item=>{item.solid.feature={suppressed:true};});assert(Math.abs((await solidMesh(off)).volume-13054.815)<4,'Suppression lost the joined source');
  for(const overlap of [40/3,15]){const round=primitive('cylinder');round.position=[overlap,0,10];const reversed=combinedBody('union',[primitive('box'),round]),caps=(await solidFaces(reversed)).filter(f=>Math.abs(f.ref.normal[2])>.99);for(const openings of [caps.filter(f=>f.ref.normal[2]<0),caps]){const result=await solidMesh(shelledBody(reversed,3,openings.map(f=>f.ref)));closedCadMesh(result);assert(result.volume>0&&result.volume<(await solidMesh(reversed)).volume-1000,'Reversed join or opposite complex openings did not hollow');}}
  resetLayers(160,120);ensureCadLayer();addCadBody(shell);const saved=await projectDataAsync();resetLayers(10,10);await loadProjectData(saved);const reopened=currentBodies()[0];assert(reopened.solid.kind==='shell'&&reopened.solid.source.solid.kind==='boolean'&&featureTimeline(reopened).length===4,'Shell lost its joined editable history');const printed=await cadCompute([reopened],'print');closedCadMesh(printed.mesh);assert(Math.abs(printed.mesh.volume-mesh.volume)<.01&&printed.stl!.byteLength===84+printed.mesh.triangles*50,'Reopened shell STL changed the cavity');resetLayers(960,640);
});
await asyncCheck('CAD adds a boss and recess beside an existing central hole in both kernels',async()=>{
  const cube=primitive('box'),plane=basePlane('xy');plane.origin=[0,0,20];
  const attach=async(support:typeof cube,points:V2[],height:number,through=false)=>{
    const local=await solidMesh({...support,position:[0,0,0],rotation:[0,0,0],scale:[1,1,1]});
    return cadBody({kind:'extrude',points,plane,height,taper:1,twist:0,feature:{attachment:captureAttachment(support,local.bounds,plane),through}},'Face feature');
  };
  const drilled=combinedBody('subtract',[cube,await attach(cube,sketchPoints('circle',0,0,6,6),-20,true)]);
  const raised=combinedBody('union',[drilled,await attach(drilled,sketchPoints('rectangle',-8,-8,4,4),4)]);
  const pocketed=combinedBody('subtract',[raised,await attach(raised,sketchPoints('rectangle',4,4,4,4),-3)]);
  const mesh=await solidMesh(pocketed),expected=8000-Math.PI*9*20+64-48;closedCadMesh(mesh);assert(Math.abs(mesh.volume-expected)<1,'Repeated face features changed volume or position');
  const precision=await solidMesh(cadBody({kind:'finish',mode:'chamfer',size:.2,edges:[],source:pocketed,feature:{suppressed:true}},'Precision history'));
  closedCadMesh(precision);assert(Math.abs(precision.volume-expected)<1,'Precision reconstruction lost a face beside the existing hole');
});
await asyncCheck('CAD attached recess depths keep their requested endpoint in both solid kernels',async()=>{
  const cube=primitive('box'),plane=basePlane('xy');plane.origin=[0,0,20];const sourceMesh=await solidMesh({...cube,position:[0,0,0]}),cut=cadBody({kind:'extrude',points:sketchPoints('rectangle',-5,-5,10,10),plane,height:-5,taper:1,twist:0,feature:{attachment:captureAttachment(cube,sourceMesh.bounds,plane)}},'Exact recess'),result=combinedBody('subtract',[cube,cut]);
  const mesh=await solidMesh(result);closedCadMesh(mesh);assert(Math.abs(mesh.volume-7500)<.01,'Mesh kernel extended the recess beyond 5mm');const native=await solidFaces(result);assert(native.some(f=>f.ref.surface==='PLANE'&&Math.abs(f.ref.center[2]-.75)<1e-5),'Precision kernel extended the recess beyond 5mm');
});
await asyncCheck('CAD saved picture views survive edits duplication Undo and project round trips',async()=>{
  resetLayers(160,120);const layer=ensureCadLayer();addCadBody(primitive('box'));layer.cad={...layer.cad!,view:{position:[100,-150,100],target:[0,0,10],up:[0,0,1],projection:'orthographic',span:80}};const expected=JSON.stringify(layer.cad.view);replaceBodies(currentBodies().map(item=>({...item,position:[10,0,10]})));assert(JSON.stringify(activeLayer().cad?.view)===expected,'Body edit lost the picture placement');duplicateLayer();assert(JSON.stringify(activeLayer().cad?.view)===expected,'Layer copy lost its picture view');const saved=projectData();resetLayers(10,10);await loadProjectData(saved);assert(JSON.stringify(activeLayer().cad?.view)===expected,'Project lost orthographic picture placement');const bad=JSON.parse(saved);bad.layers.find((l:{cad?:unknown})=>l.cad).cad.view.up=[0,0,0];let failed=false;try{await loadProjectData(JSON.stringify(bad));}catch{failed=true;}assert(failed&&JSON.stringify(activeLayer().cad?.view)===expected,'Invalid camera replaced the document');resetLayers(960,640);
});
check('CAD picture compositing respects background and foreground layers and preserves editable solid recipes',()=>{
  resetLayers(160,120);activeLayer().canvas.getContext('2d')!.fillStyle='#ef4858';activeLayer().canvas.getContext('2d')!.fillRect(0,0,160,120);const cad=ensureCadLayer();addCadBody(primitive('box'));const source=JSON.stringify(cad.cad),c=cad.canvas.getContext('2d')!;c.fillStyle='#f8bf45';c.fillRect(40,30,80,60);addLayer();activeLayer().canvas.getContext('2d')!.fillStyle='#3455dd';activeLayer().canvas.getContext('2d')!.fillRect(60,45,40,30);const output=document.createElement('canvas');output.width=160;output.height=120;renderLayers(output.getContext('2d')!,0);const ctx=output.getContext('2d')!,at=(x:number,y:number)=>Array.from(ctx.getImageData(x,y,1,1).data);assert(at(5,5)[0]===239&&at(45,35)[0]===248&&at(80,60)[2]===221&&JSON.stringify(cad.cad)===source,'Layer compositing flattened geometry or ignored the sheet order');resetLayers(960,640);
});
const sketchLine=(points:V2[],edge:number)=>{const a=points[edge],b=points[(edge+1)%points.length];return{x:b[0]-a[0],y:b[1]-a[1],length:Math.hypot(b[0]-a[0],b[1]-a[1]),angle:Math.atan2(b[1]-a[1],b[0]-a[0])};};
check('CAD length dimensions solve rectangles exactly and retain their square corners and centre',()=>{
  const seed=sketchPoints('rectangle',-10,-5,20,10),before=JSON.stringify(seed),solved=solveSketch(seed,[{id:'w',kind:'length',edge:0,value:36},{id:'h',kind:'length',edge:1,value:14},{id:'horizontal',kind:'horizontal',edge:0}],'rectangle');
  assert(Math.abs(sketchLine(solved,0).length-36)<1e-5&&Math.abs(sketchLine(solved,1).length-14)<1e-5,'Driving dimensions were not satisfied');assert(Math.abs(sketchLine(solved,0).y)<1e-6&&Math.abs(sketchLine(solved,1).x)<1e-6,'Rectangle lost its right angles');assert(Math.abs(solved.reduce((v,p)=>v+p[0],0))<1e-5&&JSON.stringify(seed)===before,'Solver moved the centre or mutated the input');
});
check('CAD absolute and between-line angle dimensions solve without flipping the initial branch',()=>{
  const rules:CadSketchConstraint[]=[{id:'angle',kind:'angle',edge:0,value:30},{id:'w',kind:'length',edge:0,value:20},{id:'h',kind:'length',edge:1,value:10}],solved=solveSketch(sketchPoints('rectangle',0,0,20,10),rules,'rectangle');assert(Math.abs(sketchLine(solved,0).angle-Math.PI/6)<1e-6,'Exact line angle failed');
  const triangle:V2[]=[[0,0],[20,0],[10,10]],angled=solveSketch(triangle,[{id:'base',kind:'horizontal',edge:0},{id:'angle',kind:'angle-between',edge:0,other:1,value:120}]);const delta=sketchLine(angled,0).angle-sketchLine(angled,1).angle;assert(Math.abs(Math.acos(Math.cos(delta))-Math.PI*2/3)<1e-6&&angled[2][1]>angled[0][1],'Between-line angle flipped or changed branch');
});
check('CAD horizontal vertical parallel and perpendicular relations constrain sketch lines',()=>{
  const points:V2[]=[[0,0],[20,2],[23,15],[-2,12]],rules:CadSketchConstraint[]=[{id:'h',kind:'horizontal',edge:0},{id:'v',kind:'vertical',edge:1},{id:'p',kind:'parallel',edge:0,other:2},{id:'n',kind:'perpendicular',edge:0,other:3}],solved=solveSketch(points,rules),a=sketchLine(solved,0),b=sketchLine(solved,2);assert(Math.abs(a.y)<1e-6&&Math.abs(sketchLine(solved,1).x)<1e-6&&Math.abs(a.x*b.y-a.y*b.x)<1e-5&&Math.abs(sketchLine(solved,3).x)<1e-6,'A geometric relation was not solved');assert(a.x*b.x<0,'Parallel lines lost their opposite directions');
});
check('CAD inconsistent dimensions and impossible triangles fail without changing the last valid sketch',()=>{
  const seed:V2[]=[[0,0],[10,0],[5,8]],before=JSON.stringify(seed);for(const rules of [[{id:'a',kind:'length',edge:0,value:10},{id:'b',kind:'length',edge:0,value:20}],[{id:'a',kind:'length',edge:0,value:30},{id:'b',kind:'length',edge:1,value:10},{id:'c',kind:'length',edge:2,value:10}],[{id:'a',kind:'horizontal',edge:0},{id:'b',kind:'angle',edge:0,value:45}]] as CadSketchConstraint[][]){let failed=false;try{solveSketch(seed,rules);}catch{failed=true;}assert(failed,'Conflicting constraints silently changed the sketch');}assert(JSON.stringify(seed)===before);
});
check('CAD redundant compatible constraints and repeated dimension changes remain stable',()=>{
  let points=sketchPoints('rectangle',-10,-5,20,10);for(const value of [40,8,60,20]){points=solveSketch(points,[{id:'a',kind:'length',edge:0,value},{id:'b',kind:'length',edge:0,value},{id:'h',kind:'horizontal',edge:0},{id:'v',kind:'vertical',edge:1}],'rectangle');assert(Math.abs(sketchLine(points,0).length-value)<1e-5,'Repeated or redundant constraints failed');}
});
check('CAD diameter dimensions keep the centre and produce a true circle from an ellipse',()=>{
  const solved=solveSketch(sketchPoints('circle',4,-7,20,10),[{id:'d',kind:'diameter',value:12}],'circle');assert(solved.length===96&&solved.every(p=>Math.abs(Math.hypot(p[0]-4,p[1]+7)-6)<1e-7),'Diameter did not preserve a true circle');let failed=false;try{solveSketch(solved,[{id:'d',kind:'diameter',value:12},{id:'e',kind:'diameter',value:16}],'circle');}catch{failed=true;}assert(failed,'Conflicting diameters were accepted');
});
await asyncCheck('CAD editing a saved dimension rebuilds an extrusion and later through holes non-destructively',async()=>{
  const root=await parametricFixture(),edited=editFeature(root,[0,0],item=>{assert(item.solid.kind==='extrude');item.solid.feature={...item.solid.feature,constraints:[{id:'w',kind:'length',edge:0,value:60},{id:'h',kind:'length',edge:1,value:30},{id:'horizontal',kind:'horizontal',edge:0}]};}),original=JSON.stringify(edited),mesh=await solidMesh(edited);closedCadMesh(mesh);assert(Math.abs(mesh.volume-(1800-Math.PI*25)*20)<4,'Dimension did not regenerate the pad and through holes: '+mesh.volume);const changed=editFeature(edited,[0,0],item=>{item.solid.feature!.constraints![0]={id:'w',kind:'length',edge:0,value:50};}),next=await solidMesh(changed);assert(Math.abs(next.volume-(1500-Math.PI*25)*20)<4&&JSON.stringify(edited)===original,'Editing only the saved dimension did not rebuild safely');
});
await asyncCheck('CAD constrained hole diameters rebuild beneath a native chamfer',async()=>{
  const root=await parametricFixture(),edited=editFeature(root,[0,1],item=>{assert(item.solid.kind==='extrude');item.solid.feature={...item.solid.feature,constraints:[{id:'diameter',kind:'diameter',value:10}]};}),edges=await solidEdges(edited),rim=edges.find(e=>e.ref.curve==='CIRCLE'&&Math.abs(e.ref.center[2]-1)<.01);assert(rim,'Hole rim was lost');const finished=finishedBody(edited,'chamfer',.5,[rim.ref]),mesh=await solidMesh(finished);closedCadMesh(mesh);const changed=editFeature(finished,[0,0,1],item=>{item.solid.feature!.constraints![0]={id:'diameter',kind:'diameter',value:8};}),rebuilt=await solidMesh(changed);closedCadMesh(rebuilt);assert(rebuilt.volume>mesh.volume+500,'Hole dimension did not regenerate the later chamfer');
});
await asyncCheck('CAD constrained revolve lengths change the solid without baking the original sketch',async()=>{
  const source=cadBody({kind:'revolve',points:[[5,0],[10,0],[10,20],[5,20]],degrees:360,plane:basePlane('xy'),feature:{sketch:'rectangle',constraints:[{id:'height',kind:'length',edge:1,value:30},{id:'width',kind:'length',edge:0,value:5},{id:'horizontal',kind:'horizontal',edge:0}]}},'Dimensioned ring'),before=JSON.stringify(source),mesh=await solidMesh(source);closedCadMesh(mesh);assert(Math.abs(mesh.volume-Math.PI*75*30)<4&&JSON.stringify(source)===before,'Revolve ignored its sketch dimensions');
});
await asyncCheck('CAD loft and sweep profile dimensions drive real precision geometry and STL',async()=>{
  const loft=defaultForm('loft'),sweep=defaultForm('sweep');assert(loft.kind==='loft'&&sweep.kind==='sweep');loft.ruled=true;loft.profiles[1].constraints=[{id:'diameter',kind:'diameter',value:24}];sweep.profile.constraints=[{id:'diameter',kind:'diameter',value:8}];sweep.path.points=[[0,0,0],[0,0,30]];const a=await solidMesh(cadBody(loft,'Dimensioned loft')),b=await solidMesh(cadBody(sweep,'Dimensioned sweep'));closedCadMesh(a);closedCadMesh(b);assert(Math.abs(a.volume-Math.PI*10*(100+120+144))<10&&Math.abs(b.volume-Math.PI*16*30)<1,'Profile dimensions did not reach the native kernel: '+a.volume+', '+b.volume);assert(binaryStl(b).byteLength===84+b.triangles*50);
});
await asyncCheck('CAD sketch constraints round trip through projects and malformed references fail safely',async()=>{
  resetLayers(160,120);ensureCadLayer();const source=cadBody({kind:'extrude',points:sketchPoints('rectangle',0,0,20,10),plane:basePlane('xy'),height:5,taper:1,twist:0,feature:{sketch:'rectangle',constraints:[{id:'width',kind:'length',edge:0,value:30},{id:'h',kind:'horizontal',edge:0}]}},'Constrained pad');addCadBody(source);const saved=projectData();resetLayers(10,10);await loadProjectData(saved);assert(JSON.parse(saved).version===10&&currentBodies()[0].solid.feature?.constraints?.[0].id==='width','Saved dimensions were discarded');assert(Math.abs((await solidMesh(currentBodies()[0])).volume-1500)<.01,'Reopened solid ignored its dimensions');const before=projectData();for(const rule of [{id:'bad',kind:'length',edge:99,value:10},{id:'bad',kind:'parallel',edge:0,other:0},{id:'bad',kind:'diameter',value:10},{id:'bad',kind:'angle',edge:0,value:NaN}]){const invalid=JSON.parse(saved);invalid.layers.find((l:{cad?:unknown})=>l.cad).cad.bodies[0].solid.feature.constraints=[rule];let failed=false;try{await loadProjectData(JSON.stringify(invalid));}catch{failed=true;}assert(failed&&projectData()===before,'Invalid constraints replaced the artwork');}resetLayers(960,640);
});

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
