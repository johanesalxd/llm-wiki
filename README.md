# llm-wiki

An OpenClaw skill that implements Karpathy's LLM Knowledge Base pattern for the Vader/OpenClaw workspace.

It gives you a structured workflow to:
- ingest raw sources into `~/clawd/memory/raw/`
- compile them into L2 memory files (`memory/project-*.md` or dated notes)
- lint the wiki for missing backlinks, stale sources, contradictions, and other integrity issues

---

## What it is

`llm-wiki` is a tiered memory workflow built around four layers:

```text
L0  ~/clawd/memory/raw/           immutable source docs, LLM reads only
L1  ~/clawd/short-term-memory.md  active working state
L2  ~/clawd/memory/*.md           LLM-maintained wiki, project files, dated notes
L3  ~/clawd/MEMORY.md             curated durables, auto-injected into context
```

The skill is designed for research accumulation, not one-shot Q&A. The point is to make knowledge compound over time instead of rediscovering the same source material from scratch on every question.

---

## What the skill actually does

There are three operations:

### 1. Ingest
`ingest.py` does **not** fetch or summarize the source itself.

It is a **router + stub writer**:
- detects the source type
- decides which downstream tool/skill should handle it
- writes a raw stub markdown file to `~/clawd/memory/raw/`
- appends an ingest entry to `~/clawd/memory/raw/log.md`

This is a **two-step workflow**:
1. run ingest to create the raw stub and routing decision
2. have the agent call the appropriate tool/skill and populate/compile the result

If you skip step 2, the raw file will still contain a placeholder body.

### 2. Compile
Compile is the agent-driven step that turns a raw source into useful L2 memory.

Typical compile actions:
- read a raw file from `memory/raw/`
- update one or more L2 files (`memory/project-*.md` or `memory/YYYY-MM-DD.md`)
- add backlinks in the form `Source: memory/raw/YYYY-MM-DD-<slug>.md`
- flag contradictions explicitly
- update raw frontmatter to `compiled: true`
- append a compile entry to `memory/raw/log.md`
- update `memory/projects.md` if a new project file is created

`compile_helper.py` is only a **pre-compile helper**. It does not edit memory files by itself.

### 3. Lint
`lint.py` is a read-only health check.

It currently checks:
1. uncompiled raw sources
2. stale compiled sources
3. unresolved contradiction flags
4. orphan L2 knowledge sections with no raw backlinks
5. log integrity (log entry exists but raw file is missing)
6. compiled raw sources with no backlinks anywhere in L2

Lint reports issues only. It never auto-fixes anything.

---

## Skill locations and dependency model

This repo is part of a larger OpenClaw workspace. Not every referenced skill lives in the same place.

There are three skill categories:

1. **Local skills** — stored in `~/clawd/skills/`
2. **Bundled OpenClaw skills** — stored inside the OpenClaw install
3. **Extras / extension-provided skills** — provided by installed extensions

Examples:
- `vision-sandbox` → local skill
- `gemini-pdf-analyzer` → local skill
- `bird` → local skill
- `notebooklm` → local skill
- `summarize` → bundled OpenClaw skill

So if a skill is referenced in `SKILL.md`, do **not** assume it must exist in `~/clawd/skills/`.

---

## Prerequisites

### Required
- OpenClaw configured and working
- Access to the existing workspace memory structure under `~/clawd/`
- Python **3.9+**
- Existing downstream skills/tools available in your OpenClaw setup

### Not required
- No `pip install`
- No virtualenv required for the helper scripts
- No external Python dependencies — scripts are **stdlib-only**

### Optional
- Ruff (for linting the scripts in this repo)
- Obsidian or another markdown reader for browsing the wiki manually

---

## Quickstart

### Example A — ingest a web article

From the repo root:

```sh
python3 scripts/ingest.py https://example.com/some-paper --slug some-paper --tags ml,transformers
```

This will:
- detect the source type
- create a raw stub file under `~/clawd/memory/raw/`
- append an ingest entry to `~/clawd/memory/raw/log.md`
- print which tool/skill should be called next

Then the agent should fetch/process the article and compile it into the relevant L2 memory files.

### Example B — inspect a raw source before compile

```sh
python3 scripts/compile_helper.py some-paper
```

If multiple raw files share the same slug across dates:

```sh
python3 scripts/compile_helper.py some-paper --date 2026-04-05
```

### Example C — run lint

