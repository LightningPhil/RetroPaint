# RetroPaint app use cases and user stories

**349 paired stories and use cases across 18 functional areas.** They describe how the app should behave, informed by its current controls, data formats, rendering paths and existing check code. They are acceptance requirements for later testing, not a report that the app already satisfies them.

Open [BROWSE.html](BROWSE.html) in a browser for searchable cards, or use the chapter links below. [CASE-INDEX.csv](CASE-INDEX.csv) is a sortable spreadsheet index. [catalog.json](catalog.json) holds the complete structured content.

The [current acceptance audit](runs/2026-10-19-full-audit/README.md) contains the verified artwork backup, actual results, failed evidence and fixes. Testing is in progress; the 349 authored cases are not 349 passes.

## Three experience levels

| Level | User and intention | Primary stories |
| --- | --- | ---: |
| L1 | Beginning young artist: make colourful marks, playful patterns and pictures, with obvious ways to recover mistakes. Reading and dexterity may still be developing. | 54 |
| L2 | Adventurous older child: combine drawing, captions, photographs, layers and increasingly deliberate edits; compare results and keep originals. | 164 |
| L3 | Confident maker: an older child, teen or adult who wants exact sizes, reusable pieces, dependable photo recipes, editable 3D designs and valid deliverable files. | 131 |

These are experience levels, not age restrictions, account roles or feature permissions. A child may use L3 tools with help, and an adult may prefer L1 play. Each story has one primary level; the cross level journeys exercise growth between them.

## Start with the right reference

1. Read [Intended behavior and decisions](BEHAVIOR-DECISIONS.md) for source-sensitive rules, current capability boundaries and proposed usability targets.
2. Use [Coverage matrix](COVERAGE-MATRIX.md) for every option family and boundary. One representative option does not close a whole family.
3. Prepare the concrete fixtures in [Test data](TEST-DATA.md). Their definitions are not a claim that the files already exist.
4. Execute using [Testing protocol](TESTING-PROTOCOL.md), and record outcomes in [Execution ledger](EXECUTION-LEDGER.csv).
5. Consult [Source review](SOURCE-REVIEW.md) for the source snapshot and existing check inventory. Existing checks are candidates for reuse, not proof of these stories.

## Functional chapters

| Area | Stories and use cases | Count |
| --- | --- | ---: |
| START | [Getting started and protecting a picture](01-start.md) | 10 |
| PAINT | [Brushes spray smudge and erasing](02-paint.md) | 20 |
| INK | [Colours textures gradients and live ink](03-ink.md) | 19 |
| PLAY | [Shapes symmetry stamps and Spiro](04-play.md) | 22 |
| EDIT | [Selections text and image transformations](05-edit.md) | 24 |
| LAYER | [Layers and mixed picture composition](06-layer.md) | 15 |
| VECTOR | [Editable vector and raster pieces](07-vector.md) | 18 |
| PHOTO | [Photo lab workflow light and looks](08-photo.md) | 19 |
| COLOUR | [Photographic colour balance and curves](09-colour.md) | 18 |
| FINISH | [Photo detail effects geometry and lens corrections](10-finish.md) | 24 |
| FILE | [Files exports projects and local recovery](11-file.md) | 24 |
| ENHANCE | [Larger enhanced image copies](12-enhance.md) | 12 |
| SOLID | [3D workshop basics transforms and layers](13-solid.md) | 22 |
| SKETCH | [3D sketches dimensions constraints and boolean building](14-sketch.md) | 22 |
| FEATURE | [3D history shells edge finishes lofts and sweeps](15-feature.md) | 29 |
| DELIVER | [3D inspection mixed pictures STL import and print preparation](16-deliver.md) | 23 |
| ACCESS | [Responsive input accessibility comfort and resilience](17-access.md) | 18 |
| JOURNEY | [Complete creative journeys across experience levels](18-journey.md) | 10 |

## What completion means

Every story includes a specific workflow, at least three acceptance criteria, an alternative or failure path, a reproducible setup and evidence requirements. Every case also inherits its area contract and the shared testing rules. A case may contain several required variants; its count is one case, not a claim that each variant has already been tested.

**Execution is in progress.** Consult the [current audit](runs/2026-10-19-full-audit/README.md) and [execution ledger](EXECUTION-LEDGER.csv) for tested outcomes and remaining work. The authored catalogue remains the normative specification; its original Not run fields are not live execution results. Component regressions and documentation validation do not establish acceptance passes.

## Scope boundaries

Coverage includes painting and special materials, patterns, selections, captions, transforms, sheets, editable pieces, all photo adjustment families, codecs and files, recovery, enhancement, CAD construction and precision editing, inspection and printing preparation, mixed picture workflows, input, layout, accessibility, comfort and resilience. It includes failure, interruption, cancellation, Undo, persistence and capability denial where relevant.

The app has no account workflow, collaboration service, cloud image upload, camera RAW development, automatic lens profiles, general AI background segmentation, SVG interchange, animated GIF authoring, direct printer control or slicer. Those are not invented as current features. Browser file dialogs, clipboard permissions, font availability and physical printing have explicit external integration conditions.

## Priorities and changes

P0 marks particularly serious loss, corruption, incorrect physical geometry or cancellation risks. P1 is normal expected functionality, including exploratory and usability requirements. These are test planning priorities, not a statement that P1 failures are harmless. Keep stable IDs. Record any approved requirement change with its reason and date; do not rewrite an expected result simply to make an implementation pass.
