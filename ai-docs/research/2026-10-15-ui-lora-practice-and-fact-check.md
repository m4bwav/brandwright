---
title: UI LoRA practice, a fact-check of common advice, and the alternatives
date: 2026-10-15
summary: "Claim-by-claim fact-check of the 'two LoRAs with trigger words, keep weights near 1.0' advice; dataset, caption, multi-LoRA and evaluation practice for screenshot LoRAs; training-free and code routes. Read before changing defaults."
tags: [research, lora, ui, captions, multi-lora, design-tokens]
---

# UI LoRA practice, fact-check and alternatives (checked 2026-10-15)

One research pass (web search and fetches by a subagent, then verified against the ai-toolkit source on disk where noted). [P] primary source, [S] secondary, [R] reasoning with no direct source.

## The advice that started this

A chat assistant told a user who works at a large chain that they could: train two LoRAs with distinct trigger words, one for the corporate style and one for a sub-website; stack them; keep the total weight near 1.0 (for example 0.6 + 0.5); use a "UI-specific base model"; expect bad text; and train "in an enterprise cloud, not on the payment site".

| Claim | Verdict | Why |
|---|---|---|
| Two LoRAs with distinct triggers, both named in the prompt | Partly right | A LoRA acts whenever it is loaded; its weight is the switch and the trigger only conditions it ([P] diffusers LoRA docs). BFL still recommends a unique trigger per caption for FLUX.2 klein ([P] docs.bfl.ai/flux_2/flux2_klein_training). Missed: sub-site screenshots are brand screenshots too, so two LoRAs trained independently learn overlapping directions that interfere when added ([P] ZipLoRA arXiv 2311.13600; NP-LoRA arXiv 2511.11051). |
| 1-2 LoRAs fine, 3-4 need tweaks, 5+ gives "hieroglyphics" | Direction right, numbers folklore | Naive merging loses detail as LoRAs are added ([P] Multi-LoRA Composition arXiv 2402.16843); no measurement behind the thresholds. VRAM is not the limit. |
| Keep the sum of weights near 1.0 | Heuristic, not a rule | diffusers' own example uses 0.7 + 0.8 ([P]). "Deep-fried" stacks come from overlapping training data. Sweep weights instead of fixing a sum. |
| Use a UI-specific base model | Outdated | No mainstream UI base exists; UI-Diffuser V2 is SD-2, mobile-only, academic licence ([P] huggingface.co/Jl-wei/ui-diffuser-v2). Pick the base with the best text and layout: Qwen-Image-2512, FLUX.2 klein, Z-Image. |
| Image models are bad at small text; rebuild in Figma | Right in substance | Qwen-Image-2512: one to three large words right about 70% of the time, sentences under 40% ([S] wavespeed.ai). The fix in 2026 is to build the final component as code from extracted tokens, not to redraw it by hand. |
| Train in an enterprise cloud, not on the payment site | Confused | Training never happens "on" a site: capture screenshots, train anywhere. A 16 GB card trains FLUX.2 klein 4B ([P] BFL: 12 GB VRAM + 32 GB RAM). The real constraints are personal data in screenshots and company policy on where data may go. |

## Practice for screenshot LoRAs

