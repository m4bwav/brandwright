# Research: brandwright-train

Findings behind [SKILL.md](SKILL.md). Changes they caused are in [CHANGELOG.md](CHANGELOG.md); lessons from use in [LEARNINGS.md](LEARNINGS.md); test runs in [TESTS.md](TESTS.md); state in `evergreen.json`. Protocol: [MAINTENANCE.md](MAINTENANCE.md).

## Current understanding

- Default: Z-Image base, rank 32, lr 1e-4, 768+1024 buckets, 40 steps per image within 1,200-3,000, checkpoints every 250.
- Site LoRAs: residual on Z-Image, continue elsewhere; stack only when needed.
- Pick the checkpoint by eye on held-out prompts; style runs often peak mid-run.

## Open questions

- No controlled test of trigger words on LLM text encoders (Z-Image, Qwen-Image, FLUX.2) was found.
- No published dataset-size study for UI LoRAs; the 20-40 and 40-100 counts are style-LoRA numbers.

## Search plan

Four tracks; every refresh runs at least one query on each, scoped to the period since the last refresh. Protocol: [MAINTENANCE.md](MAINTENANCE.md).

Subject (the goal and the latest thinking on reaching it):

- `new image models with LoRA support and company-usable licences`
- `licence revisions`

Tooling (skills, plugins, MCP servers, scripts built for this subject):

- `ai-toolkit commits and example configs`
- `musubi-tuner, OneTrainer releases`

Practice (how others use agents on this goal):

- `"Z-Image LoRA" OR "Qwen-Image LoRA" training settings 16GB <year>`

Testing (how work on this subject is verified, and how skills for it are tuned):

- `LoRA overfitting detection`
- `checkpoint selection metrics`

## Findings

### R-20261018-1 · 2026-10-18 · musubi-tuner and OneTrainer job formats
- Track: tooling
- Sources: [2026-10-18-musubi-onetrainer.md](../../ai-docs/research/2026-10-18-musubi-onetrainer.md) (musubi-tuner v0.3.6, OneTrainer b08db37, read from source)
- Magnitude: minor (new export target; ai-toolkit defaults unchanged)
- applied: C-20261018-1

### R-20261015-1 · 2026-10-15 · Models, trainers, VRAM, Blackwell, hosted training
- Track: subject, tooling, practice, testing
- Sources: [2026-10-15-models-trainers-licences.md](../../ai-docs/research/2026-10-15-models-trainers-licences.md) (every source and its date is listed there)
- Magnitude: n/a (creation)
- applied: C-20261015-1
