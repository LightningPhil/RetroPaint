// Automated tests use a separate headless browser and ephemeral profiles.
// They never connect to the user's Chrome, desktop, or current artwork tab.
import { chromium } from 'playwright';
import { createServer } from 'vite';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';

const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const args=process.argv.slice(2);
const option=(name,fallback)=>{const i=args.indexOf(name);return i<0?fallback:args[i+1];};
const stamp=new Date().toISOString().replace(/[:.]/g,'-');
const out=path.resolve(option('--out',path.join(repo,'test-results','headless-'+stamp)));
await fs.mkdir(out,{recursive:true});
if(await fs.access(path.join(out,'report.json')).then(()=>true,()=>false))throw new Error('Choose a new output folder; an earlier report is already retained here.');
const report={started:new Date().toISOString(),execution:'Isolated headless browser; no desktop control and no connection to user browser sessions',source_revision:execFileSync('git',['rev-parse','HEAD'],{cwd:repo,encoding:'utf8'}).trim(),browser:null,suites:[]};
const save=async()=>fs.writeFile(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n');
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const sourcePaths=['index.html','package.json','package-lock.json',...await fs.readdir(path.join(repo,'src'),{recursive:true}).then(paths=>paths.filter(p=>/\.(ts|css)$/.test(p)).map(p=>path.join('src',p))),...await fs.readdir(path.join(repo,'tests')).then(paths=>paths.filter(p=>/\.(ts|html|mjs)$/.test(p)).map(p=>path.join('tests',p)))];
report.source_files=await Promise.all(sourcePaths.sort().map(async p=>({path:p,sha256:sha(await fs.readFile(path.join(repo,p)))})));
const server=await createServer({root:repo,server:{host:'127.0.0.1',port:0,strictPort:false,watch:{ignored:['**/APP-USE-CASES/**','**/test-results/**']}}});
let browser;
let current='Starting';
const progress=setInterval(()=>console.log(JSON.stringify({at:new Date().toISOString(),current})),20000);
try{
  await server.listen();
  const address=server.httpServer.address();
  const origin=`http://127.0.0.1:${address.port}`;
  browser=await chromium.launch({headless:true,channel:option('--channel','chrome')});
  report.browser=browser.version();report.origin=origin;
  const only=option('--suite','all');
  const suites=[{name:'painting',url:'/tests/painting.html',width:1280,height:720},...[[1280,720],[320,568],[390,844],[844,390]].map(([width,height])=>({name:`layout-${width}x${height}`,url:'/tests/mobile.html',width,height}))];
  if(!['all','layouts','acceptance',...suites.map(s=>s.name)].includes(only))throw new Error('Unknown test suite: '+only);
  if(only==='acceptance'&&!args.includes('--reset-acceptance'))throw new Error('The acceptance suite requires --reset-acceptance');
  for(const spec of suites){
    if(only!=='all'&&only!==spec.name&&!(only==='layouts'&&spec.name.startsWith('layout-')))continue;
    current=spec.name;console.log('START '+current);
    const context=await browser.newContext({viewport:{width:spec.width,height:spec.height},acceptDownloads:true});
    const page=await context.newPage();page.setDefaultTimeout(180000);
    const errors=[];page.on('pageerror',error=>errors.push(String(error.stack??error)));
    const entry={...spec,started:new Date().toISOString(),errors};report.suites.push(entry);await save();
    try{
      const url=new URL(spec.url,origin);if(option('--check',null))url.searchParams.set('check',option('--check',null));
      await page.goto(url.href,{waitUntil:'domcontentloaded',timeout:120000});
      await page.waitForFunction(()=>/^(PASS|\d+ FAIL|FAIL)/.test(document.title),null,{timeout:600000});
      entry.title=await page.title();
      entry.results=spec.name==='painting'?await page.locator('#results li').evaluateAll(items=>items.map(item=>({status:item.classList.contains('pass')?'pass':'fail',text:item.textContent}))):await page.locator('#mobileResults').textContent().then(text=>text.split('\n').filter(row=>/^(PASS|FAIL) /.test(row)).map(text=>({status:text.startsWith('PASS ')?'pass':'fail',text})));
      entry.passed=entry.results.filter(row=>row.status==='pass').length;entry.failed=entry.results.filter(row=>row.status!=='pass').length;
      entry.viewport=await page.evaluate(()=>({width:innerWidth,height:innerHeight,dpr:devicePixelRatio,touchPoints:navigator.maxTouchPoints,coarse:matchMedia('(pointer:coarse)').matches}));
      entry.status=entry.failed||errors.length||!entry.results.length?'Fail':'Pass';
      await page.screenshot({path:path.join(out,spec.name+'.png'),fullPage:false});
      await fs.writeFile(path.join(out,spec.name+'.txt'),entry.results.map(row=>row.text).join('\n')+'\n');
      console.log(`${entry.status.toUpperCase()} ${spec.name}: ${entry.passed} passed, ${entry.failed} failed, ${errors.length} page errors`);
    }catch(error){entry.status='Fail';entry.error=String(error.stack??error);console.log('FAIL '+spec.name+': '+error);await page.screenshot({path:path.join(out,spec.name+'-failure.png')}).catch(()=>{});}
    finally{entry.finished=new Date().toISOString();await save();await context.close();}
  }
  if(args.includes('--reset-acceptance')){
    current='PHOTO-008';
    const {testReset}=await import('./photo-reset-acceptance.mjs');
    report.photo_reset=await testReset(browser,{out,origin:option('--production-url',origin),fixture:option('--fixture',path.join(repo,'APP-USE-CASES/runs/2026-10-19-full-audit/evidence/PHOTO-008-all-settings-saved-before.retropaint')),progress:value=>{current=value;console.log('RESET '+value);}});
    await save();
  }
}catch(error){report.fatal=String(error.stack??error);console.error(report.fatal);process.exitCode=1;}
finally{
  clearInterval(progress);await browser?.close();await server.close();report.finished=new Date().toISOString();
  report.status=report.fatal||report.suites.some(s=>s.status!=='Pass')||report.photo_reset?.status==='Fail'?'Fail':'Pass';
  await save();console.log('REPORT '+path.join(out,'report.json'));if(report.status==='Fail')process.exitCode=1;
}
