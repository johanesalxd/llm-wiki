# llm-wiki examples

Use these as behavior anchors when applying the skill.

## 1. Direct canonical web ingest

When the source is already canonical and self-contained, ingest directly.

Example:
- Karpathy gist: `https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f`

Expected flow:
1. Fetch the source body
2. Write immutable raw record in the raw layer
3. Compile into the most relevant L2 file
4. Write the compiled page/section as a **real wiki article**, not a highlights stub
5. Update raw frontmatter + append log entries

Use when:
- the source is first-party or clearly canonical
- the source already stands on its own
- no extra framing is needed before preservation

## 2. YouTube minimal-acquisition-first ingest

When the source is a YouTube video, do not preserve the raw URL token blindly.

Example:
- Andrej Karpathy — `[1hr Talk] Intro to Large Language Models`
- Source URL: `https://youtu.be/zjkBMFhNj_g?si=aQe3wILHX_0SZUL3`
- Raw file: `memory/raw/2026-04-07-karpathy-intro-large-language-models.md`
- Transcript companion: `memory/raw/2026-04-07-karpathy-intro-large-language-models-transcript.md`

Expected flow:
1. Run a minimal acquisition pass to obtain transcript / captions / stable description
2. Confirm what the video actually is
3. Choose a meaningful slug from the confirmed title/topic
4. For serious long-form video, create the **main raw file + transcript companion** pair by default
5. Preserve the **full transcript** in the raw layer when transcript/captions are available
6. Store chapter maps and source description as supporting metadata, not as a substitute for the transcript
7. Compile based on workspace significance, not just subject matter
8. Write the final L2 section as a **readable article-style explainer**, not an ingest log or chapter-map stub

Key lessons:
- transcript/captions should become the canonical compile source for important long-form video
- the main raw file should stay readable, while the transcript companion carries the full text
- the compiled page should tell the reader what the talk is actually saying, so the raw transcript is only needed for verification or deeper drilling

## 3. Policy-aware re-ingest under a new boundary

When the same canonical source is intentionally re-run on a new date under a new lint-policy boundary, the apparent duplicate is often valid.

Example:
- Karpathy gist and Karpathy intro talk re-run on `2026-04-07` after the production cutover boundary

Expected flow:
1. Read `references/lint-policy.md` first
2. Confirm whether the older material belongs to a legacy/testing file
3. Allow fresh raw/log artifacts on the new date if the re-run is intentional
4. Keep the important distinction on **routing**, not artificial deduplication
5. Compile the new production-era result into the active production file, not the testing archive

Key lessons:
- same-source/new-date raw or log entries can be legitimate
- the real error is usually writing the new compile output into the wrong L2 destination
- process chatter about the rerun belongs in testing or dated memory, while the main project file should stay content-first

## 4. Not wiki / action-only rejection

When the input is still just a task or design brief, do not force it into the wiki.

Example:
- agent eval harness design task

Expected flow:
1. Recognize the input is an action/problem statement, not yet a durable source
2. Do not ingest into the raw layer
3. Track or execute the task normally
4. Only ingest later if strong canonical sources or durable conclusions emerge

Use when:
- the input is mainly a todo, build request, reminder, or design problem
- there is no stable source artifact worth preserving yet
