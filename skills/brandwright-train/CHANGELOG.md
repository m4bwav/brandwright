# Changelog: brandwright-train

Every change to [SKILL.md](SKILL.md) and its companions, newest first, each with the reason (`R-` findings in [RESEARCH.md](RESEARCH.md), `L-` lessons in [LEARNINGS.md](LEARNINGS.md), `T-` runs in [TESTS.md](TESTS.md)). Protocol: [MAINTENANCE.md](MAINTENANCE.md).

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
