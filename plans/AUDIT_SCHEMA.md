# Audit Schema for {project-name}

**Status**: Living spec — single source of truth for `/audit` runs.
**Created**: `[YYYY-MM-DD at project init]`
**Owner**: `{project}` audit discipline.
**Related**: `.claude/skills/ship/audit/SKILL.md` (the skill that consumes this) · `LEDGER.md` (institutional memory; audits both consult and update it) · `CHANGELOG.md` (audit runs log here) · `docs/TODO.md` (P0/P1 findings land here).

---

## Sections

1. Context — why this exists, what it is and isn't
2. Priority framework — depth-of-effort allocation per dimension
3. Dimensions — DATA / ARCH / SECU / RELI / PERF / USER (+ supplementary TEST / DEPS / DOCS)
4. Phase groups — composition and parallelization rationale
5. Severity taxonomy — P0 / P1 / P2 / P3
6. Methodology — pipeline every audit follows
7. Report format — `audits/AUDIT_N_REPORT.md` structure (incl. finding-record format)
8. Tracker format — `audits/AUDIT_N_FIXES.md` structure
9. Cadence and triggers — when full vs scoped audits run
10. Artifacts produced — what every run emits
11. Verification — how to know the audit was done well
12. Audit failure modes — categories of bad audit, watch for during run + meta-review
13. Schema maintenance — meta-review cadence + checklist

---

## Context

`[Populated by /grill-with-docs at project init.]`

`Describe: what kind of project this is, the domain, money-adjacent surfaces (if any), compliance constraints (if any), multi-tenant or single-tenant, the user-facing risk surface (data corruption, security breach, legal non-compliance, performance degradation). The framing here justifies the dimension priority order in §2.`

`Example shape (paraphrase, don't copy verbatim): "{project} is a {type} for {users}. Every feature revolves around {load-bearing concern, e.g. money / health data / compliance}. {Specific compliance regime} is encoded directly into {data model | business logic | UI}. Multi-tenant scoping {applies | does not apply}." That combination justifies {data integrity | security | reliability} as cornerstone.`

This schema formalizes how a periodic audit of this codebase is scoped, ordered, executed, and reported. It is the template a `/audit` skill or a manual audit pass would follow. Applying it produces a `audits/AUDIT_N_REPORT.md` + paired `audits/AUDIT_N_FIXES.md` without format drift from run to run.

## Priority framework

Depth of audit effort is allocated in this descending order. All dimensions are covered — this only governs resource allocation when trade-offs are required.

| Rank | Dimension | Rationale |
|--:|---|---|
| 1 | **Data Integrity** | Money-adjacent records or load-bearing data; any invariants whose violation causes silent corruption |
| 2 | **Architecture** | Determines whether the other dimensions stay correct as the code evolves — upstream of everything else |
| 3 | **Security** | Direct harm surface (auth, authz, PII, financial exposure) |
| 4 | **Reliability** | Degradation tolerance, retry correctness, cron idempotency |
| 5 | **Performance** | Material for user experience but rarely existential |
| — | **UX / Accessibility** | Foundational for any app that is actually used, but builds on the five above; audited systematically, prioritized against the others only when conflicts arise |

Cross-cutting supplementary dimensions (testing coverage, dependency hygiene, documentation fidelity) are always covered; they inform depth rather than compete for rank.

`[The default order above suits most webapps. /grill-with-docs may justify reordering for project-specific reasons (e.g. a security-research app may rank Security #1; a real-time app may rank Performance higher). Document the rationale for any deviation.]`

## Dimension 1 — Data Integrity (cornerstone)

The question this dimension answers: `[Populated by /grill-with-docs. Example shape: "can {money | memberships | legally-binding records | core domain entity} be silently corrupted, lost, duplicated, or mutated outside an auditable path?"]`

### Audit checklist

