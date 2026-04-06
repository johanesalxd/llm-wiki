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
4. Add backlink and log entries

Use when:
- the source is first-party or clearly canonical
- the source already stands on its own
- no extra framing is needed before preservation

## 2. YouTube minimal-acquisition-first ingest

When the source is a YouTube video, do not preserve the raw URL token blindly.

Example:
- Andrej Karpathy — `[1hr Talk] Intro to Large Language Models`
- Source URL: `https://youtu.be/zjkBMFhNj_g?si=aQe3wILHX_0SZUL3`
- Raw file: `memory/raw/2026-04-06-karpathy-intro-large-language-models.md`
- Transcript companion: `memory/raw/2026-04-06-karpathy-intro-large-language-models-transcript.md`

Expected flow:
1. Run a minimal acquisition pass to obtain transcript / captions / stable description
2. Confirm what the video actually is
3. Choose a meaningful slug from the confirmed title/topic
4. Preserve the **full transcript** in the raw layer when transcript/captions are available
5. Store chapter maps and source description as supporting metadata, not as a substitute for the transcript
6. Compile based on workspace significance, not just subject matter

Key lessons:
- the video may be about LLMs, but if the point of the session is validating the YouTube ingest path, the compile target can still be the project file for the wiki itself
- if transcript/captions are available, the raw layer should preserve the **full transcript**, not only the chapter map or source description

## 3. Not wiki / action-only rejection

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
