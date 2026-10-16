# Next session: brandwright

You are continuing brandwright, a public agent plugin (`m4bwav/brandwright`) for on-brand UI mock-ups from a brand's own sites (code route, reference route, and brand plus residual sub-site LoRAs).

Read first, in order: `AGENTS.md`, `ai-docs/HANDOFF.md` (state, open items, gotchas), then only the research or decision notes the step needs (`ai-docs/INDEX.md`). The owner's private notes (vault) give the test kit's location.

Before you rely on it, check that this prompt is not older than `HANDOFF.md` and the newest `run_test*.log` in the kit. If it is, trust those.

## This step

1. Test 3 (trigger words drawn as wordmarks, HANDOFF Open item 1). If `run_test3.log` does not end in `ALL DONE`, say where it stopped and why (still waiting for ComfyUI, or a failure) and do not restart it while another session renders. At 18:45 on 2026-10-16 it was queued behind a film render, expected to start around 04:00 to 06:00 on 2026-10-17. The runner and the sibling kits were already checked; see HANDOFF. When it is done, look at the pictures yourself (header text against test 2's controls), record the run in brandwright-train TESTS and update L-002.
2. If a fix wins, propose the default change it implies (trigger shape in `make_trigger`, or caption prompt `VLM_PROMPT`) to the owner with the evidence. Change a default only on their yes; then a test, the skill CHANGELOG and the wiki.
3. The owner chose (2026-10-16) to wait for test 3 and ship one 0.1.2: PR #12 (residual site LoRAs sample less) plus anything from step 2. Once step 2 is settled, ask for the go-ahead to tag. Do not tag without a yes.
   - Never free ComfyUI or train while another session renders.
4. Keep the wiki in step with any CLI or default change (HANDOFF has how).

## Rules

- Changes go through a branch and a PR. Merge your own PR once checks pass (this repository is the owner's alone and nobody downloads it from a registry yet). Releases and tags need the owner's go-ahead.
- Commit as `Mark Rogers <156112+m4bwav@users.noreply.github.com>`, with no AI attribution.
- No kit, screenshot, LoRA or local path in the repo; `scripts/check_public.py` must pass.
- Downloads of large model files need the owner's yes.
- Stop and ask when: a licence question decides a default; a change would publish trained weights; or the GPU is needed while another session renders.

When you finish, rewrite `ai-docs/HANDOFF.md` and this file for the session after you, keeping this last paragraph as it is so the chain continues, and paste the new prompt in your final message.
