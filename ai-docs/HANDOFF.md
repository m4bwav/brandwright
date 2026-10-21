# HANDOFF

Updated 2026-10-21 (eleventh session). Read with [log.md](log.md) and [next-session-prompt.md](next-session-prompt.md).

## State

- Public repo `m4bwav/brandwright`. **0.1.4 is the latest release** (tag `v0.1.4`, 2026-10-21): the 2026-10-18 train reference refresh and the budget cut, no behaviour change. 0.1.3 (2026-10-18) brought `train --for musubi|onetrainer`. CI green on Windows, macOS and Linux, Python 3.10 and 3.14. Nothing unreleased.
- The size budget is **green on every row** since 2026-10-21 (released in 0.1.4): CLI 1,991 lines (green up to 2,000), installed skills folder 223 KB (green up to 250). Headroom is small on the CLI: about 9 lines. Before adding a feature, look for cuts first; prove any refactor with `ai-docs/notes/cli-diff-run.py` (old vs new transcripts must match). The three sub-skills' MAINTENANCE.md point to the hub's full copy; a future evergreen refresh must not paste the full protocol back into them.
- Installed for the owner as `brandwright@mark-local` (the Ai folder's directory marketplace, so it follows the checkout).
- Wiki: live at https://github.com/m4bwav/brandwright/wiki, Home, footer and Commands at 0.1.4. Working copy `../brandwright.wiki` (`git pull`, edit, `git push`). Commands page: `python ai-docs/notes/wiki-commands-page.py . ../brandwright.wiki/Commands.md`.
- `train --for musubi|onetrainer` writes jobs from formats read in source (research/2026-10-18-musubi-onetrainer.md). **Neither trainer has run them.**
- Linux: `tests/smoke_browser.py` passes in WSL 2 Ubuntu (venv `~/bw-venv`). The 4 eval action cases pass there, but capture and render cannot run inside `claude plugin eval` (sealed HOME, no env passthrough, network allowlist), so the smoke test is the proof.
- GOV.UK test kit (path in the owner's notes): tests 1 to 4 done; test-3 leftovers deleted 2026-10-18 (their pictures are in the kit's `test3-outputs`). ComfyUI keeps `govuk-brand-s250`, `govuk-brand`, `govuk-design-system` and `govuk-ds-r2-s100/200/300`.
- brandwright-train was refreshed 2026-10-18 (R-20261018-2, research/2026-10-18-train-refresh.md): all claims hold, defaults unchanged; MOSS-Image and FLUX 3 klein are now trainable in ai-toolkit (named in models.md, not in `MODELS`). It is verify-at-use, so it has no calendar date: claim 1 is due 2026-10-30, claims 2-4 on 2026-11-01 (`evergreen.py claims skills/brandwright-train --due`).
- Nothing is running. brandwright-train claims: claim 1 due 2026-10-30, claims 2-4 on 2026-11-01. The hub skill's next_due is 2026-10-29.

## Open

1. Prove `--for` on a real trainer: install musubi-tuner (or OneTrainer) and train the GOV.UK brand LoRA from the exported job, then compare with the ai-toolkit LoRA in `bw.py sheet`. Needs the owner's yes: a trainer install, model downloads and GPU time.
2. Ideas not built (pick one only with the owner's interest; the CLI has about 9 lines of green headroom):
   - OCR text-accuracy scoring (would measure header text; needs an optional OCR dependency);
   - DTCG import from dembrandt;
   - a Figma-friendly SVG export of code-route mock-ups;
   - optional `render --auth` to reuse the login session for fonts behind SSO (only if a work run shows font warnings).
3. Untested: whether the site LoRA alone (continue mode) needs its trigger.
4. (Done 2026-10-21: 0.1.4 released.)
5. Untested: MOSS-Image for UI (text quality, 16 GB training) and FLUX 3 klein on 16 GB. Only worth trying with the owner's yes (downloads, GPU).

## Gotchas

- Bash heredocs collapse `\\` to `\`: write Python patches with the Write tool, or build backslashes with `chr(92)`. Edit repo files in binary mode (they are LF).
- ComfyUI on the PC is shared with film sessions. Never `/free` it or start training while a render runs; the test runners wait for three idle checks a minute apart first.
- Annotated tags carry the tagger's email: tag with `git -c user.name="Mark Rogers" -c user.email="156112+m4bwav@users.noreply.github.com" tag -a`, or GitHub refuses the push (GH007).
- `claude plugin eval` on Windows refuses cases granted Bash (no sandbox). Run them in WSL Ubuntu from the clone `~/bw-eval`: `claude plugin eval . --case "action-*" --scaffold --allow-tools Bash --trust-plugin --runs 1 -j 4 --no-publish`. One `--case` glob only, and no `[34]` brackets. Add `--keep-temp` to read traces (`chmod 700` the temp dir and its `sealed/`, then `out/trace.jsonl`); `--ablation none` skips the no-plugin arm.
- Running WSL commands from the Bash tool: Git Bash expands `$PATH` and `$HOME` inside double quotes and rewrites `/home/...` paths. Put the commands in a script in the scratchpad and run `MSYS_NO_PATHCONV=1 wsl -d Ubuntu -- bash -c "tr -d '\r' < /mnt/c/.../script.sh | bash -l"`.
- `gh pr checks --watch` right after `gh pr create` can say "no checks reported"; run it again.
- `bw.py sheet --cols 2 --out X.png <control pics> <test pics>` puts a control row above a test row: the quickest way to judge a run.
- evergreen `checked --use-time` needs `--m 0`; without it the history says "refresh failed".
- A 250-step Z-Image brand retraining (90 pictures, no samples) takes about 25 min; ComfyUI memory-maps loaded LoRAs, so `pick` writes a step-named copy; ai-toolkit resumes from any checkpoint in `train/out/<name>` (`train --run` moves an old run aside).
