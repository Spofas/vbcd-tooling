# {project-name} — Agent Development Guide

**Universal AGENTS.md substrate.** Canonical project guide loaded by both Codex (eager-loaded) and Claude Code (via `CLAUDE.md` shim that imports `@AGENTS.md`). Agent-agnostic: nothing in this file is Claude-specific or Codex-specific.

`{one-line project description}` — replace with what this project is, in 12-25 words.

---

## Session start

On session start, read `@LEDGER.md` and `@docs/STATUS.md` for current project context. (On Claude Code, the `@`-syntax above auto-loads these into context. On Codex, read them with your file tool — Codex doesn't expand `@`-imports the same way.) On first action, also skim `CHANGELOG.md` top three entries for the most recent changes.

**Dual-vendor operation**: if this project is run with both Claude Code AND Codex, see the wiki's [[../sources/nateherk-cc-projects-in-codex|Nate Herk *CC Projects in Codex in 5 Mins*]] for the canonical recipe — file-structure cheat sheet + 3-layer mental model (shared knowledge / workflows-skills / tool-specific config) + critical detail that Codex sub-agents don't auto-invoke (CC ones do). Pack ships dual-vendor by design: `CLAUDE.md` + `AGENTS.md` as full duplicates; `.claude/skills/` + `.agents/skills/` as parallel trees. Use `/sync-vendor-files` skill to mirror edits.

## Reference map

| When you need … | Read |
|---|---|
| How the system is built | `docs/ARCHITECTURE.md` |
| Current build state and handoff notes | `docs/STATUS.md` |
| Outstanding work | `docs/TODO.md` |
| Forward-looking ideas (uncommitted) | `docs/IDEAS.md` |
| Product vision and features | `docs/PRODUCT.md` |
| Deployment runbook | `docs/deploy-runbook.md` |
| Manual QA checklist | `docs/MANUAL_TESTS.md` |
| Longer feature / work plans | `plans/` |
| Historical audits and fix trackers | `audits/` |
| Session oddities and notes-to-future-self | `LEDGER.md` |
| Full change history | `CHANGELOG.md` |
| Custom skills | `.claude/skills/` (and/or `.agents/skills/` for Codex) |

Files don't have to exist day-1; the convention is what makes the agent know where to look. Create each file when needs surface.

## Behavioral Guidelines

Behavioral guidelines to reduce common LLM coding mistakes. Tradeoff: these bias toward caution over speed. For trivial tasks, use judgment.

### §1. Goal-Driven Execution

**Define success criteria. Loop until verified.**

> Per Anthropic's published Claude Code best-practices, verification criteria (tests, screenshots, expected outputs) are *"the single highest-leverage thing you can do"* — Anthropic's #1 named practice. Make every task verifiable; defer everything else. This is §1 by design.

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan with per-step verification:

```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

### §2. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### §3. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Senior-engineer test: "Would they say this is overcomplicated?" If yes, simplify.

### §4. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: every changed line should trace directly to the user's request.

### §5. Output Mechanics

Large or compositionally-complex outputs time out. Three sub-rules:

**5a. Chunked file operations.** Writing or rewriting files over 200 lines: do it in stages of ~200 lines each. A 400-line file = 2 stages; a 1000-line file = 5 stages. Confirm each stage saved before continuing. Reading large files: use offset + limit to read in sections.

**5b. Scaffold before filling.** When creating a new multi-section document (plan, spec, audit report, test suite, migration script) likely to exceed 200 lines:
1. State the section list — titles + one-line purpose each.
2. Create the file via a minimal stub Write: header, status block, empty section headers (≤50 lines).
3. Fill each section with an Edit call, one section per Edit, confirming save between.
4. If any single section exceeds ~200 lines on drafting, decompose it further.

Front-loads decomposition. Surfaces document shape early, giving the user a redirect opportunity before effort is spent.

**5c. Decompose by semantic unit.** Line count isn't the only bottleneck — compositional complexity is. Generating large volumes of novel, interdependent content (seed data, test suites, configs) in a single response can time out even when the file is under 200 lines. Decompose by natural boundaries: one portfolio, one test suite, one component per pass. Complete and verify each unit before continuing.

### §6. Build Shared Language

**Use terms from `CONTEXT.md`. Flag drift as a real bug.**

The first 5–10 domain terms emerge from running `/grill-with-docs` once; the file grows organically as new terms surface. When you use a term that conflicts with the existing language in `CONTEXT.md`, call it out. Variables, functions, and files name consistently with `CONTEXT.md` vocabulary.

Why it matters: a shared language means the codebase is easier to navigate, the agent spends fewer tokens on thinking (concise vocabulary), and naming stays consistent across features.

### §7. Protect Trunk, Vibe Leaves

**Vibe-code freely on isolated features; human-review the core.**

Tech debt in *leaves* (UI components, throwaway prototypes, non-load-bearing flows) is contained — when it goes wrong, the blast radius is small. Tech debt in *trunk* (auth, payments, data integrity, schema, multi-tenant scoping if applicable) compounds across every future feature.

Practically:
- Before approving a change, ask: *what's the blast radius if this is wrong?*
- For trunk changes, slow down: read carefully, run `/plan-review` if available, require tests.
- For leaf changes, accept the AI's judgment; verify by running.

### §8. Accumulate, Don't Restart

**Every operator correction is a candidate for the substrate.**

If you correct Claude (or Codex) once, the lesson lives in your head. If you write it down, every future run benefits. Where to write what:
- **Standing rules** (always do X, never do Y) → AGENTS.md gotchas section (loaded by both Claude Code and Codex).
- **Session-spanning lessons / invariants / open investigations** → `/ledger-capture` writes to `LEDGER.md`.
- **Project-domain decisions** → `/grill-with-docs` writes to `CONTEXT.md` + `docs/adr/`, plus pack-level closing prompts for MANUAL_TESTS / LEDGER prefs / AUDIT_SCHEMA dims at grill-end (per `/grill-with-docs` SKILL.md Pack calibration).
- **Recurring workflow** → after the third repeat, author it as a skill via `/skill-creator`.

**Two memory layers, different jobs.** As of May 2026, both vendors ship Claude-managed auto-memory alongside this pack's operator-curated `LEDGER.md`. They are complementary, not competing — use both for their respective purposes:

- **Auto-memory** (CC: `~/.claude/projects/<project>/memory/`; Codex: `Settings > Personalization > Memories` + per-thread `Chronicle`) — **Claude/Codex-managed**, lazy-loaded, fire-and-forget. The agent self-decides what's worth keeping (preferences, conventions, "don't suggest X again"). Operator doesn't curate. Used for **high-volume, low-stakes** lessons that don't need human review.
- **`LEDGER.md`** (this pack) — **operator-curated, git-tracked, team-shareable**. Used for: *named incidents with lessons*, *design rationales not in any plan doc*, *load-bearing invariants*, *open investigations*. Raise the bar: if a lesson doesn't need human review or team visibility, let auto-memory have it — don't double-bookkeep.

Practical heuristic when something captureable surfaces: *"Will I (or a teammate) want to see this in a git diff later?"* If yes → `/ledger-capture` to LEDGER.md. If no → let auto-memory absorb it.

**Proactive capture-surface rule.** When you encounter content during work that matches a LEDGER category — a generalization from an incident, a design rationale not in any plan doc, a non-obvious load-bearing invariant, an unanswered question worth tracking — surface a closing prompt: *"This looks captureable per LEDGER — invoke `/ledger-capture` now?"* Don't auto-capture; the operator decides. Surface sparingly — quality over quantity; not every casual observation is captureable. The rule applies during ambient coding work AND at the end of skills whose output predictably produces capture-worthy content (notably `/diagnose`, after a regression-test-plus-fix lands: surface *"This bug taught us [X]. Capture as a LEDGER lesson?"*). `/audit` Step 7, `/handoff` Step 4, and `/grill-with-docs`'s multi-artifact closing prompts already operationalize this at their own protocol ends.

### §9. Avoid Vendor Lockin

**When alternatives with equivalent outcomes exist, prefer portable solutions over vendor-specific ones.**

Every vendor-locked dependency makes future replacement more expensive. Cumulatively, lockin shrinks the project's optionality. When proposing a vendor-locked dep (managed service, vendor-specific API, proprietary integration), check first whether a portable alternative delivers the same outcome:

- *Vercel KV for session storage?* → Consider Upstash Redis or a Neon session table — same outcome, portable.
- *Vercel Edge Config for feature flags?* → Consider env vars + a flag-evaluation lib (GrowthBook OSS, simple bool checks) — same outcome, portable.
- *A vendor-locked auth provider (Clerk / Auth0)?* → Surface the alternative-vs-effort tradeoff; let operator weigh.

Surface the tradeoff explicitly when it applies; **operator decides**. Don't refuse the vendor-locked option — flag it.

**Core-stack carve-out.** Deliberate stack choices named in `Quick Reference` / `Git Conventions` (e.g., Vercel + Neon + Next.js + TypeScript for this project) are the lockin the project was built on. Rule does **not** fire on those — they are the workflow's load-bearing substrate. Rule fires on *peripheral* dependencies that creep in without justification.

**The test:** would a portable alternative deliver the same outcome AND would swapping the dep cost less than ~1 day of operator work? If yes to both, the lockin is worth flagging before committing.

These guidelines are working if: fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, fewer same-mistake-twice corrections, fewer surprise vendor-lockin discoveries mid-feature, and clarifying questions come before implementation rather than after mistakes.

## Documentation updates

| File | When to update | What to write |
|---|---|---|
| `CHANGELOG.md` | **Per relevant commit.** Trigger: commit prefix is `feat:` / `fix:` / `perf:` / `refactor:`, OR commit carries the `!` breaking-change marker (e.g., `feat!:`). Skip on `chore:` / `docs:` / `style:` / `test:` / `build:` / `ci:`. | New entry at top of `[Unreleased]`, dated. For user-visible changes (feat / fix / perf, breaking-marker commits): **user-facing language** (*"You can now filter transactions by category"*). For internal refactors: **dev-facing language** (*"Refactored transaction parser for clarity"*). |
| `docs/STATUS.md` | When module status, build state, or handoff context changes | Update the affected section only |
| `docs/TODO.md` | When priorities shift, new work surfaces, or items ship | Surgical edits; move completed items to the matching CHANGELOG entry |
| `docs/IDEAS.md` | When a forward-looking idea is worth recording but not yet TODO-prioritized | Append with trigger + reason-not-now; move to TODO.md when matured |
| `docs/ARCHITECTURE.md` | When architecture, patterns, or data model change | Surgical edits to affected sections |
| `docs/PRODUCT.md` | When features are added, removed, or redesigned | Update the relevant feature section |
| `LEDGER.md` | Via `/ledger-capture` when session-level oddity worth remembering | Append a dated entry at the top of the appropriate category section |

Rules: keep entries concise; don't rewrite entire files; CHANGELOG entries follow the prefix rule above (not every push gets one); other files are updated only when relevant. Conventional Commits prefix is the **user-impact decision** — pick `feat:`/`fix:`/`perf:` when users will feel the change, `refactor:` for behavior-preserving restructure that's still worth logging for forensic value, and the lower-noise prefixes when the change is internal-only and not worth logging.

## Project Rules

- **Agent model override** — `[Populated post-init. Examples: "When launching sub-agents via the Agent tool, always pass `model: opus` explicitly" (Claude Code) — or stack-equivalent for Codex. Default agent models are tuned for cost/speed; this project may prefer capability.]`
- **LEDGER.md re-read before non-trivial commits** — Before committing a non-trivial PR, re-read `LEDGER.md` and ask: "Did this session produce anything session-spanning that would otherwise vanish?" (incident lesson, design rationale not in any plan doc, new key invariant, open/resolved investigation). If yes, capture it in the same PR via `/ledger-capture`. Unlike CHANGELOG (triggered by every commit), LEDGER.md has no structural trigger — that's why it needs active discipline.
- **No `--no-verify` / `--no-gpg-sign`** — never bypass commit hooks or signing unless the user explicitly requests it. If a hook fails, fix the underlying issue and create a new commit.

## Project Principles

`[Populated by /grill-with-docs at project init. Examples to look for during alignment: domain invariants, money-correctness rules, legal/compliance constraints, auditability requirements, architectural constants. Each principle should be one that, if violated by code, becomes an audit finding rather than a preference debate. Format: 3-7 bulleted principles, each one paragraph.]`

## Quick Reference

`[Populated post-init. Stack-specific commands, e.g.:
- Node: \`pnpm verify\` runs lint + test + build — every push must pass it.
- Python: \`uv run pytest && ruff check && mypy .\` — every push must pass it.
- Whatever your stack — ONE composite command that gates commit/push.]`

## Git conventions

`[Populated post-init. PR flow examples:
- Single-maintainer: feature branches → main directly.
- Team: feature branches → develop → main, maintainer promotes.
- Strict: claude/* branches only (push restriction enforced by remote).]`

**Conventional Commits.** Format: `<type>: <description>` with optional body.

| Type | Use for |
|---|---|
| `feat` | New feature or module |
| `fix` | Bug fix |
| `test` | Test changes |
| `refactor` | Behavior-preserving restructure |
| `docs` | Documentation |
| `style` | Formatting / CSS without logic change |
| `chore` | Tooling, config, dependencies |
| `perf` | Performance improvement |

Rules: one logical change per commit; imperative mood; first line ≤ 72 chars; use the body to explain *why* when non-obvious.

**Audit-finding fixes** include the audit-qualified ID in the commit/PR title for traceability:

```
fix(quotas): rate-limit receipts endpoint [AUDIT_4:SECU-03]
```

This lets `git log --grep='AUDIT_4:'` enumerate every fix tied to an audit and tracker `Notes` cite a SHA the reader can decode immediately.

## Common pitfalls

`[Day-1 empty. Populated by /pitfall-graduate when a LEDGER lesson or invariant hits all 3 criteria: frequency ≥3 (across LEDGER entries or commits), universal applicability ("always/never", not "if/then"), concision (fits in 1-2 lines).]`

`[Two paths land here: (a) /ledger-capture auto-invokes /pitfall-graduate --auto when criteria are met during agent work — these arrive with a `> [!warning] Pending operator review` callout and get confirm/rollback during the next /ledger-lint Step 0; (b) operator manually invokes /pitfall-graduate when they spot the pattern (no pending-review callout — operator's invocation is the confirmation).]`

`[Each entry format: short title — concrete example. How to avoid. Max 2 lines. Examples that often surface for webapps: serialization at server/client boundaries, async/await traps, date-month-indexing surprises, env-var presence-check before use — but don't pre-populate; let real incidents drive these.]`

---

**Code is the ultimate source of truth.** Docs describe the *why*; code defines the *what*.
