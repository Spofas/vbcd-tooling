---
name: plan-review
description: Reviews a plan-mode output against the 9-section AGENTS.md before approval. Use ONLY when explicitly invoked via /plan-review. Do not auto-fire on plan-mode output. Run before approving any plan that touches trunk (auth, payments, data integrity, schema, multi-tenant scoping) OR introduces something new (feature, module boundary, external integration). Skip for bug fixes with known root cause, styling/copy edits, single-file changes following an existing pattern, or refactors internal to one module.
---

# /plan-review

**When to invoke:** Claude (or Codex) has just produced a plan via plan-mode (or equivalent), and you're about to approve. **Run** when the plan touches trunk (auth, payments, data integrity, schema, multi-tenant scoping) OR introduces something new (feature, module boundary, external integration). **Skip** for bug fixes with known root cause, styling/copy edits, single-file changes following an existing pattern, or refactors internal to one module. Judgment elsewhere — when uncertain, default to running it.

**Why this skill exists:** plan-mode produces output the AI thinks is good. Without an operator-side review checklist, a non-tech operator's only options are (a) read the plan and trust their gut or (b) rubber-stamp. Both fail predictably. This skill walks the operator through a structured 6-question review against the CLAUDE.md principles, surfaces concrete follow-up prompts for any worry, and ends with an explicit approve / revise / re-grill recommendation.

## Protocol

### Step 0 — Plan-shape precondition check

Before walking the 6 questions, assess whether the plan has the minimum shape to be reviewable. Check three dimensions:

- **File list present** — plan names which files will be touched, or explicitly states "single file `path/to/foo.ts`"
- **Decision points present** — plan articulates at least one explicit choice (X over Y with rationale)
- **Verification criteria present** — plan states how to verify success (tests / preview check / specific expected output)

If **2 or more are absent**, exit Step 0 with one of three specific redirects (the AI picks based on which dimension is most missing):

- *"Plan lacks a file list. Run plan-mode again with explicit file targets, then re-invoke `/plan-review`."*
- *"Plan lacks verification criteria. Run `/grill-with-docs` to surface success conditions, then re-plan, then re-invoke `/plan-review`."*
- *"Plan lacks explicit decisions or alternatives. For trunk-touching changes (auth / payments / data integrity / schema / multi-tenant), this thin plan is review-unviable. Expand the plan or run `/grill-with-docs` first."*

**Why exit-early instead of degrade-gracefully:** a half-baked plan walked through the 6-question review produces abstract Block findings that don't help the operator understand the root cause (the plan is thin, not the implementation strategy). Clean exit + specific redirect produces sharper signal than 6 mechanical "this is incomplete" findings. For non-tech operators especially: clear redirects beat inferred root causes.

If **only 1 dimension is absent**, proceed to Step 1 with that dimension's gap auto-tagged as Block-severity (no need to walk the corresponding question — it's already a Block).

### Step 1 — Load the plan

Locate the plan-mode output the operator wants reviewed. Usually it's the most recent plan in the current conversation. If ambiguous, ask the operator to specify (file path, conversation reference, or paste-in).

Read the plan in full before asking any questions. Hold it in working memory for the rest of the protocol.

### Step 2 — Walk the 6 review questions

For each question below, answer it concretely from the plan, then surface concerns to the operator. **Don't sanitize** — if a section of the plan worries you, say so. If the plan looks clean, say so. The point is honest signal, not stamping approval.

The 6 questions map to the AGENTS.md sections most relevant to plan content, **walked in substrate-priority order** (verification first per §1, then intent / simplicity / surgical / language / blast-radius). Sections §5 Output Mechanics and §8 Accumulate-Don't-Restart are about agent execution and post-execution discipline; they don't apply to plan review.

#### Q1 — Is success criteria defined? (AGENTS.md §1 Goal-Driven Execution)

- Does the plan declare how to verify each step worked? (Tests, screenshots, expected outputs.)
- Are the verification checks themselves specified concretely (e.g., "test passes" — *which* test?), or vague ("make sure it works")?
- For any step without a verification check, surface: "How will we know this step worked?"
- **Q1 is first because verification is the single highest-leverage discipline in the substrate** — a plan without verification criteria is not approvable, regardless of how good the rest looks.

