# Tests: brandwright

Test runs for [SKILL.md](SKILL.md). Cases live in `evals/evals.json` (runnable copies in the repository's root `evals/`). A failure that taught something is a lesson in [LEARNINGS.md](LEARNINGS.md); a fix it caused is logged in [CHANGELOG.md](CHANGELOG.md) with `because: T-...`; research it triggered is in [RESEARCH.md](RESEARCH.md). A test passes on evidence (a tool call in the trace, a file, a marker), never on the transcript's claim. Entry shape: `### T-YYYYMMDD-n · date · harness · env · passed/total`, newest first. Budget 150 lines. Protocol: [MAINTENANCE.md](MAINTENANCE.md).

## Runs

### T-20261016-1 · 2026-10-16 · claude plugin eval (1 run a case, with and without the plugin) · Windows 11, Claude Code · 5/5 run, action-1 not run
- trigger-1, trigger-2 fired `brandwright` with the plugin and nothing fired without it; decoy-1 (a dog LoRA), decoy-2 (a bakery logo) and decoy-3 (a Playwright test) did not fire it.
- Action case action-1 was not run: on Windows the eval runner refuses any case granted a shell tool because it has no sandbox there ("sandbox required but unavailable"). Run it on macOS or Linux.
- Cost about $1.90 for all 11 trigger and decoy cases, both arms.
