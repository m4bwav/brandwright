---
title: Base models, LoRA trainers, licences and hosted training for UI LoRAs
date: 2026-10-15
summary: "Which open image models suit UI mock-ups (text scores, resolution, VRAM, licence for company use), which trainers support them on 16/24 GB and Blackwell, and what hosted trainers keep. Read before changing MODELS in bw.py or quoting a licence."
tags: [research, models, licences, trainers, vram, hosted]
---

# Models, trainers and licences (checked 2026-10-15)

One research pass by a subagent (103 tool calls; Hugging Face cards, licence texts, trainer repos), plus the ai-toolkit source on disk. Figures marked ESTIMATE are inferences.

## Licences for company use

| Model | Size | Licence | Internal commercial use |
|---|---|---|---|
| Z-Image (base, 2026-01-27), Z-Image-Turbo | 6B | Apache-2.0 | yes |
| Qwen-Image, Qwen-Image-2512, Edit-2509/2511 | 20B | Apache-2.0 | yes |
| FLUX.2 klein 4B and klein base 4B | 4B | Apache-2.0 | yes |
| ERNIE-Image (2026-04) | 8B | Apache-2.0 | yes |
| HiDream-O1-Image (2026-05) | 8B | MIT | yes |
| Ming-Image-0.1-Design (2026-09, built for UI and infographics) | 6B + 16B MoE encoder | MIT | yes; validated only on an 80 GB GPU |
| SDXL | 3.5B | OpenRAIL++-M | yes, use-based limits |
| Qwen-Image-2.1 (2026-09-20) | 7B | Qwen Research License | **no**: research or evaluation only |
| FLUX.2 dev, klein 9B, FLUX.1 dev/Kontext | 32/9/12B | FLUX [dev] Non-Commercial v2.0 | **no** for production use without a BFL licence |
| FLUX 3 Klein / Klein Base (2026-10-13) | 5.6B | FLUX Kommunity v1.0 | only under US$5M annual revenue |
| Krea 2 (2026-06) | 12B | Krea 2 Community v1 | only under US$1M revenue |
| Ideogram 4 (2026-06) | 9.3B | non-commercial | **no** |
| HunyuanImage 2.1/3.0 | 17B / 80B MoE | Tencent Hunyuan Community | not licensed in the EU, UK or South Korea |

Sources: the model cards and licence files on huggingface.co for each repo (Qwen/Qwen-Image-2.1/blob/main/LICENSE, black-forest-labs/FLUX.2-klein-4B, bfl.ai/legal/non-commercial-license-terms, black-forest-labs/flux-3-image-klein-base LICENSE.md, Tongyi-MAI/Z-Image, baidu/ERNIE-Image, HiDream-ai/HiDream-O1-Image, inclusionAI/Ming-Image-0.1-Design, ideogram-ai/ideogram-4-fp8 LICENSE.md, tencent/HunyuanImage-2.1), Krea 2 licence PDF in github.com/krea-ai/krea-2.

## Text rendering (vendor-reported, from the ERNIE-Image card)

| Model | OneIG-EN Text | LongTextBench EN |
|---|---|---|
| Z-Image-Turbo | 0.994 | 0.917 |
| Qwen-Image-2512 | 0.990 | 0.956 |
| Z-Image | 0.987 | 0.935 |
| ERNIE-Image (prompt enhancer) | 0.979 | 0.980 |
| FLUX.2 klein 9B | 0.866 | 0.864 |

FLUX.2 and FLUX 3 klein cards warn that text "may be inaccurate or subject to distortion".

## Inference and training memory