`[Empty at init. Populated during /grill-with-docs project-principles interview AND grown incrementally: every audit run that surfaces a recurring hazard adds a checklist item. Standard categories to seed during /grill-with-docs:`
- *Schema-level invariants* — money-fields-as-Decimal-or-equivalent, FK on-delete behavior, unique constraints, NOT NULL where mandatory, indexes on hot paths
- *Transactional correctness* — multi-entity writes inside transactions, failure paths leave no partial state
- *Audit trail completeness* — actor + timestamp on mutations, soft-delete vs hard-delete discipline, ledger reflects every mutation, immutability of approved/finalized records
- *Cascade correctness* — parent-deletion cascades correctly, soft-delete cascades to linked children
- *Decimal precision and rounding drift* — boundary serialization, sum reconciliation tolerance documented
- *Domain / spec invariants* — project-specific business rules encoded in the data model
- *Migration safety* — reversible or documented-irreversible, no schema+data migrations in same commit, prod-deploy ordering
- *Temporal correctness* — period strings, timezone discipline, soft-delete filter consistency

`Fill these with project-specific items, not generic boilerplate. Each item should be testable: "audit confirms X" or "every Y has Z."]`

### Key artifacts to inspect

`[Populated by /grill-with-docs based on project file structure. Examples: schema files, migration directories, calculation modules, soft-delete extension, serializers, action files that mutate domain records, cron entry points.]`

### Project-specific hazards (incident-shape catalog)

`[Empty at init. Populated as audits surface hazards; each entry pairs with a CHANGELOG fix and ideally a /ledger-capture lesson. Format per hazard:`

`**<Hazard name> (AUDIT_<N> P<X> #<finding-id>; resolved by <commit/PR>)** — <2-3 sentences describing the failure shape, why it's recurring, and what the audit checks for now>.`

`These accumulate institutional memory; new audits look here first to avoid re-discovering known shapes.]`

---

## Dimension 2 — Architecture

The question this dimension answers: `[Populated by /grill-with-docs. Example shape: "are patterns applied consistently enough that adding a new feature keeps the other dimensions correct by construction?"]`

### Audit checklist

`[Empty at init. Standard categories to seed during /grill-with-docs:`
- *Layering adherence* — feature-module shape (validator → calculation → action → page → client), no business logic where it doesn't belong
- *Auth context propagation* — every mutation goes through standard auth wrapper; no manual auth lookups
- *Cache / revalidation scoping* — invalidations scoped correctly; no cross-tenant or cross-feature leak
- *Serialization boundary* — no server-only types in client bundle
- *Shared-component discipline* — canonical primitives (modals, forms, file upload, etc.) used uniformly
- *i18n discipline* (if applicable) — strings centralized; no hardcoded UI text outside the canonical store
- *Naming and convention consistency* — domain-language file/folder/identifier naming
- *Dead code and duplication* — no unused exports; no two components doing the same job

`Fill with project-specific items.]`

### Key artifacts to inspect

`[Populated by /grill-with-docs. Examples: src/app/, src/lib/, src/components/, framework-specific routing or middleware files.]`

### Project-specific hazards (incident-shape catalog)

`[Empty at init. Populated incrementally.]`

---

## Dimension 3 — Security

The question this dimension answers: `[Populated by /grill-with-docs. Example shape: "can an unauthorized party read, mutate, or exfiltrate another user's / tenant's data — or bypass the authorization layer?"]`

### Audit checklist

`[Empty at init. Standard categories to seed:`
- *Authentication flows* — login/registration/reset/verify all handle unhappy paths; password hashing strength; session token discipline
- *Authorization per endpoint* — every action wrapped in auth HOF; every API route validates session + membership + role; sensitive downloads ownership-gated
- *Multi-tenant isolation* (if applicable) — tenant resolution single-entry; no client-supplied tenant IDs; cross-tenant probes
- *Input validation* — every action and API route Zod-or-equivalent before DB; bounds on string fields; URL validation
- *Secrets and configuration* — no secrets in source/lock/logs; env-var asserted at boot
- *Rate limiting* — auth, expensive endpoints, file uploads, cron
- *File upload safety* — MIME-type allowlist, size enforcement, filename sanitization, scoped storage paths
- *SQL injection and raw queries* — every raw query parameterized
- *Error and log hygiene* — generic error responses; no PII or tokens in logs
- *Dependency vulnerabilities* — `pnpm audit` / `pip audit` / equivalent clean; CVEs triaged

