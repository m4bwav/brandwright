# Changelog: brandwright-mockup

Every change to [SKILL.md](SKILL.md) and its companions, newest first, each with the reason (`R-` findings in [RESEARCH.md](RESEARCH.md), `L-` lessons in [LEARNINGS.md](LEARNINGS.md), `T-` runs in [TESTS.md](TESTS.md)). Protocol: [MAINTENANCE.md](MAINTENANCE.md).

### C-20261016-1 · 2026-10-16 · code route: real variable names, font warnings
- because: T-20261016-3, L-003, L-004
- files: ../brandwright/scripts/bw_browser.py (cmd_render), references/code-route.md (Skeleton, Rules, Render and check), ../../tests/smoke_browser.py
- `render` warns when a font fails to load. The code-route reference lists the `--bw-*` names brand.css really has and drops fallback values from the skeleton.

### C-20261015-1 · 2026-10-15 · Created
- because: user request (brand and sub-site LoRAs for mock-ups of new components, usable at work), R-20261015-1
- files: SKILL.md, references/, evals/evals.json
- First version.
