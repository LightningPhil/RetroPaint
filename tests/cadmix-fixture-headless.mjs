import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {AcceptanceDriver} from './acceptance-driver.mjs';
const args=process.argv.slice(2),option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
const root=path.resolve('APP-USE-CASES/runs/2026-10-19-full-audit'),out=path.resolve(option('--out','test-results/cadmix-fixtures')),origin=option('--origin','http://127.0.0.1:8098/');await fs.mkdir(out,{recursive:true});assert.equal((await fs.readdir(out)).length,0,'Choose a fresh fixture folder');
const plan=JSON.parse(await fs.readFile(path.join(root,'fixtures/CADMIX-pairwise-plan.json'),'utf8')),browser=await chromium.launch({headless:true,channel:'chrome'}),report={started:new Date().toISOString(),origin,execution:'Actual public projection/view, Photo lab, layer and file controls in isolated headless contexts; no desktop use',rows:[],errors:[]};
const create=async folder=>{await fs.mkdir(folder,{recursive:true});const context=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true}),page=await context.newPage(),driver=new AcceptanceDriver(page,folder);page.setDefaultTimeout(60000);page.on('pageerror',e=>report.errors.push(String(e)));await page.goto(origin,{waitUntil:'domcontentloaded'});return{context,page,driver};};
const list=async page=>{if(!await page.locator('#layersPanel').isVisible())await page.locator('#layersToggle').click();if(await page.locator('#layerOptions').evaluate(e=>e.open))await page.locator('#layerOptions summary').click();};
try{
 for(const variant of plan.rows){
  console.log('CADMIX '+variant.fixture);const folder=path.join(out,variant.fixture),{context,page,driver}=await create(folder);
  try{
   await driver.open(path.join(root,'backups/artwork-before-acceptance-audit.retropaint'),'project');await driver.drawer();assert.equal(await page.locator('#openCad').isVisible(),false);await page.locator('#advancedMode').check();await page.locator('#openCad').click();await page.waitForFunction(()=>document.activeElement?.id==='cadCanvas');await page.locator('[data-cad-tab="inspect"]').click();await page.locator('#cadInspectPage').selectOption('camera');await page.locator('#cadProjection').selectOption(variant.projection);await page.locator('#cadExactView').selectOption('iso');await page.locator('#cadShowExactView').click();await page.locator('#cadInspectPage').selectOption('picture');await page.locator('#cadPictureMode').check();await page.locator('#cadPinView').click();await page.locator('#cadClose').click();await page.locator('#cadWorkshop').waitFor({state:'hidden'});
   if(variant.photo||variant.crop){
    await list(page);await page.getByRole('button',{name:/^Paint on Backdrop(?:, selected)?$/}).click();await page.getByRole('button',{name:'Edit Backdrop in Photo lab',exact:true}).click();await driver.ready();
    if(variant.photo){await driver.group('light','light-basic');await driver.slider('Exposure',.5);await driver.slider('Brightness',5);await driver.ready();}
    if(variant.crop){await driver.group('geometry','geometry-crop');for(const [key,value] of [['width',760],['height',480],['x',100],['y',80]]){const input=page.locator('#photoCrop-'+key);await input.fill(String(value));await input.press('Tab');await driver.ready();}}
    await page.locator('#photoApply').click();await page.locator('#photoPanel').waitFor({state:'hidden'});
   }
   await list(page);await page.getByRole('button',{name:/^Paint on Paint above 3D(?:, selected)?$/}).click();const saved=await driver.download('fixture');await driver.download('fixture','png');await driver.snapshot('fixture');
   const fresh=await create(path.join(folder,'fresh'));try{await fresh.driver.open(saved,'project');await fresh.driver.download('fixture');await fresh.driver.download('fixture','png');await fresh.driver.snapshot('fixture');}finally{await fresh.context.close();}
   report.rows.push({...variant,actual_camera_pinned:true,photo_exposure:variant.photo?.5:0,photo_brightness:variant.photo?5:0,crop_pixels:variant.crop?[100,80,760,480]:null,actual_fresh_reopen_complete:true});
  }catch(error){await driver.snapshot('failure').catch(()=>{});throw error;}finally{await context.close();}
 }
 report.status=report.errors.length?'Fail':'Pass';
}catch(error){report.status='Fail';report.error=String(error.stack??error);}
finally{report.finished=new Date().toISOString();await fs.writeFile(path.join(out,'CADMIX-fixture-ui.json'),JSON.stringify(report,null,2)+'\n');await browser.close();console.log('CADMIX '+report.status);if(report.status!=='Pass')process.exitCode=1;}
