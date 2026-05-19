---
name: audit
description: Run a formal codebase audit per the project's AUDIT_SCHEMA.md. Use ONLY when explicitly invoked. Run before meaningful releases, after major architectural changes or P0 incidents, when drift signals surface (stale TODO / hard-to-navigate codebase / avoidance behavior), or as an occasional cadence (rough monthly-to-quarterly hum). Supports full-scope (parallel sub-agents per phase group), group-scoped, dimension-scoped, --resume, and --tracker modes.
---

# Audit

Conduct a formal codebase audit of the project per the schema in `plans/AUDIT_SCHEMA.md`.

## Authoritative source

`plans/AUDIT_SCHEMA.md` is the single source of truth for dimensions, phase groups, priority order, severity taxonomy, finding-record format, methodology, report/tracker structure, verification criteria, and audit-failure-modes catalog. Read it end-to-end at the start of every invocation. Do not rely on memory from prior audits, and do not duplicate schema content in this skill.

## Invocation modes

Parse the first positional argument to determine scope:

- **No argument** → **full scope.** Dispatch four sub-agents in parallel, one per phase group (Foundation, Runtime, Surface, Supplementary), then aggregate.
- **`<group>`** where `group ∈ {foundation, runtime, surface, supplementary}` → **group-scoped.** Run in-turn across the group's dimensions.
- **`<dimension>`** where `dimension ∈ {data-integrity, architecture, security, reliability, performance, ux, testing, dependencies, documentation}` → **single-dimension.** Run in-turn.
- **`--resume`** → resume the most recent incomplete audit (see §Resume below).
- **`--tracker`** → open the latest `audits/AUDIT_*_FIXES.md` and walk through `open` items, allowing batch status updates. Keeps tracker fresh between audits (see §Tracker mode).

Group and dimension vocabularies are disjoint, so parse is unambiguous. On an invalid argument, print the accepted vocabulary and exit without producing artifacts.

**Examples**
- `/audit` → full scope, parallel sub-agent dispatch.
- `/audit foundation` → foundation group only (DATA + ARCH + SECU), in-turn.
- `/audit security` → security dimension only.
- `/audit --resume` → continue the most recent incomplete audit at matching SHA + schema hash.
- `/audit --tracker` → walk the latest tracker for status updates without producing a new audit.

## Steps

1. **Load the schema.** Read `plans/AUDIT_SCHEMA.md` in full. Compute its hash via `git hash-object plans/AUDIT_SCHEMA.md` for the metadata block. This establishes dimensions, phase-group definitions, severity taxonomy, finding-record format, methodology, report structure, and audit-failure-modes catalog for this invocation.

2. **Parse arguments** per §Invocation modes. The first positional token determines scope (`full`, group name, dimension name, `resume`, `tracker`); everything after is the **operator seed** (free-text focus shifters; see §Operator seed). If the seed is empty, fall back to `.claude/audit-seed.md` if present; else seed is `(none)`. On `resume`, the seed is loaded from the partial report's metadata, NOT from this invocation. On `tracker`, see §Tracker mode.

3. **Determine audit number N.**
   - Normal run: list `audits/AUDIT_*_REPORT.md`, take the highest integer `N`, use `N+1`.
   - Resume: use the existing N of the partial report.
   - First-ever audit: ensure `audits/` exists, `N = 1`.

4. **Capture shared metadata.** Current commit SHA (`git rev-parse HEAD`), schema hash (from step 1), date, auditor (`claude via /audit` or codex equivalent), scope (human-readable: `"full"`, `"foundation"`, `"data-integrity"`, …), branches in play, **operator seed** (resolved per step 2). Seed is recorded in metadata so `--resume` preserves the original operator intent.

5. **Execute per mode.**

   **Full scope:** Dispatch four sub-agents in parallel (per the dispatch path matching your agent — see §Cross-vendor dispatch below). Each sub-agent gets the contract in §Sub-agent contract. Wait for all four; re-dispatch any that fail. Aggregate their returned findings into the unified report.

   **Group scope / Dimension scope / Resume:** Run in-turn. Work dimension by dimension in the schema's priority order, within the scope. For resume, start from the first missing dimension section.

