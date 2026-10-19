# brandwright-train refresh: claims, new trainable models, trainer changes

2026-10-18. An evergreen refresh of brandwright-train (R-20261018-2). The research subagent ran 8 searches, 41 fetches and 53 tool calls. All sources were read 2026-10-18. Tags: models, licences, ai-toolkit, musubi, onetrainer, simpletuner, refresh.

Related: builds on [2026-10-15-models-trainers-licences.md](2026-10-15-models-trainers-licences.md), see also [2026-10-18-musubi-onetrainer.md](2026-10-18-musubi-onetrainer.md).

## Verify-at-use claims (all confirmed)

- **Qwen-Image-2512 on 24 GB.** ai-toolkit's `extensions_built_in/diffusion_models/ui.tsx` defines arch `qwen_image:2512` with two accuracy recovery adapters: `"3 bit with ARA": "uint3|ostris/accuracy_recovery_adapters/qwen_image_2512_torchao_uint3.safetensors"` and a 4-bit one (`..._uint4`). The default qtype is qfloat8, so the ARA option has to be chosen. No `config/examples` file exists for 2512; the only Qwen example is `train_lora_qwen_image_24gb.yaml`. Both adapter files are on [HF](https://huggingface.co/ostris/accuracy_recovery_adapters/tree/main), 295 MB each.
- **Blackwell.** The [ai-toolkit README](https://github.com/ostris/ai-toolkit) still pins `torch==2.13.0 torchvision==0.28.0 torchaudio==2.11.0` with cu130 wheels, on Python 3.10 or later (3.12 recommended). PyTorch 2.14.1 (2026-09-30) is the latest release, and [PyTorch](https://github.com/pytorch/pytorch/releases) 2.12 dropped its CUDA 12.8 builds, so cu128 wheels stop at 2.11. In practice the choice is cu130 or cu132.
- **Licences** (from the HF API, `huggingface.co/api/models/<id>`):
  - Apache-2.0 and not gated: Z-Image (modified 2026-01-28), Z-Image-Turbo (2026-01-30), Qwen-Image-2512 (2025-12-31) and FLUX.2-klein-base-4B (2026-02-24).
  - Qwen-Image-2.1: `qwen-research`, not gated.
  - FLUX 3 klein base: `flux-kommunity-license` v1.0, gated, created 2026-10-13. Commercial use is open only to companies with gross annualized revenue under US$5M, affiliates included. Commercial users must also filter or review outputs and disclose AI generation where the law requires it.
  - Krea 2: revenue under US$1M in the trailing 12 months (Section 2.3, licence dated 2026-06-22). It has no seat cap, although some secondary sources claim one.

## Findings since 2026-10-14

- **MOSS-Image.** [OpenMOSS](https://huggingface.co/OpenMOSS-Team/MOSS-Image-SFT) released Base and SFT on 2026-10-11, both Apache-2.0 and not gated. It is a 5B DiT with a Qwen3.5 text encoder and the FLUX.2 small VAE, renders Chinese and English text, and takes JSON layout prompts. ai-toolkit has trained it since 2026-10-16 (commits c6a9b56 and b7cd8a1, convrot8 by default), and so does [SimpleTuner v4.10.0](https://github.com/bghira/SimpleTuner/releases). It has no published text scores, and its training VRAM is not measured. Magnitude 0.3; the models table now names it.
- **FLUX 3 klein base in ai-toolkit.** [PR #1078](https://github.com/ostris/ai-toolkit/pull/1078) was merged 2026-10-15, with fixes on 10-15 and 10-17. It uses arch `flux3` and model `black-forest-labs/flux-3-image-klein-base` (5.6B, Qwen3-VL-4B text encoder; gated, so the licence must be accepted first), with convrot8 for both the transformer and the text encoder. `flux3.py` has no `assistant_lora_path`, so only continue mode works. The [card](https://huggingface.co/black-forest-labs/flux-3-image-klein-base) gives an inference peak on a B200 of 31 GB in BF16 and 26 GB in NVFP4, and warns against prompting without an upsampler. Nobody has shown it training on 16 GB. Magnitude 0.3; the models table marks it trainable.
- **Quantization.** ai-toolkit now offers convrot8, convrot4 (nvfp4), convrotint2 to convrotint7, bitnet and W4A8, alongside qfloat8 and uint2 to uint7. Newer archs (FLUX 3, MOSS, Ming) default to convrot8. Z-Image, Qwen-Image-2512 and FLUX.2 klein still default to qfloat8, so the configs bw.py writes are unaffected. Open [issue #1074](https://github.com/ostris/ai-toolkit/issues/1074) reports convrot int8 problems on Windows. Magnitude 0.15; recorded here only.
- **VRAM fix.** Commit 8cf43dd (2026-10-17) frees the text encoder from the GPU after text embeddings are cached. That may explain 16 GB out-of-memory reports such as [issue #1038](https://github.com/ostris/ai-toolkit/issues/1038). setup.md now says to update an older checkout before lowering `--res`.
- **musubi-tuner.** Its README still shows cu124, but `pyproject.toml` has mutually exclusive extras: cu128 (torch>=2.7.1), cu130 (torch>=2.9.1) and cu132 (torch>=2.12.0, added in v0.3.5). There have been no release or commits since v0.3.6 (2026-09-27), so the `--for musubi` format is unchanged.
- **OneTrainer.** The head is still b08db37 (2026-10-10), so the `--for onetrainer` format is unchanged.
- **Practice.** The 16 GB Z-Image guides published since 10-14 (RunComfy, and an HF card trained on an RTX 5080 at rank 32 for 3,000 steps) agree with the defaults. In [Z-Image discussion #32](https://huggingface.co/Tongyi-MAI/Z-Image/discussions/32), Turbo runs on an RTX 5060 Ti 16 GB at about 11 s per 1024² image in 8 steps.
- **Testing.** No metric-based checkpoint picker exists yet. Practice is still held-out prompts judged by eye (an LTX blog post; T-LoRA, arXiv 2507.05964). An arXiv 2607.21612 preprint on LLM fine-tuning found lower held-out loss alongside worse behaviour, which argues against picking checkpoints by loss. ai-toolkit's "experimental band loss" (831ccfa) is undocumented. The evals are unchanged.

## For next time

- Use the HF API for licences: one call gives the licence, the gating and the dates.
- ai-toolkit's per-model defaults are in `ui.tsx`, and its commits page dates new models. `config/examples` lags behind.
- Read musubi's `pyproject.toml` along with its README.
- Forums: ai-toolkit Issues (it has no GitHub Discussions; the community is on Discord), musubi-tuner Discussions and Issues, OneTrainer Discussions, Z-Image HF discussions (user threads, no announcements), SimpleTuner releases.
- Upcoming: PyTorch Conference NA, 2026-10-20 and 21, where a release may be announced.
