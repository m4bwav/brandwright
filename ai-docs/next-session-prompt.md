# Next session: brandwright

You are continuing brandwright, a public agent plugin (`m4bwav/brandwright`) for on-brand UI mock-ups from a brand's own sites (code route, reference route, and brand plus residual sub-site LoRAs).

Read first, in order: `AGENTS.md`, `ai-docs/HANDOFF.md` (state, open items, gotchas), then only the research or decision notes the step needs (`ai-docs/INDEX.md`). The owner's private notes (vault) give the test kit's location.

Before you rely on it, check that this prompt is not older than `HANDOFF.md` and `ai-docs/log.md`. If it is, trust those.

## This step

`train --for musubi` was proven on 2026-10-21 (train T-20261021-1, PR #27 merged): the Z-Image brand LoRA job ran on musubi-tuner v0.3.6 with only its model paths set, and the LoRA is comparable to ai-toolkit's. That change is unreleased (CHANGELOG Unreleased). Nothing is running. The size budget is green (CLI 1,991 of 2,000 lines, skills folder about 227 of 250 KB). Due dates: the hub skill on 2026-10-29, brandwright-train claim 1 on 2026-10-30 and claims 2 to 4 on 2026-11-01. Start by asking the owner, in one short message, which of these they want (more than one is fine):

1. Release 0.1.5 with the musubi proof (needs their go-ahead).
2. Delete the test-5 leftovers: 6 musubi LoRAs in ComfyUI's loras folder (about 1.7 GB) and the run's output and caches in the kit (HANDOFF State). Keep the musubi install unless they say otherwise.
3. Prove the OneTrainer job, or a musubi residual site LoRA (GPU time, and a OneTrainer install for the first).
4. One idea from HANDOFF Open item 2, or a UI test of MOSS-Image or FLUX 3 klein (Open item 5). The CLI has about 9 lines of green headroom, so a feature needs cuts or the owner's agreement to raise the line.

If the owner does not answer: on or after 2026-10-29, refresh the hub skill (evergreen-refresh); on or after 2026-10-30, re-check the due brandwright-train claims (`evergreen.py claims skills/brandwright-train --due`). Before either date, record that nothing was due and stop. Do nothing that downloads, deletes or uses the GPU.

## Rules

- Changes go through a branch and a PR. Merge your own PR once checks pass (this repository is the owner's alone and nobody downloads it from a registry yet). Releases and tags need the owner's go-ahead.
- Commit as `Mark Rogers <156112+m4bwav@users.noreply.github.com>`, with no AI attribution. Tags too (`git -c user.email=... tag -a`).
- No kit, screenshot, LoRA or local path in the repo; `scripts/check_public.py` must pass.
- Downloads of large model files need the owner's yes.
- Stop and ask when: a licence question decides a default; a change would publish trained weights; or the GPU is needed while another session renders.

When you finish, rewrite `ai-docs/HANDOFF.md` and this file for the session after you, keeping this last paragraph as it is so the chain continues, and paste the new prompt in your final message.
