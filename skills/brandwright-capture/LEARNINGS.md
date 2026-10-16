# Learnings: brandwright-capture

Procedural lessons for [SKILL.md](SKILL.md). Research lives in [RESEARCH.md](RESEARCH.md); changes in [CHANGELOG.md](CHANGELOG.md); test runs in [TESTS.md](TESTS.md). Format and write-time gate: [MAINTENANCE.md](MAINTENANCE.md). Retired entries go to LEARNINGS-ARCHIVE.md.

## Active

### L-002 · 2026-10-16 · `crawl-misses-the-cta`: a short crawl can miss the call-to-action button entirely
- Trigger: a clean-install dry run captured the home page and three browse pages of an openly licensed government site (`--crawl 3`). None had the green start button, so `.bw-button-primary` became the only coloured button found: an unstyled browser-default button (Arial 13.3333px, light blue).
- Hypothesis: crawls follow navigation links, and index or browse pages rarely carry the main call to action; forms, start and sign-up pages do.
- Rule: name at least one page with the main button in the capture URLs (a form, a start or sign-up page). `tokens` now ignores 13.3333px browser-default buttons and says when no primary button was found. Read `tokens.md` and the `.bw-button-primary` line before the first mock-up.
- Evidence: T-20261016-2, C-20261016-1
- Scope: skill
- Status: active · helpful 0 · harmful 0 · last_confirmed 2026-10-16

### L-001 · 2026-10-15 · `most-common-button-is-not-the-cta`: the primary button needs its own recipe
- Trigger: the first `brand.css` from a real capture copied the most common button, a plain white feedback button, not the site's green call to action.
- Hypothesis: sites have many secondary buttons and few primary ones; frequency picks the secondary.
- Rule: keep `.bw-button` (most common) and `.bw-button-primary` (most common with a coloured fill); check both against a captured page before a code-route mock-up.
- Evidence: T-20261015-1, C-20261015-2
- Scope: skill
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-15