`Fill with project-specific items.]`

### Key artifacts to inspect

`[Populated by /grill-with-docs. Examples: auth modules, middleware, API routes, rate-limit modules, validators, package.json + lock files.]`

### Project-specific hazards (incident-shape catalog)

`[Empty at init. Populated incrementally.]`

---

## Dimension 4 — Reliability

The question this dimension answers: `[Populated by /grill-with-docs. Example shape: "when something upstream fails (email provider, DB connection, blob storage, cron), does the app fail open, fail closed, or corrupt?"]`

### Audit checklist

`[Empty at init. Standard categories to seed:`
- *Action-level error handling* — actions return structured errors, not bubbled exceptions; try/catch where recoverable
- *Fire-and-forget correctness* — fire-and-forget operations are deliberate and logged; retries bounded
- *Cron idempotency* — same input → same terminal state; mid-run failures don't corrupt
- *Database connection handling* — pool size appropriate; long queries timed out
- *Graceful degradation* — non-critical service failures don't block user actions
- *Transaction rollback* — throw-inside-transaction handled; no state outside transaction that would diverge
- *Edge cases* — empty entities, single entities, zero-amount, time-boundary
- *Observability* — unhandled exceptions reach logs; critical paths emit context

`Fill with project-specific items.]`

### Key artifacts to inspect

`[Populated by /grill-with-docs. Examples: every actions.ts, cron route, email queue, db client setup.]`

### Project-specific hazards (incident-shape catalog)

`[Empty at init. Populated incrementally.]`

---

## Dimension 5 — Performance

The question this dimension answers: `[Populated by /grill-with-docs. Example shape: "are any common user paths expensive enough to degrade at realistic scale ({estimated upper-bound load})?"]`

### Audit checklist

`[Empty at init. Standard categories to seed:`
- *Query patterns* — no N+1 loops; bounded `take`; targeted `select`
- *Index coverage* — hot-path queries have matching indexes; no redundant indexes
- *Page render cost* — server pages parallelize independent reads; no waterfall
- *Caching and revalidation* — cache used only with consistent invalidation; targeted revalidation
- *Client bundle* — lazy-loaded UI; server-only packages excluded from client
- *Hot paths* — login/dashboard/list-view under budgeted TTFB at realistic scale
- *Known deferrals* — items deliberately not optimized, with upgrade path noted

`Fill with project-specific items.]`

### Key artifacts to inspect

`[Populated by /grill-with-docs. Examples: every page.tsx, list-fetch action, schema indexes, build config.]`

### Project-specific hazards (incident-shape catalog)

`[Empty at init. Populated incrementally.]`

---

## Dimension 6 — UX / Accessibility (superstructure)

UX sits on top of the five foundational dimensions. Audited systematically, never ranked against them when resources are scarce.

### Audit checklist

`[Empty at init. Standard categories to seed:`
- *Form discipline* — typed-resolver on every form; label-input pairing; consistent error styling; submit-state reflection
- *Modals and dialogs* — shared modal primitive used; aria-modal/role/focus-trap/escape-closes/focus-returns
- *Loading and empty states* — skeleton fallback per server-rendered list; clear empty CTAs; retryable vs permanent error distinction
- *Optimistic UI consistency* — useOptimistic + useTransition uniform; rollback visible
- *Mobile and responsiveness* — bottom nav works; tables degrade; modals reach close controls
- *Locale completeness* — no language fragments leaking; date/currency formatted per locale
- *Accessibility basics* — tab order, color-not-only-signal, contrast WCAG AA, keyboard reach
- *Consistency* — button variants, copy style, icon usage uniform

`Fill with project-specific items.]`

### Key artifacts to inspect

`[Populated by /grill-with-docs. Examples: src/components/ui/, layout components, feature forms/lists, global CSS, locale message files.]`

### Project-specific hazards (incident-shape catalog)

`[Empty at init. Populated incrementally.]`

---

## Supplementary dimensions

Covered in every audit, but scoped tighter than the six above.

### Testing coverage

