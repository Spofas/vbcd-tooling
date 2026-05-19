---
name: setup-pre-commit
description: Scaffold a Node/TypeScript pre-commit hook with Tier 1 history-poisoning prevention (gitleaks + large-file check) and Tier 2 fast feedback (Prettier auto-fix, ESLint errors, tsc --noEmit, unit tests with smart-skip on visual-only commits). One-shot at project init.
---

# /setup-pre-commit

**When to invoke:** at project init, exactly once. Sets up Husky + lint-staged + gitleaks + the Tier 1 / Tier 2 hook script. Subsequent commits fire the hook automatically — the skill itself only runs once.

**Why this skill exists:** the pre-commit hook is the only fully-deterministic verification gate in the pack. AGENTS.md tells the agent to verify; this hook makes verification structural — the agent cannot claim "tests pass" without running them, cannot accidentally leak a secret into git history, cannot commit binary blobs that bloat the repo forever. Authored against the first-principles analysis: catch the things git history makes expensive to undo (secrets, large files); provide fast local feedback for everything else (format, lint, types, tests).

## Stack assumption

This skill assumes a **Node/TypeScript** project — `package.json` at repo root, npm / pnpm / yarn / bun as package manager, `tsconfig.json` if TS is in use. The pack is Node-only by design. If the operator invokes this skill on a non-Node project, exit immediately with a brief explanation.

## What gets scaffolded

| Tier | Check | Tool | Behavior |
|---|---|---|---|
| 1 | Secret scan | `gitleaks` | Blocks commit on detected secret. The unique-to-pre-commit leverage point. |
| 1 | Large-file check | shell snippet | Blocks commit on staged files >5MB (configurable). Prevents repo bloat. |
| 2 | Format (auto-fix) | Prettier via lint-staged | Auto-rewrites staged files; never blocks. |
| 2 | Lint errors | ESLint via lint-staged | Blocks on errors (warnings ignored). |
| 2 | Typecheck | `tsc --noEmit` | Whole project typecheck. Blocks on type errors. |
| 2 | Unit tests | `npm test --run` | Runs only if logic files (.ts/.tsx/.js/.jsx/.mjs/.cjs) are staged. Skipped on visual-only commits (CSS/markdown/assets). |
| 3 | Operator extensions | empty by default | Operator adds commitlint / spellcheck / custom validators here. |

Target runtime: **≤15 seconds** for a typical staged change.

## Invocation modes

