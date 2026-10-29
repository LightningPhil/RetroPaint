# Assemble the same already-reviewed native boundary workflow with a separate
# case/applicator, retaining its original Marker source and all prior evidence.
from pathlib import Path
repo=Path(__file__).resolve().parents[3];target=repo/'tests/calligraphy-acceptance-headless.mjs';assert not target.exists()
text=(repo/'tests/marker-acceptance-headless.mjs').read_text(encoding='utf-8').replace('PAINT-001','PAINT-003').replace('test-results/marker','test-results/calligraphy').replace('8098','8099').replace('MARKER ','CALLIGRAPHY ').replace('Native mouse gestures','Native calligraphy mouse gestures').replace('[data-applicator="marker"]','[data-applicator="callig"]')
text=text.replace("report.status=report.errors.length?'Fail':'Pass';","""for(const row of plan.rows.filter(r=>r.size===22&&r.strength===1)){
  const [width,height]=row.viewport;
  for(const phase of ['directions','short-sharp']){
   console.log('CALLIGRAPHY '+row.id+' '+phase);const folder=path.join(out,row.id,phase),{context,page,driver}=await create(width,height,folder);
   try{
    await page.locator('[data-tool="draw"]').click();await page.locator('[data-applicator="callig"]').click();await page.locator('#brushSize').press('Home');for(let i=0;i<21;i++)await page.locator('#brushSize').press('ArrowRight');await page.locator('#opacity').press('End');
    const colour=async name=>{if(!await page.locator('[data-target="tray-solids"]').isVisible())await page.locator('#paletteToggle').click();await page.locator('[data-target="tray-solids"]').click();await page.getByRole('button',{name,exact:true}).click();if(await page.locator('#paletteToggle').getAttribute('aria-expanded')==='true')await page.locator('#paletteToggle').click();};await colour('Red');await pair(driver,'before');
    const paths=phase==='directions'?Object.entries(plan.direction_paths).flatMap(([name,points])=>[{label:'red-'+name,points,colour:'Red'},{label:'blue-'+name,points:points.map(([x,y])=>[x,y+290]),colour:'Blue'}]).sort((a,b)=>a.colour==='Red'&&b.colour==='Blue'?-1:a.colour==='Blue'&&b.colour==='Red'?1:0):[{label:'short',points:[[800,200],[801,200]],colour:'Red'},{label:'sharp',points:[[100,420],[200,520],[300,420],[400,520]],colour:'Red'}];
    const samples=paths.map(item=>({...item,samples:item.points.flatMap((a,i)=>i===item.points.length-1?[a]:Array.from({length:21},(_,j)=>{const b=item.points[i+1],t=j/21;return[a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])];}))}));
    const required=samples.flatMap(item=>item.samples),preparation=[];
    for(let attempt=0;attempt<4;attempt++){
     const covered=await page.locator('#view').evaluate((view,points)=>{const r=view.getBoundingClientRect();return points.map(source=>({source,hit:document.elementFromPoint(r.x+source[0]/960*r.width,r.y+source[1]/640*r.height)?.id})).filter(p=>p.hit!=='view');},required);if(!covered.length)break;assert(attempt<3,'Declared calligraphy paths are covered');await page.locator('#paperControls').getByRole('button',{name:'Zoom out',exact:true}).click();await page.waitForTimeout(80);preparation.push({action:'actual-paper-Zoom-out',previously_covered:covered});
    }
    await driver.record({action:'paper-view-preparation',steps:preparation,source_geometry_unchanged:true});
    await page.locator('#view').evaluate(e=>{window.__calligraphyInput=[];for(const type of ['pointerdown','pointermove','pointerup'])e.addEventListener(type,event=>{const r=e.getBoundingClientRect();window.__calligraphyInput.push({type,trusted:event.isTrusted,pointerType:event.pointerType,timeStamp:event.timeStamp,source:[(event.clientX-r.x)*960/r.width,(event.clientY-r.y)*640/r.height]});});});
    const point=async source=>{const r=await page.locator('#view').boundingBox(),p={x:r.x+source[0]/960*r.width,y:r.y+source[1]/640*r.height};assert.equal(await page.evaluate(p=>document.elementFromPoint(p.x,p.y)?.id,p),'view');return p;};let previousColour='Red',saved;
    for(const item of samples){
     if(item.colour!==previousColour){await colour(item.colour);await driver.download('colour-selected');previousColour=item.colour;}
     const first=await point(item.samples[0]);await page.mouse.move(first.x,first.y);await page.mouse.down();for(const source of item.samples.slice(1)){const p=await point(source);await page.mouse.move(p.x,p.y);}await page.mouse.up();await driver.record({action:'native-calligraphy-path',label:item.label,colour:item.colour,points:item.points,samples:item.samples});saved=await driver.download(item.label);
    }
    await driver.download('completed','png');await driver.snapshot('completed');
    for(const item of [...samples].reverse()){await page.locator('#undoBtn').click();await driver.download(item.label+'-undone');}for(const item of samples){await page.locator('#view').press('Control+Shift+z');await driver.download(item.label+'-redone');}
    const inputs=await page.evaluate(()=>window.__calligraphyInput);await fs.writeFile(path.join(folder,'native-input.json'),JSON.stringify(inputs,null,2)+'\\n');assert.equal(inputs.filter(e=>e.type==='pointerdown').length,samples.length);assert.equal(inputs.filter(e=>e.type==='pointerup').length,samples.length);assert(inputs.every(e=>e.trusted&&e.pointerType==='mouse'));
    const fresh=await create(width,height,path.join(folder,'fresh'));try{await fresh.driver.open(saved,'project');await pair(fresh.driver,'reopened');}finally{await fresh.context.close();}report.phases??=[];report.phases.push({row:row.id,viewport:row.viewport,phase,paths:paths.map(({label,points,colour})=>({label,points,colour})),paper_view_preparation:preparation});
   }catch(error){await driver.snapshot('failure').catch(()=>{});throw error;}finally{await context.close();}
  }
 }
 report.status=report.errors.length?'Fail':'Pass';""")
target.write_text(text,encoding='utf-8');print('Created actual calligraphy boundary/direction/short-sharp runner.')