`[Empty at init.]`

- Every validator has a co-located test file exercising schema + enum edge cases
- Every pure calculation has a test file with meaningful scenarios (not just the happy path)
- Scenario tests exercise end-to-end flows across module boundaries
- Test count growth tracked per audit; a shrinking count (excluding deletions) is a signal
- No vacuous tests (`expect(true).toBe(true)` or tests that pass regardless of the code)

### Dependency hygiene

`[Empty at init.]`

- `pnpm outdated` / equivalent reviewed; majors not upgraded without a reason, but no neglect > 6 months
- `pnpm audit` / equivalent clean; each CVE triaged
- No duplicate versions of the same package at different majors in the lockfile
- Unused deps detected and removed

### Documentation fidelity

**Source-of-truth docs** (universal — these conventions apply to any project using the wiki/templates/AGENTS.md shape):

- `docs/ARCHITECTURE.md` matches actual code; spot-check 5 random claims against `src/`
- `docs/STATUS.md` reflects real module completeness and current session handoff; **`## Current release` line matches `package.json` `"version"` (or stack equivalent)**
- `docs/TODO.md` has no items already shipped per `CHANGELOG.md`; no items active that have shipped
- `docs/IDEAS.md` — items matured into TODO are struck through; obviously dead ideas pruned
- `CHANGELOG.md` — most recent `## [X.Y.Z]` version header matches `package.json` version; every version header has an ISO date; `## [Unreleased]` exists
- `CLAUDE.md` / `AGENTS.md` has no stale pointers; auto-imports point at existing files
- Plans (`plans/*.md`) — completed plans marked complete; living references match current procedure

**LEDGER.md fidelity** (universal — these checks apply regardless of project content):

- Lessons match captured incidents (verifiable against `CHANGELOG.md` + git log)
- Open threads / investigations truly open (resolved entries removed)
- Captured rationales / decisions still load-bearing
- Key invariants still true (verifiable against code)
- File size manageable (auto-loaded into prompt; sustained growth churns prompt cache)
- No two entries say contradictory things

**Skill files**:

- `.claude/skills/<name>/SKILL.md` per directory format (single-file `.claude/skills/<name>.md` will not load on Claude Code)
- Frontmatter (`name`, `description`) accurate
- Skill body matches what the skill actually does (no aspirational behavior)

---

## Phase groups

Dimensions cluster into four phase groups by artifact locality and concern locality. Each group shares the same primary source artifacts. Groups are independent enough to run in parallel.

| Group | Dimensions | Primary artifacts |
|---|---|---|
| **A — Foundation** | Data Integrity + Architecture + Security | Schema, auth, validators, action files, page files |
| **B — Runtime** | Reliability + Performance | Cron entry points, queue infra, server-action error paths, query patterns, transaction boundaries, rate limiters, indexes |
| **C — Surface** | UX + Accessibility | Component libraries, feature forms/lists/page-clients, modals, locale messages, navigation shells |
| **D — Supplementary** | Testing + Dependencies + Documentation | Test directories, coverage output, package audits, docs/, LEDGER.md, CHANGELOG.md |

Phase groups are first-class scoping units for audits: the `/audit` skill accepts a group name as its scope argument, and the full-scope mode dispatches a sub-agent per group.

**Differential cadence is encouraged.** Suggested default: Foundation bi-weekly, Runtime monthly, Surface every 2–3 months, Supplementary quarterly, plus a full-scope audit quarterly or pre-release. Adjust per project reality.

---

## Severity taxonomy

Severity is assigned per finding. Every audit declares these definitions upfront so readers calibrate consistently.

| Level | Criteria |
|---|---|
| **P0 — Critical** | Active data corruption, security breach vector, legal non-compliance, production outage. Must be fixed before next release. **Surface immediately mid-flight** — auditor stops the run if found rather than completing silently. Operator chooses one of three paths: **fix-then-resume**, **fix-then-restart**, **proceed-with-P0-flagged**. |
| **P1 — High** | User-visible incorrect behavior; real data-integrity risk under a plausible edge case; serious perf degradation at current scale; unmitigated security exposure requiring specific-but-plausible conditions. |
| **P2 — Medium** | Correctness bug with a workaround; architectural drift that will compound; moderate perf issue not yet user-visible; security hardening opportunity. |
| **P3 — Low** | Polish, cosmetic, minor duplication, doc nits. |

