---
name: handoff
description: Produces a clean carry-over prompt for the next session. Use ONLY when explicitly invoked via /handoff. Do not auto-fire on session-related events. Run at session end, before /clear, when context is getting heavy, or when handing off to a different worktree, agent, or operator.
---

# /handoff

**When to invoke:** end of a working session; when you're about to `/clear`; when context is getting heavy — recognizable by *scrolling back becomes hard, responses feel slower, or you find yourself re-explaining things the agent should remember from earlier in the session* — and you want to start fresh without losing state; when handing off work to a different worktree / different agent / different person. Output is a paste-into-next-session prompt that lets the next session start cold without ad-hoc *"remember when we…"* recap.

**Why this skill exists:** without it, "one thread per task" stays a CLAUDE.md principle without operational follow-through. Non-tech operators especially can't carry session state in their head; they need it written. This skill produces that written state, in a shape the next session can immediately consume.

## Invocation modes

The skill adapts capture scope based on how it's invoked:

- **Bare** — `/handoff` (no args). Default: captures *"context of the last work being done + files being handled"* — recent file edits, recent decisions, currently open threads.
- **Mid-plan** — agent detects an active plan (operator was executing a multi-step plan from `/plan-review`, `/to-prd`, plan-mode output, or similar). Default: captures the plan + progress through it + remaining steps.
- **Arg-driven** — `/handoff <natural-language-scope>`. Operator's args set the focus: *`/handoff focus-on-auth-bug`*, *`/handoff for-Codex-next-session`*, *`/handoff the-payment-refactor`*. Agent scopes capture to the named focus.

Modes are not mutually exclusive — operator can pass args mid-plan and the agent honors both (args = focus; plan = context).

## Protocol

### Step 1 — Survey the current session (mode-aware)

Survey scope follows the active invocation mode (see *Invocation modes* above). Bare → recent-work focus. Mid-plan → plan + progress focus. Arg-driven → operator's named focus. Capture honestly — if a step is half-done, say so; don't pretend it shipped.

**Mid-implementation handoff (dirty tree).** If the working tree has uncommitted changes, surface to the operator *before* composing the prompt: *"Working tree has uncommitted changes — commit now / stash / leave-as-is for next session? Next session will need to know how to resume."* Capture the operator's decision in the State bucket.

| Bucket | What to capture |
|---|---|
| **State** | What was the goal of this session? What got done? What's the current state of the working tree (clean / staged / unstaged / mid-rebase / etc.)? |
| **Files modified** | Paths of every file edited or created this session. Group by purpose if helpful (e.g. "core changes:" vs "test additions:"). |
| **Decisions made** | Non-obvious choices the operator made during this session — library picks, naming choices, architecture trade-offs. The kind of thing someone reading the diff alone would have to reverse-engineer. |
| **Blockers** | What's stuck and why. Specific: "Can't run `pnpm test` because Docker daemon isn't running" beats "tests don't work." |
| **Next steps** | What the next session should pick up. Ranked: most-important-first. Each step phrased as an action, not a description ("Run `/diagnose` on the failing auth test" beats "Auth test is failing"). |
| **Files to load** | Specific paths the next session should read at start to recover context. Usually `LEDGER.md` + the current branch's working files; sometimes a specific plan doc or ADR. |
| **Open questions** | Questions deferred to the next session (the operator wasn't sure or didn't have time). |

### Step 2 — Compose the handoff prompt

Format the captured state as a paste-into-next-session prompt. The output is the handoff prompt itself (not metadata about it). Use a fenced markdown block so the operator can copy-paste cleanly:

```markdown
# Handoff from session ending YYYY-MM-DD HH:MM

## Where we left off
[State paragraph: goal, what got done, current tree state.]

## Files modified
- `path/to/file1.ts` — brief reason
- `path/to/file2.tsx` — brief reason

## Decisions made
- [Decision 1, with rationale if non-obvious]
- [Decision 2]

## Blockers
- [Blocker 1, with specific cause]
  *(or: "None.")*

## Next steps (in order)
1. [Action]
2. [Action]
3. [Action]

## Files to load at session start
- `LEDGER.md`
- `[other specific paths]`

## Open questions for the operator
- [Question 1]
  *(or: "None.")*

---

To resume: paste this prompt as the first message of the next session, then read the listed files.
```

### Step 3 — Surface to the operator

Print the composed handoff prompt to the operator. **Do not write to a file by default** — the operator decides whether to persist.

If the operator wants the handoff persisted, write to `docs/handoffs/YYYY-MM-DD-{short-slug}.md` (creating `docs/handoffs/` if absent). The slug summarizes the work in 2–4 words. This gives an audit trail of session-by-session work for projects where that's valuable.

### Step 4 — Optional: capture-spanning items

Scan the survey output for anything that should also be captured in `LEDGER.md` (an invariant discovered, a decision that's session-spanning, an investigation that should track across sessions). For each candidate, surface a prompt: *"This looks captureable per `/ledger-capture` — invoke now?"* Don't auto-capture; the operator decides. Decisions that ship in the next session should ride in `/handoff`'s next-steps; decisions that survive multiple sessions should go to `/ledger-capture`.

## Anti-patterns

- **Don't pad the prompt with everything from the session.** The handoff is a *minimum-viable-restart* artifact, not a transcript. Cut anything that doesn't serve the next session's first 5 minutes.
- **Don't include speculative next steps.** If the operator hasn't decided what comes next, write "Next steps deferred — operator to decide on resume." Better honest than padded.
- **Don't write the handoff to disk by default.** The default is print-to-chat for paste. Persist only on explicit operator request.
- **Don't conflate handoff with `/ledger-capture`.** Handoff is *transient* (session-to-session). Capture is *durable* (session-spanning, lives in `LEDGER.md`). Different artifacts.
- **Don't auto-fire on `/clear`.** This skill is operator-initiated. If the operator forgets, that's their call — don't surprise them.

## Related

- `/ledger-capture` — for items that survive past the next session (invariants, lessons, design rationales).
- `/ledger-lint` — periodic audit of LEDGER.md; orthogonal to handoff.
- `LEDGER.md` Maintenance section — handoff is *not* LEDGER material; this skill complements rather than duplicates.
- AGENTS.md §8 (Accumulate, Don't Restart) — the principle handoff partly operationalizes (the rest is `/ledger-capture` + AGENTS.md gotchas).

## Invariants

- **Operator-initiated.** Never auto-fire. The skill activates only on explicit `/handoff` invocation.
- **Print-by-default.** Output is the composed handoff prompt printed to chat. File persistence is opt-in.
- **No state mutation.** This skill never modifies code, configs, or other files (except optionally `docs/handoffs/<file>.md` on explicit request).
- **Honest state capture.** If something's half-done, say so. The next session benefits from accurate state, not optimistic state.
- **Capture-spanning items go to `/ledger-capture`.** Don't try to make LEDGER entries from inside `/handoff` — refer the operator to the right tool.
