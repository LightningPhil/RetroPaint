import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {AcceptanceDriver} from './acceptance-driver.mjs';
import {controlledRenderClock} from './controlled-render-time.mjs';
const args=process.argv.slice(2),option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
const root=path.resolve('APP-USE-CASES/runs/2026-10-19-full-audit'),out=path.resolve(option('--out','test-results/layer-alpha-export')),origin=option('--origin','http://127.0.0.1:8095/');await fs.mkdir(out,{recursive:true});assert.equal((await fs.readdir(out)).length,0,'Choose a fresh evidence directory');const file=path.join(out,'LAYER-010-ui.json');
const browser=await chromium.launch({headless:true,channel:'chrome'}),report={started:new Date().toISOString(),origin,execution:'Real layer eyes, PNG/JPEG downloads and chooser reopens in isolated contexts; render phase10000ms',rows:[],errors:[]};
const create=async(width,height,folder)=>{await fs.mkdir(folder,{recursive:true});const context=await browser.newContext({viewport:{width,height},acceptDownloads:true});await context.addInitScript(controlledRenderClock);await context.addInitScript(()=>{window.__acceptanceRenderTime=10000;});const page=await context.newPage(),driver=new AcceptanceDriver(page,folder);page.setDefaultTimeout(30000);page.on('pageerror',e=>report.errors.push(String(e)));await page.goto(origin,{waitUntil:'domcontentloaded'});return{context,page,driver};};
const pair=async(driver,label)=>{const saved=await driver.download(label);await driver.download(label,'png');return saved;};
try{
 for(const [width,height] of [[1280,720],[320,568],[390,844],[844,390]]){
  console.log('ALPHA '+width+'x'+height);const folder=path.join(out,width+'x'+height),{context,page,driver}=await create(width,height,folder);
  const hide=async name=>{if(!await page.locator('#layersPanel').isVisible())await page.locator('#layersToggle').click();await page.getByRole('button',{name:'Hide '+name,exact:true}).click();};
  try{
   await driver.advanced();await driver.open(path.join(root,'headless/MIX-final/MIX-enriched.retropaint'),'project');await pair(driver,'before');await hide('Paper');await pair(driver,'paper-hidden');await hide('Backdrop');const source=await pair(driver,'both-hidden'),png=path.join(folder,'both-hidden.png');const jpeg=await driver.download('transparent-flattened','jpeg');await driver.download('source-after-exports');await driver.snapshot('source-after-exports');
   for(const label of ['backdrop-hide-undone','paper-hide-undone']){await page.locator('#undoBtn').click();await pair(driver,label);}for(const label of ['paper-hide-redone','backdrop-hide-redone']){await page.locator('#view').press('Control+Shift+z');await pair(driver,label);}
   for(const [label,input,kind] of [['png',png,'image'],['jpeg',jpeg,'image'],['project',source,'project']]){
    const {context:c,page:p,driver:d}=await create(width,height,path.join(folder,'fresh-'+label));try{await d.open(input,kind);await d.download('reopened');await d.download('reopened','png');await d.snapshot('reopened');}finally{await c.close();}
   }
   report.rows.push({width,height,paper_and_backdrop_visibility_variants:true,actual_png_jpeg_and_project_reopened:true,source_exports_and_history_captured:true});
  }catch(error){await driver.snapshot('failure').catch(()=>{});throw error;}finally{await context.close();}
 }
 report.status=report.errors.length?'Fail':'Pass';
}catch(error){report.status='Fail';report.error=String(error.stack??error);}
finally{report.finished=new Date().toISOString();await fs.writeFile(file,JSON.stringify(report,null,2)+'\n');await browser.close();console.log('ALPHA '+report.status);if(report.status!=='Pass')process.exitCode=1;}
