import { view, W, H } from './canvas';
import { state } from './state';
import { displayFrame } from './document-frame';

let surface: HTMLCanvasElement | undefined, last = '';

/** Screen-resolution guides, clipped to the visible paper, never to the artwork. */
export function renderViewGuides(): void {
  if (!state.pixelGrid && !state.rulers) { if (surface) surface.hidden = true; last = ''; return; }
  const slot = document.getElementById('canvasSlot');
  if (!slot || !view.parentElement) return;
  const paper = view.getBoundingClientRect(), area = slot.getBoundingClientRect(), stage = view.parentElement.getBoundingClientRect();
  const left = Math.max(0, paper.left, area.left, stage.left), top = Math.max(0, paper.top, area.top, stage.top);
  const right = Math.min(innerWidth, paper.right, area.right, stage.right), bottom = Math.min(innerHeight, paper.bottom, area.bottom, stage.bottom);
  if (right <= left || bottom <= top) { if (surface) surface.hidden = true; last = ''; return; }
  if (!surface) {
    surface = document.createElement('canvas'); surface.id = 'paperGuides'; surface.setAttribute('aria-hidden', 'true');
    surface.style.cssText = 'position:absolute;inset:auto;pointer-events:none;max-width:none;border:0';
  }
  if (surface.parentElement !== view.parentElement) view.after(surface);
  const ratio = devicePixelRatio || 1;
  const key = JSON.stringify([paper.x,paper.y,paper.width,paper.height,left,top,right,bottom,W,H,ratio,state.pixelGrid,state.rulers]);
  surface.hidden = false;
  if (key === last) return;
  last = key;
  const sx = paper.width / W, sy = paper.height / H, scale = Math.min(sx, sy);
  const x0 = (left-paper.left)/sx, y0 = (top-paper.top)/sy, x1 = (right-paper.left)/sx, y1 = (bottom-paper.top)/sy;
  // A cropped child of the transformed stage stays aligned while its backing
  // store is bounded by the viewport, even at the maximum paper zoom.
  const frame = displayFrame(W,H);
  surface.style.left = `${(x0-frame.x)/frame.width*100}%`; surface.style.top = `${(y0-frame.y)/frame.height*100}%`;
  surface.style.width = `${(x1-x0)/frame.width*100}%`; surface.style.height = `${(y1-y0)/frame.height*100}%`;
  surface.width = Math.max(1,Math.ceil((right-left)*ratio)); surface.height = Math.max(1,Math.ceil((bottom-top)*ratio));
  const ctx = surface.getContext('2d')!;
  const ax = surface.width/(x1-x0), ay = surface.height/(y1-y0);
  ctx.setTransform(ax,0,0,ay,-x0*ax,-y0*ay);
  if (state.pixelGrid && scale >= 6) {
    ctx.strokeStyle = '#26304730'; ctx.lineWidth = 1/sx; ctx.beginPath();
    for (let x=Math.ceil(x0);x<=x1;x++) { ctx.moveTo(x,y0); ctx.lineTo(x,y1); } ctx.stroke();
    ctx.lineWidth = 1/sy; ctx.beginPath();
    for (let y=Math.ceil(y0);y<=y1;y++) { ctx.moveTo(x0,y); ctx.lineTo(x1,y); } ctx.stroke();
  }
  if (state.rulers) {
    const size = 18/scale, step = Math.max(1,10**Math.ceil(Math.log10(45/scale)));
    ctx.fillStyle = '#fffdf7e8'; ctx.fillRect(0,0,W,size); ctx.fillRect(0,0,size,H);
    ctx.fillStyle = '#263047'; ctx.font = `${10/scale}px Trebuchet MS`; ctx.textBaseline = 'top';
    if (y0<size) for (let x=Math.max(step,Math.ceil(x0/step)*step);x<Math.min(W,x1);x+=step) ctx.fillText(String(x),x,2/scale);
    if (x0<size) for (let y=Math.max(step,Math.ceil(y0/step)*step);y<Math.min(H,y1);y+=step) { ctx.save(); ctx.translate(2/scale,y); ctx.rotate(-Math.PI/2); ctx.fillText(String(y),0,0); ctx.restore(); }
  }
}
