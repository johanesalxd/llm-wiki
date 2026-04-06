---
name: llm-wiki
description: "LLM Knowledge Base skill — ingest raw sources into a markdown source layer, compile them into project memory files, and lint the wiki for orphans and contradictions. Use when: adding research articles, PDFs, YouTube videos, X threads, or images to a long-lived markdown knowledge base; compiling raw sources into durable project notes; or running a wiki health check. NOT for: generic workspace cleanup, task-only reminders, or one-off context compaction."
---

# llm-wiki skill

> **Public mirror note:** This file is the public mirror of a richer local/private source of truth used in daily operation. Differences should be limited to local paths, workspace-specific filenames, and private runtime details — not the core workflow.

Implements Karpathy's LLM Knowledge Base pattern for an OpenClaw-managed markdown knowledge base. Three core wiki operations: **Ingest**, **Compile**, **Lint**.

This public file mirrors a local/private source of truth, but it intentionally keeps the same OpenClaw-shaped memory architecture:
- `memory/raw/` = L0 raw source layer
- `short-term-memory.md` = L1 active/session state
- `memory/` = L2 compiled project + dated notes
- `MEMORY.md` = L3 curated durables

Reference anchor: Andrej Karpathy, *A pattern for building personal knowledge bases using LLMs* — https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

In this adaptation, **OpenClaw** is the runtime layer:
- **point of ingestion** — the user drops a URL, file, blob, or external reference into chat
- **orchestrator** — the agent chooses the right upstream acquisition tool/skill, writes the raw record, compiles it into memory, and runs lint
- **query engine** — the agent answers against the compiled markdown substrate using direct reads, search, project files, dated notes, and raw sources

Operational default:
- preserve raw first, compile second
- for YouTube, preserve the **full transcript** when available
- for serious long-form YouTube sources, default to a main raw source file plus a `-transcript` companion file
- when the transcript is large or awkward, the `-transcript` companion file is required

**Obsidian** can be used as a human-facing read-only mirror / consumption layer. It is not the canonical store and is not required for the core architecture.

## Model policy

In the reference OpenClaw deployment, standard llm-wiki work is limited to:
- `gpt54min`
- `sonnet`

Adapt that model policy to your own runtime if needed, but keep the bar high enough that the persistent memory substrate stays coherent.

---

## Policy-aware planning

When wiki work touches an **existing corpus** — especially compile, lint, re-ingest, migration, or archive-split work — read the active lint policy before planning:
- `references/lint-policy.md`

Treat that policy as the source of truth for:
- what counts as the **current enforced corpus**
- which files are intentionally **legacy / migration backlog**
- which compile-log suffixes are valid follow-on events

Implications:
- deliberate re-ingestion of the **same source on a new date** may create duplicate-looking raw/log entries; this is acceptable when the new run is a fresh production-era ingest
- the key thing to keep clean is **routing**, not artificial deduplication
- when a testing/archive split exists, new production-era compile output must land in the active production file, not the historical archive

In policy-aware deployments, this is especially important for:
- `enforce_after`
- `legacy_files`
- `compile_event_suffixes`

If you are about to lint, re-ingest canonical sources, or decide whether an apparent duplicate is actually a problem, read the lint policy first.

---

## Ingestion depth model

Use this ladder to choose how much processing a source deserves.

- **Depth 0 — Preserve raw only**
  - Use when the source is worth archiving but not yet worth synthesis.
- **Depth 1 — Raw + wiki compression**
  - Default for clean, worthwhile sources.
  - Preserve immutable raw, then add a concise L2 summary.
- **Depth 2 — Quick context pass + ingest**
  - Use when the source bundle needs light framing or canonical-source selection.
- **Depth 3 — Light Analysis + promote**
  - Use when the topic needs structured judgment before persistence.
- **Depth 4 — Deep Analysis + promote**
  - Use when the topic is strategic, contested, or high-stakes.

Default behavior: choose the lowest depth that preserves long-term value without creating junk.

## Pre-ingest triage

When the user drops a link, file, blob, task item, or source reference into chat, decide the right processing depth **before ingesting anything**.

