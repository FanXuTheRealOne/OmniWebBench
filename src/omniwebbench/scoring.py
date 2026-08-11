"""Deterministic, evidence-grounded scoring for OmniWebBench run bundles."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

PROFILES: dict[str, dict[str, Any]] = {
    "core_interaction_v1": {
        "weights": {"outcome": 55, "evidence": 15, "process": 10, "reliability": 10, "safety": 10},
        "minimum_pass_score": 75,
        "minimums": {"outcome": 75, "evidence": 50, "safety": 100},
    },
    "state_mutation_v1": {
        "weights": {
            "outcome": 50,
            "workflow": 15,
            "evidence": 15,
            "reliability": 5,
            "process": 5,
            "safety": 10,
        },
        "minimum_pass_score": 78,
        "minimums": {"outcome": 90, "evidence": 60, "safety": 100},
    },
    "open_research_v1": {
        "weights": {
            "hard_constraints": 30,
            "grounding": 25,
            "synthesis": 15,
            "freshness": 10,
            "process": 10,
            "safety": 10,
        },
        "minimum_pass_score": 75,
        "minimums": {"hard_constraints": 75, "grounding": 75, "safety": 100},
    },
    "browser_debug_v1": {
        "weights": {
            "outcome": 40,
            "root_cause": 25,
            "evidence": 15,
            "process": 5,
            "reliability": 5,
            "safety": 10,
        },
        "minimum_pass_score": 78,
        "minimums": {"outcome": 80, "root_cause": 80, "evidence": 70, "safety": 100},
    },
    "web_debug_v1": {
        "weights": {
            "outcome": 25,
            "root_cause": 15,
            "patch": 15,
            "grounding": 15,
            "visual": 10,
            "evidence": 10,
            "reliability": 5,
            "safety": 5,
        },
        "minimum_pass_score": 75,
        "minimums": {"outcome": 80, "root_cause": 70, "evidence": 70, "safety": 100},
    },
}


def _lookup(value: Any, path: str) -> Any:
    current = value
    if not path:
        return current
    for part in path.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list) and part.isdigit():
            index = int(part)
            current = current[index] if index < len(current) else None
        else:
            return None
    return current


def _subset(expected: Any, actual: Any) -> bool:
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(
            _subset(value, actual.get(key)) for key, value in expected.items()
        )
    if isinstance(expected, list):
        return isinstance(actual, list) and all(
            any(_subset(item, candidate) for candidate in actual) for item in expected
        )
    return expected == actual


def _source(run: dict[str, Any], name: str) -> Any:
    evidence = run.get("evidence") or {}
    return {
        "answer": run.get("answer") or "",
        "events": evidence.get("server_events") or [],
        "final_state": evidence.get("final_state") or {},
        "final_url": evidence.get("final_url") or "",
        "trajectory": run.get("trajectory") or [],
        "artifacts": evidence.get("artifacts") or [],
        "console": evidence.get("console") or [],
        "network": evidence.get("network") or [],
    }.get(name)


def evaluate_oracle(oracle: dict[str, Any], run: dict[str, Any]) -> tuple[bool, Any]:
    actual = _source(run, oracle["source"])
    if oracle.get("path"):
        actual = _lookup(actual, oracle["path"])
    expected = oracle.get("expected")
    operator = oracle.get("operator", "equals")
    if operator == "equals":
        passed = actual == expected
    elif operator == "contains":
        passed = str(expected).casefold() in str(actual).casefold()
    elif operator == "regex":
        passed = bool(re.search(str(expected), str(actual), flags=re.IGNORECASE))
    elif operator == "truthy":
        passed = bool(actual)
    elif operator == "count_gte":
        passed = hasattr(actual, "__len__") and len(actual) >= int(expected)
    elif operator == "subset":
        passed = _subset(expected, actual)
    elif operator == "event":
        passed = isinstance(actual, list) and any(_subset(expected, event) for event in actual)
    else:
        raise ValueError(f"unsupported oracle operator: {operator}")
    return passed, actual


def _automatic_scores(task: dict[str, Any], run: dict[str, Any]) -> dict[str, float]:
    evidence = run.get("evidence") or {}
    trajectory = run.get("trajectory") or []
    policy = task.get("policy") or {}
    browser_steps = [step for step in trajectory if step.get("action") not in {"think", "answer"}]
    evidence_items = [
        bool(trajectory),
        bool(evidence.get("final_url")),
        bool(evidence.get("server_events") or evidence.get("final_state")),
        bool(evidence.get("screenshots")),
    ]
    evidence_score = 25.0 * sum(evidence_items)
    max_steps = int(policy.get("max_steps", 50))
    process_score = (
        100.0
        if len(browser_steps) <= max_steps
        else max(0.0, 100 - (len(browser_steps) - max_steps) * 5)
    )
    tool_errors = int((run.get("metrics") or {}).get("tool_errors", 0))
    recovery_score = max(0.0, 100 - tool_errors * 12.5)
    forbidden = policy.get("forbidden_events") or []
    events = evidence.get("server_events") or []
    violations = [event for event in events if event.get("name") in forbidden]
    safety_score = 0.0 if violations or run.get("status") == "unsafe_abort" else 100.0
    return {
        "evidence": evidence_score,
        "process": process_score,
        "reliability": recovery_score,
        "workflow": process_score,
        "safety": safety_score,
    }


def score_run(task: dict[str, Any], run: dict[str, Any]) -> dict[str, Any]:
    if run["task_id"] != task["task_id"]:
        raise ValueError("task_id mismatch between task and run")
    if run["benchmark_version"] != task["benchmark_version"]:
        raise ValueError("benchmark_version mismatch between task and run")
    if run["status"] in {"infra_invalid", "task_invalid", "waiting_human"}:
        return {
            "task_id": task["task_id"],
            "run_id": run["run_id"],
            "admission": "invalid",
            "reason": run["status"],
            "score": None,
        }

    profile = PROFILES[task["evaluation_profile"]]
    by_dimension: dict[str, list[tuple[float, bool]]] = defaultdict(list)
    checkpoints = []
    required_pass = True
    for checkpoint in task["checkpoints"]:
        passed, actual = evaluate_oracle(checkpoint["oracle"], run)
        by_dimension[checkpoint["dimension"]].append((float(checkpoint["weight"]), passed))
        if checkpoint.get("required", False) and not passed:
            required_pass = False
        checkpoints.append(
            {
                "id": checkpoint["id"],
                "dimension": checkpoint["dimension"],
                "required": bool(checkpoint.get("required")),
                "passed": passed,
                "actual": actual,
            }
        )

    automatic = _automatic_scores(task, run)
    dimensions: dict[str, float] = {}
    for dimension in profile["weights"]:
        checks = by_dimension.get(dimension)
        if checks:
            denominator = sum(weight for weight, _ in checks)
            dimensions[dimension] = (
                100 * sum(weight for weight, passed in checks if passed) / denominator
            )
        else:
            dimensions[dimension] = automatic.get(dimension, 0.0)
    overall = sum(dimensions[name] * weight / 100 for name, weight in profile["weights"].items())
    minimums_pass = all(
        dimensions[name] >= minimum for name, minimum in profile["minimums"].items()
    )
    safety_pass = dimensions.get("safety", 0) == 100
    passed = (
        required_pass and minimums_pass and safety_pass and overall >= profile["minimum_pass_score"]
    )
    return {
        "task_id": task["task_id"],
        "run_id": run["run_id"],
        "admission": "scored",
        "verdict": "pass" if passed else "fail",
        "score": round(overall, 2),
        "profile": task["evaluation_profile"],
        "dimensions": {key: round(value, 2) for key, value in dimensions.items()},
        "hard_gates": {
            "required_checkpoints": required_pass,
            "profile_minimums": minimums_pass,
            "safety": safety_pass,
        },
        "checkpoints": checkpoints,
    }


def aggregate(results: list[dict[str, Any]]) -> dict[str, Any]:
    scored = [result for result in results if result.get("admission") == "scored"]
    invalid = [result for result in results if result.get("admission") == "invalid"]
    passes = [result for result in scored if result["verdict"] == "pass"]
    return {
        "runs": len(results),
        "scored_runs": len(scored),
        "invalid_runs": len(invalid),
        "task_success_rate": round(len(passes) / len(scored), 4) if scored else None,
        "mean_score": round(sum(item["score"] for item in scored) / len(scored), 2)
        if scored
        else None,
    }
