#!/usr/bin/env python3
"""Mirror dual-vendor pack files between Claude Code and Codex paths.

Mirrors:
  - AGENTS.md ↔ CLAUDE.md (substrate, identical content expected)
  - .claude/skills/ ↔ .agents/skills/ (parallel skill trees)

Does NOT mirror:
  - .claude/settings.json ↔ .codex/config.toml (vendor-specific formats)
  - .claudeignore vs [permissions.default.filesystem] (vendor-specific formats)

Usage:
  python sync.py                       # auto-detect direction by newest mtime
  python sync.py --direction agents-to-claude
  python sync.py --direction claude-to-agents
  python sync.py --dry-run             # report intended changes, no writes
"""
from __future__ import annotations
import argparse
import filecmp
import shutil
import sys
from pathlib import Path


def find_project_root(start: Path) -> Path:
    """Walk up until a directory contains AGENTS.md or .git."""
    for parent in [start, *start.parents]:
        if (parent / "AGENTS.md").exists() or (parent / ".git").exists():
            return parent
    raise SystemExit("Could not locate project root (no AGENTS.md or .git found)")


def newer_of(a: Path, b: Path) -> tuple[Path, Path]:
    """Return (newer, older) by mtime; missing-files treated as older."""
    if not a.exists():
        return (b, a)
    if not b.exists():
        return (a, b)
    return (a, b) if a.stat().st_mtime >= b.stat().st_mtime else (b, a)


def sync_pair(a: Path, b: Path, dry_run: bool, label: str) -> bool:
    """Copy newer → older if they differ. Returns True if a change was (or would be) made."""
    if a.exists() and b.exists() and filecmp.cmp(a, b, shallow=False):
        print(f"{label}: already in sync ({a.name} == {b.name})")
        return False
    newer, older = newer_of(a, b)
    if not newer.exists():
        print(f"{label}: SKIP (neither file exists)")
        return False
    if dry_run:
        print(f"[dry-run] {label}: would copy {newer.name} → {older.name}")
    else:
        older.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(newer, older)
        print(f"{label}: copied {newer.name} → {older.name}")
    return True


def sync_tree(src: Path, dst: Path, dry_run: bool) -> int:
    """Mirror src directory tree → dst. Returns count of files changed.

    Flags orphans in dst (files that no longer exist in src) for manual review.
    """
    changes = 0
    if not src.exists():
        print(f"WARN: source tree missing: {src}")
        return 0

    for src_file in src.rglob("*"):
        if src_file.is_file():
            rel = src_file.relative_to(src)
            dst_file = dst / rel
            if dst_file.exists() and filecmp.cmp(src_file, dst_file, shallow=False):
                continue
            if dry_run:
                print(f"[dry-run] tree-mirror: would copy {rel}")
            else:
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dst_file)
                print(f"tree-mirror: copied {rel}")
            changes += 1

    if dst.exists():
        for dst_file in dst.rglob("*"):
            if dst_file.is_file():
                rel = dst_file.relative_to(dst)
                if not (src / rel).exists():
                    print(f"ORPHAN in {dst.relative_to(dst.parent.parent)}: {rel} "
                          "(present in destination but not in source — manual delete may be needed)")

    return changes


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--direction", choices=["auto", "agents-to-claude", "claude-to-agents"],
                   default="auto", help="Sync direction for skills tree (default: auto by mtime)")
    p.add_argument("--dry-run", action="store_true", help="Report intended changes, no writes")
    args = p.parse_args()

    here = Path(__file__).resolve().parent
    root = find_project_root(here)
    print(f"Project root: {root}")
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'WRITE'}")
    print()

    print("--- Substrate (AGENTS.md ↔ CLAUDE.md) ---")
    sync_pair(root / "AGENTS.md", root / "CLAUDE.md", args.dry_run, "substrate")

    print()
    print("--- Skills tree (.claude/skills/ ↔ .agents/skills/) ---")
    claude_skills = root / ".claude" / "skills"
    agents_skills = root / ".agents" / "skills"

    if args.direction == "auto":
        c_newest = max(
            (f.stat().st_mtime for f in claude_skills.rglob("*") if f.is_file()),
            default=0,
        ) if claude_skills.exists() else 0
        a_newest = max(
            (f.stat().st_mtime for f in agents_skills.rglob("*") if f.is_file()),
            default=0,
        ) if agents_skills.exists() else 0
        direction = "claude-to-agents" if c_newest >= a_newest else "agents-to-claude"
        print(f"Auto-detected direction (newer side wins): {direction}")
    else:
        direction = args.direction

    if direction == "claude-to-agents":
        changes = sync_tree(claude_skills, agents_skills, args.dry_run)
    else:
        changes = sync_tree(agents_skills, claude_skills, args.dry_run)

    print(f"Skills: {changes} file(s) {'would be ' if args.dry_run else ''}mirrored")

    print()
    print("Done.")
    print()
    print("NOT mirrored (vendor-specific formats — edit per-vendor):")
    print("  .claude/settings.json  ↔  .codex/config.toml")
    print("  .claudeignore          ↔  [permissions.default.filesystem] entries in .codex/config.toml")
    return 0


if __name__ == "__main__":
    sys.exit(main())
