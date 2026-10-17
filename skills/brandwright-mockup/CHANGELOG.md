# Changelog: brandwright-mockup

Every change to [SKILL.md](SKILL.md) and its companions, newest first, each with the reason (`R-` findings in [RESEARCH.md](RESEARCH.md), `L-` lessons in [LEARNINGS.md](LEARNINGS.md), `T-` runs in [TESTS.md](TESTS.md)). Protocol: [MAINTENANCE.md](MAINTENANCE.md).

### C-20261017-2 · 2026-10-17 · `python3` on macOS and Linux
- because: ../brandwright T-20261017-1, the Linux eval run (2 of 4 agents typed `python`, got `command not found` and retried with `python3`)
- files: SKILL.md (BW line)
- The `BW` line says `python3` on macOS and Linux, as the hub does.

### C-20261017-1 · 2026-10-17 · name the header text in prompts
- because: ../brandwright-train T-20261017-1, ../brandwright-train L-002
- files: references/prompts.md (Text, When results are off)
- Test 3: with the header text named in quotes, the start page drew "GOV.UK" or "Fishing Service" correctly in 4 of 4 pictures, where the control drew made-up names.

### C-20261016-2 · 2026-10-16 · base graph for on-brand pictures
- because: T-20261016-4, L-002
- files: SKILL.md (Step 3), LEARNINGS.md (L-002 confirmed)
- Step 3 says when to use the base graph and when Turbo, with the time each takes.

### C-20261016-1 · 2026-10-16 · code route: real variable names, font warnings
- because: T-20261016-3, L-003, L-004
- files: ../brandwright/scripts/bw_browser.py (cmd_render), references/code-route.md (Skeleton, Rules, Render and check), ../../tests/smoke_browser.py
- `render` warns when a font fails to load. The code-route reference lists the `--bw-*` names brand.css really has and drops fallback values from the skeleton.

### C-20261015-1 · 2026-10-15 · Created
- because: user request (brand and sub-site LoRAs for mock-ups of new components, usable at work), R-20261015-1
- files: SKILL.md, references/, evals/evals.json
- First version.
