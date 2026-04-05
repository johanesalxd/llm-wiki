# Plan 002 — llm-wiki v2

## Task slug
llm-wiki-v2

## Context
v1 build is complete and deployed. This plan addresses all critical and minor issues found in the @explore pass (2026-04-05), plus the agreed v2 feature wishlist. All files exist in `/Users/johanesalxd/Developer/git/llm-wiki/`.

## Issues to fix (from explore findings)

### Critical
- **C1 (NOT AN ISSUE — RESOLVED):** `summarize` is a bundled OpenClaw skill (not a local `~/clawd/skills/` skill). It resolves at runtime via OpenClaw's skill registry. The reference in SKILL.md and source-routing.md is correct as-is. No code change needed. However: add a clarifying note in SKILL.md and source-routing.md that skill references fall into three categories: (1) local skills in `~/clawd/skills/`, (2) bundled OpenClaw skills (e.g. `summarize`, `blogwatcher`), and (3) extra/extension skills. Agents should not assume all skills live in `~/clawd/skills/`.
- **C2:** Frontmatter multi-line YAML block list (`compiled_into:` with `- item` lines) not parsed by `lint.py` or `compile_helper.py`. Fix: update `parse_frontmatter()` in both scripts to handle multi-line YAML lists. Also update `compile-conventions.md` to show inline list format `compiled_into: ["file1.md", "file2.md"]` as the canonical format (matching what `ingest.py` already writes).

### Minor
- **M1:** NLM source type not auto-detectable. Add a clear note to `source-routing.md` that NLM sources require `--type nlm` flag explicitly. Update the "Gotchas" section in SKILL.md.
- **M2:** YouTube URLs produce weak slug `watch`. Add note to `source-routing.md` recommending `--slug <meaningful-name>` for all YouTube URLs.
- **M3:** Log.md titles are placeholder-derived, never corrected. Relax the "append-only" rule slightly: agent MAY update the title field of the most recent log entry immediately after fetching the real source title. Document this in SKILL.md compile step.
- **M4:** No duplicate detection in `ingest.py`. Add idempotency check: before writing, check if `<date>-<slug>.md` already exists in `memory/raw/`. If so, print a warning and exit unless `--force` flag is passed.
- **M5:** `projects.md` update step missing from SKILL.md compile procedure. Add it to the compile checklist in SKILL.md.
- **M6:** Script path ambiguity in SKILL.md. Add a note that all script commands run from repo root (`~/Developer/git/llm-wiki/`), or use full absolute paths.
- **M7:** `.ruff_cache/` in repo root without pyproject.toml. Add a minimal `pyproject.toml` with ruff config for the scripts directory.

## V2 Features (from wishlist)

### V2-1: Auto-ingest trigger notes in SKILL.md
Add a new section to SKILL.md: **"Auto-ingest (Vader-triggered)"** — documents the convention that when Jo drops a URL or file in conversation, Vader should automatically call `python3 /Users/johanesalxd/Developer/git/llm-wiki/scripts/ingest.py <url>` without being asked. This is a behavioral note for the orchestrator, not a code change.

### V2-2: Cron lint note in SKILL.md
Add a section: **"Lint schedule"** — documents recommended weekly lint run. Include the exact cron-friendly command: `python3 /Users/johanesalxd/Developer/git/llm-wiki/scripts/lint.py --output /tmp/llm-wiki-lint-$(date +%Y%m%d).md`. Note that this can be wired into a cron job by Jo.

### V2-3: NLM skill name fix
Update all references from `nlm` skill to `notebooklm` (the actual installed skill name). Affected files: SKILL.md, source-routing.md.

### V2-4: log.md integrity check in lint.py
Add a 5th lint check: verify that each log entry's slug has a corresponding raw file on disk. Print warning for orphaned log entries (log entry exists but no raw file). Non-blocking warning, not an error.

### V2-5: projects.md update verification in lint.py
Add a 6th lint check: for each file in `memory/raw/` with `compiled: true`, check that at least one `memory/project-*.md` file contains a backlink (`Source: memory/raw/<slug>`) OR a dated memory file does. Flag compiled files with no backlinks in any L2 file as potential orphans post-compile.

