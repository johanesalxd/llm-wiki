#!/usr/bin/env python3
"""
lint.py — llm-wiki wiki health checker.

Usage:
    python3 lint.py [--raw-dir <path>] [--memory-dir <path>] [--output <path>]

Checks:
  1. Orphan scan:       raw/*.md files with compiled: false
  2. Stale scan:        raw/*.md files compiled > 30 days ago
  3. Contradiction scan: memory/*.md files with unresolved ⚠️ CONTRADICTION: flags
  4. Orphan L2 scan:    memory/project-*.md sections with no backlink to raw source
  5. Log integrity:     log.md entries whose raw file no longer exists (orphaned entries)
  6. Post-compile backlink: compiled raw files with no backlink in any L2 memory file

Prints a markdown lint report to stdout, or saves to --output path.
Never auto-fixes anything.

Uses only stdlib. Compatible with python3 directly (no uv/pip needed).
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

MEMORY_RAW_DIR = Path.home() / "clawd" / "memory" / "raw"
MEMORY_DIR = Path.home() / "clawd" / "memory"

# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    """Parse YAML-like frontmatter into a dict of string or list values.

    Handles both inline values (key: value) and multi-line YAML block lists:
        key:
          - item1
          - item2
    In the block-list case the value is returned as a Python list[str].
    """
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    fm: dict = {}
    lines = match.group(1).splitlines()
    pending_list_key: str | None = None
    for line in lines:
        if line.startswith("- ") and pending_list_key is not None:
            # Continuation of a block list
            item = line[2:].strip().strip('"').strip("'")
            fm[pending_list_key].append(item)
            continue
        # Not a list item — close any pending block list
        pending_list_key = None
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if value == "":
                # Start of a potential block list
                fm[key] = []
                pending_list_key = key
            else:
                fm[key] = value
    return fm


def read_file_safe(path: Path) -> str:
    """Read a file, returning empty string on error."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


# ---------------------------------------------------------------------------
# Lint checks
# ---------------------------------------------------------------------------


def check_orphans(raw_dir: Path) -> list[dict]:
    """List raw files with compiled: false."""
    results = []
    if not raw_dir.exists():
        return results
    for md_file in sorted(raw_dir.glob("*.md")):
        if md_file.name == "log.md" or md_file.name.startswith("lint-"):
            continue
        text = read_file_safe(md_file)
        fm = parse_frontmatter(text)
        compiled_val = fm.get("compiled", "").lower()
        if compiled_val == "false":
            results.append(
                {
                    "file": md_file.name,
                    "path": str(md_file),
                    "title": fm.get("title", "(no title)"),
                    "date_ingested": fm.get("date_ingested", ""),
                    "source_type": fm.get("source_type", ""),
                }
            )
    return results


def check_stale(raw_dir: Path, stale_days: int = 30) -> list[dict]:
    """List raw files compiled more than stale_days ago."""
    results = []
    cutoff = date.today() - timedelta(days=stale_days)
    if not raw_dir.exists():
        return results
    for md_file in sorted(raw_dir.glob("*.md")):
        if md_file.name == "log.md" or md_file.name.startswith("lint-"):
            continue
        text = read_file_safe(md_file)
        fm = parse_frontmatter(text)
        if fm.get("compiled", "").lower() != "true":
            continue
        compiled_date_str = fm.get("compiled_date", "")
        if not compiled_date_str:
            continue
        try:
            compiled_date = datetime.strptime(compiled_date_str, "%Y-%m-%d").date()
        except ValueError:
            continue
        if compiled_date < cutoff:
            results.append(
                {
                    "file": md_file.name,
                    "path": str(md_file),
                    "title": fm.get("title", "(no title)"),
                    "compiled_date": compiled_date_str,
                    "days_ago": (date.today() - compiled_date).days,
                    "compiled_into": fm.get("compiled_into", "[]"),
                }
            )
    return results


