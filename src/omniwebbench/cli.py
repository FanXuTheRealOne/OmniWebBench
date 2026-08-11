"""Command-line interface for OmniWebBench."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from omniwebbench import __version__
from omniwebbench.fixture import serve
from omniwebbench.loader import ValidationError, load_runs, load_tasks
from omniwebbench.report import write_html_report, write_json_report
from omniwebbench.scoring import PROFILES, score_run

DEFAULT_TASKS = Path(__file__).resolve().parents[2] / "tasks/core-v0.2.jsonl"


def _tasks(path: str | Path | None) -> dict:
    source = Path(path) if path else DEFAULT_TASKS
    if not source.exists():
        raise ValidationError(f"task pack not found: {source}; pass --tasks explicitly")
    return load_tasks(source)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="omniwebbench", description="Capability-first evaluation for web agents"
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="validate a task pack or run bundle")
    validate.add_argument("path")
    validate.add_argument("--kind", choices=["tasks", "runs"], default="tasks")
    listing = sub.add_parser("list", help="list tasks")
    listing.add_argument("--tasks")
    listing.add_argument("--capability")
    show = sub.add_parser("show", help="print one task")
    show.add_argument("task_id")
    show.add_argument("--tasks")
    score = sub.add_parser("score", help="score one or more run bundles")
    score.add_argument("runs")
    score.add_argument("--tasks")
    score.add_argument("--output")
    report = sub.add_parser("report", help="score runs and write JSON + HTML reports")
    report.add_argument("runs")
    report.add_argument("--tasks")
    report.add_argument("--output-dir", default="reports/latest")
    fixture = sub.add_parser("serve-fixture", help="start the deterministic development website")
    fixture.add_argument("--host", default="127.0.0.1")
    fixture.add_argument("--port", type=int, default=8765)
    sub.add_parser("doctor", help="check package, task pack, and score profiles")
    args = parser.parse_args(argv)

    try:
        if args.command == "validate":
            records = load_tasks(args.path) if args.kind == "tasks" else load_runs(args.path)
            print(json.dumps({"valid": True, "kind": args.kind, "records": len(records)}))
        elif args.command == "list":
            tasks = _tasks(args.tasks)
            for task in tasks.values():
                if not args.capability or args.capability in task["capabilities"]:
                    print(f"{task['task_id']}\t{task['difficulty']}\t{task['title']}")
        elif args.command == "show":
            task = _tasks(args.tasks).get(args.task_id)
            if not task:
                raise ValidationError(f"unknown task_id: {args.task_id}")
            print(json.dumps(task, indent=2, ensure_ascii=False))
        elif args.command in {"score", "report"}:
            tasks = _tasks(args.tasks)
            results = []
            for run in load_runs(args.runs):
                if run["task_id"] not in tasks:
                    raise ValidationError(f"run references unknown task: {run['task_id']}")
                results.append(score_run(tasks[run["task_id"]], run))
            if args.command == "score":
                rendered = json.dumps(results, indent=2, ensure_ascii=False)
                if args.output:
                    Path(args.output).write_text(rendered + "\n", encoding="utf-8")
                else:
                    print(rendered)
            else:
                output_dir = Path(args.output_dir)
                json_path = write_json_report(results, output_dir / "report.json")
                html_path = write_html_report(results, output_dir / "index.html")
                print(
                    json.dumps(
                        {"json": str(json_path), "html": str(html_path), "runs": len(results)}
                    )
                )
        elif args.command == "serve-fixture":
            serve(args.host, args.port)
        elif args.command == "doctor":
            tasks = _tasks(None)
            assert all(sum(profile["weights"].values()) == 100 for profile in PROFILES.values())
            print(
                json.dumps(
                    {
                        "status": "ok",
                        "version": __version__,
                        "tasks": len(tasks),
                        "profiles": list(PROFILES),
                    }
                )
            )
    except (ValidationError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
