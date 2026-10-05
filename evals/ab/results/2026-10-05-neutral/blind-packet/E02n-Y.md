# E02n / Y

## Prompt

Design only roadmap B-17 from the supplied context. Keep the current stack and produce a concise implementation handoff. Research only if a decision cannot be resolved from the supplied contracts. Do not implement code.

## Final answer

# B-17 design handoff: cancel a reservation and show the confirmed outcome

I based this only on `booking-context.md`. No repository code, API schema or `ROADMAP.md` was supplied, so I filed nothing and created no registry. This design stays in chat.

## Scope
- **Outcome:** a signed-in member can cancel one of their existing reservations from the browser. The UI shows "cancelled" only after the server confirms it.
- **Excluded:** B-18 waitlist promotion, B-19 emails, B-20 offline changes, and any change to `BookingService`.
- **Constraints:** the stack and deployment are fixed. No research is needed, and none was done.

## Ownership and contracts
| Concern | Authority | Consequence |
|---|---|---|
| Whether a reservation is cancelled | Server (`BookingService`, persistence) | The browser holds no authority. Its state is a view of the server's. |
| Who may cancel | Server, using the authenticated member | The client sends only the reservation ID and a request ID. It must not send a member ID, and the server ignores one if sent. |
| Duplicate suppression | Request ID | The client generates one per user intent and reuses it on retry. |

Assumption: the existing authenticated cancel API takes a reservation ID and a request ID. The supplied context doesn't give its endpoint path, response body or error codes, so I haven't invented any.

## Choices
1. **Confirmed outcome, not optimistic.** The control goes into a pending state and disables on click. The UI shows "Cancelled" only on a success response, then refreshes the reservation from the server. The cost is a short wait. The benefit is that the UI can't claim a cancellation the server rejected.
2. **One request ID per attempt.** It is generated when the user confirms and reused on retry after a network failure or timeout. It is regenerated only after a definitive result. This relies on the server deduplicating by request ID. That is unverified (see blockers).
3. **Confirmation step.** Cancellation is likely irreversible, so I'd add a confirm prompt before the request. This is a reversible UI default and is easy to drop.
4. **Failure outcomes.** Each failure leaves the reservation shown as still booked, with a message and a retry:
   - network error or timeout (outcome unknown, so refresh state before claiming either result)
   - not found
   - forbidden
   - already cancelled
   - session expired (re-authenticate)

## Increments
**Increment 1 (conditional on blocker 1): cancel control.**
- **Requirements:** the control appears only on the member's own active reservations. Pending, success and each failure state are traced from click to visible result. Success is shown only after server confirmation.
- **Write set:** the client reservation view, plus a thin client call to the existing cancel API. No server changes are expected. The paths are not known, so the implementer finds them.
- **Prerequisites:** blocker 1, and the location of the existing reservation UI and API client.
- **Checks (all unexecuted):**
  - Cancel success shows the confirmed state after refresh.
  - A double click sends one request and a retry reuses the same request ID.
  - Not-found, forbidden, already-cancelled and network-failure paths each show the right message and leave the state unchanged.
  - The request body contains no member ID.
  - A reservation owned by another member can't be cancelled. This is verified against the server rather than assumed.

## Blockers
1. **Cancel API response and error contract.** I don't have the success shape, the error codes, or the behavior when a request ID repeats or the reservation is already cancelled. Read the existing `BookingService` endpoint and tests before building. The result-handling logic in increment 1 is conditional until this is read. If the server doesn't deduplicate by request ID, the retry check changes.
2. **Side effects of cancellation** (seat release, waitlist) are out of scope here. The UI must not promise them.

**Status:** increment 1 is conditional on blocker 1. Nothing is ready to build, and nothing was implemented or run.

## Files changed


## Diff

```diff

```