import { viewCtx } from './canvas';
import { drawPending } from './fill';
import { renderLayers } from './layers';
import { renderSelection } from './selection';
import { calloutEnabled, renderTextPreview } from './text-tool';

export function paintFrame(now: number): void {
  renderLayers(viewCtx, now, ctx => { drawPending(ctx, now); renderSelection(ctx); if(!calloutEnabled())renderTextPreview(ctx); });
  if(calloutEnabled())renderTextPreview(viewCtx);
}