CONTRADICTION_RE = re.compile(r"⚠️ CONTRADICTION:", re.IGNORECASE)
# A "resolved" contradiction has a line containing "RESOLVED" after the flag.
RESOLVED_RE = re.compile(r"RESOLVED", re.IGNORECASE)


def check_contradictions(memory_dir: Path) -> list[dict]:
    """Scan L2 memory files for unresolved contradiction flags."""
    results = []
    if not memory_dir.exists():
        return results
    for md_file in sorted(memory_dir.glob("*.md")):
        if md_file.name == "MEMORY.md":
            continue
        text = read_file_safe(md_file)
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if CONTRADICTION_RE.search(line):
                # Check if next few lines contain RESOLVED
                context_lines = lines[i : i + 5]
                resolved = any(RESOLVED_RE.search(cl) for cl in context_lines[1:])
                if not resolved:
                    results.append(
                        {
                            "file": md_file.name,
                            "path": str(md_file),
                            "line_number": i + 1,
                            "line": line.strip(),
                        }
                    )
    return results


BACKLINK_RE = re.compile(r"Source:\s*memory/raw/", re.IGNORECASE)
SECTION_HEADER_RE = re.compile(r"^#{1,4}\s+(.+)")


def check_orphan_l2(memory_dir: Path) -> list[dict]:
    """Find sections in project-*.md files with no backlink to a raw source."""
    results = []
    if not memory_dir.exists():
        return results
    for md_file in sorted(memory_dir.glob("project-*.md")):
        text = read_file_safe(md_file)
        lines = text.splitlines()
        # Split into sections by H2/H3 headers, track whether each has a backlink
        sections: list[dict] = []
        current_section: dict | None = None
        for i, line in enumerate(lines):
            header_match = SECTION_HEADER_RE.match(line)
            if header_match and line.startswith("##"):
                if current_section is not None:
                    sections.append(current_section)
                current_section = {
                    "header": line.strip(),
                    "line_number": i + 1,
                    "has_backlink": False,
                    "lines": [],
                }
            elif current_section is not None:
                current_section["lines"].append(line)
                if BACKLINK_RE.search(line):
                    current_section["has_backlink"] = True
        if current_section is not None:
            sections.append(current_section)

        for section in sections:
            if not section["has_backlink"]:
                results.append(
                    {
                        "file": md_file.name,
                        "path": str(md_file),
                        "section": section["header"],
                        "line_number": section["line_number"],
                    }
                )
    return results


# Check 5: log.md integrity — orphaned log entries with no raw file on disk
INGEST_LOG_RE = re.compile(
    r"^## \[(\d{4}-\d{2}-\d{2})\] ingest \| .+ \| .+ \| (.+)$"
)
COMPILE_LOG_RE = re.compile(
    r"^## \[(\d{4}-\d{2}-\d{2})\] compile \| (.+?) \| files updated: .+$"
)


def check_log_integrity(raw_dir: Path) -> list[dict]:
    """Warn for log entries whose referenced raw source has no file on disk."""
    results = []
    log_path = raw_dir / "log.md"
    if not log_path.exists():
        return results
    log_text = read_file_safe(log_path)
    for i, line in enumerate(log_text.splitlines(), start=1):
        text = line.strip()
        ingest_match = INGEST_LOG_RE.match(text)
        compile_match = COMPILE_LOG_RE.match(text)

        if ingest_match:
            _, slug = ingest_match.groups()
        elif compile_match:
            _, slug = compile_match.groups()
        else:
            continue

        pattern = f"*-{slug}.md"
        matches = list(raw_dir.glob(pattern))
        if not matches:
            results.append(
                {
                    "line_number": i,
                    "line": text,
                    "slug": slug,
                }
            )
    return results


# Check 6: post-compile backlink verification
BACKLINK_SLUG_RE = re.compile(r"Source:\s*memory/raw/[^/\s]+\.md", re.IGNORECASE)


