---
name: ledger-lint
description: Periodic audit of LEDGER.md. Flags resolvable open investigations, drifting invariants, dead lessons, and candidate captures from recent commits. Produces a punch list for human review; does NOT auto-edit. Suggested cadence every 1–2 weeks.
---

# /ledger-lint

**When to invoke:** periodically (every 1–2 weeks) or after a run of merges. Sweeps `LEDGER.md` for drift and surfaces missed captures. Does not modify anything — produces a review checklist for the operator to approve item-by-item. Approved items go through `/ledger-capture`.

This skill complements the audit's DOCS-dimension LEDGER.md-fidelity check (`plans/AUDIT_SCHEMA.md`): the audit runs at quarterly cadence with full project context; `/ledger-lint` runs between audits to catch what would otherwise drift.

> Targets `LEDGER.md` (operator-curated, git-tracked) at the repo root — **not** Claude Code's auto-memory dir or any Cloud Managed Agents memory store. Those layers have their own hygiene mechanisms.

## Protocol

### Step 0 — Review pending auto-graduations (run first)

Pending auto-graduations are the highest-priority drift signal because the auto-graduated bullets are loaded into every session — they shouldn't sit unreviewed. Run this step **before** any LEDGER scan.

#### Detect pending items

Read AGENTS.md's `## Common pitfalls` section. For each bullet carrying a `> [!warning] Auto-graduated ... pending operator review` callout, this is a pending item.

If no pending items exist, skip to Step 1 silently.

#### Walk each pending item

For each pending graduation, surface to operator:

```
Pending graduation #N: <title>

Bullet (auto-graduated YYYY-MM-DD):
  <AGENTS.md bullet content>

Source LEDGER entries:
  - <entry 1 title> (LEDGER.md ## Lessons from incidents)
  - <entry 2 title> (LEDGER.md ## Key invariants worth remembering)
  ...

Decision: confirm / rollback / defer?
```

Wait for explicit operator decision per item before continuing to the next.

#### Action each decision

- **confirm**:
  - In AGENTS.md, replace `> [!warning] Auto-graduated YYYY-MM-DD — pending operator review` with `> [!info] Graduated YYYY-MM-DD (confirmed)`.
  - In LEDGER source entries, replace `(auto, pending review)` callouts with `(confirmed)`.
  - Commit: `docs: confirm pitfall graduation — <title>`.

- **rollback**:
  - In AGENTS.md, remove the bullet and its pending-review callout entirely.
  - In LEDGER source entries, remove the `Graduated to AGENTS.md` callouts (the original LEDGER content stays untouched).
  - Commit: `docs: rollback pitfall graduation — <title>`.

- **defer**:
  - No file changes. The pending callout remains; this graduation resurfaces in next lint pass.

Each decision is its own commit. Clean git history.

#### Continue to Step 1

Once all pending graduations are walked, continue to Step 1 (Baseline) for the standard lint pass.

### Step 1 — Establish the baseline

1. Read `LEDGER.md` at the repo root.
2. Determine when LEDGER.md was last meaningfully updated: `git log -1 --format=%H --follow LEDGER.md` gives the last commit that touched it.
3. Collect commits since then: `git log <last-ledger-sha>..HEAD --oneline` → candidates for scanning.
4. If the scan window exceeds ~50 commits, narrow to the most-recent 50 and note "older commits not scanned."

### Step 2 — Audit `## Open investigations`

For each entry:

