# Learnings: brandwright-mockup

Procedural lessons for [SKILL.md](SKILL.md). Research lives in [RESEARCH.md](RESEARCH.md); changes in [CHANGELOG.md](CHANGELOG.md); test runs in [TESTS.md](TESTS.md). Format and write-time gate: [MAINTENANCE.md](MAINTENANCE.md). Retired entries go to LEARNINGS-ARCHIVE.md.

## Active

### L-002 · 2026-10-16 · `base-loras-weak-on-turbo`: judge base-trained LoRAs on the base graph
- Trigger: LoRAs trained on Z-Image base and generated on the Turbo graph changed the output only a little, while ai-toolkit's samples on the base model showed the brand strongly.
- Hypothesis: the distilled Turbo weights drift from the base the LoRA was trained against.
- Rule: generate base-trained LoRAs on the `zimage` graph (needs `z_image_bf16.safetensors` in ComfyUI); use Turbo only for quick drafts, or train with `--model zimage_turbo` when Turbo is the target.
- Evidence: T-20261016-1, ../brandwright-train T-20261016-1
- Scope: skill
- Status: active · helpful 0 · harmful 0 · last_confirmed 2026-10-16

### L-001 · 2026-10-15 · `ref-copies-logos-garbles-long-text`: the reference route copies the brand mark and only short quoted labels survive
- Trigger: first `ref` run on a captured government site: its crest and wordmark were redrawn in both pictures; "Get email updates" was right, a five-word title came out misspelled, and unquoted lines were nonsense.
- Hypothesis: klein copies salient reference details; text beyond a few words is beyond the 4B model.
- Rule: keep labels to one to three quoted words, expect the logo to appear (never let such a picture leave the company), and rebuild anything with real copy through the code route.
- Evidence: T-20261015-1
- Scope: skill
- Status: active · helpful 0 · harmful 0 · last_confirmed 2026-10-15
