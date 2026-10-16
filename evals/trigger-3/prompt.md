---
runs: 3
max_turns: 3
timeout_seconds: 180
tags: [trigger]
allowed_tools: [Skill, Read, Glob, Grep]
---

crawl https://careers.example.com and turn it into a captioned training set for a style LoRA, and pull out its colours and fonts
