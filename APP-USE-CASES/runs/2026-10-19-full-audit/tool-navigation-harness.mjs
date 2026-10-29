import fs from 'node:fs/promises';
import {root} from './browser-harness.mjs';
export function makeToolNavigator(tab,ui,audit,prefix){
  const checks=[];
  return {checks,
    async open(name){const close=ui.getByRole('button',{name:'Close options',exact:true});if(await close.isVisible())await close.click();await ui.getByRole('button',{name,exact:true}).click();await tab.getAXState({emit:false});},
    async capture(name){
      const close=ui.getByRole('button',{name:'Close options',exact:true});if(await close.isVisible())await close.click();
      await ui.getByRole('button',{name,exact:true}).click();await tab.getAXState({emit:false});
      const row=await ui.locator('body').evaluate(e=>({
        active:[...e.querySelectorAll('#toolBin .tool-btn.active')].map(n=>n.querySelector('.tool-label')?.textContent||n.textContent.trim()),
        workspace:e.querySelector('#workspaceToolName').textContent,size:e.querySelector('#brushSize').value,strength:e.querySelector('#opacity').value,
        redoDisabled:e.querySelector('#workspaceRedo').disabled,view:e.querySelector('#view').getBoundingClientRect().toJSON(),
        pressed:[...e.querySelectorAll('.drawer.open button[aria-pressed="true"],.drawer.open button.active,.drawer.open button.selected')].filter(n=>n.getClientRects().length).map(n=>n.getAttribute('aria-label')||n.textContent.trim()),
        fields:[...e.querySelectorAll('.drawer.open input,.drawer.open select')].filter(n=>n.getClientRects().length).map(n=>({id:n.id,value:n.value})),
        inkPreview:e.querySelector('#currentInk')?.getAttribute('style')??null
      }));
      if(!row.active.includes(name))throw new Error(name+' has no active indication');
      if(name!=='Symmetry'&&row.workspace!==name)throw new Error(name+' has no workspace name');
      if(row.redoDisabled)throw new Error(name+' discarded Redo');
      checks.push({name,...row});await audit.observe(prefix+'-'+name.toLowerCase().replaceAll(' ','-'));
      await fs.writeFile(root+'/evidence/'+prefix+'-controls.json',JSON.stringify(checks,null,2));
      if(await close.isVisible())await close.click();await tab.getAXState({emit:false});return {name,choice:row.pressed};
    }
  };
}
