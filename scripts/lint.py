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

REPO_ROOT = Path(__file__).resolve().parents[1]
MEMORY_RAW_DIR = Path.home() / "clawd" / "memory" / "raw"
MEMORY_DIR = Path.home() / "clawd" / "memory"
DEFAULT_POLICY_FILE = REPO_ROOT / "references" / "lint-policy.md"
DEFAULT_LOG_FILE = REPO_ROOT / "artifacts" / "log.md"

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
        stripped = line.lstrip()
        if stripped.startswith("- ") and pending_list_key is not None:
            item = stripped[2:].strip().strip('"').strip("'")
            fm[pending_list_key].append(item)
            continue
        pending_list_key = None
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if value == "":
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
# Policy helpers
# ---------------------------------------------------------------------------


def parse_iso_date(value: str | None) -> date | None:
    """Parse YYYY-MM-DD into a date, returning None on failure."""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def infer_file_date(md_file: Path, fm: dict, preferred_key: str | None = None) -> date | None:
    """Infer the best date associated with a raw file or frontmatter block."""
    candidate_keys: list[str] = []
    if preferred_key:
        candidate_keys.append(preferred_key)
    candidate_keys.extend(["compiled_date", "date_ingested"])
    for key in candidate_keys:
        parsed = parse_iso_date(fm.get(key, ""))
        if parsed:
            return parsed
    stem_match = re.match(r"^(\d{4}-\d{2}-\d{2})-", md_file.name)
    if stem_match:
        return parse_iso_date(stem_match.group(1))
    return None


def in_enforcement_scope(item_date: date | None, enforce_after: date | None) -> bool:
    """Return True when an item should be enforced under the current policy."""
    if enforce_after is None:
        return True
    if item_date is None:
        return False
    return item_date >= enforce_after


def load_policy(policy_file: Path) -> dict:
    """Load lint policy from a markdown file with YAML-style frontmatter."""
    default_policy = {
        "policy_file": str(policy_file),
        "enforce_after": None,
        "legacy_files": set(),
        "compile_event_suffixes": [],
    }
    if not policy_file.exists():
        return default_policy

    text = read_file_safe(policy_file)
    fm = parse_frontmatter(text)

    legacy_files = fm.get("legacy_files", [])
    if isinstance(legacy_files, str):
        legacy_files = [legacy_files]

    suffixes = fm.get("compile_event_suffixes", [])
    if isinstance(suffixes, str):
        suffixes = [suffixes]

    return {
        "policy_file": str(policy_file),
        "enforce_after": parse_iso_date(fm.get("enforce_after", "")),
        "legacy_files": set(legacy_files),
        "compile_event_suffixes": suffixes,
    }


# ---------------------------------------------------------------------------
# Lint checks
# ---------------------------------------------------------------------------


def check_orphans(raw_dir: Path, enforce_after: date | None = None) -> list[dict]:
    """List in-scope raw files with compiled: false."""
    results = []
    if not raw_dir.exists():
        return results
    for md_file in sorted(raw_dir.glob("*.md")):
        if md_file.name == "log.md" or md_file.name.startswith("lint-"):
            continue
        text = read_file_safe(md_file)
        fm = parse_frontmatter(text)
        if not in_enforcement_scope(infer_file_date(md_file, fm, preferred_key="date_ingested"), enforce_after):
            continue
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


def check_stale(raw_dir: Path, stale_days: int = 30, enforce_after: date | None = None) -> list[dict]:
    """List in-scope raw files compiled more than stale_days ago."""
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
        compiled_date = infer_file_date(md_file, fm, preferred_key="compiled_date")
        if not in_enforcement_scope(compiled_date, enforce_after):
            continue
        if compiled_date is None:
            continue
        if compiled_date < cutoff:
            results.append(
                {
                    "file": md_file.name,
                    "path": str(md_file),
                    "title": fm.get("title", "(no title)"),
                    "compiled_date": compiled_date.isoformat(),
                    "days_ago": (date.today() - compiled_date).days,
                    "compiled_into": fm.get("compiled_into", "[]"),
                }
            )
    return results


CONTRADICTION_RE = re.compile(r"⚠️ CONTRADICTION:", re.IGNORECASE)
RESOLVED_RE = re.compile(r"RESOLVED", re.IGNORECASE)


def check_contradictions(memory_dir: Path, legacy_files: set[str] | None = None) -> list[dict]:
    """Scan non-legacy L2 memory files for unresolved contradiction flags."""
    results = []
    legacy_files = legacy_files or set()
    if not memory_dir.exists():
        return results
    for md_file in sorted(memory_dir.glob("*.md")):
        if md_file.name == "MEMORY.md" or md_file.name in legacy_files:
            continue
        text = read_file_safe(md_file)
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if CONTRADICTION_RE.search(line):
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
SECTION_HEADER_RE = re.compile(r"^(#{1,4})\s+(.+)")