6. **Write artifacts** per the schema's §Report format and §Tracker format. Both live in `audits/`:
   - `audits/AUDIT_<N>_REPORT.md` — declare scope explicitly in Metadata. For scoped audits, include the stub "Out of scope for this audit. Last covered in `audits/AUDIT_<M>_REPORT.md`." for each dimension not in scope, with `M` resolved from the filesystem. Write the report in chunks per the 200-line rule: Metadata + Executive summary as one write, each dimension section as its own write, Prioritized action plan + Metrics + Delta + Schema observations at the end.
   - `audits/AUDIT_<N>_FIXES.md` — one row per finding ID, status `open` for all.

7. **Side-effect updates.**
   - `docs/TODO.md` — add new P0/P1 items, keyed by audit-qualified finding ID (e.g. `AUDIT_<N>:DATA-03`).
   - `CHANGELOG.md` — single new entry: "Audit N conducted (scope: <scope>); X findings (P0=a, P1=b, P2=c, P3=d)."
   - **LEDGER.md capture trigger** — scan findings for any matching LEDGER.md categories (incident-class lesson with structural impact, captured rationale, new key invariant, open or resolved investigation). For each match, surface a prompt to the operator: `"Finding <ID> looks captureable per LEDGER.md categories — invoke /ledger-capture? (yes / skip / list-all)."` Don't auto-capture; capture decisions stay with the operator.

8. **Meta-review prompt (signal-based).** After artifacts are written, evaluate two triggers. Surface a prompt if either fires:
   - **Signal trigger:** the Schema observations section is non-empty. Surface: `"Audit <N> captured schema observations — consider running a meta-review per plans/AUDIT_SCHEMA.md §Schema maintenance."`
   - **Cadence trigger:** `N %% 5 == 0` AND no CHANGELOG entry containing "meta-review" since audit `N-5`. Surface: `"Audit <N> reaches the every-5 cadence. Schedule a meta-review or defer."`
   - The prompt is a reminder; do not auto-run a meta-review.

9. **Report back.** One short summary in chat: scope, severity distribution, top 3 findings by severity, paths to the two new files, schema-observations count, LEDGER.md capture prompts (if any), meta-review prompt (if any).

## Cross-vendor dispatch

Two surface-specific paths for parallel sub-agent dispatch in full-scope mode. Use the path matching your runtime.

### Claude Code path

Spawn 4 sub-agents in parallel via a single message containing 4 Agent tool calls. Each call uses `subagent_type: General` (or `Explore` for read-only phases) with explicit `model: opus` for capability. Sub-agents share the contract in §Sub-agent contract.

### Codex path

Spawn 4 parallel agents via `/agent` + MultiAgentV2. Each agent gets the same contract; orchestration syntax follows OpenAI Codex docs current at the time of authoring. Use a capability-tier model (e.g. `gpt-5.5-codex` or successor) for thoroughness over speed.

The sub-agent contract below is identical for both paths; only dispatch syntax differs.

## Sub-agent contract (full-scope mode)

When dispatching the four sub-agents, each receives a prompt of this shape:

