# Wiki writing reference

This file governs **how compiled L2 pages should read**.

It is the missing layer between:
- `source-routing.md` — how to acquire the source
- `compile-conventions.md` — where the compiled content belongs and how to merge it
- this file — how to turn source material into a page that is actually worth reading later

The goal is simple:

> **Most of the time, the reader should not need to go back to the raw layer.**

If compiled pages feel like highlights, operator notes, or process chatter, the wiki is underwritten.

---

## Primary standard

Write L2 pages as **wiki articles**, not as ingest logs and not as bullet-only summaries.

The page should feel closer to:
- a concise Wikipedia article
- a good internal research brief
- a reference note built for future retrieval

It should feel unlike:
- a meeting recap
- a highlights list
- a tool log
- a checklist with source crumbs glued to it

### Core test

Ask:

1. **Could Jo understand the source from this page alone most of the time?**
2. **Would this still be useful three weeks later without the original chat context?**
3. **Does this read like a real note/article, or like a compile artifact?**

If the answer to (3) is “compile artifact,” rewrite it.

---

## Content goals

Compiled wiki writing should optimize for:
- **retrieval value** — useful on re-read
- **standalone clarity** — understandable without the ingest session
- **conceptual compression** — dense, not bloated
- **source-grounded explanation** — not vague abstraction
- **synthesis over extraction** — explain the idea, don’t just list fragments

The wiki is not just a citation surface. It is the **usable knowledge surface**.

---

## Lead / overview rule

Every substantial L2 page or section should open with a real **lead**.

The lead should:
- say what the thing is
- say what matters most about it
- summarize the whole section/page in prose
- let the reader decide whether to continue

The lead should **not**:
- tease the content
- repeat the title with different words
- start with process language like “This source was ingested to validate…” unless the page is actually about workflow validation

### Recommended lead length

- small section: **80–150 words**
- substantial page/major section: **120–250 words**

---

## Default writing mode: prose first

Default to **clear explanatory prose**.

Use bullets when they help compression, but do not let bullets replace explanation.

A good wiki page usually has:
- a lead
- 2–5 prose sections
- bullets only where they genuinely improve scanability

### Good uses of bullets
- short enumerations
- comparison dimensions
- decision criteria
- lists of examples
- caveats / tensions / failure modes

### Bad uses of bullets
- replacing all explanation with fragments
- writing “key takeaways” instead of actual content
- listing claims without integrating them
- turning the page into a notes dump

---

## Section design

Use only headings that earn their keep.

Do **not** force every page into the same template.

Pick the smallest structure that makes the page readable.

### Useful section patterns

#### 1. Concept / theory page
Use for ideas, patterns, frameworks.

Suggested shape:
- lead
- core model / explanation
- key mechanisms or claims
- tensions / caveats / implications

#### 2. Source-derived article page
Use when a source deserves durable synthesis.

Suggested shape:
- lead
- main ideas
- strongest arguments or evidence
- important caveats / disagreements
- implications for the surrounding wiki

#### 3. Operational / system page
Use for tools, workflows, projects, and living systems.

Suggested shape:
- lead
- current model / architecture
- important design decisions
- active constraints / unresolved issues

### What to avoid
Avoid filler headings such as:
- “Why it matters here” when the answer is obvious or repetitive
- “Practical implication” when it just repeats the previous section
- “Key takeaways” as a substitute for actual explanation

If a heading does not improve retrieval, cut it.

---

## Depth rule

Do **not** use a hard page-count rule like “2 A4 pages minimum.”

That produces padding.

Instead, use a **sufficiency rule**:

> The page should be long and detailed enough that the reader rarely needs the raw source for normal understanding.

### Soft depth targets

These are targets, not quotas.

- **Minor note / narrow section:** 250–500 words
- **Normal important source summary:** 500–1,200 words
- **Canonical / foundational source:** often 800–1,500+ words across the relevant page/section

If the source is important and the compiled result still feels like “highlights,” it is too thin.

---

## Concrete anchor rule

When a source uses a specific example, analogy, or demonstration to make an abstract concept click, preserve it in the compiled page.

Abstract explanation alone produces pages that are technically correct but do not generate real understanding. Concrete anchors are the moments where a concept stops being a claim and becomes something the reader can *feel*.

