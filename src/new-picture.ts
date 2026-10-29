interface NewPictureActions {
  allowed: () => boolean;
  size: () => [number, number];
  validate: (width: number, height: number) => void;
  create: (width: number, height: number) => void;
  created: () => void;
}

/** Keep the existing document untouched until valid dimensions are accepted. */
export function bindNewPicture(trigger: HTMLButtonElement, actions: NewPictureActions): HTMLDialogElement {
  const dialog = document.createElement('dialog');
  dialog.id = 'newPictureDialog';
  dialog.setAttribute('aria-labelledby', 'newPictureTitle');
  dialog.setAttribute('aria-describedby', 'newPictureLimits');
  dialog.innerHTML = `<form novalidate>
    <h2 id="newPictureTitle">New picture</h2>
    <p id="newPictureLimits">Choose a whole-pixel width and height between 1 and 4096. Your current picture stays until you create the new one.</p>
    <div class="new-picture-dimensions">
      <label>Width <input id="newPictureWidth" type="number" min="1" max="4096" step="1" inputmode="numeric" required autofocus aria-describedby="newPictureLimits newPictureError"></label>
      <label>Height <input id="newPictureHeight" type="number" min="1" max="4096" step="1" inputmode="numeric" required aria-describedby="newPictureLimits newPictureError"></label>
    </div>
    <p id="newPictureError" role="alert" hidden></p>
    <footer><button type="button" class="choice" id="newPictureCancel">Cancel</button><button type="submit" class="action-btn" id="newPictureCreate">Create picture</button></footer>
  </form>`;
  const form = dialog.querySelector<HTMLFormElement>('form')!;
  const width = dialog.querySelector<HTMLInputElement>('#newPictureWidth')!;
  const height = dialog.querySelector<HTMLInputElement>('#newPictureHeight')!;
  const error = dialog.querySelector<HTMLElement>('#newPictureError')!;
  trigger.setAttribute('aria-haspopup', 'dialog');
  trigger.setAttribute('aria-controls', dialog.id);
  trigger.addEventListener('click', () => {
    if (!actions.allowed() || dialog.open) return;
    [width.value, height.value] = actions.size().map(String);
    error.textContent = ''; error.hidden = true;
    dialog.showModal();
  });
  dialog.querySelector('#newPictureCancel')!.addEventListener('click', () => dialog.close());
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (!actions.allowed()) return;
    try {
      const w = Number(width.value), h = Number(height.value);
      actions.validate(w, h);
      actions.create(w, h);
      dialog.close();
      actions.created();
    } catch (reason) {
      error.textContent = reason instanceof Error ? reason.message : String(reason);
      error.hidden = false;
      form.querySelector<HTMLInputElement>('input:invalid')?.focus();
    }
  });
  document.body.append(dialog);
  return dialog;
}