#### Q2 — Does the plan match aligned intent? (AGENTS.md §2 Think Before Coding)

- Was there a `/grill-with-docs` session for this work? If yes, does the plan reflect what was decided there? If no, does the plan show the AI took the operator's brief seriously, or did it pick a direction silently?
- Are there assumptions baked into the plan that should be surfaced? (e.g., "this assumes you want X — is that right?")
- If the plan picked one approach without naming alternatives, that's a yellow flag — flag it.

#### Q3 — Is the plan minimum-viable? (AGENTS.md §3 Simplicity First)

- Is anything in the plan beyond what was asked?
- Are there speculative abstractions (interfaces / configs / flexibility) for things that have one current use?
- Are there error-handling branches for scenarios that can't actually happen?
- Senior-engineer test: would a senior engineer call this plan overcomplicated? If yes, flag.

#### Q4 — Are the changes surgical? (AGENTS.md §4 Surgical Changes)

- Does the plan touch files / code unrelated to the request?
- Does the plan include refactors / cleanups / formatting changes the operator didn't ask for?
- For each changed file: does the change trace directly to the request, or is it incidental?
- Plans that mention "while we're here, also…" are usually scope creep. Flag.

#### Q5 — Does the plan respect domain language? (AGENTS.md §6 Build Shared Language)

- Does the plan use terms from `CONTEXT.md`, or does it introduce new terminology?
- If new terms appear, are they actually new domain concepts (warranting a CONTEXT.md addition) or drift from established vocabulary?
- Naming consistency in the plan: variable / file / function names match domain language?

#### Q6 — Is the blast radius proportionate? (AGENTS.md §7 Protect Trunk Vibe Leaves)

- Does the plan touch the trunk (auth, payments, data integrity, schema, multi-tenant scoping, anything that ripples)? If yes, is the operator paying attention proportionate to the risk?
- For trunk changes: does the plan include extra verification, code review, or rollback plan?
- For leaf changes: does the plan accept reasonable AI judgment without asking the operator to decide every detail?

### Step 3 — Tally concerns

Categorize each "yes, I'm worried" answer:

| Severity | Definition | Recommendation |
|---|---|---|
| **Block** | Plan has no verification criteria (Q1) OR misaligns with intent (Q2) OR touches trunk without proportionate scrutiny (Q6) | **revise** or **re-grill** |
| **Push back** | Plan has scope creep / speculative complexity / domain-language drift (Q3 / Q4 / Q5) | **revise** with specific request |
| **Note** | Minor issues operator should be aware of, but plan is approvable as-is | **approve** with note |

#### Example findings per category

Concrete shapes the AI should match against — not exhaustive, illustrative.

**Block examples:**
- *Q1 (verification gap):* "Plan adds authentication endpoint with no testing strategy. Cannot verify success." → re-grill or revise.
- *Q2 (intent mismatch):* "Plan implements 'add login' but doesn't specify session timeout, error states, or password requirements. Intent unclear." → re-grill.
- *Q6 (trunk-without-scrutiny):* "Plan modifies payment processing across 4 files with no blast-radius declaration or rollback notes." → revise.

**Push back examples:**
- *Q3 (speculative complexity):* "Plan introduces a generic Repository abstraction for a feature with one current use case." → revise without the abstraction.
- *Q4 (scope creep):* "Plan reformats imports across 6 files unrelated to the auth-flow request." → drop the reformatting; commit separately if desired.
- *Q5 (domain drift):* "Plan uses 'user' and 'account' interchangeably; CONTEXT.md distinguishes them." → align terminology with CONTEXT.md before proceeding.

**Note examples:**
- "Plan adds helper `formatPrice` but `priceUtils.ts` already exports `formatCurrency` — consider consolidating in a future change."
- "Plan uses a slightly older pattern (e.g., `useEffect` for data fetching where `useSWR` would be idiomatic) — works; consider in the next refactor."

