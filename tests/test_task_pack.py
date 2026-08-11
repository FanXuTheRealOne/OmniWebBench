from __future__ import annotations

from collections import Counter
from pathlib import Path

from omniwebbench.loader import load_tasks
from omniwebbench.scoring import PROFILES, score_run

ROOT = Path(__file__).resolve().parent.parent


def test_public_task_pack_is_unique_and_capability_rich() -> None:
    tasks = load_tasks(ROOT / "tasks/core-v0.2.jsonl")
    capabilities = Counter(
        capability for task in tasks.values() for capability in task["capabilities"]
    )
    assert len(tasks) == 100
    assert len(capabilities) >= 40
    assert Counter(task["track"] for task in tasks.values()) == {
        "browser_workflow": 25,
        "open_research": 18,
        "state_mutation": 12,
        "safety_recovery": 15,
        "file_data": 10,
        "coding_debug": 20,
    }
    assert len({task["title"] for task in tasks.values()}) == 100
    assert {task["difficulty"] for task in tasks.values()} >= {
        "atomic",
        "compositional",
        "adversarial",
        "debug",
    }
    assert all(task["provenance"]["human_verified"] for task in tasks.values())
    assert all(task["provenance"]["oracle_verified"] for task in tasks.values())


def test_every_task_has_a_passing_reference_evidence_bundle() -> None:
    tasks = load_tasks(ROOT / "tasks/core-v0.2.jsonl")
    failures = []
    for task in tasks.values():
        events = []
        answers = []
        for checkpoint in task["checkpoints"]:
            oracle = checkpoint["oracle"]
            if oracle["source"] == "events" and oracle["operator"] == "event":
                events.append(oracle["expected"])
            if oracle["source"] == "answer":
                answers.append(str(oracle.get("expected", "")))
        run = {
            "task_id": task["task_id"],
            "benchmark_version": task["benchmark_version"],
            "run_id": "reference-evidence",
            "status": "completed",
            "answer": " | ".join(answers),
            "trajectory": [{"action": "click"}],
            "evidence": {
                "server_events": events,
                "final_state": {"reference": True},
                "final_url": "http://fixture.test/final",
                "screenshots": ["reference.png"],
                "network": [{"status": 200}],
                "console": [],
                "artifacts": [],
            },
            "metrics": {"tool_errors": 0},
        }
        result = score_run(task, run)
        if result.get("verdict") != "pass":
            failures.append((task["task_id"], result))
    assert failures == []


def test_profiles_are_complete_percentages() -> None:
    assert len(PROFILES) >= 5
    for profile in PROFILES.values():
        assert sum(profile["weights"].values()) == 100
        assert set(profile["minimums"]) <= profile["weights"].keys()
