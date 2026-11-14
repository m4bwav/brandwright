# Base models and licences (checked 2026-10-18)

Re-check before quoting: licences and model versions change monthly. Primary sources are each model's Hugging Face card and licence file; `huggingface.co/api/models/<id>` gives licence, gating and dates in one call. ai-toolkit's per-model defaults (quantization, the Qwen-Image-2512 3-bit and 4-bit accuracy recovery adapters) live in its `extensions_built_in/diffusion_models/ui.tsx`, not `config/examples`.

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
| MOSS-Image (2026-10-11) | 5B | Apache-2.0 | yes | not scored | not measured; ai-toolkit and SimpleTuner since 2026-10-16 |
| FLUX 3 klein (2026-10-13) | 5.6B | FLUX Kommunity v1.0 (gated) | under US$5M annual revenue | not scored | 16 GB unverified; ai-toolkit `flux3` since 2026-10-15, no residual |
| Krea 2 | 12B | Krea 2 Community (content filter required; distributed models named "Krea…" with a Notice) | under US$1M revenue | not scored; headlines right, body text gibberish in a 2026-11-05 test | 16 GB fits but is tight, measured below; train on Raw, run on Turbo |
| Ideogram 4 | 9.3B | non-commercial | **no** | best claimed | not checked |
| HunyuanImage 2.1 / 3.0 | 17B / 80B | Tencent Hunyuan Community | not in the EU, UK or South Korea | | 24 GB+ |

Text scores are vendor-reported (ERNIE-Image card). Practical text accuracy for UI is lower: on Qwen-Image-2512 one to three large words come out right about 70% of the time, whole sentences under 40%.

## Why Z-Image is the default

Apache-2.0, top-tier text scores, any aspect ratio between 512² and 2048² of area, a known 16 GB training route (an RTX 5060 Ti 16 GB run measured about 7 s a step at 512/768/1024 buckets, rank 32), and ai-toolkit can merge another LoRA during training only (`model.assistant_lora_path`, verified in its `z_image.py`), which makes residual site LoRAs possible. FLUX.2 has no such hook in ai-toolkit, so site LoRAs on klein use `continue` (`network.pretrained_lora_path`).

## Generating with the LoRA

ComfyUI needs the matching model files. Z-Image base: `z_image_bf16.safetensors` (diffusion_models), `qwen_3_4b.safetensors` (text_encoders, CLIPLoader type `lumina2`), `ae.safetensors` (vae). LoRAs trained on the base also load on Z-Image-Turbo (`--graph zimage_turbo`) for 9-step drafts; check them against the base before trusting a draft. Graph presets and file names: `GRAPHS` in `scripts/bw_comfy.py`, overridable per kit in `brand.json` `comfy_models`.

## Krea 2 on 16 GB (measured 2026-11-05)

A 300-step test on ai-toolkit, `arch: krea2`, `krea/Krea-2-Raw`, RTX 5060 Ti 16 GB, 90 UI pictures, buckets 768 and 1024, rank 32, qfloat8 on model and text encoder, `low_vram`, cached text embeddings, no samples. Not in `bw.py` `MODELS` yet: the job was written by hand.

- Time: 1 h 43 min, 20.6 s a step on average, about three times the Z-Image figure above. Steps began near 11 s and later ran near 19 s; the cause was not found.
- Memory, logged from about step 53, so model load and caching are not covered: card peak 16.0 of 16.3 GB, including about 1.8 GB held by other apps; trainer peak 10.1 GB RAM, system peak 36.8 GB. No out-of-memory error.
- Generation: the LoRA loads on Krea Turbo in ComfyUI at 8 steps, and stacks with the 4-step distill LoRA (chk133000, both at strength 1.0) at about 8.4 s against 14.2 s at 1024x768.
- Result on one seed and 4 prompts: the look moved by step 300, but it did not reach the brand. The trigger word is drawn as a logo, even with no LoRA, so a real word or no trigger may suit Krea better. A prompt without the trigger shifted toward the brand's navy by step 300, so check bleed. The agent reviewed this, not a person.

## Style LoRAs: one practitioner's arms to try (unverified)

From one maker's 50+ one-variable FLUX.2 Klein / dev runs with ai-toolkit on a photo style (r/FluxAI 1qwasra, 2026-02; one dataset, judged by eye). His target was a texture look and ours is layouts, so none of this changes the defaults or step counts above.

- Add one sample prompt with a subject that is not in the set (he used "dog on a log"). If it comes out looking like a training picture, the LoRA is memorising, not learning the style.
- Weight decay is the texture knob: about ten times lower kept grain and shadow detail; raise it for flat illustration.
- Network dims 128 / 64 / 64 / 32 (linear, linear_alpha, conv, conv_alpha) were his best for style LoRAs on every base; 256 everywhere broke images. Try it as an arm against the default, not as a default.
- Measured here 2026-11-14 (Klein 4B, one UI set, CLIP style scores): weight decay /10 was worse on every score, so keep it as a photo-texture knob only; 128/64/64/32 carried the style to unseen subjects best (0.574 vs 0.498) but is 4x larger and edges toward memorising; the default 32/32 scored best in-set (0.664 vs 0.625). The default stays.
