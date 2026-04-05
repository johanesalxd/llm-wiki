# Plan 003 — llm-wiki v3 architecture alignment

## Task slug
llm-wiki-v3-architecture-alignment

## Date
2026-04-05

## Context
After reviewing the current repo against Karpathy's X threads, gist, and the follow-up architecture diagram, the repo is structurally sound but not yet fully aligned with the actual reference pattern.

Current state:
- The layer mapping is strong: `memory/raw/` (L0), `short-term-memory.md` (L1), `memory/project-*.md` + dated files (L2), `MEMORY.md` (L3)
- `lint.py` is worth keeping
- `ingest.py` and `compile_helper.py` were correctly removed in favor of native OpenClaw tool orchestration
- The repo is still missing a clear articulation of the runtime/orchestrator/query model
- `README.md` is stale and still describes deleted scripts and an outdated quickstart

## Clarified architecture

For Jo's setup, the llm-wiki system is:

1. **Point of ingestion** — Vader/OpenClaw receives links, files, pasted blobs, Drive references, URLs, etc.
2. **Orchestrator** — Vader chooses the correct upstream tool/skill (`web_fetch`, `bird`, `gemini-pdf-analyzer`, `vision-sandbox`, `summarize`, `notebooklm`, etc.), creates raw records, compiles into memory, and runs lint.
3. **Query engine** — Vader/OpenClaw answers against the compiled memory substrate using direct reads, `memory_search`, raw files, project files, and dated notes.
4. **Human consumption layer** — Obsidian is optional and deferred; it is a future frontend for Jo, not a current dependency of the architecture.

This means the repo should describe:
- upstream acquisition tools as acquisition tools (not "the compile layer")
- Vader/OpenClaw as the runtime/orchestrator/query engine
- the wiki as the compiled persistent substrate
- lint as an independent wiki-integrity operation, distinct from Spa Day / OpenClaw maintenance

## Gaps to fix now

### 1. README drift
The README still references deleted scripts and the old helper-driven workflow. It must be rewritten to match the current repo.

### 2. Query layer not explicit enough
The repo currently describes ingest / compile / lint well enough, but it does not clearly explain that OpenClaw/Vader is the runtime/query layer in this adaptation.

### 3. Acquisition vs compile terminology
The repo should distinguish:
- acquisition/extraction tools (`web_fetch`, `bird`, `gemini-pdf-analyzer`, `vision-sandbox`, `summarize`, `notebooklm`)
- ingest (creating the raw source record)
- compile (integrating into L1/L2)
- lint (integrity audit)
- query (answering against compiled memory, with optional filing-back later)

### 4. Current limitations should be explicit
Before testing, the repo should honestly state:
- query-output filing back into the wiki is not yet standardized
- Obsidian is not yet integrated
- `projects.md` currently acts as a project index, not a full wiki-wide `index.md`
- the next milestone is real end-to-end validation, not more abstraction

## Planned repo changes

### A. Update `README.md`
Rewrite it so it:
- reflects the post-simplification reality (only `lint.py` remains)
- describes the four roles above (ingest point, orchestrator, query engine, future frontend)
- introduces the architecture in terms of acquisition / ingest / compile / lint / query
- removes examples using deleted scripts
- states the current repo status honestly: protocol + linter + refs, first real ingestion test pending

### B. Update `SKILL.md`
Refine architecture language:
- explicitly state that Vader/OpenClaw is the runtime for ingestion, orchestration, and query
- separate acquisition tools from compile semantics
- clarify that llm-wiki lint is distinct from Spa Day / OpenClaw maintenance
- add a short current-limitations note if needed

### C. Sync deployed skill copy
Copy updated `SKILL.md` to `~/clawd/skills/llm-wiki/SKILL.md`

### D. Commit on a feature branch
- branch: `docs/llm-wiki-v3-architecture`
- commit message: `docs: align llm-wiki repo with runtime architecture`

## Non-goals for this pass
- no new scripts
- no Obsidian integration
- no `index.md` implementation yet
- no query-output filing mechanism yet
- no first real source ingest yet

## Success criteria
- README no longer mentions deleted helper scripts
- repo language matches current implementation and Jo's intended operating model
- SKILL.md cleanly explains Vader/OpenClaw's role in the system
- branch created under trunk-based dev guidelines
- repo is ready for the first real end-to-end validation
