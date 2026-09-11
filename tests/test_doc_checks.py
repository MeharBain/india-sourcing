from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

CHECKER = Path(__file__).parents[1] / "scripts" / "check_docs.py"
START = "<!-- CANONICAL HIGH-RISK LIST START -->"
END = "<!-- CANONICAL HIGH-RISK LIST END -->"
HIGH_RISK = "A diff requires two independent reviewers if it:\n\n- changes `one`;"


def _write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _task(*, impact: str = "semantic", body: str = "") -> str:
    impact_metadata = {
        "semantic": "**Sweep terms:** `term`; `synonym`\n",
        "structural": "**Affected paths:** `docs/example.md`\n",
        "none": "",
    }[impact]
    semantic_scope = ""
    if impact == "semantic":
        semantic_scope = """
### Pre-approval impact sweep

Included with dispositions: `PRD.md`, `docs/DECISIONS.md`, the current-state block of
`PROGRESS.md`, `docs/CONTEXT.md`, and `docs/tasks/018-example.md`.
Additional dependents: none. Every pre-Gate-1 hit is recorded with a disposition.
"""
    return f"""# 018 — Example

**Status:** proposed
**Branch:** task/018-example
**Depends on:** none
**Documentation impact:** {impact}
{impact_metadata}
## Intent

Intent.

## Interpretations

None; the request was unambiguous.

## Scope

Scope.
{semantic_scope}
{body}

## Out of scope

- Nothing else.

## Acceptance criteria

1. It works.

## Files expected to change

```
docs/tasks/018-example.md
```

## Risks

- Drift.

## Blockers and questions

*(none at creation)*
"""


@pytest.fixture
def valid_tree(tmp_path: Path) -> Path:
    config = {
        "minimum_task_number": 18,
        "markdown_paths": ["AGENTS.md", "docs"],
        "high_risk_list": {
            "owner_path": "docs/tasks/README.md",
            "mirror_paths": ["AGENTS.md", "docs/AGENT_ARCHITECTURE.md", "policy.toml"],
            "start_marker": START,
            "end_marker": END,
        },
        "retired_phrases": [{"phrase": "retired phrase", "paths": ["AGENTS.md"]}],
    }
    _write(tmp_path, "docs/doc-checks.json", json.dumps(config))
    marked = f"{START}\n{HIGH_RISK}\n{END}\n"
    _write(tmp_path, "docs/tasks/README.md", marked)
    _write(tmp_path, "AGENTS.md", marked)
    _write(tmp_path, "docs/AGENT_ARCHITECTURE.md", marked)
    _write(tmp_path, "policy.toml", marked)
    _write(tmp_path, "docs/tasks/018-example.md", _task())
    return tmp_path


def _run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), "--root", str(root)],
        check=False,
        capture_output=True,
        text=True,
    )


def test_valid_fixture_passes_with_one_concise_line(valid_tree: Path) -> None:
    result = _run(valid_tree)

    assert result.returncode == 0
    assert result.stdout.splitlines() == ["Documentation checks passed."]
    assert result.stderr == ""


@pytest.mark.parametrize(
    ("content", "reason"),
    [
        (_task().replace("## Risks\n\n- Drift.\n\n", ""), "missing required section 'Risks'"),
        (
            _task().replace(
                "## Intent\n\nIntent.\n\n## Interpretations\n\nNone; the request was unambiguous.",
                "## Interpretations\n\nNone; the request was unambiguous.\n\n## Intent\n\nIntent.",
            ),
            "required sections are out of order",
        ),
    ],
)
def test_missing_or_out_of_order_sections_fail(
    valid_tree: Path, content: str, reason: str
) -> None:
    _write(valid_tree, "docs/tasks/018-example.md", content)

    result = _run(valid_tree)

    assert result.returncode == 1
    assert "docs/tasks/018-example.md" in result.stderr
    assert reason in result.stderr


def test_missing_semantic_sweep_metadata_fails(valid_tree: Path) -> None:
    _write(valid_tree, "docs/tasks/018-example.md", _task().replace("**Sweep terms:**", "**Terms:**"))

    result = _run(valid_tree)

    assert result.returncode == 1
    assert "docs/tasks/018-example.md" in result.stderr
    assert "semantic task is missing Sweep terms metadata" in result.stderr


def test_nonexistent_internal_path_fails(valid_tree: Path) -> None:
    _write(valid_tree, "AGENTS.md", f"{START}\n{HIGH_RISK}\n{END}\n[Missing](docs/missing.md)\n")

    result = _run(valid_tree)

    assert result.returncode == 1
    assert "AGENTS.md" in result.stderr
    assert "linked path does not exist: docs/missing.md" in result.stderr


def test_nonexistent_explicit_heading_fragment_fails(valid_tree: Path) -> None:
    _write(valid_tree, "docs/target.md", "# Present heading\n")
    _write(
        valid_tree,
        "AGENTS.md",
        f"{START}\n{HIGH_RISK}\n{END}\n[Missing heading](docs/target.md#absent-heading)\n",
    )

    result = _run(valid_tree)

    assert result.returncode == 1
    assert "AGENTS.md" in result.stderr
    assert "heading fragment does not exist: docs/target.md#absent-heading" in result.stderr


def test_changed_high_risk_mirror_fails(valid_tree: Path) -> None:
    _write(valid_tree, "policy.toml", f"{START}\nchanged\n{END}\n")

    result = _run(valid_tree)

    assert result.returncode == 1
    assert "policy.toml" in result.stderr
    assert "canonical high-risk list differs from docs/tasks/README.md" in result.stderr


def test_retired_phrase_fails_only_in_configured_paths(valid_tree: Path) -> None:
    _write(valid_tree, "docs/history.md", "retired phrase\n")
    allowed = _run(valid_tree)
    assert allowed.returncode == 0

    agents = (valid_tree / "AGENTS.md").read_text(encoding="utf-8")
    _write(valid_tree, "AGENTS.md", f"{agents}retired phrase\n")

    rejected = _run(valid_tree)

    assert rejected.returncode == 1
    assert "AGENTS.md" in rejected.stderr
    assert "contains configured retired phrase: retired phrase" in rejected.stderr
    assert "docs/history.md" not in rejected.stderr