Severity is orthogonal to effort. A P3 may take an afternoon; a P0 may take ten minutes. The action plan orders by severity first, then by severity × effort within each tier.

## Methodology

Each audit run follows the same pipeline.

**Scope declaration.** Capture before starting:
- Commit SHA being audited (`git rev-parse HEAD`)
- Schema hash (`git hash-object plans/AUDIT_SCHEMA.md`) — pinned for resume coherence
- Branches in play
- Audit scope (full / group / dimension; with names)
- **Operator seed** — free-text focus shifters supplied via the invocation prompt or `.claude/audit-seed.md` fallback. Recorded so `--resume` preserves the original intent. Empty seed is recorded as `(none)` for explicit absence.
- What's deliberately out of scope
- Auditor identity

**Tool-assisted passes.** Run (and capture outputs of):
- `[stack-specific composite verify command, e.g. pnpm verify]` — baseline state check (lint + test + build)
- `[stack-specific dep-vulnerability scanner, e.g. pnpm audit]`
- `[stack-specific dep-freshness check, e.g. pnpm outdated]`
- `[stack-specific schema validator, e.g. prisma validate]` if applicable
- **Test-count delta** — current count compared against `docs/STATUS.md`'s recorded count from the prior audit. Shrinking count excluding deletions is a signal.
- Coverage snapshot if available

**Anti-pattern grep sweep** — universal templates (each project adapts to its stack):
- Raw SQL — every hit must be parameterized
- Bare wildcard cache invalidation — must be scoped
- Unbounded list queries — must declare bounds
- Server actions without auth wrapper — every mutation must go through standard HOF
- Server-only types in client bundle
- Direct ID lookup without tenant scope (multi-tenant apps) — every lookup verifies tenant

`[Add project-specific anti-pattern greps as they're discovered.]`

**Manual passes.** For each dimension in scope, walk the checklist item by item. Every checklist item produces either a finding or an explicit "no findings — verified by …" note. Absence is signal.

**Evidence collection.** Every finding includes:
- A `file:line` pointer (or `module/` when diffuse)
- A minimal code snippet or query result quoted in-line
- A concrete impact (not "could be a problem" — *why* it matters for this app)

**Severity calibration.** Assign severity on draft; calibrate against other findings of the same level before finalizing.

**Effort estimate.** Per finding: rough wall-time to fix (`< 30min`, `1–2h`, `4–8h`, `> 1d`).

**Delta against prior audit.** Compare finding IDs against the previous `AUDIT_M_FIXES.md` for the same scope. Carry forward open items; acknowledge closed; note regressions; note deferred. **Comparison target:** most recent prior audit covering at least the same scope.

**Schema observations capture.** During the run, log every place the schema didn't fit cleanly. These accumulate into the report's Schema observations section and feed the periodic meta-review.

## Report format

### `audits/AUDIT_N_REPORT.md` (immutable)

1. **Metadata.** Auditor, date, commit SHA, schema hash, branches, scope, methodology summary. For scoped audits: explicit "out of scope" stub per uncovered dimension.
2. **Executive summary.** Counts by severity (P0/P1/P2/P3), headline findings, overall risk posture in one paragraph. Readable by someone who won't read the rest.
3. **Severity taxonomy.** The definitions above, reproduced so the report is self-contained.
4. **Findings by dimension.** In the priority order: Data Integrity, Architecture, Security, Reliability, Performance, UX, then supplementary. Each dimension **in the declared scope** gets a section. Empty sections appear with an explicit "no findings" note. For scoped audits, dimensions out of scope get a short stub: `> Out of scope for this audit. Last covered in audits/AUDIT_<M>_REPORT.md.`
5. **Prioritized action plan.** Cross-dimension ordered list, by severity then severity × effort within each tier, with each item linking back to its finding ID. Includes a "Defer rationale" column.
6. **Metrics appendix.** Objective numbers: test count, coverage %, LOC, dependency counts, top-N slowest queries if measured, bundle size if measured.
7. **Delta from prior audit.** What shipped, what regressed, what was deferred. **Comparison target:** the most recent prior audit that covered at least the same scope.
8. **Schema observations.** Meta-commentary on the schema itself, captured during the audit. Empty (with explicit "no observations — the schema held up" note) if nothing misfit.