### Step 4 — Surface explicit recommendation

End with one of three explicit recommendations:

- **`approve`** — plan is ready. List any "Note" items the operator should be aware of, but no Block / Push-back concerns surfaced.
- **`revise`** — plan has Block or Push-back concerns. List them numbered with specific revision asks. Example:
  ```
  Plan-review recommendation: REVISE before approval.

  1. Q1 (Verification): Plan has no test or check declared for the new
     "username uniqueness" rule. Add a verification step before approval.
  2. Q2 (Intent): Plan adds a "username" field, but no /grill-with-docs session
     established whether usernames are needed. Either run /grill-with-docs to
     decide, or remove the field.
  3. Q4 (Surgical): Plan reformats imports across 4 files unrelated to the
     auth-flow request. Drop those changes; commit separately if desired.
  ```
- **`re-grill`** — the plan reveals that intent itself is unclear, not just the plan. Recommend running `/grill-with-docs` before re-planning.

### Step 5 — Wait for operator decision

Do not proceed past plan-review without explicit operator response. Possible operator paths:

- **"Approve"** → operator approves the plan. The skill exits; agent proceeds to implementation.
- **"Revise"** → operator asks the agent to revise per the surfaced concerns. Plan-mode re-runs; `/plan-review` can be re-invoked on the revised plan.
- **"Re-grill"** → operator runs `/grill-with-docs` to clarify intent. After alignment, plan-mode re-runs.
- **"Override"** → operator explicitly approves despite plan-review's concerns.
  - **Block-severity overrides (Q1 verification gap / Q2 intent mismatch / Q6 trunk-without-scrutiny):** rationale required. Include a one-line "why approve anyway" note in the commit message (e.g., *"override Q1: verification will land in next PR; tested manually for now"*) OR capture as a LEDGER entry via `/ledger-capture` (rationale category). Block-severity overrides are the highest-risk operator decisions; future-self needs to trace the reasoning when something breaks.
  - **Push-back-severity overrides (Q3 simplicity / Q4 scope creep / Q5 domain drift):** judgment call — no documentation requirement. Operator's decision is captured implicitly in what ships.

## Anti-patterns

- **Don't be gentle.** Plan-review's value comes from honest signal. Hedging ("looks mostly fine, but maybe…") helps no one. Be specific about concerns.
- **Don't approve through omission.** A question you didn't ask is a concern you didn't surface. Walk every question, even if the answer is "no concerns."
- **Don't review your own plans automatically.** This skill is operator-initiated. If the agent produced the plan AND ran plan-review on it without operator request, the review is non-independent.
- **Don't expand scope inside plan-review.** This skill reviews; it doesn't propose alternatives unless asked.
- **Don't replace `/grill-with-docs`.** Plan-review checks the plan against intent; it doesn't establish intent. If intent isn't clear, recommend re-grilling — don't try to grill inside plan-review.

## Related

- `/grill-with-docs` — predecessor when intent is fuzzy. Plan-review assumes intent is established.
- `/audit` — broader / periodic. Plan-review is per-plan; audit is project-wide.
- AGENTS.md sections §1, §2, §3, §4, §6, §7 — the principles plan-review walks against (in substrate-priority order: verification → think → simplicity → surgical → language → blast-radius). §5 Output Mechanics and §8 Accumulate-Don't-Restart don't apply to plan content.
- `/handoff` — orthogonal; runs at session end, plan-review runs before commit.

## Invariants

- **Operator-initiated.** Never auto-fire on plan-mode output.
- **6 questions, every plan.** Don't skip questions. Even if the plan looks clean, walk all six.
- **Explicit recommendation.** End with `approve` / `revise` / `re-grill`. Hedging defeats the skill's purpose.
- **No mutation.** This skill never modifies the plan or any file. It produces a recommendation only.
- **Bounded specificity.** When surfacing concerns, cite plan content (line, section, or paragraph) — vague concerns are unactionable.
- **Override discipline.** Operator can approve despite concerns; if so, note it in LEDGER.md or an ADR for posterity.
