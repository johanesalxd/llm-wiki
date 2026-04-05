================================================================================
FINDINGS REPORT: README.md Assessment for Human Review and First-Use Onboarding
Repository: /Users/johanesalxd/Developer/git/llm-wiki
Date: 2026-04-05
Scope: README.md sufficiency for (a) human reviewer, (b) first-time user onboarding
================================================================================


────────────────────────────────────────────────────────────────────────────────
1. WHAT README.md CURRENTLY CONTAINS (section summary)
────────────────────────────────────────────────────────────────────────────────

README.md is 70 lines. It has six sections:

  a. Title + one-sentence description
     "An OpenClaw skill implementing Karpathy's LLM Knowledge Base pattern for
     the Vader/OpenClaw workspace."

  b. "What it is" (6 lines)
     Describes the tiered memory model: L0 raw sources → L2 project files →
     L3 MEMORY.md durable layer. Names the directories under ~/clawd/memory/.

  c. "Three sections" (10 lines across 3 sub-sections)
     Brief one-paragraph description of Ingest, Compile, and Lint. Each is
     one or two sentences — no procedure, no edge cases.

  d. "Tiered memory architecture" (8 lines)
     An ASCII diagram showing L0–L3 paths under ~/clawd/. No explanation of
     what each tier means or how data flows between them.

  e. "Quickstart" (11 lines)
     Two code blocks. The first shows the slash-command invocation style
     (/llm-wiki ingest, /llm-wiki compile, /llm-wiki lint). The second shows
     direct Python invocations for all three scripts. No explanation of
     prerequisites, expected output, or what the user should do next after
     running each command.

  f. "Repository layout" (13 lines)
     An annotated directory tree covering: README.md, SKILL.md, scripts/
     (ingest.py, lint.py, compile_helper.py), references/ (two files), and
     .opencode/plans/. One-line annotation for each file. No mention of
     pyproject.toml, .opencode/artifacts/, .opencode/node_modules/, or
     .opencode/package.json.


────────────────────────────────────────────────────────────────────────────────
2. GAPS BETWEEN WHAT README SAYS AND WHAT THE CODEBASE ACTUALLY DOES
────────────────────────────────────────────────────────────────────────────────

