# Benchmark design

## Design requirements

OmniWebBench follows eight requirements:

1. **Observable success.** Every required claim maps to a deterministic oracle or explicitly calibrated judge.
2. **Reproducibility.** Task, environment, evaluator and agent metadata are versioned independently.
3. **Diagnostic power.** Atomic probes and checkpoints localize failures instead of returning only zero or one.
4. **Agent neutrality.** The benchmark exchanges JSON; it does not dictate an agent library, model or browser-control method.
5. **Safety as a gate.** An unsafe completion is not a pass with a small deduction.
6. **Infrastructure honesty.** Site, fixture and authentication failures are separated from agent failures.
7. **Contamination resistance.** Hidden test prompts, parameterized variants and evaluator isolation reduce memorization.
8. **Traceable evolution.** Task revisions, retirement reasons and evaluator changes are public.

## Suite architecture

The target suite contains six independently reported tracks:

| Track | Environment | Primary oracle |
|---|---|---|
| Interaction diagnostics | deterministic fixture | event and page state |
| Stateful workflows | containerized sites | database + UI state |
| Visual and accessibility | controlled pages | state + visual/accessibility assertions |
| Open-web research | live public web | claim rubric + URL/time evidence |
| Safety and robustness | controlled adversarial pages | completion-under-policy + forbidden events |
| Browser and web debugging | repo + local app + browser | tests + console/network + visual state |

Tracks are never averaged without first reporting their separate results.

## Capability taxonomy

Capabilities are hierarchical and multi-label. Top-level groups include perception, grounding, interaction, navigation, state, data, artifacts, planning, recovery, safety, research and debugging. Task difficulty is orthogonal: atomic, visual, compositional, long-horizon, adversarial or debug.

## Failure taxonomy

Every failure is assigned one primary root cause and zero or more contributing causes:

- `PERCEPTION_MISS`
- `GROUNDING_WRONG_TARGET`
- `ACTION_EXECUTION_ERROR`
- `NAVIGATION_STATE_LOSS`
- `CONSTRAINT_VIOLATION`
- `INCOMPLETE_WORKFLOW`
- `WRONG_FINAL_STATE`
- `UNSUPPORTED_CLAIM`
- `HALLUCINATED_COMPLETION`
- `RECOVERY_LOOP`
- `ENVIRONMENT_DAMAGE`
- `UNSAFE_ACTION`
- `HUMAN_GATE_MISUSE`
- `ARTIFACT_INVALID`
- `ROOT_CAUSE_WRONG`
- `REGRESSION_INTRODUCED`
- `INVALID_INFRASTRUCTURE`
- `INVALID_TASK`

Infrastructure invalidity requires independent health evidence. An agent that breaks its own connection, stops a healthy browser, changes security settings or loops into rate limits receives an agent failure.

## Verified-release pipeline

1. Author task and explicit capability intent.
2. Pin fixture, seed, browser and evaluator revisions.
3. Produce a gold trajectory that passes.
4. Produce at least one plausible failure trajectory that fails.
5. Mutation-test every oracle so omitted or corrupted outcomes do not pass.
6. Reset and rerun at least three times.
7. Independent reviewer checks clarity, solvability, side effects and shortcut leakage.
8. Calibrate baseline agents and human performance.
9. Freeze digests and add to `verified`.
10. Monitor live validity and retire broken tasks without rewriting history.
