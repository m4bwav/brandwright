# Next session: brandwright

You are continuing brandwright, a public agent plugin (`m4bwav/brandwright`) for on-brand UI mock-ups from a brand's own sites (code route, reference route, and brand plus residual sub-site LoRAs).

Read first, in order: `AGENTS.md`, `ai-docs/HANDOFF.md` (state, open items, gotchas), then only the research or decision notes the step needs (`ai-docs/INDEX.md`). The owner's private notes (vault) give the test kit's location.

Before you rely on it, check that this prompt is not older than `HANDOFF.md` and the newest `run_test.log`. If it is, trust those.

## This step

1. Find out whether the GOV.UK training test ran: `run_test.log` and `bw.py status <kit>`.
   - If it has not started and the PC's ComfyUI queue is busy, do not free it or start training over a render. Re-check later, or leave it to the ready-job row `bw-govuk-1`.
   - If it ran:
     - look at the training samples, the `out/` comparisons (no LoRA / brand / brand + design-system, same seed) and `sweep.jpg`;
     - judge whether the brand LoRA adds the brand, and whether the residual site LoRA adds the site's look on top;
     - write T- entries in brandwright-train and brandwright-mockup TESTS.md, and LEARNINGS for anything surprising (weights that work on the Turbo graph, the step count that looked best).
   - If it failed, fix the cause in `bw.py` (with a test) and re-queue it under a new ready-job id.
2. If the wiki is still not live (`git ls-remote https://github.com/m4bwav/brandwright.wiki.git` fails), ask the owner to click "Create the first page", then push `../brandwright.wiki` (HANDOFF has the commands).
3. Run the eval cases in `evals/` once with `claude plugin eval` and record them in TESTS.md.

## Rules

- Changes go through a branch and a PR. Merge your own PR once checks pass (this repository is the owner's alone and nobody downloads it from a registry yet). Releases and tags need the owner's go-ahead.
- Commit as `Mark Rogers <156112+m4bwav@users.noreply.github.com>`, with no AI attribution.
- No kit, screenshot, LoRA or local path in the repo; `scripts/check_public.py` must pass.
- Downloads of large model files need the owner's yes.
- Stop and ask when: a licence question decides a default; a change would publish trained weights; or the GPU is needed while another session renders.

When you finish, rewrite `ai-docs/HANDOFF.md` and this file for the session after you, keeping this last paragraph as it is so the chain continues, and paste the new prompt in your final message.
