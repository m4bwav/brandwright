# ai-docs index

What past sessions learned here. Open only the entries whose line matches the task.

- [HANDOFF.md](HANDOFF.md): current state, open items, gotchas. Read when continuing work.
- [next-session-prompt.md](next-session-prompt.md): the kickoff prompt for the next session.
- [log.md](log.md): what happened, by date.
- [decisions/2026-10-15-three-routes-residual-site-loras-zimage-default.md](decisions/2026-10-15-three-routes-residual-site-loras-zimage-default.md): why code, reference and LoRA routes; why residual site LoRAs; why Z-Image; why kits stay out of repos. Read before changing the architecture or defaults.
- [research/2026-10-15-ui-lora-practice-and-fact-check.md](research/2026-10-15-ui-lora-practice-and-fact-check.md): fact-check of the usual two-LoRA advice; dataset, caption, multi-LoRA and evaluation practice; training-free and code routes. Read before changing capture, captions or the LoRA modes.
- [research/2026-10-15-models-trainers-licences.md](research/2026-10-15-models-trainers-licences.md): licences, text scores, VRAM, trainers, hosted training. Read before changing `MODELS` or quoting a licence.
- [research/2026-10-18-musubi-onetrainer.md](research/2026-10-18-musubi-onetrainer.md): musubi-tuner and OneTrainer job formats, flags and traps (`__version`, alpha default, docs path error). Read before changing `train --for`.
- [notes/wiki-commands-page.py](notes/wiki-commands-page.py): rebuilds the wiki's Commands page from `--help` (`python ai-docs/notes/wiki-commands-page.py . ../brandwright.wiki/Commands.md`).
