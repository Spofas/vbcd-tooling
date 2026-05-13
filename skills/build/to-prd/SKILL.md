---
name: to-prd
description: Turn the current conversation context into a PRD and publish it to the project issue tracker. Use when user wants to create a PRD from the current context.
---

<!--
Source: https://github.com/mattpocock/skills/blob/main/skills/engineering/to-prd/SKILL.md
License: see upstream LICENSE for terms.
Copy date: 2026-05-13
Body content verbatim from upstream. Pack calibration section appended below for operator-pack-specific overrides (project-conventions source; PRD destination policy); upstream body untouched.
Operator-side usage discipline (trigger + chain ordering with /grill-with-docs + /to-issues) lives in README §4.2.
-->

This skill takes the current conversation context and codebase understanding and produces a PRD. Do NOT interview the user — just synthesize what you already know.

The issue tracker and triage label vocabulary should have been provided to you — run `/setup-matt-pocock-skills` if not.

## Process

1. Explore the repo to understand the current state of the codebase, if you haven't already. Use the project's domain glossary vocabulary throughout the PRD, and respect any ADRs in the area you're touching.

2. Sketch out the major modules you will need to build or modify to complete the implementation. Actively look for opportunities to extract deep modules that can be tested in isolation.

A deep module (as opposed to a shallow module) is one which encapsulates a lot of functionality in a simple, testable interface which rarely changes.

Check with the user that these modules match their expectations. Check with the user which modules they want tests written for.

3. Write the PRD using the template below, then publish it to the project issue tracker. Apply the `ready-for-agent` triage label - no need for additional triage.

<prd-template>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A LONG, numbered list of user stories. Each user story should be in the format of:

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

This list of user stories should be extremely extensive and cover all aspects of the feature.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets. They may end up being outdated very quickly.

Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it within the relevant decision and note briefly that it came from a prototype. Trim to the decision-rich parts — not a working demo, just the important bits.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)

## Out of Scope

A description of the things that are out of scope for this PRD.

## Further Notes

Any further notes about the feature.

</prd-template>

## Pack calibration

This pack overrides the upstream *"run `/setup-matt-pocock-skills`"* prerequisite. Project conventions live in a sidecar file (`conventions.md`) next to this SKILL.md.

**Convention source (in order):**
1. Read `.claude/skills/build/to-prd/conventions.md` (or `.agents/skills/build/to-prd/conventions.md` for Codex).
2. If the file exists and placeholders are filled, use the values directly.
3. If the file exists but placeholders are still in `[Specify: ...]` form, OR if the file is missing entirely, **interview the operator inline**:
   - *"PRD destination — `tracker` (publish to GitHub Issues / Linear / etc.) or `local` (write to `docs/prds/<slug>.md`)?"*
   - If `tracker`: *"Tracker URL?"* and *"Triage label to apply?"*
   - Write answers to `conventions.md` for subsequent invocations (auto-populate fallback).

**Destination behavior:**
- `destination = tracker` → publish to the issue tracker, apply the triage label, return the issue URL (matches the upstream verbatim body's Step 3).
- `destination = local` → write the PRD to `docs/prds/<slug>.md` (slug derived from the PRD title, kebab-case). No tracker call, no triage label. Return the file path.

The upstream body still applies for the PRD structure (Process steps 1–2 + the `<prd-template>` block); only the publication step in Step 3 varies by destination.

**Pack-pattern note:** `conventions.md` joins the placeholder-file family (CONTEXT.md, AGENTS.md placeholders, LEDGER.md User preferences, MANUAL_TESTS.md, AUDIT_SCHEMA.md dimension checklists). All get populated at `/grill-with-docs` closing prompts at project init; this one is consistent with the existing pattern.
