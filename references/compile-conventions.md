# Compile conventions

Detailed conventions for integrating raw sources into L2 memory files.

---

## When to create a new project file vs update an existing one

**Update an existing project file** when the raw source is directly relevant to an active project tracked in `memory/projects.md`. Signs of a good match:

- The source's tags overlap with the project file's topic area.
- The source contains insights that extend, contradict, or confirm content already in the project file.
- The project file has a section that would naturally absorb the source's summary.

**Create a new project file** when:

- No existing project file covers the topic, and the topic is expected to generate multiple future sources.
- The raw source introduces a distinct research thread that deserves its own tracking.
- Naming convention: `memory/project-<topic-kebab-slug>.md`
- Register the new file in `memory/projects.md` index.

**Use a dated note** (`memory/YYYY-MM-DD.md`) when:

- The source is one-off, low-priority, or its relevance is unclear.
- The source is informational but does not fit any active project.
- Dated notes are acceptable compile targets; they may later be refactored into project files.

---

## Backlink format

Every summary section added to an L2 file during a compile operation must include a backlink to the raw source. Use this exact format:

```
Source: memory/raw/YYYY-MM-DD-<slug>.md
```

The backlink goes at the end of the summary block, before any cross-references. Example:

```markdown
### Key insight from the Smith et al. paper

The authors show that chain-of-thought prompting improves reasoning accuracy
by 18% on GSM8K when temperature is set to 0.

Source: memory/raw/2026-04-05-smith-chain-of-thought.md
```

Do not use full absolute paths in backlinks — relative paths from `~/clawd/` make the wiki portable.

---

## Flagging contradictions

When a raw source contradicts existing content in an L2 file, insert a contradiction flag on its own line immediately after the relevant claim:

```
⚠️ CONTRADICTION: <clear description of what contradicts what>
```

Example:

```markdown
### Temperature tuning for reasoning tasks

Previous note (2026-01-10) suggested temperature 0.7 for best diversity.
Smith et al. (2026) find temperature 0 maximises accuracy on reasoning benchmarks.

⚠️ CONTRADICTION: Earlier guidance recommends temperature 0.7; Smith et al. recommend temperature 0 for reasoning. Review both sources and update the recommendation.

Source: memory/raw/2026-04-05-smith-chain-of-thought.md
```

**Resolution:** When a human resolves the contradiction, add a `RESOLVED` note on the next line:

```
⚠️ CONTRADICTION: ...
RESOLVED 2026-04-10: Adopted Smith et al. recommendation for reasoning tasks; temperature 0.7 guidance retained for creative generation only.
```

The lint script treats any `⚠️ CONTRADICTION:` not followed (within 5 lines) by `RESOLVED` as an open issue.

---

## Handling sources that span multiple topics

If a raw source is relevant to more than one project or topic:

1. List all target L2 files in the compile brief before starting.
2. Add a focused summary to each relevant L2 file — only the aspects relevant to that file's topic.
3. Include the same `Source:` backlink in each L2 file.
4. Update `compiled_into` in the raw frontmatter to list all files updated:
   ```yaml
   compiled_into: ["memory/project-llm-reasoning.md", "memory/project-prompt-engineering.md"]
   ```
   Always use inline list format — the lint parser and current conventions assume inline list formatting here.

Do not add a single monolithic dump to one file and skip the others — this creates orphan L2 sections in the files that were skipped.

---

## Cross-references

After adding a summary to an L2 file, add cross-references to related sections within the same or other L2 files where the connection is meaningful:

```
See also: memory/project-prompt-engineering.md § Temperature and sampling
```

Cross-references are optional but encouraged for topics that appear in multiple projects. They help the agent navigate the wiki without re-reading all files.

---

## Example: before and after a compile operation

### Before (raw stub, uncompiled)

File: `memory/raw/2026-04-05-smith-chain-of-thought.md`

```markdown
---
title: Chain-of-Thought Prompting Elicits Reasoning in Large Language Models
source_url: https://arxiv.org/abs/2201.11903
source_type: web
date_ingested: 2026-04-05
compiled: false
compiled_into: []
tags: ["chain-of-thought", "reasoning", "prompting"]
---

# Chain-of-Thought Prompting Elicits Reasoning in Large Language Models

Chain-of-thought (CoT) prompting adds intermediate reasoning steps to few-shot
examples, enabling LLMs to solve multi-step reasoning problems significantly
better than standard prompting.

Key findings:
- 18% accuracy improvement on GSM8K at temperature 0
- Works best with models ≥100B parameters
- Few-shot CoT > zero-shot CoT for arithmetic
```

### During compile

1. Read the raw file frontmatter and body in full
2. Use `memory/projects.md` plus relevant `memory/project-*.md` files to identify the right L2 targets
3. Read both project files to understand existing content
4. Add summary sections to each

### After (L2 update to `memory/project-llm-reasoning.md`)

```markdown
## Chain-of-thought prompting (Smith et al., 2026)

Chain-of-thought (CoT) prompting significantly improves multi-step reasoning
by including intermediate reasoning steps in few-shot examples.

- 18% accuracy gain on GSM8K at temperature 0
- Effective at ≥100B parameter scale
- Few-shot CoT outperforms zero-shot CoT for arithmetic tasks

⚠️ CONTRADICTION: Previous note suggested temperature 0.7 for reasoning tasks;
Smith et al. find temperature 0 maximises accuracy. Review and reconcile.

Source: memory/raw/2026-04-05-smith-chain-of-thought.md
See also: memory/project-prompt-engineering.md § Few-shot prompting
```

### After (raw frontmatter updated)

```yaml
---
title: Chain-of-Thought Prompting Elicits Reasoning in Large Language Models
source_url: https://arxiv.org/abs/2201.11903
source_type: web
date_ingested: 2026-04-05
compiled: true
compiled_date: 2026-04-05
compiled_into: ["memory/project-llm-reasoning.md", "memory/project-prompt-engineering.md"]
tags: ["chain-of-thought", "reasoning", "prompting"]
---
```

> **Format note:** Always use inline list format for `compiled_into`. Multi-line YAML block lists (with `- item` on separate lines) are not part of the standard llm-wiki flow.

### After (log entry appended)

```
## [2026-04-05] compile | smith-chain-of-thought | files updated: memory/project-llm-reasoning.md, memory/project-prompt-engineering.md
```

---

## Compile checklist

Before finishing a compile:

- [ ] Raw file body was read in full (not skimmed)
- [ ] All relevant L2 files identified (checked `projects.md` index)
- [ ] Summary added to each relevant L2 file with `Source:` backlink
- [ ] Contradictions flagged with `⚠️ CONTRADICTION:` where found
- [ ] Cross-references added where relevant
- [ ] Raw file frontmatter updated: `compiled: true`, `compiled_date`, `compiled_into` (inline list format)
- [ ] `memory/projects.md` updated if a new project file was created or an existing one materially changed
- [ ] Compile entry appended to `memory/raw/log.md`
- [ ] Log entry is append-only (no edits to existing entries)