def check_orphan_l2(memory_dir: Path, legacy_files: set[str] | None = None) -> tuple[list[dict], list[dict]]:
    """Find uncited sections in project files, split into current vs legacy backlog.

    Migration-aware policy:
    - if a file is listed as legacy in lint policy, all uncited sections are legacy
    - if a project file has never had any raw backlink, all uncited sections are legacy
    - if a project file has at least one raw backlink, uncited sections before the first
      backlink are treated as legacy backlog; uncited sections after that point are treated
      as current orphan-L2 issues

    Scope note:
    - only level-2 (`##`) sections are scanned as top-level units
    """
    current_results = []
    legacy_results = []
    legacy_files = legacy_files or set()
    if not memory_dir.exists():
        return current_results, legacy_results

    for md_file in sorted(memory_dir.glob("project-*.md")):
        text = read_file_safe(md_file)
        lines = text.splitlines()
        first_backlink_line = None
        for i, line in enumerate(lines, start=1):
            if BACKLINK_RE.search(line):
                first_backlink_line = i
                break

        sections: list[dict] = []
        current_section: dict | None = None
        for i, line in enumerate(lines):
            header_match = SECTION_HEADER_RE.match(line)
            if header_match and header_match.group(1) == "##":
                if current_section is not None:
                    sections.append(current_section)
                current_section = {
                    "header": line.strip(),
                    "line_number": i + 1,
                    "has_backlink": False,
                }
            elif current_section is not None and BACKLINK_RE.search(line):
                current_section["has_backlink"] = True
        if current_section is not None:
            sections.append(current_section)

        for section in sections:
            if section["has_backlink"]:
                continue
            item = {
                "file": md_file.name,
                "path": str(md_file),
                "section": section["header"],
                "line_number": section["line_number"],
            }
            if (
                md_file.name in legacy_files
                or first_backlink_line is None
                or section["line_number"] < first_backlink_line
            ):
                legacy_results.append(item)
            else:
                current_results.append(item)
    return current_results, legacy_results


INGEST_LOG_RE = re.compile(r"^## \[(\d{4}-\d{2}-\d{2})\] ingest \| .+ \| .+ \| (.+)$")
COMPILE_LOG_RE = re.compile(
    r"^## \[(\d{4}-\d{2}-\d{2})\] compile \| (.+?) \| files updated: .+$"
)


def expand_compile_slug_candidates(slug: str, compile_event_suffixes: list[str]) -> list[str]:
    """Return raw-file slug candidates for compile log events.

    Compile log entries may describe a later compile event rather than a distinct raw file,
    for example `<slug>-second-pass`. Policy controls which suffixes are recognized.
    """
    candidates = [slug]
    for suffix in compile_event_suffixes:
        if slug.endswith(suffix):
            candidates.append(slug[: -len(suffix)])
    return candidates


def check_log_integrity(
    raw_dir: Path,
    log_file: Path,
    enforce_after: date | None = None,
    compile_event_suffixes: list[str] | None = None,
) -> list[dict]:
    """Warn for post-cutoff log entries whose referenced raw source has no file on disk."""
    results = []
    compile_event_suffixes = compile_event_suffixes or []
    if not log_file.exists():
        return results
    log_text = read_file_safe(log_file)
    for i, line in enumerate(log_text.splitlines(), start=1):
        text = line.strip()
        ingest_match = INGEST_LOG_RE.match(text)
        compile_match = COMPILE_LOG_RE.match(text)

        if ingest_match:
            entry_date_str, slug = ingest_match.groups()
            if not in_enforcement_scope(parse_iso_date(entry_date_str), enforce_after):
                continue
            slug_candidates = [slug]
        elif compile_match:
            entry_date_str, slug = compile_match.groups()
            if not in_enforcement_scope(parse_iso_date(entry_date_str), enforce_after):
                continue
            slug_candidates = expand_compile_slug_candidates(slug, compile_event_suffixes)
        else:
            continue

        matches = []
        for candidate in slug_candidates:
            matches.extend(raw_dir.glob(f"*-{candidate}.md"))
        if not matches:
            results.append(
                {
                    "line_number": i,
                    "line": text,
                    "slug": slug,
                }
            )
    return results


