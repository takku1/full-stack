---
layer: custom
decides: [the decisions this domain layer owns, named in the stack brief]
constrains: [neighbors named in the stack brief]
criteria: [fit to the layer's quality scenarios, integration cost, maturity, license, team familiarity]
evidence: [current release and date, maintenance activity, license, documented limits]
tags: []
---

# Custom layer

Use for a layer the defaults do not fit: a kernel service, compositor,
firmware, data pipeline stage, ML model serving, or game engine. Name the
layer in the stack brief (for example `compositor`) and use that name in
the stack block.

## Define the layer before choosing for it

1. **Responsibility**: what this layer owns and what it explicitly does not.
   Split where hidden decisions, authority, or lifecycle differ, not by
   directory.
2. **Neighbors**: which layers it consumes from and provides to, and the
   contract with each.
3. **Quality scenarios** specific to it: latency, memory, real-time
   deadlines, determinism, safety.
4. **Existing owners**: what in the repository already does this. Prefer
   integrating through its boundary over replacing it.

## Then

Follow the same pass-1 rules as every layer: two or three candidates,
evidence checked now, `provides` and `assumes` tags, novelty. An idea can
transfer from a reference system even when its implementation cannot;
record the fit gap. Add a project-local rule to the stack block only with
cited evidence.
