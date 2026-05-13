---
name: to-issues
description: Break a plan, spec, or PRD into independently-grabbable issues on the project issue tracker using tracer-bullet vertical slices. Use when user wants to convert a plan into issues, create implementation tickets, or break down work into issues.
---

<!--
Source: https://github.com/mattpocock/skills/blob/main/skills/engineering/to-issues/SKILL.md
License: see upstream LICENSE for terms.
Copy date: 2026-05-13
Body content verbatim from upstream. Pack calibration section appended below — same pattern as `/to-prd` (conventions sidecar overrides upstream `/setup-matt-pocock-skills` dependency); upstream body untouched.
Operator-side usage discipline (trigger + chain ordering with /to-prd) lives in README §4.2.
-->

# To Issues

Break a plan into independently-grabbable issues using vertical slices (tracer bullets).

The issue tracker and triage label vocabulary should have been provided to you — run `/setup-matt-pocock-skills` if not.

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes an issue reference (issue number, URL, or path) as an argument, fetch it from the issue tracker and read its full body and comments.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code. Issue titles and descriptions should use the project's domain glossary vocabulary, and respect ADRs in the area you're touching.

### 3. Draft vertical slices

Break the plan into **tracer bullet** issues. Each issue is a thin vertical slice that cuts through ALL integration layers end-to-end, NOT a horizontal slice of one layer.

Slices may be 'HITL' or 'AFK'. HITL slices require human interaction, such as an architectural decision or a design review. AFK slices can be implemented and merged without human interaction. Prefer AFK over HITL where possible.

<vertical-slice-rules>
- Each slice delivers a narrow but COMPLETE path through every layer (schema, API, UI, tests)
- A completed slice is demoable or verifiable on its own
- Prefer many thin slices over few thick ones
</vertical-slice-rules>

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each slice, show:

- **Title**: short descriptive name
- **Type**: HITL / AFK
- **Blocked by**: which other slices (if any) must complete first
- **User stories covered**: which user stories this addresses (if the source material has them)

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the dependency relationships correct?
- Should any slices be merged or split further?
- Are the correct slices marked as HITL and AFK?

Iterate until the user approves the breakdown.

### 5. Publish the issues to the issue tracker

For each approved slice, publish a new issue to the issue tracker. Use the issue body template below. These issues are considered ready for AFK agents, so publish them with the correct triage label unless instructed otherwise.

Publish issues in dependency order (blockers first) so you can reference real issue identifiers in the "Blocked by" field.

<issue-template>
## Parent

A reference to the parent issue on the issue tracker (if the source was an existing issue, otherwise omit this section).

## What to build

A concise description of this vertical slice. Describe the end-to-end behavior, not layer-by-layer implementation.

Avoid specific file paths or code snippets — they go stale fast. Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it here and note briefly that it came from a prototype. Trim to the decision-rich parts — not a working demo, just the important bits.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Blocked by

- A reference to the blocking ticket (if any)

Or "None - can start immediately" if no blockers.

</issue-template>

Do NOT close or modify any parent issue.

## Pack calibration

This pack overrides the upstream *"run `/setup-matt-pocock-skills`"* prerequisite. Project conventions live in a sidecar file (`conventions.md`) next to this SKILL.md — same pattern as `/to-prd`.

**Convention source (in order):**
1. Read `.claude/skills/build/to-issues/conventions.md` (or `.agents/skills/build/to-issues/conventions.md` for Codex).
2. If the file exists and placeholders are filled, use the values directly.
3. If placeholders are unfilled OR file is missing, **interview the operator inline** for tracker URL + triage label, then write `conventions.md` for subsequent invocations.

**Prerequisite:** unlike `/to-prd` (which supports `destination=local` for `docs/prds/<slug>.md`), `/to-issues` *requires* an issue tracker — vertical-slice issues are by definition tracker-bound (parallel-grabbable, dependency-referenced by ID). If `conventions.md` shows `destination=local`, surface to operator: *"`/to-issues` requires a tracker — your `/to-prd` conventions show local-only. Need tracker URL + triage label?"*

**Cross-skill conventions sharing.** `/to-prd` and `/to-issues` use the same tracker URL + triage label. At `/grill-with-docs` closing prompts, populate BOTH `conventions.md` files in one shot — operator types once, both files filled.
