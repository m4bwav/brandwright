# Tests: brandwright-mockup

Test runs for [SKILL.md](SKILL.md). Cases live in `evals/evals.json` (runnable copies in the repository's root `evals/`). A failure that taught something is a lesson in [LEARNINGS.md](LEARNINGS.md); a fix it caused is logged in [CHANGELOG.md](CHANGELOG.md) with `because: T-...`; research it triggered is in [RESEARCH.md](RESEARCH.md). A test passes on evidence (a tool call in the trace, a file, a marker), never on the transcript's claim. Entry shape: `### T-YYYYMMDD-n · date · harness · env · passed/total`, newest first. Budget 150 lines. Protocol: [MAINTENANCE.md](MAINTENANCE.md).

## Runs

### T-20261016-1 · 2026-10-16 · real run · RTX 5060 Ti, ComfyUI, Z-Image Turbo graph · passed with findings
- `gen` with no LoRA, brand 1.0, and brand 1.0 + residual site 1.0, same seed, three prompts (modal, start page, status card): all ran (about 26 s for 2 pictures); the LoRAs, trained on the base model, shift Turbo output only a little.
- `sweep` brand 0.6/1.0/1.4 x site 0/0.7/1.0: 9 cells and a sheet in 2 min 8 s.
- led to: L-002

### T-20261015-1 · 2026-10-15 · real runs · Windows 11, RTX 5060 Ti 16 GB, ComfyUI · passed
- Code route: an application-tracker card that site does not have, written on the captured `brand.css` and rendered with `bw.py render --channel msedge`. The site's typeface, colour variables and real primary button came out exact; `score` 0.9 delta-E against 1.1 for a real captured page.
- Reference route: `bw.py ref` with two captured tiles on FLUX.2 klein 4B (distilled), 2 pictures: header, crest, hero, card list and green button carried over; the short quoted label "Get email updates" was right; the longer title and all unquoted text were garbled.
- `gen --raw` (banner and icon on Z-Image Turbo, 1536x640 and 1024x1024, batches of 4): worked through the same graph code.
- led to: L-001
