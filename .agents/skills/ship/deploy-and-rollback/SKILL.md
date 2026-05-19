---
name: deploy-and-rollback
description: Walks through a safe deployment sequence — pre-deploy gates, blast-radius declaration, deploy, active monitor window, CHANGELOG, rollback path. Use ONLY when explicitly invoked. Fire on (a) trunk-touching commits about to deploy (auth / payments / data integrity / multi-tenant scoping / schema migration), (b) infrastructure changes (env vars, DNS, Vercel or hosting project settings, third-party integration changes). Skip for non-trunk feature commits, styling-only / copy-only / asset-only changes. Refuses to auto-execute deploy commands; always asks the operator first.
---

# /deploy-and-rollback

**When to invoke:**

- **Trunk-touching commit about to be deployed** — auth, payments, data integrity, multi-tenant scoping, schema migration. For continuous-deploy stacks (Vercel-from-`main` and similar), this means *before* the `git push origin main` that triggers the deploy, not after.
- **Infrastructure change** — env vars, DNS, hosting project settings (Vercel / Fly / Render), third-party integration (Stripe webhook config, Resend domain, etc.).
- **Preview / staging deploy that will be promoted directly to prod** — same protocol.

**Skip for:** non-trunk feature commits, pure styling / copy / asset changes, refactors internal to one leaf module. Those go through pre-commit hook + preview-URL-walk + operator judgment instead.

**Trigger discipline:** this skill matches §7 (Pack trunk vs. pack leaves) — full safety belt where blast radius is real; lighter path elsewhere. Operator-invoked only; never auto-fire on every commit.

**Why this skill exists:** non-tech operators are the most likely to ship without a runbook, the least likely to remember rollback steps under stress, and the most likely to skip the verify gate if it's friction. This skill makes the safe-deploy sequence into a checklist the agent walks the operator through, refuses to auto-execute, and produces a `docs/deploy-runbook.md` artifact that grows with each deploy. Belt-and-suspenders against the highest-blast-radius operator-initiated mistake.

## Protocol

### Step 1 — Pre-deploy gates (verify)

Before anything else, verify all signals are green:

- [ ] **Working tree is clean** — `git status` shows no uncommitted changes (or operator confirms outstanding state is intentional).
- [ ] **On the right branch** — `git branch --show-current` matches the operator's expected deploy branch.
- [ ] **Tests pass** — run the project's verify command (from CLAUDE.md Quick Reference; e.g., `pnpm verify` / `uv run pytest && ruff check && mypy .`). All green.
- [ ] **Type-check clean** — typically part of verify; flag if not.
- [ ] **Lint clean** — typically part of verify.
- [ ] **Build succeeds** — `pnpm build` / equivalent. Surface any warnings worth attention.
- [ ] **No `.env` drift** — required env vars listed in `.env.example` exist in the deploy environment. (Ask operator to confirm if not auto-checkable.)
- [ ] **Migration order** — if there's a schema migration in this deploy, it ran in staging first / is reversible / has a documented rollback (or operator confirms rollback strategy).
- [ ] **Preview URL walked (conditional)** — *if change touches UI or any critical-path screen:* operator has clicked through affected screens on the Vercel (or equivalent) preview URL, no visual regression, no broken interactions. *If backend-only:* mark N/A. Anchored to operator profile (visual polish + UX smoothness load-bearing); the only structural gate enforcing visual checks before prod.
- [ ] **Latest CHANGELOG.md entry** — confirm `## [Unreleased]` has entries for what's about to ship, OR confirm the operator wants to ship without a CHANGELOG entry.

If any check fails: **halt.** Surface the failure to the operator. Do not proceed until either fixed or operator explicitly overrides ("override: ship anyway because X").

### Step 2 — Blast-radius declaration

Before deploying, the operator declares scope explicitly. This forces conscious thought before the irreversible step.

Surface these questions to the operator (do NOT answer them yourself — operator answers):

1. **Which users / tenants are affected?** "All", "Tenants matching X", "Specific user IDs Y", or "No users yet — pre-launch."
2. **Which systems / data?** "Code only", "Code + schema migration", "Code + data migration", "Infra config (DNS / load balancer / etc.)", "Third-party integrations (Stripe / Resend / etc.)".
3. **Expected behavior change?** What will users see differently? (One-line answer.)
4. **Reversibility?** "Fully reversible (code-only, no data change)", "Partially reversible (data migration with backup)", "Not reversible (data destruction; document strategy)".
5. **Off-hours / on-hours?** Are users currently active? If yes, is this OK to ship now?

If reversibility is "Not reversible," **halt** and confirm the operator understands. Recommend a paired pre-deploy snapshot or backup. Don't proceed without explicit operator confirmation.

Capture the operator's answers — they go into the CHANGELOG entry and (if persisted) into `docs/handoffs/deploy-YYYY-MM-DD.md`.

### Step 3 — Identify or build the deploy runbook

