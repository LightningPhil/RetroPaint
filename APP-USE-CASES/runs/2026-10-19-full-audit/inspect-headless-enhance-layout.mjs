import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
const folder=path.resolve('APP-USE-CASES/runs/2026-10-19-full-audit/evidence');
const suffix=process.argv[3]??'before';
const browser=await chromium.launch({headless:true,channel:'chrome'});
try{
 const context=await browser.newContext({viewport:{width:320,height:568}}),page=await context.newPage();page.setDefaultTimeout(90000);
 await page.goto(process.argv[2]??'http://127.0.0.1:8090/',{waitUntil:'domcontentloaded'});
 await page.locator('#studioBtn').click();await page.getByRole('switch',{name:'Advanced mode',exact:true}).check();await page.locator('[data-studio="layers"]').click();await page.locator('#openSuperResolution').click();await page.locator('#superResolutionDialog[open]').waitFor();
 await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
 const row=await page.locator('#superResolutionDialog').evaluate(e=>({rect:e.getBoundingClientRect().toJSON(),scrollHeight:e.scrollHeight,clientHeight:e.clientHeight,font:getComputedStyle(e).font,children:Array.from(e.children).map(n=>({tag:n.tagName,class:n.className,id:n.id,rect:n.getBoundingClientRect().toJSON(),scrollHeight:n.scrollHeight,clientHeight:n.clientHeight})),buttons:Array.from(e.querySelectorAll('button')).map(n=>({id:n.id,text:n.textContent,rect:n.getBoundingClientRect().toJSON()}))}));
 await page.screenshot({path:path.join(folder,'ENHANCE-headless-layout-'+suffix+'.png')});await fs.writeFile(path.join(folder,'ENHANCE-headless-layout-'+suffix+'.json'),JSON.stringify(row,null,2)+'\n');console.log(JSON.stringify({clientHeight:row.clientHeight,scrollHeight:row.scrollHeight,buttons:row.buttons.map(b=>({id:b.id,width:b.rect.width,height:b.rect.height}))},null,2));await context.close();
}finally{await browser.close();}
