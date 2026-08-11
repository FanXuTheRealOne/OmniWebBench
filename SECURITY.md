# Security policy

## Reporting a vulnerability

Do not open a public issue for vulnerabilities that expose credentials, permit arbitrary code execution outside the benchmark sandbox, bypass evaluator isolation, or enable hidden-test extraction.

Use GitHub private vulnerability reporting for this repository. Include affected version, reproduction steps, impact and any suggested mitigation. Maintainers will acknowledge a valid report within seven days and coordinate disclosure after a fix is available.

## Benchmark safety boundary

OmniWebBench tasks must not require:

- credential theft or secret extraction;
- CAPTCHA, paywall or access-control bypass;
- unauthorized purchases, messages, posts or account changes;
- malware execution, phishing or deceptive consent;
- destructive actions outside resettable fixtures;
- collection of unnecessary personal data.

Live tasks are read-only by default. Credentials and consent remain explicit human gates. A benchmark runner must redact cookies, authorization headers, signed URLs, CDP endpoints and secrets before persisting artifacts.

## Supported versions

Only the most recent minor benchmark release receives task-validity and security fixes during the developer-preview phase.
