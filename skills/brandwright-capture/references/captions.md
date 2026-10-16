# Captions for UI and screenshot LoRAs

The principle (BFL's FLUX.2 klein training guide, 2026): describe everything visible except the style you want the model to learn. For a brand, the style is the colours, type, corner radius, shadows, spacing and icon look. So the caption names what is there and where; it never names how it looks.

## Shape

```
<brand trigger> [<site trigger>], <view>. <what it is>. <parts, top to bottom or left to right>. Text: "<headline>", "<button label>".
```

## Examples

Good:

```
acmeui acmecareersui, desktop web page screenshot. A job search results page: a search bar with a location field across the top, filter checkboxes in a left column, and a list of six job cards each with a title, a location and a "Apply now" button.
acmeui, isolated button UI component, desktop size, on a plain background, text reads "Continue".
acmeui, mobile web screen screenshot. Sign-in screen with a heading "Sign in", two fields labelled "Email address" and "Password", and a full-width "Sign in" button.
```

Bad, and why:

```
acmeui, a clean modern blue and white page with rounded cards and Helvetica headings   <- style words: the LoRA stops learning them
a screenshot                                                                          <- nothing that varies is described, so layout cannot be prompted later
acmeui, page for John Smith, account 4417 1234 5678 9010                              <- personal data in a caption
```

## Visible text

Quote the main strings exactly: headings, button labels, tab names. It teaches the model that quoted text in a prompt is drawn, and stops the LoRA memorising the site's own copy. Skip body paragraphs and small print.

## Trigger words

Made-up words, one for the brand and one per site. With LLM text encoders (Z-Image, Qwen-Image, FLUX.2) a trigger is not strictly needed for a style LoRA, but it costs nothing, makes prompts explicit and helps when two LoRAs are loaded. No controlled test of triggers on these encoders was found (2026-10-15).

## Vision models for captions

- Local, keeps data on the machine: Ollama with a vision model (Qwen3-VL family, Gemma vision models). `bw.py caption` sends the instruction in `VLM_PROMPT` (bw.py) and flags style words in the reply.
- JoyCaption Beta One is built for diffusion captions but describes photos better than interfaces.
- A cloud model (Claude, Gemini, GPT) names components and reads text best, but the screenshots leave the machine: only with the user's yes and the company's policy.

## Counts

BFL's style example: 20-40 pictures (27 used); more dilutes. For UI, cover more page types rather than more copies of one type: a brand LoRA of 40-100 across properties, a site LoRA of 20-40. Remove near-duplicates; keep one or two of each repeated header, footer and nav.
