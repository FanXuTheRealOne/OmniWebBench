#!/usr/bin/env python3
"""Run release-facing integrity checks over all checked-in benchmark contracts."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator

from omniwebbench.loader import load_tasks
from omniwebbench.scoring import PROFILES
from omniwebbench.task_factory import build_dev_tasks

ROOT = Path(__file__).resolve().parent.parent


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    tasks_path = ROOT / "tasks/core-v0.1.jsonl"
    tasks = load_tasks(tasks_path)
    schema = _json(ROOT / "schemas/task.schema.json")
    validator = Draft202012Validator(schema)
    errors = []
    for task in tasks.values():
        errors.extend(
            f"{task['task_id']}: {error.message}" for error in validator.iter_errors(task)
        )
    generated = "".join(json.dumps(task, ensure_ascii=False) + "\n" for task in build_dev_tasks())
    if generated != tasks_path.read_text(encoding="utf-8"):
        errors.append("checked-in task pack differs from task_factory output")
    if any(sum(profile["weights"].values()) != 100 for profile in PROFILES.values()):
        errors.append("one or more score profiles do not sum to 100")
    capabilities = Counter(
        capability for task in tasks.values() for capability in task["capabilities"]
    )
    report = {
        "status": "failed" if errors else "ok",
        "benchmark_version": "0.1.0",
        "tasks": len(tasks),
        "capabilities": len(capabilities),
        "profiles": len(PROFILES),
        "task_pack_sha256": hashlib.sha256(tasks_path.read_bytes()).hexdigest(),
        "errors": errors,
    }
    print(json.dumps(report, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
