"""Reports must be portable across machines with different locale encodings."""

from __future__ import annotations

from pathlib import Path

from pytest import MonkeyPatch

from agent_eval.store import EvaluationStore


def test_report_symbols_can_be_saved_with_a_windows_default_encoding(
    tmp_path: Path, monkeypatch: MonkeyPatch,
) -> None:
    store = EvaluationStore(tmp_path, "eval-test").create()
    original_write_text = Path.write_text

    def windows_write_text(
        path: Path, data: str, encoding: str | None = None,
        errors: str | None = None, newline: str | None = None,
    ) -> int:
        return original_write_text(
            path, data, encoding=encoding or "cp1252", errors=errors, newline=newline,
        )

    monkeypatch.setattr(Path, "write_text", windows_write_text)
    report = '<meta charset="utf-8"><p>Correctness Δ → improved</p>'
    path = store.write_text("report.html", report)
    assert path.read_bytes().decode("utf-8") == report
