# Changelog: brandwright-train

Every change to [SKILL.md](SKILL.md) and its companions, newest first, each with the reason (`R-` findings in [RESEARCH.md](RESEARCH.md), `L-` lessons in [LEARNINGS.md](LEARNINGS.md), `T-` runs in [TESTS.md](TESTS.md)). Protocol: [MAINTENANCE.md](MAINTENANCE.md).

### C-20261021-1 · 2026-10-21 · MAINTENANCE.md points to the hub's copy
- because: owner's choice on 2026-10-21 to cut the installed skills folder back under 250 KB; the four MAINTENANCE.md files were the same 9.6 KB protocol copy
- files: MAINTENANCE.md
- The full protocol now lives once in [../brandwright/MAINTENANCE.md](../brandwright/MAINTENANCE.md), which always ships in the same plugin; this file keeps Step 0 in short and the link.

### C-20261018-2 · 2026-10-18 · refresh: new trainable models, setup notes
- because: R-20261018-2
- files: references/models.md (table, header), references/setup.md (ostris ai-toolkit, Other trainers), RESEARCH.md (Current understanding: step defaults brought in line with SKILL.md after L-001; Open questions; Search plan)
- Two new trainable models and four setup notes; defaults unchanged.

### C-20261018-1 · 2026-10-18 · `train --for musubi|onetrainer`
- because: R-20261018-1 (musubi-tuner v0.3.6 and OneTrainer b08db37 job formats); HANDOFF idea chosen by the owner
- files: SKILL.md (command line), references/setup.md (Other trainers), ../brandwright/scripts/bw.py (`export_config`, `MUSUBI`, `ONETRAINER`)
- People whose training machine runs musubi-tuner or OneTrainer get the same job without rewriting it by hand. Residual maps to musubi `--base_weights`; OneTrainer refuses it.

### C-20261017-3 · 2026-10-17 · L-002 extended with test 4
- because: ../brandwright-mockup T-20261017-2
- files: LEARNINGS.md (L-002)
- Leaving the trigger out does not stop invented header names, and the brand LoRA carries the look without it. `make_trigger` stays.

### C-20261017-2 · 2026-10-17 · `python3` on macOS and Linux
- because: ../brandwright T-20261017-1, the Linux eval run (2 of 4 agents typed `python`, got `command not found` and retried with `python3`)
- files: SKILL.md (BW line), references/setup.md (venv on Linux and macOS)
- The `BW` line says `python3` on macOS and Linux, as the hub does, and the setup reference makes the venv with `python3 -m venv venv` there.

### C-20261017-1 · 2026-10-17 · trigger shape kept after test 3
- because: T-20261017-1, L-002
- files: TESTS.md, LEARNINGS.md (L-002)
- Test 3 found that naming the header text in the prompt fixes the drawn wordmark, and that a non-word trigger or logo-quoting captions do not. `make_trigger` and `VLM_PROMPT` stay as they are; the prompt rule went to the mockup skill.

### C-20261016-5 · 2026-10-16 · fewer samples for residual site LoRAs
- because: T-20261016-3, L-005; the owner chose this default on 2026-10-16
- files: ../brandwright/scripts/bw.py (train_config, cmd_train, --samples, --sample-every), SKILL.md (Step 3 defaults), ../../tests/test_bw.py
- In test 2, 5 sample sets of 4 took about 40 of the site LoRA's 121 minutes, and residual samples leave the brand LoRA out anyway. Residual site LoRAs now sample 2 prompts every 200 steps with no step-0 sample (about 8 min for 400 steps); brand LoRAs keep 4 at every checkpoint. `--samples 0` sets ai-toolkit's `disable_sampling`; field names checked in ai-toolkit's `TrainConfig` (2026-10-09 checkout).

### C-20261016-4 · 2026-10-16 · judge residual checkpoints on brand + site
- because: T-20261016-3, L-005
- files: SKILL.md (Step 5)
- The skill says residual samples leave the brand LoRA out, and to pick site checkpoints with gen or sweep.

### C-20261016-3 · 2026-10-16 · pick survives a running ComfyUI
- because: L-004
- files: ../brandwright/scripts/bw.py (cmd_pick), ../../tests/test_bw.py
- When the ComfyUI copy cannot be replaced, `pick` writes `<brand>-<lora>-s<step>.safetensors` instead and points `comfy_loras` at it.

### C-20261016-2 · 2026-10-16 · retrains start fresh
- because: L-003
- files: ../brandwright/scripts/bw.py (set_aside_old_run, train --resume), SKILL.md (Step 5), ../../tests/test_bw.py
- `train --run` moves an earlier run's checkpoints to `train/out/<name>-run-<date>` so ai-toolkit starts at step 0; `--resume` keeps the old behaviour.

### C-20261016-1 · 2026-10-16 · fewer steps, checkpoints every 100
- because: T-20261016-1, L-001
- files: ../brandwright/scripts/bw.py (train_config, --steps, --save-every), SKILL.md (Step 3, Step 5), ../../tests/test_bw.py
- Default steps 5 a picture within 400 to 1,500 (was 40 within 1,200 to 3,000); save every 100 steps (was 250) and keep 20 saves so the early winners survive.

### C-20261015-1 · 2026-10-15 · Created
- because: user request (brand and sub-site LoRAs for mock-ups of new components, usable at work), R-20261015-1
- files: SKILL.md, references/, evals/evals.json
- First version.