### Finding record (inside the report)

```
### {ID} — {Title}

- **Severity:** {P0 | P1 | P2 | P3}
- **Effort:** {< 30min | 1–2h | 4–8h | > 1d}
- **Location:** `file/path.ts:NN` (or `module/` if diffuse)
- **Evidence:**
    ```
    // the minimal snippet that shows the issue
    ```
- **Impact:** {concrete consequence; what goes wrong if left}
- **Recommendation:** {specific, implementable action}
- **Reference:** (optional — CVE, CWE, doc link)
```

IDs use dimension prefixes: `DATA-NN`, `ARCH-NN`, `SECU-NN`, `RELI-NN`, `PERF-NN`, `USER-NN`, `TEST-NN`, `DEPS-NN`, `DOCS-NN`. All four letters for uniform width. Numbers start from `01` per audit; tracker disambiguates by audit number prefix (`AUDIT_5:DATA-03`).

## Tracker format

### `audits/AUDIT_N_FIXES.md` (mutable)

Created at the same time as the report. Status updated as items move; the report itself never changes.

| ID | Title | Severity | Status | Owner | Notes |
|---|---|---|---|---|---|
| DATA-01 | … | P1 | open | — | |
| SECU-02 | … | P1 | in progress | claude/… | PR #… |
| ARCH-03 | … | P2 | shipped | — | YYYY-MM-DD, commit abc… |

**Status vocabulary:** `open`, `in progress`, `shipped`, `deferred`, `wont fix`.

When a tracker item ships, it moves from the tracker to the matching `CHANGELOG.md` entry. Deferred and wont-fix stay until the next audit reconsiders.

**PR-title convention.** Audit-fix commits include the audit-qualified ID:

```
fix(scope): description [AUDIT_4:SECU-03]
```

This lets `git log --grep='AUDIT_4:'` enumerate every fix tied to an audit.

## Cadence and triggers

Audits are **periodic snapshots**, not per-change gates. Two run modes:

**Scheduled audit** — quarterly, or before a major release. Full pass.

**Scoped audit** — after a large architectural change. Affected dimensions only.

**Not a substitute for:**
- Per-PR review (`/review`)
- Per-PR security gate (`/security-review`)
- The push-time verify gate

## Artifacts produced

Every audit run produces exactly two files in `audits/`:

- `audits/AUDIT_N_REPORT.md` — immutable diagnostic
- `audits/AUDIT_N_FIXES.md` — mutable tracker

Naming: `N` is the next integer after the highest existing `AUDIT_*_REPORT.md`. **Single counter across scopes** — full, group, and dimension audits all share the same N sequence; scope is declared in Metadata.

Side-effect updates per run:
- `docs/TODO.md` — new P0/P1 items added
- `CHANGELOG.md` — single entry summarizing the run

## Verification — how to tell the schema was followed

**Structural:**
- Every dimension in scope has a section, with findings or explicit "no findings" note
- Every finding has every required field
- Severity distribution is plausible (not 100% P3 — under-reading; not 100% P0 — inflation)
- Every P0 and P1 has concrete `file:line` and an under-a-day fix
- Paired tracker exists with same IDs
- Commit SHA in metadata resolves to a real commit
- Schema hash matches at audit start

**Functional:**
- Re-running the audit by a different reviewer produces substantially overlapping findings: **>70% overlap on P0/P1, >50% on P2/P3**
- Executive summary enables a reader to act without reading the full report
- Action plan ordering would survive debate
- Schema observations either explain why nothing misfit OR capture specific gaps with evidence

## Audit failure modes

Categories of bad audit, watch for during run AND meta-review.