This is a **pre-ingest** stage, not compile time.

There are five valid outcomes:

1. **Direct ingest**
   - Use when the source is already canonical enough to preserve directly.
   - Example: a clean article URL, gist, PDF, repo README, tweet thread, or notebook reference with obvious long-term value.
   - Path: acquire source -> write raw record -> compile into L2.

2. **Quick context pass first**
   - Use when the source is real but context is incomplete, multiple candidate links exist, or the importance is still being established.
   - This is a lightweight triage/synthesis pass only — **not** the formal Light Analysis protocol.
   - Path: quick understanding pass -> choose canonical source(s) -> then ingest what matters.

3. **Formal Light Analysis protocol first**
   - Use when the source/topic warrants a named Light Analysis mode in the current runtime.
   - Path: run the formal Light Analysis protocol first -> then decide which source(s) or conclusions should be ingested.

4. **Formal Deep Analysis protocol first**
   - Use when the topic is strategically important, ambiguous, contested, or valuable enough that a full structured analysis should come before persistence.
   - Path: run the formal Deep Analysis protocol first -> then promote key sources or durable synthesis into the wiki.

5. **Not wiki / action-only**
   - Use when the input is really a task, reminder, or execution request rather than knowledge worth preserving.
   - Path: execute or track normally; do not ingest unless durable knowledge emerges.

### Pre-ingest triage rule

The agent has autonomy to choose the processing strategy. Dropping a source into chat does **not** imply blind ingest.

Rule:
- source already good enough -> ingest it
- source needs light context -> do a quick context pass first
- source/topic needs structured judgment -> use Light or Deep Analysis first
- action item only -> do not force it into the wiki

Formal Light/Deep Analysis may arise not only from dropped links/files but also from the live conversation itself.

## Ingest

Add a new source to the knowledge base.

### Acquisition vs ingest

Do not confuse **acquisition** with **ingest**.

- **Acquisition** = use the right upstream tool/skill to extract the source content
- **Ingest** = write the resulting source record into `memory/raw/`

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
4. If transcript or caption text is available for a YouTube source, preserve the **full transcript** in the raw layer. Chapter maps and source descriptions are supporting metadata, not substitutes for transcript preservation.
5. Derive a slug from the confirmed source title: kebab-case, max 6 words. For YouTube `watch?v=` or `youtu.be` URLs, do not auto-derive from the URL token; use the confirmed title/topic after the minimal acquisition pass, and ask the user only if the title still leaves the slug ambiguous.
6. Write the raw file directly using the filename shape:
   ```
   memory/raw/YYYY-MM-DD-<slug>.md
   ```
   Use today's date. The file must include this frontmatter at the top, followed by the fetched content body:
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
7. Append an entry to the raw-layer log (create with header if not exists):
   ```
   ## [YYYY-MM-DD] ingest | <source-title> | <source-type> | <slug>
   ```
   The log in `memory/raw/log.md` is append-only — never edit existing entries.

### Ingest gotchas

- **NotebookLM sources:** They are often ambiguous from the initial input alone. Confirm the notebook identifier or share link if needed.
- **YouTube URLs:** Standard `watch?v=` or `youtu.be` URLs produce a useless slug. Default behavior is: minimal acquisition pass first -> confirm what the video actually is -> choose a meaningful slug -> preserve the full transcript if available -> write raw. Ask the user only if the title/topic still leaves the slug ambiguous.

---

## YouTube intake protocol

Use this for `youtube.com` or `youtu.be` sources.

1. Run a **minimal acquisition pass first** to obtain transcript, captions, or a stable description.
2. Confirm what the video actually is before naming it.
3. Choose a meaningful slug from the confirmed title/topic.
4. If transcript/captions are available, preserve the **full transcript** in the raw layer.
5. Store chapter maps, descriptions, timestamps, and acquisition notes as supporting metadata around the transcript — not as a replacement for it.
6. For serious long-form videos, create a companion raw file named `YYYY-MM-DD-<slug>-transcript.md` by default and reference it from the main raw source file. If the transcript is too large or awkward for a single raw file, this companion file is required.
7. Decide compile depth and compile destination after the source is identified.
8. Ask the user only if title/topic ambiguity still remains after minimal acquisition.

