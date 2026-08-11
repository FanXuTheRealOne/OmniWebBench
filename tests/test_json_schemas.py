from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent


def _json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_task_pack_matches_public_json_schema() -> None:
    validator = Draft202012Validator(_json("schemas/task.schema.json"))
    for line in (ROOT / "tasks/core-v0.2.jsonl").read_text(encoding="utf-8").splitlines():
        validator.validate(json.loads(line))


def test_run_and_submission_examples_match_public_schemas() -> None:
    Draft202012Validator(_json("schemas/run.schema.json")).validate(
        _json("examples/sample-run.json")
    )
    Draft202012Validator(_json("schemas/submission.schema.json")).validate(
        _json("examples/sample-submission.json")
    )
