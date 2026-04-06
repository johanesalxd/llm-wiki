# Source routing reference

Extended version of the routing table in `SKILL.md`. Covers URL patterns, file extensions, and edge cases.

---

## Routing table

| Source type | Detection rule | Tool | Notes |
|---|---|---|---|
| Web article / blog / doc | URL starts with `http`/`https`, not a known special type | `web_fetch` | Default fallback for any HTTP URL |
| PDF (remote) | URL contains `.pdf` before `?` or `#` | PDF analysis tool or skill | Handles PDFs served directly from URLs |
| PDF (local file) | File extension `.pdf` | PDF analysis tool or skill | Pass local path to the PDF handler |
| Image / screenshot | Extension `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`, `.bmp`, `.tif`, `.tiff` | vision or image-analysis tool | Works for both local files and image URLs |
| YouTube video | Domain `youtube.com` or `youtu.be` | summarization/transcript tool | Covers standard watch URLs and short links |
| X / Twitter thread | Domain `x.com` or `twitter.com` | thread extraction tool | See thread vs single tweet edge case below |
| NotebookLM notebook | notebook name or share link | NotebookLM tool or adapter | Often cannot be auto-detected from the first input alone |

---

## URL patterns with examples

### Web (article / blog / doc)

Matches any `http`/`https` URL that does not match a more specific pattern.

```
https://example.com/blog/some-post
https://arxiv.org/abs/2301.00001
https://docs.python.org/3/library/pathlib.html
https://github.com/owner/repo/blob/main/README.md
```

Tool: `web_fetch <url>`

Edge case: GitHub raw file URLs (`raw.githubusercontent.com`) are treated as web. If the file is a PDF, override to the PDF analysis path.

---

### PDF (remote)

Matches when the URL path contains `.pdf` before a `?`, `#`, or end of string.

```
https://arxiv.org/pdf/2301.00001.pdf
https://example.com/whitepaper.pdf
https://example.com/reports/q1.pdf?download=true
```

Tool: PDF analysis tool or skill with the URL.

Edge case: some services redirect to a PDF without `.pdf` in the URL. If `web_fetch` returns binary content or a PDF mime type, re-route to the PDF analysis path.

---

### PDF (local)

Matches when the input is a local file path with `.pdf` extension.

```
~/Downloads/paper.pdf
/tmp/report-2026-04.pdf
```

Tool: PDF analysis tool or skill with the file path.

---

### Image / screenshot

Matches file extension or image URL ending in a known image format.

```
~/Desktop/screenshot.png
/tmp/diagram.webp
https://example.com/image.jpg
```

Tool: vision or image-analysis tool.

Edge case: URLs ending in image extensions served through CDNs often include query params. The `?` boundary in the detection regex handles this:

```
https://cdn.example.com/img.png?w=800&h=600
```

---

### YouTube

Matches the domain `youtube.com` or `youtu.be` anywhere in the URL.

```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://youtu.be/dQw4w9WgXcQ
https://youtube.com/shorts/abcdef123
```

Tool: summarization/transcript tool with the video URL.

> **Slug gotcha:** Standard `watch?v=` YouTube URLs often collapse to the useless slug `watch` if an agent derives the filename from the URL path alone. When ingesting YouTube sources, always choose a meaningful slug based on the actual video/topic.

**Edge cases:**

| Pattern | Notes |
|---|---|
| `youtube.com/playlist?list=...` | YouTube playlist — each video is a separate source. Ingest one video at a time, or summarize the playlist as a single source with a note listing all videos. |
| `youtube.com/channel/...` | Channel page — not a video. Use `web_fetch` and note the channel; ingest specific videos separately. |
| `youtube.com/@handle` | Handle URL — same as channel page. |
| `youtube.com/live/...` | Live stream — treat as a video URL if a transcript is available. |

---

### X / Twitter thread

Matches the domain `x.com` or `twitter.com`.

```
https://x.com/username/status/1234567890
https://twitter.com/username/status/1234567890
```

Tool: thread extraction tool.

**Edge cases:**

| Pattern | Notes |
|---|---|
| Single tweet (not a thread) | The same extraction path can often handle a single post gracefully. |
| X Notes (`x.com/i/notes/...`) | Use `web_fetch` instead of a thread extractor. |
| X Spaces recording | Treat as metadata fetch only unless a transcript is separately available. |
| Protected/private account | Extraction will fail. Note in the stub that content is unavailable and preserve whatever metadata is available. |

---

### NotebookLM notebook

Identified by the user providing a notebook name or share link rather than a standard content URL.

```
"project-alpha notebook"
"LLM reading list NLM"
```

Tool: NotebookLM tool or adapter.

> **Auto-detection gotcha:** NotebookLM notebooks cannot always be inferred reliably from a raw URL or free-text name alone. Treat them as a manual routing case when needed.

Edge case: if the user provides a NotebookLM share URL, use a lightweight fetch first to check whether the content is publicly accessible, then route to the NotebookLM path if a notebook identifier can be confirmed.

---

## Detection priority order

When a URL could match multiple rules, apply rules in this order:

1. YouTube (`youtube.com` / `youtu.be`)
2. X / Twitter (`x.com` / `twitter.com`)
3. PDF (`.pdf` in URL path)
4. Image (image extension in URL path)
5. Web (default fallback for any `http`/`https` URL)

Local file paths:
1. PDF (`.pdf` extension)
2. Image (image extension)
3. Web/text import fallback

---

## Ambiguous inputs

If the source input does not look like a URL or a local file path, ask the user to clarify:

- Is this a NotebookLM notebook name?
- Is this a local file path?
- Is this a search query or topic rather than an ingestable source?

Do not guess — routing the wrong source type wastes time and produces a malformed stub.
