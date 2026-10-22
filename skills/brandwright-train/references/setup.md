# Trainer setup, troubleshooting and hosted training

## ostris ai-toolkit (the trainer bw.py drives)

Windows (Python 3.10+, 3.12 recommended), from the ai-toolkit README (checked 2026-10-15):

```
git clone https://github.com/ostris/ai-toolkit.git
cd ai-toolkit
python -m venv venv
.\venv\Scripts\activate
pip install --no-cache-dir torch==2.13.0 torchvision==0.28.0 torchaudio==2.11.0 --index-url https://download.pytorch.org/whl/cu130
pip install -r requirements.txt
```

Linux and macOS: the same with `python3 -m venv venv` and `source venv/bin/activate`. Then `set BRANDWRIGHT_AI_TOOLKIT=<folder>` (or `"ai_toolkit"` in brand.json). `bw.py train --run` uses the folder's `venv` Python and runs `run.py <config>.json` detached; the config is plain ai-toolkit JSON, so it also runs by hand: `python run.py path\to\config.json`.

- **Blackwell (RTX 50xx, sm_120)** needs PyTorch 2.7+ built for CUDA 12.8 or later; ai-toolkit's cu130 wheels need NVIDIA driver 580+. "no kernel image is available" means an older wheel.
- Out of memory: first `git pull` an older checkout (2026-10-17 fix: the text encoder stayed on the GPU after caching embeddings), then lower `--res` to `768` (or `512 768`), keep rank 32 or lower, close ComfyUI or free its memory (`POST /free` with `{"unload_models": true, "free_memory": true}`) only if no one else is using it.
- Gated download (401/403 from Hugging Face): accept the model's terms on its page and `huggingface-cli login` in the trainer's venv; Z-Image, Qwen-Image-2512 and FLUX.2 klein base 4B are not gated as of 2026-10-18; FLUX 3 klein and Krea 2 are.
- Log not moving: the first steps cache latents and text embeddings; the download of the base model can take a long time. `bw.py status` prints the last log line.
- **Windows symlink warning** from Hugging Face: harmless; the cache uses more disk.

## Other trainers

`BW train KIT --lora LORA --for musubi` writes the same job (dataset, rank, alpha, steps, lr, checkpoints, residual or continue) as `train/<name>-musubi/dataset.toml` and `train.sh` (set the DiT, VAE and text-encoder paths at its top). `--for onetrainer` writes `config.json` and `concepts.json` for `python scripts/train.py --config-path`; OneTrainer trains by epochs and cannot merge a LoRA during training, so residual mode is refused there. Formats read from musubi-tuner v0.3.6 and OneTrainer b08db37 on 2026-10-18 ([research note](../../../ai-docs/research/2026-10-18-musubi-onetrainer.md)). `--run` starts ai-toolkit only.

The musubi job for a Z-Image brand LoRA ran unchanged on 2026-10-21 (musubi v0.3.6, Windows, RTX 5060 Ti 16 GB): install with `uv sync --python 3.12 --extra cu130` in the musubi-tuner folder, put its venv first on `PATH` (or activate it) so train.sh's `python` is the right one, and point `DIT`, `VAE` and `TEXT_ENCODER` at ComfyUI's own files (`z_image_bf16`, `ae`, `qwen_3_4b`), so nothing else downloads. 300 steps took 41 min with caching; `convert_lora.py --target other` gives a file ComfyUI loads with no missing keys. The OneTrainer job has not been run.

| Trainer | Notes |
|---|---|
| kohya-ss/musubi-tuner | Qwen-Image (incl. Edit 2511), Z-Image, FLUX.2; `--blocks_to_swap` runs Qwen-Image on 12-24 GB; differential training with `--base_weights`; Z-Image LoRAs need `convert_lora.py --target other` for ComfyUI; its README shows cu124 wheels, which fail on Blackwell: install with `pip install -e .[cu130]` (or `[cu132]`) from its pyproject extras |
| Nerogar/OneTrainer | JSON configs, `python scripts/train.py --config-path`; 16 GB and 8 GB presets for Z-Image, Qwen, FLUX.2, ERNIE |
| bghira/SimpleTuner | broad model list (v4.10.0 adds FLUX 3 klein, MOSS-Image); Docker or WSL |
| tdrussell/diffusion-pipe | WSL2 (DeepSpeed) |

The dataset folders (PNG + same-name `.txt`) work in all of them.

## Hosted training with company data

Only with the user's confirmation that company policy allows it.

- The cleanest: run ai-toolkit in the company's own cloud account (AWS SageMaker custom container with VPC and KMS, Azure ML with customer-managed keys, a private GPU VM). ai-toolkit ships Modal examples (`config/examples/modal`).
- Replicate: trainings push to a private destination model; API predictions are deleted after an hour.
- fal.ai: send `X-Fal-Store-IO: 0`; delete uploaded files yourself.
- Modal: SOC 2 Type II; inputs deleted within 7 days.
- RunPod: Secure Cloud only (SOC 2, ISO 27001).
- Not for confidential data: Civitai's trainer keeps inputs 30 days.
