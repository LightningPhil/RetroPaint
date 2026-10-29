// Native controls and actual downloaded files. Geometry checks below do not
// call RetroPaint's kernel, importer, serializer or mesh-volume implementation.
import { chromium } from 'playwright';
import { createServer } from 'vite';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import { AcceptanceDriver } from './acceptance-driver.mjs';

const out=path.resolve('test-results/workshop-'+new Date().toISOString().replace(/[:.]/g,'-'));
await fs.mkdir(out,{recursive:true});
const suppliedOrigin=process.argv[process.argv.indexOf('--origin')+1];
const external=process.argv.includes('--origin');
const server=external?null:await createServer({server:{host:'127.0.0.1',port:0,strictPort:false,hmr:false,watch:{ignored:['**/test-results/**','**/APP-USE-CASES/**']}}});
await server?.listen();
const browser=await chromium.launch({channel:'chrome',headless:true});
const origin=external?new URL('?layout-preview',suppliedOrigin).href:`http://127.0.0.1:${server.httpServer.address().port}/?layout-preview`;
const report={started:new Date().toISOString(),origin,checks:[],errors:[],out};

function inspectStl(bytes){
  const count=bytes.readUInt32LE(80);assert.equal(bytes.length,84+50*count);
  const min=[Infinity,Infinity,Infinity],max=[-Infinity,-Infinity,-Infinity],edges=new Map();let volume=0;
  for(let i=0;i<count;i++){
    const vertices=Array.from({length:3},(_,v)=>Array.from({length:3},(_,k)=>bytes.readFloatLE(84+50*i+12+v*12+k*4)));
    for(const v of vertices)for(let k=0;k<3;k++){assert(Number.isFinite(v[k]));min[k]=Math.min(min[k],v[k]);max[k]=Math.max(max[k],v[k]);}
    const [a,b,c]=vertices;
    volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6;
    for(let j=0;j<3;j++){
      const a=vertices[j].join(','),b=vertices[(j+1)%3].join(','),key=[a,b].sort().join('|');
      const e=edges.get(key)??{count:0,balance:0};e.count++;e.balance+=a<b?1:-1;edges.set(key,e);
    }
  }
  assert(volume>0,'STL must enclose positive volume');
  assert([...edges.values()].every(e=>e.count===2&&e.balance===0),'STL must be closed with consistent winding');
  return {triangles:count,volume,min,max,size:max.map((v,k)=>v-min[k])};
}
const near=(actual,expected,tolerance,label)=>assert(Math.abs(actual-expected)<=tolerance,`${label}: got ${actual}, expected ${expected} ± ${tolerance}`);
const check=async(name,run)=>{try{const evidence=await run();report.checks.push({name,status:'Pass',evidence});console.log('PASS '+name);}catch(error){report.checks.push({name,status:'Fail',error:String(error.stack??error)});console.log('FAIL '+name+': '+error.message);await page?.screenshot({path:path.join(out,'failure-'+report.checks.length+'.png')}).catch(()=>{});}finally{await fs.writeFile(path.join(out,'report.json'),JSON.stringify(report,null,2));}};
let page;
try{
  for(const [width,height] of [[1280,720],[320,568],[390,844],[844,390]])await check(`workspace modes ${width}x${height}`,async()=>{
    const context=await browser.newContext({viewport:{width,height}}),p=await context.newPage();
    try{
      await p.goto(origin);await p.locator('#studioBtn').click();
      for(const selector of ['#openCad','#drawingMode','[data-studio="layers"]','#layersToggle','#photoToggle'])assert.equal(await p.locator(selector).isVisible(),false,selector);
      await p.locator('#view').press('l');await p.locator('#view').press('p');assert.equal(await p.locator('#layersPanel').isVisible(),false);assert.equal(await p.locator('#photoPanel').isVisible(),false);
      await p.locator('#advancedMode').check();
      for(const selector of ['#openCad','#drawingMode','[data-studio="layers"]','#layersToggle','#photoToggle'])assert.equal(await p.locator(selector).isVisible(),true,selector);
      await p.locator('[data-studio="layers"]').click();await p.locator('#advancedMode').uncheck();
      assert.equal(await p.locator('[data-studio="file"]').getAttribute('aria-selected'),'true');
      await p.screenshot({path:path.join(out,`basic-${width}x${height}.png`)});
      await p.reload();await p.locator('#studioBtn').click();assert.equal(await p.locator('#advancedMode').isChecked(),false);
      await p.locator('#advancedMode').check();await p.reload();await p.locator('#studioBtn').click();assert.equal(await p.locator('#advancedMode').isChecked(),true);
      await p.screenshot({path:path.join(out,`advanced-${width}x${height}.png`)});
      const bounds=await p.locator('#studioDrawer').boundingBox();assert(bounds.x>=-1&&bounds.y>=-1&&bounds.x+bounds.width<=width+1&&bounds.y+bounds.height<=height+1);
      return {basicHidesAdvanced:true,shortcutsGated:true,persistedBothModes:true};
    }finally{await context.close();}
  });
  page=await browser.newPage({viewport:{width:1280,height:900},acceptDownloads:true});
  page.setDefaultTimeout(30000);page.on('pageerror',error=>report.errors.push(String(error)));
  await check('mode changes preserve vectors and switch new text to pixels',async()=>{
    await page.goto(origin);const d=new AcceptanceDriver(page,out);
    await d.drawer();await page.locator('#advancedMode').check();await page.locator('#drawingMode').selectOption('vector');await d.close();
    const text=async words=>{
      await page.locator('[data-tool="text"]').click();await page.locator('#textContent').fill(words);await d.close();
      const r=await page.locator('#view').boundingBox();await page.mouse.click(r.x+r.width*.45,r.y+r.height*.45);await page.keyboard.press('Control+Enter');
    };
    const saved=async label=>JSON.parse(await fs.readFile(await d.download(label),'utf8'));
    await text('Keep this vector');const before=await saved('vector-before');const original=before.layers.flatMap(l=>l.objects??[]).find(o=>o.kind==='text');assert(original);
    await d.drawer();await page.locator('#advancedMode').uncheck();await d.close();assert.deepEqual(await saved('vector-basic'),before);
    await text('Basic pixels');const basic=await saved('basic-new-text'),pieces=basic.layers.flatMap(l=>l.objects??[]);assert.deepEqual(pieces.find(o=>o.id===original.id),original);assert.equal(pieces.at(-1).kind,'raster');
    await d.drawer();await page.locator('#advancedMode').check();await d.close();await text('Advanced vector');const advanced=await saved('advanced-new-text');assert.equal(advanced.layers.flatMap(l=>l.objects??[]).at(-1).kind,'text');
    return {unchangedOnSwitch:true,basicText:'raster',advancedText:'text',originalVectorPreserved:true};
  });
  page.setDefaultTimeout(30000);
  await page.goto(origin);await page.locator('#studioBtn').click();await page.locator('#advancedMode').check();await page.locator('#openCad').click();await page.locator('#cadCanvas').waitFor();
  const idle=()=>page.waitForFunction(()=>!document.getElementById('cadWorkshop').hasAttribute('aria-busy'));
  const click=async selector=>{await page.locator(selector).click();await idle();};
  const tab=async name=>{if(await page.locator("#cadToolsToggle").isVisible()&&await page.locator("#cadToolsToggle").getAttribute("aria-expanded")==="false")await click("#cadToolsToggle");await click(`[data-cad-tab="${name}"]`);};
  const count=()=>page.locator('#cadPieceCount').textContent();
  const saveProject=async label=>{
    const [d]=await Promise.all([page.waitForEvent('download'),click('#cadSaveProject')]);const p=path.join(out,label+'.retropaint');await d.saveAs(p);return JSON.parse(await fs.readFile(p,'utf8'));
  };
  const stl=async label=>{
    await tab('print');const [d]=await Promise.all([page.waitForEvent('download'),click('#cadExportStl')]);const p=path.join(out,label+'.stl');await d.saveAs(p);return inspectStl(await fs.readFile(p));
  };
  const add=async shape=>{await tab('add');await click(`[data-cad-primitive="${shape}"]`);};
  const clear=async()=>{await page.locator('#cadCanvas').focus();await page.keyboard.press('Control+a');await page.keyboard.press('Delete');await idle();assert.equal(await count(),'0 pieces');};

  for(const shape of ['rectangle','circle','polygon'])await check('native drawn '+shape+' extrudes',async()=>{
    await clear();await tab('sketch');await page.locator('#cadPlane').selectOption('xy');
    assert.equal(await page.locator('#cadEmpty').isVisible(),false);
    await click(shape==='rectangle'?'#cadRectSketch':shape==='circle'?'#cadCircleSketch':'#cadPolygonSketch');
    const r=await page.locator('#cadCanvas').boundingBox(),x=r.x+r.width*.45,y=r.y+r.height*.45;
    if(shape==='polygon'){for(const [dx,dy]of [[0,0],[80,0],[50,70],[0,0]])await page.mouse.click(x+dx,y+dy);}
    else{await page.mouse.move(x,y);await page.mouse.down();await page.mouse.move(x+70,y+55,{steps:10});await page.mouse.up();}
    assert.match(await page.locator('#cadFeatureSummary').textContent(),/on workplane/);
    await click('#cadNextFeature');await page.locator('#cadFeatureAmount').fill('8');await click('#cadCreateFeature');assert.equal(await count(),'1 piece');
    const project=await saveProject('drawn-'+shape),solid=project.layers.flatMap(l=>l.cad?.bodies??[])[0].solid;
    const area=Math.abs(solid.points.reduce((sum,a,i)=>{const b=solid.points[(i+1)%solid.points.length];return sum+a[0]*b[1]-b[0]*a[1];},0))/2;
    const mesh=await stl('drawn-'+shape);near(mesh.volume,area*8,Math.max(.1,area*.001),'drawn area × depth');return mesh;
  });
  await check('drawn sketch revolves in original front plane',async()=>{
    await clear();await tab('sketch');await page.locator('#cadPlane').selectOption('xz');await click('#cadRectSketch');
    for(const [id,value]of [['X',5],['Y',2],['W',10],['H',20]])await page.locator('#cadSketch'+id).fill(String(value));
    await click('#cadUseDimensions');await click('#cadRevolveSketch');await click('#cadNextFeature');await click('#cadCreateFeature');assert.equal(await count(),'1 piece');
    const mesh=await stl('revolve-drawn-rectangle');near(mesh.volume,Math.PI*100*20,8,'revolved cylinder volume');near(mesh.size[2],20,.01,'original plane vertical axis');near(mesh.min[0],-5,.01,'axis at original left edge');return mesh;
  });
  for(const depth of [5,-5])await check('face sketch automatic '+(depth>0?'join':'cut'),async()=>{
    await clear();await add('box');await click('[data-cad-view="top"]');await click('#cadFit');await tab('sketch');await click('#cadPickFace');await click('[data-cad-view="top"]');
    const r=await page.locator('#cadCanvas').boundingBox();await page.mouse.click(r.x+r.width/2,r.y+r.height/2);
    assert.equal(await page.locator('#cadPlane').inputValue(),'face');await click('#cadRectSketch');
    for(const [id,value]of [['X',-5],['Y',-5],['W',10],['H',10]])await page.locator('#cadSketch'+id).fill(String(value));
    await click('#cadUseDimensions');await click('#cadNextFeature');assert.equal(await page.locator('#cadFeatureOperation').inputValue(),'auto');await page.locator('#cadFeatureAmount').fill(String(depth));await click('#cadCreateFeature');assert.equal(await count(),'1 piece');
    const mesh=await stl('automatic-'+depth);near(mesh.volume,8000+depth*100,.1,'face feature material');await click('#cadUndo');const undone=await stl('automatic-undone-'+depth);near(undone.volume,8000,.1,'undo restores cube');await click('#cadRedo');return mesh;
  });

  for(const shape of ['circle','polygon'])for(const depth of [4,-4])await check('native face '+shape+' automatic '+depth,async()=>{
    await clear();await add('box');await click('[data-cad-view="top"]');await click('#cadFit');await tab('sketch');await click('#cadPickFace');await click('[data-cad-view="top"]');
    const r=await page.locator('#cadCanvas').boundingBox(),x=r.x+r.width/2,y=r.y+r.height/2;await page.mouse.click(x,y);
    assert.equal(await page.locator('#cadPlane').inputValue(),'face');await click(shape==='circle'?'#cadCircleSketch':'#cadPolygonSketch');
    if(shape==='polygon'){for(const [dx,dy]of [[-20,-20],[20,-20],[0,20],[-20,-20]])await page.mouse.click(x+dx,y+dy);}
    else{await page.mouse.move(x,y);await page.mouse.down();await page.mouse.move(x+20,y,{steps:8});await page.mouse.up();}
    await click('#cadNextFeature');await page.locator('#cadFeatureAmount').fill(String(depth));await click('#cadCreateFeature');assert.equal(await count(),'1 piece');
    const project=await saveProject('face-'+shape+'-'+depth),solid=project.layers.flatMap(l=>l.cad?.bodies??[])[0].solid;assert.equal(solid.kind,'boolean');assert.equal(solid.operation,depth>0?'union':'subtract');
    const points=solid.children[1].solid.points,area=Math.abs(points.reduce((sum,a,i)=>{const b=points[(i+1)%points.length];return sum+a[0]*b[1]-b[0]*a[1];},0))/2;
    const mesh=await stl('face-'+shape+'-'+depth);near(mesh.volume,8000+depth*area,.2,'native face material');return mesh;
  });
  for(const [shape,plane]of [['circle','yz'],['polygon','xz']])await check('native '+shape+' revolve on '+plane,async()=>{
    await clear();await tab('sketch');await page.locator('#cadPlane').selectOption(plane);await click(shape==='circle'?'#cadCircleSketch':'#cadPolygonSketch');
    const r=await page.locator('#cadCanvas').boundingBox(),x=r.x+r.width*.5,y=r.y+r.height*.5;
    if(shape==='polygon'){for(const [dx,dy]of [[0,0],[60,0],[30,60],[0,0]])await page.mouse.click(x+dx,y+dy);}
    else{await page.mouse.move(x,y);await page.mouse.down();await page.mouse.move(x+30,y,{steps:8});await page.mouse.up();}
    await click('#cadRevolveSketch');await click('#cadNextFeature');await click('#cadCreateFeature');assert.equal(await count(),'1 piece');
    const project=await saveProject('revolve-'+shape),solid=project.layers.flatMap(l=>l.cad?.bodies??[])[0].solid;
    const moment=Math.abs(solid.points.reduce((sum,a,i)=>{const b=solid.points[(i+1)%solid.points.length];return sum+(a[0]+b[0])*(a[0]*b[1]-b[0]*a[1]);},0))/6;
    const mesh=await stl('revolve-'+shape);near(mesh.volume,2*Math.PI*moment,2*Math.PI*moment*.002,'revolution volume');return mesh;
  });

  for(const mode of ['pull','push','hole','cancel'])await check('two-click face sketch and direct '+mode,async()=>{
    await clear();await add('box');const before=await saveProject('direct-before-'+mode);await click('#cadFit');await tab('sketch');await click('#cadPickFace');await click('[data-cad-view="top"]');
    let r=await page.locator('#cadCanvas').boundingBox(),x=r.x+r.width/2,y=r.y+r.height/2;await page.mouse.click(x,y);assert.equal(await page.locator('#cadPlane').inputValue(),'face');
    await click(mode==='hole'?'#cadCircleSketch':'#cadRectSketch');r=await page.locator('#cadCanvas').boundingBox();x=r.x+r.width/2;y=r.y+r.height/2;
    await page.mouse.click(x-15,y-15);await page.mouse.move(x+15,y+15,{steps:5});await page.mouse.click(x+15,y+15);
    assert.equal(await page.locator('#cadSketchActions').isVisible(),true);await click(mode==='hole'?'#cadQuickHole':mode==='push'?'#cadQuickCut':'#cadQuickPull');
    if(mode!=='hole'){
      const h=await page.locator('#cadPullHandle').boundingBox();assert(h);await page.mouse.move(h.x+h.width/2,h.y+h.height/2);await page.mouse.down();await page.mouse.move(h.x+h.width/2,h.y+h.height/2+(mode==='push'?30:-30),{steps:8});await page.mouse.up();
      assert.match(await page.locator('#cadPullHandle').textContent(),mode==='push'?/Push/:/Pull/);
    }
    await page.screenshot({path:path.join(out,'direct-'+mode+'-preview.png')});
    if(mode==='cancel'){await click('#cadQuickCancel');assert.deepEqual(await saveProject('direct-cancelled'),before);return {unchanged:true};}
    await click('#cadQuickApply');assert.equal(await count(),'1 piece');assert.equal(await page.locator('#cadPullHandle').isVisible(),false);
    const project=await saveProject('direct-'+mode),solid=project.layers.flatMap(l=>l.cad?.bodies??[])[0].solid,feature=solid.children[1].solid,p=feature.points;
    const area=Math.abs(p.reduce((sum,a,i)=>{const b=p[(i+1)%p.length];return sum+a[0]*b[1]-b[0]*a[1];},0))/2,depth=mode==='hole'?-20:feature.height;
    const mesh=await stl('direct-'+mode);near(mesh.volume,8000+area*depth,.2,'direct manipulation material');return mesh;
  });
  const expected={box:8000,sphere:4/3*Math.PI*1000,cylinder:Math.PI*100*20,cone:Math.PI*100*20/3,tube:Math.PI*(100-64)*20,pyramid:4000/3,wedge:4000,torus:2*Math.PI*Math.PI*5.5*4.5*10};
  for(const shape of Object.keys(expected))await check('primitive '+shape,async()=>{
    await clear();await add(shape);assert.equal(await count(),'1 piece');const mesh=await stl(shape);
    near(mesh.volume,expected[shape],expected[shape]*.012,shape+' volume');near(mesh.min[2],0,.001,shape+' bed');
    await click('#cadUndo');assert.equal(await count(),'0 pieces');await click('#cadRedo');assert.equal(await count(),'1 piece');
    return mesh;
  });
  await check('tube exact size and 2 mm wall',async()=>{
    await clear();await add('tube');await tab('move');await click('[data-cad-edit="size"]');
    for(let i=0;i<3;i++)await page.locator('#cadSize'+i).fill('40');await page.locator('#cadWall').fill('2');await click('#cadApplySize');
    const mesh=await stl('tube-40-wall-2');for(const v of mesh.size)near(v,40,.01,'tube size');
    near(mesh.volume,Math.PI*(400-324)*40,35,'tube wall volume');return mesh;
  });
  await check('invalid tube wall preserves model and permits correction',async()=>{
    const before=await saveProject('tube-before-invalid');await tab('move');await click('[data-cad-edit="size"]');await page.locator('#cadWall').fill('21');await click('#cadApplySize');
    assert.match(await page.locator('#cadStatus').textContent(),/Tube wall must be less than half/);assert.deepEqual(await saveProject('tube-invalid-rejected'),before);
    await page.locator('#cadWall').fill('3');await click('#cadApplySize');const mesh=await stl('tube-corrected-wall-3');near(mesh.volume,Math.PI*(400-289)*40,40,'corrected wall volume');
    await click('#cadUndo');assert.deepEqual(await saveProject('tube-wall-undone'),before);await click('#cadRedo');return mesh;
  });
  for(const [operation,volume] of [['union',12000],['subtract',4000],['intersect',4000],['hull',12000]])await check('boolean '+operation,async()=>{
    await clear();await add('box');await add('box');await tab('move');await click('[data-cad-edit="transform"]');await page.locator('#cadPos0').fill('10');await click('#cadApplyTransform');
    await page.locator('#cadCanvas').focus();await page.keyboard.press('Control+a');await tab('build');await page.locator('#cadBuildPage').selectOption('combine');await click(`[data-cad-boolean="${operation}"]`);
    assert.equal(await count(),'1 piece');const mesh=await stl(operation);near(mesh.volume,volume,.05,operation+' volume');
    await click('#cadUndo');assert.equal(await count(),'2 pieces');await click('#cadRedo');assert.equal(await count(),'1 piece');return mesh;
  });
  await check('enclosed shell Preview Cancel Apply and Undo',async()=>{
    await clear();await add('box');const before=await saveProject('shell-original');await tab('build');await page.locator('#cadBuildPage').selectOption('shell');await click('#cadPickShellFaces');await click('#cadClearShellFaces');await page.locator('#cadShellThickness').fill('2');await click('#cadPreviewShell');
    await click('#cadFeatureCancel');assert.deepEqual(await saveProject('shell-cancelled'),before);
    await tab('build');await click('#cadPickShellFaces');await click('#cadClearShellFaces');await click('#cadPreviewShell');await click('#cadFeatureApply');const mesh=await stl('shell-2mm');near(mesh.volume,8000-16**3,.1,'shell material volume');
    await click('#cadUndo');assert.deepEqual(await saveProject('shell-undone'),before);await click('#cadRedo');return mesh;
  });
  await check('ruled loft uses original profile dimensions',async()=>{
    await clear();await tab('build');await page.locator('#cadBuildPage').selectOption('loft');await page.locator('#cadLoftPane').selectOption('settings');await page.locator('#cadLoftSides').selectOption('ruled');await click('#cadLoftMake');
    assert.equal(await count(),'1 piece');const mesh=await stl('loft');near(mesh.volume,Math.PI*10*(100+60+36),8,'loft frustum volume');near(mesh.size[2],30,.01,'loft height');
    await click('#cadUndo');assert.equal(await count(),'0 pieces');await click('#cadRedo');return mesh;
  });
  await check('straight sweep uses original profile and path',async()=>{
    await clear();await tab('build');await page.locator('#cadBuildPage').selectOption('sweep');await page.locator('#cadSweepPane').selectOption('coordinates');await page.locator('#cadSweepCoordinates').fill('0,0,0;0,0,30');await page.locator('#cadSweepPane').selectOption('settings');await page.locator('#cadSweepPathMode').selectOption('polyline');await click('#cadSweepMake');
    assert.equal(await count(),'1 piece');const mesh=await stl('sweep');near(mesh.volume,Math.PI*9*30,2,'sweep volume');near(mesh.size[2],30,.01,'sweep height');
    await click('#cadUndo');assert.equal(await count(),'0 pieces');await click('#cadRedo');return mesh;
  });
  await check('project save reopen preserves editable CAD',async()=>{
    const before=await saveProject('workshop-before');await click('#cadClose');await page.locator('#projectInput').setInputFiles(path.join(out,'workshop-before.retropaint'));await page.locator('#editorStatus').filter({hasText:'Project opened'}).waitFor();
    await page.locator('#studioBtn').click();await page.locator('#openCad').click();await page.locator('#cadCanvas').waitFor();await idle();
    const after=await saveProject('workshop-reopened');assert.deepEqual(after,before);const mesh=await stl('reopened');near(mesh.volume,Math.PI*9*30,2,'reopened sweep volume');return {exactProject:true,mesh};
  });
  for(const width of [320,390])await check('phone '+width+' polygon closes and extrudes',async()=>{
    await page.setViewportSize({width,height:844});await clear();
    if(await page.locator('#cadToolsToggle').getAttribute('aria-expanded')==='false')await click('#cadToolsToggle');
    await tab('sketch');await page.locator('#cadPlane').selectOption('xy');await click('#cadPolygonSketch');
    const r=await page.locator('#cadCanvas').boundingBox(),x=r.x+r.width*.4,y=r.y+r.height*.4;
    for(const [dx,dy]of [[0,0],[50,0],[25,50],[0,0]])await page.mouse.click(x+dx,y+dy);
    assert.equal(await page.locator('#cadToolsToggle').getAttribute('aria-expanded'),'false');await click('#cadQuickPull');await page.locator('#cadPullHandle').focus();await page.keyboard.press('ArrowDown');await click('#cadQuickApply');assert.equal(await count(),'1 piece');
    const mesh=await stl('phone-polygon-'+width);await page.screenshot({path:path.join(out,'phone-sketch-'+width+'.png')});return mesh;
  });

}finally{
  report.finished=new Date().toISOString();report.status=report.errors.length||report.checks.some(c=>c.status==='Fail')?'Fail':'Pass';
  await fs.writeFile(path.join(out,'report.json'),JSON.stringify(report,null,2));await browser.close();await server?.close();console.log('REPORT '+path.join(out,'report.json'));if(report.status==='Fail')process.exitCode=1;
}