Read `docs/deploy-runbook.md` if it exists. If it doesn't, build it now via interview:

```
# Deploy runbook

## Deploy command(s)
[Operator-provided. Examples by stack:
- Vercel: `vercel deploy --prod`
- Fly.io: `flyctl deploy`
- Render: `git push origin main` (auto-deploys via CI)
- Custom: `<command sequence>`]

## Post-deploy verification
[How to know the deploy succeeded:
- Hit a health endpoint (e.g., `/api/health`)
- Spot-check the production URL
- Watch a specific dashboard
- Check the deploy provider's status]

## Rollback command(s)
[Operator-provided. Examples:
- Vercel: revert via dashboard or `vercel rollback <previous-deployment-url>`
- Fly.io: `flyctl releases revert <release-number>`
- Git-based deploy: `git revert <commit> && git push`
- Schema migration rollback: stack-specific migration-down command]

## Rollback verification
[How to know the rollback succeeded — same shape as post-deploy verification.]

## Monitoring signals (agent-runnable)
[REQUIRED: at least one signal the agent can actually run during Step 5. Operator provides one or more:

- **CLI command** — e.g., `vercel logs --since 2m` (agent runs via Bash; parses for non-OK status / 500s / error patterns)
- **Health endpoint** — e.g., `GET https://prod-url/api/health` (agent runs via WebFetch; verifies 200 + expected payload shape)
- **Spot-check prompt** — e.g., "refresh /dashboard, verify recent transactions list renders" (agent prompts operator at each interval; operator eyes it)
- **Dashboard URL** — Sentry / Vercel Analytics / similar (agent WebFetches; parses for error spikes)

Mix is fine. If none provided, Step 5 cannot run actively — it will halt and request these be filled in.]
```

If the runbook is missing fields, fill them via short interview with the operator. Save the populated runbook to `docs/deploy-runbook.md`.

The runbook is **build-once, refine-as-stack-changes**. It's not rebuilt every deploy.

**First-build rollback rehearsal (one-time, strongly recommended).** When this runbook is *first* built — before any real-money rollback has relied on it — surface this to the operator:

> *"Before this runbook serves a real rollback, recommend exercising it once on a low-stakes deploy. Deploy something trivial (CSS tweak, copy change), then run the rollback command from the runbook + verify per the rollback-verification step. ~30 min. Verifies the runbook commands actually work and trains muscle memory once when stakes are zero. The first rollback you ever run will otherwise be the highest-stakes one."*

Operator decides yes / later / skip. If accepted, walk them through it. If deferred or skipped, capture as an open investigation via `/ledger-capture` — *"Rollback rehearsal pending for `docs/deploy-runbook.md` (first-build)."* Surfaces again at next `/ledger-lint` Step 0 / `/audit` RELI dimension.

Not blocking the runbook build — the recommendation is one-shot at first-build only, not per-deploy friction.

### Step 4 — Deploy (operator-executed)

**Critical:** this skill **does not auto-execute the deploy command.** It surfaces the command to the operator, who runs it themselves (or pastes it for the agent to run with explicit confirmation).

Surface to the operator:

```
Pre-deploy gates: ✓
Blast radius confirmed: <summary from Step 2>
Deploy command (per docs/deploy-runbook.md): <command>

Run this command? Confirm to proceed.
```

If the operator confirms, run the command. Capture stdout/stderr; surface any errors.

If the operator wants to run it themselves, exit the skill. They can re-invoke `/deploy-and-rollback monitor` (with `monitor` arg) to skip ahead to Step 5 once their deploy fires.

### Step 5 — Monitor window (active)

After the deploy command returns success, **do not exit immediately.** The agent monitors **actively** for breakage — heartbeats every 2 min, not silent waiting.

Default monitor window: **10 minutes.** Operator can override (`/deploy-and-rollback monitor 5min` or `/deploy-and-rollback monitor 30min`).

**Mechanism.** The agent runs the **agent-runnable signals** listed in `docs/deploy-runbook.md`'s `## Monitoring signals (agent-runnable)` section at 2-minute intervals. Each runbook **must** list at least one runnable signal — if none exist, halt at Step 5 entry and route back to Step 3 to fill them in before proceeding. (Operator override possible — *"override: monitor by spot-check only"* — but flag as an open investigation via `/ledger-capture`: incomplete runbook.)

Signal shapes the agent can run:

| Shape | What the agent does |
|---|---|
| CLI command (e.g., `vercel logs --since 2m`) | Bash; parse output for non-OK status / 500s / error patterns |
| Health endpoint (e.g., `GET /api/health`) | WebFetch; verify 200 + expected payload shape |
| Spot-check prompt (e.g., *"refresh /dashboard, verify list renders"*) | Surface prompt to operator at each interval; operator answers |
| Dashboard URL (Sentry / Vercel Analytics / etc.) | WebFetch; parse for error spikes |

