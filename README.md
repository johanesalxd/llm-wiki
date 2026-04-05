# llm-wiki

An OpenClaw skill that adapts Karpathy's LLM Knowledge Base pattern to the Vader/OpenClaw workspace.

This repo is intentionally small. It is **not** a standalone app or a mini framework. It is:
- a workflow/spec for how the knowledge base should operate
- a deployed `SKILL.md` for OpenClaw
- one useful integrity tool: `scripts/lint.py`
- reference notes for routing and compile conventions

The goal is simple: make knowledge compound over time instead of re-deriving everything from raw documents on every query.

---

## Architecture

This implementation maps the pattern onto Jo's existing memory stack:

```text
L0  ~/clawd/memory/raw/           immutable raw sources
L1  ~/clawd/short-term-memory.md  active working state
L2  ~/clawd/memory/*.md           compiled wiki: project files + dated notes
L3  ~/clawd/MEMORY.md             curated durables, auto-injected
```

### Runtime roles in this setup

For this repo, **Vader / OpenClaw** plays three roles:

1. **Point of ingestion**
   - Jo drops a URL, uploads a file, asks for a Drive fetch, shares a tweet, etc.
   - Vader receives the source and decides how to acquire it.

2. **Orchestrator**
   - Vader chooses the right acquisition tool/skill
   - writes the raw source record into `memory/raw/`
   - compiles relevant insights into L1/L2 memory files
   - runs lint when needed

3. **Query engine**
   - Vader answers against the compiled memory substrate using direct reads, `memory_search`, raw files, project files, and dated notes.

A future **human-consumption frontend** like Obsidian may be added later, but it is **not** required for the current architecture.

### High-level flow

```mermaid
flowchart TD
    A[Jo drops link / file / blob / task / source] --> B[Vader intake triage]

    B -->|Source is good enough| C[Direct ingest]
    B -->|Needs a little more context| D[Quick context pass first]
    B -->|Use formal Light Analysis protocol| E[Light Analysis skill first]
    B -->|Use formal Deep Analysis protocol| F[Deep Analysis skill first]
    B -->|Action item only| G[Not wiki / action-only]

    E --> H[Follow ~/clawd/skills/deep-analysis/SKILL.md]
    F --> H

    C --> I[Acquire source with the right tool]
    I --> J[Write raw record into memory/raw]
    J --> K[Compile into L2 memory]
    K --> L[Run lint when needed]
    L --> M[Query against compiled wiki]

    D --> N[Clarify context and choose canonical source(s)]
    N --> C

    H --> O[Produce structured analysis]
    O --> P[Promote durable sources or synthesis into llm-wiki]
    P --> J

    G --> Q[Execute / track normally]

    M --> R[Optional future file-back of durable query outputs]
```

This diagram is intentionally aligned with `SKILL.md`, which is the source of truth for behavior.

### Model policy

Standard llm-wiki work is limited to:
- `gpt54min`
- `sonnet`

Use one of those two by default for ingestion, orchestration, query, compile, and lint review work around the wiki. This is a safety/quality guardrail to keep the memory substrate from drifting under weaker models.

Do not downgrade llm-wiki work to cheaper/weaker models unless Jo explicitly asks.

---

## Operating model

There are five distinct concepts in this system:

### Pre-ingest triage
Before any ingest, Vader decides the right processing depth:
- **direct ingest** when the source is already canonical enough
- **quick context pass first** when context is incomplete and the best source still needs to be identified
- **formal Light Analysis protocol first** when the named Light Analysis mode should be used
- **formal Deep Analysis protocol first** when the named Deep Analysis mode should be used
- **not wiki / action-only** when the item is really just a task or reminder

Important distinction:
- **quick context pass** is a lightweight triage/synthesis step and is **not** the formal Light Analysis protocol
- formal **Light Analysis** / **Deep Analysis** are governed by `~/clawd/skills/deep-analysis/SKILL.md`

Dropping a source into chat does not mean it should be ingested blindly.

### 1. Acquisition
Turn an external source into usable text, images, or extracted content.

