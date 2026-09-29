# RetroPaint (Dazzle)

A tactile painting toy: chunky tools, live ink, symmetry, stamps, and a spirograph kit.

## Scripts

```bash
npm install
npm run dev      # http://localhost:8080
npm run build    # typecheck + compile to dist/
npm run preview  # serve dist/ on port 8080
```

Requires Node 20+.

## GitHub Pages

Pushes to `main` (or `master`) run `.github/workflows/pages.yml`, which compiles the app and publishes `dist/`. In the repo settings, set **Pages → Build and deployment → Source** to **GitHub Actions**.

The Vite `base` is `./`, so the site works at `https://<user>.github.io/RetroPaint/`.

There is no test workflow. Do not add one.

## Skill slider

The slider in the top-right starts at **1** (brush, bucket, five colors). Move it to **4** to open live ink, the spiro kit, filters, and opacity. The choice is remembered in this browser.
