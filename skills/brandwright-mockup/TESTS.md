# Tests: brandwright-mockup

Test runs for [SKILL.md](SKILL.md). Cases live in `evals/evals.json` (runnable copies in the repository's root `evals/`). A failure that taught something is a lesson in [LEARNINGS.md](LEARNINGS.md); a fix it caused is logged in [CHANGELOG.md](CHANGELOG.md) with `because: T-...`; research it triggered is in [RESEARCH.md](RESEARCH.md). A test passes on evidence (a tool call in the trace, a file, a marker), never on the transcript's claim. Entry shape: `### T-YYYYMMDD-n · date · harness · env · passed/total`, newest first. Budget 150 lines. Protocol: [MAINTENANCE.md](MAINTENANCE.md).

## Runs

### T-20261017-1 · 2026-10-17 · claude plugin eval 2.1.281 (1 run a case, with and without the plugin, `--scaffold`) · WSL 2 Ubuntu on Windows 11, bubblewrap sandbox, Python 3.14, no Pillow or Playwright · 1/1, outcome blocked
- action-4 (render `kits/northwind/out/card.html` to a 1440x900 PNG): loaded `brandwright-mockup`, ran `bw.py render ... --width 1440 --height 900`; stopped at "Playwright is not installed" for the same reason as action-3.
- All 4 action cases, both arms: $1.46, 71 s at `-j 4`. Without the plugin no case ran `bw.py` (0/4).

### T-20261016-5 · 2026-10-16 · real run, owner's report · a work computer, code route (capture, tokens, render), checkout of 2026-10-16 · passed
- The owner ran the code route on their employer's sites from a work computer. Their verdict: it "worked better than expected". Nothing failed and they reported nothing to fix.
- The company, its sites and the screenshots stay in the owner's private notes, never here.

### T-20261016-4 · 2026-10-16 · real run · RTX 5060 Ti 16 GB, ComfyUI, Z-Image base graph (30 steps, cfg 4) and Turbo · passed with findings
- Three prompts (modal, start page, status card), 2 pictures each, with no LoRA, brand 1.0 (step 250), brand 1.0 + residual site 1.0 on the base graph, and brand 1.0 on Turbo. Then site checkpoints 100, 200 and 300 on the modal, and a brand 0.6/1.0/1.4 x site 0/0.7/1.0 sweep on the start page.
- Base graph: about 78 s a picture (155 s for 2); Turbo 13 s. The base graph carried the brand: blue masthead, white header with a crest, bold heading, green "Start now". At brand 1.4 + site 1.0 the button even had the real start button's arrow. Square corners on modals and cards, where Turbo drew rounded, generic iOS-style cards.
- Short quoted strings mostly right ("Renew a fishing licence", "Start now", "Application received", "Delete this file?"), but sometimes in US spelling ("license"). Unquoted body text garbled. The trigger was drawn as a wordmark again ("GovUKDesignSyYi"). 2 of about 30 pictures had a line of Chinese characters in the header.
- Best weights: brand 1.0 + site 1.0 (cleanest), brand 1.4 + site 1.0 (most detail). Site 0 at brand 1.4 gave busy collage pages.
- led to: L-002 confirmed, C-20261016-2

### T-20261016-3 · 2026-10-16 · work-machine dry run, code route · Windows 11, venv with Playwright only, Edge · passed with findings
- A status card (heading, tag, paragraph, primary button) on the dry-run kit's brand.css, rendered with `render --channel msedge` in 2.4 s: the site's typeface loaded from its own URLs, the real green button, exact text.
- Findings: a guessed variable name with a fallback value went unnoticed (L-003); `render` had no way to report a font that failed to load, now it warns (L-004; the smoke test covers it with a missing font file).
- led to: L-003, L-004, C-20261016-1

### T-20261016-2 · 2026-10-16 · claude plugin eval (1 run a case, with and without the plugin) · Windows 11, Claude Code · 2/2 run, action-4 not run
- trigger-5 fired `brandwright-mockup` with the plugin and not without; decoy-6 (a ComfyUI sunset) did not fire it.
- Action case action-4 was not run: on Windows the eval runner refuses any case granted a shell tool because it has no sandbox there ("sandbox required but unavailable"). Run it on macOS or Linux.
- Cost about $1.90 for all 11 trigger and decoy cases, both arms.

### T-20261016-1 · 2026-10-16 · real run · RTX 5060 Ti, ComfyUI, Z-Image Turbo graph · passed with findings
- `gen` with no LoRA, brand 1.0, and brand 1.0 + residual site 1.0, same seed, three prompts (modal, start page, status card): all ran (about 26 s for 2 pictures); the LoRAs, trained on the base model, shift Turbo output only a little.
- `sweep` brand 0.6/1.0/1.4 x site 0/0.7/1.0: 9 cells and a sheet in 2 min 8 s.
- led to: L-002

### T-20261015-1 · 2026-10-15 · real runs · Windows 11, RTX 5060 Ti 16 GB, ComfyUI · passed
- Code route: an application-tracker card that site does not have, written on the captured `brand.css` and rendered with `bw.py render --channel msedge`. The site's typeface, colour variables and real primary button came out exact; `score` 0.9 delta-E against 1.1 for a real captured page.
- Reference route: `bw.py ref` with two captured tiles on FLUX.2 klein 4B (distilled), 2 pictures: header, crest, hero, card list and green button carried over; the short quoted label "Get email updates" was right; the longer title and all unquoted text were garbled.
- `gen --raw` (banner and icon on Z-Image Turbo, 1536x640 and 1024x1024, batches of 4): worked through the same graph code.
- led to: L-001
