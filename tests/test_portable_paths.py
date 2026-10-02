"""Nested harness files must stay out of evaluated patches on every platform."""

from __future__ import annotations

from pathlib import Path

from agent_eval.harness import snapshot_harness
from agent_eval.workspace import create_workspace


def test_nested_harness_paths_use_git_separators(tmp_path: Path) -> None:
    harness = tmp_path / "harness"
    skill = harness / ".claude" / "skills" / "example" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("Follow the project conventions.\n", encoding="utf-8")
    snapshot = snapshot_harness(harness)
    assert [file.path for file in snapshot.files] == [".claude/skills/example/SKILL.md"]


def test_nested_harness_files_never_leak_into_the_evaluated_patch(tmp_path: Path) -> None:
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    (fixture / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
    harness = tmp_path / "harness"
    skill = harness / ".claude" / "skills" / "example" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("Follow the project conventions.\n", encoding="utf-8")
    workspace = create_workspace(fixture, tmp_path / "workspace")
    copied = workspace.overlay(harness, exclude_from_git=True)
    assert copied == [".claude/skills/example/SKILL.md"]
    assert workspace.changed_files() == []
    assert workspace.diff() == ""
