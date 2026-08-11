<p align="center">
  <img src="assets/hero.png" alt="OmniWebBench — Measure what web agents actually do" width="100%">
</p>

<p align="center">
  <a href="https://github.com/FanXuTheRealOne/OmniWebBench/actions/workflows/ci.yml"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/FanXuTheRealOne/OmniWebBench/ci.yml?branch=main&style=flat-square&label=CI"></a>
  <a href="LICENSE"><img alt="Apache 2.0" src="https://img.shields.io/badge/code-Apache--2.0-111111?style=flat-square"></a>
  <a href="DATA_LICENSE.md"><img alt="Task data CC BY 4.0" src="https://img.shields.io/badge/tasks-CC%20BY%204.0-13aebb?style=flat-square"></a>
  <img alt="Benchmark version" src="https://img.shields.io/badge/benchmark-v0.1.0-111111?style=flat-square">
  <img alt="Public dev tasks" src="https://img.shields.io/badge/public%20dev%20tasks-24-13aebb?style=flat-square">
  <img alt="Python" src="https://img.shields.io/badge/python-3.11%2B-111111?style=flat-square">
</p>

<p align="center"><strong>A capability-first, evidence-grounded benchmark for general-purpose web agents.</strong></p>

<p align="center"><a href="https://fanxutherealone.github.io/OmniWebBench/"><strong>Explore the interactive benchmark overview →</strong></a></p>

OmniWebBench evaluates what an agent **did in the browser**, not merely what it said it did. Every scored claim must resolve to an observable checkpoint: an instrumented server event, final application state, URL, artifact, network record, console record, visual evidence, or executable test.

The project is agent- and framework-neutral. A system may use screenshots, accessibility trees, DOM, Playwright, Selenium, CDP, or computer-use APIs. The evaluator consumes one standard run bundle and keeps the agent implementation out of the benchmark dependency graph.

> [!IMPORTANT]
> **v0.1 is a public developer preview.** It ships a runnable 24-task deterministic diagnostic suite, schemas, fixture server, scorer, reports, and governance contract. It does not claim a frontier leaderboard yet. The `verified` and hidden `test` splits will only open after independent task audits and baseline calibration.

## Why another benchmark?

Existing benchmarks answer different, important questions:

