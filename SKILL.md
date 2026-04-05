---
name: llm-wiki
description: "LLM Knowledge Base skill — ingest raw sources into memory/raw/, compile them into L2 memory files, and lint the wiki for orphans and contradictions. Use when: adding research articles, PDFs, YouTube videos, X threads, or images to the knowledge base; compiling raw sources into project memory files; or running a wiki health check. NOT for: spa day (that's openclaw context optimization), STM/L1 management, or distill-and-flush."
---

# llm-wiki skill

Implements Karpathy's LLM Knowledge Base pattern for the Vader/OpenClaw workspace. Three core wiki operations: **Ingest**, **Compile**, **Lint**.

In this adaptation, **Vader / OpenClaw** is the runtime layer:
- **point of ingestion** — Jo drops a URL, file, blob, or external reference into chat
- **orchestrator** — Vader chooses the right upstream acquisition tool/skill, writes the raw record, compiles it into memory, and runs lint
- **query engine** — Vader answers against the compiled markdown memory substrate using direct reads, `memory_search`, project files, dated notes, and raw sources

A future Obsidian layer is optional and human-facing only. It is not required for the current architecture.

## Model policy

Standard llm-wiki work is limited to:
- `gpt54min`
- `sonnet`

Use one of these two by default for ingestion, orchestration, query, compile, and lint review around the wiki. This is a quality guardrail for the persistent memory substrate.

Do not downgrade llm-wiki work to cheaper/weaker models unless Jo explicitly asks.

> **Skill taxonomy:** Skills referenced in this file fall into three categories:
> 1. **Local skills** — in `~/clawd/skills/` (e.g. `llm-wiki` itself)
> 2. **Bundled OpenClaw skills** — shipped with OpenClaw at `~/.local/share/mise/installs/node/24.13.0/lib/node_modules/openclaw/skills/` (e.g. `summarize`, `blogwatcher`)
> 3. **Extra/extension skills** — installed separately
>
> Agents must not assume all skills live in `~/clawd/skills/`. Check all three locations if a skill is not found locally.

---

## Ingest

Add a new source to the knowledge base.

### Acquisition vs ingest

Do not confuse **acquisition** with **ingest**.

- **Acquisition** = use the right upstream tool/skill to extract the source content
- **Ingest** = write the resulting source record into `~/clawd/memory/raw/`

The tools in the routing table below are acquisition tools. The wiki protocol begins once the source is captured into the raw layer.

### Source type detection

| Source | Detection | Tool |
|---|---|---|
| Web URL (article/blog/doc) | starts with `http`/`https` | `web_fetch` → save as .md |
| PDF | `.pdf` extension or URL | `gemini-pdf-analyzer` skill |
| Image / screenshot | `.png`/`.jpg`/`.webp` | `vision-sandbox` skill |
| YouTube URL | `youtube.com` or `youtu.be` | `summarize` skill |
| X/Twitter thread | `x.com` or `twitter.com` | `bird thread <url>` |
| NotebookLM notebook | nlm notebook name | `notebooklm` skill |

### Ingest procedure

