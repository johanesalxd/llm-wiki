# Source routing reference

Extended version of the routing table in SKILL.md. Covers URL patterns, file extensions, and edge cases.

> **Skill taxonomy:** Skills referenced in this file fall into three categories:
> 1. **Local skills** — in `~/clawd/skills/`
> 2. **Bundled OpenClaw skills** — shipped with OpenClaw at `~/.local/share/mise/installs/node/24.13.0/lib/node_modules/openclaw/skills/` (e.g. `summarize`, `blogwatcher`)
> 3. **Extra/extension skills** — installed separately
>
> Agents must not assume all skills live in `~/clawd/skills/`. Check all three locations if a skill is not found locally.

---

## Routing table

| Source type | Detection rule | Tool | Notes |
|---|---|---|---|
| Web article / blog / doc | URL starts with `http`/`https`, not a known special type | `web_fetch` | Default fallback for any HTTP URL |
| PDF (remote) | URL contains `.pdf` before `?` or `#` | `gemini-pdf-analyzer` skill | Handles PDFs served directly from URLs |
| PDF (local file) | File extension `.pdf` | `gemini-pdf-analyzer` skill | Pass local path to skill |
| Image / screenshot | Extension `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`, `.bmp`, `.tif`, `.tiff` | `vision-sandbox` skill | Works for both local files and image URLs |
| YouTube video | Domain `youtube.com` or `youtu.be` | `summarize` skill | Covers standard watch URLs and short links |
| X / Twitter thread | Domain `x.com` or `twitter.com` | `bird thread <url>` | See thread vs single tweet edge case below |
| NotebookLM notebook | NLM notebook name (not a URL) | `notebooklm` skill | **Cannot be auto-detected** — requires `--type nlm` flag; input is notebook name, not a URL |

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

Edge case: GitHub raw file URLs (`raw.githubusercontent.com`) are treated as web. If the file is a PDF, override to `gemini-pdf-analyzer`.

---

### PDF (remote)

Matches when the URL path contains `.pdf` before a `?`, `#`, or end of string.

```
https://arxiv.org/pdf/2301.00001.pdf
https://example.com/whitepaper.pdf
https://example.com/reports/q1.pdf?download=true   ← .pdf before ?
```

Tool: `gemini-pdf-analyzer` skill with the URL.

Edge case: some services redirect to a PDF without `.pdf` in the URL (e.g., some DOI redirects, SSRN). If `web_fetch` returns binary content or a PDF mime type, re-route to `gemini-pdf-analyzer`.

---

### PDF (local)

Matches when the input is a local file path with `.pdf` extension.

```
~/Downloads/paper.pdf
/tmp/report-2026-04.pdf
```

Tool: `gemini-pdf-analyzer` skill with the file path.

---

### Image / screenshot

Matches file extension or image URL ending in a known image format.

```
~/Desktop/screenshot.png
/tmp/diagram.webp
https://example.com/image.jpg
```

Tool: `vision-sandbox` skill.

Edge case: URLs ending in image extensions served through CDNs often include query params. The `?` boundary in the detection regex handles this:

```
https://cdn.example.com/img.png?w=800&h=600   ← .png before ?
```

---

### YouTube

Matches the domain `youtube.com` or `youtu.be` anywhere in the URL.

```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://youtu.be/dQw4w9WgXcQ
https://youtube.com/shorts/abcdef123
```

Tool: `summarize` skill with the video URL.

> **Slug gotcha:** Standard `watch?v=` YouTube URLs produce the weak auto-slug `watch` when passed to `ingest.py`. Always use `--slug <meaningful-name>` for YouTube URLs:
> ```sh
> python3 scripts/ingest.py "https://youtube.com/watch?v=abc123" --slug karpathy-llm-os-talk
> ```

**Edge cases:**

| Pattern | Notes |
|---|---|
| `youtube.com/playlist?list=...` | YouTube playlist — each video is a separate source. Ingest one video at a time, or summarize the playlist as a single source with a note listing all videos. |
| `youtube.com/channel/...` | Channel page — not a video. Use `web_fetch` and note the channel; ingest specific videos separately. |
| `youtube.com/@handle` | Handle URL — same as channel page. |
| `youtube.com/live/...` | Live stream — treat as a video URL; `summarize` handles it if a transcript is available. |

---

### X / Twitter thread

Matches the domain `x.com` or `twitter.com`.

```
https://x.com/username/status/1234567890
https://twitter.com/username/status/1234567890
```

Tool: `bird thread <url>`

**Edge cases:**

| Pattern | Notes |
|---|---|
| Single tweet (not a thread) | Still use `bird thread` — it handles single posts gracefully. |
| X Notes (`x.com/i/notes/...`) | X Notes are long-form articles on X. Use `web_fetch` instead of `bird thread`. |
| X Spaces recording | Not supported by `bird thread`. Use `web_fetch` on the Space URL for metadata; no transcript available unless separately provided. |
| Protected/private account | `bird thread` will fail. Note in the stub that content is unavailable and set `source_type: twitter`. |

---

### NotebookLM notebook

Identified by the user providing a notebook name rather than a URL.

```
"project-alpha notebook"
"LLM reading list NLM"
```

Tool: `notebooklm` skill with the notebook name.

> **Auto-detection gotcha:** `ingest.py` **cannot** auto-detect NotebookLM notebooks from a URL or name. Always pass `--type nlm` explicitly when calling the script with an NLM source. The `notebooklm` skill is the correct skill name — not `nlm`.

Edge case: if the user provides a NotebookLM share URL (`notebooklm.google.com/...`), use `web_fetch` first to check if the content is publicly accessible, then route to `notebooklm` if a notebook name can be identified.

---

## Detection priority order

When a URL could match multiple rules (e.g., a PDF served from a YouTube CDN URL), apply rules in this order:

1. YouTube (`youtube.com` / `youtu.be`)
2. X / Twitter (`x.com` / `twitter.com`)
3. PDF (`.pdf` in URL path)
4. Image (image extension in URL path)
5. Web (default fallback for any `http`/`https` URL)

Local file paths:
1. PDF (`.pdf` extension)
2. Image (image extension)
3. Web (default — treat as an importable markdown/text file via `web_fetch`)

---

## Ambiguous inputs

If the source input does not look like a URL or a local file path, ask the user to clarify:

- Is this a NotebookLM notebook name?
- Is this a local file path (provide the full path)?
- Is this a search query or topic (not an ingestable source)?

Do not guess — routing the wrong source type wastes time and produces a malformed stub.
