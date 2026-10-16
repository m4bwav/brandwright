# Tests: brandwright-capture

Test runs for [SKILL.md](SKILL.md). Cases live in `evals/evals.json` (runnable copies in the repository's root `evals/`). A failure that taught something is a lesson in [LEARNINGS.md](LEARNINGS.md); a fix it caused is logged in [CHANGELOG.md](CHANGELOG.md) with `because: T-...`; research it triggered is in [RESEARCH.md](RESEARCH.md). A test passes on evidence (a tool call in the trace, a file, a marker), never on the transcript's claim. Entry shape: `### T-YYYYMMDD-n · date · harness · env · passed/total`, newest first. Budget 150 lines. Protocol: [MAINTENANCE.md](MAINTENANCE.md).

## Runs

### T-20261016-2 · 2026-10-16 · work-machine dry run · Windows 11, fresh clone of v0.1.0, new venv with only `pip install playwright` (125 MB), Edge · passed with a finding
- `doctor` named what each optional piece unlocks (Pillow for prep, score and sheet). `new`, then `capture --site www <home> --crawl 3 --channel msedge`: 4 pages, 8 views in 32 s with no browser download. `tokens` without Pillow: tokens.json, brand.css and tokens.md in 0.2 s (palette.png skipped).
- Finding: the home and browse pages had no call-to-action, so `.bw-button-primary` came from an unstyled browser-default button. After the fix, `tokens` said so; one more capture of a start page gave the real green button (L-002).
- led to: L-002, C-20261016-1

### T-20261016-1 · 2026-10-16 · claude plugin eval (1 run a case, with and without the plugin) · Windows 11, Claude Code · 2/2 run, action-3 not run
- trigger-3 fired `brandwright-capture` with the plugin and not without; decoy-4 (a bug-report screenshot) did not fire it.
- Action case action-3 was not run: on Windows the eval runner refuses any case granted a shell tool because it has no sandbox there ("sandbox required but unavailable"). Run it on macOS or Linux.
- Cost about $1.90 for all 11 trigger and decoy cases, both arms.

### T-20261015-1 · 2026-10-15 · real run and unittest · Windows 11, Python 3.14, Playwright with Edge · passed
- Live capture of a public government site (main site, 10 pages with a crawl; its design-system site, 12 pages), desktop and mobile, through `--channel msedge`: 44 page views, consent banner hidden, 7-21 components a page.
- `tokens`: the site's own brand variables came through (brand colour, text, link and focus colours), `@font-face` for its typeface, and a `.bw-button-primary` that matched the real green start button.
- `prep`: 569 candidates to 105 kept (dedupe, caps); brand 90, sites 53 and 52. `caption` on a Mac's Ollama `gemma4:26b`: content-and-layout captions with quoted labels and no style words, 15-60 s each.
- Smoke test on the fictional fixture site: masks (e-mail, phone, typed values), banner hidden, tokens, render, prep.
- Failures fixed the same day: STYLE_WORDS returned tuples and crashed `caption` after 26 pictures (PR #1); the same button text kept four times (same-text dedupe added); tiles crowded out components (tile cap 40 to 24); crawls wandered into cookie pages (`SKIP_BORING`).
- led to: L-001, C-20261015-2

