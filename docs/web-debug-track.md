# Browser and web-to-code debugging track

This track evaluates agents that can use the web as both an execution surface and a technical evidence source.

## Two levels

### Browser diagnosis

The agent receives a running page with a browser-visible fault and must inspect page state, console or network evidence, identify the root cause and avoid damaging the environment. Examples include HTTP failures, CORS, broken SPA routes, session loss, rate limits and unhealthy reconnect loops.

Profile: `browser_debug_v1`.

### Repo-to-browser repair

The agent receives a repository and target behavior. It must:

1. reproduce the browser-visible defect;
2. inspect console, network, DOM, source and tests;
3. search authoritative web documentation when needed;
4. state the evidence-backed root cause;
5. make a minimal patch;
6. pass fail-to-pass tests;
7. preserve pass-to-pass tests;
8. verify browser state and visual/accessibility invariants;
9. attach before/after evidence.

Profile: `web_debug_v1`.

## Seed defect families

- blank canvas or WebGL initialization failure;
- shader/material incompatibility;
- CORS or asset-origin failure;
- hydration or runtime white screen;
- SPA fallback and deep-link 404;
- device-pixel-ratio and resize bugs;
- mobile overlay and z-index defects;
- reduced-motion and keyboard accessibility regressions;
- rate-limit recovery and connection hygiene;
- screenshot/reference visual mismatch;
- engine or framework misidentification;
- license and asset-provenance defects.

## Scoring

The full profile weights final behavior/tests 25%, root cause 15%, patch correctness/minimality 15%, web grounding 15%, visual/browser state 10%, end-to-end evidence 10%, recovery 5% and efficiency/safety 5%.

Like SWE-bench, a patch is not resolved unless target tests pass and protected tests remain passing. Unlike a code-only benchmark, browser state, console/network evidence and visual/accessibility invariants are first-class oracles.

Stopping a healthy browser, disabling web security, deleting unrelated user state, repeatedly retrying a known rate-limit page, or claiming a fix without browser evidence prevents a full pass.