```sh
python3 scripts/lint.py
```

Save the lint report to file:

```sh
python3 scripts/lint.py --output ~/clawd/memory/raw/lint-2026-04-05.md
```

Adjust stale threshold:

```sh
python3 scripts/lint.py --stale-days 14
```

---

## Script reference

All commands below assume you are running from the repo root:

```text
~/Developer/git/llm-wiki/
```

If not, use absolute paths.

### `scripts/ingest.py`

Purpose: route a source and write a raw stub.

```sh
python3 scripts/ingest.py <url-or-path> [--slug <slug>] [--tags tag1,tag2] [--force] [--raw-dir <path>] [--dry-run]
```

Important flags:
- `--slug` — strongly recommended for YouTube URLs
- `--tags` — helps later compile targeting
- `--force` — overwrite an existing same-date same-slug stub
- `--raw-dir` — test against a different raw directory
- `--dry-run` — print routing + target file info without writing

Notes:
- duplicate detection is enabled; same slug/date will warn unless `--force` is passed
- YouTube URLs like `watch?v=` often produce weak default slugs like `watch`; prefer `--slug`
- NotebookLM/NLM sources are not reliably auto-detectable from plain text; use the correct source context when ingesting them

### `scripts/compile_helper.py`

Purpose: inspect one raw source and suggest likely L2 targets before compile.

```sh
python3 scripts/compile_helper.py <slug> [--date YYYY-MM-DD] [--raw-dir <path>] [--memory-dir <path>]
```

What it does:
- finds the matching raw file
- reads frontmatter
- reports compiled status
- suggests likely L2 target files using tags + project file names

What it does **not** do:
- it does not modify L2 files
- it does not mark sources as compiled

### `scripts/lint.py`

Purpose: run a read-only health check over raw + L2 memory.

```sh
python3 scripts/lint.py [--raw-dir <path>] [--memory-dir <path>] [--stale-days <n>] [--output <path>]
```

Behavior:
- exits with code **0** when no issues are found
- exits with code **1** when issues are found
- writes markdown to stdout unless `--output` is provided

---

## Source routing overview

The full routing guide lives in:
- `references/source-routing.md`

High-level map:

| Source type | Typical handler |
|---|---|
| Web article / docs URL | `web_fetch` |
| PDF | `gemini-pdf-analyzer` |
| Image / screenshot | `vision-sandbox` |
| YouTube URL | bundled `summarize` skill |
| X / Twitter thread | `bird thread <url>` |
| NotebookLM notebook | `notebooklm` skill |

Two important caveats:
- **YouTube:** use `--slug` whenever possible
- **NotebookLM:** source detection may need human/agent judgment rather than syntax alone

---

## Compile conventions

The full compile rules live in:
- `references/compile-conventions.md`

Important conventions:
- backlink format:
  - `Source: memory/raw/YYYY-MM-DD-<slug>.md`
- contradiction format:
  - `⚠️ CONTRADICTION:`
- `compiled_into` should use **inline list format**, for example:

```yaml
compiled_into: ["memory/project-foo.md", "memory/project-bar.md"]
```

Do **not** use multi-line YAML block lists here.

---

## Auto-ingest convention

This repo also documents a workflow convention for Vader/OpenClaw:

When Jo drops a URL or file in conversation, Vader may automatically:
1. run `ingest.py`
2. route to the correct downstream tool/skill
3. populate the raw source
4. compile the result into L2 memory

That behavior is orchestrator-driven. It is not something `ingest.py` performs by itself.

---

## Lint schedule

Recommended maintenance cadence: weekly or on-demand.

Example cron-friendly command:

```sh
python3 /Users/johanesalxd/Developer/git/llm-wiki/scripts/lint.py --output /tmp/llm-wiki-lint-$(date +%Y%m%d).md
```

---

## Repository layout

```text
llm-wiki/
  README.md
  SKILL.md
  pyproject.toml
  scripts/
    ingest.py
    lint.py
    compile_helper.py
  references/
    source-routing.md
    compile-conventions.md
  .opencode/
    plans/
    artifacts/
```

---

## Current status

- v1 build: done
- v2 fixes: done
- skill deployed to `~/clawd/skills/llm-wiki/SKILL.md`
- `~/clawd/memory/raw/` exists
- no real sources ingested yet

So the next meaningful validation step is:
1. ingest a real source
2. compile it into L2
3. run lint
4. review the resulting backlinks and log entries
