#!/usr/bin/env python3
"""Generate the checked-in deterministic development task pack."""

from __future__ import annotations

import json
from pathlib import Path

from omniwebbench.task_factory import build_dev_tasks, build_legacy_tasks

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    packs = {
        ROOT / "tasks/core-v0.1.jsonl": build_legacy_tasks(),
        ROOT / "tasks/core-v0.2.jsonl": build_dev_tasks(),
    }
    for output, tasks in packs.items():
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            "".join(json.dumps(task, ensure_ascii=False) + "\n" for task in tasks),
            encoding="utf-8",
        )
        print(f"wrote {len(tasks)} tasks to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
