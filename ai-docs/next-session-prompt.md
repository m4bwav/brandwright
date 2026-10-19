# Next session: brandwright

You are continuing brandwright, a public agent plugin (`m4bwav/brandwright`) for on-brand UI mock-ups from a brand's own sites (code route, reference route, and brand plus residual sub-site LoRAs).

Read first, in order: `AGENTS.md`, `ai-docs/HANDOFF.md` (state, open items, gotchas), then only the research or decision notes the step needs (`ai-docs/INDEX.md`). The owner's private notes (vault) give the test kit's location.

Before you rely on it, check that this prompt is not older than `HANDOFF.md` and `ai-docs/log.md`. If it is, trust those.

## This step

0.1.3 is released (2026-10-18) and nothing is running. brandwright-train was refreshed on 2026-10-18 and all its claims hold. Its claims fall due again on 2026-10-30 (claim 1) and 2026-11-01 (claims 2 to 4). The size budget is yellow on two rows: CLI lines (2,072 of 2,000) and the installed skills folder (251 of 250 KB). No work is queued, so start by asking the owner which of these they want, in one short message:

1. Budget: raise the green lines (CLI 2,000 lines, skills folder 250 KB), or cut back under them without losing behaviour (HANDOFF Open item 4 lists candidates).
2. Prove `train --for musubi` (or `onetrainer`) on a real trainer with the GOV.UK brand LoRA (HANDOFF Open item 1). This needs a trainer install, model downloads and GPU time, so it needs their yes.
3. One idea from HANDOFF Open item 2, or a UI test of MOSS-Image or FLUX 3 klein (Open item 5, which needs downloads and GPU time).
4. A 0.1.4 release of the refreshed references (docs only; it needs their go-ahead).

If the owner does not answer, cut the CLI under 2,000 lines without changing behaviour (the tests must pass unchanged). If a claim is due by then, re-check it first (`evergreen.py claims skills/brandwright-train --due`). Do nothing that downloads, deletes or uses the GPU.

## Rules

- Changes go through a branch and a PR. Merge your own PR once checks pass (this repository is the owner's alone and nobody downloads it from a registry yet). Releases and tags need the owner's go-ahead.
- Commit as `Mark Rogers <156112+m4bwav@users.noreply.github.com>`, with no AI attribution. Tags too (`git -c user.email=... tag -a`).
- No kit, screenshot, LoRA or local path in the repo; `scripts/check_public.py` must pass.
- Downloads of large model files need the owner's yes.
- Stop and ask when: a licence question decides a default; a change would publish trained weights; or the GPU is needed while another session renders.

When you finish, rewrite `ai-docs/HANDOFF.md` and this file for the session after you, keeping this last paragraph as it is so the chain continues, and paste the new prompt in your final message.
