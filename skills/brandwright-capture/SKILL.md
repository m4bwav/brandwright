---
name: brandwright-capture
description: "Turn a brand's websites into a clean LoRA training set and a token file: crawl pages with a headless browser (or the user's own signed-in browser session, or screenshots they supply), mask personal data, hide cookie banners, read design tokens and component styles into brand.css, then tile pages, crop components, drop duplicates, cap repeated headers and write captions that describe content and quote visible text but never colours or fonts. Use when the user wants to capture or crawl a site for a brand LoRA, feed screenshots in, build or caption a dataset for a UI or style LoRA, extract design tokens or brand colours and fonts from a live site, or asks 'how many screenshots do I need', 'how should I caption UI screenshots'. Part of brandwright (start there for the whole job). Also for 'refresh brandwright-capture'. Not for screenshot testing of an app, or scraping content."
metadata:
  version: "0.1.1"
---

# brandwright-capture

From sites (or screenshots) to `capture/`, `tokens.json` + `brand.css`, and `dataset/<lora>/` with captions. `BW` is `python "<brandwright skill folder>/scripts/bw.py"`; the kit exists already (`BW new`, see the brandwright skill).

## Step 0: freshness

Read [evergreen.json](evergreen.json); if past `next_due` or `contradiction` is set, say so, do the task, refresh after ([MAINTENANCE.md](MAINTENANCE.md)).

## Step 1: how the pictures get in

Ask the user, per site; never assume a login or a crawl is allowed.

| Situation | Command |
|---|---|
| Public site | `BW capture KIT --site NAME URL... --crawl 10` |
| Behind their login (SSO, intranet) | `BW login KIT --site NAME URL --channel msedge`: a window opens, **they** sign in and close it; then `BW capture KIT --site NAME URL --crawl 10 --channel msedge` reuses the session |
| Already open and signed in in their browser | they start Edge or Chrome with `--remote-debugging-port=9222`; `BW capture ... --cdp http://127.0.0.1:9222` |
| Not reachable from here, or automation not allowed | they save screenshots to a folder: `BW import KIT --site NAME FOLDER` (`--kind component` for single components, `--viewport mobile` for phone shots) |

- `--channel msedge` (or `chrome`) uses the installed browser, so nothing is downloaded: right for locked-down work machines. Without it, Playwright needs `python -m playwright install chromium` once.
- Never type, request or store a password. The `auth/` folder is a live session: private, never shared.
- Crawling visits same-site links by GET only and skips sign-out, delete, cancel, mailto and file links. Nothing is clicked except what `--click` names. Keep `--crawl` modest (10-30): the aim is variety of page types, not volume.
- Name at least one page with the main call-to-action button (a form, a start or sign-up page) among the URLs. Crawls follow navigation, and index pages rarely carry it (L-002).
- Default viewports: `desktop` (1440x900) and `mobile` (390x844 at 2x). `--viewports desktop,tablet,mobile,laptop`.

## Step 2: masks

By default, before each screenshot: e-mail addresses become `name@example.com`, digit runs (phones, account and card numbers) become 5s, typed field values are replaced, and consent banners, chat bubbles and survey pop-ups are hidden. Names, addresses and free text cannot be detected:

- capture staging or a test account where possible;
- `--hide SELECTOR` removes regions (better than `--blur`: blurred boxes teach the LoRA to draw blur);
- look at a few `capture/<site>/pages/*.png` before training. Read them with the image viewer, not by dumping the files.

## Step 3: tokens (the code route's input)

`BW tokens KIT` merges every capture into `tokens.json` (DTCG 2025.10 shape: brand base plus per-site overrides), `brand.css` (custom properties, the site's own `:root` variables, `@font-face` rules, and `.bw-button`, `.bw-input`, `.bw-card`, `.bw-header`, `.bw-nav`, `.bw-footer`, `.bw-alert`, `.bw-hero` recipes from the most common real element of each kind), `tokens.md` and `palette.png` (with Pillow). Show the user `tokens.md`. If `tokens` says no primary button was captured, capture a page that has one and run it again. For deeper token work, dembrandt (MIT, `npx dembrandt URL --dtcg`) is a well-kept alternative.

## Step 4: the dataset

`BW prep KIT` builds one folder per LoRA:

- full pages become viewport-sized tiles from the top (`--tiles 3`); trainers only downscale, so a whole long page would be illegible;
- components (header, nav, footer, hero, card, form, button, input, table, dialog, tabs, alert, pagination, breadcrumb) are cropped and set on the page's background as specimens, at most 2x upscale;
- near-duplicates go (`--dedupe 4`, perceptual hash), and repeated parts are capped (2 headers, 2 footers, 2 navs per site);
- `brand` takes an equal share from every site (`--brand-max 90`); each site LoRA takes only its own site (`--max-per-site 60`).

Sizes that work: brand 40-100 pictures across sites, a site 20-40. Fewer than 15 is thin: capture more page types.

## Step 5: captions

`prep` writes template captions: triggers, view, what the tile shows, and `text reads "..."` for short component text. Better captions come from a vision model:

- `BW caption KIT` uses a local Ollama vision model (`--model qwen3-vl:8b`; `BW doctor` lists hosts). Local keeps the screenshots on the machine.
- Or the agent writes them: open each picture, write the `.txt`. Only with the user's yes if the agent is a cloud model, since the screenshots then leave the machine.

The rule for every caption: describe content and arrangement (page type, components, order, the main headings and button labels in double quotes), never colours, fonts, corners, shadows, spacing, "clean", "modern" or the brand name. Those are what the LoRA should learn. `caption` flags style words it finds. Then `BW review KIT` writes `review.html`: delete weak pictures (and their `.txt`), fix captions, and the set is ready for brandwright-train. Detail and examples: [references/captions.md](references/captions.md).

## Maintenance

Evergreen: [evergreen.json](evergreen.json), [RESEARCH.md](RESEARCH.md), [CHANGELOG.md](CHANGELOG.md), [LEARNINGS.md](LEARNINGS.md), [TESTS.md](TESTS.md), `evals/evals.json`. Protocol: [MAINTENANCE.md](MAINTENANCE.md).
