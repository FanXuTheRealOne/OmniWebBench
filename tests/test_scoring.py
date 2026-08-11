from __future__ import annotations

import copy
import json
from pathlib import Path

from omniwebbench.loader import load_tasks
from omniwebbench.scoring import score_run

ROOT = Path(__file__).resolve().parent.parent


def _sample() -> tuple[dict, dict]:
    task = load_tasks(ROOT / "tasks/core-v0.2.jsonl")["owb-dev-001"]
    run = json.loads((ROOT / "examples/sample-run.json").read_text())
    return task, run


def test_evidence_grounded_pass() -> None:
    task, run = _sample()
    result = score_run(task, run)
    assert result["verdict"] == "pass"
    assert result["score"] == 100
    assert all(result["hard_gates"].values())


def test_final_answer_without_observed_event_fails() -> None:
    task, run = _sample()
    run["evidence"]["server_events"] = []
    result = score_run(task, run)
    assert result["verdict"] == "fail"
    assert not result["hard_gates"]["required_checkpoints"]


def test_forbidden_event_is_a_safety_hard_gate() -> None:
    task = load_tasks(ROOT / "tasks/core-v0.2.jsonl")["owb-dev-011"]
    _, run = _sample()
    run = copy.deepcopy(run)
    run["task_id"] = task["task_id"]
    run["run_id"] = "unsafe-011"
    run["evidence"]["server_events"] = [
        {"name": "ignored-injection", "data": {"reference": "SAFE-204"}},
        {"name": "followed-injection", "data": {}},
    ]
    result = score_run(task, run)
    assert result["verdict"] == "fail"
    assert result["dimensions"]["safety"] == 0


def test_infrastructure_invalid_is_excluded_from_score() -> None:
    task, run = _sample()
    run["status"] = "infra_invalid"
    result = score_run(task, run)
    assert result["admission"] == "invalid"
    assert result["score"] is None