| Benchmark | Best at | Gap OmniWebBench targets |
|---|---|---|
| [WebArena](https://github.com/web-arena-x/webarena) / [WebArena Verified](https://github.com/ServiceNow/webarena-verified) | Reproducible stateful tasks and executable evaluators | Cross-suite capability diagnosis, safety, recovery, evidence and debugging |
| [VisualWebArena](https://github.com/web-arena-x/visualwebarena) | Visually grounded browser tasks | Modality attribution and fine-grained process failure labels |
| [BrowserGym](https://github.com/ServiceNow/BrowserGym) / [AgentLab](https://github.com/ServiceNow/AgentLab) | Standardized environments and scalable experimentation | A benchmark contract rather than an agent runtime |
| [Online-Mind2Web](https://github.com/OSU-NLP-Group/Online-Mind2Web) | Live-web generalization | Deterministic replay, mutation oracles, safety and debugging |
| [WorkArena](https://github.com/ServiceNow/WorkArena) | Enterprise knowledge work and compositional planning | Broad website primitives and open adapter protocol |
| [ST-WebAgentBench](https://github.com/segev-shlomov/ST-WebAgentBench) | Completion under safety policy | General capability coverage and web debugging |
| [SWE-bench](https://github.com/swe-bench/SWE-bench) | Reproducible issue-level software engineering evaluation | Browser-specific state, trajectory and evidence semantics |

OmniWebBench borrows the strongest evaluation ideas rather than copying any one task set:

- **From SWE-bench:** immutable instance IDs, pinned environments, fail-to-pass plus pass-to-pass thinking, gold verification, audited subsets, and reproducible submission artifacts.
- **From WebArena Verified:** executable state evaluators, structured agent responses, task revisions, checksummed evidence, and offline reevaluation.
- **From WebSuite:** atomic capability probes that explain *why* an end-to-end task failed.
- **From WorkArena++:** compositional and long-horizon workflows.
- **From Online-Mind2Web:** live-web validity audits and repeated runs.
- **From ST-WebAgentBench and WASP:** completion-under-policy, prompt-injection resistance, safe deferral, and explicit unsafe-action metrics.

See [Benchmark landscape](docs/benchmark-landscape.md) for the source-by-source design review.

## What it measures

The public development pack exercises these capability families:

| Family | Example capabilities |
|---|---|
| Perception & grounding | visual target grounding, labels, icon-only controls, structured page reading |
| Interaction primitives | click, keyboard, text entry, select, checkbox, modal, tabs, iframe, drag-and-drop |
| Navigation & state | pagination, multi-tab, session continuity, dynamic content, final-state inspection |
| Workflows | validated forms, constrained checkout, multi-step creation, upload and download |
| Reasoning | filtering, sorting, extraction, constraint following, answer synthesis |
| Reliability | transient failures, retry discipline, timeouts, idempotency, environment health |
| Safety | prompt injection, destructive-action boundaries, human confirmation, forbidden side effects |
| Debugging | console/network inspection, browser-visible diagnosis, root-cause evidence |
| Expansion tracks | open-web research, artifact production, repo-to-browser debugging, visual fidelity |

Coverage is reported by capability and difficulty—not hidden behind one overall score.

## Quick start

Requires Python 3.11+.

```bash
git clone https://github.com/FanXuTheRealOne/OmniWebBench.git
cd OmniWebBench
python -m venv .venv
source .venv/bin/activate
pip install -e .

omniwebbench doctor
omniwebbench list
omniwebbench serve-fixture --port 8765
```

In a second terminal:

```bash
source .venv/bin/activate
omniwebbench validate tasks/core-v0.1.jsonl
omniwebbench score examples/sample-run.json
omniwebbench report examples/sample-run.json --output-dir reports/sample
open reports/sample/index.html  # macOS; use your browser elsewhere
```

The fixture URL inside each task contains two placeholders:

```text
{{FIXTURE_URL}}/lab?task_id=owb-dev-001&run_id={{RUN_ID}}
```

Your adapter resolves those placeholders, opens the URL in a real browser, and writes a [run bundle](schemas/run.schema.json). The benchmark does not require your agent to import OmniWebBench.

## Evaluation contract

```mermaid
flowchart LR
    T[Versioned task] --> R[Agent adapter]
    R --> B[Real browser]
    B --> E[Instrumented environment]
    E --> P[Evidence bundle]
    R --> P
    P --> O[Deterministic oracles]
    O --> G{Hard gates}
    G -->|admitted| S[Dimension scores]
    G -->|infra/task invalid| X[Excluded from denominator]
    G -->|unsafe or missing required checkpoint| F[Agent failure]
    S --> A[Track + capability aggregates]
```

Each task contains:

- natural-language intent and capability labels;
- a pinned environment contract and reset policy;
- weighted checkpoints with deterministic oracles;
- forbidden events, action/time budgets and side-effect scope;
- an evaluation profile and repeat policy;
- authoring, license and verification provenance.

Each run contains:

- exact agent/model/scaffold disclosure;
- action trajectory with outcomes;
- server events and final state;
- URLs, screenshots, artifacts, console and network evidence;
- cost, latency, tokens, tool errors and environment health.

The evaluator recomputes checkpoint results. It never trusts a submitted `success: true` field.

## Scoring

OmniWebBench publishes a **score vector**, not only one number:

```text
task_success · outcome · evidence · process · reliability · safety
hard_constraint_pass · unsafe_action_rate · infra_invalid_rate
median_wall_time · p95_steps · tool_errors · tokens · cost
```

The default core profile is:

```text
55% observable outcome
15% evidence completeness
10% process compliance
10% recovery / reliability
10% safety
```

A weighted score cannot compensate for a failed hard gate. A run fails when any required checkpoint is missing, safety is below 100%, a profile minimum is missed, or the overall score is below threshold. Infrastructure- and task-invalid runs are reported separately and excluded from task-success denominators.

Live tasks use repeated runs and uncertainty intervals. Stateful tasks reset between runs. Adversarial and debug tasks report both pass@1 and pass@2. Full formulas and aggregation rules are in [Scoring](docs/scoring.md).

## Trust tiers

Leaderboard rows will carry one of three visible trust levels:

1. `self_reported` — schema-valid result uploaded by the author.
2. `reproducible` — code, config, raw run bundle and environment digest are public and independently rerunnable.
3. `official_verified` — executed or audited by benchmark maintainers on the frozen test split.

Only `official_verified` rows are eligible for the primary leaderboard. This follows the spirit of SWE-bench Verified: quality and reproducibility outrank raw task count.

## Repository map

```text
assets/                 generated project artwork
docs/                   benchmark method and public protocols
examples/               valid run bundle and adapter contract examples
schemas/                task, run and submission JSON Schemas
src/omniwebbench/       fixture server, validator, scorer and reports
tasks/core-v0.1.jsonl   24 runnable public development tasks
tests/                  oracle, safety, fixture and CLI regression tests
```

## Integrity and responsible use

- Public dev tasks are diagnostic and must not be presented as hidden-test results.
- Test prompts and gold oracles are withheld until the evaluation window closes.
- Task revisions change whenever intent, fixture state or evaluator semantics change.
- Official submissions disclose model, scaffold, observation mode, action space, retries, cost and human assistance.
- Agents must not access benchmark source, fixture state APIs, hidden test data, evaluator code, or secrets during a run.
- Live-web tasks are read-only unless the task and user explicitly authorize a reversible side effect.
- CAPTCHA bypass, credential harvesting and unauthorized external actions are out of scope.

Read [Benchmark integrity](docs/integrity.md), [Security](SECURITY.md), and the [Agent protocol](docs/agent-protocol.md) before publishing results.

## Status and roadmap

- [x] Versioned task/run/submission contracts
- [x] 24-task deterministic public diagnostic suite
- [x] Instrumented server events and hard-gated scoring
- [x] JSON and self-contained HTML reports
- [x] Safety, recovery, multi-tab, file and debug probes
- [ ] Independent verification round for `verified-v0.1`
- [ ] Containerized stateful sites and database oracles
- [ ] Read-only live-web research track with drift monitor
- [ ] Repo-to-browser web debugging track with fail-to-pass/pass-to-pass tests
- [ ] Multilingual and accessibility slices
- [ ] Public official leaderboard and reproducibility service

Detailed milestones and release gates are in [ROADMAP.md](ROADMAP.md).

## Contributing

Contributions are welcome, especially:

- independently audited tasks and deterministic oracles;
- adapters for browser agent frameworks;
- accessibility, multilingual and mobile/responsive tasks;
- environment drift, anti-cheating and trace-verification tooling;
- baseline runs with complete reproduction metadata.

Start with [CONTRIBUTING.md](CONTRIBUTING.md) and [Task authoring](docs/task-authoring.md). Every new task needs a gold trajectory, a verified failure trajectory, an environment reset test and an oracle mutation test.

## Citation

This developer preview has no archival paper yet. Cite the software using [CITATION.cff](CITATION.cff). A versioned benchmark card and DOI will accompany the first verified release.

## License

Code is licensed under [Apache-2.0](LICENSE). Public task specifications and documentation are licensed under [CC BY 4.0](DATA_LICENSE.md). Generated artwork in `assets/` may be reused for OmniWebBench project communication under the repository license; do not use it to imply endorsement.

<p align="center"><img src="assets/evidence-chain.png" alt="Abstract OmniWebBench evidence chain" width="100%"></p>
