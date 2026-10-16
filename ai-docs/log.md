# Log

Append-only, newest last.

## 2026-10-15

- The owner asked for a plugin to build brand and sub-site LoRAs for mock-ups of new components, after a chat assistant's advice: check the research, build the "ultimate" version, publish a public repo with modernization and a wiki, and make it usable at work the next day.
- Research: two subagents. One fact-checked the advice and covered UI LoRA practice ([note](research/2026-10-15-ui-lora-practice-and-fact-check.md)); the other covered models, trainers and licences ([note](research/2026-10-15-models-trainers-licences.md)). Verified in the ai-toolkit source on disk:
  - `assistant_lora_path`: merged during training, off for samples. This is the residual mode.
  - `pretrained_lora_path`: this is the continue mode.
  - JSON configs are accepted.
- Design: [decision](decisions/2026-10-15-three-routes-residual-site-loras-zimage-default.md).
- Built:
  - four skills and the CLI (`bw.py`, `bw_browser.py`, `bw_comfy.py`);
  - 23 offline tests and a browser smoke test on a fictional fixture site;
  - budget and public-repository guards, and CI on three operating systems.
- Real runs on GOV.UK (an openly licensed site):
  - Capture: 44 page views.
  - Tokens: the real brand variables. A primary-button recipe was added after the first `brand.css` copied the most common button, a plain one.
  - prep: 105 kept.
  - Captions: Gemma 4 26B on the Mac. A crash in the style-word check was fixed in PR #1.
  - Code-route mock-up: exact.
  - Reference route: worked, with only short quoted labels right.
  - Banner and icon: made through `bw.py gen` on Z-Image Turbo.
- Published `m4bwav/brandwright` (public). PR #1 (caption fix, help text) and PR #2 (banner, icon, `train --wait`, contact sheets, test records) were both merged on green.
- Installed `brandwright@mark-local` and registered the four skills in the evergreen catalog.
- The wiki is written (13 pages) and waits for its first page to be created on GitHub.
- The training test is queued for when the PC's GPU is free; see [HANDOFF.md](HANDOFF.md).

## 2026-10-16

- The overnight test ran to completion. Brand LoRA (Z-Image base, 90 pictures): 2 h 29 min for 1,200 steps. Residual site LoRA: 1 h 49 min for 800 steps. Then gen and sweep on the Turbo graph.
- Step 250 was the best brand checkpoint; later steps collapsed. Default steps were cut to 5 a picture (400-1,500), with saves every 100 steps and 20 kept (PR #4).
- Base-trained LoRAs are weak on Turbo, and the trigger word gets drawn as the wordmark. Both are recorded as LEARNINGS.
