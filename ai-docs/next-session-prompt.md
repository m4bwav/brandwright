# Next session: brandwright

You are continuing brandwright, a public agent plugin (`m4bwav/brandwright`) for on-brand UI mock-ups from a brand's own sites (code route, reference route, and brand plus residual sub-site LoRAs).

Read first, in order: `AGENTS.md`, `ai-docs/HANDOFF.md` (state, open items, gotchas), then only the research or decision notes the step needs (`ai-docs/INDEX.md`). The owner's private notes (vault) give the test kit's location.

Before you rely on it, check that this prompt is not older than `HANDOFF.md` and `ai-docs/log.md`. If it is, trust those.

## This step

1. Release 0.1.2 (HANDOFF Open item 1). It holds PR #12 (residual site LoRAs sample less) and PR #15 (test 3: name the header text in prompts; no default changed). If the owner has already said yes in the conversation that started this session, release it: bump the version everywhere AGENTS.md lists, move the root CHANGELOG's "Unreleased" under `## 0.1.2 · DATE`, run the tests, budget and public check, PR and merge, tag `v0.1.2`, publish the GitHub Release with that entry as notes, then update the wiki (Home and the Commands page; HANDOFF has how). If they have not said yes, ask once with a one-paragraph summary of what 0.1.2 contains, and do nothing else on it.
2. Offer, without starting it, test 4 from HANDOFF Open item 2 (gen without the trigger in the prompt). It needs GPU time: the owner's yes and an idle ComfyUI.
   - Never free ComfyUI or train while another session renders.
3. If time remains and a macOS or Linux shell is available, run the 4 action cases in `evals/` (HANDOFF Open item 3).

## Rules

- Changes go through a branch and a PR. Merge your own PR once checks pass (this repository is the owner's alone and nobody downloads it from a registry yet). Releases and tags need the owner's go-ahead.
- Commit as `Mark Rogers <156112+m4bwav@users.noreply.github.com>`, with no AI attribution.
- No kit, screenshot, LoRA or local path in the repo; `scripts/check_public.py` must pass.
- Downloads of large model files need the owner's yes.
- Stop and ask when: a licence question decides a default; a change would publish trained weights; or the GPU is needed while another session renders.

When you finish, rewrite `ai-docs/HANDOFF.md` and this file for the session after you, keeping this last paragraph as it is so the chain continues, and paste the new prompt in your final message.
