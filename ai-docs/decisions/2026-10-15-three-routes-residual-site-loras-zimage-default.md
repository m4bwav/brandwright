---
title: Three routes, residual site LoRAs, Z-Image by default, kits outside the repo
date: 2026-10-15
summary: "Why brandwright offers code, reference and LoRA routes; why site LoRAs train on top of the brand LoRA; why Z-Image is the default base; why the CLI is stdlib with optional Playwright and Pillow; why kits never enter a repository."
tags: [decision, architecture, lora, licences, privacy]
---

# Three routes, residual site LoRAs, Z-Image by default

## Context

The owner wants brand and sub-site LoRAs to mock up new components at work, starting the next day. A chat assistant had told them to train two LoRAs with trigger words and stack them near weight 1.0. Research on 2026-10-15 ([fact-check](../research/2026-10-15-ui-lora-practice-and-fact-check.md), [models](../research/2026-10-15-models-trainers-licences.md)) found that advice half right, and found image models still unreliable on small text.

## Decisions

1. **Three routes, cheapest first.**
   - Code: tokens and component recipes read from the live site, HTML on `brand.css`, rendered.
   - Reference: FLUX.2 klein with up to 4 screenshots.
   - LoRA.

   Why: the literature puts pixel diffusion at concept level and production fidelity in code (UI-Diffuser, Design2Code). The code route also works on a work laptop with no GPU, which meets "use it tomorrow".
2. **Site LoRAs train on top of the brand LoRA.**
   - `residual`: ai-toolkit `model.assistant_lora_path`, verified in `z_image.py`. The brand LoRA is merged during training and inverted for samples.
   - `continue`: `network.pretrained_lora_path`, generic in `BaseSDTrainProcess.py`.
   - `stack` stays as an option.

   Why: two independent LoRAs on overlapping data interfere (ZipLoRA, Multi-LoRA Composition).

   Rejected: one LoRA with two triggers (concepts bleed, and one half cannot be retrained alone); merging the brand LoRA into a full checkpoint copy (needs torch in the CLI and a 12+ GB file per brand).
3. **Z-Image base is the default.** It is Apache-2.0, has top-tier text scores, trains on 16 GB, and is the only model with the residual hook. Qwen-Image-2512 is for 24 GB+, and klein 4B for speed and the reference route.

   Rejected as defaults:
   - Qwen-Image-2.1: research licence.
   - FLUX.2 dev and klein 9B: non-commercial.
   - FLUX 3 klein: two days old, with a revenue limit.
4. **The CLI is standard library only, with Playwright and Pillow optional.**
   - `--channel msedge` uses the browser already on a Windows work machine, so nothing is downloaded beyond `pip install playwright`.
   - Trainer configs are written as JSON, which ai-toolkit accepts (`toolkit/config.py`), so no YAML dependency.
5. **Kits live outside every repository.**
   - `bw.py new` writes a `*` `.gitignore` into each kit.
   - The repository's `.gitignore` excludes `kits/` and `*.safetensors`.
   - `scripts/check_public.py` fails CI on local paths, private addresses or kit files.

   Why: a kit holds company screenshots and a live login session.
6. **Logins are always the person's own.** `login` opens a window and waits for it to close; `--cdp` attaches to their running browser. Crawling is GET-only and skips sign-out and delete links.
7. **Captions describe content and quote strings, never style.** That follows BFL's principle. `caption` runs a local Ollama vision model by default, so screenshots stay on the machine.

Related: builds on [UI LoRA practice and fact-check](../research/2026-10-15-ui-lora-practice-and-fact-check.md); builds on [models, trainers and licences](../research/2026-10-15-models-trainers-licences.md)