The test: if removing the example makes the concept harder to intuitively grasp — not just harder to verify — keep the example.

Good concrete anchors:
- a specific surprising result that makes an abstract property visceral (e.g. a model that knows X but not the reverse of X)
- a vivid demonstration that shows what a failure mode actually looks like in practice (e.g. a model generating plausible-looking but fabricated details)
- an analogy from the source that reframes the concept in a sticky way

Bad uses of examples:
- padding with anecdotes that do not deepen understanding
- repeating the same point through multiple examples when one suffices
- including examples that only illustrate what the prose already explains clearly

The goal is not to preserve every example from the source. It is to preserve the ones that carry explanatory weight the prose alone cannot.

---

## Synthesis rule

Do not just repeat the source structure.

The compiled page should answer:
- what is the source actually saying?
- what is the model or argument underneath it?
- what should a future reader remember?
- what changed in the wiki after reading this?

The source is the input. The wiki page is the **distillation**.

---

## Source-grounding rule

Stay grounded in the source, but write for humans.

That means:
- preserve exact claims where precision matters
- preserve numbers where they matter
- cite/backlink the raw source
- but do not write as if the page were just annotated excerpts

Good compiled writing should sound like:
- “Here is the idea, in clear language, grounded in the source.”

Not like:
- “Here are some notes I copied from the source.”

---

## Process-chatter rule

Do not pollute content pages with operator narration.

Keep out of normal content pages:
- rerun commentary
- “this validated the workflow” chatter
- migration ceremony
- “we ran this under a new boundary” narration
- source acquisition play-by-play

That material belongs in:
- testing archive files
- dated session memory
- workflow / operations pages

Exception:
- if the page is actually about the workflow itself, process commentary is content

---

## Reader-value rule

Write for the future reader, not the current operator.

The future reader often wants one of three things:
1. **quick orientation** — what is this and why should I care?
2. **real understanding** — how does it work / what is the argument?
3. **targeted recall** — what were the important specifics again?

A strong wiki page serves all three.

---

## Compression rule

Compression does **not** mean shallowness.

Good compression:
- removes repetition
- removes ceremony
- removes operator narration
- surfaces the real model / idea / conflict / evidence

Bad compression:
- strips out explanation until only bullet fragments remain
- leaves only “highlights”
- turns the page into headings with almost no content beneath them

---

## Multi-source pages

When multiple sources converge on one page:
- merge them into one readable article
- do not stack source mini-summaries end to end
- synthesize by concept, not by ingestion order

Good multi-source writing should feel like:
- one coherent page

Not like:
- a stitched-together source log

---

## Anti-patterns

Watch for these failure modes:

### 1. Compile artifact voice
Symptoms:
- “What it is” / “Why it matters” / “Practical implication” on every page regardless of fit
- rigid headings with thin content
- obvious template smell

Fix:
- rewrite in normal article prose
- keep only headings that add retrieval value

### 2. Highlights page
Symptoms:
- everything is bullets
- no real explanation
- useful for 30 seconds, useless later

Fix:
- add a lead
- add real prose sections
- explain the model, not just the fragments

### 3. Process pollution
Symptoms:
- page is about the ingest session, not the source/topic
- filled with validation chatter

Fix:
- move workflow history to testing/dated memory
- keep content page about the content

### 4. Source shadowing
Symptoms:
- page is so thin the raw source is still required for ordinary use

Fix:
- deepen the synthesis until the page is self-sufficient for normal reading

---

## Practical editing checklist

Before you finish a compiled page or section, ask:

- Does it open with a real lead?
- Is there enough prose to explain the idea, not just list it?
- Would this still make sense without the ingest chat?
- Is the page about the **topic**, not about the workflow?
- Did I remove filler headings that add no retrieval value?
- Would Jo need the raw layer for ordinary reading, or only for verification/depth?

If Jo would still need the raw source for ordinary reading, keep writing.

---

## Relationship to other references

- `source-routing.md` decides **what tool/path to use**
- `compile-conventions.md` decides **where the compiled result belongs and how to merge it**
- `wiki-writing.md` decides **how the final compiled page should read**

Use all three together.