def check_compile_backlinks(raw_dir: Path, memory_dir: Path) -> list[dict]:
    """For each compiled raw file, verify at least one L2 file has its backlink."""
    results = []
    if not raw_dir.exists():
        return results

    # Load all L2 memory file content once
    l2_texts: list[str] = []
    if memory_dir.exists():
        for md_file in memory_dir.glob("*.md"):
            if md_file.name == "MEMORY.md":
                continue
            l2_texts.append(read_file_safe(md_file))

    for md_file in sorted(raw_dir.glob("*.md")):
        if md_file.name == "log.md" or md_file.name.startswith("lint-"):
            continue
        text = read_file_safe(md_file)
        fm = parse_frontmatter(text)
        if fm.get("compiled", "").lower() != "true":
            continue
        # Build expected backlink fragment: memory/raw/YYYY-MM-DD-slug.md
        expected_backlink = f"memory/raw/{md_file.name}"
        found = any(expected_backlink in l2 for l2 in l2_texts)
        if not found:
            results.append(
                {
                    "file": md_file.name,
                    "path": str(md_file),
                    "title": fm.get("title", "(no title)"),
                    "expected_backlink": expected_backlink,
                }
            )
    return results


# ---------------------------------------------------------------------------
# Report builder
# ---------------------------------------------------------------------------


