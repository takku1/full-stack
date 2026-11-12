---
layer: interface
decides: [boundary style between components, contract format and source of truth, versioning and compatibility policy, error and retry semantics, sync or event mechanism]
constrains: [client, runtime, platform]
criteria: [fit to interaction patterns, consumer count and control, compatibility needs, tooling for contract checking, failure semantics, team familiarity]
evidence: [spec and tooling maturity, generator and validator maintenance, platform support for the transport]
tags: [http-request-response, rpc-typed, graphql, server-push, event-stream, message-queue, sync-capable, contract-first, versioned-api, idempotent-writes, cors-or-same-origin, in-process-call]
---

# Interface layer

Decides how components talk across boundaries and what each side may rely
on. The contract matters more than the transport.

## Establish first

1. **Boundaries**: which components talk, in which direction, in or out of
   process, and who controls each side's release.
2. **Interaction patterns**: request/response, server push, streaming,
   offline sync, background events, bulk transfer.
3. **Semantics per call**: success, each failure, timeout, retry,
   idempotency, ordering, partial results, cancellation.
4. **Consumers**: internal only, several teams, or public. Public and
   multi-team consumers need versioning and deprecation rules.
5. **Contract source of truth**: schema-first file, code-first types, or an
   existing published contract you must preserve.

## Choosing

Within one deployable, an in-process call beats a network boundary. Plain
HTTP request/response with a written schema is the boring default between
processes. Add push, streams, or queues only for a scenario that polling or
request/response cannot meet. Offline clients need an explicit sync
protocol with versions or change feeds.

## Traps to check

- Retried writes without idempotency keys.
- A contract defined only in prose, so client and server drift.
- Breaking changes without versioning when consumers release separately.
- Server push chosen on a platform without long-lived connections.
- Errors that collapse distinct failures into one generic message.

## Neighbor assumptions to record

What the platform must support (long-lived connections, gateways, CORS),
what the runtime must generate or validate, and what the client must
handle (retries, offline queue, version negotiation).
