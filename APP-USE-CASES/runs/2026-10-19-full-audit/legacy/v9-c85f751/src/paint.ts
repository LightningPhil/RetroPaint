import { viewCtx } from './canvas';
import { drawPending } from './fill';
import { renderLayers } from './layers';
import { renderSelection } from './selection';
import { renderTextPreview } from './text-tool';

export function paintFrame(now: number): void {
  renderLayers(viewCtx, now, ctx => { drawPending(ctx, now); renderSelection(ctx); renderTextPreview(ctx); });
}