1. Detect source type from the URL pattern or file extension (see table above; for edge cases see `references/source-routing.md`).
2. Call the appropriate tool to fetch/summarize/extract the source content.
3. Derive a slug from the source title: kebab-case, max 6 words. For YouTube `watch?v=` URLs, always ask Jo for a meaningful slug — auto-derived slug will be useless.
4. Write the stub file directly using the `write` tool:
   ```
   ~/clawd/memory/raw/YYYY-MM-DD-<slug>.md
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
5. Append an entry to `~/clawd/memory/raw/log.md` using the `edit` tool (create with header if not exists):
   ```
   ## [YYYY-MM-DD] ingest | <source-title> | <source-type> | <slug>
   ```
   `log.md` is append-only — never edit existing entries.

### Ingest gotchas

- **NLM / NotebookLM sources:** Cannot auto-detect from a URL or name. Always pass `--type nlm` explicitly, and use `notebooklm` skill (not `nlm`). See `references/source-routing.md` for details.
- **YouTube URLs:** Standard `watch?v=` URLs produce a useless slug. Always confirm a meaningful slug with Jo before ingesting.

---

## Compile

Integrate a raw source into L2 memory files.

### Compile procedure

1. Read the target raw file at `~/clawd/memory/raw/YYYY-MM-DD-<slug>.md` using the `read` tool.
2. Check its frontmatter: `compiled` status, `tags`, `source_type`.
3. Identify which L2 files are relevant:
   - Read `~/clawd/memory/projects.md` index for active projects.
   - Scan `~/clawd/memory/project-*.md` files for topically related sections.
   - If no project file matches, use a dated note: `~/clawd/memory/YYYY-MM-DD.md`.
4. For each relevant L2 file, add a summary section using the `edit` tool:
   - Write a concise summary of the source's key insights.
   - Add a backlink: `Source: memory/raw/YYYY-MM-DD-<slug>.md`
   - Note any contradiction with existing content using the flag:
     ```
     ⚠️ CONTRADICTION: <description of the contradiction>
     ```
   - Add cross-references to related sections where relevant.
5. Update the raw doc's frontmatter using the `edit` tool:
   ```yaml
   compiled: true
   compiled_date: YYYY-MM-DD
   compiled_into: ["memory/project-foo.md", "memory/project-bar.md"]
   ```
   Always use inline list format for `compiled_into` — multi-line YAML block lists are not supported by the lint parser.
6. Update `~/clawd/memory/projects.md` to reflect any new projects or updated project files created during compile.
7. Append a compile entry to `~/clawd/memory/raw/log.md`:
   ```
   ## [YYYY-MM-DD] compile | <slug> | files updated: memory/project-foo.md, memory/project-bar.md
   ```

For detailed conventions on L2 integration (when to create new files, how to handle multi-topic sources, backlink format), see `references/compile-conventions.md`.

---

## Query

Ask questions against the compiled wiki.

In this adaptation, Vader / OpenClaw is the query engine. Query work is read-heavy and should prefer the compiled memory substrate first:

1. Start with the most relevant L2 files (`memory/project-*.md`, dated notes, `memory/projects.md`).
2. Use `memory_search` when recall across `memory/*.md` is needed.
3. Read raw files in `memory/raw/` only when the compiled layer is missing detail, provenance, or exact wording.
4. Synthesize answers from the compiled substrate whenever possible instead of re-deriving everything from raw sources.

**Current limitation:** query outputs are not yet standardized as first-class wiki artifacts. If a query produces durable insight worth preserving, Vader should route it into normal memory maintenance deliberately instead of inventing an ad hoc format.

---

## Lint

Wiki health check. Reports problems — never auto-fixes.

This is distinct from OpenClaw maintenance work such as Spa Day.

- **llm-wiki lint** = research/wiki integrity
- **Spa Day / context optimization** = OpenClaw instruction, memory-surface, and system hygiene

### Lint checks

**1. Orphan scan**
List all `~/clawd/memory/raw/*.md` where `compiled: false`. These are uncompiled sources waiting for integration.

**2. Stale scan**
List raw docs where `compiled_date` is more than 30 days ago. These may need re-review if the topic has evolved.

**3. Contradiction scan**
Search all `~/clawd/memory/*.md` L2 files for `⚠️ CONTRADICTION:` strings that have not been followed by a resolution note. These require human judgment.

**4. Orphan L2 scan**
Find sections in `~/clawd/memory/project-*.md` that have no `Source: memory/raw/` backlink. Knowledge asserted without a cited source.

**5. Log integrity scan**
Verify that each `log.md` entry's slug has a corresponding raw file on disk. Warns for orphaned log entries (entry exists, file does not).

**6. Post-compile backlink check**
For each raw file with `compiled: true`, verify that at least one `memory/*.md` L2 file contains the expected `Source: memory/raw/<file>` backlink. Flags compiled files with no backlinks as potential orphans post-compile.

### Running lint

```sh
# Print report to terminal
python3 /Users/johanesalxd/Developer/git/llm-wiki/scripts/lint.py

# Save report to file
python3 /Users/johanesalxd/Developer/git/llm-wiki/scripts/lint.py --output ~/clawd/memory/raw/lint-YYYY-MM-DD.md
```

Lint output is a markdown report. Review it and decide which issues to action — no automatic changes are made.

### Lint schedule

Run lint weekly to catch drift early. Suggested cron-friendly command:

```sh
python3 /Users/johanesalxd/Developer/git/llm-wiki/scripts/lint.py --output /tmp/llm-wiki-lint-$(date +%Y%m%d).md
```

---

## Auto-ingest (Vader-triggered)

When Jo drops a URL or file path into conversation without an explicit instruction, Vader should automatically trigger ingest without being asked. Follow the Ingest procedure above using native `write`/`edit` tools directly.

**Exception:** If the URL appears to be a NotebookLM link or Jo mentions it is an NLM source, prompt for the notebook name/type before ingesting.

---

## Conventions

### File layout

```
~/clawd/
  memory/
    raw/              L0 — immutable source stubs (LLM reads only)
      log.md          append-only ingest/compile log
      lint-*.md       lint reports (not raw sources)
      YYYY-MM-DD-<slug>.md
    project-*.md      L2 — project knowledge files
    YYYY-MM-DD.md     L2 — dated notes
    projects.md       L2 — project index
    MEMORY.md         L3 — curated durables, auto-injected
  short-term-memory.md  L1 — active working state
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
compiled_into: []            # inline list of memory files updated — e.g. ["memory/project-foo.md"]
tags: []                     # optional topic tags
---
```

### Rules

- Filename format: `YYYY-MM-DD-<kebab-slug>.md` (max 6 words in slug).
- `memory/raw/log.md` is **append-only** — never edit existing entries.
- Compile step is always **manual/agent-triggered** — never automatic.
- Lint reports — always **report only**, human decides on fixes.
- Contradiction flags (`⚠️ CONTRADICTION:`) must remain until explicitly resolved by a human.
- `compiled_into` field must use **inline list format** — multi-line YAML block lists are not supported by the lint parser.
