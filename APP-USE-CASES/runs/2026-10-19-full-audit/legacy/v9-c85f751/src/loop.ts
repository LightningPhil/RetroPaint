import { clearConfirmationOpen } from './clear-confirmation';
import { tickDrips, tickHole, tickSqueegee } from './effects';
import { inputActive,tickSpray } from './input';
import { renderOverlay } from './overlay';
import { paintFrame } from './paint';
import { motorOn,tickMotor } from './spiro';
import { updateBelt } from './ui';
import { updateLayerThumbnails } from './layer-ui';
import { photoEditing } from './photo-preview';
import { invalidatePhotoRenders } from './photo-render';
import { drips, isBusy } from './effects';
import { renderWorkspaceOverlay } from './workspace-overlay';
import { updateWorkspaceUi } from './workspace-ui';
import { invalidatePicture,pictureRevision } from './render-state';
import { bus } from './bus';
import { activeLayerId,currentLive,layers } from './layers';
import { liveAnimated } from './live';
import { objectAnimated } from './object-scene';
import { getPending } from './fill';
import { getPreview } from './preview';
import { state } from './state';

export function visibleAnimation():boolean {return layers.some(layer=>layer.visible&&(liveAnimated(layer.id===activeLayerId?currentLive():layer.live)||layer.objects?.some(objectAnimated)));}
function overlayKey():string {
  return JSON.stringify([state.tool,state.cursor,state.paperScale,state.brushWidth,state.opacity,state.applicator,state.ink,state.neonTint,state.sparkleTint,state.symmetry,state.symmetryMask,state.symmetrySlice,state.choosingSlice,state.spiro,state.stampId,state.stampScale,state.stampSpin,state.stampFlipH,state.stampFlipV,state.pixelGrid,state.rulers,state.poly.length,state.poly.at(-1),document.getElementById('canvasSlot')?.classList.contains('moving-paper')]);
}

export function startLoop(): void {
  let last = performance.now(),painted=-1,overlay='';
  for(const event of ['layers','history','selection','objects','photo-update','photo-end','text','text-anchor','tool-request','settle-input'])bus.addEventListener(event,invalidatePicture);
  for(const event of ['input','change','click','keydown','document-frame','canvas-size'])document.addEventListener(event,invalidatePicture,{capture:true});
  document.addEventListener('visibilitychange',invalidatePicture);
  const frame = (now: number) => {
    const dt = Math.min(50, now - last);
    last = now;
    if(document.hidden){requestAnimationFrame(frame);return;}
    if(state.cad.open){requestAnimationFrame(frame);return;}
    const inMotion=Boolean(inputActive()||isBusy()||drips.length||motorOn());
    if (!clearConfirmationOpen() && !photoEditing) {
      if(drips.length||isBusy())invalidatePhotoRenders();
      tickSqueegee(dt);
      tickHole(dt);
      tickDrips(dt);
      tickSpray();
      tickMotor(now);
    }
    const animated=visibleAnimation()||Boolean(getPending())||Boolean(state.liveArmed&&(getPreview()||state.poly.length)),revision=pictureRevision(),repaint=painted!==revision||inMotion||animated;
    if(repaint){paintFrame(now);painted=revision;}
    const key=overlayKey();if(repaint||key!==overlay){renderOverlay();overlay=key;}
    renderWorkspaceOverlay(now);
    updateWorkspaceUi();
    updateBelt(now);
    updateLayerThumbnails(now);
    requestAnimationFrame(frame);
  };
  requestAnimationFrame(frame);
}
