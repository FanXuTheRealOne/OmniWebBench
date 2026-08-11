# Contributing to OmniWebBench

Thank you for improving open evaluation for web agents.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python scripts/generate_dev_tasks.py
ruff check .
ruff format --check .
pytest
```

## Contribution types

- **Task:** include every artifact in the [task authoring guide](docs/task-authoring.md).
- **Agent adapter:** keep agent dependencies outside the evaluator package and include one reproducible sample run.
- **Evaluator:** add positive, negative and mutation tests; explain false-positive and false-negative risks.
- **Fixture:** include health, reset, isolation and deterministic-seed tests.
- **Documentation:** cite primary sources and distinguish shipped behavior from roadmap work.

## Pull request requirements

- one focused change;
- issue or design rationale for evaluator semantics;
- updated schemas and version when the public contract changes;
- no credentials, cookies, signed URLs or private datasets;
- passing tests and lint;
- provenance and license for every external asset;
- benchmark-impact statement: which scores may change and why.

Task and evaluator changes require two reviewers after the verified split is released. A contributor must not be the sole verifier of their own task.

## Commit style

Use short imperative summaries, for example:

```text
add iframe diagnostic task
harden forbidden-event evaluation
document live-task drift policy
```

## Contributor license

By contributing code, you agree that it is licensed under Apache-2.0. By contributing task specifications or documentation, you agree that they are licensed under CC BY 4.0 unless the PR explicitly identifies a compatible alternative.
