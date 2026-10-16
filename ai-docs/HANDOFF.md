# HANDOFF

Updated 2026-10-16, around 18:40. Read with [log.md](log.md) and [next-session-prompt.md](next-session-prompt.md).

## State

- Public repo `m4bwav/brandwright`. **0.1.1 is released** (tag `v0.1.1`, GitHub Release, 2026-10-16). `main` is ahead of it with PR #12 (residual site LoRAs sample less; CHANGELOG "Unreleased"). CI is green on Windows, macOS and Linux, Python 3.10 and 3.14.
- Installed for the owner as `brandwright@mark-local` (the Ai folder's directory marketplace, so it follows the checkout).
- The code route worked on the owner's work computer ("better than expected", mockup T-20261016-5). Nothing to fix.
- Wiki: live at https://github.com/m4bwav/brandwright/wiki, in step with `main` (Home at 0.1.1, Training has the new sampling defaults). Working copy `../brandwright.wiki` (upstream set; `git pull`, edit, `git push`). Commands page: `python ai-docs/notes/wiki-commands-page.py . ../brandwright.wiki/Commands.md` (reads the version from `bw.py`).
- GOV.UK test kit (path in the owner's notes):
  - tests 1 and 2 done (train T-20261016-1 and -3, mockup T-20261016-4);
  - **test 3 queued** (`run_test3.py`, log `run_test3.log`, started 18:33 and waiting for ComfyUI to be idle). It tests the trigger-as-wordmark problem; see the log entry for 2026-10-16, third session. Its two sibling kits are `govuk-trig-b1` and `govuk-trig-b2`. The owner approved its GPU time.
- ComfyUI's loras folder holds `govuk-brand-s250`, `govuk-design-system` and `govuk-ds-r2-s100/200/300`; test 3 adds `govuktrigb1-brand` and `govuktrigb2-brand`.

## Open

1. Read test 3's results (`run_test3.log` says `ALL DONE`; outputs under each kit's `out/`). Controls are test 2's brand-only gens of the start page and the status card (seed 11). Compare the header text:
   - A: does naming the header text in the prompt fix it with the old LoRA?
   - B1: does the non-word trigger `zqkvx` stop the wordmark?
   - B2: does quoting the logo text in captions fix it, and can the prompt then ask for the real logo?
   Then record train T-20261017-1 and update L-002. If B1 or B2 wins, propose to the owner the default change it implies: `make_trigger` without the brand's letters, and/or a `VLM_PROMPT` that quotes the header's site name instead of leaving logos out. Both change defaults, so ask first.
2. Release 0.1.2 with PR #12 and whatever comes of item 1. Ask the owner first.
3. Run the 4 action cases in `evals/` on macOS or Linux (needs a sandboxed shell). action-2 needs a fixture kit with a dataset.
4. Ideas not built:
   - an `export` command for musubi or OneTrainer configs;
   - OCR text-accuracy scoring (would measure item 1 too);
   - DTCG import from dembrandt;
   - a Figma-friendly SVG export of code-route mock-ups;
   - optional `render --auth` to reuse the login session for fonts behind SSO (only if a work run shows font warnings; the first work run showed none reported).

## Gotchas

- Bash heredocs collapse `\\` to `\`: write Python patches with the Write tool, or build backslashes with `chr(92)`.
- ComfyUI on the PC is shared with film sessions. Never `/free` it or start training while a render runs; the test runners wait for three idle checks a minute apart first.
- ComfyUI memory-maps loaded LoRAs, so a loaded file cannot be overwritten on Windows; `pick` writes a step-named copy.
- ai-toolkit resumes from any checkpoint in `train/out/<name>`; `train --run` moves an old run aside (`--resume` to continue it).
- ai-toolkit always draws a sample at the end of training, and never in the loop's first step; `skip_first_sample` drops only the step-0 baseline.
- `gh pr checks --watch` right after `gh pr create` can return "no checks reported" at once; wait about 20 s first.
- `claude plugin eval` takes one `--case` glob (a second replaces the first).
- evergreen `checked --use-time` needs `--m 0`; without it the history says "refresh failed".
