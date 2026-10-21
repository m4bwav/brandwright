---
name: brandwright-train
description: "Train a brand LoRA and sub-site LoRAs for UI mock-ups with ostris ai-toolkit: pick the base model by licence and GPU memory (Z-Image, Qwen-Image-2512, FLUX.2 klein 4B), write the config, choose how a site LoRA relates to the brand LoRA (residual: learns only the difference; continue: starts from it; stack), run it detached, watch steps and samples, and pick the checkpoint. Covers Blackwell and 16 GB cards, other trainers (musubi-tuner, OneTrainer, SimpleTuner) and private hosted training. Use when the user asks to train or fine-tune a LoRA on a brand, website or UI dataset, which base model or licence to use for company work, how much VRAM or time it needs, how to train a site LoRA on top of a brand LoRA, or 'is the training done'. Part of brandwright. Also for 'refresh brandwright-train'. Not for training on people's faces or general character LoRAs."
metadata:
  version: "0.1.4"
---

# brandwright-train

From `dataset/<lora>/` (made by brandwright-capture) to `loras/<lora>-<model>.safetensors` and a copy in ComfyUI. `BW` is `python "<brandwright skill folder>/scripts/bw.py"` (`python3` on macOS and Linux).

## Step 0: freshness

Read [evergreen.json](evergreen.json); this unit is verify-at-use for model names and licences. If past `next_due` or `contradiction` is set, say so, do the task, refresh after ([MAINTENANCE.md](MAINTENANCE.md)).

## Step 1: what this machine can do

`BW doctor --toolkit PATH` shows the GPU, free VRAM, ai-toolkit and ComfyUI. No NVIDIA GPU here: write the config anyway (`BW train` without `--run`) and run it on a training machine or a private cloud GPU ([references/setup.md](references/setup.md)). If ComfyUI or another job holds the GPU, wait or ask; never kill someone else's process.

## Step 2: pick the base model

| `--model` | Licence | Min VRAM | Use when |
|---|---|---|---|
| `zimage` (default) | Apache-2.0 | 16 GB | almost always: strong text, any aspect 512-2048, and residual site LoRAs |
| `qwen_image` (2512) | Apache-2.0 | 24 GB | a 24 GB+ card or cloud: the best open text and layout |
| `klein4b` (FLUX.2 klein base 4B) | Apache-2.0 | 12 GB | speed (under an hour for 1,800 steps on a 4090); weaker text; pairs with the `ref` route |
| `zimage_turbo` | Apache-2.0 | 16 GB | fast 9-step generation matters more than residual site LoRAs |

Not for company work: Qwen-Image-2.1 (research licence), FLUX.2 dev and klein 9B, FLUX.1 dev (non-commercial), Ideogram 4 (non-commercial); FLUX 3 klein (under US$5M revenue only) and Krea 2 (under US$1M) have revenue limits. Re-check a licence before quoting it: [references/models.md](references/models.md).

## Step 3: brand first

```
BW train KIT --lora brand            # writes train/<name>.json and prints steps, VRAM, mode
BW train KIT --lora brand --run      # starts ai-toolkit detached; log in train/<name>.log
BW train KIT --lora brand --for musubi   # or --for onetrainer: the same job for another trainer (references/setup.md)
```

Defaults: rank 32 (flat UI needs less than photos), lr 1e-4, buckets 768 and 1024, about 5 passes over the pictures (5 steps a picture, 400 to 1,500), a checkpoint every 100 steps, and samples on held-out prompts (pricing table, settings page, modal, toast: kinds the capture rarely has, so samples show generalisation): 4 at every checkpoint for the brand LoRA, 2 every 200 steps and none at step 0 for a residual site LoRA, whose samples cost about 2 min a picture and leave the brand out (`--samples`, `--sample-every`; `--samples 0` turns them off). The first run downloads the base model (Z-Image about 20 GB).

## Step 4: then each site, on top of the brand

| `--mode` | What the site LoRA learns | Use at generation |
|---|---|---|
| `residual` (default on Z-Image) | Only what the site adds: the brand LoRA is merged in during training and switched off for samples (ai-toolkit `assistant_lora_path`) | `--lora brand=1 --lora SITE=1` |
| `continue` (default elsewhere) | Starts from the brand LoRA's weights and trains on the site | `--lora SITE=1` alone |
| `stack` | Independent of the brand | both, weights found by `sweep`; overlap makes them fight |

`residual` and `continue` need the brand LoRA picked first (`BW pick KIT --lora brand`).

## Step 5: watch, then pick

`BW status KIT`: step, checkpoints, newest sample. Open the samples (`train/out/<name>/samples/`) at each saved step:

- too weak: generic UI, wrong colours: keep going;
- right: brand colours, type and spacing on held-out components, text still legible;
- too far: copies real pages, the same layout whatever the prompt, text goes soft, pages turn sparse and empty: an earlier checkpoint wins. On the first real run (90 pictures, Z-Image) step 250 was best and everything from 500 on had collapsed into blurred, near-empty layouts (L-001).

Pick by eye, then: `BW pick KIT --lora brand --step 300 --to <ComfyUI>/models/loras` (or set `BRANDWRIGHT_COMFY_LORAS`). Without `--step`, the final file. Then brandwright-mockup, starting with `BW sweep` to confirm the weight.

For a residual site LoRA the samples are drawn without the brand LoRA, so they look weaker than the real result. Judge its checkpoints with `BW gen` or `BW sweep` on brand + site instead (L-005).

Retraining a LoRA with `--run` moves the earlier run's folder to `train/out/<name>-run-<date>`, because ai-toolkit would otherwise resume from its last checkpoint (L-003). Pass `--resume` to continue that run on purpose.

## Rules

- Training reads only the kit and the base model; nothing leaves the machine unless the user chooses a hosted trainer, and then only after they confirm their company allows it.
- Trained brand LoRAs reproduce trademarks: keep them inside the company, never publish them.
- Errors and their fixes (out of memory, Blackwell "no kernel image", a gated download, a stalled log): [references/setup.md](references/setup.md).

## Maintenance

Evergreen: [evergreen.json](evergreen.json), [RESEARCH.md](RESEARCH.md), [CHANGELOG.md](CHANGELOG.md), [LEARNINGS.md](LEARNINGS.md), [TESTS.md](TESTS.md), `evals/evals.json`. Protocol: [MAINTENANCE.md](MAINTENANCE.md).
