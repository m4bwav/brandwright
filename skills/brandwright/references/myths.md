# Common advice about brand LoRAs, checked

Checked 2026-10-15; sources are in the repository's `ai-docs/research/2026-10-15-ui-lora-practice-and-fact-check.md` and this skill's RESEARCH.md. Use this when a user arrives with advice from elsewhere.

| They were told | What holds | What to do instead |
|---|---|---|
| "Train two LoRAs with distinct trigger words and put both words in the prompt to switch them on" | A LoRA changes the model whenever it is loaded; its weight is the switch. The trigger only conditions it (BFL still recommends one per caption). | Keep a trigger per LoRA, but train the site LoRA on top of the brand LoRA (residual or continue mode), because sub-site screenshots are brand screenshots too and two independent LoRAs learn the same directions. |
| "1-2 LoRAs is the sweet spot, 5+ turns text into hieroglyphics" | Direction right (merging more LoRAs loses detail), numbers folklore. VRAM is not the limit. | Two well-trained LoRAs (brand + residual site) need no more. |
| "Keep the weights summing to about 1.0, e.g. 0.6 + 0.5" | A heuristic for overlapping LoRAs, not a rule; diffusers' own example uses 0.7 + 0.8. | With a residual site LoRA, start at brand 1.0 + site 1.0, then `bw.py sweep`. |
| "Use a UI-specific base model" | None in mainstream use; the academic ones are old and non-commercial. | Pick the base with the best text and a licence the company can use: Z-Image, Qwen-Image-2512, FLUX.2 klein 4B. |
| "Image models can't do small text; rebuild it all in Figma" | Still true for small text and icons (about 70% right for 1-3 large words, under 40% for sentences on Qwen-Image-2512). | Build anything final with the code route (real HTML on `brand.css`); use pictures for direction. |
| "Train in an enterprise cloud, not on the payment site" | Training never happens on a site. A 16 GB card trains these models locally, which keeps the data on the machine. | The constraints are personal data in screenshots and company policy on where data may go. |
