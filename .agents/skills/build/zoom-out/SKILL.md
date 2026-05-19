---
name: zoom-out
description: Tell the agent to zoom out and give broader context or a higher-level perspective. Use when you're unfamiliar with a section of code or need to understand how it fits into the bigger picture.
disable-model-invocation: true
---

<!--
Source: https://github.com/mattpocock/skills/blob/main/skills/engineering/zoom-out/SKILL.md
License: see upstream LICENSE for terms.
Copy date: 2026-05-13
Body content verbatim from upstream (~1 sentence). No Pack calibration applied — `disable-model-invocation: true` in frontmatter is the strongest possible auto-fire suppression (open-spec field; honored by Claude Code; assumed honored by other Agent-Skills adopters). Operator-side trigger discipline + pairing-with-/diagnose chain note live in README §4.4.
-->

I don't know this area of code well. Go up a layer of abstraction. Give me a map of all the relevant modules and callers, using the project's domain glossary vocabulary.
