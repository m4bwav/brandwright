---
name: brandwright-mockup
description: "Make on-brand UI mock-ups of new components, screens and pages for a brand kit: pixel-exact HTML on brand.css (real colours, fonts and component styles read from the live site) rendered to PNG; concept images from the brand and sub-site LoRAs through ComfyUI with prompt patterns per component; weight sweeps with contact sheets; training-free mock-ups from up to four reference screenshots with FLUX.2 klein; palette scoring against the brand. Use when the user asks for a mock-up, concept, wireframe-to-visual or variations of a new card, form, dashboard, modal, page or flow in their brand or a sub-site's style, wants LoRA weights tuned, or asks why generated text is wrong. Part of brandwright. Also for 'refresh brandwright-mockup'. Not for logos, illustrations or photos, or building the production front end."
metadata:
  version: "0.1.5"
---

# brandwright-mockup

Three ways to a mock-up, from exact to exploratory. `BW` is `python "<brandwright skill folder>/scripts/bw.py"` (`python3` on macOS and Linux); the kit has `tokens.json`/`brand.css` (brandwright-capture) and, for LoRAs, picked LoRAs in ComfyUI (brandwright-train).

## Step 0: freshness

Read [evergreen.json](evergreen.json); if past `next_due` or `contradiction` is set, say so, do the task, refresh after ([MAINTENANCE.md](MAINTENANCE.md)).

## Step 1: ask what it is for

- Going to developers, a spec, a stakeholder review of wording: **code route** (Step 2). Exact text, exact colours, editable.
- Exploring directions, mood, "what could this look like": **LoRA** (Step 3) or **ref** (Step 4), several seeds, then the chosen direction rebuilt with the code route.

## Step 2: code route (pixel-exact)

Write an HTML file next to the kit's `brand.css`, using its variables and recipe classes, then render it:

```
BW render KIT/out/pricing.html --out KIT/out/pricing.png --width 1440 --height 900 [--full] [--selector .card] [--scale 2] [--channel msedge]
```

`brand.css` holds the site's own `:root` variables (often the real design tokens, e.g. `--brand-colour`), `--bw-*` tokens, `@font-face` rules pointing at the site's fonts, and `.bw-button`, `.bw-input`, `.bw-card`, `.bw-header`, `.bw-nav`, `.bw-footer`, `.bw-alert`, `.bw-hero` copied from the most common real element. `<body data-site="SITE">` applies a site's overrides. Page skeleton, rules and checks: [references/code-route.md](references/code-route.md). Look at the PNG and compare it with a captured page before handing it over.

## Step 3: LoRA mock-ups

```
BW gen KIT "PROMPT" --lora brand=1.0 --lora SITE=1.0 --size 1344x768 --n 4 [--seed N] [--graph zimage_turbo]
```

- Graph: Z-Image LoRAs run on the base `zimage` graph by default, about 80 s a picture on a 16 GB card. `--graph zimage_turbo` is six times faster but shows the brand only weakly (L-002). Use Turbo for layout drafts and the base graph for anything meant to look on brand.
- Triggers are added for the LoRAs loaded. Weights: residual site LoRA, start brand 1.0 + site 1.0; continue mode, the site LoRA alone at 1.0; stack mode, find them with a sweep.
- `BW sweep KIT "PROMPT" --a brand --b SITE --wa 0.6,0.8,1.0 --wb 0.6,0.8,1.0`: same seed, a contact sheet `sweep.jpg`. Run one before any batch with new LoRAs.
- Sizes (multiples of 16): desktop page 1344x768 or 1536x864, mobile screen 768x1344 (or 720x1560), single component 1024x1024 or 1024x768.
- Prompt shape: view, what it is, parts in order, the exact strings in double quotes, and nothing about colours or fonts (the LoRA brings those). Patterns per component: [references/prompts.md](references/prompts.md).
- Outputs land in `KIT/out/<time>-<slug>/` with `mockup.json` (prompt, LoRAs, weights, seed, steps), so any picture can be remade.

## Step 4: training-free reference route

```
BW ref KIT "a settings page with a left menu and a form" --refs page1.png page2.png component.png --size 1344x768
```

FLUX.2 klein 4B (Apache-2.0) takes up to 4 reference images (captured pages from `capture/<site>/pages`, ideally cropped to one viewport) and is told to copy their style but not their content. About 15-30 s a picture on a 16 GB card. Good for a first look before any LoRA exists; less consistent across a batch than a trained LoRA. `--lora` adds a klein-trained LoRA.

## Step 5: check before handing over

- `BW score KIT out/<dir>`: delta-E from the picture's main colours to the brand palette and the off-palette share; lower is closer. Rough (photos score worse); use it to rank seeds and sweep cells, not as a pass mark.
- Read the text in every generated picture. Wrong or invented words are normal for small text: say so, and offer the code route for the final.
- Never present a generated picture as a real page of the site, and never put real customer data into a prompt.
- `BW sheet DIR... --out sheet.jpg` for a set the user can compare at a glance.

## Maintenance

Evergreen: [evergreen.json](evergreen.json), [RESEARCH.md](RESEARCH.md), [CHANGELOG.md](CHANGELOG.md), [LEARNINGS.md](LEARNINGS.md), [TESTS.md](TESTS.md), `evals/evals.json`. Protocol: [MAINTENANCE.md](MAINTENANCE.md).
