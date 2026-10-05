# E02n / X

## Prompt

Design only roadmap B-17 from the supplied context. Keep the current stack and produce a concise implementation handoff. Research only if a decision cannot be resolved from the supplied contracts. Do not implement code.

## Final answer

# B-17 implementation handoff: cancel a reservation and show the confirmed outcome

Scope is B-17 only. Waitlist promotion, emails and offline changes (B-18 to B-20) are excluded. The stack is unchanged. The only source was `booking-context.md`.

## Design

1. **Control.** Add a "Cancel reservation" button on each existing reservation the member sees.
   - A confirmation step comes first, because cancelling is destructive. The prompt names the workshop and seat.
   - Show the button only on reservations the UI already treats as active.
   - The server remains the authority on whether cancellation is allowed.

2. **Request.** The browser calls the existing authenticated cancellation API with `{reservationId, requestId}`.
   - **No member ID.** Never send one. The server derives the member from the session, and client-supplied IDs can't authorize anything.
   - **Request ID.** Generate one (a UUID) when the member confirms the dialog. Keep it for the life of that attempt, including retries after a timeout or network error. Create a new one only for a new, deliberate cancel action. This is what makes retries safe, assuming the server dedupes on it (see open questions).

3. **Outcome display.** Show the confirmed outcome only after the server reports success. Do not update the UI optimistically.
   - While the request is in flight, disable the control and show a pending state to prevent double submits.
   - On a confirmed success, mark the reservation as cancelled, or remove it. Show a message such as "Your seat in <workshop> is cancelled", using data from the server response.
   - Move focus to the message and announce it with an `aria-live` region.

4. **Failure states.** Map each to distinct copy and keep the reservation as it was.
   - **Not authorized or not found** (403/404): "We couldn't find this reservation." Refresh the list.
   - **Already cancelled:** show it as cancelled. Treat it as success if the server treats the repeat as idempotent.
   - **Rejected by a business rule** (for example a cutoff): show the server's reason.
   - **Network error or timeout, outcome unknown:** don't claim success or failure. Show "We couldn't confirm. Retry", reusing the same request ID. Alternatively refetch the reservation to learn its true state.
   - **Unauthenticated** (401): send the member through the existing sign-in flow.

5. **Server.** No new cancellation logic. `BookingService` already provides it. The only server work is exposing whatever the response needs, if the existing response lacks it.

## Tests

- **Unit:**
  - The request body contains no member ID.
  - The request ID is stable across retries and new for each new action.
  - Each response status maps to the right UI state.
- **Integration (against the existing API contract):**
  - A member cancels their own reservation.
  - A member cannot cancel another member's reservation, even with a forged ID in the payload.
  - A repeated request ID does not double-cancel.
- **UI:** double-click protection, focus and live-region behaviour, and the unknown-outcome retry path.

## Acceptance criteria

- A signed-in member can cancel their own reservation and see a confirmation that came from the server response.
- Failures never show a success message.
- Cancelling twice never produces a double effect.
- No code path sends a member ID.

## Open questions

The context doesn't specify these. Check them against the `BookingService` API before building, and don't research externally.

- **Response shape.** What does a success response contain (updated reservation, status)? The outcome message depends on it.
- **Idempotency.** Does a repeated request ID return the original result? What happens when a different request ID targets an already-cancelled reservation? Steps 2 and 4 assume the first. If it's false, refetch the reservation state instead of retrying blindly.
- **Cancellation rules.** Are there cutoffs or other limits, and how are they signalled in the error response?
- **Seat release.** Does cancelling free the seat for others immediately? This is probably invisible to the UI, but confirm it before wording the message. Waitlist behaviour is B-18 and out of scope.

## Files changed


## Diff

```diff

```