## Deliverables

Write the following files to the current working directory (`/Users/johanesalxd/Developer/git/llm-wiki`):

### 1. `scripts/ingest.py` — updated
- Add duplicate detection: check if `<YYYY-MM-DD>-<slug>.md` already exists before writing. If exists, print warning and exit unless `--force` flag passed.
- No other changes to existing logic.

### 2. `scripts/lint.py` — updated
- Fix `parse_frontmatter()` to handle multi-line YAML block lists. When a line is `key:` with no inline value, read subsequent lines that start with `- ` as list items, accumulate them, and return as a Python list.
- Add **Check 5 (log integrity):** scan `log.md` entries, extract slug from each entry, verify corresponding raw file exists. Print warnings for orphaned log entries.
- Add **Check 6 (post-compile backlink verification):** for each raw file with `compiled: true`, scan L2 memory files for `Source: memory/raw/<slug>` backlink. Flag compiled files with no backlinks found anywhere.

### 3. `scripts/compile_helper.py` — updated
- Fix `parse_frontmatter()` with same multi-line YAML list fix as lint.py (share the fix — same function signature, same logic).
- Add `--date` flag: when multiple raw files match a slug across different dates, `--date YYYY-MM-DD` selects a specific one. Without flag, still returns most recent.

### 4. `SKILL.md` — updated
Add/update the following sections:
- **Ingest → NLM note:** add gotcha that NLM sources require `--type nlm` flag.
- **Ingest → YouTube note:** add note recommending `--slug <name>` for YouTube URLs.
- **Compile → procedure:** add `projects.md` update step and the log title correction note.
- **Compile → script paths note:** add note that all commands run from `~/Developer/git/llm-wiki/`.
- **New section: Auto-ingest (Vader-triggered):** document the behavioral convention for auto-ingest when Jo drops a URL.
- **New section: Lint schedule:** document weekly lint run command with absolute paths.
- Add skill taxonomy note: clarify that skills fall into three categories — (1) local `~/clawd/skills/`, (2) bundled OpenClaw skills (e.g. `summarize`, `blogwatcher` at `~/.local/share/mise/installs/node/24.13.0/lib/node_modules/openclaw/skills/`), (3) extras. Agents should check all locations, not just local.
- Fix `nlm` skill reference → `notebooklm`.

### 5. `references/source-routing.md` — updated
- Add note under YouTube section: slug weakness with `watch?v=` URLs, recommend `--slug`.
- Add note under NLM section: cannot auto-detect, requires `--type nlm`.
- Add skill taxonomy note (same as SKILL.md above).
- Fix `nlm` skill reference → `notebooklm`.

### 6. `references/compile-conventions.md` — updated
- Update `compiled_into` format: change all examples from YAML block list to inline list `compiled_into: ["memory/project-foo.md", "memory/project-bar.md"]`. Add a note: "Always use inline list format — the lint and compile_helper parsers do not support multi-line YAML block lists."
- Add `projects.md` update step to the compile checklist.

### 7. `pyproject.toml` — new
Minimal ruff config:
```toml
[tool.ruff]
target-version = "py39"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "W"]
```

### 8. `~/clawd/skills/llm-wiki/SKILL.md` — sync
After updating repo `SKILL.md`, copy it to `~/clawd/skills/llm-wiki/SKILL.md` to keep them in sync.

## Post-build steps
After writing all files:
1. Run `python3 scripts/ingest.py --help` — verify `--force` flag appears.
2. Run `python3 scripts/lint.py` — verify 6 checks run (no crash).
3. Run `python3 scripts/compile_helper.py --help` — verify `--date` flag appears.
4. Run `python3 scripts/ingest.py https://youtube.com/watch?v=test123 --dry-run` — verify it suggests `--slug` in output.
5. Verify `~/clawd/skills/llm-wiki/SKILL.md` matches repo `SKILL.md` (diff should be empty).

## Completion
After all files written and post-build steps verified, reply exactly:
LLM-WIKI-V2-BUILD-DONE
