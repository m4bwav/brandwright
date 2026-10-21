# ai-docs index

What past sessions learned here. Open only the entries whose line matches the task.

- [HANDOFF.md](HANDOFF.md): current state, open items, gotchas. Read when continuing work.
- [next-session-prompt.md](next-session-prompt.md): the kickoff prompt for the next session.
- [log.md](log.md): what happened, by date.
- [decisions/2026-10-15-three-routes-residual-site-loras-zimage-default.md](decisions/2026-10-15-three-routes-residual-site-loras-zimage-default.md): why code, reference and LoRA routes; why residual site LoRAs; why Z-Image; why kits stay out of repos. Read before changing the architecture or defaults.
- [notes/cli-diff-run.py](notes/cli-diff-run.py): runs 50 CLI commands against fakes (ComfyUI, ai-toolkit) and prints a transcript; diff old and new scripts to prove a refactor changes nothing. Read before cutting or restructuring the CLI.
- [research/2026-10-15-ui-lora-practice-and-fact-check.md](research/2026-10-15-ui-lora-practice-and-fact-check.md): fact-check of the usual two-LoRA advice; dataset, caption, multi-LoRA and evaluation practice; training-free and code routes. Read before changing capture, captions or the LoRA modes.
- [research/2026-10-15-models-trainers-licences.md](research/2026-10-15-models-trainers-licences.md): licences, text scores, VRAM, trainers, hosted training. Read before changing `MODELS` or quoting a licence.
- [research/2026-10-18-musubi-onetrainer.md](research/2026-10-18-musubi-onetrainer.md): musubi-tuner and OneTrainer job formats, flags and traps (`__version`, alpha default, docs path error). Read before changing `train --for`.
- [research/2026-10-18-train-refresh.md](research/2026-10-18-train-refresh.md): brandwright-train refresh: licences and the Qwen ARA re-checked, MOSS-Image and FLUX 3 klein trainable in ai-toolkit, musubi cu130 extras, convrot quant types. Read before adding a model to `MODELS` or quoting a licence.
- [notes/wiki-commands-page.py](notes/wiki-commands-page.py): rebuilds the wiki's Commands page from `--help` (`python ai-docs/notes/wiki-commands-page.py . ../brandwright.wiki/Commands.md`).
