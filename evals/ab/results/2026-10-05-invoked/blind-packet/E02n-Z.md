# E02n / Z

## Prompt

Design only roadmap B-17 from the supplied context. Keep the current stack and produce a concise implementation handoff. Research only if a decision cannot be resolved from the supplied contracts. Do not implement code.

## Final answer

# B-17 design handoff: cancel a reservation and show the confirmed outcome

I read only `booking-context.md`. There is no application source in this workspace, so nothing here is checked against code. File paths, component names and API signatures are unknown, and I have not invented any.

## Outcome
- A member viewing a reservation can activate a **Cancel reservation** control.
- The screen then shows a result that matches what the server actually reported.
- **Excluded:**
  - a new endpoint
  - client-side seat release
  - waitlist (B-18), email (B-19) and offline (B-20) behavior
  - any change to cancellation policy

## Ownership and contracts
| State | Owner | Notes |
|---|---|---|
| Reservation status and seat capacity | Server, `BookingService` | The client never computes or changes them. |
| Authorization | Server | It uses the authenticated member. The client sends only the reservation ID and a request ID, never a member ID. |
| Cached reservation | Existing details cache | Written only from a server response or from a details re-query. |
| In-flight and result UI state | The reservation screen | It is local and disposable. |
| Request ID | The client | One ID is generated per user cancel intent and reused on every retry of that intent. |

## Decisions
1. **Request ID.** Generate it when the user confirms and keep it across retries. Reusing it relies on the server's stated idempotent repetition, which returns "already cancelled" without releasing capacity again.
2. **Confirmation step.** Add an inline confirm step before sending, because cancellation is hard to undo. Using the existing button component, the control becomes "Confirm cancel" and "Keep reservation". This is a UX choice I'm proposing and it needs product sign-off. No dialog is needed.
3. **Pending state.** While a request is pending, disable the control. This prevents duplicate submissions from the same screen.
4. **Outcome mapping.** Show an outcome only after a server response or a reconcile result:

| Response | Client behavior |
|---|---|
| Confirmed cancellation | Update the cache from the response. Show "Reservation cancelled." The status shows cancelled and the control is removed. |
| Already cancelled | Treat it as success. Update the cache. Show "This reservation was already cancelled." No error. |
| Denial | Show the inline error "You can't cancel this reservation." Leave the cache unchanged. |
| Missing reservation | Show the inline error "Reservation not found." Leave the cache unchanged. |
| Temporary server failure | Show the inline error "Couldn't cancel — try again." Keep the control enabled with the same request ID. |
| Network error or timeout (no response) | Outcome unknown. Do not show success or failure. Re-query the details, then follow the reconcile rules below. |

5. **Reconcile rules.** These apply after a network error or timeout:
   - If the details show cancelled, show the confirmed outcome.
   - If the details show active, show "Couldn't confirm — try again." Retry reuses the same request ID.
   - If the re-query also fails, show "Status unknown," offer a retry, and keep the cache untouched.
   - A timeout is never treated as a rollback.
6. **Restart or reload.** A reload during an unknown outcome loses the pending UI state. The details query then shows the true server status on load, so no client persistence is needed. Persisting the request ID across reloads is optional and I'd skip it. Without it, a repeat attempt after reload sends a new request ID. That is safe only if the server treats an already-cancelled reservation as "already cancelled" regardless of request ID. The context says repetition after success is safe but doesn't say that explicitly, so treat this as **conditional**.
7. **Accessibility.**
   - Use the keyboard-accessible button component.
   - Announce outcomes through the existing inline-error component, or an equivalent live region for success.
   - Keep focus on a stable element after the control disappears, for example the status text.

## Increments
Each increment ends with a check. The check commands depend on the repo's existing test setup, which I haven't seen.

1. **Locate the integration points.** Find the reservation screen, the request client, the details cache and the shared button and error components. **Check:** record the actual paths and signatures before any code change. If the client lacks a cancel call or a request-ID parameter, that is a blocker (see below).
2. **Add a cancel action.** Add a thin function that calls the existing cancellation API through the existing client, takes a reservation ID and request ID, and maps the response variants to a typed outcome. **Check:** unit tests, one per response variant plus network error.
3. **Add the cache update and reconcile.** Write the cache from confirmed and already-cancelled responses. On a network error, re-query the details. **Check:** tests that the cache changes only on those two outcomes. Also test the three reconcile branches: cancelled, active and re-query failure.
4. **Add the UI.** Add the control, the confirm step and the pending state, with copy per the outcome table. **Check:** component tests covering:
   - the control disappears after success
   - the denial, not-found and temporary-failure errors appear and the control stays enabled
   - double activation sends one request
   - the keyboard path works
5. **Exercise the real path.** Run against a dev or staging server and cancel a real reservation. Then repeat the request with the same ID. Then simulate a dropped response after commit. **Check:**
   - a single capacity release
   - the UI shows the confirmed outcome after reconcile
   - a reload shows the correct status

## Open blockers and conditional work
- **Conditional on source access.** Increments 2–5 depend on unverified facts: the real client API, how the cache is written, and the component props.
- **Conditional on server behavior.** Decision 6's "new request ID after reload is safe" is unverified. If it doesn't hold, persist the request ID per reservation, for example in session storage.
- **Product sign-off needed on copy.** This covers the confirm step and the strings above. It does not cover cancellation rules, such as cutoff windows. Those are outside this task, so if the server denies for such a rule, the UI shows only the generic denial message.
- **Noted, not built.** Optimistic UI, a cancel button on list views, and email or waitlist hooks.

Nothing was implemented, run or tested. This is design only.

## Files changed


## Diff

```diff

```