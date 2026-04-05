# Plan: Simplify llm-wiki — Drop ingest.py + compile_helper.py

**Date:** 2026-04-05
**Author:** Vader
**Status:** APPROVED — executing

## Reasoning

The llm-wiki build over-engineered the helper layer. Two of three scripts are dead weight:

- `ingest.py` — 200 lines to write a stub .md file and append one log line. Vader can do this natively with the `write` tool. No exec approval needed, no allowlist friction.
- `compile_helper.py` — reads frontmatter and suggests L2 targets based on tags. Vader reads files directly and applies judgment. No value-add.
- `lint.py` — scans 20+ files for frontmatter patterns, orphans, backlink integrity, contradiction flags. This has real value. Keeping it.

Using yolo/subagent for ingest+compile was considered and rejected: these are sequential, single-file operations — subagents are for parallel read/compute work. Main handles them natively with zero friction.

## Changes

### 1. Delete scripts
- `scripts/ingest.py` — remove
- `scripts/compile_helper.py` — remove
- `scripts/lint.py` — keep untouched

### 2. Rewrite SKILL.md
- **Ingest procedure:** replace `ingest.py` call with native tool steps (write stub directly, append log.md directly)
- **Compile procedure:** replace `compile_helper.py` call with native read steps (read the raw file, check projects.md, identify L2 targets using judgment)
- **Lint section:** keep unchanged (still references `lint.py`)
- Remove the script path header note (no longer relevant to ingest/compile)
- Update pyproject.toml scripts entry to remove deleted scripts

### 3. Update pyproject.toml
- Remove `ingest` and `compile-helper` script entries
- Keep `lint` entry

### 4. Git commit
- Branch: `chore/simplify-scripts`
- Commit: `chore: drop ingest.py and compile_helper.py, use native tools`

## What does NOT change
- `scripts/lint.py` — untouched
- `references/` — untouched
- `memory/raw/` conventions — untouched
- Frontmatter schema — untouched
- Log.md format — untouched