- Read the `**To resolve:**` action.
- Try to resolve it from current state:
  - If it says "check X" → read X
  - If it says "grep for Y" → run the grep
  - If it says "verify against Z" → check Z
  - If it cites an external dependency (e.g. "wait for upstream patch"): check the relevant `package.json` (or stack equivalent) version vs. current upstream release notes (operator's call whether to dig).
- If the investigation can now be answered, flag for **possible removal** with the resolution.
- If still unanswered, note "still open, action needed: <action>".

### Step 3 — Audit `## Key invariants worth remembering`

For each invariant bullet:

- Identify the file or subsystem it's load-bearing for (usually stated inline).
- Spot-check: read a few lines of that file to confirm the invariant still holds.
  - Example: invariant "Decimal never crosses the server/client boundary" → read 2-3 random `page.tsx` files (or framework equivalent), confirm the invariant.
- Do NOT do exhaustive verification — sanity check, not a full audit.
- If drift is suspected, flag for **verification needed**. Never auto-remove an invariant; the operator decides.

### Step 4 — Audit `## Lessons from incidents` (light touch)

Lessons are historical — they don't go stale. But check:

- Is the linked file/path still present? (If renamed/deleted, flag.)
- Is the **Lesson —** part actually a generalization, or did it drift into being just an incident note? (If incident-only, flag for re-write.)

If both look fine, move on. Lessons typically don't need attention on a lint pass.

### Step 5 — Audit `## Captured design rationales` (light touch)

Rationales are durable — they document a decision at a point in time. Check:

- Has the decision been revisited since capture? Scan recent commits for rework in the same area.
- If the decision was undone or revised, flag as **needs update**.

### Step 6 — Scan recent commits for missed captures

Look at commits since LEDGER.md was last touched (Step 1). Pattern-match for candidates:

| Pattern in commit message / diff | Likely category |
|---|---|
| `fix:`, `revert:`, "incident", "regression", "race", "broken upstream" | Possible **lesson** (if there's a generalization) |
| "decided", "chose X over Y", "dropped in favor of", "revised approach" | Possible **rationale** |
| Schema migration adding `NOT NULL`, `@@unique`, or new index on a hot path | Possible **invariant** (the constraint is the invariant) |
| `// TODO: verify`, "unknown", "not sure why", commit body with open questions | Possible **investigation** |

For each candidate:

- Read the commit message (and short diff if helpful).
- Ask: is there a generalization worth preserving? (Not every fix is a lesson.)
- Is the decision documented elsewhere? (If it's in a plan doc or already in CHANGELOG with sufficient detail, skip.)

Flag genuine candidates for capture; skip routine ones.

**Project-specific signal sources** (`[Populated by /grill-with-docs at project init. Examples to look for: audit-fix commits referencing AUDIT_<N>:<DIM>-<NN>, schema migrations adding constraints, commits touching auth/middleware files. The pattern is project-specific signal sources where invariants and lessons tend to surface — fill in as the project's own surface area becomes clear.]`)

### Step 7 — Produce the punch list

Present findings as a compact, actionable list. Format:

```
# /ledger-lint report — <date>

Baseline: LEDGER.md last touched at <sha> (<date>); <N> commits scanned since.

## Investigations
- [ ] `<title>` — likely resolvable. Evidence: <what you found>.
- [ ] `<title>` — still open; action: <what's needed>.

## Invariants
- [ ] `<invariant>` — needs verification. <why you suspect drift>.
- [ ] (others all look current)

## Lessons / Rationales
- [ ] `<title>` — references file that no longer exists (`<file>`)
- [ ] `<title>` — body reads as incident-only; lesson generalization missing
- [ ] (others all look current)

## Candidate captures from recent commits
- [ ] <sha> "<subject>" — looks like a missed **lesson**. <why>
- [ ] <sha> "<subject>" — looks like a missed **rationale**. <why>
- [ ] <sha> "<subject>" — looks like a missed **invariant**. <why>

## Suggested actions
1. Close investigation X via `/ledger-capture` (close)
2. Verify invariant Y (check `<file>:<line>`)
3. Capture new lesson from commit Z via `/ledger-capture` (lesson)
```

### Step 8 — Do NOT auto-edit

The lint produces suggestions, not changes. The operator reviews and decides which items to action. Approved items go through `/ledger-capture`.

## Anti-patterns

- **Don't over-flag.** If unsure whether an invariant is drifting, say "looks current" rather than flagging uncertain items. False positives create alert fatigue.
- **Don't resolve investigations for the operator.** You can say "appears resolvable; resolution would be <X>," but the operator confirms before removal.
- **Don't edit LEDGER.md from this skill.** That's `/ledger-capture`'s job. Splitting responsibilities means lint runs side-effect-free.
- **Don't scan all commits forever.** Bound the scan at 50 commits; mention older commits not scanned.

## Related

- `/ledger-capture` — where approved findings get applied.
- Audit's DOCS-dimension LEDGER.md-fidelity check (`plans/AUDIT_SCHEMA.md`) — quarterly, deeper, with full project context.
- `LEDGER.md` Maintenance section at the top of the file.

## Invariants

- **Read-only for the LEDGER scan (Steps 1-8).** This skill never modifies `LEDGER.md` during the lint scan. Output of Steps 1-8 is a punch list only.
- **Step 0 is the only write path** — it actions operator-confirmed graduation review (confirm / rollback). Operator decision required for every Step 0 edit; never auto-action.
- **Operator decides.** Never close an investigation, remove an invariant, or capture a candidate without explicit approval.
- **Bounded scan.** Default 50-commit ceiling on the missed-captures pass; surface the limit when truncated.
- **Categories match `/ledger-capture`.** Lesson / Rationale / Invariant / Open investigation. Don't invent new categories during scan.
