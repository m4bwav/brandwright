# HANDOFF

Updated 2026-10-17, around 05:15. Read with [log.md](log.md) and [next-session-prompt.md](next-session-prompt.md).

## State

- Public repo `m4bwav/brandwright`. **0.1.1 is released** (tag `v0.1.1`, 2026-10-16). `main` is ahead of it with PR #12 (residual site LoRAs sample less) and PR #15 (test 3 results, header-text prompt rule). Both are under "Unreleased" in the root CHANGELOG. CI is green on Windows, macOS and Linux, Python 3.10 and 3.14.
- **0.1.2 waits for the owner's go-ahead to tag.** It is PR #12 plus PR #15's docs. No default changed after test 3.
- Installed for the owner as `brandwright@mark-local` (the Ai folder's directory marketplace, so it follows the checkout).
- Wiki: live at https://github.com/m4bwav/brandwright/wiki, in step with `main` (Mock-ups and FAQ have the header-text rule as of 2026-10-17). Working copy `../brandwright.wiki` (upstream set; `git pull`, edit, `git push`). Commands page: `python ai-docs/notes/wiki-commands-page.py . ../brandwright.wiki/Commands.md` (reads the version from `bw.py`). Home names the latest release, so update it when 0.1.2 is tagged.
- GOV.UK test kit (path in the owner's notes): tests 1, 2 and 3 done (train T-20261016-1, -3, T-20261017-1; mockup T-20261016-4). Test 3 ran 03:37 to 04:50 on 2026-10-17, after the film queue ended.
- Test 3 verdict: name the header text in the prompt in quotes; it fixes the drawn wordmark with the existing LoRA. A non-word trigger (`zqkvx`) is printed in the page more often and carries less brand; quoting the logo in captions does not teach it. So `make_trigger` and `VLM_PROMPT` stay (train L-002).
- ComfyUI's loras folder holds `govuk-brand-s250`, `govuk-design-system`, `govuk-ds-r2-s100/200/300`, `govuktrigb1-brand` and `govuktrigb2-brand`. The two trig LoRAs and kits `govuk-trig-b1`/`-b2` are test leftovers; the owner may delete them.

## Open

1. Ask the owner for the go-ahead to tag 0.1.2 (bump the version everywhere AGENTS.md lists, move "Unreleased" under `## 0.1.2 · DATE`, tag `v0.1.2`, GitHub Release with that entry, wiki Home and Commands page). Do not tag without a yes.
2. Idea from test 3, not run: generate without the trigger in the prompt (`gen --raw` with the prompt written out). The trigger is what gets printed; on a language-model text encoder the LoRA may not need it. Needs GPU time, so the owner's yes and an idle ComfyUI.
3. Run the 4 action cases in `evals/` on macOS or Linux (needs a sandboxed shell). action-2 needs a fixture kit with a dataset.
4. Ideas not built:
   - an `export` command for musubi or OneTrainer configs;
   - OCR text-accuracy scoring (would measure header text too);
   - DTCG import from dembrandt;
   - a Figma-friendly SVG export of code-route mock-ups;
   - optional `render --auth` to reuse the login session for fonts behind SSO (only if a work run shows font warnings).

## Gotchas

- Bash heredocs collapse `\\` to `\`: write Python patches with the Write tool, or build backslashes with `chr(92)`.
- ComfyUI on the PC is shared with film sessions. Never `/free` it or start training while a render runs; the test runners wait for three idle checks a minute apart first. Film queues log to `<film>_run.log` in ComfyUI's video output folder and print `QUEUE EMPTY` at the end.
- Waiting on a long run: a background until-loop that matches the done line and failure words, with a deadline under 2 h, re-armed each time it ends.
- A 250-step Z-Image brand retraining (90 pictures, no samples) took about 25 min, not the hour guessed.
- ComfyUI memory-maps loaded LoRAs, so a loaded file cannot be overwritten on Windows; `pick` writes a step-named copy.
- ai-toolkit resumes from any checkpoint in `train/out/<name>`; `train --run` moves an old run aside (`--resume` to continue it).
- ai-toolkit always draws a sample at the end of training, and never in the loop's first step; `skip_first_sample` drops only the step-0 baseline.
- `gh pr checks --watch` right after `gh pr create` can return "no checks reported" at once; wait about 20 s first.
- `claude plugin eval` takes one `--case` glob (a second replaces the first).
- evergreen `checked --use-time` needs `--m 0`; without it the history says "refresh failed".
