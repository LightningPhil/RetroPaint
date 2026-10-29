import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {AcceptanceDriver} from './acceptance-driver.mjs';
import {controlledRenderClock} from './controlled-render-time.mjs';
const args=process.argv.slice(2),option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
const root=path.resolve('APP-USE-CASES/runs/2026-10-19-full-audit'),out=path.resolve(option('--out','test-results/duplicate-fixture')),origin=option('--origin','http://127.0.0.1:8098/');await fs.mkdir(out,{recursive:true});assert.equal((await fs.readdir(out)).length,0,'Use a fresh fixture output directory');
const browser=await chromium.launch({headless:true,channel:'chrome'}),report={started:new Date().toISOString(),origin,execution:'Actual public UI enriches the genuine MIX Character layer; pixels and live definitions become its Existing artwork object, with a new editable text object and an independent saved photo recipe. Fixed completed-render phase10000ms.',errors:[]};
const create=async folder=>{await fs.mkdir(folder,{recursive:true});const context=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true});await context.addInitScript(controlledRenderClock);await context.addInitScript(()=>{window.__acceptanceRenderTime=10000;});const page=await context.newPage(),driver=new AcceptanceDriver(page,folder);page.setDefaultTimeout(30000);page.on('pageerror',e=>report.errors.push(String(e)));await page.goto(origin,{waitUntil:'domcontentloaded'});return{context,page,driver};};
const {context,page,driver}=await create(path.join(out,'producer'));
try{
 await driver.advanced();await driver.open(path.join(root,'headless/MIX-final/MIX-enriched.retropaint'),'project');await driver.download('before');await driver.drawer();await page.locator('#drawingMode').selectOption('vector');await driver.close();if(await page.locator('#layersPanel').isVisible())await page.locator('#closeLayers').click();
 await page.locator('[data-tool="text"]').click();await page.locator('#textContent').fill('Copy source');await page.locator('#textFont').selectOption('Arial');await page.locator('#textSize').fill('24');await page.locator('#placeText').click();await page.locator('#view').press('Escape');
 await driver.photo();await driver.group('light','light-basic');await driver.slider('Exposure',.25);await driver.slider('Brightness',10);await driver.ready();await page.locator('#photoApply').click();await page.locator('#photoPanel').waitFor({state:'hidden'});const saved=await driver.download('enriched');await driver.download('enriched','png');await driver.snapshot('enriched');
 const fresh=await create(path.join(out,'fresh'));try{await fresh.driver.open(saved,'project');await fresh.driver.download('fixture');await fresh.driver.download('fixture','png');await fresh.driver.snapshot('fixture');report.fresh_reopen_complete=true;}finally{await fresh.context.close();}
 report.status=report.errors.length?'Fail':'Pass';
}catch(error){report.status='Fail';report.error=String(error.stack??error);await driver.snapshot('failure').catch(()=>{});}
finally{report.finished=new Date().toISOString();await fs.writeFile(path.join(out,'duplicate-fixture-ui.json'),JSON.stringify(report,null,2)+'\n');await context.close();await browser.close();console.log('DUPLICATE FIXTURE '+report.status);if(report.status!=='Pass')process.exitCode=1;}
