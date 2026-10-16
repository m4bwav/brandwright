# Next session: brandwright

You are continuing brandwright, a public agent plugin (`m4bwav/brandwright`) for on-brand UI mock-ups from a brand's own sites (code route, reference route, and brand plus residual sub-site LoRAs).

Read first, in order: `AGENTS.md`, `ai-docs/HANDOFF.md` (state, open items, gotchas), then only the research or decision notes the step needs (`ai-docs/INDEX.md`). The owner's private notes (vault) give the test kit's location.

Before you rely on it, check that this prompt is not older than `HANDOFF.md` and the newest `run_test.log`. If it is, trust those.

## This step

1. The GOV.UK test ran on 2026-10-16. Its results and the next experiment are in HANDOFF (Open, item 1).
   - Base-graph judging needs `z_image_bf16.safetensors` in ComfyUI (12.3 GB). Ask the owner before downloading it.
   - Never free ComfyUI or train while another session renders.
2. The wiki is live; keep it in step with any CLI or default change (HANDOFF has how).
3. Run the eval cases in `evals/` once with `claude plugin eval` and record them in TESTS.md.

## Rules

- Changes go through a branch and a PR. Merge your own PR once checks pass (this repository is the owner's alone and nobody downloads it from a registry yet). Releases and tags need the owner's go-ahead.
- Commit as `Mark Rogers <156112+m4bwav@users.noreply.github.com>`, with no AI attribution.
- No kit, screenshot, LoRA or local path in the repo; `scripts/check_public.py` must pass.
- Downloads of large model files need the owner's yes.
- Stop and ask when: a licence question decides a default; a change would publish trained weights; or the GPU is needed while another session renders.

When you finish, rewrite `ai-docs/HANDOFF.md` and this file for the session after you, keeping this last paragraph as it is so the chain continues, and paste the new prompt in your final message.
