# {project-name} — Domain Context

**Ubiquitous language for this project.** A small, curated glossary of domain terms the operator, the AI, and the code all use consistently. Implementation of the *ubiquitous language* practice (Eric Evans / DDD; surfaced via Matt Pocock's *Code is not cheap*).

This file is loaded into agent context (reference `@CONTEXT.md` from AGENTS.md, or include in skill bodies that need domain awareness). Keep it tight; the file's value comes from being **scannable in one screen**.

## Why this file exists

For agents working on the codebase, the gap between "I understood the words" and "I understood what you actually meant" is where most defects originate. A small shared glossary closes the gap:

- The operator brings domain knowledge (business / product / customer language).
- The AI brings code-pattern knowledge.
- This file is the bridge — every term named here is a contract: the AI uses it consistently in code (variables, functions, files, commits), the operator uses it consistently in conversation, and surface drift is treated as a bug.

## Maintenance

- **Populated initially by `/grill-with-docs`** (Pocock skill, in `.claude/skills/` or `.agents/skills/`). The first 5–10 terms emerge from the first alignment session.
- **Grown organically.** Each time a new domain concept surfaces in conversation or code, capture it here. Don't backfill all-at-once — capture-as-you-go.
- **Periodically pruned.** During `/ledger-lint`, scan for terms no longer used in the codebase (they signal dead concepts or rename drift).
- **One concept = one entry.** Synonyms collapse into a single canonical term; document the rejected alternates so the AI doesn't reintroduce them.
- **Scope: project-domain only.** Generic programming terms (function, class, route) don't belong here. Capture only what is specific to *this project's domain*.

## Format

Each entry: **term name** + 1-sentence definition + optional notes on usage / synonyms / examples.

```markdown
### <Term>

<One-sentence definition.>

**Used in:** <where this term appears — code paths, UI surfaces, business rules>
**Synonyms (don't use):** <rejected alternates that mean the same thing>
**Examples:** <2-3 concrete instances if the term is abstract>
```

Keep definitions terse. If a term needs more than 3 sentences, it likely belongs in `docs/ARCHITECTURE.md` or a `docs/adr/` entry, not here.

---

## Terms

`[Empty at init. Populated by /grill-with-docs first run.]`

`[Examples of what good entries look like for different project shapes:`

`Example — financial SaaS:`
```markdown
### Portfolio

A user-owned collection of investment positions; the top-level entity scoped to a single user.

**Used in:** schema (Portfolios table), all action files in src/actions/portfolio/, dashboard route.
**Synonyms (don't use):** "account" (collides with auth/Accounts table), "wallet" (suggests crypto, misleading).
**Examples:** "My Retirement," "College Fund 2030," "Speculative."
```

`Example — content/CMS:`
```markdown
### Edition

A point-in-time published snapshot of a piece. Editions are immutable once published; new edits create a new draft, not a mutation of the published edition.

**Used in:** Editions table, /pub/[slug]/[edition-id] route, edition-diff component.
**Synonyms (don't use):** "version" (overloaded with package versioning), "revision" (used in drafts).
**Examples:** edition_2026_05, edition_2026_06_corrected.
```

`Example — multi-tenant B2B tool:`
```markdown
### Workspace

A multi-tenant boundary; every domain entity belongs to exactly one Workspace. Tenant resolution is single-entry via WorkspaceContext at request handling.

**Used in:** every action file (workspace_id scoping), middleware/workspace-resolver.ts, RBAC.
**Synonyms (don't use):** "team" (used for sub-groupings within a workspace), "org" (legacy term from v1; renamed).
**Examples:** Workspace IDs are slugified human-readable: "acme-corp," "pilot-customer-2026."
```

`Delete the examples above and the placeholder note when /grill-with-docs populates real terms for this project.]`

---

## Anti-patterns

- **Don't include programming primitives.** `Map`, `Set`, `class` — irrelevant. Domain concepts only.
- **Don't include UI labels.** Button text, copy strings, marketing terms — those live in i18n / copy files.
- **Don't include every entity in the schema.** Only entities that have non-obvious naming, scoping, or invariants worth pinning.
- **Don't write definitions in the abstract.** "A widget is a thing that does X" is useless; "A Widget is the smallest unit a Workspace can bill against" is useful.
- **Don't grow this past two screens.** If it's growing, either the project's domain is genuinely complex (split by sub-domain) or the file is collecting trivia (prune).

---

## Related substrate

- **`AGENTS.md` §6 Build Shared Language** — the agent-side discipline this file implements.
- **`/grill-with-docs`** (Pocock skill) — the writes-this-initially primitive.
- **`/audit` ARCH dimension** — the audit pass checks "domain-language file/folder/identifier naming" against this file.
- **`LEDGER.md` invariants** — domain-shaped invariants reference these terms.