- **Size**: BFL's style example uses 20-40 images (27 used) and warns that too many dilutes the style ([P] docs.eu.bfl.ai/flux_2/flux2_klein_training_example). [R] brand 40-100 crops across properties, sub-site 20-40.
- **Crops**: trainers only downscale into buckets ([P] ai-toolkit README), so a 1440x12000 full page becomes illegible. Use viewport-sized tiles, section tiles and component crops; keep aspect within about 1:3.
- **Resolution**: iterate at 512, train finals at 1024+ ([P] BFL).
- **Personal data**: capture staging or seeded accounts; mask at capture time. Blurred blocks teach the LoRA to draw blur: replace with plausible fake text instead [R].
- **Duplicates**: headers and footers repeat on every page; keep one or two per site (perceptual hash dedupe; [S] imagededup).
- **Balance**: keep the brand LoRA generic: cap any one site's share, balance per property [R].
- **Captions**: "Describe everything visible except the style/concept you want to teach" ([P] BFL). For UI: caption page type, components, arrangement, viewport and the main strings in quotes; never colours, fonts, radius, shadow or spacing. Quoted strings stop the LoRA memorising copy and match how text-strong models are prompted [R].
- **Rank / LR / steps**: BFL klein style example rank 128/alpha 64 at LR ~1e-4, 1200-2000 steps, best checkpoint at 1500 of 3000 ([P]); BFL notes smaller ranks suit low-detail content such as vector logos, so flat UI starts at 16-32 [R]. Train on the Base (undistilled) checkpoint ([P]).
- **Evaluation**: save often; render held-out component prompts with a fixed seed; style similarity (CSD, arXiv 2404.01292, with care: arXiv 2605.09030); OCR word accuracy on quoted strings (STRICT arXiv 2505.18985); delta-E to brand colours [R]; XY weight grids.

## Combining brand and sub-site

Ranked options:

1. **Differential sub-site LoRA**: train the brand LoRA, then train the sub-site LoRA with the brand LoRA merged into the base so it learns only the difference (kohya `--base_weights`, [S] doc mirror). **ai-toolkit equivalent, verified in its source on 2026-10-15**: for Z-Image, `model.assistant_lora_path` merges a LoRA during training and switches it off for sampling (`extensions_built_in/diffusion_models/z_image/z_image.py`, `load_training_adapter`). FLUX.2 has no such hook in ai-toolkit.
2. **Continue from the brand LoRA**: `network.pretrained_lora_path` (generic in `jobs/process/BaseSDTrainProcess.py`) initialises the new LoRA from the brand LoRA; the result is used on its own, so nothing is stacked.
3. One LoRA with two triggers: simplest; concepts bleed.
4. Naive stacking: fine at moderate weights, worst under overlap.

## Training-free and code routes

- Reference conditioning: FLUX.2 klein takes up to 4 reference images, dev 6, pro 8-10 ([P] BFL spec table); Qwen-Image-Edit-2509 works best with 1-3 ([P] model card); Qwen-Image-2.1 up to 10 but a research (non-commercial) licence ([P] model card). Z-Image-Edit was still unreleased.
- Tokens: dembrandt (MIT, Playwright, `--dtcg`, MCP server, [P] github.com/dembrandt/dembrandt); Project Wallace. DTCG format 2025.10 is the first stable version (Community Group report, not a W3C standard; [P] w3.org/community/design-tokens, 2025-10-28) and has multi-brand theming that maps onto brand + sub-site.
- Research consensus: pixel diffusion gives inspiration and low-fidelity variety (UI-Diffuser arXiv 2306.06233; ControlGUI arXiv 2502.03330); production fidelity comes through code (Design2Code arXiv 2403.03163).
- What teams use in 2026: Claude Design (reads design systems, web capture; [P] anthropic.com/news/claude-design-anthropic-labs), Figma Make kits, Google Stitch DESIGN.md ([S]), v0 design systems ([S]).

## Pipeline this research supports

Capture with masks, extract tokens, then two tracks: **code** (tokens + real component recipes, rendered with a headless browser) for anything someone will build, and **pixels** (reference images first, LoRAs when references are not consistent enough) for exploration. Score outputs by palette delta-E and OCR, sweep weights, and pick checkpoints by eye on held-out prompts.

## Not verified

LyCORIS rank guidance (doc 404); the exact kohya README wording for `--base_weights`; Stitch's primary post; Qwen-Image-2.1 release date; OmniGen2 and Kontext reference caps; closed-model reference counts; any controlled trigger-word ablation for LLM text encoders; any UI-specific dataset-size study.

Related: see also [the model and trainer research](2026-10-15-models-trainers-licences.md)
