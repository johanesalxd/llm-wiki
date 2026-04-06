---
name: llm-wiki
description: "LLM Knowledge Base skill — ingest raw sources into a markdown source layer, compile them into project memory files, and lint the wiki for orphans and contradictions. Use when: adding research articles, PDFs, YouTube videos, X threads, or images to a long-lived markdown knowledge base; compiling raw sources into durable project notes; or running a wiki health check. NOT for: generic workspace cleanup, task-only reminders, or one-off context compaction."
---

# llm-wiki skill

Implements Karpathy's LLM Knowledge Base pattern for an agent-maintained markdown knowledge base. Three core wiki operations: **Ingest**, **Compile**, **Lint**.

Reference anchor: Andrej Karpathy, *A pattern for building personal knowledge bases using LLMs* — https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

In this adaptation, the agent plays three roles:
- **point of ingestion** — the user provides a URL, file, blob, or external reference
- **orchestrator** — the agent chooses the right acquisition tool, writes the raw record, compiles it into the wiki, and runs lint when needed
- **query engine** — the agent answers against the compiled markdown substrate using direct reads, search, project files, dated notes, and raw sources

A human-facing mirror or reader layer may exist, but it is not the canonical store and is not required for the core architecture.

## Ingestion depth model

Use this ladder to choose how much processing a source deserves.

- **Depth 0 — Preserve raw only**
  - Use when the source is worth archiving but not yet worth synthesis.
- **Depth 1 — Raw + wiki compression**
  - Default for clean, worthwhile sources.
  - Preserve immutable raw, then add a concise summary to the compiled layer.
- **Depth 2 — Quick context pass + ingest**
  - Use when the source bundle needs light framing or canonical-source selection.
- **Depth 3 — Light Analysis + promote**
  - Use when the topic needs structured judgment before persistence.
- **Depth 4 — Deep Analysis + promote**
  - Use when the topic is strategic, contested, or high-stakes.

Default behavior: choose the lowest depth that preserves long-term value without creating junk.

## Pre-ingest triage

When the user provides a link, file, blob, task item, or source reference, decide the right processing depth **before ingesting anything**.

This is a **pre-ingest** stage, not compile time.

There are five valid outcomes:

1. **Direct ingest**
   - Use when the source is already canonical enough to preserve directly.
   - Example: a clean article URL, gist, PDF, repo README, tweet thread, or notebook reference with obvious long-term value.
   - Path: acquire source -> write raw record -> compile into the wiki.

2. **Quick context pass first**
   - Use when the source is real but context is incomplete, multiple candidate links exist, or the importance is still being established.
   - This is a lightweight triage/synthesis pass only — **not** the formal Light Analysis protocol.
   - Path: quick understanding pass -> choose canonical source(s) -> then ingest what matters.

3. **Formal Light Analysis protocol first**
   - Use when the source/topic warrants a named Light Analysis mode in the current workspace.
   - Path: run the formal Light Analysis protocol first -> then decide which source(s) or conclusions should be ingested.

4. **Formal Deep Analysis protocol first**
   - Use when the topic is strategically important, ambiguous, contested, or valuable enough that a full structured analysis should come before persistence.
   - Path: run the formal Deep Analysis protocol first -> then promote key sources or durable synthesis into the wiki.

5. **Not wiki / action-only**
   - Use when the input is really a task, reminder, or execution request rather than knowledge worth preserving.
   - Path: execute or track normally; do not ingest unless durable knowledge emerges.

### Pre-ingest triage rule

The agent has autonomy to choose the processing strategy. Dropping a source into chat does **not** imply blind ingest.

The governing rule is:
- if the source is already good enough -> ingest it
- if the source needs just a little more context -> do a quick context pass first
- if the source/topic warrants a formal analysis protocol -> use that first
- if it is just an action item -> do not force it into the wiki

Formal analysis may arise not only from dropped links/files but also from the live conversation itself.

## Ingest

Add a new source to the knowledge base.

### Acquisition vs ingest

Do not confuse **acquisition** with **ingest**.

- **Acquisition** = use the right upstream tool or skill to extract the source content
- **Ingest** = write the resulting source record into the raw layer

The tools in the routing table below are acquisition tools. The wiki protocol begins once the source is captured into the raw layer.

### Source type detection

