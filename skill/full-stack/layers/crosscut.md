---
layer: crosscut
decides: [identity provider or auth library, secrets store, telemetry stack, test tooling]
constrains: [data, runtime, interface, client, platform]
criteria: [fit to the raised assurance disciplines, least privilege, operability for this team, maturity, cost]
evidence: [identity provider and library maintenance, platform support for secrets and telemetry, license]
tags: [authentication, role-based-authorization, audit-logging, encryption-at-rest, encryption-in-transit, structured-logging, tracing, contract-tests, end-to-end-tests]
---

# Cross-cutting technology

This layer chooses the shared *technology* that the assurance disciplines
need: identity provider or auth library, secrets store, telemetry stack,
and test tooling. *What must be true and how it is checked* lives in the
[assurance flow](../flows/assurance.md) and its modules (security,
observability, verification, privacy). Read those first; choose here only
what they require that no layer already provides.

## Establish first

1. Which assurance disciplines the screen raised, and at what tier.
2. What the platform and existing stack already provide (managed identity,
   secret manager, logging, test runner). Reuse beats adding.
3. Who operates each choice and how it fails.

## Choosing

Prefer the platform's managed identity and secrets services, or an
established library, over custom code. Prefer the telemetry the platform
already collects; add OpenTelemetry when calls cross several services.
Prefer the project's existing test runner.

## Neighbor assumptions to record

What each layer must call (identity verification, secret retrieval,
telemetry export) and what it must provide (correlation IDs, audit events).