- **Severity inflation** — Every finding is P0/P1. Cross-check: if no P2/P3 exist, the auditor is over-reading.
- **Severity deflation** — No P0s found. Cross-check: do the dimensions with incident-class hazards get scrutinized?
- **Dimension blind spot** — A whole dimension produces 0 findings repeatedly. Either it doesn't apply (consider retiring) or methodology fails to surface its issues.
- **Finding fatigue** — Hundreds of P2/P3 polish items burying the P0s. Raise the floor (split polish into a backlog doc) or split the audit.
- **Vague evidence** — Findings without `file:line` or with handwaves. Sharpen or drop.
- **Implementation tests, not contract tests** — TEST findings flagging tests that don't test private implementation. Tests should verify contracts.
- **Doc-state-as-truth** — Audit relies on what docs claim rather than what code does. Documentation drift is a finding (DOCS); never source of truth elsewhere.
- **Cross-audit ID reuse** — Two audits both use `DATA-03`. Audit-qualified form `AUDIT_<N>:DATA-03` should disambiguate.
- **Stale comparison target** — Delta computed against an audit covering different scope. Verify in metadata.

When a failure mode surfaces during a run, the auditor stops and addresses it before publishing.

## Schema maintenance

The schema evolves via a feedback loop built into every audit. Each audit's §"Schema observations" section captures places the schema didn't fit. Those observations accumulate and periodically roll up into schema revisions.

### When to run a schema meta-review

- **Every 5 audits**, whichever first.
- **Or immediately**, when a single audit surfaces a schema gap severe enough to compromise the current run.
- **Or on demand** before changing the audit cadence, onboarding a new auditor, or making a major product pivot.

### Steps for a schema meta-review

1. **Collect.** Read §"Schema observations" from every `audits/AUDIT_*_REPORT.md` since the last meta-review.
2. **Apply the meta-checklist** (below) to the schema as it currently stands.
3. **Draft amendments.** Concrete proposed edits to this file, each keyed to specific evidence. No amendment without evidence.
4. **Review severity.** Amendments that re-label prior findings must be explicit about retroactive effect.
5. **Commit.** A single `docs: AUDIT_SCHEMA.md meta-review N` commit with a CHANGELOG entry.

### Meta-checklist — questions to ask of the schema itself

**Dimension fit.**
- Did findings fail to map cleanly to a dimension? Recurring misfits signal a missing dimension.
- Did findings cluster heavily? Subdivide for clearer prioritization?
- Is any dimension consistently empty? Consider retiring.

**Severity calibration.**
- Did findings feel between two tiers? Recurring "P1-or-P2" signals taxonomy gap.
- Is one tier overused? Definitions too permissive.
- Is any tier consistently empty? Definition mismatched to real findings.
- Do P0 findings consistently map to incidents in CHANGELOG?

**Finding-record utility.**
- Are all fields filled consistently? Fields blank >50% of the time are removal candidates.
- Is any field repeatedly supplemented ad-hoc? Formalize.
- Are IDs and prefixes used as designed?

**Methodology completeness.**
- Did stated tool-assisted and manual steps catch the findings?
- Are tool commands still current?
- Has any step become redundant?

**Report structure value.**
- Is executive summary read and acted on?
- Is metrics appendix producing signal or filler?
- Is any section a reliable dead zone?

**Tracker format utility.**
- Is status taxonomy sufficient?
- Is the `owner` column adding value?
- Are shipped items graduating to CHANGELOG?

**Cadence alignment.**
- Is declared cadence honored in practice?
- Are scoped audits being used when appropriate?

**Priority framework validity.**
- After seeing real findings, does the declared priority order still hold?
- Has the product changed in a way that should shift priorities?

### Amendment boundaries

- **Freely amendable:** dimension lists, sub-areas, methodology tools, finding-record fields, report sub-sections, cadence, tracker fields.
- **Amend with care:** severity taxonomy definitions (retroactive effect), priority framework order (user-owned product decision).
- **Out of scope:** individual findings from prior audit reports. Reports are immutable.
- **Out of scope for the skill itself:** the `/audit` skill is a thin wrapper. Fix the schema, not the skill.