| Source | Detection | Tool |
|---|---|---|
| Web URL (article/blog/doc) | starts with `http`/`https` | `web_fetch` |
| PDF | `.pdf` extension or URL | PDF analysis tool or skill |
| Image / screenshot | `.png`/`.jpg`/`.webp` | vision or image-analysis tool |
| YouTube URL | `youtube.com` or `youtu.be` | summarization/transcript tool |
| X/Twitter thread | `x.com` or `twitter.com` | thread extraction tool |
| NotebookLM notebook | notebook name or share link | NotebookLM tool or adapter |

### Ingest procedure

1. Detect source type from the URL pattern or file extension (see `references/source-routing.md` for edge cases).
2. Call the appropriate tool to fetch, summarize, or extract the source content.
3. For YouTube sources, do a minimal acquisition pass first so the agent can identify the video properly before naming it. Do not preserve raw YouTube IDs or guess from the URL alone.
4. Derive a slug from the confirmed source title: kebab-case, max 6 words. For YouTube `watch?v=` or `youtu.be` URLs, do not auto-derive from the URL token; use the confirmed title/topic after the minimal acquisition pass, and ask the user only if the title still leaves the slug ambiguous.
5. Write the stub file directly into the raw layer using this filename shape:
   ```
   raw/YYYY-MM-DD-<slug>.md
   ```
   The file should include frontmatter like:
   ```yaml
   ---
   title: <source title>
   source_url: <original URL or file path>
   source_type: web|pdf|image|youtube|twitter|nlm
   date_ingested: YYYY-MM-DD
   compiled: false
   compiled_into: []
   tags: []
   ---
   ```
6. Append an entry to the raw-layer log in this format:
   ```
   ## [YYYY-MM-DD] ingest | <source-title> | <source-type> | <slug>
   ```
   The log is append-only — never edit existing entries.

### Ingest gotchas

- **NotebookLM sources:** They are often ambiguous from the initial input alone. Confirm the notebook identifier or share link if needed.
- **YouTube URLs:** Standard `watch?v=` or `youtu.be` URLs produce a useless slug. Default behavior is: minimal acquisition pass first -> confirm what the video actually is -> choose a meaningful slug -> write raw. Ask the user only if the title/topic still leaves the slug ambiguous.

## YouTube intake protocol

Use this for `youtube.com` or `youtu.be` sources.

1. Run a **minimal acquisition pass first** to obtain transcript, captions, or a stable description.
2. Confirm what the video actually is before naming it.
3. Choose a meaningful slug from the confirmed title/topic.
4. Write the immutable raw record in the raw layer.
5. Decide compile depth and compile destination after the source is identified.
6. Ask the user only if title/topic ambiguity still remains after minimal acquisition.

Rule: **raw-first, but not blind**. Do not preserve bare YouTube IDs as if they were meaningful knowledge artifacts.

## Compile

Integrate a raw source into the compiled wiki layer.

### Compile procedure

1. Read the target raw file in full.
2. Check its frontmatter: `compiled` status, `tags`, `source_type`.
3. Identify which compiled files are relevant:
   - read the project index
   - scan existing project files for topically related sections
   - if no project file matches, use a dated note
4. Route using judgment, not rigid user micromanagement:
   - update an existing project file when the source clearly extends an active topic
   - create a new project file when the topic is distinct and likely to attract multiple future sources
   - use a dated note when the source is one-off, low-priority, or not yet clearly durable

### Compile destination rule

Choose the compile destination based on **workspace significance**, not just topic.

Ask:
- Why does this source matter in the current workspace?
- Is it extending domain knowledge, validating a workflow, recording an implementation lesson, or supporting an active project?

Example:
- a video may be about LLMs in general
- but if it primarily validates the wiki's YouTube ingest workflow, the right destination can still be the project file for the wiki itself

5. For each relevant compiled file, add a summary section:
   - Prefer this summary shape when possible:
     - **What it is**
     - **Why it matters here**
     - **Key takeaways**
     - **Routing / usage implication** (for operational sources)
   - Add a backlink: `Source: raw/YYYY-MM-DD-<slug>.md`
   - Note any contradiction with the flag:
     ```
     ⚠️ CONTRADICTION: <description of the contradiction>
     ```
   - Add cross-references where relevant.
6. Update the raw doc's frontmatter:
   ```yaml
   compiled: true
   compiled_date: YYYY-MM-DD
   compiled_into: ["project-foo.md", "project-bar.md"]
   ```
