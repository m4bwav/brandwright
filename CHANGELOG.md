# Changelog

Plugin versions, newest first. Skill-level changes are in each skill's `CHANGELOG.md`; the session log is `ai-docs/log.md`.

## Unreleased

## 0.1.3 · 2026-10-18

Jobs for other trainers, and two documentation changes from the fourth training test and the Linux eval run.

- `train --for musubi` writes the same LoRA job for kohya-ss/musubi-tuner (a dataset TOML and a `train.sh`), and `--for onetrainer` writes a OneTrainer config and concepts file. Residual site LoRAs map to musubi's `--base_weights`; OneTrainer cannot merge a LoRA during training, so it refuses residual mode. Formats were read from musubi-tuner v0.3.6 and OneTrainer's 2026-10-11 source; neither trainer has run them yet.
- Prompt guide: with the brand LoRA alone on Z-Image the trigger word is optional (`gen --raw`); the look held without it in the fourth training test. Keep the triggers when a site LoRA is loaded too: there one picture in two fell back to the base model's photographs. Naming the header text is still what stops invented site names.
- The capture, train and mockup skills say `python3` on macOS and Linux, as the hub does. In the Linux eval run, 2 of 4 agents first typed `python` and got `command not found`.

## 0.1.2 · 2026-10-17

Faster residual site training and a prompt rule from the third training test. No default changed for captions or triggers.

- `train`: residual site LoRAs draw 2 sample prompts every 200 steps and skip the step-0 sample, which cut about 30 minutes from a 400-step run in the second training test. Brand LoRAs keep 4 at every checkpoint. New `--sample-every`; `--samples 0` turns sampling off.
- Prompt guide: name the header text in quotes (`the header shows the name "Fishing Service"`). In the third training test this stopped the model inventing a site name or drawing the trigger word in the header. A trigger that is not a word, or captions quoting the logo, made it worse, so the defaults stay.

## 0.1.1 · 2026-10-16

Fixes from a fresh-install dry run of the code route and from the second training test. The code route has since been used on a work computer without trouble.

- `tokens` no longer takes an unstyled browser-default button as the primary button, and says when the capture has no call-to-action button.
- `render` warns when a font fails to load (behind a login, or refusing pages opened from disk), instead of quietly drawing a fallback font.
- The code-route guide lists the real `--bw-*` variable names and drops fallback values, which hid wrong names.
- README: work-machine notes from a fresh-install dry run.
- `pick --to` no longer crashes on Windows when ComfyUI has the old LoRA loaded: it writes a step-named copy (`<brand>-<lora>-s250.safetensors`) and `gen` uses it.

## 0.1.0 · 2026-10-16

First release: brand and sub-site LoRAs for on-brand UI mock-ups, with a training-free reference route and a code route. Tested end to end on GOV.UK, an openly licensed site: capture, tokens, dataset, captions, both mock-up routes, and an overnight brand plus residual site LoRA training run.

- Skills: `brandwright` (routes, kit, data and licence rules, common myths), `brandwright-capture`, `brandwright-train`, `brandwright-mockup`, each evergreen with research dated 2026-10-15.
- `bw.py`:
  - `new`, `doctor`, `import`;
  - `tokens`: DTCG-shaped `tokens.json` with per-site overrides, plus `brand.css` with the site's own CSS variables, `@font-face` rules and component recipes, including the primary button;
  - `prep`: viewport tiles, component specimens, perceptual and same-text dedupe, caps on repeated parts, brand and site datasets, template captions;
  - `caption`: a local vision model through Ollama, with a cache and style-word flags; the manifest is saved after every caption;
  - `review`, `score` (palette delta-E), `sheet` (cells sized to the pictures' aspect);
  - help text on every argument (the wiki's Commands page is generated from it).
- Training: `train` writes ostris ai-toolkit JSON for Z-Image, Z-Image Turbo, Qwen-Image-2512 or FLUX.2 klein base 4B. Site LoRAs train in residual mode (the brand LoRA is merged during training), continue mode or stack mode. `--run` starts the job detached, and `--run --wait` blocks until it ends. A retrain moves the earlier run's checkpoints aside so ai-toolkit starts from step 0; `--resume` continues that run instead. `status` and `pick` follow up. Default steps are about 5 passes over the dataset (400 to 1,500), with a checkpoint every 100 steps and 20 kept, because the first real run peaked at step 250 and had collapsed by step 500.
- Browser (Playwright): `login`, where the person signs in themselves; `capture`, with masking, overlay hiding, same-site crawl, `--cdp` and `--channel msedge`; `render` for the code route.
- ComfyUI: `gen` with LoRA chains and automatic triggers, `sweep` with a contact sheet, and `ref`, which uses FLUX.2 klein with up to 4 reference screenshots.
- Tests:
  - 23 offline tests;
  - eval cases for every skill (triggers, decoys and actions);
  - a browser smoke test on a fictional fixture site;
  - a size budget and a public-repository check, both in CI;
  - CI on Windows, macOS and Linux with Python 3.10 and 3.14.