def check_compile_backlinks(
    raw_dir: Path,
    memory_dir: Path,
    enforce_after: date | None = None,
) -> list[dict]:
    """For each in-scope compiled raw file, verify at least one L2 file has its backlink."""
    results = []
    if not raw_dir.exists():
        return results

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
        if not in_enforcement_scope(infer_file_date(md_file, fm, preferred_key="compiled_date"), enforce_after):
            continue
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
    legacy_orphan_l2: list[dict],
    log_integrity: list[dict],
    compile_backlinks: list[dict],
    raw_dir: Path,
    memory_dir: Path,
    log_file: Path,
    policy: dict,
) -> str:
    today = date.today().isoformat()
    lines: list[str] = []

    lines.append(f"# llm-wiki lint report — {today}")
    lines.append("")
    lines.append(f"Scanned: `{raw_dir}` (raw) | `{memory_dir}` (L2 memory) | `{log_file}` (log)")
    lines.append(f"Policy: `{policy['policy_file']}`")
    if policy["enforce_after"]:
        lines.append(f"Enforce-after: `{policy['enforce_after'].isoformat()}`")
    if policy["legacy_files"]:
        lines.append(
            "Legacy files: "
            + ", ".join(f"`{name}`" for name in sorted(policy["legacy_files"]))
        )
    lines.append("")

    total_issues = (
        len(orphans)
        + len(stale)
        + len(contradictions)
        + len(orphan_l2)
        + len(log_integrity)
        + len(compile_backlinks)
    )
    lines.append(f"**Total current issues: {total_issues}**")
    lines.append(f"**Legacy migration backlog: {len(legacy_orphan_l2)}**")
    lines.append("")
    lines.append("| Check | Issues |")
    lines.append("|---|---|")
    lines.append(f"| 1. Orphan scan (uncompiled raw) | {len(orphans)} |")
    lines.append(f"| 2. Stale scan (compiled >30 days) | {len(stale)} |")
    lines.append(f"| 3. Contradiction scan | {len(contradictions)} |")
    lines.append(f"| 4. Orphan L2 scan (no backlink) | {len(orphan_l2)} |")
    lines.append(f"| 5. Log integrity (orphaned log entries) | {len(log_integrity)} |")
    lines.append(f"| 6. Post-compile backlink check | {len(compile_backlinks)} |")
    lines.append(f"| Legacy uncited L2 backlog | {len(legacy_orphan_l2)} |")
    lines.append("")

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

    lines.append("---")
    lines.append("")
    lines.append(f"## Stale scan — {len(stale)} compiled raw source(s) older than 30 days")
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
            lines.append(f"- `{item['file']}` line {item['line_number']}: {item['line']}")
    else:
        lines.append("_No unresolved contradiction flags found._")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(
        f"## Orphan L2 scan — {len(orphan_l2)} current section(s) with no raw source backlink"
    )
    lines.append("")
    if orphan_l2:
        lines.append(
            "These sections appear in llm-wiki-managed portions of project files and have no `Source: memory/raw/...` backlink."
        )
        lines.append("")
        for item in orphan_l2:
            lines.append(f"- `{item['file']}` line {item['line_number']}: {item['section']}")
    else:
        lines.append("_No current orphan L2 sections found._")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"## Legacy uncited L2 scan — {len(legacy_orphan_l2)} backlog section(s)")
    lines.append("")
    if legacy_orphan_l2:
        lines.append(
            "These sections are treated as migration backlog under the current lint policy, not as fresh llm-wiki failures."
        )
        lines.append("")
        for item in legacy_orphan_l2:
            lines.append(f"- `{item['file']}` line {item['line_number']}: {item['section']}")
    else:
        lines.append("_No legacy uncited L2 backlog found._")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"## Log integrity scan — {len(log_integrity)} orphaned log entry(ies)")
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
    lines.append("_Lint report is read-only. No automatic fixes were made. Human decides on actions._")

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
        "--log-file",
        default=str(DEFAULT_LOG_FILE),
        help=f"append-only ingest/compile log file (default: {DEFAULT_LOG_FILE}).",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Save lint report to this file path instead of printing to stdout.",
    )
    parser.add_argument(
        "--policy-file",
        default=str(DEFAULT_POLICY_FILE),
        help=f"Markdown lint policy file with frontmatter (default: {DEFAULT_POLICY_FILE}).",
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
    log_file = Path(args.log_file)
    policy = load_policy(Path(args.policy_file))
    enforce_after = policy["enforce_after"]
    legacy_files = policy["legacy_files"]
    compile_event_suffixes = policy["compile_event_suffixes"]

    orphans = check_orphans(raw_dir, enforce_after=enforce_after)
    stale = check_stale(raw_dir, stale_days=args.stale_days, enforce_after=enforce_after)
    contradictions = check_contradictions(memory_dir, legacy_files=legacy_files)
    orphan_l2, legacy_orphan_l2 = check_orphan_l2(memory_dir, legacy_files=legacy_files)
    log_integrity = check_log_integrity(
        raw_dir,
        log_file,
        enforce_after=enforce_after,
        compile_event_suffixes=compile_event_suffixes,
    )
    compile_backlinks = check_compile_backlinks(
        raw_dir,
        memory_dir,
        enforce_after=enforce_after,
    )

    report = build_report(
        orphans,
        stale,
        contradictions,
        orphan_l2,
        legacy_orphan_l2,
        log_integrity,
        compile_backlinks,
        raw_dir,
        memory_dir,
        log_file,
        policy,
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