```
Run Phase <X> of project audit <N>.

Scope: dimensions {D1, D2, D3} (per plans/AUDIT_SCHEMA.md §Phase groups, Group <X>).

Instructions:
1. Read plans/AUDIT_SCHEMA.md end-to-end before starting.
2. Execute the audit for the dimensions in your scope, following the methodology and finding-record format the schema specifies.
3. Shared metadata to include on all findings: commit SHA = <SHA>, schema hash = <HASH>, audit N = <N>, date = <DATE>, auditor = "<auditor>".
4. Use the dimension prefix the schema declares (DATA/ARCH/SECU/RELI/PERF/USER/TEST/DEPS/DOCS). Within your run, number sequentially per dimension starting from `01`. The aggregator will renumber on collision (see §Aggregation).
5. Operator seed (optional, may be empty): <SEED>. Weight alongside the schema's checklist; never override the methodology.
6. Use capability-tier model; prefer thoroughness over speed.

Return format:
- A markdown section per dimension in your scope, each containing findings in the schema's finding-record format.
- A phase summary block at the end:
    - Counts by severity (P0/P1/P2/P3)
    - Phase-local schema observations (empty bullet list is acceptable)

Rules:
- Do NOT write any files.
- Do NOT update TODO.md, CHANGELOG.md, or LEDGER.md — main agent's job.
- Do NOT attempt to merge with other phases' output — that is the main agent's job.
- Every finding has file:line evidence and a concrete, implementable recommendation.
- **Surface P0 findings IMMEDIATELY in your return** (don't bury). Main agent halts on receipt and asks the operator how to proceed.
```

## Aggregation on return

Main agent reconciles the four phase outputs into one report:

1. **ID-collision renumber.** Two phases can both emit `DATA-01` (or any `<PREFIX>-NN`) for unrelated findings. Detect collisions and renumber per dimension by phase order (Foundation → Runtime → Surface → Supplementary). Preserve original phase IDs in each finding's Notes for traceability (e.g. "Originally Foundation-DATA-01").
2. **Cross-phase deduplication.** If two phases independently flag the same root issue (overlapping `file:line` AND overlapping Impact wording), merge into a single finding. Keep the more concrete Recommendation; cross-reference both original phase IDs in the merged Cross-references field. A merge counts as one finding in the severity tally, not two.
3. **Severity reconciliation.** When two phases assigned different severities to the same merged finding, take the **higher** severity and document the reconciliation in the merged finding's Notes (e.g. "Reconciled P1 from SECU vs P2 from RELI; took higher per schema.").
4. **Concatenate** per-dimension finding sections in the schema's priority order (DATA → ARCH → SECU → RELI → PERF → USER → TEST → DEPS → DOCS).
5. **Sum severity counts** (post-dedup, post-reconciliation).
6. **Produce a unified executive summary** that surfaces top 3-5 findings + risk posture in one paragraph.
7. **Merge cross-dimension action plan**, ordered per schema (severity, then severity × effort within tier).
8. **Combine schema observations** from all four phases into the report's Schema observations section. Deduplicate verbatim repeats; preserve distinct angles.

**P0 surfacing during full-scope.** If any sub-agent returns a P0, halt aggregation and surface immediately to the operator. Operator chooses one of three paths:
- **fix-then-resume** — preserve audit N at current SHA after fix lands. Resume freshness check applies (SHA + schema hash).
- **fix-then-restart** — discard partial outputs; start audit N+1 against the post-fix SHA. Cleaner history when the fix is large.
- **proceed-with-P0-flagged** — continue current audit; P0 prominent in Executive summary + Action plan top item.

**Failure handling.** If a sub-agent fails or returns malformed output, re-dispatch only that phase. Do not restart the whole audit.

## Resume (--resume flag)

The skill can continue an incomplete audit without re-running completed phases.

**Detection.** Find the most recent `audits/AUDIT_<M>_REPORT.md`. Inspect its sections against the schema's §Report format. Missing sections → resume candidate.

**Freshness check.** Read recorded commit SHA AND schema hash from the partial report's Metadata. Compare against current state:
- `git rev-parse HEAD` must match recorded SHA
- `git hash-object plans/AUDIT_SCHEMA.md` must match recorded schema hash

If either differs, **do not resume** — warn the user with a short diff summary (which commits moved; whether the schema changed) and offer to restart as audit `M+1` against current state. Cross-commit OR cross-schema findings are incoherent.

