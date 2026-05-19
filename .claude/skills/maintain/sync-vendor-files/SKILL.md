---
name: sync-vendor-files
description: Mirror dual-vendor pack files (AGENTS.md ↔ CLAUDE.md, .claude/skills/ ↔ .agents/skills/) so both Claude Code and Codex see identical pack content. Use after editing pack files in either vendor's location to re-sync the other side.
---

# /sync-vendor-files

Pack ships duplicate content to both vendor paths (`.claude/skills/` for Claude Code, `.agents/skills/` for Codex). This skill mirrors edits between them so both agents stay in lockstep.

## What it mirrors

| Pair | Behavior |
|---|---|
| `AGENTS.md` ↔ `CLAUDE.md` | Newer mtime wins; copies to the older |
| `.claude/skills/<bucket>/<name>/**` ↔ `.agents/skills/<bucket>/<name>/**` | Tree mirror in chosen direction; orphans flagged for manual review |

## What it does NOT mirror

These are **vendor-specific by design** and must be edited per-vendor:

- `.claude/settings.json` (JSON) ↔ `.codex/config.toml` (TOML) — different schemas, equivalent function
- `.claudeignore` (path-based) ↔ `[permissions.default.filesystem]` entries in `.codex/config.toml` (config-based) — equivalent ignore effect, different mechanism

If you change a stop-hook or an ignore pattern, you must update **both** files manually (or use the AI to translate JSON → TOML and `.claudeignore` lines → `[permissions.default.filesystem]` entries).

## How to use

1. **Default (auto-direction)** — detects which side has the most recent edits and mirrors that side to the other:
   ```bash
   python .claude/skills/maintain/sync-vendor-files/sync.py
   ```

2. **Explicit direction** — force one side as the source:
   ```bash
   python .claude/skills/maintain/sync-vendor-files/sync.py --direction agents-to-claude
   python .claude/skills/maintain/sync-vendor-files/sync.py --direction claude-to-agents
   ```

3. **Dry-run first** — see what would change without writing:
   ```bash
   python .claude/skills/maintain/sync-vendor-files/sync.py --dry-run
   ```

If running on Codex, the script path is identical but lives at `.agents/skills/maintain/sync-vendor-files/sync.py` — both vendor copies of `sync.py` are byte-identical.

## When to invoke

- **After you edit a SKILL.md or AGENTS.md / CLAUDE.md in one vendor location** and want the other vendor's path to match
- **As a precommit step** when you're about to push pack changes that should land symmetrically on both vendors
- **Periodically** (e.g., as part of `/ledger-lint`'s biweekly cadence) — `--dry-run` first to verify the pack is symmetric, then promote any drift

## When NOT to invoke

- **Mid-edit on the side you're about to overwrite** — let your in-progress edit complete and save first
- **When you're editing `.claude/settings.json` or `.codex/config.toml`** — they're vendor-specific; the sync skips them
- **When both sides have diverged significantly** — auto-direction will pick one side and overwrite the other. If you've edited *both* sides independently (e.g., CC session edited the CC skill while a Codex session edited the Codex skill), reconcile manually before running

## What success looks like

```
Project root: C:\path\to\your-project
Mode: WRITE

--- Substrate (AGENTS.md ↔ CLAUDE.md) ---
substrate: already in sync (AGENTS.md == CLAUDE.md)

--- Skills tree (.claude/skills/ ↔ .agents/skills/) ---
Auto-detected direction (newer side wins): claude-to-agents
tree-mirror: copied build/tdd/SKILL.md
tree-mirror: copied build/diagnose/SKILL.md
Skills: 2 file(s) mirrored

Done.

NOT mirrored (vendor-specific formats — edit per-vendor):
  .claude/settings.json  ↔  .codex/config.toml
  .claudeignore          ↔  [permissions.default.filesystem] entries in .codex/config.toml
```

## Pack calibration

This skill is **the recommended mechanism** when you've edited one vendor side and want a quick re-mirror.

For everyday edits, the simpler natural-language path also works: tell Claude/Codex *"mirror this change to the other vendor's skill directory and to the other substrate file."* The script is the deterministic fallback when you want to be sure the entire tree is symmetric.

## Related

- [[../../../../README.md]] — pack README documents the dual-vendor design and sync discipline
- [[../../../../MAINTAINING.md]] — pack maintenance discipline (this skill is the operational arm of the duplication design)
