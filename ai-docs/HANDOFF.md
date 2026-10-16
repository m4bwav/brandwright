# HANDOFF

Updated 2026-10-16, around 10:45. Read with [log.md](log.md) and [next-session-prompt.md](next-session-prompt.md).

## State

- Public repo `m4bwav/brandwright`. **0.1.0 is released** (tag `v0.1.0`, GitHub Release, 2026-10-16). `main` is ahead of it with PRs #7 and #9 (see CHANGELOG "Unreleased"). CI is green on Windows, macOS and Linux, Python 3.10 and 3.14.
- Installed for the owner as `brandwright@mark-local` (the Ai folder's directory marketplace, so it follows the checkout).
- Wiki: live at https://github.com/m4bwav/brandwright/wiki. Working copy `../brandwright.wiki` (upstream set; `git pull`, edit, `git push`). Commands page: `python ai-docs/notes/wiki-commands-page.py . ../brandwright.wiki/Commands.md`. It covers 0.1.0 and the PR #9 code-route notes.
- ComfyUI on the PC now has `z_image_bf16.safetensors` (Z-Image base, 12.3 GB, SHA-256 checked), so the `zimage` graph runs.
- GOV.UK test kit (path in the owner's notes):
  - test 1 ran overnight;
  - test 2 (`run_test2.py`, log `run_test2.log`) ran 07:25-10:13 on 2026-10-16. Results are in brandwright-train T-20261016-3 and brandwright-mockup T-20261016-4.
  - On the base graph, brand (step 250) + residual site LoRA give recognisably on-brand pages, at about 78 s a picture against 13 s on Turbo.
  - ComfyUI's loras folder now holds `govuk-brand-s250.safetensors`, `govuk-design-system.safetensors` and `govuk-ds-r2-s100/200/300.safetensors`. `brand.json` points `brand` at the s250 copy.
- Evals: the first `claude plugin eval` run passed all trigger (5/5) and decoy (6/6) cases. The 4 action cases cannot run on Windows (the runner refuses a shell grant without a sandbox) and the Mac has no SSH.
- The owner is about to try the code route on a work computer. PR #9 (from a fresh-install dry run) fixed the browser-default primary button, added font-load warnings to `render`, and listed the real `--bw-*` names. README has the work-machine notes.

## Open

1. Ask the owner whether to release 0.1.1 with PRs #7 and #9 (the code-route fixes matter for work use). Releases need the owner's yes.
2. Sampling cost: 5 sample sets of 4 took about 40 of 121 minutes in test 2, and residual samples leave out the brand LoRA anyway (train L-005). Consider defaulting `--samples 2` for site LoRAs, or sampling every 200 steps. This changes a default, so check with the owner.
3. Trigger words are drawn as wordmarks (train L-002). Try triggers that do not read as words, or prompts that name the header text.
4. Run the 4 action cases in `evals/` on macOS or Linux (needs a sandboxed shell). action-2 needs a fixture kit with a dataset.
5. Ideas not built:
   - an `export` command for musubi or OneTrainer configs;
   - OCR text-accuracy scoring;
   - DTCG import from dembrandt;
   - a Figma-friendly SVG export of code-route mock-ups;
   - optional `render --auth` to reuse the login session for fonts behind SSO (only if a work run shows font warnings).

## Gotchas

- Bash heredocs collapse `\\` to `\`: write Python patches with the Write tool, or build backslashes with `chr(92)`.
- ComfyUI on the PC is shared with film sessions. Never `/free` it or start training while a render runs; `run_test2.py` waits for three idle checks a minute apart first.
- ComfyUI memory-maps loaded LoRAs, so a loaded file cannot be overwritten on Windows; `pick` now writes a step-named copy.
- ai-toolkit resumes from any checkpoint in `train/out/<name>`; `train --run` moves an old run aside (`--resume` to continue it).
- `gh pr checks --watch` right after `gh pr create` can return "no checks reported" at once; wait about 20 s first.
- `claude plugin eval` takes one `--case` glob (a second replaces the first).
