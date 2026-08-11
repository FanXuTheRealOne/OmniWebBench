# Benchmark landscape and design transfer

OmniWebBench is informed by the strongest public web-agent and software-engineering evaluation systems. This document records what is transferred, what is not, and why.

## SWE-bench

[SWE-bench](https://github.com/swe-bench/SWE-bench) anchors an instance to a repository and base commit, applies a candidate patch, and evaluates fail-to-pass plus pass-to-pass tests in a reproducible environment. Its Verified split demonstrates that expert review and solvability audits matter more than nominal dataset size.

Transferred to OmniWebBench:

- immutable instance IDs and benchmark versions;
- pinned environment identifiers and evaluator digests;
- public dev versus audited/hidden test splits;
- gold-run verification and negative/mutation testing of evaluators;
- resolution and regression concepts mapped to target checkpoints and protected invariants;
- reproducible submission bundles instead of screenshots of a score.

Browser tasks differ because the state is distributed across DOM, server database, browser session, files, tabs and external sites. A browser benchmark therefore needs more evidence channels and explicit infrastructure-invalid handling.

## WebArena and WebArena Verified

[WebArena](https://github.com/web-arena-x/webarena) introduced realistic self-hosted websites and execution-based evaluators. [WebArena Verified](https://github.com/ServiceNow/webarena-verified) audits all 812 tasks and provides a hard subset, structured agent responses, network-trace evaluation and offline reevaluation.

Transferred:

- resettable stateful environments;
- deterministic final-state and network-aware oracles;
- evaluator-specific raw and normalized outputs;
- agent/evaluator dependency separation;
- task revision and checksummed reproduction artifacts.

## VisualWebArena

[VisualWebArena](https://github.com/web-arena-x/visualwebarena) contributes visually grounded tasks in realistic self-hosted environments. OmniWebBench adopts visual-only and modality-challenge slices, but publishes them separately from DOM-accessible tasks so observation advantages are visible.

## BrowserGym and AgentLab

[BrowserGym](https://github.com/ServiceNow/BrowserGym) standardizes browser task environments; [AgentLab](https://github.com/ServiceNow/AgentLab) scales experiments and trace analysis. OmniWebBench remains adapter-neutral and can be wrapped by BrowserGym instead of replacing it.

## Mind2Web and Online-Mind2Web

[Mind2Web](https://arxiv.org/abs/2306.06070) provides more than 2,000 tasks across 137 websites and 31 domains. [Online-Mind2Web](https://github.com/OSU-NLP-Group/Online-Mind2Web) evaluates 300 verified tasks across 136 live websites and periodically replaces invalid tasks.

Transferred:

- broad-domain open-web evaluation;
- validity and drift audits;
- repeated runs and explicit volatility;
- URL-bound grounding for factual claims.

Static unique answers are not used for volatile claims. Live failures are classified as agent, task or infrastructure failures before aggregation.

## WorkArena and WorkArena++

[WorkArena](https://github.com/ServiceNow/WorkArena) covers enterprise knowledge work. WorkArena++ expands to 682 compositional tasks involving planning, retrieval, arithmetic and contextual understanding.

Transferred:

- compositional task templates;
- long-horizon and memory-oriented slices;
- realistic knowledge-work constraints;
- difficulty defined by dependency structure, not prompt length.

## WebSuite

[WebSuite](https://arxiv.org/abs/2406.01623) combines atomic interactions with end-to-end workflows so failures can be attributed to specific web actions. OmniWebBench’s dev pack follows this diagnostic structure and maps every task to explicit capability labels.

## Safety benchmarks

[ST-WebAgentBench](https://github.com/segev-shlomov/ST-WebAgentBench) evaluates task completion and policy compliance jointly. [WASP](https://github.com/facebookresearch/wasp) measures prompt-injection robustness. OmniWebBench adopts completion-under-policy, forbidden events, policy hierarchies, human-confirmation expectations and explicit unsafe-action rates.

## Halluminate WebBench and ByteDance Web-Bench

Two similarly named projects cover different domains:

- [Halluminate WebBench](https://github.com/Halluminate/WebBench) focuses on live browser-agent tasks across real websites.
- [ByteDance Web-Bench](https://github.com/bytedance/web-bench) evaluates web development and coding.

OmniWebBench treats live browsing and repo-to-browser debugging as separate tracks with different environments and scorecards.

## Design conclusion

No existing benchmark simultaneously provides atomic browser diagnosis, realistic stateful workflows, live-web research, safety policy, recovery, artifact evidence and browser-aware debugging. OmniWebBench is designed as a suite with common contracts, not as one homogeneous task pool or one misleading overall score.
