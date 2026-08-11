"""Load and validate benchmark task and run records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REQUIRED_TASK_FIELDS = {
    "schema_version",
    "task_id",
    "benchmark_version",
    "split",
    "title",
    "intent",
    "capabilities",
    "difficulty",
    "environment",
    "checkpoints",
    "policy",
    "evaluation_profile",
    "repeat_count",
    "provenance",
}

REQUIRED_RUN_FIELDS = {
    "schema_version",
    "run_id",
    "task_id",
    "benchmark_version",
    "agent",
    "status",
    "trajectory",
    "evidence",
    "metrics",
    "environment",
}


class ValidationError(ValueError):
    """Raised when a benchmark record violates the public contract."""


def _records(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    if source.suffix == ".jsonl":
        try:
            return [json.loads(line) for line in text.splitlines() if line.strip()]
        except json.JSONDecodeError as exc:
            raise ValidationError(f"invalid JSONL in {source}: {exc}") from exc
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {source}: {exc}") from exc
    return value if isinstance(value, list) else [value]


def validate_task(task: dict[str, Any]) -> None:
    missing = REQUIRED_TASK_FIELDS.difference(task)
    if missing:
        raise ValidationError(f"task is missing fields: {sorted(missing)}")
    if task["schema_version"] != "omniwebbench.task.v1":
        raise ValidationError(f"unsupported task schema: {task['schema_version']}")
    if not task["task_id"].startswith("owb-"):
        raise ValidationError("task_id must start with 'owb-'")
    if not task["capabilities"] or len(task["capabilities"]) != len(set(task["capabilities"])):
        raise ValidationError(f"{task['task_id']}: capabilities must be unique and non-empty")
    if not task["checkpoints"]:
        raise ValidationError(f"{task['task_id']}: at least one checkpoint is required")
    checkpoint_ids = [item["id"] for item in task["checkpoints"]]
    if len(checkpoint_ids) != len(set(checkpoint_ids)):
        raise ValidationError(f"{task['task_id']}: checkpoint ids must be unique")
    for checkpoint in task["checkpoints"]:
        if checkpoint.get("weight", 0) <= 0:
            raise ValidationError(f"{task['task_id']}: checkpoint weight must be positive")
        if not checkpoint.get("oracle"):
            raise ValidationError(f"{task['task_id']}: checkpoint oracle is required")
    if not 1 <= int(task["repeat_count"]) <= 5:
        raise ValidationError(f"{task['task_id']}: repeat_count must be within 1..5")


def validate_run(run: dict[str, Any]) -> None:
    missing = REQUIRED_RUN_FIELDS.difference(run)
    if missing:
        raise ValidationError(f"run is missing fields: {sorted(missing)}")
    if run["schema_version"] != "omniwebbench.run.v1":
        raise ValidationError(f"unsupported run schema: {run['schema_version']}")
    if run["status"] not in {
        "completed",
        "partial",
        "agent_error",
        "infra_invalid",
        "task_invalid",
        "waiting_human",
        "unsafe_abort",
    }:
        raise ValidationError(f"unsupported run status: {run['status']}")


def load_tasks(path: str | Path) -> dict[str, dict[str, Any]]:
    tasks: dict[str, dict[str, Any]] = {}
    for task in _records(path):
        validate_task(task)
        if task["task_id"] in tasks:
            raise ValidationError(f"duplicate task_id: {task['task_id']}")
        tasks[task["task_id"]] = task
    return tasks


def load_runs(path: str | Path) -> list[dict[str, Any]]:
    runs = _records(path)
    for run in runs:
        validate_run(run)
    return runs
