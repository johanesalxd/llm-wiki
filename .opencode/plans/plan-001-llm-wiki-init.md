# Plan 001 — llm-wiki init

## Task slug
llm-wiki-init

## Context
Building a new OpenClaw skill called `llm-wiki` that implements Karpathy's LLM Knowledge Base pattern adapted for the Vader/OpenClaw workspace.

The skill sits in two places:
- `~/clawd/skills/llm-wiki/SKILL.md` — OpenClaw skill entrypoint (the file OpenClaw reads)
- `~/Developer/git/llm-wiki/` — the repo (symlinked to `~/llm-wiki`)

The SKILL.md at the repo root and the one at `~/clawd/skills/llm-wiki/SKILL.md` should be the same file (or the skill dir SKILL.md should reference the repo). For now, write SKILL.md at the repo root AND copy/symlink it to `~/clawd/skills/llm-wiki/SKILL.md`.

## Memory architecture context
- `~/clawd/memory/raw/` = L0 layer (immutable source docs, LLM reads only)
- `~/clawd/memory/*.md` = L2 layer (LLM-maintained wiki, project files, dated notes)
- `~/clawd/short-term-memory.md` = L1 (active state)
- `~/clawd/MEMORY.md` = L3 (curated durables, auto-injected)

## Deliverables

Write the following files to the current working directory (`/Users/johanesalxd/Developer/git/llm-wiki`):

### 1. `README.md`
Brief overview of the skill: what it is, the three sections (Ingest/Compile/Lint), how it fits into the tiered memory architecture, and a quickstart example.

### 2. `SKILL.md`
Full OpenClaw SKILL.md with YAML frontmatter. Must include:

**Frontmatter:**
```yaml
---
name: llm-wiki
description: "LLM Knowledge Base skill — ingest raw sources into memory/raw/, compile them into L2 memory files, and lint the wiki for orphans and contradictions. Use when: adding research articles, PDFs, YouTube videos, X threads, or images to the knowledge base; compiling raw sources into project memory files; or running a wiki health check. NOT for: spa day (that's openclaw context optimization), STM/L1 management, or distill-and-flush."
---
```

**Sections:**

#### Ingest
How to ingest a new source. Cover:
- Source type detection table:
  | Source | Detection | Tool |
  |---|---|---|
  | Web URL (article/blog/doc) | starts with http/https | `web_fetch` → save as .md |
  | PDF | .pdf extension or URL | `gemini-pdf-analyzer` skill |
  | Image / screenshot | .png/.jpg/.webp | `vision-sandbox` skill |
  | YouTube URL | youtube.com or youtu.be | `summarize` skill |
  | X/Twitter thread | x.com or twitter.com | `bird thread <url>` |
  | NotebookLM notebook | nlm notebook name | `nlm` skill |
- Output: write compiled `.md` to `~/clawd/memory/raw/<YYYY-MM-DD>-<slug>.md`
- Append entry to `~/clawd/memory/raw/log.md` (create if not exists): `## [YYYY-MM-DD] ingest | <source-title> | <source-type> | <slug>`
- Mark as UNCOMPILED in frontmatter: `compiled: false`

#### Compile
How to compile a raw doc into L2 memory. Cover:
- Read the target `memory/raw/<slug>.md`
- Identify which L2 files are relevant (check `memory/projects.md` index, scan project files)
- Update relevant `memory/project-*.md` or `memory/YYYY-MM-DD.md`:
  - Add a summary section with backlink to raw source
  - Note any contradictions with existing content (flag explicitly: `⚠️ CONTRADICTION:`)
  - Add cross-references where relevant
- Update raw doc frontmatter: `compiled: true`, `compiled_date: YYYY-MM-DD`, `compiled_into: [list of memory files updated]`
- Append compile entry to `~/clawd/memory/raw/log.md`: `## [YYYY-MM-DD] compile | <slug> | files updated: <list>`

