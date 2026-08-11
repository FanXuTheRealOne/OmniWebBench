# OmniWebBench GitHub README design QA

**Source visual truth**

- `/var/folders/96/nks84w25541blh3jdpxsbmfh0000gn/T/clipboard-2026-08-11-182002-EA66CAD9.png`
- Source pixels: 414 × 318.
- Intended translation: retain the warm paper, cut-paper plant silhouettes, dense irregular rhythm and blue/black/red/orange/green palette while using GitHub-native Markdown for the repository information architecture.

**Rendered implementation**

- Top-of-README screenshot: `docs/qa/readme-top.jpg`.
- Coding/Debug focused screenshot: `docs/qa/readme-debug.jpg`.
- Live GitHub top screenshot: `docs/qa/readme-live-top.jpg`.
- Live GitHub Debug screenshot: `docs/qa/readme-live-debug.jpg`.
- CSS viewport and screenshot pixels: 1200 × 900, device scale factor 1.
- State: GitHub-style light-theme README rendering, top state and Coding Agent + Browser Debug section.
- Browser recording: `/Users/xufan/.config/browser-harness/agent-workspace/recordings/omniwebbench-readme-final-qa`.

**Full-view comparison evidence**

- Combined source and implementation: `docs/qa/readme-source-comparison.jpg` (1700 × 900).
- The implementation preserves the source's warm paper ground, hand-cut leaf language, high-chroma palette and asymmetrical density in a real raster hero asset. The GitHub-owned content surface remains deliberately clean so the benchmark documentation is readable.

**Focused-region comparison evidence**

- `docs/qa/readme-debug.jpg` verifies the dedicated 20-task Debug section, task ranges, evidence requirements and development flow at readable size.
- A separate typography crop was not required: the top and focused screenshots render the smallest relevant badge, navigation, table and code text at inspectable size.

**Findings**

- P0: none.
- P1: none.
- P2: none.
- P3: none. The local Grip preview showed alert markers as plain text, but the final live GitHub pass confirmed all five admonitions render with GitHub's native Important, Warning and Tip treatments.

**Required fidelity surfaces**

- Fonts and typography: GitHub's native system stack provides a clear repository-document hierarchy. The art reference is translated through imagery instead of forcing a decorative font into long technical copy.
- Spacing and layout rhythm: hero, centered identity block, badge row, navigation, overview tables and long-form sections have distinct vertical groups. No desktop horizontal overflow was measured.
- Colors and visual tokens: badges reuse ultramarine, cyan, red, orange and green from the source; black label cells maintain strong contrast.
- Image quality and asset fidelity: `assets/hero.png` is a 2172 × 678 real raster crop; `assets/matisse-divider.png` is 1800 × 233; both load at full natural width with no stretching or placeholder substitution. `assets/social-preview.png` is prepared at GitHub's 1280 × 640 social-card size.
- Copy and content: the README clearly separates the current 100 runnable public tasks from the 1,000-task roadmap, explains six run steps, labels the evaluator trust boundary, and gives Coding Agents an explicit observe/diagnose/patch/rerun/verify contract.
- Accessibility: all decorative images have descriptive alt text; headings, links, tables, code blocks and disclosure elements use GitHub-native semantics. Badge colors are paired with text labels rather than color-only meaning.

**Interaction and load checks**

- 59 links rendered.
- 7 tables and 2 disclosure sections rendered.
- All 7 visible image resources completed with non-zero natural width.
- Desktop document overflow: 0 px.
- No page or asset-load errors were observed during the final browser recording.
- Live repository check: hero natural width 2172 px, README heading present, Debug section present, Five-minute start present, and 5 native GitHub alerts rendered.

**Comparison history**

- Initial focused capture: Debug task IDs wrapped awkwardly at every hyphen in the narrow table column.
- Fix: changed the column to short numeric suffixes and added one explicit `owb-dev-` prefix note below the table.
- Post-fix evidence: `docs/qa/readme-debug.jpg`; task ranges now stay intact and scan cleanly.

**Implementation checklist**

- [x] Replace the generic 3D-tech repository hero with Matisse-inspired raster artwork.
- [x] Add matching badges, top navigation and repository-at-a-glance summaries.
- [x] Expand installation, fixture, adapter, run-bundle, scoring and development-loop instructions.
- [x] Add the dedicated 20-task Coding Agent + Browser Debug section.
- [x] Prepare a 1280 × 640 repository social-preview asset.
- [x] Verify GitHub-style rendering, images, links, tables and desktop overflow.

**Follow-up polish**

- Upload `assets/social-preview.png` in GitHub repository Settings → General → Social preview; this setting is not controlled by repository files.

final result: passed
