# Next session: brandwright

You are continuing brandwright, a public agent plugin (`m4bwav/brandwright`) for on-brand UI mock-ups from a brand's own sites (code route, reference route, and brand plus residual sub-site LoRAs).

Read first, in order: `AGENTS.md`, `ai-docs/HANDOFF.md` (state, open items, gotchas), then only the research or decision notes the step needs (`ai-docs/INDEX.md`). The owner's private notes (vault) give the test kit's location.

Before you rely on it, check that this prompt is not older than `HANDOFF.md` and `ai-docs/log.md`. If it is, trust those.

## This step

1. Finish test 4 (HANDOFF Open item 1). Read the kit's `run_test4.log`.
   - If it ends with `ALL DONE`, look at the 4 later runs next to their controls, then record the verdict: mockup T-20261017-2, train L-002, and the prompt guide plus the root CHANGELOG's Unreleased if the trigger turns out to be optional.
   - If the runner stopped without `ALL DONE`, run only the missing gens. The owner already said yes to this GPU time on 2026-10-17, but only on an idle ComfyUI.
   - Never free ComfyUI or train while another session renders.
2. Optional small fix (HANDOFF Open item 2): say `python3` on macOS and Linux in the capture, train and mockup skills, as the hub does. Log it in each skill's CHANGELOG.
3. Do not start the WSL Playwright install (Open item 3) without the owner's yes.

## Rules

- Changes go through a branch and a PR. Merge your own PR once checks pass (this repository is the owner's alone and nobody downloads it from a registry yet). Releases and tags need the owner's go-ahead.
- Commit as `Mark Rogers <156112+m4bwav@users.noreply.github.com>`, with no AI attribution. Tags too (`git -c user.email=... tag -a`).
- No kit, screenshot, LoRA or local path in the repo; `scripts/check_public.py` must pass.
- Downloads of large model files need the owner's yes.
- Stop and ask when: a licence question decides a default; a change would publish trained weights; or the GPU is needed while another session renders.

When you finish, rewrite `ai-docs/HANDOFF.md` and this file for the session after you, keeping this last paragraph as it is so the chain continues, and paste the new prompt in your final message.
