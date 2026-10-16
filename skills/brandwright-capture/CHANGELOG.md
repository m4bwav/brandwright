# Changelog: brandwright-capture

Every change to [SKILL.md](SKILL.md) and its companions, newest first, each with the reason (`R-` findings in [RESEARCH.md](RESEARCH.md), `L-` lessons in [LEARNINGS.md](LEARNINGS.md), `T-` runs in [TESTS.md](TESTS.md)). Protocol: [MAINTENANCE.md](MAINTENANCE.md).

### C-20261016-1 · 2026-10-16 · no browser-default primary button; say when the CTA is missing
- because: T-20261016-2, L-002
- files: ../brandwright/scripts/bw.py (recipe_set, cmd_tokens), SKILL.md (Step 1, Step 3), ../../tests/test_bw.py
- `recipe_set` skips coloured buttons at Chromium's unstyled 13.3333px size; `tokens` prints a hint when no primary button was captured; the skill asks for a page with the main button in the capture.

### C-20261015-2 · 2026-10-15 · fixes from the first real capture
- because: T-20261015-1, L-001
- files: ../brandwright/scripts/bw.py (prep, recipe_set, cmd_caption), ../brandwright/scripts/bw_browser.py (SKIP_BORING, hex colours)
- Primary-button recipe; monospace fonts kept out of `--bw-font`; recipe fonts that are not a main family dropped; same-text dedupe; tile cap 24; cookie, privacy and sitemap pages skipped in crawls; colours read through a canvas; the caption crash fixed and progress saved per picture.

### C-20261015-1 · 2026-10-15 · Created
- because: user request (brand and sub-site LoRAs for mock-ups of new components, usable at work), R-20261015-1
- files: SKILL.md, references/, evals/evals.json
- First version.