**Resume execution.** If both match: keep audit number `M`. Identify the first missing dimension section and continue from there using the same mode (full or scoped, per the partial report's scope). For full-scope resume, re-dispatch only sub-agents for phase groups whose dimensions are missing. Aggregate the resumed findings into the existing report; do not rewrite completed sections.

## Tracker mode (`--tracker`)

Walk the latest tracker for status updates without producing a new audit. Keeps tracker fresh between audit runs.

1. Read latest `audits/AUDIT_*_FIXES.md`.
2. List `open` items (or all items if operator passes `--all` after `--tracker`).
3. For each, prompt operator: keep status / mark in-progress (with branch ref) / mark shipped (with commit SHA) / defer (with rationale) / wont-fix (with rationale).
4. Update tracker in place.
5. If any item moves to `shipped`, prompt operator to verify a corresponding `CHANGELOG.md` entry exists for that fix.
6. Commit changes as `docs(audit): tracker update — AUDIT_<M>` and push.

## Operator seed

Per-run free-text the operator supplies to shift the audit's focus. **Doesn't replace** the schema's per-dimension checklist — adds *extra* scrutiny on top.

### Source precedence

1. **Invocation prompt** (primary) — everything after the scope token in the `/audit` invocation. Natural-language asks ("audit the codebase, especially the cron-driven recurring expense generation") work too: when the main agent invokes `/audit` from a natural-language ask, the relevant free-text from the user's message is passed as the seed.
2. **`.claude/audit-seed.md`** (persistent fallback) — file the operator can populate for seeds that should apply across multiple audit runs without re-typing each time. Read only when the invocation has no free-text seed.
3. **Empty** (default) — audit runs against the schema's checklist with no extra focus shifters. Recorded in metadata as `(none)` for explicit absence.

### Why a fallback file exists at all

Use it for persistent priorities — e.g., "always extra-scrutinize CSP header until SECU-04 from AUDIT_3 ships." Once the priority is addressed, delete the file. Avoids re-typing the same focus shifter every audit. For one-off focus, use the invocation prompt — it's read once and recorded in the audit's metadata.

### Format (file, when used)

Plain bullet list:

```
- Standing priority: verify <X> per AUDIT_<N>:<DIM>-<NN>
- Standing priority: spot-check <Y>
```

### How sub-agents see it

Whatever source resolves to the seed (prompt / file / empty), it's substituted into each sub-agent's prompt verbatim under "Operator seed". Sub-agents weight it alongside the schema's checklist; they never override the methodology with it.

### Resume semantics

`--resume` reads the seed from the partial report's metadata, NOT from the resume invocation's prompt. Preserves operator intent across re-runs at the same SHA. To change the seed mid-audit, restart against the new SHA (audit `M+1`) instead of resuming.

## Invariants

- **Schema content stays in `plans/AUDIT_SCHEMA.md`.** This skill never duplicates it. Schema changes propagate automatically to the next invocation.
- **Every finding has `file:line` evidence and a concrete, implementable recommendation.** Vague findings fail the bar.
- **Reports are immutable.** Never edit an existing `AUDIT_<N>_REPORT.md` after it is marked complete. Status changes go in the paired `_FIXES.md`.
- **Resume continues only at matching SHA AND matching schema hash.** Cross-commit or cross-schema findings are incoherent.
- **Sub-agents do not write files.** Aggregation is main agent's responsibility.
- **Sub-agents number freely from `01`.** Aggregator renumbers on collision; original phase IDs preserved in Notes.
- **Cross-phase merges take the higher severity** and document the reconciliation in the merged finding's Notes.
- **P0 halts aggregation immediately.** Sub-agents flag P0 prominently; main agent surfaces the operator decision tree (fix-then-resume / fix-then-restart / proceed-with-P0-flagged) before continuing.
- **Operator seed never overrides the methodology.** It adds extra scrutiny on top of the schema's checklist.
- **Resume reads the seed from the partial report's metadata**, not the resume invocation's prompt. To change the seed, restart against the new SHA.
- **Chunked writes.** Report sections are written in stages to respect the 200-line per-write rule.
- **Meta-review prompts are reminders only.** The skill never auto-invokes a meta-review.
- **Schema gaps found during a run go into the Schema observations section.** Do not silently improvise new dimensions, fields, or severity levels mid-run.
