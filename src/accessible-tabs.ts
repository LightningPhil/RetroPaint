/** One predictable keyboard pattern for tool categories and settings tabs. */
export function initAccessibleTabs():void {
  const tabs=(list:Element)=>[...list.querySelectorAll<HTMLButtonElement>('[role=tab]')].filter(tab=>!tab.disabled&&!tab.hidden);
  const sync=(list:Element)=>{const items=tabs(list),active=items.find(tab=>tab.getAttribute('aria-selected')==='true')??items[0];for(const tab of items)tab.tabIndex=tab===active?0:-1;};
  document.querySelectorAll('[role=tablist]').forEach(sync);
  document.addEventListener('keydown',event=>{
    if(event.ctrlKey||event.metaKey||event.altKey)return;
    const target=event.target instanceof Element?event.target.closest<HTMLButtonElement>('[role=tab]'):null,list=target?.closest('[role=tablist]');if(!target||!list)return;
    const items=tabs(list).filter(tab=>tab.getClientRects().length),index=items.indexOf(target);let next:number;
    if(event.key==='ArrowRight')next=(index+1)%items.length;else if(event.key==='ArrowLeft')next=(index-1+items.length)%items.length;else if(event.key==='Home')next=0;else if(event.key==='End')next=items.length-1;else return;
    event.preventDefault();event.stopImmediatePropagation();const tab=items[next];if(tab){tab.click();tab.focus();sync(list);}
  });
  const observer=new MutationObserver(changes=>{const lists=new Set<Element>();for(const change of changes){const list=change.target instanceof Element?change.target.closest('[role=tablist]'):null;if(list)lists.add(list);}lists.forEach(sync);});
  document.querySelectorAll('[role=tablist]').forEach(list=>observer.observe(list,{subtree:true,attributes:true,attributeFilter:['aria-selected','hidden','disabled']}));
}
