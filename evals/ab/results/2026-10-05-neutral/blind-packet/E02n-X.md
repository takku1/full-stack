# E02n / X

## Prompt

Design only roadmap B-17 from the supplied context. Keep the current stack and produce a concise implementation handoff. Research only if a decision cannot be resolved from the supplied contracts. Do not implement code.

## Final answer

# B-17 implementation handoff: cancellation control and confirmed outcome

**Scope:** Add a cancel control for a member's existing reservation. Show the outcome only after the server confirms it. B-18, B-19 and B-20 are out of scope. That means no waitlist promotion, no emails and no offline queueing. The stack is unchanged, and the server's `BookingService` cancellation is reused as is.

## Stated contracts
- The browser calls the authenticated API. The caller supplies a **reservation ID** and a **request ID**.
- The server verifies access against the authenticated member. A client-supplied member ID can never authorize cancellation.
- The server owns booking authority and persistence.

## Design

**1. Control**
- Show a "Cancel reservation" button on each of the member's own active reservations.
- Clicking it opens a confirm step that names the workshop and seat. Cancellation is destructive and likely hard to undo, because the seat may be taken.
- Hide or disable the control for reservations that are already cancelled.

**2. Request**
- Send `{reservationId, requestId}` and nothing else.
- Don't send a member ID, and don't use the UI's ownership check as authorization.
- Generate the request ID once per user-confirmed attempt, and reuse the same ID on automatic or manual retries of that attempt. A new confirmation gets a new ID.
- While the request is in flight, disable the control to prevent double submits, and show a pending state.

**3. Outcome (server-confirmed only)**
- Make no optimistic update. Change the reservation to "Cancelled" and show a confirmation message only when the server reports success.
- Prefer re-reading reservation state from the server, or using the returned state, as the source for what's displayed.
- Handle failures separately and accurately:

| Case | UX |
|---|---|
| Not permitted or not found | "Couldn't cancel this reservation." Refresh the list and don't reveal whether it belongs to someone else. |
| Rejected by a business rule (e.g. a cutoff) | Show the server's reason, and leave the reservation active. |
| Network error or timeout | Say the result is unknown. Offer retry with the same request ID, and refetch the reservation. Never claim success or failure. |
| Already cancelled | Show it as cancelled, using the idempotency answer from the open questions. |

**4. Accessibility and state**
- Return focus sensibly after the dialog closes.
- Announce the result through a live region.
- Keep the control keyboard-operable.
- Reset the UI state when the member navigates away mid-request, then refetch.

## Open questions
The supplied context doesn't answer these. Resolve them by reading `BookingService` and the API handler. No external research is needed.
1. What are the response shape and error codes for success, forbidden, not found and rule rejection?
2. Is a repeated request ID idempotent, returning the original result? Is cancelling an already-cancelled reservation a success or an error?
3. Is there a cancellation cutoff or other rule, and does the server expose it for the UI to show?
4. Does the existing reservation list/read endpoint return enough state to render "Cancelled"?

If the contracts turn out to be missing, such as no idempotency or no read endpoint, record that as a new roadmap item. Don't expand B-17 to cover it.

## Verification for the implementer
- Component tests: confirm flow, pending state, each failure case, and no optimistic success.
- A test that asserts the request payload contains no member ID.
- A test that a retry reuses the request ID and a fresh confirmation gets a new one.
- An integration check against the real API, using a second member's reservation ID, expecting rejection.
- Update `ROADMAP.md` status for B-17 only when it's done.

## Files changed


## Diff

```diff

```