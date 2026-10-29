import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {AcceptanceDriver} from './acceptance-driver.mjs';
const root=path.resolve('APP-USE-CASES/runs/2026-10-19-full-audit'),out=path.join(root,'headless/FILE-001-before');await fs.mkdir(out,{recursive:true});assert.equal((await fs.readdir(out)).length,0);
const report={case:'FILE-001',started:new Date().toISOString(),origin:'http://127.0.0.1:8101/',harness_sha256:createHash('sha256').update(await fs.readFile(new URL(import.meta.url))).digest('hex'),expectation:'New picture first permits supported dimensions and explicit acceptance. Merely opening New or submitting invalid sizes must preserve the complete previous document.',rows:[],errors:[]},browser=await chromium.launch({headless:true,channel:'chrome'});
try{for(const [index,viewport] of [[1280,720],[320,568],[390,844],[844,390]].entries()){
 const folder=path.join(out,'v'+(index+1));await fs.mkdir(folder);const context=await browser.newContext({viewport:{width:viewport[0],height:viewport[1]},acceptDownloads:true}),page=await context.newPage(),d=new AcceptanceDriver(page,folder);page.on('pageerror',e=>report.errors.push(String(e)));try{
  await page.goto(report.origin);await page.bringToFront();const r=await page.locator('#view').boundingBox();await page.mouse.click(r.x+r.width/2,r.y+r.height/2);await d.download('before');await d.download('before','png');await d.drawer();await page.getByRole('button',{name:'New picture',exact:true}).click();await page.waitForTimeout(150);const dialogs=await page.getByRole('dialog',{name:'New picture',exact:true}).count();await d.snapshot('after-opening-new');
  if(dialogs===0){await d.close();await d.download('after-opening-new');await d.download('after-opening-new','png');report.rows.push({viewport,missing_dimension_and_acceptance_controls:true,expected_previous_data_until_explicit_valid_acceptance:true,status:'Fail',unexecuted_branches:'Requested valid/invalid size entry cannot be reached because New immediately replaces the picture.'});}else{report.rows.push({viewport,status:'Unexpected dialog present; inspect before classifying'});}
 }finally{await context.close();}
}report.status=report.rows.every(r=>r.status==='Fail')?'Fail':'Inspect';}catch(error){report.status='Harness failure';report.error=String(error.stack??error);}finally{report.finished=new Date().toISOString();await fs.copyFile(new URL(import.meta.url),path.join(out,'executed-harness.mjs'));await fs.writeFile(path.join(out,'FILE-001-ui.json'),JSON.stringify(report,null,2)+'\n');await browser.close();console.log(JSON.stringify({status:report.status,rows:report.rows.length}));}
