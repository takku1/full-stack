# Checkout design and handoff

Origin: [supplied request](../../INPUT.md). Scope: existing `app.py` checkout and `pricing.py` total calculation; no new runtime dependency, UI, service or framework. Baseline source is preserved in [baseline](../../baseline/). One baseline integration test passed before edits.

Current baseline: checkout forwards prices to pricing and wraps the integer sum in a dictionary. Target: optional discount forwarded through the same boundary, with domain validation and rounding owned by pricing. Migration: extend both signatures with default zero; existing valid calls and dictionary shape survive. Invalid prices now deliberately raise errors as requested.

Requirements and acceptance:
- R1: checkout([100, 250]) returns {'total_cents': 350}; explicit zero and empty input preserve the same shape.
- R2: discount_percent is an integer (excluding bool) from 0 through 30 inclusive (superseding the initial 50 cap by the follow-up request). Both keyword and positional calls work. Out-of-range integers raise ValueError; wrong types raise TypeError.
- R3: each price is a nonnegative integer excluding bool. Invalid types raise TypeError, negatives raise ValueError; checkout propagates errors without returning a partial result.
- R4: calculate floor(sum(prices) * (100 - discount_percent) / 100) using exact integer arithmetic. Apply discount to the aggregate, not to each item. Large integers retain precision.

The exception classes are an implementation convention chosen because the request does not prescribe them. Prices remain an iterable, matching sum's existing consumption model; there is no new container restriction. Integer subclasses remain accepted except bool. Input iteration exceptions propagate. Iterables are consumed once; caller-owned collections are not mutated.

Responsibilities/contracts: app.checkout owns response composition and forwards the optional argument. pricing.total_cents owns price validity, discount validity, summation, and rounding. The provider guarantees a nonnegative integer or raises an error; checkout consumes that value without duplicating domain policy. There is no durable state, network, shared mutable state, lifecycle, or security boundary in this change. No benchmarks or platform-wide performance claims are required; calculation remains a single input pass.

Decision: extend the existing pricing provider rather than calculate discounts in checkout, so future discount policy changes stay with pricing and other callers share its guarantees. Keeping exact integer arithmetic avoids float precision loss. No research uncertainty requires external sources. Existing modules are sufficient; there is no unresolved prerequisite.

Handoff sequence: W1 establish baseline and evidence; W2 implement pricing contract and checkout forwarding, then run real checkout integration for R1-R4; W3 change cap to 30 and update acceptance/boundary tests, observing affected responsibilities; W4 edit the documentation label only. Work state belongs in [ROADMAP](../../ROADMAP.md). Tests use real imports with no mocks. Completed runtime evidence is recorded in [evidence](../../evidence/RESULTS.md); it is distinct from this design assessment.
