# Next session: brandwright

You are continuing brandwright, a public agent plugin (`m4bwav/brandwright`) for on-brand UI mock-ups from a brand's own sites (code route, reference route, and brand plus residual sub-site LoRAs).

Read first, in order: `AGENTS.md`, `ai-docs/HANDOFF.md` (state, open items, gotchas), then only the research or decision notes the step needs (`ai-docs/INDEX.md`). The owner's private notes (vault) give the test kit's location.

Before you rely on it, check that this prompt is not older than `HANDOFF.md` and `ai-docs/log.md`. If it is, trust those.

## This step

0.1.3 is released (2026-10-18) and nothing is running. The CLI size budget is yellow (2,072 of 2,000 lines). There is no queued work, so start by asking the owner which of these they want, in one short message:

1. Prove `train --for musubi` (or `onetrainer`) on a real trainer with the GOV.UK brand LoRA (HANDOFF Open item 1). This needs a trainer install, model downloads and GPU time, so it needs their yes.
2. Bring the CLI back under 2,000 lines without losing behaviour, or ask whether the green line should move.
3. One idea from HANDOFF Open item 2.
4. The brandwright-train evergreen work: 3 verify-at-use claims are due, and the refresh is due on 2026-10-29.

If the owner is not there to answer, do item 4, or item 2 if it can be done without changing behaviour (tests must pass unchanged). Do nothing that downloads, deletes or uses the GPU.

## Rules

- Changes go through a branch and a PR. Merge your own PR once checks pass (this repository is the owner's alone and nobody downloads it from a registry yet). Releases and tags need the owner's go-ahead.
- Commit as `Mark Rogers <156112+m4bwav@users.noreply.github.com>`, with no AI attribution. Tags too (`git -c user.email=... tag -a`).
- No kit, screenshot, LoRA or local path in the repo; `scripts/check_public.py` must pass.
- Downloads of large model files need the owner's yes.
- Stop and ask when: a licence question decides a default; a change would publish trained weights; or the GPU is needed while another session renders.

When you finish, rewrite `ai-docs/HANDOFF.md` and this file for the session after you, keeping this last paragraph as it is so the chain continues, and paste the new prompt in your final message.
