# Tests: brandwright-capture

Test runs for [SKILL.md](SKILL.md). Cases live in `evals/evals.json` (runnable copies in the repository's root `evals/`). A test passes on evidence (a tool call in the trace, a file, a marker), never on the transcript's claim. Entry shape: `### T-YYYYMMDD-n · date · harness · env · passed/total`, newest first. Budget 150 lines. Protocol: [MAINTENANCE.md](MAINTENANCE.md).

## Runs

### T-20261015-1 · 2026-10-15 · real run and unittest · Windows 11, Python 3.14, Playwright with Edge · passed
- Live capture of a public government site (main site, 10 pages with a crawl; its design-system site, 12 pages), desktop and mobile, through `--channel msedge`: 44 page views, consent banner hidden, 7-21 components a page.
- `tokens`: the site's own brand variables came through (brand colour, text, link and focus colours), `@font-face` for its typeface, and a `.bw-button-primary` that matched the real green start button.
- `prep`: 569 candidates to 105 kept (dedupe, caps); brand 90, sites 53 and 52. `caption` on a Mac's Ollama `gemma4:26b`: content-and-layout captions with quoted labels and no style words, 15-60 s each.
- Smoke test on the fictional fixture site: masks (e-mail, phone, typed values), banner hidden, tokens, render, prep.
- Failures fixed the same day: STYLE_WORDS returned tuples and crashed `caption` after 26 pictures (PR #1); the same button text kept four times (same-text dedupe added); tiles crowded out components (tile cap 40 to 24); crawls wandered into cookie pages (`SKIP_BORING`).
- led to: L-001, C-20261015-2

