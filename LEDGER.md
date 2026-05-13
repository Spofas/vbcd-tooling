# LEDGER.md

Session-spanning knowledge that doesn't fit elsewhere. Append-only via `/ledger-capture`; periodically audited via `/ledger-lint`.

> **Why named LEDGER.md (not MEMORY.md):** to avoid collision with three agent-managed "memory" surfaces — Claude Code's auto-memory at `~/.claude/projects/<>/memory/MEMORY.md`, Cloud Managed Agents memory store, and Dreaming. **This file is the operator-curated, git-tracked, project-scoped layer**; the others are agent-curated and out of git. Don't move content between them.

## Maintenance

- New entries go at the **top** of their section (most recent first).
- `/ledger-capture` writes here; `/ledger-lint` reads only for Steps 1-8 (Step 0 is the only write path, and only for graduation confirm/rollback per operator decision).
- Audit's DOCS-dimension LEDGER-fidelity check reads this structure too — **section names are load-bearing.** Don't rename them.
- File size is operator-managed: when a section grows large, `/ledger-lint` will surface candidates for archival or removal.
- **Graduation**: when a Lesson or Key Invariant hits all 3 criteria (frequency ≥3, universal applicability, concision), `/ledger-capture` auto-defers to `/pitfall-graduate`. The graduated rule lands in AGENTS.md `## Common pitfalls`; the LEDGER source entry stays in place with a `> [!info] Graduated to AGENTS.md` callout (traceability + rollback path). Auto-graduations are pending until confirmed during `/ledger-lint` Step 0.

## User preferences

`[Populated by /grill-with-docs at project init. Examples to capture during alignment:`
- *Commit/push behavior* — "commits and pushes happen without asking" vs. "show diff and prompt before each commit"
- *Default sub-agent model* — capability-first (opus) vs. cost-first (sonnet/haiku) vs. auto
- *Communication preferences* — terse vs. verbose, ask-before-acting threshold, when to use plan-mode
- *Stack-specific defaults* — preferred package manager, formatter, test runner, deploy target

`Format: bulleted list of key=value pairs, one preference per line.]`

## Lessons from incidents

*Empty at init. Populated by `/ledger-capture` (lesson).*

**Format:**
```
### YYYY-MM-DD — short title

[2-3 paragraphs: what happened (the incident), what's the fix (file/pattern/commit),
and the lesson (the generalization that survives past this incident).]

**Lesson —** <one-sentence generalization that's useful even if the incident is forgotten>
```

A lesson is the load-bearing part. "We fixed this bug" isn't a lesson worth a ledger entry. The lesson is a principle that survives.

## Captured design rationales

*Empty at init. Populated by `/ledger-capture` (rationale).*

> **ADR precedence.** If a decision meets ADR criteria (hard-to-reverse + surprising-without-context + result-of-real-tradeoff — all three required), capture it as an ADR in `docs/adr/` instead. Those are the canonical home for consequential architectural decisions. This LEDGER category is for **tactical** decisions made in conversation that don't meet ADR threshold but are still worth remembering for context (library picks, naming conventions, mid-tier choices, "we picked X today, might revisit").

**Format:**
```
### YYYY-MM-DD — short title

[Body: what was decided, what alternatives were considered, why this choice. Optionally:
"What would change the call?" — what new evidence or constraint would warrant revisiting.]

[If a plan doc captures the implementation, link to it.]
```

For decisions made in conversation that don't otherwise live in a plan doc.

## Key invariants worth remembering

*Empty at init. Populated by `/ledger-capture` (invariant).*

**Format:** single bullet per invariant.

```
- **<Invariant name>** — <one-sentence explanation>; load-bearing for <which file/subsystem>; <what breaks if violated>.
```

Invariants are non-obvious cross-cutting facts whose violation causes bugs. Don't include trivial things visible from a single file ("the code must compile" is not an invariant).

## Open investigations

*Empty at init. Populated by `/ledger-capture` (open investigation). Removed by `/ledger-capture` (close investigation) once resolved.*

**Format:**
```
### <short title>

[Body: what's the question, what are the possibilities (optional).]

**To resolve:** <specific action — grep this, check that, ask the person who knows>
```

Used to track uncertainties worth not forgetting. The `**To resolve:**` line is what makes the entry actionable.