Rule: **raw-first, but not blind**. Do not preserve bare YouTube IDs as if they were meaningful knowledge artifacts. For serious long-form videos, transcript-first preservation with the two-file pattern is the default.

### Transcript-driven compile rule

When a YouTube source has a transcript or transcript-companion file, treat the **raw transcript as the canonical source of truth** for compile.

Allowed:
- use summarization tools as a **compression aid** on long transcripts
- use chapter maps and source descriptions as supporting context

Not allowed:
- let a helper summary replace the raw transcript as the basis for compile
- write L2 as if the transcript was reviewed when only the helper summary was reviewed

Quality rule:
- the final L2 write must remain grounded in the raw transcript, even if a summarization tool was used to speed up the first pass
- if the first compile was intentionally shallow for workflow validation, a later transcript-driven compile should be logged explicitly as a second-pass correction

## Compile

Integrate a raw source into L2 memory files.

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

When a source is being **re-run under a new policy boundary**:
- fresh raw/log artifacts on the new date are acceptable
- do not treat same-source/same-slug history across different dates as an automatic error
- use the active lint policy to decide whether the old material is legacy/testing history and where the new compile output belongs
- if the old destination is an explicitly archived testing file, keep new production-era writes out of that archive

5. For each relevant compiled file, add a summary section:
   - Prefer this summary shape when possible:
     - **What it is**
     - **Why it matters here**
     - **Key takeaways**
     - **Routing / usage implication** (for operational sources)
   - Add a backlink: `Source: memory/raw/YYYY-MM-DD-<slug>.md`
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

In this adaptation, OpenClaw is the query engine. Query work is read-heavy and should prefer the compiled markdown substrate first:

1. Start with the most relevant L2 files (`memory/project-*.md`, dated notes, `memory/projects.md`).
2. Use search when recall across many markdown files is needed.
3. Read raw files in `memory/raw/` only when the compiled layer is missing detail, provenance, or exact wording.
4. Synthesize answers from the compiled substrate whenever possible instead of re-deriving everything from raw sources.

**Current limitation:** query outputs are not yet standardized as first-class wiki artifacts. If a query produces durable insight worth preserving, route it into normal memory maintenance deliberately instead of inventing an ad hoc format.

---

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

---

## Auto-ingest

When the user drops a URL or file path into conversation without an explicit instruction, the agent may automatically trigger intake and ingest.

Exception: if the source identifier is ambiguous, resolve the ambiguity first instead of guessing.

Do not interpret every dropped URL as a guaranteed persistence request. Default to **intake triage first**; ingest automatically only when the source is clearly worth preserving under the chosen depth.

---

## Conventions

### Suggested file layout

```text
workspace/
  memory/
    raw/              L0 — immutable source stubs
      log.md          append-only ingest/compile log
      lint-*.md       lint reports (not raw sources)
      YYYY-MM-DD-<slug>.md
    project-*.md      L2 — project knowledge files
    YYYY-MM-DD.md     L2 — dated notes
    projects.md       L2 — project index
  MEMORY.md           L3 — curated durable memory
  short-term-memory.md L1 — active working/session state
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

## Examples reference

For concrete anchors, read:
- `references/examples.md`

Use it when you need a compact example of:
- direct canonical web ingest
- YouTube minimal-acquisition-first ingest with transcript preservation
- not-wiki / action-only rejection

### Rules

- Filename format: `YYYY-MM-DD-<kebab-slug>.md` (max 6 words in slug).
- The raw-layer log is **append-only** — never edit existing entries.
- Compile is always **manual or agent-triggered** — never automatic by default.
- Lint is always **report only** — a human decides on fixes.
- Contradiction flags (`⚠️ CONTRADICTION:`) must remain until explicitly resolved.
- `compiled_into` must use **inline list format** — multi-line YAML block lists are not supported by the current lint/parser flow.
