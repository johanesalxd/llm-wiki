---
enforce_after: 2026-04-07
legacy_files: []
compile_event_suffixes:
  - -second-pass
---

# Lint policy

This file controls **enforcement boundaries** for `scripts/lint.py`.

Why it exists:
- real deployments usually adopt llm-wiki **after** some memory already exists
- old material should not be treated as a fresh lint failure just because backlink discipline was introduced later
- policy should stay visible in markdown instead of being hidden inside code

## Current policy

- **enforce_after:** only content dated on or after this date is treated as part of the current enforced corpus
- **legacy_files:** project files listed here are treated as migration backlog / historical corpus
- **compile_event_suffixes:** compile-log suffixes that describe a valid follow-on compile event rather than a distinct raw filename slug

## How to adapt this repo for another deployment

1. change `enforce_after` to the date when your deployment starts strict llm-wiki enforcement
2. list any pre-existing project files under `legacy_files`
3. add compile-event suffixes only if your workflow deliberately uses them

The linter remains read-only. This policy only changes what is counted as a **current issue** versus a **legacy backlog**.
