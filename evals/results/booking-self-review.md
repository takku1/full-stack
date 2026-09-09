# Booking cancellation design exercise

Author-generated exercise against E02, 2026-09-09. This is a self-review using known fixture constraints, not an independent forward test or a claim of comparative effectiveness. All existing-system facts come from the synthetic fixture; no implementation was inspected or executed.

## Scope and allocation

B-17 adds a cancellation control and confirmed feedback to the existing reservation screen. B-18, B-19, and B-20 remain excluded. The server BookingService remains authoritative for authorization, cancellation, and capacity. The browser owns transient interaction state and a derived reservation cache.

Reuse the existing API, authenticated client, cache, accessible button, and inline-error component. Concrete source paths must be located during implementation; none are supplied. No technology decision needs external research for this fixed-contract task.

## Interaction

The member activates the control for the displayed reservation. The browser sends the reservation ID and a request ID through the existing authenticated client and displays pending feedback. Client-supplied member identity never replaces server authorization.

Confirmed cancellation or already-cancelled response updates the cached reservation and shows the confirmed state. Denial or missing reservation is displayed using the existing error presentation; the browser does not invent a successful state. Temporary server failure permits recovery through existing API semantics.

For a network interruption after submission, the browser cannot infer whether the server committed. Display an uncertain/pending-reconciliation state and query reservation details. The existing idempotent cancellation outcome permits a retry under the established request contract; it does not justify issuing unrelated capacity mutations. The UI should avoid redundant concurrent requests while one attempt is unresolved.

## Implementation handoff

1. Locate the existing reservation screen, request client, and cache update/requery paths. Verify that the supplied contract matches implementation; preserve its server semantics.
2. Add the accessible control and bounded presentation states: idle, pending, confirmed cancellation, explicit failure, and uncertain outcome needing reconciliation. Product copy can be proposed within the existing style.
3. Connect the control to the existing API and cache behavior. Implement response mapping and reconciliation without a new server authority.
4. Check confirmed cancellation, already-cancelled repetition, denied access, missing reservation, and response loss after server commit. Verify keyboard activation and that capacity is never changed by browser code.

These checks are planned acceptance checks. None ran in this exercise. The package is ready for source localization and implementation against the stipulated contract, with a conditional recheck if the real code differs.

## Review observations

Scope, existing-owner reuse, uncertainty after commit, and planned-versus-executed evidence are explicit. No new API, fake paths, or optional roadmap features were introduced. This demonstrates an internally consistent application of the instructions to one known fixture. It does not test whether a fresh model follows them, whether implementation succeeds, or whether the skill outperforms either predecessor.
