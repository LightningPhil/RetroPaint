import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
const out=path.resolve('APP-USE-CASES/runs/2026-10-19-full-audit/evidence/headless-tab-focus-capability.json');
const browser=await chromium.launch({headless:true,channel:'chrome'}),context=await browser.newContext(),page=await context.newPage(),observations=[];
try{
 await page.goto('http://127.0.0.1:8101/');
 await page.evaluate(()=>{window.__focusProbe=[];for(const type of ['blur','focus'])window.addEventListener(type,e=>window.__focusProbe.push({type,trusted:e.isTrusted,at:performance.now()}));document.addEventListener('visibilitychange',e=>window.__focusProbe.push({type:'visibilitychange',trusted:e.isTrusted,hidden:document.hidden,at:performance.now()}));});
 const sample=async(label)=>observations.push({label,...await page.evaluate(()=>({visibility:document.visibilityState,hidden:document.hidden,focused:document.hasFocus(),events:window.__focusProbe}))});
 await page.bringToFront();await sample('original-page-activated');
 const other=await context.newPage();await other.goto('about:blank');await other.bringToFront();await page.waitForTimeout(250);await sample('other-tab-activated');
 await page.bringToFront();await page.waitForTimeout(100);await sample('original-page-reactivated');
 const session=await browser.newBrowserCDPSession();const target=await session.send('Target.createTarget',{url:'about:blank',newWindow:true,background:false});await session.send('Target.activateTarget',{targetId:target.targetId});await page.waitForTimeout(250);await sample('isolated-new-browser-window-activated');await session.send('Target.closeTarget',{targetId:target.targetId});await page.bringToFront();await sample('probe-finished');
 await fs.writeFile(out,JSON.stringify({at:new Date().toISOString(),browser:browser.version(),scope:'Separate headless browser only. Genuine target/tab activation; no synthetic DOM focus/visibility event, lifecycle override or user desktop access.',observations},null,2)+'\n');console.log(JSON.stringify(observations));
}finally{await browser.close();}
