---
name: ledger-capture
description: Capture session-spanning knowledge into LEDGER.md — a lesson from an incident, a design rationale not in any plan doc, a new key invariant, or an open/resolved investigation. Use when chat-only knowledge would otherwise vanish at session end.
---

# /ledger-capture

**When to invoke:** you've noticed something worth preserving past the current conversation — a lesson from a bug, a design decision made in chat, a non-obvious load-bearing fact about the system, or an open question to track. Don't let it evaporate; call this skill and the structured content lands in `LEDGER.md`.

This skill writes into the categorical structure that `LEDGER.md` defines and that the audit's DOCS-dimension fidelity check reads. **Don't improvise sections** — the schema is shared with `/ledger-lint` and `/audit`.

> `LEDGER.md` is the operator-curated, git-tracked layer. It is **distinct** from Claude Code's auto-memory (`~/.claude/projects/<>/memory/MEMORY.md`) and from Cloud Managed Agents memory + Dreaming. Don't move content between layers.

## Protocol

### Step 1 — Categorize

Ask the user which category. If the prior message makes it obvious, propose the category and confirm:

1. **Lesson** — something broke, we fixed it, and there's a generalization worth remembering. Distinct from a CHANGELOG bug-fix entry: a lesson survives after the bug is forgotten.

   *Example:* "Server-side Decimal converted to JS number at API boundary, losing precision on transactions >$10K. Fix: serialize as string. **Lesson —** money values cross JS boundaries as strings, not numbers."

2. **Design rationale** — we chose X over Y because Z, and the reasoning isn't in any plan doc. Typically a decision made in conversation. **ADR check:** if the decision meets all 3 ADR criteria (hard-to-reverse + surprising-without-context + result-of-real-tradeoff), recommend the operator author it as an ADR via `/grill-with-docs` (or directly in `docs/adr/`) instead and exit Step 1. LEDGER design rationales are for **tactical** decisions that don't meet ADR threshold but are still worth remembering for context.

   *Example:* "Chose Neon over Supabase for the DB. Alternatives: Supabase (built-in auth + storage), Planetscale (no longer free tier). Why Neon: branch-per-PR matches our preview-deploy workflow; cheaper at our scale; can add auth via NextAuth separately."

3. **Key invariant** — a load-bearing fact about the system that isn't obvious from any single file. The kind of thing whose violation would cause a bug.

   *Example:* "Every API route handler must call `requireAuth()` before any data access. Load-bearing in: `app/api/**/route.ts`. Violation = user can read other users' data (multi-tenant leak)."

4. **Open investigation** — an uncertainty worth tracking. Something you don't know the answer to yet, with a "to resolve" action.

   *Example:* "Why does the `/api/transactions` route 502 intermittently under load? **To resolve:** add instrumentation per `/diagnose` Phase 4 on next high-traffic window; correlate with Vercel function timeout logs."

5. **Close investigation** — resolve and remove an existing entry from `LEDGER.md`'s `## Open investigations` section. (No creation-side example — Close removes existing content rather than creating new.)

### Step 2 — Elicit the specifics

Match prompts to the category. Keep them short.

**For Lesson:**
- "What happened? (the incident — short, 2-3 sentences)"
- "What's the fix? (file, pattern, or shipped commit)"
- **"What's the lesson?** (the generalization that survives past this incident)"

The lesson is the load-bearing part. Push on it — "we fixed this bug" isn't a lesson worth a ledger entry. The lesson is a principle.

**For Design rationale:**
- "What was decided?"
- "What was the alternative considered?"
- "Why this choice?"
- "What would change the call?" (optional — helps future-you judge whether to revisit)

**For Key invariant:**
- "What's the invariant?" (one clear sentence)
- "Where is it load-bearing?" (which file/subsystem depends on it)
- "What breaks if it's violated?"

**For Open investigation:**
- "What's the question?"
- "What are the possibilities?" (optional)
- "How would you resolve it?" (the specific action — grep this, check that, ask the person who knows)

**For Close investigation:**
- Read `LEDGER.md`'s `## Open investigations` section. Show entries with numbers.
- Ask which one to close.
- Confirm the resolution (what did we learn?) before removing.

### Step 3 — Place in LEDGER.md correctly

Read `LEDGER.md` at the repo root. Find the target section. Insert in the format that matches existing entries:

| Category | Section | Format |
|---|---|---|
| Lesson | `## Lessons from incidents` | `### YYYY-MM-DD — <title>`, body 2-3 paragraphs (what happened, fix, lesson), ending with bold `**Lesson —** <generalization>` |
| Design rationale | `## Captured design rationales` | `### YYYY-MM-DD — <title>`, body describing decision + alternatives + rationale; close with link to plan doc if any |
| Key invariant | `## Key invariants worth remembering` | Single bullet: `**<Invariant name>** — <one-sentence explanation; where it's load-bearing; what breaks if violated>` |
| Open investigation | `## Open investigations` | `### <short title>`, body describing the question, then `**To resolve:** <specific action>` |
| Close investigation | Remove from `## Open investigations` | Delete the entire `### <title>` sub-section |

