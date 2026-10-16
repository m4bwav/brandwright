# brandwright

![A brass robot arm painting glowing interface cards and buttons onto panes of glass in a lamp-lit design studio](https://raw.githubusercontent.com/m4bwav/brandwright/main/.github/images/banner.jpg)

An agent plugin for mock-ups of new UI that look like they came from your own sites. Point it at your brand's websites, or hand it screenshots. It learns the look three ways:

- Code route: it reads the live site's colours, fonts, CSS variables and real button, input and card styles into `brand.css`. The agent then builds the new component as HTML on top of it and renders a PNG. Text, colours and spacing come out exact, and developers can use the file. No GPU needed.
- Reference route: FLUX.2 klein draws a new screen in the style of up to four of your screenshots. No training, about half a minute a picture.
- LoRA route: a brand LoRA trained on all your sites, plus a LoRA for each sub-site. The sub-site LoRA learns only what that site adds on top of the brand. After that, every prompt comes out on brand in seconds.

Four skills and one Python CLI:

- `brandwright`: picks the route, sets up the kit (one private folder per brand), and has the rules on data, licences and trademarks.
- `brandwright-capture`: crawls with a headless browser or your own signed-in session, or imports screenshots. It masks personal data, reads design tokens and builds a captioned dataset.
- `brandwright-train`: chooses the base model by licence and GPU, writes the ostris ai-toolkit config, and trains the brand LoRA, then each site LoRA on top of it. It watches the samples and picks the checkpoint.
- `brandwright-mockup`: HTML on `brand.css`, ComfyUI generation with prompt patterns per component, weight sweeps, the reference route, and palette scoring.
- `skills/brandwright/scripts/bw.py`: the CLI. Python 3.10+ on Windows, macOS or Linux. Capture needs Playwright, datasets need Pillow, pictures need ComfyUI, training needs ai-toolkit.

## Quick start on a work machine

```
python -m pip install playwright pillow
python bw.py doctor
python bw.py new D:\kits\acme --brand "Acme" --site "portal=https://portal.acme.example/"
python bw.py login D:\kits\acme --site portal https://portal.acme.example/ --channel msedge   # you sign in, then close the window
python bw.py capture D:\kits\acme --site portal https://portal.acme.example/ https://portal.acme.example/apply --crawl 15 --channel msedge
python bw.py tokens D:\kits\acme             # tokens.json, brand.css, tokens.md
```

That is enough for the code route: ask your agent for "a new order-tracking card in our style" and it builds HTML on `brand.css`, then runs `bw.py render`. `--channel msedge` uses the Edge already on the machine, so Playwright needs no browser download. If the site cannot be reached or automated, save screenshots to a folder and run `python bw.py import D:\kits\acme --site portal <folder>`.

Tested this way on a fresh install with Playwright alone: about 8 seconds a page and 2 to 3 seconds a render. Pillow is only for `palette.png`, `score`, `prep` and `sheet`. Three things to check before the first mock-up:

- List a page that has the main button (a form, a start or sign-up page), as `.../apply` above. Crawls follow menus and can miss it; `tokens` says when no primary button was found.
- Read `tokens.md`, and the `.bw-button-primary` line in `brand.css`.
- If `render` prints `font ... did not load`, the site's fonts need a login or refuse pages opened from disk. Get the font files and point `@font-face` at local copies, or the mock-up shows a fallback font.

For pictures and LoRAs, add a GPU machine with ComfyUI and ai-toolkit:

```
python bw.py prep D:\kits\acme
python bw.py caption D:\kits\acme                 # local vision model through Ollama (optional)
python bw.py train D:\kits\acme --lora brand --run
python bw.py pick D:\kits\acme --lora brand --to <ComfyUI>\models\loras
python bw.py train D:\kits\acme --lora portal --run    # residual: learns what the portal adds
python bw.py gen D:\kits\acme "isolated modal dialog asking \"Cancel this order?\"" --lora brand=1 --lora portal=1
```

## Why two LoRAs trained this way

The common advice is two LoRAs with trigger words, stacked at weights that sum to about 1.0. That is half right. A sub-site's screenshots are brand screenshots too, so two LoRAs trained independently learn the same things and fight when stacked. brandwright trains the brand LoRA first. Then it trains each site LoRA with the brand LoRA merged in, so the site LoRA learns only the difference. That is "residual" mode on Z-Image, via ai-toolkit's `assistant_lora_path`. On other models it starts the site LoRA from the brand LoRA ("continue" mode). The full fact-check, with sources, is in [ai-docs/research](ai-docs/research/2026-10-15-ui-lora-practice-and-fact-check.md).

## Models and licences

Checked 2026-10-15. Re-check before relying on any of these.

| Model | Licence | Train on | Notes |
|---|---|---|---|
| Z-Image (default) | Apache-2.0 | 16 GB | strong text, any aspect ratio, residual site LoRAs |
| Qwen-Image-2512 | Apache-2.0 | 24 GB | best open text and layout |
| FLUX.2 klein base 4B | Apache-2.0 | 12 GB | fastest; used by the reference route |
| Qwen-Image-2.1, FLUX.2 dev / klein 9B, Ideogram 4 | research or non-commercial | | not for company work |

## Your data

- A kit holds your company's screenshots, login session and trained LoRAs. It lives where you put it and gets a `.gitignore` of `*`. brandwright sends its pictures only to the ComfyUI server and Ollama host you name.
- Capture masks e-mail addresses, digit runs and typed field values, and hides cookie and chat pop-ups. Names cannot be detected: use a test account or `--hide` regions that show people.
- Captioning runs on a local model (Ollama) by default. Sending screenshots to a cloud model, or training on a hosted GPU, is your call under your company's policy.
- Trained brand LoRAs reproduce trademarks. Keep them inside the company. Train only on brands you work for or have rights to.

## Install

Claude Code, from a clone:

```
git clone https://github.com/m4bwav/brandwright
claude plugin marketplace add ./brandwright
claude plugin install brandwright@brandwright
```

Other agents that read Agent Skills (`SKILL.md`): link or copy the four folders under `skills/` into the agent's skills folder. The CLI on its own: `python skills/brandwright/scripts/bw.py --help`. The [wiki](https://github.com/m4bwav/brandwright/wiki) has every command, the kit layout, recipes and an FAQ.

## Tests

- `python tests/test_bw.py`: offline tests on synthetic kits, captures and tokens (dataset tests need Pillow).
- `python tests/smoke_browser.py [--channel msedge]`: captures the fictional fixture site. It checks masking, the hidden cookie banner, tokens, `brand.css`, a render and a dataset. It skips without Playwright or a browser.
- `python scripts/budget.py` (size budget below) and `python scripts/check_public.py` (no local paths, private addresses or kit files in the repository).
- The trigger, decoy and action cases in `evals/` run with `claude plugin eval`.

## Size budget

brandwright should stay small enough that nobody thinks twice about installing it. `scripts/budget.py` measures each row, and CI fails at red.

| measure | green up to | yellow up to | now (0.1.1) |
|---|---:|---:|---:|
| longest skill description, characters | 1,000 | 1,300 | 935 |
| all four descriptions, characters | 3,600 | 4,400 | 3,499 |
| largest SKILL.md, tokens | 2,500 | 3,500 | 1,575 |
| largest reference file, tokens | 2,000 | 3,000 | 884 |
| CLI lines (three files) | 2,000 | 2,600 | 1,957 |
| installed skills folder, KB | 250 | 500 | 226 |

## Evergreen

Every skill keeps its research current on a schedule. `brandwright-train` re-checks model licences and trainer options before quoting them, because those change monthly. Plugin versions are in [CHANGELOG.md](CHANGELOG.md). Each skill's changes, findings and lessons are in its own CHANGELOG.md, RESEARCH.md and LEARNINGS.md.

## Licence

MIT, see [LICENSE](LICENSE). Semantic versions; tags `vX.Y.Z`.
