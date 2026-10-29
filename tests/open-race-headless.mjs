// Exercise the real file inputs while deliberately pausing asynchronous reads.
import { chromium } from 'playwright';
import { createServer } from 'vite';
import assert from 'node:assert/strict';
import path from 'node:path';

const server = await createServer({ server: { host: '127.0.0.1', port: 0 } });
await server.listen();
const browser = await chromium.launch({ channel: 'chrome', headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  await page.addInitScript(() => {
    const original = File.prototype.text;
    File.prototype.text = async function () {
      if (this.name === 'delayed.retropaint') {
        window.openReadStarted = true;
        await new Promise(resolve => { window.releaseOpenRead = resolve; });
      }
      return original.call(this);
    };
  });
  await page.goto(`http://127.0.0.1:${server.httpServer.address().port}/`);
  const fixture = path.resolve('APP-USE-CASES/runs/2026-10-19-full-audit/backups/artwork-before-acceptance-audit.retropaint');
  const fs = await import('node:fs/promises');
  const bytes = await fs.readFile(fixture);
  await page.locator('#projectInput').setInputFiles({ name: 'delayed.retropaint', mimeType: 'application/json', buffer: bytes });
  await page.waitForFunction(() => window.openReadStarted);
  const view = page.locator('#view');
  const before = await view.evaluate(el => [el.width, el.height]);
  const box = await view.boundingBox();
  await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  const painted = await view.evaluate(el => el.toDataURL());
  await page.evaluate(() => window.releaseOpenRead());
  await page.getByRole('status').filter({ hasText: 'picture changed while the file was opening' }).waitFor();
  assert.deepEqual(await view.evaluate(el => [el.width, el.height]), before);
  assert.equal(await view.evaluate(el => el.toDataURL()), painted);
  // A normal retry remains possible after the stale operation is rejected.
  await page.locator('#projectInput').setInputFiles({ name: 'retry.retropaint', mimeType: 'application/json', buffer: bytes });
  await page.getByRole('status').filter({ hasText: 'Project opened with editable pieces' }).waitFor();
  console.log('PASS delayed project open preserves new work and allows retry');
} finally {
  await browser.close();
  await server.close();
}
