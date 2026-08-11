# OmniWebBench benchmark card

## Summary

OmniWebBench is an open, framework-neutral benchmark for agents that operate real web browsers. It separates observable task outcome from evidence quality, process compliance, reliability and safety. Version 0.1.0 is a developer preview containing 24 deterministic public tasks.

## Intended use

- diagnose browser-agent capabilities and failure modes;
- compare agent versions under the same browser, fixture and policy;
- validate run/evidence contracts before expensive live or containerized evaluation;
- develop reproducible task packs and agent adapters;
- measure completion under policy, not completion alone.

## Out-of-scope use

- claiming broad real-world superiority from the public dev split;
- training on hidden-test or evaluator internals;
- bypassing access controls, CAPTCHAs or website policies;
- performing unauthorized real-world purchases, messages, posts or destructive actions;
- comparing models without disclosing scaffold, observation mode and retries.

## Versioned assets

| Asset | Version | Public |
|---|---:|---:|
| Task schema | `omniwebbench.task.v1` | yes |
| Run schema | `omniwebbench.run.v1` | yes |
| Submission schema | `omniwebbench.submission.v1` | yes |
| Dev task pack | `0.1.0` | 24 tasks |
| Verified split | not released | no |
| Hidden test split | not released | no |

## Environment

The public split uses a standard-library Python HTTP fixture. It exposes normal webpages to the agent and an instrumented event ledger to the evaluator. Agents must not access ledger endpoints directly during a run. Official evaluation will isolate the agent, browser, environment and evaluator into separate trust zones.

## Metrics

Primary metrics are task success and completion under policy. Diagnostic metrics include dimension scores, required-checkpoint pass, unsafe-action rate, infrastructure-invalid rate, latency, steps, tool errors, tokens and cost.

## Known limitations

- The public v0.1 fixture is intentionally compact and does not represent the visual or behavioral diversity of the open web.
- Event-ledger evidence is locally reproducible but not cryptographically attested in this preview.
- No official baseline leaderboard has been calibrated yet.
- Live-web, containerized CRUD and repo-to-browser debug tracks remain roadmap items.
- English is the only authored language in v0.1.

## Maintenance

Every benchmark release freezes task, environment and evaluator digests. Material evaluator changes require a new benchmark version. Invalid or ambiguous tasks are retired with a public reason and remain addressable by their original ID.
