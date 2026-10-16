# Research: brandwright-train

Findings behind [SKILL.md](SKILL.md). Changes they caused are in [CHANGELOG.md](CHANGELOG.md); lessons from use in [LEARNINGS.md](LEARNINGS.md); state in `evergreen.json`. Protocol: [MAINTENANCE.md](MAINTENANCE.md).

## Current understanding

- Default: Z-Image base, rank 32, lr 1e-4, 768+1024 buckets, 40 steps per image within 1,200-3,000, checkpoints every 250.
- Site LoRAs: residual on Z-Image, continue elsewhere; stack only when needed.
- Pick the checkpoint by eye on held-out prompts; style runs often peak mid-run.

## Open questions

- No controlled test of trigger words on LLM text encoders (Z-Image, Qwen-Image, FLUX.2) was found.
- No published dataset-size study for UI LoRAs; the 20-40 and 40-100 counts are style-LoRA numbers.

## Search plan

- Subject: new image models with LoRA support and company-usable licences; licence revisions
- Tooling: ai-toolkit commits and example configs; musubi-tuner, OneTrainer releases
- Practice: "Z-Image LoRA" OR "Qwen-Image LoRA" training settings 16GB <year>
- Testing: LoRA overfitting detection; checkpoint selection metrics

## Findings

### R-20261015-1 · 2026-10-15 · Models, trainers, VRAM, Blackwell, hosted training
- Track: subject, tooling, practice, testing
- Sources: [2026-10-15-models-trainers-licences.md](../../ai-docs/research/2026-10-15-models-trainers-licences.md) (every source and its date is listed there)
- Magnitude: n/a (creation)
- applied: C-20261015-1
