---
discipline: observability
triggers: [internet or trust boundary, availability or latency target, operated by others or unattended]
tier2_when: [stated availability target, several services, many users]
---

# Observability

## Policy

- Tier 1 when any trigger holds; tier 2 for stated targets or several
  services.
- Default: structured logs with a correlation ID per request or job; the
  main scenario's failure is visible in one signal.
- Never: log secrets, credentials, or personal data; alert on causes
  nobody acts on; add a telemetry vendor where the platform already has one.

## Framework

RED for services (rate, errors, duration) and USE for resources
(utilization, saturation, errors). OpenTelemetry for vendor-neutral
instrumentation. SLO-based alerting from the reliability module.

## How to

1. Name the one signal that shows the main scenario failing, and where an
   operator sees it.
2. Emit structured logs on failure paths with the correlation ID and no
   sensitive fields.
3. Reuse the platform's existing logging and metrics.
4. Tier 2: RED metrics per endpoint, traces across service calls, and
   alerts on SLO burn rather than raw error counts.

## Checks

- Triggering a failure path emits the expected log or metric.
- Logs from a test run contain no secrets or personal fields (scan).
- Tier 2: a trace spans the cross-service path; the alert fires in a
  simulated burn.
