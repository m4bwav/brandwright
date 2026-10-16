# HANDOFF

Updated 2026-10-15 late evening. Read with [log.md](log.md) and [next-session-prompt.md](next-session-prompt.md).

## State

- Public repo `m4bwav/brandwright`, main green on Windows, macOS and Linux, Python 3.10 and 3.14, with the browser smoke test and guards. PRs #1 and #2 are merged. Version 0.1.0 is in the files, but there is no tag or GitHub Release yet: that needs the owner's go-ahead.
- Installed for the owner as `brandwright@mark-local` (the Ai folder's directory marketplace). The four skills are registered in the evergreen catalog, and lint passes.
- Wiki: 13 pages are committed in a sibling folder, `../brandwright.wiki` (branch master, remote set). GitHub creates the wiki's git repository only after someone saves the first page in the web UI, and the browser extension was not connected. A background loop was left polling `git ls-remote` and will push once the page exists. If that session has ended: `git -C ../brandwright.wiki pull --allow-unrelated-histories -X ours origin master`, then `git push origin master`.
- Real runs (GOV.UK, which is openly licensed, as the test brand; the kit is outside the repo):
  - capture of 22 pages × 2 viewports through Edge;
  - tokens: the real brand variables and the real green primary button;
  - prep: 105 pictures kept;
  - captions: Gemma 4 26B on the Mac;
  - code-route mock-up: exact, with a palette score of 0.9;
  - reference route on FLUX.2 klein: style carried over, short quoted labels right.
- Training ran overnight (2026-10-15 23:28 to 2026-10-16 03:51):
  - Brand LoRA: 1,200 steps in 2 h 29 min. The residual site LoRA: 800 steps in 1 h 49 min. Comparisons and a sweep followed. Everything exited 0, so residual mode works.
  - Findings: step 250 was the best brand checkpoint; from step 500 on, it had collapsed into soft, near-empty layouts. Defaults were lowered in PR #4.
  - The final LoRAs show only a weak effect on the Turbo graph, and the trigger word is drawn as the wordmark (train and mockup LEARNINGS).
  - The runner and the comparison images are in the kit folder (path in the owner's notes).

## Open

1. Re-pick the brand LoRA at step 250 (`bw.py pick KIT --lora brand --step 250 --to <ComfyUI loras>`). Retrain the site LoRA in residual mode on top of it with the new defaults (about 260 steps) and judge again on the base graph.
2. Base-model inference in ComfyUI needs `z_image_bf16.safetensors` (12.3 GB, Comfy-Org/z_image). It was not downloaded without the owner's yes. Until then the runs use the Turbo graph with base-trained LoRAs.
3. Run the `evals/` cases with `claude plugin eval` (none run yet). action-2 needs a fixture kit with a dataset.
4. Release 0.1.0 (tag and GitHub Release) after the owner's go-ahead; then refresh the wiki's version lines.
5. Ideas not built:
   - an `export` command for musubi or OneTrainer configs;
   - OCR text-accuracy scoring;
   - DTCG import from dembrandt;
   - a Figma-friendly SVG export of code-route mock-ups.

## Gotchas

- Bash heredocs collapse `\\` to `\`: write Python patches with the Write tool, or build backslashes with `chr(92)`. This bit four times in this session.
- `bw.py caption` against the Mac's Ollama took 15-60 s a picture, and much longer while the Mac was shared.
- ComfyUI on the PC is shared with film sessions. Never `/free` it or start training while a render runs.
