from __future__ import annotations

from collections import Counter
from pathlib import Path

from omniwebbench.loader import load_tasks
from omniwebbench.scoring import PROFILES

ROOT = Path(__file__).resolve().parent.parent


def test_public_task_pack_is_unique_and_capability_rich() -> None:
    tasks = load_tasks(ROOT / "tasks/core-v0.1.jsonl")
    capabilities = Counter(
        capability for task in tasks.values() for capability in task["capabilities"]
    )
    assert len(tasks) == 24
    assert len(capabilities) >= 25
    assert {task["difficulty"] for task in tasks.values()} >= {
        "atomic",
        "compositional",
        "adversarial",
        "debug",
    }
    assert all(task["provenance"]["human_verified"] for task in tasks.values())
    assert all(task["provenance"]["oracle_verified"] for task in tasks.values())


def test_profiles_are_complete_percentages() -> None:
    assert len(PROFILES) >= 5
    for profile in PROFILES.values():
        assert sum(profile["weights"].values()) == 100
        assert set(profile["minimums"]) <= profile["weights"].keys()
