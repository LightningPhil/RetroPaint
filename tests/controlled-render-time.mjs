// Only controls the browser's render timestamps for reproducible animated-art
// comparisons. Timers, Date, DOM input and the application code stay intact.
// Never use a fixed value as evidence of real elapsed age or performance.
export function controlledRenderClock(){
 const nativeNow=performance.now.bind(performance),nativeFrame=requestAnimationFrame.bind(window);
 window.__acceptanceRenderTime=null;
 Object.defineProperty(performance,'now',{configurable:true,value:()=>window.__acceptanceRenderTime??nativeNow()});
 window.requestAnimationFrame=callback=>nativeFrame(now=>callback(window.__acceptanceRenderTime??now));
}
