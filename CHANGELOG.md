# Changelog

Plugin versions, newest first. Skill-level changes are in each skill's `CHANGELOG.md`; the session log is `ai-docs/log.md`.

## Unreleased

## 0.1.0 · 2026-10-15

First release: brand and sub-site LoRAs for on-brand UI mock-ups, with a training-free reference route and a code route.

- Skills: `brandwright` (routes, kit, data and licence rules, common myths), `brandwright-capture`, `brandwright-train`, `brandwright-mockup`, each evergreen with research dated 2026-10-15.
- `bw.py`:
  - `new`, `doctor`, `import`;
  - `tokens`: DTCG-shaped `tokens.json` with per-site overrides, plus `brand.css` with the site's own CSS variables, `@font-face` rules and component recipes, including the primary button;
  - `prep`: viewport tiles, component specimens, perceptual and same-text dedupe, caps on repeated parts, brand and site datasets, template captions;
  - `caption`: a local vision model through Ollama, with a cache and style-word flags;
  - `review`, `score` (palette delta-E), `sheet`.
- Training: `train` writes ostris ai-toolkit JSON for Z-Image, Z-Image Turbo, Qwen-Image-2512 or FLUX.2 klein base 4B. Site LoRAs train in residual mode (the brand LoRA is merged during training), continue mode or stack mode. `--run` starts the job detached. `status` and `pick` follow up.
- Browser (Playwright): `login`, where the person signs in themselves; `capture`, with masking, overlay hiding, same-site crawl, `--cdp` and `--channel msedge`; `render` for the code route.
- ComfyUI: `gen` with LoRA chains and automatic triggers, `sweep` with a contact sheet, and `ref`, which uses FLUX.2 klein with up to 4 reference screenshots.
- Tests:
  - 22 offline tests;
  - a browser smoke test on a fictional fixture site;
  - a size budget and a public-repository check, both in CI;
  - CI on Windows, macOS and Linux with Python 3.10 and 3.14.
