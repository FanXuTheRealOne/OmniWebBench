# Governance

OmniWebBench is maintainer-led during the developer preview and is intended to become reviewer-governed before the first verified leaderboard.

## Roles

- **Maintainers** manage releases, security, infrastructure and repository policy.
- **Task reviewers** audit solvability, reset behavior, side effects and oracle correctness.
- **Reproduction reviewers** rerun submissions and verify disclosures.
- **Contributors** propose tasks, adapters, environments, evaluators and documentation.

## Decisions

Routine changes use lazy consensus in pull requests. Changes to schemas, score profiles, test visibility, licensing or leaderboard eligibility require a written design note and at least two approvals once three or more maintainers exist.

## Conflicts of interest

Reviewers disclose employment, funding, model-provider relationships and direct involvement with an evaluated submission. A conflicted reviewer may provide technical context but cannot be the sole approval for a leaderboard result or benchmark-rule change.

## Versioning

- Patch: documentation, tooling or task-invalidity corrections that do not change admitted scores.
- Minor: new tasks or profiles with the prior leaderboard preserved.
- Major: changed scoring semantics, environment contract or comparability boundary.

Historical results remain linked to their original benchmark, task and evaluator versions.
