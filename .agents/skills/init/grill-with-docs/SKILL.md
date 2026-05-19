---
name: grill-with-docs
description: Grilling session that challenges your plan against the existing domain model, sharpens terminology, and updates documentation (CONTEXT.md, ADRs) inline as decisions crystallise. Use ONLY when explicitly invoked via /grill-with-docs. Run at project init, before any large feature implementation, before any big pivot in project direction, OR when the operator can't write a clear acceptance criterion for the work.
---

<!--
Source: Matt Pocock — github.com/mattpocock/skills/blob/main/skills/engineering/grill-with-docs/SKILL.md
Original author: Matt Pocock (mattpocock/skills)
License: see upstream repository for license terms
Copied into this template pack on 2026-05-13.

Pocock's content body is preserved verbatim above. **One pack calibration** is encoded
inline in the `description` field: pack-narrowed trigger discipline (4 concrete triggers
+ explicit-invocation-only) appended to Pocock's broader description for Operating-AI
auto-match accuracy. Additional pack-specific calibrations are added in a clearly-demarcated
`## Pack calibration` section at the end (depth cap + multi-artifact closing prompts),
anchored to the operator profile in templates/MAINTAINING.md. Upstream sync — refresh
Pocock's body; preserve the description-trigger appendix and the Pack calibration section.

The operator-side trigger discipline lives in README §4.1. Sidecars CONTEXT-FORMAT.md
and ADR-FORMAT.md ship alongside this SKILL.md.
-->

<what-to-do>

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time, waiting for feedback on each question before continuing.

If a question can be answered by exploring the codebase, explore the codebase instead.

</what-to-do>

<supporting-info>

## Domain awareness

During codebase exploration, also look for existing documentation:

### File structure

Most repos have a single context:

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

If a `CONTEXT-MAP.md` exists at the root, the repo has multiple contexts. The map points to where each one lives:

```
/
├── CONTEXT-MAP.md
├── docs/
│   └── adr/                          ← system-wide decisions
├── src/
│   ├── ordering/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/                 ← context-specific decisions
│   └── billing/
│       ├── CONTEXT.md
│       └── docs/adr/
```

Create files lazily — only when you have something to write. If no `CONTEXT.md` exists, create one when the first term is resolved. If no `docs/adr/` exists, create it when the first ADR is needed.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

### Update CONTEXT.md inline

When a term is resolved, update `CONTEXT.md` right there. Don't batch these up — capture them as they happen. Use the format in [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).

Don't couple `CONTEXT.md` to implementation details. Only include terms that are meaningful to domain experts.

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR. Use the format in [ADR-FORMAT.md](./ADR-FORMAT.md).

</supporting-info>

---

## Pack calibration (pack-specific overrides; not from Pocock)

Anchored to the operator profile in `templates/MAINTAINING.md`. These augment Pocock's default behavior, they don't replace it.

### Depth cap (non-tech operator override)

Sessions cap at **15–30 questions, always** — including the project-init grill. Two signals to stop:

1. **Stop early** when the next questions stop revealing new decisions. That's alignment.
2. **Hard-stop at 30.** If gaps still surface, the scope is too big for one grill — split into modular grills on smaller scopes (one per major subsystem, feature area, or domain).

Pocock's 40–100 range in his upstream framing is descriptive of his cohort, not prescriptive. For the non-tech operator profile, fewer-but-deeper questions outperform more-but-shallow; the recommended-answer pattern (AI proposes, operator confirms or corrects) means each question carries weight.

### Multi-artifact closing prompts (Operating-AI auto-surface)

`/grill-with-docs` natively writes to CONTEXT.md and ADRs. **At the end of every grill session**, also surface closing prompts for the pack's other curated artifacts so the operator can capture them while alignment context is fresh:

- **`docs/MANUAL_TESTS.md` critical paths** — *"Are there critical user paths from this scope that should land in `docs/MANUAL_TESTS.md`?"* These are the flows the operator commits to walking before promoting preview to production.
- **`LEDGER.md ## User preferences`** — *"Did this session establish any user-preference defaults (commit/push behavior, default sub-agent model, communication style)? Worth capturing now."*
- **`plans/AUDIT_SCHEMA.md` dimension checklists** — *"Did this grill surface new project-specific invariants worth adding to AUDIT_SCHEMA dimension checklists?"*
- **`/to-prd` + `/to-issues` conventions** — *"Both `/to-prd` and `/to-issues` ship with placeholders for tracker URL + triage label (`/to-prd` also asks: tracker vs local destination). Want to populate both now while the project's tracker conventions are fresh?"* Operator-decided; populate `conventions.md` in BOTH skill directories from one operator answer (`/to-prd` and `/to-issues` share the same tracker info — operator types once, both files filled). Auto-populates on first skill invocation if skipped here.

The AI surfaces these prompts automatically; the operator decides which captures to action. Pocock's skill doesn't auto-write to these files — this is a pack-level behavior layered via `## Pack calibration`, not a fork of Pocock's content.

The operator-side trigger discipline (project init / large feature / pivot / can't-write-acceptance-criterion fallback) lives in `README §4.1`.