At each 2-minute mark, the agent surfaces one of:

- **Heartbeat (positive):** *"T+2min — `vercel logs` clean, no errors. `/api/health` 200 OK. Proceeding."* Short positive confirmation, not silent.
- **Anomaly:** *"T+4min — error rate spike: 12 × `500 internal server error` on `/api/payments` in last minute. Recommend rollback. Decision: rollback / wait / proceed?"* Halts, waits for operator.

If the window passes with all heartbeats clean, exit Step 5 with a final *"Monitor window complete: 10 min, all signals clean."* summary.

### Step 6 — CHANGELOG promotion

By the time the deploy runs, `CHANGELOG.md`'s `## [Unreleased]` section already contains per-commit entries (per AGENTS.md per-commit CHANGELOG rule: `feat:` / `fix:` / `perf:` / `refactor:` / `!` prefixes write entries). Step 6 **promotes** those entries under a dated header — it does not re-author them.

Default form (date-only, no semver):

```markdown
## [Unreleased]

## [YYYY-MM-DD] — Deploy

### Added / Changed / Fixed / etc.
- [Existing per-commit entries, moved here verbatim — do not re-author]

### Deploy
- Blast radius: [Step 2 summary]
- Deployed at: HH:MM (UTC or local — be consistent)
- Verified by: [link / output / signal that confirmed success during Step 5 monitor]
```

If the project cuts semver versions (operator-decided), replace the dated header with `## [X.Y.Z] — YYYY-MM-DD` and surface the next version bump to the operator for confirmation. Don't auto-bump. **Default for solo continuous-deploy projects is date-only**; ask the operator at first invocation if uncertain.

**Empty-`[Unreleased]` case.** If the deploy was triggered only by chore/docs/style/test/build/ci-prefix commits (which skip CHANGELOG per AGENTS.md), the new dated header still gets the `### Deploy` sub-section — but no `### Added/Changed/Fixed` content. The deploy event is still captured for forensics; just no user-impact-summary because there is none.

### Step 7 — Optional rollback (if needed)

If the operator decides to roll back (during Step 5 or after):

1. Run the rollback command from `docs/deploy-runbook.md`.
2. Verify rollback succeeded (per the runbook's rollback-verification step).
3. Update CHANGELOG: append a "Rolled back YYYY-MM-DD HH:MM — reason: <X>" note to the affected version's entry, or revert the version-bump entirely if no traffic was served.
4. Capture the failure mode for `/ledger-capture` (lesson) — surface to operator: "What went wrong? Worth capturing as a lesson for next time?"

## Anti-patterns

- **Never auto-execute deploys.** Even with operator pre-approval. The friction is the safety. If the operator wants automated deploys, that's CI/CD's job, not this skill's.
- **Don't skip pre-deploy gates.** Especially `pnpm verify` / equivalent. The two minutes of friction prevents most blast-radius incidents.
- **Don't fill the deploy runbook with assumptions.** Ask the operator. They know their stack. Wrong commands in the runbook are worse than missing commands.
- **Don't compress the monitor window.** 10 minutes is the default for a reason — most deploy failures surface in the first 2–5 minutes. Halving the window halves the catch rate.
- **Don't hide rollback steps.** If a rollback is needed, the runbook's rollback steps should be obvious, not buried.

## Stack-specific surface (operator notes)

This skill is stack-agnostic by design — every command is operator-supplied. But common patterns the operator should plan for:

- **Vercel / Netlify / Render**: deploys via git push; rollback via dashboard or CLI.
- **Fly.io / Render-like**: deploys via CLI; rollback via release-revert.
- **Self-hosted / Docker**: deploys via CI/CD pipeline; rollback via image-revert.
- **Schema migrations**: always have a documented rollback path. For destructive migrations, snapshot first.

The runbook captures whichever applies.

## Related

- `/handoff` — runs at session end; orthogonal.
- `/audit` — periodic health check; deploys may surface audit-worthy state.
- `/ledger-capture` — capture lessons from rollback or unexpected deploy state.
- AGENTS.md §1 (Goal-Driven Execution), §4 (Surgical Changes), §7 (Protect Trunk) — principles this skill operationalizes at the deploy boundary (pre-deploy gates verify; rollback path stays surgical; blast-radius declaration honors trunk discipline).

## Invariants

- **Never auto-execute deploy commands.** Always ask the operator first; the friction is the safety.
- **Pre-deploy gates are not skippable.** If verify fails, halt. Operator override must be explicit.
- **Runbook persists in `docs/deploy-runbook.md`.** Never inline rollback steps in conversation only — they need to survive past this session.
- **Monitor window applies even on successful deploys.** No "skip the monitor, looked fine" path.
- **CHANGELOG entry is mandatory.** Every deploy gets one. The Deploy sub-section captures blast radius for posterity.
- **Rollback failures get captured.** A rolled-back deploy is a candidate for `/ledger-capture` (lesson) by default.
