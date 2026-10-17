# HANDOFF

Updated 2026-10-17, around 12:20. Read with [log.md](log.md) and [next-session-prompt.md](next-session-prompt.md).

## State

- Public repo `m4bwav/brandwright`. **0.1.2 is released** (tag `v0.1.2`, GitHub Release, 2026-10-17): residual site LoRAs sample less (PR #12) and the header-text prompt rule (PR #15). CI green on Windows, macOS and Linux, Python 3.10 and 3.14. Root CHANGELOG has no Unreleased section yet.
- Installed for the owner as `brandwright@mark-local` (the Ai folder's directory marketplace, so it follows the checkout).
- Wiki: live at https://github.com/m4bwav/brandwright/wiki, Home and Commands at 0.1.2. Working copy `../brandwright.wiki` (upstream set; `git pull`, edit, `git push`). Commands page: `python ai-docs/notes/wiki-commands-page.py . ../brandwright.wiki/Commands.md` (reads the version from `bw.py`). Home names the latest release.
- Eval action cases: all 4 pass on Linux (WSL 2 Ubuntu on the owner's PC; skill TESTS entries dated 2026-10-17). action-2 to -4 have `fixture.sh` scaffolds. Capture and render outcomes stop at missing Playwright in WSL.
- GOV.UK test kit (path in the owner's notes): tests 1 to 3 done. **Test 4 is half done** (mockup T-20261017-2): `run_test4.py` in the kit, log `run_test4.log`, lock `run_test4.lock`. It ran 2 of 6 gens, then another session's film queue took ComfyUI at 08:42. The runner keeps waiting (3 idle checks a minute apart) and finishes by itself. It prints `ALL DONE` at the end.
- Test 4 so far: without the trigger the brand LoRA still gives the GOV.UK look (navy, white card, green button), and the header still invents a name. Naming the header text stays the fix.
- ComfyUI's loras folder holds `govuk-brand-s250`, `govuk-design-system`, `govuk-ds-r2-s100/200/300`, `govuktrigb1-brand` and `govuktrigb2-brand`. The two trig LoRAs and kits `govuk-trig-b1`/`-b2` are test-3 leftovers; the owner may delete them.

## Open

1. Finish test 4. If `run_test4.log` ends with `ALL DONE`, judge the 4 later runs against their controls (seed 11, base graph; each `out/*/mockup.json` names its prompt, LoRAs and seed, so the controls from tests 2 and 3 are easy to find). If the runner process is gone without `ALL DONE`, delete `run_test4.lock` and run only the missing gens (edit the runner or call `bw.py gen ... --raw` directly), only on an idle ComfyUI. Then record the verdict in mockup T-20261017-2, train L-002, and, if the trigger turns out optional, a line in the mockup prompt guide and the root CHANGELOG's Unreleased.
2. The sub-skills (capture, train, mockup) say `python`; only the hub says `python3` on macOS and Linux. Two eval runs retried after `python: command not found`. Small doc fix, optional.
3. To prove capture and render on Linux too: `pip install playwright` and `playwright install chromium` inside WSL (about 150 MB download), then rerun action-3 and action-4. Ask the owner first.
4. Ideas not built:
   - an `export` command for musubi or OneTrainer configs;
   - OCR text-accuracy scoring (would measure header text too);
   - DTCG import from dembrandt;
   - a Figma-friendly SVG export of code-route mock-ups;
   - optional `render --auth` to reuse the login session for fonts behind SSO (only if a work run shows font warnings).

## Gotchas

- Bash heredocs collapse `\\` to `\`: write Python patches with the Write tool, or build backslashes with `chr(92)`.
- ComfyUI on the PC is shared with film sessions. Never `/free` it or start training while a render runs; the test runners wait for three idle checks a minute apart first. Film queues log to `<film>_run.log` in ComfyUI's video output folder and print `QUEUE EMPTY` at the end, but a film session can queue the next job minutes later.
- Waiting on a long run: a background until-loop that matches the done line and failure words, with a deadline under 2 h, re-armed each time it ends.
- Annotated tags carry the tagger's email: tag with `git -c user.name="Mark Rogers" -c user.email="156112+m4bwav@users.noreply.github.com" tag -a`, or GitHub refuses the push (GH007).
- `claude plugin eval` on Windows refuses cases granted Bash (no sandbox). Run them in WSL Ubuntu: clone the branch into the WSL home, then `claude plugin eval . --case "action-*" --scaffold --allow-tools Bash --trust-plugin --runs 1 -j 4 --no-publish`. Scaffolds run only with `--scaffold`, from the run's workspace (cwd), so fixtures are written inline. Kept temp dirs are sealed: `chmod 700` the dir and its `sealed/` to read `out/trace.jsonl`.
- `claude plugin eval` takes one `--case` glob (a second replaces the first).
- A 250-step Z-Image brand retraining (90 pictures, no samples) took about 25 min. A base-graph gen of 2 pictures takes about 3 min.
- ComfyUI memory-maps loaded LoRAs, so a loaded file cannot be overwritten on Windows; `pick` writes a step-named copy.
- ai-toolkit resumes from any checkpoint in `train/out/<name>`; `train --run` moves an old run aside (`--resume` to continue it). It always draws a sample at the end and never in the loop's first step.
- `gh pr checks --watch` right after `gh pr create` can return "no checks reported" at once; wait about 20 s first.
- evergreen `checked --use-time` needs `--m 0`; without it the history says "refresh failed".
