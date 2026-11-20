# Changelog: brandwright

Every change to [SKILL.md](SKILL.md) and its companions, newest first, each with the reason (`R-` findings in [RESEARCH.md](RESEARCH.md), `L-` lessons in [LEARNINGS.md](LEARNINGS.md), `T-` runs in [TESTS.md](TESTS.md)). Protocol: [MAINTENANCE.md](MAINTENANCE.md).

### C-20261119-1 · 2026-11-19 · guideline fields in brand.json and `check`
- because: books round 6 (Wheeler, Designing Brand Identity pp. 150-159, 204; Bringhurst 3.3, 6.5; Villagomez ch. 6)
- files: scripts/bw.py (`check`, `lint_brand`, `brand_palette`), references/kit.md, tests/test_bw.py
- Optional fields `signatures`, `clear_space`, `min_size_px`, `backgrounds`, `colors` (name, hex, role), `type` (role, family, web licence, real small caps, figures, bold), `misuse`, `chart_colors`, `marks_to_keep`, `media`. Old kits pass unchanged. `check` lints them and, with `--html`, fails on placeholder text. `score` also counts the named colours and works without tokens.json when they exist.

### C-20261021-1 · 2026-10-21 · CLI under the line budget; one protocol copy for the plugin
- because: owner's choice on 2026-10-21 (cut back under the size budget rather than raise it); the CLI row was yellow at 2,072 of 2,000 lines and the skills folder at 251 of 250 KB
- files: scripts/bw.py, scripts/bw_browser.py, scripts/bw_comfy.py; MAINTENANCE.md is now the one full copy the sibling skills point to
- 81 lines out with no change in behaviour: a `kit_cmd` parser helper, `finish` for gen and ref, `launch_kw` and `contextlib.suppress` in the browser module, comprehensions in place of append loops. Help pages identical; tests unchanged; old and new scripts compared on 50 commands with `ai-docs/notes/cli-diff-run.py`.

### C-20261015-1 · 2026-10-15 · Created
- because: user request (brand and sub-site LoRAs for mock-ups of new components, usable at work), R-20261015-1, R-20261015-2
- files: SKILL.md, references/, evals/evals.json
- First version.
