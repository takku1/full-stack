---
layer: runtime
decides: [server or core language, framework, scripting and automation language, build and package tooling, concurrency model]
constrains: [data, interface, client, platform]
criteria: [team familiarity, ecosystem for the required integrations, performance and resource fit to scenarios, concurrency model, deployment fit, maturity, license]
evidence: [current release and support window, maintained libraries for each required integration, documented limits]
tags: [javascript-server, typescript, python, jvm, dotnet, go, rust, native-binary, single-threaded-event-loop, async-io, managed-memory, scripting-shell-portable]
---

# Runtime layer

Decides the language, framework, and tooling that execute the system's
logic, plus the language used for scripts and automation.

## Establish first

1. **Existing languages** in the repository and organization, and who
   maintains them. A second language is a cost every maintainer pays.
2. **Required integrations**: data stores, external services, hardware,
   and platform SDKs. Each needs a maintained library in the candidate
   ecosystem; check, do not assume.
3. **Workload shape**: request/response, long-running jobs, streaming,
   CPU-bound work, startup-time limits, memory ceilings.
4. **Delivery targets**: where it runs (server, serverless, device,
   browser, embedded), which constrains the language and binary form.
5. **Scripting needs**: build, migration, and operations scripts and the
   operating systems they must run on.

## Choosing

Prefer the language the team already runs in production unless a
required scenario or integration rules it out; record that evidence. Pick a
framework for its fit to the workload and its maintenance record, not its
popularity. For scripts, prefer the main language or a portable script
runner already present over a shell dialect that breaks on another OS.

## Traps to check

- A language chosen for one library while every other integration is weak.
- Blocking calls inside an event loop; unbounded concurrency against a
  data store's connection limit.
- Framework conventions that would take ownership of domain policy.
- Shell scripts that assume one OS when the team or CI uses another.
- Runtime versions near end of support.

## Neighbor assumptions to record

Drivers the data layer needs, contract tooling the interface needs, build
output the platform must run, and any shared types with the client.
