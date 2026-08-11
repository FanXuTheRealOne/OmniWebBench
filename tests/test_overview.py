import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_overview_is_current_and_complete() -> None:
    namespace = runpy.run_path(str(ROOT / "scripts" / "build_overview.py"))
    generated = namespace["build"]()
    committed = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")

    assert committed == generated
    assert committed.count('class="task-card"') == 24
    assert "24 ≠ 130" in committed
    assert "36" in committed
    assert "browser_debug_v1" in committed
    assert "web_debug_v1" in committed
    assert "https://cdn" not in committed
    assert "<script src=" not in committed
