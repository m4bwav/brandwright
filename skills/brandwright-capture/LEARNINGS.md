# Learnings: brandwright-capture

Procedural lessons for [SKILL.md](SKILL.md). Research lives in [RESEARCH.md](RESEARCH.md); changes in [CHANGELOG.md](CHANGELOG.md); test runs in [TESTS.md](TESTS.md). Format and write-time gate: [MAINTENANCE.md](MAINTENANCE.md). Retired entries go to LEARNINGS-ARCHIVE.md.

## Active

### L-001 · 2026-10-15 · `most-common-button-is-not-the-cta`: the primary button needs its own recipe
- Trigger: the first `brand.css` from a real capture copied the most common button, a plain white feedback button, not the site's green call to action.
- Hypothesis: sites have many secondary buttons and few primary ones; frequency picks the secondary.
- Rule: keep `.bw-button` (most common) and `.bw-button-primary` (most common with a coloured fill); check both against a captured page before a code-route mock-up.
- Evidence: T-20261015-1, C-20261015-2
- Scope: skill
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-15

