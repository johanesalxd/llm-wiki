# Plan 004 — llm-wiki lint migration awareness

## Task slug
llm-wiki-lint-migration-awareness

## Date
2026-04-05

## Problem
The first real llm-wiki validation passed, but `lint.py` reports 177 orphan L2 sections because it applies the new backlink standard to legacy project memory that predates llm-wiki adoption.

This is noisy and misleading.

## Goal
Make lint migration-aware:
- keep strict checks for llm-wiki-managed content
- report legacy uncited L2 sections separately
- avoid treating the entire pre-wiki corpus as a fresh failure

## Approach

### 1. Introduce adoption-date policy
Use `2026-04-05` as the llm-wiki adoption date for this workspace.

### 2. Reframe orphan-L2 behavior
When a `project-*.md` section has no backlink:
- if the containing file has evidence of llm-wiki-managed content added on/after the adoption date, keep it as a normal orphan-L2 issue
- otherwise treat it as `legacy_uncited_l2` and report it separately as migration backlog

### 3. Update report structure
Split orphan-L2 reporting into:
- **Orphan L2 scan (llm-wiki-managed)** — true current issues
- **Legacy uncited L2 scan** — migration backlog, informative but not a blocker

### 4. Exit-code policy
Do not count legacy uncited sections toward the failing exit code.
Only current llm-wiki-managed issues should fail the run.

## Deliverables
- update `scripts/lint.py`
- rerun lint to `~/clawd/memory/raw/lint-2026-04-05.md`
- confirm the new report distinguishes legacy backlog from true failures