2.1  ingest.py — described as "source router + stub writer"
     README says:
       python3 scripts/ingest.py https://example.com/some-paper --slug some-paper --tags ml,transformers

     What the script actually does (from reading scripts/ingest.py):
       - Detects source type via regex patterns (YouTube, Twitter, PDF, image,
         web, with a local-file fallback).
       - Looks up the routing table to print WHICH TOOL the agent must call
         next; it does NOT call that tool itself.
       - Generates a kebab-case slug (auto-derived from URL last path segment,
         or user-supplied via --slug).
       - Writes a stub .md file to ~/clawd/memory/raw/YYYY-MM-DD-<slug>.md
         with required YAML frontmatter and a placeholder body line:
         "_[Agent: populate this section with the fetched/summarized content]_"
       - Appends an entry to ~/clawd/memory/raw/log.md (creates it with
         header if absent).
       - Supports --dry-run (print without writing) and --force (overwrite
         existing stub).
       - Emits a stderr warning when a YouTube URL produces the degenerate
         slug "watch".

     README gap: The README never explains that ingest.py is a router/planner
     only — it does NOT fetch content. A first-time user reading the quickstart
     will run the script expecting content to appear in the stub file. The
     two-step nature ("script prints routing decision → agent/human calls the
     indicated tool → agent fills body") is completely absent from README.

     README gap: --dry-run and --force flags are undocumented in README (they
     exist in the script's argparse and docstring).

     README gap: --raw-dir flag is undocumented in README (allows overriding
     the default ~/clawd/memory/raw/ path — critical for testing or alternate
     workspaces).

     README gap: The YouTube slug warning ("Use --slug <meaningful-name>") is
     mentioned in SKILL.md and source-routing.md but not in README.

2.2  compile_helper.py — described as "pre-compile brief printer"
     README says:
       python3 scripts/compile_helper.py some-paper

     What the script actually does (from reading scripts/compile_helper.py):
       - Accepts a slug argument (not a filename).
       - Searches ~/clawd/memory/raw/ for *-<slug>.md; returns the most
         recent match when multiple dates share a slug.
       - Supports --date YYYY-MM-DD to disambiguate when multiple files share
         the same slug.
       - Reads and parses YAML frontmatter from the matched file.
       - Suggests L2 target project files via simple substring tag-matching
         against project-*.md filenames.
       - Prints a formatted compile brief: title, type, URL, ingested date,
         tags, compiled status, compiled_into list, and suggested L2 targets.
       - If no project files match tags, falls back to suggesting ALL
         project-*.md files.
       - Does NOT modify any files.

     README gap: The --date flag is unmentioned in README — a user with
     multiple slugs of the same name will not know how to disambiguate.

     README gap: The L2 suggestion logic (tag-based substring matching against
     project-*.md filenames) is not documented anywhere in README. This is key
     to understanding compile_helper output.

     README gap: The "does not modify any files" guarantee is not stated in
     README; it is only in the script docstring and SKILL.md.

2.3  lint.py — described as "wiki health checker"
     README says:
       python3 scripts/lint.py --output ~/clawd/memory/raw/lint-2026-04-05.md

     What the script actually does (from reading scripts/lint.py):
       - Runs 6 distinct checks (orphan scan, stale scan, contradiction scan,
         orphan L2 scan, log integrity scan, post-compile backlink check).
       - Outputs a structured Markdown report with a summary table and a
         section per check.
       - Returns exit code 0 if zero issues, exit code 1 if any issues found
         (useful for CI / cron integration).
       - Accepts --raw-dir, --memory-dir, --stale-days (default 30) flags.
       - Writes the report to --output path if provided, otherwise prints to
         stdout.
       - Never modifies any files (read-only).
       - Skips log.md and lint-*.md files in the orphan scan.

     README gap: The 6 individual lint checks are named in README's "Three
     sections > Lint" paragraph, but only 4 are listed there vs. the actual 6
     in the script. README lists: uncompiled sources, stale compiled docs,
     unresolved contradiction flags, uncited L2 knowledge. Missing from README:
     check 5 (log integrity scan) and check 6 (post-compile backlink check).

     README gap: --stale-days flag not mentioned in README.
     README gap: Exit code behavior (0 = clean, 1 = issues found) not
     documented; relevant for cron/CI use.

2.4  The two-step ingest workflow is architecturally invisible in README
     SKILL.md lines 63, 170–175 make the two-step model explicit: the script
     is a router, and a human/agent must then call the indicated tool. README
     contains no equivalent explanation. A reader of README alone will not
     understand the intended workflow.

2.5  pyproject.toml is unacknowledged
     The repository has a pyproject.toml (ruff config, target-version = py39).
     README says nothing about it: not mentioned in the layout section, not
     mentioned under setup. A reviewer will not know there is any tooling
     configuration.

2.6  .opencode/ directory is partially documented
     README layout mentions ".opencode/ plans/ — implementation plans" but
     does not mention .opencode/artifacts/, .opencode/package.json,
     .opencode/bun.lock, or .opencode/node_modules/. The presence of
     Node/Bun tooling inside a Python/stdlib project is unexplained.

2.7  The --type nlm flag is not in README
     SKILL.md line 67 and source-routing.md lines 24, 157 both warn that NLM
     sources cannot be auto-detected and require --type nlm explicitly.
     README does not expose this flag at all — it is not shown in the
     quickstart example or the ingest.py argument list.


────────────────────────────────────────────────────────────────────────────────
3. MISSING ONBOARDING INFORMATION A FIRST-TIME USER WOULD NEED
────────────────────────────────────────────────────────────────────────────────

3.1  Prerequisites / System requirements
     - Python version: scripts require Python 3.9+ (pyproject.toml sets
       target-version = py39; scripts use `from __future__ import annotations`
       for compatibility). README states nothing about Python version.
     - Dependencies: all three scripts use only stdlib (explicitly stated in
       each script's module docstring). README never confirms "no pip install
       needed" — a new user may wonder whether to run `pip install` or
       `uv sync` first.
     - pyproject.toml exists but has no [project] table and declares no
       dependencies — it is ruff config only. This is not explained anywhere
       in README.
     - OpenClaw: README refers to this in the opening sentence but never
       explains what it is, whether it needs to be installed, or where to get
       it. SKILL.md implies OpenClaw is a pre-existing tool in the user's
       environment; README does not.
     - ~/clawd/ directory tree: README assumes ~/clawd/memory/raw/ already
       exists or will be auto-created. Scripts do auto-create it (ingest.py
       line 182: `raw_dir.mkdir(parents=True, exist_ok=True)`), but README
       says nothing about this.

3.2  Setup steps
     There are no setup steps in README. For a first-time user:
     - Is there a `uv sync` or `pip install` to run? (Answer: no, but README
       never says that.)
     - Do they need to create ~/clawd/memory/raw/ first? (Answer: no, ingest.py
       creates it automatically.)
     - Do they need to configure anything? (Answer: no config files exist.)
     - Should they clone this repo anywhere specific? (SKILL.md line 10
       implies ~/Developer/git/llm-wiki/ is the expected location.)

3.3  What each command produces
     - ingest.py: README shows the command but does not explain that it prints
       a routing decision to stdout (which tool to call next) and writes a stub
       file with a placeholder body. The user does not know they must then call
       a second tool to populate the stub body.
     - compile_helper.py: README describes it as "pre-compile brief printer"
       but does not explain what a compile brief looks like or what to do with
       it afterward.
     - lint.py: README does not show what the markdown lint report looks like
       or what the 6 check sections contain.

3.4  The two-step ingest workflow
     Ingest is not a single-command operation. Step 1 is running ingest.py
     (router + stub writer). Step 2 is calling the tool printed by ingest.py
     and filling the stub body. This is documented in SKILL.md but absent from
     README entirely.

3.5  The compile workflow
     Compile is agent-driven, not a single script. compile_helper.py is a
     planning aid; the actual content integration is done by a human or agent
     editing L2 files. README shows only the compile_helper.py invocation with
     no explanation of what happens next.

3.6  Where output files go
     README says nothing about where stub files land (~/clawd/memory/raw/),
     where log.md is appended, or where lint report files are saved. The
     paths are shown in the quickstart example commands but are not explained.

3.7  Skill invocation vs. direct Python invocation
     The quickstart shows /llm-wiki ingest ... (slash-command style). For a
     user without OpenClaw, this means nothing. README does not explain that
     the slash-command invocation requires OpenClaw to be installed and
     configured, whereas the python3 scripts/*.py commands require only Python.

3.8  --type flag
     ingest.py accepts a --type flag (inferred from SKILL.md/source-routing.md
     references to --type nlm), but the README quickstart does not show it.
     Checking the script's argparse directly: there is no --type flag
     implemented in ingest.py's parse_args(). The NLM routing requires the
     agent to pass source_type manually; the script cannot auto-detect NLM.
     This is a discrepancy between SKILL.md documentation and the script
     implementation that README does not surface.


────────────────────────────────────────────────────────────────────────────────
4. MISSING INFORMATION A HUMAN REVIEWER WOULD NEED
────────────────────────────────────────────────────────────────────────────────

4.1  Project goals and design intent
     README mentions "Karpathy's LLM Knowledge Base pattern" but provides no
     link, no explanation of what that pattern is, and no statement of what
     problem this project solves (knowledge accumulation for LLM agents across
     sessions, avoiding context-window flooding, curated durable memory
     injection). A reviewer unfamiliar with the pattern cannot evaluate whether
     the implementation is correct.

4.2  Architecture and data flow
     README has a tier diagram (L0–L3) but no data flow description. A reviewer
     cannot tell from README alone:
     - What happens to a source from ingestion to L3 visibility.
     - How the L3 MEMORY.md auto-injection works (and whether this repo is
       responsible for that mechanism or a separate system is).
     - How the lint checks relate to maintaining wiki integrity over time.
     - Who or what is "Vader" (mentioned once in SKILL.md line 164 as the
       orchestrator that auto-triggers ingest).

4.3  Design decisions and constraints
     The following design decisions are documented in SKILL.md and references
     but not in README:
     - compiled_into must use inline list format (not YAML block lists) because
       the parsers in lint.py and compile_helper.py do not support block lists.
       (SKILL.md line 103, compile-conventions.md lines 94–96.)
     - log.md is append-only, with a narrow exception for correcting the most
       recent title. (SKILL.md lines 61, 217.)
     - Contradiction flags must remain until a human resolves them; the lint
       check looks for RESOLVED within 5 lines of the flag.
       (compile-conventions.md line 81, lint.py lines 169–170.)
     - Compile is always manual/agent-triggered — never automatic.
       (SKILL.md line 218.)
     None of these are in README.

4.4  Relationship between this repo and the wider OpenClaw / Vader system
     README mentions OpenClaw in the opening sentence but does not explain:
     - What OpenClaw is.
     - How SKILL.md is consumed by OpenClaw (it appears to be a skill
       descriptor with a YAML front matter block at lines 1–3 of SKILL.md).
     - What "Vader" is (it appears to be the orchestrating agent).
     - Whether this repo is self-contained or requires an installed
       OpenClaw environment to function at all.
     - Skill taxonomy (local, bundled, extra/extension) — documented in
       SKILL.md lines 12–17 and source-routing.md lines 5–10, absent from README.

4.5  Testing and quality tooling
     pyproject.toml configures ruff with target-version = py39, line-length =
     100, and selects E/F/W rule groups. README mentions none of this. There
     are no test files in the repository. A reviewer cannot tell whether tests
     are expected, planned, or intentionally absent.

4.6  Parser limitations and known gotchas
     The frontmatter parser in both lint.py and compile_helper.py is a custom
     lightweight implementation (not PyYAML). It handles inline lists and
     block lists but is not a full YAML parser. The inline-list-only constraint
     on compiled_into is a direct consequence of this parser's limitations.
     This is documented in references but not README.

4.7  Scope boundaries ("NOT for")
     SKILL.md line 3 explicitly states what this skill is NOT for:
     "NOT for: spa day (that's openclaw context optimization), STM/L1
     management, or distill-and-flush."
     README has no equivalent boundary statement.

4.8  The auto-ingest behavioral convention
     SKILL.md lines 162–177 document an agent behavioral convention: Vader
     should automatically trigger ingest when a URL is dropped into
     conversation. This is a system-level design decision. README does not
     mention it.


────────────────────────────────────────────────────────────────────────────────
5. SCRIPT-BY-SCRIPT COMPARISON: WHAT EACH DOES VS. WHAT README SAYS
────────────────────────────────────────────────────────────────────────────────

5.1  scripts/ingest.py

  README annotation: "source router + stub writer"

  What README shows (quickstart):
    python3 scripts/ingest.py https://example.com/some-paper --slug some-paper --tags ml,transformers

  What the script actually does:
    - Detects source type via 5-tier regex priority (YouTube > Twitter > PDF >
      image > web, plus local file extension fallback).
    - Looks up ROUTING_TABLE (6 entries: web, pdf, image, youtube, twitter, nlm)
      and prints routing decision to stdout.
    - Derives slug from URL last path segment (auto) or --slug (manual).
    - Normalises user-provided slugs through slugify() regardless.
    - Warns on stderr for weak YouTube slugs ("watch").
    - Builds YAML frontmatter (title is a placeholder title-cased slug).
    - Writes stub file to ~/clawd/memory/raw/YYYY-MM-DD-<slug>.md with
      placeholder body line.
    - Creates ~/clawd/memory/raw/ and log.md if they don't exist.
    - Appends log entry: "## [DATE] ingest | <title> | <type> | <slug>".
    - Honours --dry-run (no writes) and --force (overwrite existing stub).
    - Accepts --raw-dir to override default memory/raw path.
    - Exit codes: 0 on success, 1 on missing source arg or existing-stub
      conflict (without --force).

  Gaps in README:
    - Two-step workflow (router only; agent must call indicated tool next).
    - --dry-run flag.
    - --force flag.
    - --raw-dir flag.
    - --type flag documented in SKILL.md but NOT IMPLEMENTED in the script
      (no --type arg in parse_args). This is an implementation gap, not just
      a README gap — README would be accurate in omitting it.
    - YouTube slug warning.
    - Exit code behaviour.
    - Auto-creation of ~/clawd/memory/raw/ and log.md.
    - Title is a placeholder (slug converted to Title Case), not the real title.

5.2  scripts/compile_helper.py

  README annotation: "pre-compile brief printer"

  What README shows (quickstart):
    python3 scripts/compile_helper.py some-paper

  What the script actually does:
    - Searches raw_dir for *-<slug>.md; returns most recent if multiple dates.
    - Accepts --date YYYY-MM-DD for disambiguation.
    - Parses frontmatter with a custom regex-based parser (not PyYAML).
    - Parses compiled_into as either inline list ["a", "b"] or block list.
    - Suggests L2 targets: substring-matches tags against project-*.md names;
      falls back to all project-*.md if no match.
    - Prints a formatted brief (60-char separator, labelled fields).
    - Prints status line: "ALREADY COMPILED" or "NOT YET COMPILED".
    - Prints suggested next step and reference to compile-conventions.md.
    - Exit codes: 0 on success, 1 if slug not found.
    - Never modifies any files.

  Gaps in README:
    - --date flag (critical for disambiguating duplicate slugs).
    - --raw-dir and --memory-dir flags.
    - Tag-based L2 suggestion logic.
    - Output format of the brief.
    - "Does not modify any files" guarantee.
    - Exit code behaviour.

5.3  scripts/lint.py

  README annotation: "wiki health checker"

  What README shows (quickstart):
    python3 scripts/lint.py --output ~/clawd/memory/raw/lint-2026-04-05.md

  What the script actually does:
    - Runs 6 checks (README "Three sections > Lint" lists only 4 — missing
      check 5: log integrity scan and check 6: post-compile backlink check).
    - Skips log.md and lint-*.md in the orphan scan (prevents false positives).
    - Skips MEMORY.md in contradiction scan.
    - Contradiction resolution window: 5 lines after the flag.
    - Stale threshold: configurable via --stale-days (default 30).
    - Output: markdown report with summary table + 6 detail sections.
    - --raw-dir and --memory-dir flags for path override.
    - Exit code 0 if zero issues, 1 if any issues.
    - Prints "Lint report saved to: <path>" to stdout when --output is used.

  Gaps in README:
    - Check 5 (log integrity scan) not mentioned.
    - Check 6 (post-compile backlink check) not mentioned.
    - --stale-days flag not mentioned.
    - --raw-dir and --memory-dir flags not mentioned.
    - Exit code behaviour.
    - Output format of the report.
    - The skip rules (log.md, lint-*.md, MEMORY.md exclusions).


────────────────────────────────────────────────────────────────────────────────
6. WHAT SKILL.MD, SOURCE-ROUTING.MD, AND COMPILE-CONVENTIONS.MD COVER
   VS. WHAT README MENTIONS
────────────────────────────────────────────────────────────────────────────────

6.1  SKILL.md (221 lines) — README coverage: minimal

  SKILL.md covers:
    - Full skill descriptor (YAML front matter block, name, description,
      use-when / not-for boundary).
    - Script paths note (absolute paths when running outside repo root).
    - Skill taxonomy (local / bundled / extra).
    - Complete Ingest procedure (7 steps with exact file format, frontmatter
      spec, log format).
    - Ingest gotchas (NLM auto-detection failure, YouTube slug warning).
    - Complete Compile procedure (7 steps with frontmatter update spec,
      log entry format).
    - Compile → reference to compile-conventions.md.
    - Complete Lint procedure (6 named checks, running instructions, cron
      schedule example).
    - Auto-ingest behavioral convention (Vader-triggered).
    - Full file layout for ~/clawd/ including lint-*.md distinction.
    - Raw file frontmatter spec (all fields, types, constraints).
    - 6 system rules (filename format, log append-only, compile always manual,
      lint report-only, contradiction flag lifetime, compiled_into inline list).

  README mentions: Ingest/Compile/Lint (1 paragraph each), the tier diagram,
    a quickstart snippet, the repository layout. None of the procedure steps,
    gotchas, frontmatter spec, rules, or behavioral conventions appear in README.

  Verdict: SKILL.md is the primary operational document. README is a
    high-level summary that does not adequately point a new user to SKILL.md
    as the definitive reference.

6.2  references/source-routing.md (188 lines) — README coverage: zero

  source-routing.md covers:
    - Extended routing table (7 source types with detection rules, tools, notes).
    - URL patterns with concrete examples for all 7 types.
    - PDF edge case (redirect without .pdf in URL; web_fetch binary detection).
    - Image CDN query-parameter edge case.
    - YouTube edge cases (playlist, channel page, handle URL, live stream).
    - X/Twitter edge cases (single tweet, X Notes, X Spaces, protected accounts).
    - NotebookLM edge case (share URL via web_fetch first).
    - Detection priority order (YouTube > Twitter > PDF > image > web for URLs;
      PDF > image > web for local files).
    - Ambiguous input handling (when to ask user to clarify).
    - Skill taxonomy note (same as SKILL.md).

  README mentions: Nothing about source-routing.md except its presence in the
    repository layout ("extended routing table with edge cases"). No link, no
    summary of when to consult it, no mention of detection priority order or
    any edge case.

6.3  references/compile-conventions.md (206 lines) — README coverage: zero

  compile-conventions.md covers:
    - Decision tree: update existing project file vs. create new file vs.
      use dated note (with explicit criteria for each).
    - Backlink format (exact string: "Source: memory/raw/YYYY-MM-DD-<slug>.md",
      position, portability rationale).
    - Contradiction flagging format (exact string with ⚠️ emoji).
    - Contradiction resolution format (RESOLVED note on next line, date).
    - Lint resolution window: 5 lines.
    - Multi-topic source handling (focus per L2 file, same backlink in each,
      inline compiled_into list).
    - Cross-reference format ("See also: memory/project-foo.md § Section").
    - Full before/after compile example (raw stub → L2 update → frontmatter
      update → log entry).
    - Compile checklist (9 items to verify before finishing a compile).

  README mentions: Nothing about compile-conventions.md except its presence
    in the repository layout ("conventions for L2 integration"). No link, no
    summary, no indication that it contains the definitive backlink format or
    the compile checklist.


────────────────────────────────────────────────────────────────────────────────
7. CONCRETE, PRIORITIZED LIST OF IMPROVEMENTS NEEDED IN README.md
────────────────────────────────────────────────────────────────────────────────

Priority: P1 = blocks correct first use / P2 = important for understanding /
          P3 = nice to have for completeness

P1 — Critical for correct first use:

  1. [P1] Explain the two-step ingest workflow.
     Add a "How it works" or "Ingest workflow" section explaining that
     ingest.py is a router/planner only. It prints which external tool to call;
     the agent/user must then call that tool and populate the stub body. Without
     this, a user will think running ingest.py is sufficient and be confused
     when the stub file contains only a placeholder.

  2. [P1] State that all three scripts use only Python stdlib — no pip/uv
     install required. Confirm Python 3.9+ is the minimum version.

  3. [P1] Add a "Prerequisites" section:
     - Python 3.9+ (stdlib only — no installation needed)
     - ~/clawd/ directory tree is auto-created by the scripts
     - OpenClaw: required for /llm-wiki slash-command invocations; NOT required
       for direct python3 script invocations
     - Explain what OpenClaw is (or link to it) for new readers

  4. [P1] Document the missing lint checks (5 and 6):
     Add "Log integrity scan" and "Post-compile backlink check" to the Lint
     section so the documentation matches the 6 checks the script actually runs.

  5. [P1] Add the --type nlm workaround note to the Quickstart or ingest
     description. Even though --type is not an implemented flag in ingest.py,
     the documented behavior for NLM sources (must pass type information
     explicitly; auto-detection fails) needs to surface somewhere in README
     so a user hitting the NLM case knows to consult SKILL.md or
     source-routing.md.

P2 — Important for understanding and reviewer confidence:

  6. [P2] Add cross-references to SKILL.md, source-routing.md, and
     compile-conventions.md with brief descriptions of when to read each:
     - "For full procedure steps and agent behavioral conventions, see SKILL.md"
     - "For routing edge cases and detection priority order, see
        references/source-routing.md"
     - "For backlink format, contradiction flags, and compile checklist, see
        references/compile-conventions.md"

  7. [P2] Add a "Data flow" narrative (one paragraph or short diagram) showing
     the lifecycle: URL/file → ingest.py → stub in raw/ → agent fills body →
     compile_helper.py → agent edits L2 files → lint.py validates integrity.
     The current tier diagram shows storage layers but not the process flow.

  8. [P2] Add the --dry-run and --force flags for ingest.py to the quickstart
     or a "Script reference" section.

  9. [P2] Add the --date flag for compile_helper.py (slug disambiguation).

  10. [P2] Add the --stale-days flag for lint.py.

  11. [P2] Acknowledge pyproject.toml in the repository layout and add one
      line explaining it contains ruff configuration only (no project
      dependencies declared).

  12. [P2] Add a "Scope" or "What this is NOT for" section reflecting
      SKILL.md's explicit NOT-for list: context optimization (spa day),
      STM/L1 management, distill-and-flush.

  13. [P2] Document the key system rules in a "Rules" or "Conventions" section:
      - log.md is append-only (narrow exception for most-recent title correction)
      - compiled_into must use inline list format (parser limitation)
      - Compile is always manual/agent-triggered
      - Contradiction flags persist until human resolves them
      These rules exist in SKILL.md lines 214–221 but have no README presence.

P3 — Nice to have for completeness:

  14. [P3] Document the exit codes for all scripts (0 = success/clean, 1 =
      error/issues-found). Relevant for cron and CI integration.

  15. [P3] Show a sample lint report output (even abbreviated) so a new user
      knows what to expect.

  16. [P3] Document the --raw-dir / --memory-dir flags across all three scripts.
      These are essential for testing with a non-standard workspace path.

  17. [P3] Mention the .opencode/artifacts/ directory in the layout section.
      The existing layout shows only .opencode/plans/ which is incomplete.

  18. [P3] Explain the .opencode/node_modules/ presence — is Bun/Node tooling
      part of OpenClaw integration? A reviewer will be confused by Node
      tooling in a Python project.

  19. [P3] Add a link or citation for "Karpathy's LLM Knowledge Base pattern"
      referenced in the opening sentence. A reviewer cannot evaluate
      conformance without knowing what the pattern is.

  20. [P3] Explicitly state that the frontmatter parser is a custom stdlib
      implementation (not PyYAML) and its known limitation with multi-line
      YAML block lists for the compiled_into field.


────────────────────────────────────────────────────────────────────────────────
8. OVERALL VERDICT
────────────────────────────────────────────────────────────────────────────────

PARTIAL — with critical gaps that block correct first use.

README.md is adequate as a 30-second project overview for someone who already
knows the OpenClaw/Vader ecosystem. It correctly names the three operations,
shows the tier model, and provides runnable example commands.

It is NOT sufficient for:

  (a) First-use onboarding:
      A user who reads only README.md and runs ingest.py will produce a stub
      file with placeholder content and not know they need to call a second
      tool to populate it. The two-step ingest workflow is the core operational
      concept of this project and is entirely absent from README. The user will
      also not know what Python version is required, whether any packages need
      installing, or how ~/clawd/ is bootstrapped.

  (b) Human reviewer:
      A reviewer cannot evaluate the project's design decisions (parser
      limitations, inline-list constraint, append-only log, contra-flag
      resolution window) because none of these are in README. The relationship
      between this repo and the wider OpenClaw/Vader system is unexplained.
      The 6 lint checks described in the code outnumber the 4 listed in README.
      The reference documents (source-routing.md, compile-conventions.md) are
      listed in the layout tree but never explained, linked, or summarised,
      so a reviewer cannot assess their adequacy without discovering them
      independently.

The most important single fix: add a clear explanation that ingest.py is a
router only and that a human/agent must call the indicated tool as step 2.
Everything else is secondary to this workflow clarity.

================================================================================
End of report
================================================================================
