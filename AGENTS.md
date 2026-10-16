# AGENTS.md

Rules for any AI agent (Claude Code, Copilot, Cursor, Codex, Gemini CLI) working in this repository. `CLAUDE.md` imports this file and `.github/copilot-instructions.md` points here.

## What this is

A cross-agent plugin with four skills for on-brand UI mock-ups. `skills/brandwright/` is the hub (routes, kit contract, myths) and holds the CLI: `scripts/bw.py` (kit, import, tokens, prep, caption, review, train, status, pick, score, sheet), which imports `scripts/bw_browser.py` (Playwright: login, capture, render) and `scripts/bw_comfy.py` (ComfyUI: gen, sweep, ref). `skills/brandwright-capture/` (capture, masks, tokens, dataset, captions), `skills/brandwright-train/` (models, licences, ai-toolkit, modes) and `skills/brandwright-mockup/` (code route, prompts, sweeps, reference route). Each skill carries the evergreen companions (RESEARCH, CHANGELOG, LEARNINGS, TESTS, MAINTENANCE, `evergreen.json`, `evals/evals.json`). Tests in `tests/`; runnable eval cases in the root `evals/` (`claude plugin eval` format); the size budget is `scripts/budget.py`; `scripts/check_public.py` guards the public repository. Research, decisions and the log are under `ai-docs/` (start with `ai-docs/HANDOFF.md`).

## Rules

- The CLI runs on Python 3.10+ on Windows, macOS and Linux with the standard library alone; Playwright (capture, login, render) and Pillow (prep, score, sheet) are optional imports with a clear message when missing. No other dependencies.
- **A kit is the user's company data.** Nothing in this repository may contain a real kit, a screenshot of a real company site, a trained LoRA, a login profile or a caption written from one. Tests use synthetic pictures and the fictional fixture site in `tests/fixtures/site/`. `.gitignore` excludes `kits/` and `*.safetensors`; `bw.py new` writes a `*` `.gitignore` into every kit. Keep both.
- **Never automate a login.** `login` opens a window for the person; nothing in the code types, stores or asks for a password. Crawling is GET-only and skips sign-out, delete and cancel links; keep `SKIP_LINK`.
- Masking stays on by default (`MASK_JS`); `--no-mask` is for test data. Any change to masking needs a check in `tests/smoke_browser.py`.
- Captions never name colours, fonts or style (`STYLE_WORDS` in `bw.py` and the template test keep it so).
- Model and licence facts in the skills carry a date and a source in RESEARCH.md or `ai-docs/research/`. Never call a model "free for commercial use" without the licence name; re-check licences when refreshing (`brandwright-train` is verify-at-use).
- Trainer configs are plain ostris ai-toolkit JSON; field names come from its example configs and `extensions_built_in/diffusion_models/ui.tsx`. Check them against the trainer's current source before changing `MODELS`.
- Every change to the CLI has a test in `tests/test_bw.py`. Run `python tests/test_bw.py`, `python tests/smoke_browser.py` (when Playwright and a browser are present), `python scripts/budget.py` and `python scripts/check_public.py` before committing.
- The skills are evergreen units. Before editing one, read its `evergreen.json`; if `next_due` has passed or `contradiction` is set, say so and refresh after the task. Log every change in that skill's CHANGELOG.md with its reason; lessons go to LEARNINGS.md with a code name.
- A release bumps the version in `.claude-plugin/plugin.json`, `plugin.json`, `VERSION` in `bw.py`, `metadata.version` in every SKILL.md and `version` in every `evergreen.json` together, then tags `vX.Y.Z` and publishes a GitHub Release with the CHANGELOG entry as notes. Releases need the owner's go-ahead.
- The size budget in README.md and `scripts/budget.py` changes only with the owner's agreement. Warn at yellow.
- No top-level `bin/` folder: Cowork refuses to install a plugin that has one.
- Prose people read is checked with the everwrite checker when it is available: zero strong findings.
- This is a public repository. Nothing in it names a person other than the author credit, a machine, an absolute path on someone's machine, a private project, a real company's internal site, or a credential.
- No AI attribution anywhere: no Co-Authored-By trailers, no "generated with" lines in commits, pull requests, releases or files.

## everlast (session knowledge, load on demand)

- `ai-docs/INDEX.md` lists what past sessions learned here (research, decisions, solutions, plans). At the start of a task, scan it and open only the entries whose title or tags match. Read `ai-docs/HANDOFF.md` when continuing unfinished work.
- Before finishing a task that hit a dead end, verified a non-obvious command, made a design choice, or taught you something about the user, record it in `ai-docs/` (solutions, decisions, log) and rewrite `HANDOFF.md` when work is left unfinished. Say "nothing to record" when that is true.
- Anything naming a person, an employer, an internal host or name, or a credential goes to the owner's private notes, never here.
- Link documents with relative markdown links and a typed `Related:` line (`supersedes`, `contradicts`, `builds on`, `see also`). No wikilinks.
