"""Run bounded, dependency-free documentation checks.

This checker validates only configured mechanical rules. It does not infer a task's
documentation-impact classification, judge semantic consistency, or reject historical wording
unless an exact phrase/path pair is explicitly configured.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

REQUIRED_SECTIONS = [
    "Intent",
    "Interpretations",
    "Scope",
    "Out of scope",
    "Acceptance criteria",
    "Files expected to change",
    "Risks",
    "Blockers and questions",
]
REQUIRED_METADATA = ["Status", "Branch", "Depends on", "Documentation impact"]
VALID_IMPACTS = {"none", "structural", "semantic"}
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
HEADING_PATTERN = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _read(path: Path, root: Path, errors: list[str]) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"{_relative(path, root)}: cannot read file: {exc}")
        return None


def _metadata(content: str, name: str) -> str | None:
    match = re.search(rf"^\*\*{re.escape(name)}:\*\*\s*(.+?)\s*$", content, re.MULTILINE)
    return match.group(1).strip() if match else None


def _section_body(content: str, heading: str, level: int) -> str | None:
    prefix = "#" * level
    match = re.search(rf"^{prefix}\s+{re.escape(heading)}\s*$", content, re.MULTILINE)
    if match is None:
        return None
    remainder = content[match.end() :]
    next_heading = re.search(rf"^#{{1,{level}}}\s+", remainder, re.MULTILINE)
    return remainder[: next_heading.start()] if next_heading else remainder


def _evidence_entries(content: str) -> list[str]:
    bullets = re.findall(r"(?ms)^-\s+.*?(?=^-\s+|^#{1,6}\s+|\Z)", content)
    paragraphs = [
        paragraph
        for paragraph in re.split(r"\n\s*\n", content)
        if not re.search(r"(?m)^-\s+", paragraph)
    ]
    return [entry.strip() for entry in [*bullets, *paragraphs] if entry.strip()]


def _has_bounded_disposition(entry: str) -> bool:
    if re.search(r"\bincluded\b", entry, re.IGNORECASE):
        return True
    excluded = re.search(r"\bexcluded\b", entry, re.IGNORECASE)
    if excluded is None:
        return False
    remainder = entry[excluded.end() :]
    return bool(re.search(r"(?:[:—-]|\bbecause\b|\bas\b)\s*\S+", remainder))


def _has_disposition_for_tokens(entries: list[str], tokens: list[str]) -> bool:
    for entry in entries:
        lowered = entry.lower()
        if all(token.lower() in lowered for token in tokens) and _has_bounded_disposition(entry):
            return True
    return False


def _has_additional_dependent_evidence(sweep: str, entries: list[str]) -> bool:
    for explicit in entries:
        if "additional dependents" not in explicit.lower():
            continue
        detail = re.split(r"additional dependents(?:\s+are)?\s*:?", explicit, flags=re.IGNORECASE)
        if len(detail) > 1 and (
            re.search(r"\bnone\b", detail[1], re.IGNORECASE)
            or re.search(r"(?:[\w./-]+\.(?:md|toml|py|json)|\.codex/agents)", detail[1])
        ):
            return True

    # Some already-approved Task 018-era specs combine the dependent inventory with a bounded
    # hit-disposition section. Accept that form only when its declared search command names a
    # non-core policy path; a free-floating path elsewhere in the task is not sufficient.
    return bool(
        re.search(r"(?im)^hit dispositions:\s*$", sweep)
        and re.search(
            r"(?s)```powershell.*?(?:AGENTS\.md|docs/AGENT_ARCHITECTURE\.md|\.codex/agents).*?```",
            sweep,
        )
    )


def _has_hit_disposition_evidence(sweep: str) -> bool:
    marker = re.search(
        r"(?im)^(?:pre-approval hits?[^\n]*dispositions[^\n]*|pre-gate-1 hit dispositions|"
        r"hit dispositions|every live hit[^\n]*disposed[^\n]*):?\s*$",
        sweep,
    )
    return marker is not None and bool(re.search(r"(?m)^-\s+", sweep[marker.end() :]))


def _check_task(path: Path, root: Path, errors: list[str]) -> None:
    content = _read(path, root, errors)
    if content is None:
        return
    relative = _relative(path, root)

    for metadata in REQUIRED_METADATA:
        if _metadata(content, metadata) is None:
            errors.append(f"{relative}: missing required metadata '{metadata}'")

    headings = re.findall(r"^##\s+(.+?)\s*$", content, re.MULTILINE)
    missing = [section for section in REQUIRED_SECTIONS if section not in headings]
    for section in missing:
        errors.append(f"{relative}: missing required section '{section}'")
    if not missing:
        positions = [headings.index(section) for section in REQUIRED_SECTIONS]
        if positions != sorted(positions):
            errors.append(f"{relative}: required sections are out of order")
        intent_position = headings.index("Intent")
        if intent_position + 1 >= len(headings) or headings[intent_position + 1] != "Interpretations":
            errors.append(f"{relative}: 'Interpretations' must appear immediately after 'Intent'")

    impact = _metadata(content, "Documentation impact")
    if impact is None:
        return
    if impact not in VALID_IMPACTS:
        errors.append(
            f"{relative}: Documentation impact must be one of none, structural, or semantic"
        )
        return
    if impact == "none":
        return
    if impact == "structural":
        if _metadata(content, "Affected paths") is None:
            errors.append(f"{relative}: structural task is missing Affected paths metadata")
        return

    if _metadata(content, "Sweep terms") is None:
        errors.append(f"{relative}: semantic task is missing Sweep terms metadata")
    scope = _section_body(content, "Scope", 2)
    sweep = _section_body(scope or "", "Pre-approval impact sweep", 3)
    if sweep is None:
        errors.append(f"{relative}: semantic task is missing a pre-approval impact sweep")
        return

    entries = _evidence_entries(sweep)
    core_targets = [
        ("PRD.md", ["PRD.md"]),
        ("docs/DECISIONS.md", ["docs/DECISIONS.md"]),
        ("the current-state block of PROGRESS.md", ["current-state", "PROGRESS.md"]),
        ("docs/CONTEXT.md", ["docs/CONTEXT.md"]),
    ]
    for label, tokens in core_targets:
        if not _has_disposition_for_tokens(entries, tokens):
            errors.append(
                f"{relative}: pre-approval sweep lacks an included/excluded disposition for "
                f"{label}"
            )

    if not (
        _has_disposition_for_tokens(entries, [relative])
        or _has_disposition_for_tokens(entries, ["this task file"])
    ):
        errors.append(
            f"{relative}: pre-approval sweep lacks an included/excluded disposition for its "
            "own task file"
        )
    if not _has_additional_dependent_evidence(sweep, entries):
        errors.append(f"{relative}: pre-approval sweep does not list additional dependents")
    if not _has_hit_disposition_evidence(sweep):
        errors.append(f"{relative}: pre-approval sweep does not record hit dispositions")


def _configured_markdown_files(root: Path, configured: list[str], errors: list[str]) -> list[Path]:
    files: set[Path] = set()
    for relative in configured:
        path = root / relative
        if not path.exists():
            errors.append(f"{relative}: configured Markdown path does not exist")
        elif path.is_dir():
            files.update(path.rglob("*.md"))
        elif path.suffix.lower() == ".md":
            files.add(path)
        else:
            errors.append(f"{relative}: configured Markdown path is not Markdown")
    return sorted(files)


def _heading_slugs(content: str) -> set[str]:
    slugs: set[str] = set()
    counts: dict[str, int] = {}
    for heading in HEADING_PATTERN.findall(content):
        plain = re.sub(r"[`*_~]", "", heading).strip().lower()
        slug = re.sub(r"[^\w\- ]", "", plain, flags=re.UNICODE)
        slug = re.sub(r"\s+", "-", slug)
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        slugs.add(slug if count == 0 else f"{slug}-{count}")
    return slugs


def _check_links(path: Path, root: Path, errors: list[str]) -> None:
    content = _read(path, root, errors)
    if content is None:
        return
    relative = _relative(path, root)
    in_fence = False
    searchable_lines: list[str] = []
    for line in content.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            searchable_lines.append(line)
    for raw_target in LINK_PATTERN.findall("\n".join(searchable_lines)):
        target = raw_target.strip()
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE):
            continue
        path_part, separator, fragment = target.partition("#")
        decoded_path = unquote(path_part)
        linked = path if not decoded_path else root / decoded_path
        if not linked.exists():
            errors.append(f"{relative}: linked path does not exist: {decoded_path}")
            continue
        if separator:
            linked_content = _read(linked, root, errors)
            if linked_content is not None and unquote(fragment) not in _heading_slugs(linked_content):
                display = f"{decoded_path}#{fragment}" if decoded_path else f"#{fragment}"
                errors.append(f"{relative}: heading fragment does not exist: {display}")


def _marked_block(
    path: Path, root: Path, start: str, end: str, errors: list[str]
) -> str | None:
    content = _read(path, root, errors)
    if content is None:
        return None
    relative = _relative(path, root)
    if content.count(start) != 1 or content.count(end) != 1:
        errors.append(f"{relative}: expected exactly one canonical high-risk marker block")
        return None
    before, remainder = content.split(start, 1)
    block, after = remainder.split(end, 1)
    if before is None or after is None:
        return None
    return block.strip().replace("\r\n", "\n")


def _check_high_risk(root: Path, config: dict[str, object], errors: list[str]) -> None:
    owner_relative = str(config["owner_path"])
    start = str(config["start_marker"])
    end = str(config["end_marker"])
    owner = _marked_block(root / owner_relative, root, start, end, errors)
    if owner is None:
        return
    for mirror_relative in config["mirror_paths"]:
        mirror_path = root / str(mirror_relative)
        mirror = _marked_block(mirror_path, root, start, end, errors)
        if mirror is not None and mirror != owner:
            errors.append(
                f"{mirror_relative}: canonical high-risk list differs from {owner_relative}"
            )


def check(root: Path, config_path: Path) -> list[str]:
    errors: list[str] = []
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"{config_path}: cannot load configuration: {exc}"]

    minimum = int(config["minimum_task_number"])
    task_directory = root / "docs" / "tasks"
    for path in sorted(task_directory.glob("[0-9][0-9][0-9]-*.md")):
        if int(path.name[:3]) >= minimum:
            _check_task(path, root, errors)

    markdown_files = _configured_markdown_files(root, config["markdown_paths"], errors)
    for path in markdown_files:
        _check_links(path, root, errors)

    _check_high_risk(root, config["high_risk_list"], errors)

    for rule in config["retired_phrases"]:
        phrase = str(rule["phrase"])
        for relative in rule["paths"]:
            path = root / str(relative)
            content = _read(path, root, errors)
            if content is not None and phrase in content:
                errors.append(f"{relative}: contains configured retired phrase: {phrase}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Check bounded documentation invariants.")
    parser.add_argument("--root", type=Path, help="Repository root (defaults to script parent).")
    arguments = parser.parse_args()
    root = (arguments.root or Path(__file__).resolve().parents[1]).resolve()
    errors = check(root, root / "docs" / "doc-checks.json")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Documentation checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
