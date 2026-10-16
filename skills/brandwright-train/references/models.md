# Base models and licences (checked 2026-10-15)

Re-check before quoting: licences and model versions change monthly. Primary sources are each model's Hugging Face card and licence file.

| Model | Size | Licence | Company use | Text (OneIG-EN / LongText EN) | Train VRAM |
|---|---|---|---|---|---|
| Z-Image (base) | 6B | Apache-2.0 | yes | 0.987 / 0.935 | 16 GB (qfloat8, low_vram) |
| Z-Image-Turbo | 6B | Apache-2.0 | yes | 0.994 / 0.917 | 16 GB with the training adapter |
| Qwen-Image-2512 | 20B | Apache-2.0 | yes | 0.990 / 0.956 | 24 GB (3-bit + accuracy recovery adapter) |
| FLUX.2 klein base 4B | 4B | Apache-2.0 | yes | weaker ("may be inaccurate") | 12 GB |
| ERNIE-Image | 8B | Apache-2.0 | yes | 0.979 / 0.980 | 24 GB inference; OneTrainer 16 GB preset |
| HiDream-O1-Image | 8B | MIT | yes | LongText 0.979 | not checked |
| Ming-Image-0.1-Design | 6B + 16B encoder | MIT | yes, built for UI | not scored | 80 GB validated |
| Qwen-Image-2.1 | 7B | Qwen Research License | **no** (research or evaluation only) | strong | 24 GB at 512 px |
| FLUX.2 dev / klein 9B / FLUX.1 dev | 32 / 9 / 12B | FLUX [dev] Non-Commercial | **no**, unless licensed from BFL | 0.866 (klein 9B) | 22 GB+ |
| FLUX 3 klein (2026-10-13) | 5.6B | FLUX Kommunity v1.0 | under US$5M annual revenue | not scored | new |
| Krea 2 | 12B | Krea 2 Community | under US$1M revenue | not scored | not checked |
| Ideogram 4 | 9.3B | non-commercial | **no** | best claimed | not checked |
| HunyuanImage 2.1 / 3.0 | 17B / 80B | Tencent Hunyuan Community | not in the EU, UK or South Korea | | 24 GB+ |

Text scores are vendor-reported (ERNIE-Image card). Practical text accuracy for UI is lower: on Qwen-Image-2512 one to three large words come out right about 70% of the time, whole sentences under 40%.

## Why Z-Image is the default

Apache-2.0, top-tier text scores, any aspect ratio between 512² and 2048² of area, a known 16 GB training route (an RTX 5060 Ti 16 GB run measured about 7 s a step at 512/768/1024 buckets, rank 32), and ai-toolkit can merge another LoRA during training only (`model.assistant_lora_path`, verified in its `z_image.py`), which makes residual site LoRAs possible. FLUX.2 has no such hook in ai-toolkit, so site LoRAs on klein use `continue` (`network.pretrained_lora_path`).

## Generating with the LoRA

ComfyUI needs the matching model files. Z-Image base: `z_image_bf16.safetensors` (diffusion_models), `qwen_3_4b.safetensors` (text_encoders, CLIPLoader type `lumina2`), `ae.safetensors` (vae). LoRAs trained on the base also load on Z-Image-Turbo (`--graph zimage_turbo`) for 9-step drafts; check them against the base before trusting a draft. Graph presets and file names: `GRAPHS` in `scripts/bw_comfy.py`, overridable per kit in `brand.json` `comfy_models`.