- `/setup-pre-commit` — **default invocation. Zero questions.** Accepts all defaults: 5MB large-file threshold, no Tier 3 extensions. Aligns with the pack's simplicity principle; operators can always edit `.husky/pre-commit`, `.gitleaks.toml`, or `package.json` directly after scaffolding.
- `/setup-pre-commit --interactive` — opt-in interview for operators who want to customize at scaffold time (set a non-default large-file threshold, declare Tier 3 extensions, surface stack-specific gotchas as they're picked up).

## Protocol

### Step 1 — Detect Node project + verify preconditions

Confirm `package.json` exists at repo root. If not, exit: *"This pack is Node/TypeScript-only. `package.json` not found at repo root."*

Detect:
- **Package manager** from lockfile: `pnpm-lock.yaml` → pnpm, `yarn.lock` → yarn, `bun.lockb` → bun, else npm.
- **TypeScript** from `tsconfig.json` presence.
- **ESLint** from `.eslintrc.*` / `eslint.config.*` presence. If missing, note it — the hook expects ESLint and will fail without it. Surface to operator.

### Step 2 — Interview operator (ONLY if `--interactive`)

**Default behavior (no flag): skip this step entirely.** Use defaults — 5MB large-file threshold, no Tier 3 extensions. Proceed to Step 3.

**If invoked with `--interactive`**, ask these brief questions:
1. *"Large-file threshold? Default 5MB."* — accept a number in MB; convert to bytes.
2. *"Tier 3 operator extensions? Examples: commitlint, cspell. Default: none."* — list of additions, or "none."

The interview is opt-in because the simplicity principle favors zero per-invocation ceremony. Operators who want to customize at scaffold time use `--interactive`; everyone else gets sensible defaults immediately. Either way, the scaffolded artifacts (`.husky/pre-commit`, `.gitleaks.toml`, `package.json` keys) can be edited after the fact.

### Step 3 — Surface `gitleaks` install requirement to operator

`gitleaks` is a system binary, not an npm package. The skill does NOT auto-install it. Surface the per-OS install command and wait for operator confirmation:

- **macOS**: `brew install gitleaks`
- **Windows**: `winget install gitleaks` or `scoop install gitleaks`
- **Linux**: `apt install gitleaks` (Debian/Ubuntu) / download from [releases](https://github.com/gitleaks/gitleaks/releases) / use your distro's package manager

Operator runs the command; skill verifies via `gitleaks version`. If missing, skill proceeds anyway (the hook degrades gracefully — see Step 5 hook script) but flags the gap.

### Step 4 — Install Node devDependencies

Add to `devDependencies` and install:
- `husky`
- `lint-staged`
- `prettier`

Use the detected package manager:
- npm: `npm install --save-dev husky lint-staged prettier`
- pnpm: `pnpm add --save-dev husky lint-staged prettier`
- yarn: `yarn add --dev husky lint-staged prettier`
- bun: `bun add --dev husky lint-staged prettier`

### Step 5 — Initialize Husky and write hook + configs

**Husky init** (creates `.husky/` directory):
```bash
npx husky init  # or pnpm dlx / yarn dlx / bunx
```

**Write `.husky/pre-commit`** (overwrites the default sample):

```bash
#!/usr/bin/env bash
# Pre-commit hook scaffolded by /setup-pre-commit
# Target runtime: ≤15s

set -e
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

# ----- Tier 1: history-poisoning prevention -----

# Secret scan (gitleaks)
if command -v gitleaks >/dev/null 2>&1; then
  echo "→ gitleaks: scanning staged files for secrets..."
  if ! gitleaks protect --staged --redact --no-banner; then
    echo ""
    echo "✗ Secret detected in staged content. Commit blocked."
    echo "  If a real credential leaked: rotate it. The commit didn't land but"
    echo "  the secret may be in your shell history / editor undo buffer."
    echo "  False positive? Add an exception to .gitleaks.toml [allowlists]."
    exit 1
  fi
else
  echo "⚠ gitleaks not installed — secret scan skipped (Tier 1 weakened)."
  echo "  Install: brew install gitleaks / winget install gitleaks / scoop install gitleaks"
fi

# Large-file check (5MB default; override via LARGE_FILE_THRESHOLD env var, in bytes)
LARGE_FILE_THRESHOLD="${LARGE_FILE_THRESHOLD:-5242880}"
LARGE_FILES=""
for FILE in $(git diff --cached --name-only --diff-filter=ACM); do
  if [ -f "$FILE" ]; then
    SIZE=$(wc -c <"$FILE" 2>/dev/null | tr -d ' ')
    if [ -n "$SIZE" ] && [ "$SIZE" -gt "$LARGE_FILE_THRESHOLD" ]; then
      LARGE_FILES="$LARGE_FILES\n  $FILE ($((SIZE / 1024 / 1024))MB)"
    fi
  fi
done
if [ -n "$LARGE_FILES" ]; then
  printf "✗ Large file(s) staged (>%d bytes):" "$LARGE_FILE_THRESHOLD"
  printf "$LARGE_FILES\n"
  echo "  Move to Git LFS (git lfs track '*.ext') or remove from commit."
  echo "  Override (this commit only): LARGE_FILE_THRESHOLD=<bytes> git commit"
  exit 1
fi

# ----- Tier 2: fast feedback -----

# Format + lint (via lint-staged; per-file dispatch on staged files only)
echo "→ lint-staged: format + lint..."
npx lint-staged

# Typecheck (whole project)
echo "→ tsc --noEmit: typecheck..."
npx tsc --noEmit

# Unit tests — only if logic files are staged
LOGIC_EXTS='\.(ts|tsx|js|jsx|mjs|cjs)$'
STAGED=$(git diff --cached --name-only --diff-filter=ACM)
LOGIC_FILES=$(echo "$STAGED" | grep -E "$LOGIC_EXTS" || true)

if [ -n "$LOGIC_FILES" ]; then
  echo "→ npm test --run: unit tests (logic files staged)..."
  npm test --run
else
  echo "→ npm test: skipped (no logic files staged — visual/docs only)"
fi

echo "✓ Pre-commit checks passed."
```

Make it executable: `chmod +x .husky/pre-commit`.

**Write `.gitleaks.toml`** at repo root:

```toml
# Gitleaks configuration
# Extends the default ruleset. Add custom rules or allowlist exceptions below.

[extend]
useDefault = true

# Allowlist: known-safe paths and patterns
[[allowlists]]
description = "Test fixtures, examples, and mocks"
paths = [
  '''(?i)\.env\.example''',
  '''(?i)\.env\.sample''',
  '''(?i)fixtures/.*''',
  '''(?i)__mocks__/.*''',
  '''(?i)test/.*\.ts$''',
  '''(?i)tests/.*\.ts$''',
]

# Add per-secret false-positive exceptions here as they surface.
# Example:
# [[allowlists]]
# description = "Known-safe documentation example"
# regexes = ['''sk_test_FAKE_DOCS_KEY_xxxxxxxxxxxxxxxxxxxxxxxxxx''']
```

### Step 6 — Merge into `package.json`

Prettier and lint-staged configs live as top-level keys in `package.json` (fewer config files in repo root; one source of truth for tooling configuration). Merge three sections:

**`scripts` section** (convenience commands):

```json
{
  "scripts": {
    "prepare": "husky",
    "typecheck": "tsc --noEmit",
    "lint": "eslint . --max-warnings 0",
    "verify": "npm run lint && npm run typecheck && npm test --run"
  }
}
```

The `prepare` script ensures Husky re-installs hooks on every `npm install` (e.g., after a fresh clone).

**Top-level `prettier` key** (skip if `.prettierrc*` already exists at repo root):

```json
{
  "prettier": {
    "semi": true,
    "trailingComma": "all",
    "singleQuote": true,
    "printWidth": 100,
    "tabWidth": 2,
    "useTabs": false
  }
}
```

**Top-level `lint-staged` key** (skip if `lint-staged.config.*` or `.lintstagedrc*` already exists):

```json
{
  "lint-staged": {
    "*.{ts,tsx,js,jsx,mjs,cjs}": [
      "prettier --write",
      "eslint --max-warnings 0 --no-warn-ignored"
    ],
    "*.{css,scss,less}": ["prettier --write"],
    "*.{md,mdx,json,yml,yaml}": ["prettier --write"]
  }
}
```

**Collision handling:** if any key collides with existing values, surface to operator: *"`<key>` already exists in package.json — overwrite (yes), merge non-destructively (default for scripts), or skip (keep existing)?"*

### Step 7 — Verify + CHANGELOG + surface notes

**Verify the hook works.** Stage a no-op change (e.g., touch a comment in any file), then run `npx lint-staged` and `npx tsc --noEmit` manually. Confirm they succeed.

**Add CHANGELOG entry:**

```markdown
### Added

- Pre-commit hook (`/setup-pre-commit`): Tier 1 (gitleaks + large-file check) and Tier 2 (Prettier + ESLint + tsc + unit tests with smart-skip on visual-only commits). Target runtime ≤15s. See `.husky/pre-commit`.
```

**Surface cloud-context reminder** to operator at the end:

```
✓ Pre-commit hook scaffolded.

Notes:
- The hook fires on every `git commit` in local Claude Code or terminal.
- In Cloud Claude Code (web / mobile / GitHub app / remote routines), the hook
  travels with the repo but degrades — sandboxes are iteration-pressured and
  may bypass via --no-verify. Treat your deploy provider's build (Vercel/etc.)
  as the universal non-bypassable gate; this hook is the local-feedback accelerator.
- For agent-side guardrails (blocks dangerous git commands like push --force from
  the agent), install /git-guardrails-claude-code via mattpocock/skills.
- Operator override per-commit: `git commit --no-verify` skips the hook. Discouraged;
  use sparingly for WIP commits or known-intentional broken-state.
```

## Anti-patterns

- **Don't auto-install `gitleaks`.** It's a system binary; the operator's package manager (brew/winget/apt) is the right surface for installing it. Auto-installing would mean shelling out to package managers with elevated privileges — security risk and platform variance. Surface the command, let the operator run it.
- **Don't skip Tier 1 to save time.** Tier 1 is ~1 second total — gitleaks scan on a typical staged diff plus a `wc -c` loop. The unique value of Tier 1 (history-poisoning prevention) is not duplicable at any other layer. Never make these optional.
- **Don't put integration tests in the hook.** Integration tests need DB / secrets / external services. They're slow (10s–minutes), flake-prone, and silently fail in cloud sandboxes without configured secrets. Run them manually or via a dedicated operator-initiated skill. The hook's target runtime (≤15s) assumes only unit tests.
- **Don't widen the test-skip rule beyond logic-file detection.** "If only CSS / docs changed, skip tests" is the right rule. Don't extend to "if only one .ts file changed, run just one test" — that's `vitest --changed` territory and adds complexity for marginal gain.
- **Don't normalize `--no-verify`.** The bypass exists for genuine WIP / known-intentional cases. If the operator finds themselves using it routinely, that's a signal to fix the underlying friction (slow tests, flaky lint), not to keep bypassing.

## Related

- `/git-guardrails-claude-code` (install via `npx skills@latest add mattpocock/skills`) — agent-side complement; blocks dangerous git commands from the agent. Pair with this skill for full coverage.
- AGENTS.md §1 (Goal-Driven Execution) — the principle the hook operationalizes; agent declares success criteria, hook enforces them deterministically. (Anthropic's #1 named practice; §1 by design in the substrate.)
- AGENTS.md §7 (Protect Trunk, Vibe Leaves) — Tier 1 (secrets, large files) protects the trunk's history; nothing else in the pack catches these.
- `/ledger-capture` — when `gitleaks` blocks a commit because of a near-leaked secret, that's a lesson worth capturing. Optionally surface a prompt: *"You almost committed a secret — capture as a lesson?"*
- `/audit` TEST dimension — runs full-suite verification quarterly; complements the per-commit hook with a slower, broader scan.
- `/webapp-testing` — UI-level verification; orthogonal to this hook (which doesn't run E2E tests).

## Invariants

- **Node/TypeScript only.** Skill exits on non-Node projects. The pack is Node-only by design.
- **Tier 1 is never optional.** `gitleaks` + large-file check always run. If `gitleaks` is missing, the hook surfaces a warning but the check is lost — operator must install for full coverage.
- **Target runtime ≤15s.** If real-world hooks exceed this, the operator is one of: running slow tests in the hook (move to manual / dedicated skill), running on a slow machine (accept the cost or invest in faster hardware), or has a pathological test suite (separate problem to fix).
- **Hook is one-shot scaffold.** Skill writes the hook + configs once. Subsequent edits to the hook are operator-managed; the skill doesn't re-run automatically.
- **Smart-skip is conservative.** ANY logic file (.ts/.tsx/.js/.jsx/.mjs/.cjs) staged triggers tests. Only purely non-logic commits (CSS / markdown / assets / configs) skip. False positives (e.g., a `.tsx` change that's "really just visual") are acceptable; false negatives (a logic change that skipped tests) are not.
- **Operator override preserved.** `git commit --no-verify` bypasses. This is git's contract; the skill doesn't try to defeat it. Document its existence and discouragement, then trust the operator.
- **Existing configs preserved.** If `.prettierrc` / `lint-staged.config.js` / `.gitleaks.toml` already exist, the skill surfaces them and asks before overwriting. Defaults to merging where safe, prompting where not.
