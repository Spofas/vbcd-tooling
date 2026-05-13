---
name: pitfall-graduate
description: Promote a recurring LEDGER lesson or invariant into AGENTS.md's Common Pitfalls section so it loads on every session. Use only when all 3 criteria hold (frequency ≥3, universal applicability, fits in 1-2 lines). Two modes — --auto (agent-initiated; flags as pending operator review) and operator-initiated (pre-confirmed).
---

# /pitfall-graduate

**When to invoke:** when a LEDGER lesson or key invariant has surfaced enough times to warrant always-loaded status. Most commonly auto-invoked by `/ledger-capture` after a new Lesson or Key Invariant crosses the threshold during agent work; can also be operator-invoked when they spot a pattern themselves.

**Why this skill exists:** without graduation, recurring pitfalls stay buried in LEDGER.md — read on demand, not loaded every session. The AI keeps making the same mistake because the lesson isn't in always-loaded context. Graduation promotes load-bearing rules to AGENTS.md so they're enforced from session start. The two-mode design lets agents act during long autonomous runs without halting for confirmation, while preserving operator authority via `/ledger-lint` Step 0 review.

## Invocation modes

- **`/pitfall-graduate <lesson-ref> --auto`** — agent-initiated. Writes to AGENTS.md with a `> [!warning] Pending operator review` callout. Doesn't pause for confirmation; review happens later via `/ledger-lint` Step 0.
- **`/pitfall-graduate <lesson-ref>`** — operator-initiated. No pending-review callout (the operator's deliberate decision is the confirmation).

`<lesson-ref>` is either:
- A LEDGER entry title (operator-supplied), e.g., `/pitfall-graduate "2026-05-10 — Decimal at boundaries"`
- A cluster of LEDGER entry titles (when `/ledger-capture` detects multiple matching lessons), passed as a list

## Criteria — all 3 must hold

1. **Frequency** — the pattern has surfaced ≥3 times. Count includes the current entry plus prior LEDGER entries on the same root cause OR commits referencing the same lesson. If <3, decline.

2. **Universal applicability** — the rule is unconditional ("always X" / "never Y"). Context-dependent rules ("if conditions A and B, then Y") stay in LEDGER; they need full context, which doesn't fit in 1-2 lines.

3. **Concision** — the rule fits in 1-2 lines without losing teeth. If a reader needs the full incident to understand the rule, it's not concise enough.

If any criterion fails, decline with explicit reason. Do not write to AGENTS.md.

## Protocol

### Step 1 — Identify the candidate(s)

Read the source LEDGER entries. If invoked with a single entry ref, scan LEDGER for other entries on the same root cause. If invoked with a cluster, all members are inputs.

### Step 2 — Apply the 3 criteria

Run each test explicitly. Show results (or, in `--auto` mode, log them in the commit body):

- Frequency: N entries match; threshold is 3.
- Universality: rule is "always/never" — yes/no.
- Concision: rule fits in 1-2 lines — yes/no.

If all 3 hold, proceed. If any fail, exit with explicit reason.

### Step 3 — Draft the AGENTS.md bullet

Format:

```
- **<Short title>** — <concrete example>. <How to avoid>.
```

Max 2 lines. The title names the rule; the example anchors it to a real situation; the avoidance is the action the agent takes.

Example:
```
- **Decimal at boundaries** — monetary values must be Decimal at all server/client crossings.
  Never pass raw `number` from a server component to a client component for currency.
```

### Step 4 — Coordinate two diffs

Two simultaneous edits, single atomic commit:

**AGENTS.md (insert):**
- Find the `## Common pitfalls` section.
- Insert the new bullet at the **top** of the section (most recent first).
- If `--auto`, prepend the callout immediately above the bullet:
  ```
  > [!warning] Auto-graduated YYYY-MM-DD — pending operator review (see /ledger-lint Step 0)
  ```

**LEDGER source entries (callout):**
For each source entry, add a callout at the top of the entry body:

- `--auto` mode:
  ```
  > [!info] Graduated to AGENTS.md `## Common pitfalls` (auto, pending review) — YYYY-MM-DD
  ```
- Manual mode:
  ```
  > [!info] Graduated to AGENTS.md `## Common pitfalls` (confirmed) — YYYY-MM-DD
  ```

LEDGER source content stays untouched — only the callout is added.

### Step 5 — Commit

Show the diffs.

In **`--auto` mode**, commit without operator confirmation:
```
git add AGENTS.md LEDGER.md
git commit -m "docs: auto-graduate pitfall — <title> [pending review]"
```

In **manual mode**, show the diffs and prompt for operator approval before committing:
```
git add AGENTS.md LEDGER.md
git commit -m "docs: graduate pitfall — <title> [LEDGER → AGENTS.md]"
```

Push behavior follows LEDGER.md `## User preferences` (same as `/ledger-capture`).

### Step 6 — Report

Brief summary to operator (or commit body in `--auto` mode):
- Title graduated
- Mode (`--auto` / manual)
- Source LEDGER entries
- If `--auto`: "Pending operator review during next `/ledger-lint`."

## Anti-patterns

- **Don't graduate context-dependent lessons.** "Always X" is graduable; "If conditions A and B, then Y" is not. The latter needs the LEDGER entry's full context to apply correctly.
- **Don't delete LEDGER source entries.** Graduation is promotion, not removal. The LEDGER entries stay (with callouts) for traceability and potential rollback.
- **Don't graduate before frequency hits 3.** A single occurrence is not a pattern; 2 might be coincidence. Threshold of 3 is the discipline.
- **Don't skip the criteria checks in `--auto` mode.** The agent must apply all 3 tests explicitly. If any fails, decline — even if `/ledger-capture` suggested the graduation.
- **Don't graduate from `/ledger-lint`'s punch list directly via `--auto`.** Auto-graduation happens at capture time, when the new lesson and its cluster are fresh in context. If `/ledger-lint` surfaces a missed graduation candidate, the operator invokes `/pitfall-graduate` *manually* (no `--auto`).
- **Don't graduate Design rationales or Open investigations.** Only Lessons and Key Invariants are graduable. Rationales are contextual; investigations are pending resolution. Neither belongs in always-loaded substrate.

## Related

- `/ledger-capture` — invokes this skill in `--auto` mode (Step 5 of `/ledger-capture`). Auto-graduation happens at capture time, not later.
- `/ledger-lint` — Step 0 surfaces pending auto-graduations for operator confirm / rollback / defer. Without lint review, auto-graduations sit indefinitely with the pending callout.
- AGENTS.md `## Common pitfalls` — the destination section.
- LEDGER.md `## Lessons from incidents` + `## Key invariants worth remembering` — the graduable source sections.
- AGENTS.md §8 (Accumulate, Don't Restart) — the principle this skill operationalizes at the substrate layer.

## Invariants

- **Atomic two-file commit.** AGENTS.md and LEDGER.md updates ship in one commit. Never AGENTS.md without the LEDGER back-references.
- **All 3 criteria must hold.** If frequency, universality, or concision fails, decline. No partial graduations.
- **Auto mode always marks pending.** Even if the agent is highly confident, `--auto` invocation gets the pending-review callout. Confirmation is the operator's act, not the agent's.
- **Manual mode is pre-confirmed.** Operator-initiated invocations (no `--auto` flag) skip the pending callout. Invoking the skill IS the confirmation.
- **LEDGER source entries are never deleted.** Graduation promotes; it doesn't remove. Operator can manually prune later if desired.
- **Only Lessons and Key Invariants graduate.** Design rationales and Open investigations stay in LEDGER permanently.
- **One graduation per invocation.** If multiple clusters cross the threshold simultaneously, `/ledger-capture` invokes `/pitfall-graduate` multiple times in sequence — each as its own commit. Clean git history.
