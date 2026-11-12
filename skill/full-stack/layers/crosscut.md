---
layer: crosscut
decides: [authentication and authorization model, secrets and key handling, observability (logs, metrics, traces, alerts), test strategy by layer, privacy and audit obligations]
constrains: [data, runtime, interface, client, platform]
criteria: [threat and obligation fit, least privilege, operability for this team, test speed and confidence, maturity, cost]
evidence: [identity provider and library maintenance, compliance requirements cited, platform support for logging and secrets]
tags: [authentication, role-based-authorization, audit-logging, encryption-at-rest, encryption-in-transit, structured-logging, tracing, contract-tests, end-to-end-tests]
---

# Cross-cutting concerns

Not a tier but a set of obligations every other layer must meet. Check
this module against every affected layer, even when it decides nothing new.

## Establish first

1. **Actors and permissions**: who may do what, to which data, and who
   grants access. Trace each permission to the component that enforces it.
2. **Threats and obligations**: personal or regulated data, payments,
   abuse cases, audit and retention duties.
3. **Operations**: how a failure is noticed, by whom, and what they need
   to diagnose it.
4. **Verification**: which behaviors need unit, contract, integration, or
   end-to-end checks, and which must survive a restart.

## Choosing

Use an established identity provider or library before writing
authentication. Enforce authorization at the component that owns the data,
not only in the client. Use structured logs with request correlation as the
boring default; add tracing when calls cross several services. Put contract
tests on every boundary whose sides release separately.

## Traps to check

- Authorization enforced only in the client or the gateway.
- Secrets or personal data written to logs.
- Tokens without expiry or revocation.
- A test plan that mocks the boundary the outcome is about.
- No alert for the failure the brief's scenarios care about most.

## Neighbor assumptions to record

For each layer: what it must enforce, log, encrypt, or expose for checks.
