import { bus, emit } from './bus';
import { editable, message, settle } from './editor';
import { state } from './state';
import { advancedEnabled } from './advanced-mode';

let loading = false;
export function initCadLaunch(): void {
  const open = async () => {
    if(!advancedEnabled()){message('Switch to Advanced mode in More to edit 3D. Your model stays intact.');return;}
    if (loading || state.cad.open || !editable()) return;
    loading = true; const button = document.getElementById('openCad') as HTMLButtonElement; button.disabled = true;
    button.setAttribute('aria-busy', 'true');
    try { settle(); emit('close-options'); emit('close-photo'); const cad = await import('./cad-ui'); if(advancedEnabled())await cad.openCad(); }
    catch (error) { message(error instanceof Error ? error.message : 'Could not open the 3D workshop.'); }
    finally { loading = false; button.disabled = !advancedEnabled(); button.removeAttribute('aria-busy'); }
  };
  document.getElementById('openCad')!.addEventListener('click', () => void open());
  bus.addEventListener('open-cad', () => void open());
}
