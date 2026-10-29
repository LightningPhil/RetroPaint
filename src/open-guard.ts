import { bus } from './bus';

// An open may spend time decoding images or rebuilding CAD. Do not let its
// eventual result replace edits or a newer open made in the meantime.
let revision = 0;
let request = 0;
for (const event of ['history', 'layers', 'document-created', 'document-opened']) {
  bus.addEventListener(event, () => { revision++; });
}
document.addEventListener('document-frame', () => { revision++; });

export function beginOpen(): () => boolean {
  const currentRequest = ++request, currentRevision = revision;
  return () => currentRequest === request && currentRevision === revision;
}

export function requireCurrentOpen(isCurrent: () => boolean): void {
  if (!isCurrent()) throw new Error('The picture changed while the file was opening. Your current work was kept; open the file again to try.');
}
