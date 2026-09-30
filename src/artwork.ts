/** Age belongs to the current picture, including when Undo restores it. */
export class ArtworkAge {
  private started: number | null = null;
  constructor(private readonly now = () => performance.now()) {}
  markWork(): void { this.started ??= this.now(); }
  reset(): void { this.started = null; }
  snapshot(): number | null { return this.started; }
  restore(started: number | null): void { this.started = started; }
  needsClearConfirmation(): boolean {
    return this.started !== null && this.now() - this.started > 120_000;
  }
}
export const artwork = new ArtworkAge();
