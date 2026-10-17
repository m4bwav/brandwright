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
- The owner created the wiki's first page. The watcher merged it and pushed all 13 pages at 06:59 on 2026-10-16. The wiki is live.
- Second session of the day (the owner said yes to the 12.3 GB download and to tagging the release):
  - Downloaded `z_image_bf16.safetensors` (Comfy-Org/z_image, SHA-256 checked) into ComfyUI's diffusion_models, so the `zimage` base graph can run.
  - Released 0.1.0: PR #6 brought the CHANGELOG entry up to date and fixed retrains (ai-toolkit resumes from any checkpoint in `train/out/<name>`, so `train --run` now moves that folder aside; `--resume` keeps it). Tag `v0.1.0` and the GitHub Release are published.
  - PR #7: `pick --to` crashed with WinError 1224 because ComfyUI had the old LoRA memory-mapped; it now writes a step-named copy and points `comfy_loras` at it.
  - First `claude plugin eval` run (PR #8): triggers 5/5 with the plugin and 0/5 without, decoys 6/6. The 4 action cases cannot run on Windows: the runner refuses a shell grant without a sandbox, and the Mac has no SSH.
  - Wiki: Commands page regenerated, Training page has the retrain and pick notes, Home links the release.
  - Test 2 started at 07:27 (runner `run_test2.py` in the kit): brand LoRA picked at step 250, site LoRA retrained in residual mode with the new defaults (400 steps, samples every 100), then judged on the base graph. Sampling during training takes about 2 min a picture (8 min a set of 4).
  - The owner plans to try the code route on a work computer. A fresh-install dry run of the README quick start (v0.1.0 clone, venv with Playwright only, Edge, public GOV.UK pages) found three gaps, fixed in PR #9: a short crawl gave a browser-default primary button, `render` hid font-load failures, and a guessed `--bw-*` name hid behind a `var()` fallback. README, wiki, capture L-002 and mockup L-003/L-004 record them.
  - Test 2 finished at 10:13. Site LoRA: 400 steps in 2 h 1 min (40 min of it sample sets). On the Z-Image base graph, brand (step 250) + residual site LoRA gave recognisable design-system pages: masthead, header, green start button, even its arrow at brand 1.4. Turbo stayed generic. Base graph about 78 s a picture against 13 s on Turbo. ai-toolkit leaves the brand LoRA out of residual samples, so site checkpoints are judged with gen or sweep (train L-005). Recorded in train T-20261016-3, mockup T-20261016-4 and L-002.
- Third session (evening):
  - The owner ran the code route on a work computer: it "worked better than expected", nothing to fix (mockup T-20261016-5). Company details stay in the owner's private notes.
  - Released 0.1.1 on the owner's yes (PR #11, tag `v0.1.1`, GitHub Release): the pick fix (PR #7) and the code-route fixes (PR #9).
  - Residual site LoRAs sample less (PR #12, owner chose the default from test 2's numbers): 2 prompts every 200 steps, no step-0 sample, so about 8 instead of 40 minutes on a 400-step run. Brand LoRAs keep 4 at every checkpoint. New `--sample-every`; `--samples 0` sets ai-toolkit's `disable_sampling`. `skip_first_sample` and `disable_sampling` are `TrainConfig` fields; the in-loop sampler skips the first step and a final sample is always drawn at the end, so 400 steps every 200 gives sets at 200 and 400.
  - Wiki: Home at 0.1.1, Training has the new sampling defaults, Commands regenerated. The Commands generator now reads the version from `bw.py` and says when `main` has unreleased changes.
  - Trigger words drawn as wordmarks (train L-002): test 2's sweep still shows "govuk" and "GovUKDesignSy..." in the headers. Likely cause: the trigger `govukui` spells the brand, and the caption prompt (`VLM_PROMPT`) tells the vision model to leave logos out, so nothing in the captions accounts for the masthead text except the trigger. Only 8 of 90 brand captions quote "GOV..." text; about 25 pictures show the masthead.
  - Test 3 (runner `run_test3.py` in the kit, log `run_test3.log`; the owner said yes to the GPU time) waits for ComfyUI to be idle, then: A) existing LoRAs with prompts naming the header text ("GOV.UK" logo, or another name); B1) brand LoRA retrained to 250 steps with the non-word trigger `zqkvx`; B2) the same plus "The header shows the "GOV.UK" logo." on the 25 masthead captions. Kits `govuk-trig-b1` and `govuk-trig-b2` sit next to the test kit. Then the same 3 prompts on each.
  - evergreen: `checked --use-time` without `--m` records a failed refresh; pass `--m 0 --note ...` (fixed in brandwright-train's evergreen.json).
- Fourth session (19:00): test 3 was still waiting at 18:45, with ComfyUI busy on a film render queue (7 parts of about 1 to 1.7 h each left), so it should start around 04:00 to 06:00 on 2026-10-17. Not restarted.
  - Checked the runner with no GPU use. Sibling kit captions are right: `zqkvx` on all 90, and the logo sentence on 25 in b2. A config-only `train` on a scratch copy of b1 matches test 1's model block. `pick` with no `--step` takes the final file.
  - The owner chose to wait for test 3 and ship one 0.1.2 (PR #12 plus any default test 3 justifies).

## 2026-10-17

- Fifth session (from 22:12 on 2026-10-16): waited for test 3 with background until-loops (re-armed every 1 h 55 min). The film queue ended at 03:35; test 3 started at 03:37 and printed `ALL DONE` at 04:50 (each 250-step brand retraining took about 25 min, faster than the 2 h guessed).
- Results (train T-20261017-1): naming the header text in the prompt fixes the drawn wordmark with the old LoRA ("GOV.UK" and "Fishing Service" right in 4 of 4 brand-only pictures). The non-word trigger `zqkvx` was printed in the page in 4 of 6 pictures and the cards drifted off brand; quoting the logo text in captions did not make plain prompts draw it. So no default change: `make_trigger` and `VLM_PROMPT` stay. The rule went into the mockup prompt guide (mockup C-20261017-1), L-002 was updated, and the root CHANGELOG's Unreleased section has it.
- Idea from it: test generation without the trigger in the prompt (the trigger itself is what gets printed; on a language-model encoder a LoRA may not need it). Not run.
