# Landscape studio handoff

This is a planning handoff, not an implemented feature. The conversation explicitly began as research and planning. The checkout already contained extensive uncommitted changes; preserve them.

## Intended experience

- An artist-led VistaPro/Bryce-inspired landscape studio integrated with RetroPaint, running entirely in the browser on static GitHub Pages.
- Procedural mountains, vegetation, oceans and independent lakes, with rivers and erosion; editable CAD objects and reflective/glass materials in the same scene.
- Progressive ray-traced rendering with genuine output up to 4096 pixels on the long edge, including UHD 3840 × 2160.
- Initial camera: thin-lens depth of field with focal length, aperture and click-to-focus. Keep camera ray generation replaceable for a later multi-element photographic lens engine.
- Initial atmosphere: blue distance haze and low-lying, potentially patchy mist; final reflections and transmission should see the same atmosphere.
- A beautiful, approachable creative workflow, presets and direct manipulation, with deeper controls available without overwhelming the artist.

## Existing foundations

Three.js 0.186.1 is already installed. CAD recipes, millimetre units, geometry workers, camera views and paint-layer integration exist in `src/cad-model.ts`, `src/cad-engine.ts`, `src/cad-viewport.ts` and `src/project.ts`. The CAD viewport currently uses WebGLRenderer and fixed MeshStandardMaterial settings. The project loader accepts versions through 13. CAD uses Z-up; define an explicit scale conversion between CAD millimetres and landscape metres.

## Decisions to investigate

1. Qualify `three-gpu-pathtracer` against glass, terrain, reflections, fog, depth of field, dense instancing, progressive output and 4K memory. Its 0.0.28 release requires Three.js r187; upgrade and regression-test the existing CAD first. Verify the selected release's actual fog and camera features.
2. Compare artist-controlled uplift/stream-power terrain and multi-scale erosion against alternatives using matched seeds and resolutions. The SIGGRAPH 2024 MultiScaleErosion reference is MIT licensed, but uses desktop OpenGL compute and requires a WebGPU port: https://github.com/H-Schott/MultiScaleErosion. TerrainX is a BSD-licensed WebGPU stream-power reference: https://github.com/GPU-Gang/WebGPU-Erosion-Simulation.
3. Establish a versioned scene document separating source recipes from evaluated fields, meshes, caches and renderer state. Include stable independent seeds, edit ordering, masks, asset links, camera, atmosphere, materials and snapshots where needed for reliable reopening.
4. Keep terrain, water and CAD objects in one physical 3D scene so reflection and shadows work across them; define how the rendered result composes with existing paint layers. Decide linked versus frozen CAD assets.
5. Model water bodies and drainage separately from visible terrain. Priority-Flood is a candidate for drainage analysis; preserve artist-created closed basins and separately controlled lake levels.
6. Plan coarse-to-fine erosion, boundary handling, shared-edge terrain meshes, reproducible populations, GPU memory budgets, cancellation, asynchronous BVH rebuilds and device fallback. Avoid assuming SharedArrayBuffer or cross-origin isolation on GitHub Pages.
7. Verify actual native 4K output, colour management, saved-scene fidelity, tiled export and mist/glass/reflection interactions on representative devices. Define measured targets after benchmarking.

## Current audit

- `npm run build` passed on the existing checkout. Vite reports browser externalization warnings for dependencies and a large CAD chunk; these are observations, not confirmed failures.
- No landscape, terrain or erosion files were found by a filename search. This does not establish that every possible related implementation is absent.
- The existing working tree was already modified; do not reset, overwrite or attribute those changes to this task.
