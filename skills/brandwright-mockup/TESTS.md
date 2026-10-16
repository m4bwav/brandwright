# Tests: brandwright-mockup

Test runs for [SKILL.md](SKILL.md). Cases live in `evals/evals.json` (runnable copies in the repository's root `evals/`). A test passes on evidence (a tool call in the trace, a file, a marker), never on the transcript's claim. Entry shape: `### T-YYYYMMDD-n · date · harness · env · passed/total`, newest first. Budget 150 lines. Protocol: [MAINTENANCE.md](MAINTENANCE.md).

## Runs

### T-20261015-1 · 2026-10-15 · real runs · Windows 11, RTX 5060 Ti 16 GB, ComfyUI · passed
- Code route: an application-tracker card that site does not have, written on the captured `brand.css` and rendered with `bw.py render --channel msedge`. The site's typeface, colour variables and real primary button came out exact; `score` 0.9 delta-E against 1.1 for a real captured page.
- Reference route: `bw.py ref` with two captured tiles on FLUX.2 klein 4B (distilled), 2 pictures: header, crest, hero, card list and green button carried over; the short quoted label "Get email updates" was right; the longer title and all unquoted text were garbled.
- `gen --raw` (banner and icon on Z-Image Turbo, 1536x640 and 1024x1024, batches of 4): worked through the same graph code.
- led to: L-001