7. Update the project index if new compiled files were created.
8. Append a compile entry to the raw-layer log:
   ```
   ## [YYYY-MM-DD] compile | <slug> | files updated: project-foo.md, project-bar.md
   ```

For detailed conventions on integration, see `references/compile-conventions.md`.

### Post-lint routing and refactoring

Lint may surface structural drift such as:
- mixed-topic project files
- sections that likely belong in a different project file
- durable subsections that deserve promotion into their own project file
- dated notes that should be promoted into project memory

When lint surfaces this signal, treat refactoring as part of the wiki maintenance workflow:
- re-home sections when the topical fit is clear
- split an overloaded project file when a distinct thread has become durable
- promote a recurring subsection into its own project file
- update the project index accordingly

This refactoring is judgment-based.

## Query

Ask questions against the compiled wiki.

The agent is the query runtime. Query work is read-heavy and should prefer the compiled markdown substrate first:

1. Start with the most relevant compiled files.
2. Use search when recall across many markdown files is needed.
3. Read raw files only when the compiled layer is missing detail, provenance, or exact wording.
4. Synthesize answers from the compiled substrate whenever possible instead of re-deriving everything from raw sources.

**Current limitation:** query outputs are not yet standardized as first-class wiki artifacts. If a query produces durable insight worth preserving, route it into normal memory maintenance deliberately instead of inventing an ad hoc format.

## Lint

Wiki health check. Reports problems — never auto-fixes.

This is distinct from generic workspace cleanup.

### Lint checks

**1. Orphan scan**
List all raw-layer files where `compiled: false`. These are uncompiled sources waiting for integration.

**2. Stale scan**
List raw docs where `compiled_date` is more than 30 days ago. These may need re-review if the topic has evolved.

**3. Contradiction scan**
Search compiled files for `⚠️ CONTRADICTION:` strings that have not been followed by a resolution note. These require human judgment.

**4. Orphan compiled-section scan**
Find compiled sections that have no `Source: raw/...` backlink.

**5. Log integrity scan**
Verify that each log entry's slug has a corresponding raw file on disk.

**6. Post-compile backlink check**
For each raw file with `compiled: true`, verify that at least one compiled file contains the expected backlink.

### Running lint

```sh
# Print report to terminal
python3 scripts/lint.py

# Save report to file
python3 scripts/lint.py --output /tmp/llm-wiki-lint-YYYYMMDD.md
```

Lint output is a markdown report. Review it and decide which issues to action — no automatic changes are made.

### Lint cadence

Do not run lint after every clean ingest by default.

Prefer lint:
- after a batch of ingests
- after structural refactors or file re-homing
- when integrity drift is suspected
- on a regular weekly maintenance cadence

## Auto-ingest

When the user drops a URL or file path into conversation without an explicit instruction, the agent may automatically trigger intake and ingest.

Exception: if the source identifier is ambiguous, resolve the ambiguity first instead of guessing.

Do not interpret every dropped URL as a guaranteed persistence request. Default to **intake triage first**; ingest automatically only when the source is clearly worth preserving under the chosen depth.

## Conventions

### Suggested file layout

```text
workspace/
  raw/                immutable source stubs
    log.md            append-only ingest/compile log
    YYYY-MM-DD-<slug>.md
  project-*.md        compiled project knowledge files
  YYYY-MM-DD.md       compiled dated notes
  projects.md         project index
```

### Raw file frontmatter (required)

```yaml
---
title: <source title>
source_url: <original URL or file path>
source_type: web|pdf|image|youtube|twitter|nlm
date_ingested: YYYY-MM-DD
compiled: true|false
compiled_date: YYYY-MM-DD   # omit if not yet compiled
compiled_into: []            # inline list of compiled files updated
tags: []                     # optional topic tags
---
```

### Rules

- Filename format: `YYYY-MM-DD-<kebab-slug>.md` (max 6 words in slug).
- The raw-layer log is **append-only** — never edit existing entries.
- Compile is always **manual or agent-triggered** — never automatic by default.
- Lint is always **report only** — a human decides on fixes.
- Contradiction flags (`⚠️ CONTRADICTION:`) must remain until explicitly resolved.
- `compiled_into` must use **inline list format** — multi-line YAML block lists are not supported by the current lint/parser flow.
