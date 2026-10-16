# The code route: exact mock-ups from brand.css

Generated pictures get small text, icons and lines wrong. The code route builds the mock-up as a real page from what `bw.py tokens` read off the live site, then screenshots it. Text, colours, fonts, borders and spacing are exact, and the HTML can go straight to developers.

## Skeleton

Put the file in the kit (so `brand.css` and the fonts resolve) and keep it self-contained:

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pricing card mock-up</title>
<link rel="stylesheet" href="../brand.css">
<style>
  /* layout only; every colour, font and size comes from brand.css variables or recipe classes */
  main { max-width: 960px; margin: 48px auto; display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--bw-space-x3, 24px); }
  .plan h2 { font-size: var(--bw-size-s5, 24px); margin: 0 0 8px; }
</style>
</head>
<body data-site="careers">
  <header class="bw-header">...</header>
  <main>
    <article class="bw-card plan">
      <h2>Weekly</h2>
      <p>$12 a week</p>
      <button class="bw-button">Choose plan</button>
    </article>
  </main>
</body>
</html>
```

## Rules

- Use the site's own variables first (`var(--brand-colour)` and the like, copied into `:root` in `brand.css`), then `--bw-*`, then the recipe classes. Hard-code a value only when brand.css has nothing, and say so.
- Real words: the copy the user gave, or plausible copy for the context. Never real customer data.
- Icons: simple inline SVG strokes or Unicode arrows; never copy the brand's logo file into a mock-up meant to leave the company.
- Fonts load from the site's own URLs in `@font-face`. Behind a login or offline, the browser falls back (the fallback stack is in `--bw-font`): say so if the render shows a fallback font.
- One file per mock-up; states (hover, error, empty) as extra sections or extra files.

## Render and check

```
bw.py render KIT/out/pricing.html --out KIT/out/pricing.png --width 1440 --height 900 --full
bw.py render KIT/out/pricing.html --selector .plan --scale 2 --out KIT/out/plan-card@2x.png
```

Look at the PNG next to a captured page (`capture/<site>/pages/`). Check: the primary colour on the right elements, the font family, button shape and padding, the header. `bw.py score KIT KIT/out/pricing.png` should come out close to the captured pages' own score.

## Combining with the picture routes

1. Explore with `gen` or `ref` (several seeds).
2. Pick a direction with the user.
3. Rebuild it here: the generated picture is the layout reference, `brand.css` is the truth for styles, the user's words are the copy.
4. Optionally feed the render back to `ref` as a reference to restyle a variant.
