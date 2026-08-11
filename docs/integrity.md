# Benchmark integrity

## Threat model

Benchmark scores can be inflated through prompt memorization, evaluator access, direct state APIs, handcrafted per-task policies, omitted failures, excessive retries or undisclosed human intervention.

## Countermeasures

- Hidden test prompts and oracle configuration.
- Public parameterized dev variants with private held-out seeds.
- Agent, browser, fixture and evaluator network isolation.
- Immutable task/environment/evaluator digests.
- Signed official run manifests and artifact hashes.
- Raw trajectories, console, network and screenshot evidence retained for audit.
- Independent reproduction for the `reproducible` trust tier.
- Maintainer execution or audit for `official_verified`.
- Per-agent versioning; material scaffold changes create a new leaderboard row.
- Public invalid-task and task-retirement registry.

## Contamination disclosure

Submissions disclose whether benchmark tasks, task generators, documentation or derived trajectories were used for training, fine-tuning, prompt optimization or tool development. Public dev usage is allowed but must be disclosed. Hidden test leakage invalidates a submission.

## Result bundle

An official bundle includes:

- task/environment/evaluator digests;
- agent source commit and dependency lock;
- model identifier and provider date/version;
- all run JSON, trajectories and admitted evidence;
- aggregate report and scorer version;
- machine/browser metadata;
- human-assistance and retry disclosures;
- SHA-256 manifest over every file.
