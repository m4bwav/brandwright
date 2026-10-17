# Tests: brandwright-train

Test runs for [SKILL.md](SKILL.md). Cases live in `evals/evals.json` (runnable copies in the repository's root `evals/`). A failure that taught something is a lesson in [LEARNINGS.md](LEARNINGS.md); a fix it caused is logged in [CHANGELOG.md](CHANGELOG.md) with `because: T-...`; research it triggered is in [RESEARCH.md](RESEARCH.md). A test passes on evidence (a tool call in the trace, a file, a marker), never on the transcript's claim. Entry shape: `### T-YYYYMMDD-n · date · harness · env · passed/total`, newest first. Budget 150 lines. Protocol: [MAINTENANCE.md](MAINTENANCE.md).

## Runs

### T-20261017-1 · 2026-10-17 · real run · Windows 11, RTX 5060 Ti 16 GB, ai-toolkit (2026-10-09), Z-Image base graph in ComfyUI · passed with findings
- Test 3: why the trigger is drawn as the wordmark (L-002). Seed 11, 2 pictures a prompt, 1344x768, base graph. Controls: test 2's brand-only start page and status card (headers read "Otlety" and "Porvic How ode").
- A, the old LoRA (`govukui`, step 250) with the header text named in the prompt: `the header shows the "GOV.UK" logo` gave "GOV.UK" in 2 of 2, `the header shows the name "Fishing Service"` gave that name in 2 of 2 (one also wrote a small "gouk Govui" above it), brand + design system 1 of 2 ("GOV.UIK"). The rest of the page stayed as on brand as the control. The logo marks next to the text are invented.
- B1, brand LoRA retrained to 250 steps with the non-word trigger `zqkvx` (90 pictures, about 25 min): headers still invented names ("Nisumsperents", "Sinener"), and `zqkvx` itself was printed in the page or card in 4 of 6 pictures. Status cards drifted off brand (dark panels, red tags). With "GOV.UK" in the prompt the name was right in 2 of 2, on red and magenta badges.
- B2, as B1 plus `The header shows the "GOV.UK" logo.` on the 25 masthead captions: plain prompts still invented the site name, so the quoted captions did not teach it; with "GOV.UK" in the prompt 2 of 2 right, on pink and orange badges, often inside drawn browser chrome. `zqkvx` printed in both status cards.
- Verdict: naming the header text in the prompt fixes it with the existing LoRA. A non-word trigger is worse, not better: the model prints the unknown string, and a trigger that spells the brand seems to carry some of the brand's look. No default changes (`make_trigger`, `VLM_PROMPT` stay).
- led to: L-002 (updated), ../brandwright-mockup C-20261017-1

### T-20261016-3 · 2026-10-16 · real run · Windows 11, RTX 5060 Ti 16 GB, ai-toolkit (2026-10-09), Z-Image base · passed with findings
- Brand LoRA re-picked at step 250. Site LoRA retrained in residual mode on top of it with the new defaults: 52 pictures, 400 steps, checkpoints every 100. 2 h 1 min in all: about 7-8.6 s a step, plus about 40 min for 5 sample sets of 4. Exit 0.
- The earlier 800-step run was moved aside first (C-20261016-2), and `pick` survived ComfyUI holding the old file (C-20261016-3).
- No collapse by step 400 for the site LoRA. Checkpoints 100, 200 and 300 drew similar modals; 300 and the final added the design system's underlined bold headings and outlined buttons.
- The trainer's samples are drawn without the brand LoRA (log: `Unloading assistant lora`), so they understate the result.
- led to: L-005

### T-20261016-2 · 2026-10-16 · claude plugin eval (1 run a case, with and without the plugin) · Windows 11, Claude Code · 2/2 run, action-2 not run
- trigger-4 fired `brandwright-train` with the plugin and not without; decoy-5 (a face LoRA) did not fire it.
- Action case action-2 was not run: on Windows the eval runner refuses any case granted a shell tool because it has no sandbox there ("sandbox required but unavailable"). Run it on macOS or Linux.
- Cost about $1.90 for all 11 trigger and decoy cases, both arms.

### T-20261016-1 · 2026-10-16 · real run · Windows 11, RTX 5060 Ti 16 GB, ai-toolkit (2026-10-09), Z-Image base · passed with findings
- Brand LoRA: 90 pictures (two sites of an openly licensed government brand), 1,200 steps, rank 32, lr 1e-4, buckets 768/1024, qfloat8, low_vram: 2 h 29 min (about 7.4 s a step). Config written by `bw.py train`, run with `--run --wait`; exit 0.
- Site LoRA, residual mode (brand LoRA as `assistant_lora_path`): 52 pictures, 800 steps: 1 h 49 min; exit 0. Residual mode works end to end.
- Samples on the base model: step 250 crisp and clearly in the brand (blue top bar, underlined heading, flat square buttons); from step 500 on, text soft and pages sparse and near-empty: overtrained.
- Generation on Z-Image Turbo in ComfyUI with the final LoRAs (base-trained): a weak but visible shift (square green button, flatter tag, heavier type), stronger with brand + site; the trigger word was drawn as the site's wordmark.
- led to: L-001, L-002, C-20261016-1
