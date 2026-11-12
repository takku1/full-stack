# Decision record template

One record per affected layer, written in pass 2 against the committed
profile. ADR-shaped (title, context, decision, status, consequences) with
selection fields added. Cap: about 250 words per layer. Tables beat prose,
and a field that does not apply reads "none". Reference brief IDs (QS-1,
F-2) instead of restating them.

```markdown
### <Layer>: <decision title>

- **Status**: proposed | accepted | conditional (<awaiting what>) | blocked (<by what>)
- **Context**: brief fields this depends on (QS-…, constraints, futures)
- **Candidates**:
  | Candidate | Evidence (checked <date>, source) | Provides | Assumes from neighbors | Novel |
  |---|---|---|---|---|
- **Scores**: each candidate against each quality scenario and cost
  (ordinal is fine: meets / partial / fails; low / medium / high cost)
- **Regret**: per future, shortfall of each candidate against the best
  candidate in that future; note the minimax-regret candidate
- **Decision**: <choice>, because <scenario fit and the deciding trade-off>
- **Neighbor assumptions**: <layer: what this choice needs from it>
- **Consequences**: what becomes easier, what becomes harder, the fit gap
  and who owns it
- **Revisit when**: <observable condition that reopens this>
- **Novelty**: spends the innovation budget? yes/no
```

A choice fixed by the user records that origin; investigate its
integration constraints instead of reopening it. A keep-current layer gets
one line: choice and what it provides.
