# Research: brandwright

Findings behind [SKILL.md](SKILL.md). Changes they caused are in [CHANGELOG.md](CHANGELOG.md); lessons from use in [LEARNINGS.md](LEARNINGS.md); test runs in [TESTS.md](TESTS.md); state in `evergreen.json`. Protocol: [MAINTENANCE.md](MAINTENANCE.md).

## Current understanding

- Pixel diffusion gives concepts; production fidelity comes through code built from tokens (UI-Diffuser, Design2Code). brandwright offers both.
- Two independent LoRAs on overlapping data interfere (ZipLoRA, Multi-LoRA Composition). Train the site LoRA on top of the brand LoRA: residual (Z-Image, ai-toolkit assistant_lora_path) or continue (pretrained_lora_path).
- Weights need not sum to 1; sweep them. Triggers condition a LoRA, the weight switches it.
- Open models with the best text and a company-usable licence (2026-10-15): Z-Image, Qwen-Image-2512, ERNIE-Image (Apache-2.0).

## Open questions

- No controlled test of trigger words on LLM text encoders (Z-Image, Qwen-Image, FLUX.2) was found.
- No published dataset-size study for UI LoRAs; the 20-40 and 40-100 counts are style-LoRA numbers.

## Search plan

Four tracks; every refresh runs at least one query on each, scoped to the period since the last refresh. Protocol: [MAINTENANCE.md](MAINTENANCE.md).

Subject (the goal and the latest thinking on reaching it):

- `"UI mockup" OR "design system" diffusion LoRA <year>`
- `new open image models with text rendering`
- `licence changes (Z-Image, Qwen-Image, FLUX.2/3 klein)`

Tooling (skills, plugins, MCP servers, scripts built for this subject):

- `path:SKILL.md "design tokens" OR brand mockup`
- `dembrandt releases`
- `ComfyUI brand or UI LoRA nodes`

Practice (how others use agents on this goal):

- `"brand LoRA" OR "style LoRA" UI screenshots workflow <year>`
- `Claude Design, Figma Make, Stitch DESIGN.md updates`

Testing (how work on this subject is verified, and how skills for it are tuned):

- `OCR text accuracy benchmarks for image models`
- `CSD style similarity`
- `brand consistency evaluation <year>`

## Findings

### R-20261030-1 · 2026-10-30 · Quiet check
- Subject: no new open image model with text rendering or licence change found since 2026-10-15 (Ideogram 4 open weights from June stay non-commercial; Qwen-Image and Z-Image remain the text renderers). Tooling: dembrandt had a dependabot merge only (2026-10-22). Practice: nothing new on brand or UI LoRAs. Testing: nothing new.
- magnitude 0.1 · applied: none

### R-20261015-1 · 2026-10-15 · Fact-check of the common two-LoRA advice; multi-LoRA interference; differential training
- Track: subject, tooling, practice, testing
- Sources: [2026-10-15-ui-lora-practice-and-fact-check.md](../../ai-docs/research/2026-10-15-ui-lora-practice-and-fact-check.md) (every source and its date is listed there)
- Magnitude: n/a (creation)
- applied: C-20261015-1

### R-20261015-2 · 2026-10-15 · Licences, text scores, VRAM of open image models; trainers
- Track: subject, tooling, practice, testing
- Sources: [2026-10-15-models-trainers-licences.md](../../ai-docs/research/2026-10-15-models-trainers-licences.md) (every source and its date is listed there)
- Magnitude: n/a (creation)
- applied: C-20261015-1
