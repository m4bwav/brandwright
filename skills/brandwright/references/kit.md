# The kit: folder contract and brand.json

One kit per brand. It holds the company's screenshots, login sessions and trained LoRAs, so it lives on storage the company approves and never inside a repository. `bw.py new` writes a `.gitignore` containing `*` and a README into it.

```
KIT/
  brand.json                 names, triggers, sites, model, ComfyUI URL, picked LoRAs
  .gitignore                 "*": git never picks the kit up
  auth/<site>/               browser profile from `bw.py login` (secret: it can open the site as the user)
  capture/<site>/
    pages/<page>__<viewport>.png   full-page screenshots
    imports/                       screenshots the user supplied (`bw.py import`)
    capture.jsonl                  one record per picture: url, title, viewport, dsf, bg, component boxes and text
    tokens/<page>__<viewport>.json computed-style tallies, custom properties, @font-face rules, component recipes
  tokens.json   brand.css   tokens.md   palette.png      from `bw.py tokens` (the code route)
  dataset/<lora>/NNNN.png + NNNN.txt + manifest.jsonl    from `bw.py prep` and `bw.py caption`
  review.html                from `bw.py review`
  train/<name>.json  .log  .pid   train/out/<name>/       trainer config, log, checkpoints and samples
  loras/<lora>-<model>.safetensors                       from `bw.py pick`
  out/<timestamp>-<slug>/    mock-ups with mockup.json (prompt, LoRAs, weights, seed) or sweep.jpg
```

## brand.json

```json
{
  "brandwright": 1,
  "brand": {"name": "Acme", "trigger": "acmeui"},
  "sites": [
    {"name": "careers", "trigger": "acmecareersui", "urls": ["https://careers.acme.example/"], "lora": true,
     "blur": [".customer-name"]}
  ],
  "model": "zimage",
  "comfy": "http://127.0.0.1:8188",
  "comfy_loras": {"brand": "acme-brand.safetensors", "careers": "acme-careers.safetensors"},
  "comfy_models": {"zimage": {"unet": "z_image_bf16.safetensors"}},
  "ai_toolkit": "C:/tools/ai-toolkit",
  "picked": {"brand": {"file": "...", "from": "acme-brand-zimage_000001500.safetensors", "model": "zimage", "date": "2026-10-16"}},
  "private": true
}
```

- `trigger`: a made-up word for the brand, and one per site. Site captions carry both (`acmeui acmecareersui, ...`); `gen` adds the right triggers for the LoRAs it loads.
- `lora: false` on a site: its pictures still feed the brand LoRA, but it gets no LoRA of its own.
- `blur`: CSS selectors blurred on every capture of that site. `--hide` on the command line hides instead; hiding is better because blurred boxes teach the LoRA to draw blur.
- `comfy_models`: override any loader file name per graph (`unet`, `clip`, `clip_type`, `vae`, `steps`, `cfg`, `sampler`, `scheduler`, `shift`).
- `ai_toolkit`: the trainer folder, or set `BRANDWRIGHT_AI_TOOLKIT`.

## Environment variables

`BRANDWRIGHT_COMFY` (default ComfyUI URL for new kits), `BRANDWRIGHT_COMFY_LORAS` (ComfyUI `models/loras` folder for `pick`), `BRANDWRIGHT_AI_TOOLKIT`, `BRANDWRIGHT_OLLAMA` (default `http://127.0.0.1:11434`), `BRANDWRIGHT_VLM` (default `qwen3-vl:8b`).

## The scripts

`scripts/bw.py` is the CLI; it imports `bw_browser.py` (Playwright: login, capture, render) and `bw_comfy.py` (ComfyUI: gen, sweep, ref). Copy all three together.
