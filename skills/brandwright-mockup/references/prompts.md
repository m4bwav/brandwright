# Prompt patterns for UI mock-ups

Shape: **view, what it is, parts in order, exact strings in double quotes**. No colours, fonts, "modern", "clean" or the brand name: the LoRA supplies the look, and style words fight it. Triggers are added by `bw.py gen`.

## Views

| Want | Start the prompt with | Size |
|---|---|---|
| a whole desktop page | `desktop web page screenshot,` | 1344x768, 1536x864 |
| the top of a page | `desktop web page screenshot, top of the page,` | 1344x768 |
| a phone screen | `mobile web screen screenshot,` | 768x1344 |
| one component | `isolated <kind> UI component, desktop size, on a plain background,` | 1024x768, 1024x1024 |

The `isolated ... on a plain background` and `top of the page` phrases match how `prep` captioned the training set, so they recall what the LoRA learned.

## Components

```
isolated card UI component, desktop size, on a plain background, a product card with an image at the top, the title "Weekly plan", the price "$12 a week" and a full-width button "Choose plan"
isolated form UI component, desktop size, on a plain background, a delivery address form with fields labelled "Street", "City" and "Postcode", and a "Continue" button
isolated modal dialog UI component, desktop size, on a plain background, heading "Remove this item?", one line of body text, a secondary button "Cancel" and a primary button "Remove"
isolated table UI component, desktop size, on a plain background, a table of four orders with columns "Order", "Date", "Status" and "Total", a status tag in each row
isolated alert UI component, desktop size, on a plain background, an error summary titled "There is a problem" with two linked error messages
isolated navigation UI component, desktop size, on a plain background, a horizontal tab bar with tabs "Overview", "Orders", "Settings", the first selected
```

## Screens and pages

```
desktop web page screenshot, a dashboard with a header, a left side menu, four summary tiles across the top showing "Orders", "Revenue", "Returns" and "Customers", and a line chart below
mobile web screen screenshot, a checkout screen with an order summary card, a payment method selector and a full-width "Pay now" button at the bottom
desktop web page screenshot, top of the page, a search results page for "part-time jobs" with a filter column on the left and a list of six results with titles and locations
```

## Text

- Keep strings short: one to three words per label is reliable, sentences are not.
- Put every string you care about in double quotes; unquoted text gets invented.
- Long copy (paragraphs, legal text): describe it as "a short paragraph of body text" and accept placeholder text, or use the code route.

## When results are off

| Symptom | Try |
|---|---|
| Looks generic, brand missing | raise the brand weight 0.2, or a later checkpoint |
| Copies a real page instead of the request | lower the weights, an earlier checkpoint, more specific parts in the prompt |
| Site look missing | raise the site weight; check its trigger is in the prompt |
| Text garbled | shorter strings, larger component size, the base graph instead of turbo, or the code route |
| Same layout every seed | vary the parts list; turbo graphs vary less than base |
