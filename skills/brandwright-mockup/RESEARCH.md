# Research: brandwright-mockup

Findings behind [SKILL.md](SKILL.md). Changes they caused are in [CHANGELOG.md](CHANGELOG.md); lessons from use in [LEARNINGS.md](LEARNINGS.md); test runs in [TESTS.md](TESTS.md); state in `evergreen.json`. Protocol: [MAINTENANCE.md](MAINTENANCE.md).

## Current understanding

- Code route for anything final; pictures for exploration.
- Quote every string; keep labels to 1-3 words.
- Sweep weights on one seed before batches.

## Open questions

- No controlled test of trigger words on LLM text encoders (Z-Image, Qwen-Image, FLUX.2) was found.
- No published dataset-size study for UI LoRAs; the 20-40 and 40-100 counts are style-LoRA numbers.

## Search plan

Four tracks; every refresh runs at least one query on each, scoped to the period since the last refresh. Protocol: [MAINTENANCE.md](MAINTENANCE.md).

Subject (the goal and the latest thinking on reaching it):

- `text rendering in open image models`
- `UI generation benchmarks`

Tooling (skills, plugins, MCP servers, scripts built for this subject):

- `ComfyUI reference/edit nodes`
- `screenshot-to-code tools`

Practice (how others use agents on this goal):

- `brand-consistent mockup workflows with AI <year>`

Testing (how work on this subject is verified, and how skills for it are tuned):

- `OCR word accuracy (STRICT), CSD style similarity, delta-E palette checks`

## Findings

### R-20261015-1 · 2026-10-15 · Text accuracy, reference routes, code route, evaluation
- Track: subject, tooling, practice, testing
- Sources: [2026-10-15-ui-lora-practice-and-fact-check.md](../../ai-docs/research/2026-10-15-ui-lora-practice-and-fact-check.md) (every source and its date is listed there)
- Magnitude: n/a (creation)
- applied: C-20261015-1
