# Research: brandwright-capture

Findings behind [SKILL.md](SKILL.md). Changes they caused are in [CHANGELOG.md](CHANGELOG.md); lessons from use in [LEARNINGS.md](LEARNINGS.md); state in `evergreen.json`. Protocol: [MAINTENANCE.md](MAINTENANCE.md).

## Current understanding

- Trainers only downscale into buckets: tile long pages, crop components; keep aspect within about 1:3.
- Caption content, arrangement and quoted strings; never colours, fonts or style words.
- Repeated headers and footers over-train; dedupe and cap them.
- Blurred masks teach blur; hide regions or replace text with plausible fakes.

## Open questions

- No controlled test of trigger words on LLM text encoders (Z-Image, Qwen-Image, FLUX.2) was found.
- No published dataset-size study for UI LoRAs; the 20-40 and 40-100 counts are style-LoRA numbers.

## Search plan

- Subject: Playwright screenshot mask options; DTCG spec updates; design token extraction from live sites
- Tooling: dembrandt, Project Wallace, style-dictionary releases; captioning models for UI (Qwen-VL, Gemma, JoyCaption)
- Practice: captioning "style LoRA" UI OR screenshot <year>
- Testing: dataset quality checks for LoRAs; PII detection in screenshots (Presidio image redactor)

## Findings

### R-20261015-1 · 2026-10-15 · Dataset, masking and caption practice for screenshot LoRAs
- Track: subject, tooling, practice, testing
- Sources: [2026-10-15-ui-lora-practice-and-fact-check.md](../../ai-docs/research/2026-10-15-ui-lora-practice-and-fact-check.md) (every source and its date is listed there)
- Magnitude: n/a (creation)
- applied: C-20261015-1