def build_report(
    orphans: list[dict],
    stale: list[dict],
    contradictions: list[dict],
    orphan_l2: list[dict],
    log_integrity: list[dict],
    compile_backlinks: list[dict],
    raw_dir: Path,
    memory_dir: Path,
) -> str:
    today = date.today().isoformat()
    lines: list[str] = []

    lines.append(f"# llm-wiki lint report — {today}")
    lines.append("")
    lines.append(f"Scanned: `{raw_dir}` (raw) | `{memory_dir}` (L2 memory)")
    lines.append("")

    # Summary
    total_issues = (
        len(orphans)
        + len(stale)
        + len(contradictions)
        + len(orphan_l2)
        + len(log_integrity)
        + len(compile_backlinks)
    )
    lines.append(f"**Total issues: {total_issues}**")
    lines.append("")
    lines.append("| Check | Issues |")
    lines.append("|---|---|")
    lines.append(f"| 1. Orphan scan (uncompiled raw) | {len(orphans)} |")
    lines.append(f"| 2. Stale scan (compiled >30 days) | {len(stale)} |")
    lines.append(f"| 3. Contradiction scan | {len(contradictions)} |")
    lines.append(f"| 4. Orphan L2 scan (no backlink) | {len(orphan_l2)} |")
    lines.append(f"| 5. Log integrity (orphaned log entries) | {len(log_integrity)} |")
    lines.append(f"| 6. Post-compile backlink check | {len(compile_backlinks)} |")
    lines.append("")

    # Orphan scan
    lines.append("---")
    lines.append("")
    lines.append(f"## Orphan scan — {len(orphans)} uncompiled raw source(s)")
    lines.append("")
    if orphans:
        lines.append(
            "These raw files have `compiled: false` and have not been integrated into L2 memory."
        )
        lines.append("")
        for item in orphans:
            lines.append(
                f"- `{item['file']}` — {item['title']} ({item['source_type']}, ingested {item['date_ingested']})"
            )
    else:
        lines.append("_No uncompiled raw sources found._")
    lines.append("")

    # Stale scan
    lines.append("---")
    lines.append("")
    lines.append(
        f"## Stale scan — {len(stale)} compiled raw source(s) older than 30 days"
    )
    lines.append("")
    if stale:
        lines.append(
            "These sources were compiled >30 days ago and may need re-review if the topic has evolved."
        )
        lines.append("")
        for item in stale:
            lines.append(
                f"- `{item['file']}` — {item['title']} "
                f"(compiled {item['compiled_date']}, {item['days_ago']} days ago)"
            )
    else:
        lines.append("_No stale compiled sources found._")
    lines.append("")

    # Contradiction scan
    lines.append("---")
    lines.append("")
    lines.append(f"## Contradiction scan — {len(contradictions)} unresolved flag(s)")
    lines.append("")
    if contradictions:
        lines.append(
            "These L2 memory files contain `⚠️ CONTRADICTION:` flags without a RESOLVED note."
        )
        lines.append("")
        for item in contradictions:
            lines.append(
                f"- `{item['file']}` line {item['line_number']}: {item['line']}"
            )
    else:
        lines.append("_No unresolved contradiction flags found._")
    lines.append("")

    # Orphan L2 scan
    lines.append("---")
    lines.append("")
    lines.append(
        f"## Orphan L2 scan — {len(orphan_l2)} section(s) with no raw source backlink"
    )
    lines.append("")
    if orphan_l2:
        lines.append(
            "These sections in project files have no `Source: memory/raw/...` backlink — "
            "knowledge asserted without a cited source."
        )
        lines.append("")
        for item in orphan_l2:
            lines.append(
                f"- `{item['file']}` line {item['line_number']}: {item['section']}"
            )
    else:
        lines.append("_No orphan L2 sections found._")
    lines.append("")

    # Check 5: log integrity
    lines.append("---")
    lines.append("")
    lines.append(
        f"## Log integrity scan — {len(log_integrity)} orphaned log entry(ies)"
    )
    lines.append("")
    if log_integrity:
        lines.append(
            "These `log.md` entries reference a slug with no corresponding raw file on disk."
        )
        lines.append("")
        for item in log_integrity:
            lines.append(
                f"- line {item['line_number']}: slug `{item['slug']}` — `{item['line']}`"
            )
    else:
        lines.append("_No orphaned log entries found._")
    lines.append("")

    # Check 6: post-compile backlink verification
    lines.append("---")
    lines.append("")
    lines.append(
        f"## Post-compile backlink check — {len(compile_backlinks)} compiled file(s) with no L2 backlink"
    )
    lines.append("")
    if compile_backlinks:
        lines.append(
            "These raw files are marked `compiled: true` but no L2 memory file contains "
            "a `Source: memory/raw/<file>` backlink. They may be orphaned post-compile."
        )
        lines.append("")
        for item in compile_backlinks:
            lines.append(
                f"- `{item['file']}` — {item['title']} "
                f"(expected backlink: `{item['expected_backlink']}`)"
            )
    else:
        lines.append("_All compiled files have at least one L2 backlink._")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(
        "_Lint report is read-only. No automatic fixes were made. Human decides on actions._"
    )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="lint.py",
        description=(
            "llm-wiki wiki health checker.\n\n"
            "Scans memory/raw/ and memory/ for issues: uncompiled sources, "
            "stale compiled docs, unresolved contradictions, and uncited L2 sections.\n\n"
            "Never auto-fixes — report only."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--raw-dir",
        default=str(MEMORY_RAW_DIR),
        help=f"memory/raw directory to scan (default: {MEMORY_RAW_DIR}).",
    )
    parser.add_argument(
        "--memory-dir",
        default=str(MEMORY_DIR),
        help=f"L2 memory directory to scan (default: {MEMORY_DIR}).",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Save lint report to this file path instead of printing to stdout.",
    )
    parser.add_argument(
        "--stale-days",
        type=int,
        default=30,
        help="Days threshold for stale compiled sources (default: 30).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    raw_dir = Path(args.raw_dir)
    memory_dir = Path(args.memory_dir)

    orphans = check_orphans(raw_dir)
    stale = check_stale(raw_dir, stale_days=args.stale_days)
    contradictions = check_contradictions(memory_dir)
    orphan_l2 = check_orphan_l2(memory_dir)
    log_integrity = check_log_integrity(raw_dir)
    compile_backlinks = check_compile_backlinks(raw_dir, memory_dir)

    report = build_report(
        orphans,
        stale,
        contradictions,
        orphan_l2,
        log_integrity,
        compile_backlinks,
        raw_dir,
        memory_dir,
    )

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        print(f"Lint report saved to: {output_path}")
    else:
        print(report)

    total_issues = (
        len(orphans)
        + len(stale)
        + len(contradictions)
        + len(orphan_l2)
        + len(log_integrity)
        + len(compile_backlinks)
    )
    return 0 if total_issues == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
