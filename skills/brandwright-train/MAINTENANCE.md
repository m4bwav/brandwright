# Maintenance: brandwright-train

This unit is evergreen and follows the same protocol as the hub skill, kept once for the plugin in [../brandwright/MAINTENANCE.md](../brandwright/MAINTENANCE.md) (Step 0, refresh, interval rule, learnings, tests, links). Everything there applies to this unit, with this folder's files: [SKILL.md](SKILL.md), [RESEARCH.md](RESEARCH.md), [CHANGELOG.md](CHANGELOG.md), [LEARNINGS.md](LEARNINGS.md), [TESTS.md](TESTS.md), `evals/evals.json` and `evergreen.json`.

Step 0 in short: read `evergreen.json`. If `contradiction` is set or today is on or after `next_due`, say so in one line, do the task, then refresh in the same session. If `verify_at_use` is true, re-check the due `volatile_claims` before relying on them and set their `checked` to today.