#### Lint
Wiki health check. Cover:
- **Orphan scan:** list all `memory/raw/*.md` where `compiled: false` (uncompiled sources)
- **Stale scan:** list raw docs compiled >30 days ago that haven't been referenced in any L2 file recently
- **Contradiction scan:** search L2 files for `⚠️ CONTRADICTION:` flags that haven't been resolved
- **Orphan L2 scan:** find `memory/project-*.md` sections with no backlinks from raw sources (knowledge with no cited source)
- Output: a lint report as markdown, either printed to terminal or saved to `~/clawd/memory/raw/lint-YYYY-MM-DD.md`
- Lint should NOT auto-fix anything — report only, human decides

#### Conventions
- All raw files live in `~/clawd/memory/raw/`
- Filename format: `YYYY-MM-DD-<kebab-slug>.md`
- Required frontmatter for every raw file:
  ```yaml
  ---
  title: <source title>
  source_url: <original URL or file path>
  source_type: web|pdf|image|youtube|twitter|nlm
  date_ingested: YYYY-MM-DD
  compiled: true|false
  compiled_date: YYYY-MM-DD  # omit if not yet compiled
  compiled_into: []           # list of memory files updated
  tags: []                    # optional topic tags
  ---
  ```
- `memory/raw/log.md` is append-only — never edit existing entries
- Compile step is always manual/agent-triggered — never automatic

### 3. `scripts/ingest.py`
A Python helper script that:
- Takes a source URL or file path as CLI argument: `python3 ingest.py <url-or-path> [--slug <slug>] [--tags tag1,tag2]`
- Detects source type based on URL pattern or file extension
- Prints the routing decision: which tool to use and what command to run
- Does NOT call the tool itself (the agent reads the output and calls the tool) — this is a router/planner only
- Writes a stub `memory/raw/YYYY-MM-DD-<slug>.md` with correct frontmatter and `compiled: false`
- Appends the ingest entry to `memory/raw/log.md`
- Uses only stdlib (no external deps) — compatible with `python3` directly

### 4. `scripts/lint.py`
A Python helper script that:
- Scans `~/clawd/memory/raw/*.md` for files with `compiled: false`
- Scans `~/clawd/memory/raw/*.md` for files where `compiled_date` is >30 days ago
- Scans all `~/clawd/memory/*.md` for `⚠️ CONTRADICTION:` strings
- Prints a lint report to stdout (markdown format)
- Optional: `--output <path>` to save report to file
- Uses only stdlib — no external deps

### 5. `scripts/compile_helper.py`
A Python helper script that:
- Takes a raw slug as argument: `python3 compile_helper.py <slug>`
- Reads `~/clawd/memory/raw/YYYY-MM-DD-<slug>.md`
- Prints a compile brief: title, source type, source URL, current compiled status, suggested L2 target files (based on tags if present)
- Used by the agent as a pre-compile check before editing memory files
- Uses only stdlib

### 6. `references/source-routing.md`
Reference table for source type routing — extended version of the table in SKILL.md with examples and edge cases. Cover: URL patterns, file extensions, edge cases (PDFs behind URLs, YouTube playlists vs single videos, X Notes vs tweets, etc.)

### 7. `references/compile-conventions.md`
Detailed conventions for how to integrate raw sources into L2 memory files. Cover:
- When to create a new project file vs update an existing one
- How to write backlinks (format: `Source: memory/raw/YYYY-MM-DD-<slug>.md`)
- How to flag contradictions
- How to handle sources that span multiple topics
- Example before/after of a compile operation

## Post-build steps
After writing all files:
1. Run `python3 scripts/ingest.py --help` to verify CLI works
2. Run `python3 scripts/lint.py` to verify lint script runs (even if memory/raw/ is empty)
3. Run `python3 scripts/compile_helper.py --help` to verify
4. Create `~/clawd/memory/raw/` directory if it doesn't exist: `mkdir -p /Users/johanesalxd/clawd/memory/raw`
5. Create empty `~/clawd/memory/raw/log.md` with header if it doesn't exist
6. Copy SKILL.md to `~/clawd/skills/llm-wiki/SKILL.md`

## Completion
After all files are written and post-build steps verified, reply exactly:
LLM-WIKI-BUILD-DONE
