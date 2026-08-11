## What changed

<!-- Concise summary. -->

## Why

<!-- Benchmark gap, bug or method rationale. -->

## Benchmark impact

- Affected task/evaluator versions:
- Can existing scores change? Why?
- New failure modes covered:

## Evidence

- [ ] Tests cover positive and negative behavior.
- [ ] Generated tasks are unchanged or intentionally updated.
- [ ] Fixtures reset deterministically.
- [ ] No secrets, private datasets or signed URLs are included.
- [ ] External data/assets have provenance and compatible licenses.
- [ ] Documentation and changelog are updated when the public contract changes.

## Validation

```text
ruff check .
ruff format --check .
pytest
```
