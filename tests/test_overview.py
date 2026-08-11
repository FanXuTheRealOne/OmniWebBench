import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_overview_is_current_and_complete() -> None:
    namespace = runpy.run_path(str(ROOT / "scripts" / "build_overview.py"))
    generated = namespace["build"]()
    committed = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")

    assert committed == generated
    assert committed.count('class="task-card"') == 100
    assert "100 / 1,000" in committed
    assert "Coding/Debug 20" in committed
    assert "browser_debug_v1" in committed
    assert "web_debug_v1" in committed
    assert "https://cdn" not in committed
    assert "<script src=" not in committed
