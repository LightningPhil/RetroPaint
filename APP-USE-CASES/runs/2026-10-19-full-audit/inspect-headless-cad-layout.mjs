import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
const folder=path.resolve('APP-USE-CASES/runs/2026-10-19-full-audit/evidence');
const suffix=process.argv[3]??'before';
const browser=await chromium.launch({headless:true,channel:'chrome'});
try{
 const context=await browser.newContext({viewport:{width:1280,height:720}}),page=await context.newPage();page.setDefaultTimeout(90000);
 await page.goto(process.argv[2]??'http://127.0.0.1:8090/',{waitUntil:'domcontentloaded'});
 await page.locator('#studioBtn').click();await page.getByRole('switch',{name:'Advanced mode',exact:true}).check();await page.locator('#openCad').click();await page.locator('#cadWorkshop').waitFor();
 await page.locator('[data-cad-tab="build"]').click();await page.locator('#cadBuildPage').selectOption('loft');
 const rows=[];
 for(const pane of ['outline','placement','draw','point','coordinates','copy','settings']){
  await page.locator('#cadLoftPane').selectOption(pane);await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  const row=await page.locator('#cadPagebuild').evaluate(e=>{const content=e.querySelector('.cad-page-content'),style=getComputedStyle(e),innerStyle=getComputedStyle(content);return {pane:document.querySelector('#cadLoftPane').value,page:{clientHeight:e.clientHeight,scrollHeight:e.scrollHeight,clientWidth:e.clientWidth,scrollWidth:e.scrollWidth,rect:e.getBoundingClientRect().toJSON(),padding:style.padding,overflowY:style.overflowY},content:{zoom:innerStyle.zoom,height:content.getBoundingClientRect().height,scrollHeight:content.scrollHeight,clientHeight:content.clientHeight,width:content.getBoundingClientRect().width,margin:innerStyle.margin,font:innerStyle.font},visibleControls:Array.from(e.querySelectorAll('input,select,button')).filter(n=>n.getClientRects().length).map(n=>({id:n.id,rect:n.getBoundingClientRect().toJSON()}))};});
  rows.push(row);await page.screenshot({path:path.join(folder,'CAD-headless-layout-'+pane+'-'+suffix+'.png')});
 }
 await fs.writeFile(path.join(folder,'CAD-headless-layout-'+suffix+'.json'),JSON.stringify(rows,null,2)+'\n');console.log(JSON.stringify(rows.map(r=>({pane:r.pane,clientHeight:r.page.clientHeight,scrollHeight:r.page.scrollHeight,contentHeight:r.content.height,zoom:r.content.zoom})),null,2));
 await context.close();
}finally{await browser.close();}
