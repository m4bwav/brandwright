# Learnings: brandwright-train

Procedural lessons for [SKILL.md](SKILL.md). Research lives in [RESEARCH.md](RESEARCH.md); changes in [CHANGELOG.md](CHANGELOG.md); test runs in [TESTS.md](TESTS.md). Format and write-time gate: [MAINTENANCE.md](MAINTENANCE.md). Retired entries go to LEARNINGS-ARCHIVE.md.

## Active

### L-003 · 2026-10-16 · `toolkit-resumes-same-name`: a retrain under the same name continues the old run
- Trigger: before retraining the GOV.UK site LoRA, `train/out/<name>/` still held the 800-step run's checkpoints; ai-toolkit's `get_latest_save_path` loads the newest one from that folder and carries on from its step.
- Hypothesis: a 400-step retrain would have loaded step 750 and stopped at once, or trained on top of the collapsed LoRA, with no error.
- Rule: `bw.py train --run` moves an earlier run's folder aside unless `--resume` is passed; when running ai-toolkit by hand, rename or delete the old folder first.
- Evidence: ai-toolkit `jobs/process/BaseSDTrainProcess.py` (`get_latest_save_path`), C-20261016-2
- Scope: skill
- Status: active · helpful 0 · harmful 0 · last_confirmed 2026-10-16

### L-002 · 2026-10-16 · `trigger-drawn-as-wordmark`: LLM-encoder models write the trigger word into the header
- Trigger: the first trained LoRAs drew "GovkUI", "govirkUI" and "govikui" as the site name in headers, from the trigger `govukui`.
- Hypothesis: the training headers show the real wordmark, so the model ties the trigger to the logo text and renders it.
- Rule: when a header or logo shows, name its text in the prompt in quotes (`a header with the name "Acme"`); consider triggers that do not read as words.
- Evidence: T-20261016-1
- Scope: skill
- Status: active · helpful 0 · harmful 0 · last_confirmed 2026-10-16

### L-001 · 2026-10-16 · `ui-style-loras-peak-early`: pick from the first few hundred steps
- Trigger: 90 pictures, rank 32, lr 1e-4 on Z-Image: step 250 was the best sample set; 500, 750, 1,000 and 1,200 had collapsed into soft, near-empty layouts.
- Hypothesis: flat UI style is learned in about three passes; after that the many plain backgrounds and downscaled small text dominate.
- Rule: default to about 5 passes (5 steps a picture, 400 to 1,500), save every 100 steps, keep 20 saves, and pick by eye; lower lr or rank before adding steps.
- Evidence: T-20261016-1, C-20261016-1
- Scope: skill
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-16
