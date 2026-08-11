# Task packs

`core-v0.1.jsonl` is the public 24-task deterministic development pack. It is generated from `omniwebbench.task_factory` and checked into source control so agents can be integrated without executing generation code.

## Split semantics

- `dev`: fully public prompts, fixture and oracles; diagnostic only.
- `verified`: independently audited tasks with frozen environment and evaluator revisions.
- `test`: hidden prompts/seeds/oracles used for official evaluation.
- `live`: read-only public-web tasks with validity timestamps and repeated-run policy.

Public dev results must not be described as official test results. Task IDs remain stable; material intent or oracle changes require a task revision and benchmark release.

## Regeneration

```bash
python scripts/generate_dev_tasks.py
git diff --exit-code -- tasks/core-v0.1.jsonl
```

No proprietary query, customer prompt, credential or private dataset is included in this task pack.
