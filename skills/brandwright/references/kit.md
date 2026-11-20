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

## Guideline fields (optional)

Copy them from the brand's guidelines when it has some; `BW check KIT` lints them, and kits without them still pass. Sources: Wheeler, *Designing Brand Identity* (5th ed.) pp. 150-159, 204; Bringhurst, *Elements of Typographic Style* 3.3, 6.5; Villagomez, *Culture + Typography* intro, ch. 6.

```json
"signatures": [{"name": "horizontal", "file": "marks/h.svg"}, {"name": "stacked", "file": "marks/v.svg"}],
"clear_space": "cap height of the logotype on every side",
"min_size_px": 24,
"backgrounds": ["#ffffff", "#0b6e4f"],
"colors": [{"name": "Grove", "hex": "#0b6e4f", "role": "primary"}],
"type": [{"role": "text", "family": "Source Serif 4", "web_licence": "OFL", "small_caps": true, "text_figures": true, "true_bold": true}],
"misuse": ["no drop shadow on the mark", "never stretch the signature"],
"chart_colors": ["#0b6e4f", "#c8553d", "#3d6ec8"],
"marks_to_keep": ["the 1952 seal on the footer"],
"media": [{"medium": "signage", "note": "same letter skeleton, heavier stroke"}]
```

- `colors` roles: primary, secondary, accent, functional, neutral. `colors`, `chart_colors` and `backgrounds` join the tokens palette in `score`, and `score` works from them alone before any capture.
- `type`: the proper family name per role (display, text, documents). `check` warns when no `web_licence` is recorded. `small_caps`, `text_figures`, `true_bold` say what the face really has; a mock-up never fakes a style the face lacks (no synthetic bold or scaled-down capitals).
- `misuse`: the guidelines' "incorrect use" list; check mock-ups against it by eye.
- `media`: one letter skeleton across media, the stroke weight adjusted per medium (screen, neon, cast metal, print).
- `chart_colors`: hand them to chartwright or the dataviz palette when a mock-up holds a chart.

## Environment variables

`BRANDWRIGHT_COMFY` (default ComfyUI URL for new kits), `BRANDWRIGHT_COMFY_LORAS` (ComfyUI `models/loras` folder for `pick`), `BRANDWRIGHT_AI_TOOLKIT`, `BRANDWRIGHT_OLLAMA` (default `http://127.0.0.1:11434`), `BRANDWRIGHT_VLM` (default `qwen3-vl:8b`).

## The scripts

`scripts/bw.py` is the CLI; it imports `bw_browser.py` (Playwright: login, capture, render) and `bw_comfy.py` (ComfyUI: gen, sweep, ref). Copy all three together.
