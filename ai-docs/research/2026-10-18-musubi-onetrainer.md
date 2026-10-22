# musubi-tuner and OneTrainer job formats (for `train --for`)

2026-10-18. Read from source, not run: kohya-ss/musubi-tuner at tag v0.3.6 (commit f8a1b03, 2026-09-27) and Nerogar/OneTrainer at commit b08db37 (2026-10-11; the repository has no release tags). Tags: trainers, musubi, onetrainer, export.

Related: builds on [2026-10-15-models-trainers-licences.md](2026-10-15-models-trainers-licences.md).

## musubi-tuner

| Model | Scripts (`src/musubi_tuner/`) | `--network_module` | Notes |
|---|---|---|---|
| Z-Image base | `zimage_cache_latents.py`, `zimage_cache_text_encoder_outputs.py`, `zimage_train_network.py` | `networks.lora_zimage` | docs/zimage.md: timesteps `shift`, `--weighting_scheme none`, `--discrete_flow_shift 2.0`; text-encoder fp8 is `--fp8_llm` |
| Z-Image Turbo | same as base | same | docs say train on base. Turbo routes: the De-Turbo DiT (ostris/Z-Image-De-Turbo) or the Turbo DiT plus `--base_weights zimage_turbo_training_adapter_v2.safetensors` |
| FLUX.2 klein base 4B | `flux_2_*` | `networks.lora_flux_2` | `--model_version klein-base-4b` on all three scripts (default `dev`); `--fp8_text_encoder`; timesteps `flux2_shift` |
| Qwen-Image | `qwen_image_*` | `networks.lora_qwen_image` | `--fp8_vl`; timesteps `shift` with flow shift 2.2, or `qwen_shift`. "2512" is not named anywhere: unverified that the 2512 DiT loads |

- `--network_alpha` defaults to 1.0, not to the rank: pass it.
- No match for ai-toolkit's "weighted" timesteps; brandwright uses each model's documented recommendation.
- Starting from a LoRA: `--network_weights`. Merging LoRAs into the model before training (residual, as ai-toolkit's `assistant_lora_path`): `--base_weights A B --base_weights_multiplier 1.0 1.0`.
- Dataset TOML: one `[[datasets]]` per resolution over the same folder, each with its own `cache_directory` (docs/dataset_config.md says shared caches mix). Unverified that this matches ai-toolkit's multi-resolution buckets.
- Z-Image LoRA to ComfyUI: `python src/musubi_tuner/convert_lora.py --input IN --output OUT --target other`. The docs give the path as `networks/convert_lora.py`, which is wrong.

## OneTrainer

- Presets in `training_presets/`: `Z-Image/#z-image LoRA 16GB.json` (and 8GB, DeTurbo 16GB/8GB), `Flux 2/#flux2 LoRA 16GB.json` (base 9B only; klein is detected from the transformer config, so 4B should load: unverified), `QwenImage/#qwen LoRA 16GB.json` and 24GB (Qwen-Image, not 2512: unverified).
- `scripts/train.py --config-path FILE` starts from `TrainConfig.default_values()`, so a partial config works. **Put `"__version": 11` in it**: without it train.py migrates the file, and migration 8 replaces the `transformer` block (dtype, train flag) with the empty `prior` block (`TrainConfig.py:800-806`).
- Trains by `epochs` only (no step limit): brandwright writes `ceil(steps / images)`.
- `resolution` takes a comma list (`"768,1024"`). `save_every` + `save_every_unit: "STEP"`.
- No merge-during-training equivalent, so residual mode is refused; `lora_model_name` starts from an existing LoRA (continue mode).
- Concepts file: a list with `path` and `text.prompt_source: "sample"`, which reads the `.txt` caption beside each image.
- Output format: brandwright writes `DIFFUSERS_LORA` as the presets do (`COMFY_LORA` also exists, not tested with ComfyUI here).

## Not verified

Neither trainer was run on 2026-10-18. Model file paths are left as placeholders at the top of the musubi `train.sh`.

## Run on 2026-10-21 (musubi, Z-Image brand LoRA)

The musubi job ran unchanged apart from the three model paths (train T-20261021-1): v0.3.6, `uv sync --python 3.12 --extra cu130` (torch 2.14.1+cu130), ComfyUI's `z_image_bf16`, `ae` and `qwen_3_4b` files, 90 pictures at 768 and 1024, 300 steps, about 7.5 s a step, 41 min with both caches. The two-dataset TOML, `--fp8_base --fp8_scaled --fp8_llm` and `--network_alpha` all worked on 16 GB. The checkpoints are `<name>-step00000050.safetensors` and so on, plus `<name>.safetensors` for the last step, 280 MB at rank 32 (ai-toolkit's fp16 save is 170 MB). `src/musubi_tuner/convert_lora.py --target other` (not the `networks/` path in the docs) gives a file ComfyUI 0.38.2 loads without "lora key not loaded" warnings. Steps 150 to 300 were close to the ai-toolkit step-250 LoRA on one seed: same navy and green, white header, and the trigger sometimes drawn in the header (train L-002). Still unverified: the OneTrainer job, the other models, residual `--base_weights` and continue `--network_weights`.
