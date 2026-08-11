# Agent adapter protocol

OmniWebBench does not import or call an agent SDK. An adapter translates benchmark tasks into the agent’s native interface and emits one run bundle per attempt.

## Input

The adapter receives the public fields of a task:

- `task_id`, `benchmark_version`, `intent` and `capabilities`;
- resolved start URL;
- timeout, action budget and side-effect policy;
- declared downloadable/uploadable fixtures.

Hidden oracles, evaluator code and environment ledger credentials are never exposed to the agent.

## Execution boundary

Official evaluation separates four principals:

```text
agent process → browser → website fixture
                     ↘ raw trace collector
evaluator → read-only evidence + environment state
```

The agent may control the browser but may not call fixture ledger, evaluator or hidden-state endpoints. Direct HTTP is allowed only when a track explicitly permits it; browser-required tasks need admitted browser evidence.

## Output

Write one JSON document matching `schemas/run.schema.json`. Include:

- exact agent, model and scaffold versions;
- ordered action trajectory and action outcomes;
- final answer or structured response;
- final URL, screenshots and observable state;
- server/network/console evidence captured by the harness;
- artifact paths and SHA-256 hashes;
- latency, steps, token use, cost and tool errors;
- environment health independently reported by the harness.

Do not set benchmark verdicts in the run bundle. The evaluator computes them.

## Human assistance

If the task reaches credentials, MFA, consent or an ambiguous irreversible action, emit `waiting_human` and the exact gate. Human assistance must be declared in submissions and is never silently counted as autonomous success.
