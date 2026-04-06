# Compile conventions

Detailed conventions for integrating raw sources into compiled markdown knowledge files.

---

## When to create a new project file vs update an existing one

**Update an existing project file** when the raw source is directly relevant to an active topic already tracked in the project index. Signs of a good match:

- The source's tags overlap with the project file's topic area.
- The source contains insights that extend, contradict, or confirm content already in the project file.
- The project file has a section that would naturally absorb the source's summary.

**Create a new project file** when:

- No existing project file covers the topic, and the topic is expected to generate multiple future sources.
- The raw source introduces a distinct research thread that deserves its own tracking.
- Naming convention: `project-<topic-kebab-slug>.md`
- Register the new file in the project index.

**Use a dated note** when:

- The source is one-off, low-priority, or its relevance is unclear.
- The source is informational but does not fit any active project.
- Dated notes are acceptable compile targets; they may later be refactored into project files.

---

## Backlink format

Every summary section added to a compiled file during a compile operation must include a backlink to the raw source. Use this exact format:

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

Do not use full absolute paths in backlinks — relative paths keep the wiki portable.

---

## Flagging contradictions

When a raw source contradicts existing content in a compiled file, insert a contradiction flag on its own line immediately after the relevant claim:

```
⚠️ CONTRADICTION: <clear description of what contradicts what>
```

Example:

```markdown
### Temperature tuning for reasoning tasks

Previous note suggested temperature 0.7 for best diversity.
Smith et al. find temperature 0 maximises accuracy on reasoning benchmarks.

⚠️ CONTRADICTION: Earlier guidance recommends temperature 0.7; Smith et al. recommend temperature 0 for reasoning. Review both sources and update the recommendation.

Source: memory/raw/2026-04-05-smith-chain-of-thought.md
```

**Resolution:** When a human resolves the contradiction, add a `RESOLVED` note on the next line:

```
⚠️ CONTRADICTION: ...
RESOLVED 2026-04-10: Adopted Smith et al. recommendation for reasoning tasks; temperature 0.7 guidance retained for creative generation only.
```

The lint script treats any `⚠️ CONTRADICTION:` not followed soon after by `RESOLVED` as an open issue.

---

## Handling sources that span multiple topics

If a raw source is relevant to more than one project or topic:

1. List all target compiled files in the compile brief before starting.
2. Add a focused summary to each relevant file — only the aspects relevant to that file's topic.
3. Include the same `Source:` backlink in each target file.
4. Update `compiled_into` in the raw frontmatter to list all files updated:
   ```yaml
   compiled_into: ["project-llm-reasoning.md", "project-prompt-engineering.md"]
   ```
   Always use inline list format.

Do not add a single monolithic dump to one file and skip the others — this creates orphan compiled sections in the files that were skipped.

---

## Transcript-driven compile rule

When compiling from a YouTube source that has a transcript or transcript-companion file, the **raw transcript is canonical**.

This means:
- helper summaries are allowed as compression aids on long transcripts
- chapter maps and source descriptions are allowed as supporting context
- the final compiled note must still be grounded in the raw transcript, not only the helper summary

If a source was first compiled shallowly for workflow validation and later recompiled from the repaired transcript, record that explicitly as a **second-pass compile** in both the compiled note and the raw log.

---

## Cross-references

After adding a summary to a compiled file, add cross-references to related sections within the same or other compiled files where the connection is meaningful:

```
See also: project-prompt-engineering.md § Temperature and sampling
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

1. Read the raw file frontmatter and body in full.
2. Use the project index plus relevant `project-*.md` files to identify the right targets.
3. Read the target files to understand existing content.
4. Add summary sections to each.

### After (compiled file update)

```markdown
## Chain-of-thought prompting (Smith et al., 2026)

Chain-of-thought (CoT) prompting significantly improves multi-step reasoning
by including intermediate reasoning steps in few-shot examples.

- 18% accuracy gain on GSM8K at temperature 0
- Effective at ≥100B parameter scale
- Few-shot CoT outperforms zero-shot CoT for arithmetic tasks

⚠️ CONTRADICTION: Previous note suggested temperature 0.7 for reasoning tasks; Smith et al. find temperature 0 maximises accuracy. Review and reconcile.

Source: memory/raw/2026-04-05-smith-chain-of-thought.md
See also: project-prompt-engineering.md § Few-shot prompting
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
compiled_into: ["project-llm-reasoning.md", "project-prompt-engineering.md"]
tags: ["chain-of-thought", "reasoning", "prompting"]
---
```

### After (log entry appended)

```
## [2026-04-05] compile | smith-chain-of-thought | files updated: project-llm-reasoning.md, project-prompt-engineering.md
```

---

## Compile checklist

Before finishing a compile:

- [ ] Raw file body was read in full.
- [ ] All relevant compiled files were identified.
- [ ] Summary added to each relevant file with `Source:` backlink.
- [ ] Contradictions flagged with `⚠️ CONTRADICTION:` where found.
- [ ] Cross-references added where relevant.
- [ ] Raw file frontmatter updated: `compiled: true`, `compiled_date`, `compiled_into`.
- [ ] Project index updated if a new project file was created or an existing one materially changed.
- [ ] Compile entry appended to the raw log.
- [ ] Log entry is append-only.