- Z-Image-Turbo inference "fits comfortably within 16G" (github.com/Tongyi-MAI/Z-Image). FLUX.2 klein 4B about 13 GB. Qwen-Image fp8 file 20.4 GB (86% of a 24 GB card); GGUF builds for 16 GB.
- Training: FLUX.2 klein base 4B from 12 GB (docs.bfl.ai/flux_2/flux2_klein_training; 1800 steps in under an hour on a 4090 per the BFL blog 2026-06-04). Z-Image on 16 GB with qfloat8 + low_vram; one logged RTX 5060 Ti 16 GB run took about 7 s/step at 512/768/1024 buckets, rank 32, 3000 steps in about 6 h (smeltcore.com, 2026-10-01). Qwen-Image needs 24 GB with a 3- or 4-bit accuracy recovery adapter in ai-toolkit (`qwen_image_2512_torchao_uint3.safetensors` for 2512), or musubi-tuner with `--blocks_to_swap`.
- Blackwell (sm_120) needs PyTorch 2.7+ built for CUDA 12.8+; ai-toolkit pins cu130 (driver 580+). musubi's README shows cu124, which fails on Blackwell.

## Trainers

| Trainer | Covers | Windows | Config | Headless |
|---|---|---|---|---|
| ostris/ai-toolkit | Z-Image (base, Turbo + adapter, De-Turbo), FLUX.2 klein/dev, FLUX 3 klein (added 2026-10-15), Qwen-Image 2512/2.1/Edit, ERNIE, HiDream, Krea 2, Ideogram 4, Ming, SDXL | native | YAML or JSON | `python run.py config.json` |
| kohya-ss/musubi-tuner 0.3.6 | Qwen-Image + Edit, Z-Image, FLUX.2, Kontext, HiDream-O1, Krea 2, Ideogram 4 | yes | dataset TOML + flags | `accelerate launch ...` |
| Nerogar/OneTrainer | ERNIE, Z-Image, Qwen, FLUX.2, Krea 2, Ideogram 4, SDXL; 16 GB and 8 GB presets | native | JSON | `python scripts/train.py --config-path` |
| bghira/SimpleTuner | broad | Docker/WSL | JSON/TOML | `simpletuner train` |
| tdrussell/diffusion-pipe | broad incl. Qwen-2.1 t2i | WSL2 | TOML | deepspeed |
| kohya-ss/sd-scripts | SDXL, SD3, FLUX.1 only | yes | TOML | accelerate |

ComfyUI loads ai-toolkit, OneTrainer and SimpleTuner LoRAs through `LoraLoaderModelOnly` (comfy/lora.py maps `diffusion_model.*` and `transformer.*` keys for Z-Image, Qwen, Flux). musubi Z-Image LoRAs need `convert_lora.py --target other`.

## Choices made from this

- Default base: **Z-Image** (Apache-2.0, top text scores, any aspect 512²-2048², trains on 16 GB, and ai-toolkit can merge the brand LoRA during site training: residual mode).
- 24 GB and up: **Qwen-Image-2512** (best Apache text and layout).
- Fast and training-free route: **FLUX.2 klein 4B** (Apache, 4 reference images).
- The plugin warns against Qwen-Image-2.1, FLUX.2 dev/klein 9B, Ideogram 4 for company work, and flags revenue thresholds on FLUX 3 Klein and Krea 2.

## Hosted training with private data

Replicate (private destination models; API inputs deleted after 1 h), fal.ai (send `X-Fal-Store-IO: 0`), Civitai (keeps inputs 30 days: not for confidential data), AWS SageMaker (VPC, KMS, network isolation; custom container), Azure ML (customer-managed keys, HBI workspace), Modal (SOC 2 Type II; inputs deleted within 7 days), RunPod Secure Cloud (SOC 2, ISO 27001). Run ai-toolkit in the company's own cloud account where policy requires.

## Not verified

Maximum resolution of FLUX.2 / FLUX 3 klein; HiDream-O1 and Krea 2 VRAM; Replicate training-file retention; any 16 GB benchmark for Qwen-Image or ERNIE training.

Related: see also [UI LoRA practice and fact-check](2026-10-15-ui-lora-practice-and-fact-check.md)
