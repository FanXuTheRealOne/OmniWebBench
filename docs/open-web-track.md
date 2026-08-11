# Open-web research track

The open-web track measures whether an agent can discover, enter, verify and synthesize information from changing public websites.

## Task families

- fact retrieval with freshness constraints;
- cross-source comparison under a shared unit/definition;
- repository and license verification;
- multi-page structured extraction;
- source disagreement and uncertainty handling;
- dynamic threshold tasks such as stars, price, availability or schedule;
- research-to-artifact workflows.

## Evidence contract

Every hard claim binds to:

- exact source URL and retrieval timestamp;
- page title and admitted browser frame or network record;
- extracted value before normalization;
- transformation rule when units or definitions change;
- uncertainty or missing-data marker.

Search-result snippets alone do not prove repository, license, price or policy claims. The agent must enter the authoritative page unless the task explicitly permits an index source.

## Drift and validity

Each task has a lightweight validity probe. A run becomes `INVALID_TASK` only when the target fact or workflow is no longer answerable from the allowed public context. Blocking, CAPTCHA and regional outages are separately classified as infrastructure. Live tasks run at least three times and publish validity and invalid-infrastructure rates.

## Score profile

`open_research_v1` weights hard constraints 30%, grounding 25%, synthesis 15%, freshness/uncertainty 10%, process 10% and safety 10%. Hard constraints, grounding and safety have independent minimums.
