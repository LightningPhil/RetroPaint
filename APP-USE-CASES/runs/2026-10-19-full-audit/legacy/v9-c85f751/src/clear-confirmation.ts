import { artwork, type ArtworkAge } from './artwork';
import { icon, labelIcon } from './icons';

let currentDialog: HTMLDialogElement | null = null;
export function clearConfirmationOpen(): boolean { return currentDialog?.open ?? false; }

export function bindClearConfirmation(trigger: HTMLButtonElement, clear: () => void, age: ArtworkAge = artwork, allowed: () => boolean = () => true): HTMLDialogElement {
  const dialog = document.createElement('dialog');
  dialog.id = 'clearConfirmation';
  currentDialog = dialog;
  dialog.setAttribute('aria-labelledby', 'clearTitle');
  dialog.setAttribute('aria-describedby', 'clearMessage');
  dialog.innerHTML = `<div class="clear-symbols" aria-hidden="true">${icon('clock')}${icon('clear')}</div>
    <h2 id="clearTitle">Clear your picture?</h2>
    <p id="clearMessage">You've been working on this for a while. Are you sure you want to clear it?</p>
    <div class="clear-actions"><button type="button" class="action-btn keep-picture" autofocus>Keep drawing</button>
    <button type="button" class="action-btn clear-picture">Clear picture</button></div>`;
  const keep = dialog.querySelector<HTMLButtonElement>('.keep-picture')!;
  const confirm = dialog.querySelector<HTMLButtonElement>('.clear-picture')!;
  labelIcon(keep, 'marker'); labelIcon(confirm, 'clear');
  keep.addEventListener('click', () => dialog.close());
  confirm.addEventListener('click', () => { dialog.close(); clear(); });
  trigger.addEventListener('click', () => {
    if (!allowed()) return;
    if (age.needsClearConfirmation()) { if (!dialog.open) dialog.showModal(); }
    else clear();
  });
  document.body.append(dialog);
  return dialog;
}
