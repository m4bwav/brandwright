# HANDOFF

Updated 2026-10-17, around 14:45. Read with [log.md](log.md) and [next-session-prompt.md](next-session-prompt.md).

## State

- Public repo `m4bwav/brandwright`. **0.1.2 is the latest release** (tag `v0.1.2`, 2026-10-17). CI green on Windows, macOS and Linux, Python 3.10 and 3.14.
- Root CHANGELOG **Unreleased** has two doc changes, no code: the sub-skills say `python3` on macOS and Linux (PR #18), and the trigger is optional with the brand LoRA alone (test 4, PR #19). Not worth a release alone; release with the next code change, on the owner's yes.
- Installed for the owner as `brandwright@mark-local` (the Ai folder's directory marketplace, so it follows the checkout).
- Wiki: live at https://github.com/m4bwav/brandwright/wiki, Home and Commands at 0.1.2. Working copy `../brandwright.wiki` (upstream set; `git pull`, edit, `git push`). Commands page: `python ai-docs/notes/wiki-commands-page.py . ../brandwright.wiki/Commands.md` (reads the version from `bw.py`). Home names the latest release. Update both after the next release.
- Eval action cases: all 4 pass on Linux (WSL 2 Ubuntu on the owner's PC, 2026-10-17). Capture and render outcomes stop at missing Playwright in WSL.
- GOV.UK test kit (path in the owner's notes): **tests 1 to 4 are done.** Test 4 (mockup T-20261017-2) found the brand LoRA keeps the look without its trigger on Z-Image, naming the header text still fixes invented names, and brand + site LoRA without triggers fell back to photographs in one picture of two. Defaults stay (`gen` adds triggers; `--raw` is safe with the brand LoRA alone).
- ComfyUI's loras folder holds `govuk-brand-s250`, `govuk-design-system`, `govuk-ds-r2-s100/200/300`, `govuktrigb1-brand` and `govuktrigb2-brand`. The two trig LoRAs and kits `govuk-trig-b1`/`-b2` are test-3 leftovers; the owner may delete them (ask, do not delete unasked).

## Open

1. To prove capture and render on Linux too: `pip install playwright` and `playwright install chromium` inside WSL (about 150 MB download), then rerun action-3 and action-4. **Ask the owner first.**
2. Ideas not built (pick one only with the owner's interest; keep the size budget green):
   - an `export` command for musubi or OneTrainer configs (stdlib, no new dependency);
   - OCR text-accuracy scoring (would measure header text too; needs an optional OCR dependency);
   - DTCG import from dembrandt;
   - a Figma-friendly SVG export of code-route mock-ups;
   - optional `render --auth` to reuse the login session for fonts behind SSO (only if a work run shows font warnings).
3. Untested: whether the site LoRA alone (continue mode) needs its trigger. Test 4 covered brand alone and brand + residual site only.

## Gotchas

- Bash heredocs collapse `\\` to `\`: write Python patches with the Write tool, or build backslashes with `chr(92)`. Edit repo files in binary mode (they are LF).
- ComfyUI on the PC is shared with film sessions. Never `/free` it or start training while a render runs; the test runners wait for three idle checks a minute apart first. Film queues log to `<film>_run.log` in ComfyUI's video output folder and print `QUEUE EMPTY` at the end, but a film session can queue the next job minutes later. Test 4 waited 5 h 25 min for one.
- Waiting on a long run: a background until-loop that matches the done line, failure words and the runner's PID being gone, with a deadline under 2 h.
- Annotated tags carry the tagger's email: tag with `git -c user.name="Mark Rogers" -c user.email="156112+m4bwav@users.noreply.github.com" tag -a`, or GitHub refuses the push (GH007).
- `claude plugin eval` on Windows refuses cases granted Bash (no sandbox). Run them in WSL Ubuntu: clone the branch into the WSL home, then `claude plugin eval . --case "action-*" --scaffold --allow-tools Bash --trust-plugin --runs 1 -j 4 --no-publish`. Scaffolds run only with `--scaffold`, from the run's workspace (cwd). Kept temp dirs are sealed: `chmod 700` the dir and its `sealed/` to read `out/trace.jsonl`. One `--case` glob only.
- A 250-step Z-Image brand retraining (90 pictures, no samples) takes about 25 min. A base-graph gen of 2 pictures takes about 3 min.
- ComfyUI memory-maps loaded LoRAs, so a loaded file cannot be overwritten on Windows; `pick` writes a step-named copy.
- ai-toolkit resumes from any checkpoint in `train/out/<name>`; `train --run` moves an old run aside (`--resume` to continue it).
- `gh pr checks --watch` right after `gh pr create` can return "no checks reported" at once; wait about 20 s first (a foreground `sleep` is refused; just run the watch again).
- `bw.py sheet --cols 2 --out X.png <control pics> <test pics>` puts a control row above a test row: the quickest way to judge a run.
- evergreen `checked --use-time` needs `--m 0`; without it the history says "refresh failed".
