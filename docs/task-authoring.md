# Task authoring guide

## A good task

A benchmark task is specific enough to evaluate, natural enough to represent a real request, and constrained enough to run safely. It names the desired outcome, not a click path. Multiple valid trajectories should pass when they reach the same authorized state.

## Required artifacts

Every proposed task PR includes:

1. task JSON and schema validation;
2. fixture/seed or live-site policy;
3. gold run with raw evidence;
4. at least one realistic negative run;
5. reset/health test;
6. oracle mutation test;
7. capability and difficulty rationale;
8. side-effect and credential review;
9. source and data-license provenance;
10. independent reviewer sign-off.

## Oracle rules

- Prefer server/database state over visible text.
- Prefer executable tests over LLM judging.
- Use URL/text matching only when it uniquely proves the outcome.
- Bind factual claims to source URLs and timestamps.
- Never reward merely opening the right page when retrieval or mutation is required.
- Protect pre-existing state with regression checkpoints.
- Reject shortcuts that query hidden fixture or evaluator APIs.

## Live tasks

Live tasks must be read-only by default, have at least two viable source paths, define freshness and volatility, and include a periodic validity probe. Remove tasks requiring CAPTCHA bypass or undeclared credentials.

## Review checklist

- Can a human complete the task from the supplied context?
- Can a plausible wrong trajectory accidentally pass?
- Can the correct outcome be reached without the capability being measured?
- Does reset restore all server, browser, file and session state?
- Are all images/files redistributable?
- Are unsafe outcomes impossible or explicitly instrumented?
- Does the task remain meaningful across viewport and browser variations?
