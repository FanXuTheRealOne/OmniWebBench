# OmniWebBench overview design QA

## Evidence

- Source visual: `/var/folders/96/nks84w25541blh3jdpxsbmfh0000gn/T/clipboard-2026-08-11-182002-EA66CAD9.png` (414 × 318)
- Generated hero asset: `docs/assets/matisse-botanical.jpg` (1774 × 887)
- Desktop implementation: `docs/qa/overview-desktop.jpg` (CSS viewport 1200 × 792; Retina capture 2400 × 1584)
- Quick-start state: `docs/qa/quickstart-desktop.jpg` (1200 × 792)
- Coding/Debug state: `docs/qa/debug-desktop.jpg` (1200 × 792)
- Mobile implementation: `docs/qa/overview-mobile.jpg` (390 × 844)
- Combined source/implementation comparison: `docs/qa/source-implementation-comparison.jpg` (1800 × 792)
- Browser recording: `/Users/xufan/.config/browser-harness/agent-workspace/recordings/omniwebbench-matisse-verification`

## Comparison result

The implementation carries over the source image's cut-paper botanical vocabulary, warm paper ground, irregular leaf silhouettes, ultramarine/black/cyan/red/orange/green palette, and dense edge composition. It translates those traits into an editorial benchmark page instead of copying the reference as a literal layout. The hero uses a real generated raster asset; no CSS or SVG illustration substitutes are present.

## QA passes

- Typography: hierarchy remains legible at 1200, 768, and 390 CSS pixels. The hero line breaks are explicit, preventing an orphaned final character.
- Spacing/layout: desktop sections, guide cards, task grid, debug cards, and filters retain clear grouping. Grid items use zero-minimum tracks so long command content cannot expand the mobile page.
- Viewport resilience: measured horizontal overflow is 0 px at 1200, 768, and 390 CSS pixels.
- Color/accessibility: orange status and copy controls use black text; highlighted rules use black text on lime. Native buttons, inputs, selects, summaries, and links remain keyboard reachable.
- Imagery: the hero asset loads successfully and retains its intended 2:1 crop without stretching. The paper texture and leaf density remain visible at desktop and mobile sizes.
- Copy/content: the page distinguishes the current 100 runnable tests from the 1,000-task roadmap and provides concrete clone, validate, fixture, adapter, scoring, report, Debug, and FAQ instructions.
- States/interactions: copy feedback changes to `已复制`; track filtering returns exactly 20 Coding/Debug tasks; FAQ disclosure controls, profile tabs, anchors, search, and filters are wired.

## Findings

- P0: none.
- P1: none.
- P2: none.
- P3: on mobile, the title intentionally overlaps the denser botanical crop. The contrast remains readable, and the overlap preserves the reference's collage character rather than introducing a generic card overlay.

## Verification

- `ruff check .`: passed
- `pytest -q`: 13 passed
- `scripts/audit_benchmark.py`: status `ok`, 100 tasks, 41 capabilities, 5 profiles, 6 tracks
- Task pack SHA-256: `ea1eadd0d863ffd2811e8ead2161034db05a7819433c655f136f0b71c6750fda`

passed