Typical upstream tools:
- `web_fetch` for articles/docs/pages
- `bird thread <url>` for X / Twitter
- `gemini-pdf-analyzer` for PDFs
- `vision-sandbox` for images/screenshots
- `summarize` for YouTube
- `notebooklm` for NotebookLM notebooks

These are **acquisition tools**, not the wiki itself.

### 2. Ingest
Create a raw source record in:

```text
~/clawd/memory/raw/YYYY-MM-DD-<slug>.md
```

This preserves the source material in a stable, inspectable markdown form.

### 3. Compile
Integrate the source into the persistent wiki layer:
- update relevant `memory/project-*.md` files
- or update a dated note in `memory/YYYY-MM-DD.md`
- add backlinks to the raw source
- flag contradictions explicitly
- update source metadata and the append-only log

### 4. Lint
Run a read-only integrity audit over the wiki:
- uncompiled raw sources
- stale compiled sources
- unresolved contradiction flags
- uncited L2 sections
- orphaned log entries
- compiled files with no L2 backlinks

This is **not** Spa Day.

- **llm-wiki lint** = research/wiki integrity
- **Spa Day** = OpenClaw/context/system hygiene

### 5. Query
Ask questions against the compiled memory substrate.

In this adaptation, the query runtime is Vader/OpenClaw itself. The answers are generated from the layered markdown memory system, not from a separate vector product or app.

---

## What this repo currently includes

```text
llm-wiki/
  README.md
  SKILL.md
  pyproject.toml
  scripts/
    lint.py
  references/
    source-routing.md
    compile-conventions.md
  .opencode/
    plans/
```

### Included
- `SKILL.md` — operational protocol for ingest / compile / lint
- `scripts/lint.py` — read-only wiki integrity checker
- `references/source-routing.md` — source acquisition routing guidance
- `references/compile-conventions.md` — how to integrate raw sources into L2
- `.opencode/plans/` — historical design decisions and build plans

### Not included
- no helper ingest script
- no helper compile script
- no Obsidian integration yet
- no dedicated `index.md` catalog yet
- no standardized query-output filing workflow yet

That is deliberate. The repo is currently a **protocol + linter**, not a full product.

---

## Why only `lint.py` remains

Earlier versions included helper scripts for ingest and pre-compile inspection.
Those were removed because they added friction without adding real capability.

- ingest is better handled directly by Vader/OpenClaw using native tools
- compile targeting is judgment-heavy and better handled by the agent directly
- linting benefits from a script because it scans many files mechanically and consistently

So the current repo keeps only the part that is truly worth scripting.

---

## Current status

- layer mapping is established
- skill is deployed to `~/clawd/skills/llm-wiki/SKILL.md`
- helper scripts were simplified away
- `lint.py` remains as the only script
- first real end-to-end validation is **still pending**

The next meaningful milestone is:
1. ingest one real source
2. compile it into L1/L2
3. run lint
4. review backlinks + log integrity

---

## Design notes vs Karpathy reference

Compared to the original LLM wiki pattern, this repo is strongest on:
- immutable raw source separation
- schema/protocol discipline
- contradiction tracking
- append-only history
- compatibility with an existing memory system

It is currently weaker on:
- a first-class `index.md` content catalog
- a standardized query-output filing loop
- a human browsing frontend like Obsidian

That is acceptable for now. The current objective is to validate the workflow with real sources before adding more surface area.

---

## Quick reference

- Runtime skill entrypoint:
  - `~/clawd/skills/llm-wiki/SKILL.md`
- Repo root:
  - `~/Developer/git/llm-wiki/`
- Raw source layer:
  - `~/clawd/memory/raw/`
- Main integrity tool:
  - `python3 /Users/johanesalxd/Developer/git/llm-wiki/scripts/lint.py`

---

## Bottom line

This repo is the operating manual for an LLM-maintained knowledge base inside OpenClaw.

Jo curates sources and asks questions.
Vader acquires, compiles, cross-references, and audits.
The markdown memory layers become the persistent knowledge substrate.
