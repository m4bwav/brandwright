# Research: brandwright-train

Findings behind [SKILL.md](SKILL.md). Changes they caused are in [CHANGELOG.md](CHANGELOG.md); lessons from use in [LEARNINGS.md](LEARNINGS.md); test runs in [TESTS.md](TESTS.md); state in `evergreen.json`. Protocol: [MAINTENANCE.md](MAINTENANCE.md).

## Current understanding

- Default: Z-Image base, rank 32, lr 1e-4, 768+1024 buckets, about 5 steps a picture within 400-1,500, checkpoints every 100 (L-001; the 40-a-picture rule overtrained).
- Site LoRAs: residual on Z-Image, continue elsewhere; stack only when needed.
- Pick the checkpoint by eye on held-out prompts; style runs often peak mid-run.

## Open questions

- MiniMax H3 Image licence and VRAM before listing it; can ZenTrainer train residual LoRAs? (R-20261120-1)
- No controlled test of trigger words on LLM text encoders (Z-Image, Qwen-Image, FLUX.2) was found.
- No published dataset-size study for UI LoRAs; the 20-40 and 40-100 counts are style-LoRA numbers.
- MOSS-Image: real UI text quality and 16 GB training VRAM. FLUX 3 klein: does it train on 16 GB with convrot8?

## Search plan

Four tracks; every refresh runs at least one query on each, scoped to the period since the last refresh. Protocol: [MAINTENANCE.md](MAINTENANCE.md).

Subject (the goal and the latest thinking on reaching it):

- `new image models with LoRA support and company-usable licences`
- `licence revisions` (via `huggingface.co/api/models/<id>`)
- Forums: [ai-toolkit Issues](https://github.com/ostris/ai-toolkit/issues) (no Discussions), [musubi-tuner Discussions](https://github.com/kohya-ss/musubi-tuner/discussions), [OneTrainer Discussions](https://github.com/Nerogar/OneTrainer/discussions), [Z-Image HF discussions](https://huggingface.co/Tongyi-MAI/Z-Image/discussions)

Tooling (skills, plugins, MCP servers, scripts built for this subject):

- `ai-toolkit commits and example configs`
- `musubi-tuner, OneTrainer, SimpleTuner releases` (musubi: read pyproject.toml with the README)
- ai-toolkit `extensions_built_in/diffusion_models/ui.tsx` for per-model defaults; `config/examples` lags

Practice (how others use agents on this goal):

- `"Z-Image LoRA" OR "Qwen-Image LoRA" training settings 16GB <year>`

Testing (how work on this subject is verified, and how skills for it are tuned):

- `LoRA overfitting detection`
- `checkpoint selection metrics`

## Findings

### R-20261120-1 · 2026-11-20 · Refresh: ai-toolkit UI auth and path-traversal fix; H3 Image adapter; ZenTrainer
- Summary: ostris/ai-toolkit main (2026-11-18) adds an auth token on UI write routes, a rolling read key when a password is set, and fixes a path traversal hole in caption/delete routes; anyone exposing the UI should pull. Same week: fixed negative self-correction noise scale, an adamconvrot fix (may matter for FLUX 3 klein convrot8), faster noise pairing, lighter memory flushing, merged LoRAs keep per-weight dtype. 2026-11-10: MiniMax H3 Image training adapter (licence and VRAM unchecked, so not listed in models). Tooling: Nynxz/ZenTrainer v0.4.1 (MIT), a ComfyUI-native LoRA trainer covering Z-Image, FLUX 3, Krea 2 and others; secondary source only, repo not read. musubi-tuner still v0.3.6. Practice/testing: RunComfy and evo-hq skills confirm "a finished job is not proof", matching L-001.
- Track: subject, tooling (practice and testing confirm only)
- Sources: https://github.com/ostris/ai-toolkit/commits/main, https://comfyui-wiki.com/en/news/2026-11-07-zentrainer, https://github.com/kohya-ss/musubi-tuner/releases, https://www.skills.sh/runcomfy-com/skills/lora-training
- Magnitude: 0.25
- Applied: none (note; search plan: add comfyui-wiki.com/news as a trainer lead source)

### R-20261018-2 · 2026-10-18 · Refresh: claims hold; MOSS-Image and FLUX 3 klein now trainable
- Track: subject, tooling, practice, testing
- Claims 2-4 confirmed. MOSS-Image (5B, Apache-2.0) and FLUX 3 klein (`flux3`, continue only) train in ai-toolkit since 2026-10-15/16; OOM fix 8cf43dd; musubi cu130 extras; `--for` formats unchanged; checkpoint picking by eye stands.
- Sources: [2026-10-18-train-refresh.md](../../ai-docs/research/2026-10-18-train-refresh.md) (every source and its date)
- Magnitude: 0.3 (point: two new trainable models)
- applied: C-20261018-2

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
