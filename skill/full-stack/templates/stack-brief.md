# Stack brief template

Written once by the orchestrator, read by every layer. Field labels are
prompts; write "none" rather than leaving a field out.

```markdown
## Stack brief: <outcome>

- **Outcome**: <observable result>; requirement IDs <...>
- **Excluded**: <what this choice must not take on>
- **Quality scenarios** (each observable; mark "proposed" if not user-stated):
  - <QS-1: stimulus, environment, response, measure>
- **Constraints**: existing stack <...>; team skills <...>; licenses <...>;
  platforms and deployment targets <...>; budget <...>
- **Futures** (2–4, for regret): <F-1>, <F-2>
- **Innovation budget**: <n> non-boring choices (default 1)
- **Brief tags** (for rules): <offline-operation, user-accounts, ...>
- **Layers**:
  | Layer | Status | Reason |
  |---|---|---|
  | data | keep-current / affected / out-of-scope | <evidence> |
  | runtime | | |
  | interface | | |
  | client | | |
  | platform | | |
  | crosscut | | |
- **Settled contracts**: <cross-layer contracts already fixed, with source>
```

A layer is **affected** only when the outcome needs a new choice there or
the current choice demonstrably cannot meet a required scenario. Record the
evidence in "Reason".
