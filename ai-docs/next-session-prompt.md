# Next session: brandwright

You are continuing brandwright, a public agent plugin (`m4bwav/brandwright`) for on-brand UI mock-ups from a brand's own sites (code route, reference route, and brand plus residual sub-site LoRAs).

Read first, in order: `AGENTS.md`, `ai-docs/HANDOFF.md` (state, open items, gotchas), then only the research or decision notes the step needs (`ai-docs/INDEX.md`). The owner's private notes (vault) give the test kit's location.

Before you rely on it, check that this prompt is not older than `HANDOFF.md` and the newest `run_test*.log` in the kit. If it is, trust those.

## This step

1. Ask the owner first: did the code route work on the work computer? Turn anything that went wrong into a test, a fix and a lesson (capture or mockup LEARNINGS). Their company's name, sites and screenshots never go in the repository.
2. Ask whether to release 0.1.1 with the Unreleased changes (HANDOFF, Open, item 1). Do not tag without a yes.
3. Then HANDOFF Open items 2 and 3 (sample cost for residual site LoRAs; trigger words drawn as wordmarks). Item 2 changes a default: propose it with the numbers from test 2 before changing it.
   - Never free ComfyUI or train while another session renders.
4. Keep the wiki in step with any CLI or default change (HANDOFF has how).

## Rules

- Changes go through a branch and a PR. Merge your own PR once checks pass (this repository is the owner's alone and nobody downloads it from a registry yet). Releases and tags need the owner's go-ahead.
- Commit as `Mark Rogers <156112+m4bwav@users.noreply.github.com>`, with no AI attribution.
- No kit, screenshot, LoRA or local path in the repo; `scripts/check_public.py` must pass.
- Downloads of large model files need the owner's yes.
- Stop and ask when: a licence question decides a default; a change would publish trained weights; or the GPU is needed while another session renders.

When you finish, rewrite `ai-docs/HANDOFF.md` and this file for the session after you, keeping this last paragraph as it is so the chain continues, and paste the new prompt in your final message.
