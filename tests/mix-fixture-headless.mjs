import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {AcceptanceDriver} from './acceptance-driver.mjs';
const args=process.argv.slice(2),option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
const out=path.resolve(option('--out','test-results/mix-fixture')),origin=option('--origin','http://127.0.0.1:8094/');await fs.mkdir(out,{recursive:true});const file=path.join(out,'MIX-producer-ui.json');if(await fs.access(file).then(()=>true,()=>false))throw new Error('Retained fixture exists; choose a fresh output directory.');
const browser=await chromium.launch({headless:true,channel:'chrome'}),context=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true}),page=await context.newPage(),driver=new AcceptanceDriver(page,out),report={started:new Date().toISOString(),origin,execution:'All MIX fixture content created through actual public UI in isolated headless Chrome',errors:[]};page.on('pageerror',e=>report.errors.push(String(e)));
page.setDefaultTimeout(20000);
const showLayers=async()=>{console.log('MIX show layers');if(!await page.locator('#layersPanel').isVisible())await page.locator('#layersToggle').click();};
const hideLayers=async()=>{if(await page.locator('#layersPanel').isVisible())await page.locator('#closeLayers').click();};
const options=async()=>{await showLayers();if(!await page.locator('#layerOptions').evaluate(e=>e.open))await page.locator('#layerOptions summary').click();};
const add=async name=>{console.log('MIX add '+name);await showLayers();if(await page.locator('#layerOptions').evaluate(e=>e.open))await page.locator('#layerOptions summary').click();await page.locator('#addLayer').click();await options();await page.locator('#layerName').fill(name);await page.locator('#layerName').press('Enter');await hideLayers();await driver.record({action:'created-and-renamed-layer',name});};
const select=async name=>{await showLayers();if(await page.locator('#layerOptions').evaluate(e=>e.open))await page.locator('#layerOptions summary').click();await page.getByRole('button',{name:new RegExp('^Paint on '+name+'(?:, selected)?$')}).click();await hideLayers();await driver.record({action:'selected-layer',name});};
const point=async(x,y)=>{const r=await page.locator('#view').boundingBox();return{x:r.x+x/960*r.width,y:r.y+y/640*r.height};};
const click=async(x,y)=>{const p=await point(x,y);await page.mouse.click(p.x,p.y);};
const drag=async(x,y,xx,yy)=>{const p=await point(x,y),q=await point(xx,yy);await page.mouse.move(p.x,p.y);await page.mouse.down();await page.mouse.move(q.x,q.y,{steps:12});await page.mouse.up();await driver.record({action:'paper-gesture',from:[x,y],to:[xx,yy]});};
const solid=async name=>{console.log('MIX colour '+name);await driver.snapshot('before-colour-'+name);await page.locator('[data-target="tray-solids"]').click();await page.getByRole('button',{name,exact:true}).click();};
const mode=async value=>{await driver.drawer();await page.locator('#drawingMode').selectOption(value);await driver.close();};
const pair=async label=>{console.log('MIX save '+label);const saved=await driver.download(label);await driver.download(label,'png');await driver.snapshot(label);return saved;};
try{
 await page.goto(origin,{waitUntil:'domcontentloaded'});await driver.advanced();await add('Backdrop');await solid('Blue');await page.locator('[data-tool="bucket"]').click();await click(480,320);await page.waitForTimeout(1000);
 await add('Character');await solid('Red');await page.locator('[data-tool="shapes"]').click();await page.locator('#shapesDrawer details summary').click();await page.locator('#shapeFill').selectOption('primary');await page.locator('#shapeOutline').selectOption('none');await page.locator('[data-shape="rect"]').click();await drag(100,100,200,180);
 await solid('Green');await drag(400,300,500,380);await options();await driver.slider('Layer opacity',.5);await hideLayers();
 await add('Caption');await mode('vector');await solid('Yellow');await page.locator('[data-tool="text"]').click();await page.locator('#textContent').fill('MIX caption');await page.locator('#textFont').selectOption('Arial');await page.locator('#textSize').fill('36');await click(90,480);await page.locator('#placeText').click();await page.locator('#view').press('Escape');
 await page.locator('[data-tool="stamp"]').click();await page.getByRole('button',{name:'Stamp 🐱',exact:true}).click();await click(730,490);await page.locator('#view').press('Escape');await pair('MIX-basic');
 await mode('raster');await select('Backdrop');await driver.photo();await driver.group('light','light-basic');await driver.slider('Exposure',.5);await driver.ready();await page.locator('#photoApply').click();await page.locator('#photoPanel').waitFor({state:'hidden'});
 await select('Character');await page.locator('[data-tool="draw"]').click();await page.locator('[data-applicator="marker"]').click();await page.locator('#brushSize').press('Home');for(let i=1;i<35;i++)await page.locator('#brushSize').press('ArrowRight');
 await page.locator('[data-target="tray-textures"]').click();await page.getByRole('button',{name:'water ink',exact:true}).click();await drag(100,420,500,420);
 await page.locator('[data-target="tray-live"]').click();await page.locator('#clearBeltBtn').click();for(const colour of ['Red','Blue']){await page.getByRole('button',{name:colour+' for live ink',exact:true}).click();await page.locator('#addBeltBtn').click();}await drag(100,560,500,560);const enriched=await pair('MIX-enriched');
 const freshOut=path.join(out,'fresh');await fs.mkdir(freshOut,{recursive:true});const fresh=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true}),p=await fresh.newPage(),d=new AcceptanceDriver(p,freshOut);p.on('pageerror',e=>report.errors.push(String(e)));await p.goto(origin,{waitUntil:'domcontentloaded'});await d.open(enriched,'project');await d.download('MIX-reopened');await d.download('MIX-reopened','png');await d.snapshot('MIX-reopened');await fresh.close();report.fresh_reopen_complete=true;report.status=report.errors.length?'Fail':'Pass';
}catch(error){report.status='Fail';report.error=String(error.stack??error);await driver.snapshot('failure').catch(()=>{});}
finally{report.finished=new Date().toISOString();await fs.writeFile(file,JSON.stringify(report,null,2)+'\n');await context.close();await browser.close();console.log('MIX '+report.status);if(report.status!=='Pass')process.exitCode=1;}
