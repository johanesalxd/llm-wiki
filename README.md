# llm-wiki

A markdown-first knowledge base pattern built around **OpenClaw** as the runtime and **Obsidian** as the human-facing read layer.

This repo is intentionally small. It is **not** a standalone app or vector database. It is:
- a workflow/spec for how a long-lived markdown knowledge base should operate
- a public `SKILL.md` for agent runtimes
- one useful integrity tool: `scripts/lint.py`
- a few reference files for routing and compile conventions

The goal is simple: **make knowledge compound over time instead of re-deriving everything from raw documents on every query.**

> Further OpenClaw background: if you want the broader design context behind this setup, read Jo's OpenClaw guide here — https://github.com/johanesalxd/random-stuff/blob/main/others/openclaw/openclaw-anthropic-guide.md

---

## What this system assumes

This repo reflects a working setup where:
- **OpenClaw** handles ingestion, orchestration, and query
- **Obsidian** is a read-only human mirror for browsing the knowledge base
- the knowledge base itself is a set of layered markdown files

The architecture is not secret or proprietary. The local/private deployment may have different paths and workspace-specific conventions, but the core operating model is public and reusable.

---

## Reference

This repo is inspired by:
- Andrej Karpathy, *A pattern for building personal knowledge bases using LLMs*
- https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

---

## Tiered memory architecture

The system uses a four-layer markdown memory stack.

```text
L0  memory/raw/           immutable source records
L1  short-term-memory.md  active working state / session tracking
L2  memory/               compiled project files, dated notes, and indexes
L3  MEMORY.md             curated durable memory
```

### L0 — Raw sources
Raw records preserve source fidelity.

Examples:
- articles fetched from the web
- PDF extraction output
- image-analysis output
- YouTube source shell + transcript companion
- X/Twitter thread captures

This is the layer you fall back to when you need:
- original wording
- provenance
- missing detail
- contradiction checks

### L1 — Short-term memory
Short-term memory is the active working layer.

It tracks:
- open fronts
- in-progress tasks
- session-level active state

This is not the main llm-wiki knowledge substrate. It is the current working scratchpad and session/state tracker.

### L2 — Compiled knowledge
This is the main reading and query surface.

Examples:
- `memory/project-*.md`
- `memory/YYYY-MM-DD.md`
- `memory/projects.md`

Most useful answers should come from here first.

### L3 — Curated durables
This is the smallest, highest-signal layer.

It holds:
- durable lessons
- long-lived decisions
- preferences and stable operating constraints

In an OpenClaw setup, `MEMORY.md` is a built-in durable memory surface.

---

## OpenClaw + Obsidian roles

The same knowledge base is accessed in two different ways.

### OpenClaw
OpenClaw is the runtime.

It plays three roles:
1. **Point of ingestion**
   - receives URLs, files, blobs, and references
2. **Orchestrator**
   - chooses the right acquisition tool
   - writes raw records
   - compiles useful summaries into the wiki
   - runs lint when needed
3. **Query engine**
   - answers against the compiled markdown substrate
   - falls back to raw sources only when necessary

### Obsidian
Obsidian is the human-facing read layer.

Use it to:
- browse project notes
- read dated notes
- inspect raw sources manually
- navigate the knowledge base as markdown

Obsidian is **not** the canonical store and does not drive ingest logic. It is a read-only mirror / consumption layer.

---

## Human view vs agent view

### Human / Obsidian view
A human usually experiences the system like this:
1. open Obsidian
2. read a project file or dated note
3. if needed, drill down into the raw source

### Agent / OpenClaw view
The agent should usually do this instead:
1. start from the compiled layer first
2. answer from project files / dated notes / indexes when sufficient
3. drop into raw only for provenance, exact wording, or missing detail

That asymmetry is intentional.

---

## Ingestion flow: source to query

This is the normal path when a human drops a source into the system.

```mermaid
flowchart TD
    A[User provides link / file / blob / source] --> B[OpenClaw intake triage]

    B -->|Source is good enough| C[Direct ingest]
    B -->|Needs a little more context| D[Quick context pass first]
    B -->|Needs structured judgment| E[Light or Deep Analysis first]
    B -->|Action item only| F[Not wiki / action-only]

    C --> G[Acquire source with the right tool]
    G --> H[Write raw record into L0]
    H --> I[Compile into L2 notes]
    I --> J[Run lint when needed]
    J --> K[Future query starts from L2]

    D --> L[Clarify context and choose canonical source]
    L --> C

    E --> M[Produce structured analysis]
    M --> N[Promote durable sources or synthesis]
    N --> H

    F --> O[Execute or track normally]
```

