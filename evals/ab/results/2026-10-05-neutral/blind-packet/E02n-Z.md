# E02n / Z

## Prompt

Design only roadmap B-17 from the supplied context. Keep the current stack and produce a concise implementation handoff. Research only if a decision cannot be resolved from the supplied contracts. Do not implement code.

## Final answer

# B-17 handoff: cancel a reservation and show the confirmed outcome

Design only. No source paths were supplied, so none are named here. Step 1 must find them.

## Outcome and exclusions
- **Outcome:** a member viewing a reservation can cancel it. The screen shows the confirmed result only after the server confirms it.
- **Excluded:** a new endpoint, client-side seat release, treating a timeout as rollback, waitlist (B-18), emails (B-19), offline changes (B-20), and any change to cancellation policy.

## Ownership and contracts
| State | Owner |
|---|---|
| Reservation status and seat capacity | Server (`BookingService`). The client never mutates capacity. |
| Authorization | Server, from the authenticated member. The client sends only the reservation ID and request ID, never a member ID. |
| Cached reservation | Existing details cache. It is a projection of server state. |
| Request ID | Client. It is generated once per cancel intent and reused on every retry of that intent. |
| In-flight and uncertain UI state | The reservation screen (local). |

The client calls the existing authenticated cancel API through the existing request client. The reservation ID and request ID are the inputs.

## Design choices
1. **No optimistic update.** The status changes in the cache only on a server response that confirms cancellation. The contract gives a definitive outcome per response, and an optimistic update would risk showing a cancellation that did not happen.
2. **Reuse the request ID on retry.** The server returns the already-cancelled outcome on repeats without releasing capacity again, so retrying is safe. This resolves the case where the server commits but the response is lost.
3. **An unknown outcome is not a failure.** On a network error or timeout, do not roll back and do not claim cancellation. Query reservation details to reconcile. If the status is cancelled, show the confirmed outcome. If it is still active, show a retryable error. If the query also fails, keep the "could not confirm" state with a retry that reuses the same request ID.
4. **Button behaviour.** Use the existing keyboard-accessible button, shown only for a cancellable status. Disable it while a request is in flight to prevent double-submit. I am assuming that a confirmation step is acceptable. It is a product decision and is listed under open items.

## Response mapping
| Response | UI behaviour |
|---|---|
| Confirmed cancellation | Update the cached reservation. Show status "Cancelled" and a confirmation message. Hide the control. |
| Already cancelled | Treat as success, with the same cache update. Optionally use wording such as "This reservation was already cancelled". |
| Denial | Inline error with no retry. Do not change the cache. |
| Missing reservation | Inline error. Refetch details so the screen matches the server. |
| Temporary server failure | Inline error with retry, reusing the request ID. The status is unchanged. |
| Network interruption or timeout | Reconcile as in choice 3. |

Use the existing inline-error component for all errors.

**Proposed copy (not final):**
- Success: "Your reservation is cancelled."
- Already cancelled: "This reservation was already cancelled."
- Could not confirm: "We couldn't confirm the cancellation. Check again."

## Increments, each with checks
1. **Locate and read.** Find the reservation screen, the request client, the cache, and the button and inline-error components. Confirm the cancel API's request and response shapes, the status values, and which statuses allow cancellation.
   - *Check:* the shapes match the contract above. Any mismatch goes back as a blocker.
2. **Cancel action.** Add a function that generates the request ID once per intent, calls the API, and maps each response to an outcome. Keep it separate from the UI.
   - *Check (unit):* each of the five responses maps correctly, the request ID is reused on retry, and no member ID is sent.
3. **Cache and reconcile.** Update the cache on confirmed or already-cancelled responses. On a network error, run the details query and branch on its result.
   - *Check (unit):* the cache is unchanged on denial and on server failure. After a lost response, reconcile shows a cancelled status.
4. **UI.** Add the button, the in-flight state, the success message, and the inline errors.
   - *Check:* the control works by keyboard, is disabled while in flight, and is hidden once cancelled. Run the real path against the real server if one is available, and exercise the existing test suite.
5. **Acceptance run.** Cancel an active reservation. Repeat the cancel with the same request ID. Try another member's reservation. Try a missing ID. Simulate a dropped response. Verify each result against the table above.

## Open items
- **Source paths and shapes (blocker for step 1).** Everything in increments 2–4 depends on facts not yet verified, so it is conditional.
- **Which statuses are cancellable.** Not stated. Assumed to be "active" only. Confirm this.
- **Confirmation dialog.** Product decision. Skipping it is a smaller change, but a cancel is not undoable from the client.
- **Final copy.** Needs product sign-off.

The context stipulates that a dropped response after a server commit is possible. No research was needed because the supplied contracts settle every decision.

## Files changed


## Diff

```diff

```