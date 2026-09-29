export const bus = new EventTarget();

export function emit(name: string, detail?: unknown): void {
  bus.dispatchEvent(new CustomEvent(name, { detail }));
}