### Plain-English version
1. **Source arrives**
   - article, PDF, image, YouTube link, X thread, notebook reference, etc.
2. **OpenClaw triages it**
   - direct ingest
   - quick context pass
   - light analysis first
   - deep analysis first
   - or not-wiki / action-only
3. **OpenClaw acquires usable content**
4. **L0 raw record is written**
5. **L2 compiled notes are updated**
6. **Future query starts from the compiled layer**

---

## Query flow: question to summary to raw

This is the reverse path when a human asks a question later.

```mermaid
flowchart TD
    A[User asks a question] --> B[OpenClaw reads L2 first]
    B --> C{Enough detail?}
    C -->|Yes| D[Answer from compiled summary]
    C -->|No| E[Drop to raw source]
    E --> F[Pull provenance / exact wording / missing detail]
    F --> G[Answer with raw-backed context]
    D --> H[Human can inspect same path in Obsidian]
    G --> H
```

### Plain-English version
1. question arrives
2. OpenClaw reads compiled notes first
3. if that is enough, answer from L2
4. if not, fall back to L0 raw sources
5. human can inspect the same markdown trail in Obsidian

---

## YouTube special case

YouTube is the main place where a two-file raw pattern helps.

When transcript/captions are available, preserve **two raw files**:

### 1. Main raw source file
This keeps the canonical shell:
- title
- source URL
- source description
- chapter map / metadata
- acquisition notes
- pointer to transcript companion

### 2. Transcript companion file
This keeps the full-fidelity text:
- full transcript / captions
- backlink to the main raw source

Why split it?
- the main file stays readable in Obsidian
- the transcript remains available for deep query / later recompilation
- long-form videos stop being “chapter map only” stubs

In the OpenClaw-shaped layout used here, those files live under `memory/raw/`.

---

## Analysis surfaces used in practice

This system is not just ingest + query. Sometimes a source needs extra judgment before it should enter the wiki.

### Search
Use search when current context is incomplete and the right source still needs to be found or compared.

Common examples in an OpenClaw setup:
- `web_search`
- `web_fetch`
- `firecrawl`
- repo-specific helpers such as `gemini-search` when used as an external helper (for example: `https://github.com/johanesalxd/gemini-search`)

### Light Analysis
A lighter structured pass before persistence.

Use it when:
- the source/topic needs quick framing
- there are multiple candidate sources
- a little judgment is needed before ingesting

### Deep Analysis
A heavier structured pass before persistence.

Use it when:
- the topic is strategic
- the source is contested or ambiguous
- you want a stronger synthesis before promoting anything into the wiki

In a real OpenClaw deployment, these analysis modes are wrappers around existing acquisition and reasoning tools — not separate storage systems.

---

## What this repo includes

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
    examples.md
```

### Included
- `SKILL.md` — public agent-facing workflow for ingest / compile / lint
- `scripts/lint.py` — read-only wiki integrity checker
- `references/source-routing.md` — source acquisition routing guidance
- `references/compile-conventions.md` — how to integrate raw sources into compiled notes
- `references/examples.md` — concrete examples for stable behavior

### Not included
- no dedicated frontend
- no helper ingest daemon
- no helper compile daemon
- no vector store requirement
- no standardized query-output filing workflow yet

That is deliberate. The repo is currently a **protocol + linter**, not a full product.

One more practical note: the memory architecture described here is intentionally close to a real OpenClaw workspace rather than a fully abstract schema. That makes the repo easier to maintain alongside the local/private skill.

---

## Why only `lint.py` remains

This repo keeps only the part that is clearly worth scripting.

- ingest is usually better handled directly by the agent runtime using native tools
- compile targeting is judgment-heavy and usually better handled by the agent directly
- linting benefits from a script because it scans many files mechanically and consistently

So the current repo automates the part that is truly mechanical and leaves the judgment-heavy parts to the runtime.

---

## Current status

- OpenClaw-first operating model is established
- Obsidian mirror / read layer is a valid human path
- layer mapping (L0-L3) is established
- public `SKILL.md` now mirrors the local/private source of truth much more closely
- workflow has been validated on canonical web and YouTube source patterns
- YouTube ingest is now transcript-first when transcript/captions are available

The next meaningful step is continued real-world use across varied source types, followed by incremental README / UX refinement.

---

## Bottom line

This repo documents a practical pattern:
- **OpenClaw ingests and queries**
- **Obsidian helps humans read**
- **raw sources preserve fidelity**
- **compiled notes become the main knowledge surface**
- **lint protects integrity drift over time**

That is the whole point: a knowledge base that compounds instead of evaporating between sessions.
