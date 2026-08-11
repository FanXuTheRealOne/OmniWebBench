#!/usr/bin/env python3
"""Generate the checked-in deterministic development task pack."""

from __future__ import annotations

import json
from pathlib import Path

from omniwebbench.task_factory import build_dev_tasks

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    output = ROOT / "tasks/core-v0.1.jsonl"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "".join(json.dumps(task, ensure_ascii=False) + "\n" for task in build_dev_tasks()),
        encoding="utf-8",
    )
    print(f"wrote {len(build_dev_tasks())} tasks to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