New entries land at the **top** of their section (most recent first).

### Step 4 — Show the diff, then commit per project preference

Show the user the exact change you're about to make:

```
Preview of LEDGER.md change:
<inline diff>
```

**Commit-and-push behavior** depends on the project's `LEDGER.md` `## User preferences` section:

- If preferences declare *"commits and pushes happen without asking"* → commit + push as a single flow without prompting. The user has set the policy; respect it.
- Otherwise → show the diff and prompt for explicit approval before committing.

Commit on the **current branch** (capture rides with the triggering PR):

```
git add LEDGER.md
git commit -m "docs: ledger <category> — <short title>"
git push -u origin <current-branch>
```

Commit message examples:
- `docs: ledger lesson — <short> (<generalization>)`
- `docs: ledger rationale — <what was decided>`
- `docs: ledger invariant — <short>`
- `docs: ledger open investigation — <short>`
- `docs: ledger close investigation — <short>`

### Step 5 — Graduation check (Lessons and Key Invariants only)

For new entries of category **Lesson** or **Key Invariant**, run this check after Step 4 commits. For all other categories (Design rationale / Open / Close investigation), skip — those categories don't graduate.

**Goal:** detect when a captured lesson/invariant indicates a recurring pattern worth promoting to AGENTS.md's always-loaded `## Common pitfalls` section.

#### Apply the 3 graduation criteria

1. **Frequency check.** Scan LEDGER.md for entries on the same root cause as the new entry:
   - Lessons whose `**Lesson —**` line is a near-synonym of the new entry's generalization
   - Invariants describing the same load-bearing fact
   - Optionally: `git log --grep` for `fix:` commits citing the same issue
   Count the cluster (new entry + matches). If **<3**, exit Step 5 (no graduation).

2. **Universal applicability check.** Is the rule unconditional ("always X" / "never Y") or context-dependent ("if conditions A and B, then Y")? If context-dependent, exit Step 5 — the rule needs full LEDGER context to apply.

3. **Concision check.** Can the rule be expressed in 1-2 lines without losing teeth? If a reader would need the incident's full context to understand the rule, exit Step 5.

If **all 3 hold**, defer to `/pitfall-graduate --auto` with the cluster as input. The agent immediately invokes `/pitfall-graduate` per its protocol. The pitfall lands in AGENTS.md with a `> [!warning] Pending operator review` callout — operator confirms / rolls back / defers during the next `/ledger-lint` Step 0.

#### Why auto-graduate (not flag-and-wait)

During long autonomous tasks, the agent shouldn't halt for "should I graduate this pitfall?" — that defeats the always-loaded mechanism's value. Auto-graduation lets the agent keep moving; the pending-review marker preserves operator authority over what survives in AGENTS.md.

If the operator is actively in the conversation when the threshold is hit, the agent MAY ask for confirmation rather than auto-deferring — but the default is auto with pending marker.

## Anti-patterns to avoid

- **Don't add entries that belong elsewhere.** A bug fix goes to `CHANGELOG.md`. A new feature's design goes to a plan doc in `plans/`. LEDGER is for content that doesn't fit the structural triggers other docs already have.
- **Don't add boilerplate invariants.** "The code must compile" is not a LEDGER invariant. Invariants are non-obvious cross-cutting facts whose violation causes bugs.
- **Don't re-state code.** If an invariant is trivially visible from one file, cite the file instead. LEDGER is for cross-cutting or non-obvious facts.
- **Capture the lesson, not the incident.** A LEDGER lesson should be useful even if the specific incident is forgotten.
- **Don't categorize creatively.** Five categories exist for a reason. If something doesn't fit, either (a) it doesn't belong in LEDGER, or (b) raise a Schema observation in the next audit so the schema can evolve.
- **Don't conflate with auto-memory or Dreaming.** Those layers are agent-curated and out of git; LEDGER is operator-curated and in git. Capture here, not there.

## Related

- `/ledger-lint` — periodic audit (every 1-2 weeks); finds items that should be captured but weren't.
- `LEDGER.md` Maintenance section at the top of the file.
- Audit's DOCS-dimension LEDGER.md-fidelity check (`plans/AUDIT_SCHEMA.md` Documentation fidelity) — uses the same categorical structure.

## Invariants

- **Categories are fixed.** Five categories: Lesson / Rationale / Invariant / Open investigation / Close investigation. Don't invent new ones.
- **Section names in LEDGER.md are load-bearing.** `/ledger-lint` and the audit's DOCS check read these. Don't rename without coordinating both.
- **Commit policy follows project preference.** Don't impose a default; read `LEDGER.md`'s `## User preferences` section.
- **One capture per invocation.** If multiple things need capturing, run the skill multiple times. Each capture gets its own commit for clean git history.
