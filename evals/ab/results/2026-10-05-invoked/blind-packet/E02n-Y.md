# E02n / Y

## Prompt

Design only roadmap B-17 from the supplied context. Keep the current stack and produce a concise implementation handoff. Research only if a decision cannot be resolved from the supplied contracts. Do not implement code.

## Final answer

# B-17 design: cancel an existing reservation

**Filing:** This design stays in chat. No source tree, design note, or `ROADMAP.md` is in the supplied context, so I wrote no files and made no registry update. **Research:** none was needed. **Checks:** none were run, and all checks below are unexecuted.

## 1. Scope
- **Outcome:** a member viewing their reservation can cancel it and sees a confirmed result.
- **Work ID:** B-17 only. B-18, B-19 and B-20 are excluded and unselected.
- **Exclusions:**
  - no new endpoint
  - no client-side seat release
  - no policy changes
  - no waitlist, email or offline behavior
  - no framework or storage changes
- **Disposition:** the whole increment is **ready**, subject to the path discovery in section 4. No costly-to-reverse commitment is involved.

## 2. Ownership and contracts

| State or decision | Authority | Browser's role |
|---|---|---|
| Cancellation, capacity, authorization | Server `BookingService` (existing authenticated API) | Sends reservation ID and request ID only. It never sends a member ID for authorization. |
| Reservation status | Server | The reservation-details cache is a copy. It is written only from a server response or a details query. |
| Pending, uncertain and error display | Reservation screen's local UI state | Not persisted. |

Response handling, trigger to observable result:

| Server outcome | Client behavior |
|---|---|
| Confirmed cancellation | Update the cached reservation, then show the "cancelled" status and a confirmation message. |
| Already cancelled | Same as confirmed, with copy such as "This reservation was already cancelled." Nothing was released twice. |
| Denial | Inline error. Do not change the cache. |
| Missing reservation | Inline error. Do not change the cache. Offer no retry. |
| Temporary failure, network error or timeout | Enter the **uncertain** state. Never assume rollback. Run the details query. If it shows cancelled, show the confirmed outcome. If it shows active, show an inline error with retry. If the query also fails, show "couldn't confirm, check again" with a re-query action. |

- **Request ID:** generate one per cancel intent and reuse it for every retry of that intent. This is safe because the server is idempotent. Generate a new one only after the reservation is known to be active again, or after a fresh user action following a definitive failure.
- **Double submit:** disable the button while a request or reconcile is in flight, using the existing button component's disabled or busy state if it has one.
- **Cancellation:** if the member leaves the screen mid-request, the server outcome stands. The next details load reconciles the display.
- **Confirmed outcome:** it appears only after a server response or a reconciling query. There is no optimistic "cancelled" display.
- **Control visibility:** show the control only for a reservation whose status is not cancelled. After cancellation, replace it with the cancelled status and message.

## 3. Choices
- **Reuse:** use the existing request client, details cache, inline-error component and accessible button. This is dictated by the constraints.
- **Confirmation step (reversible default):** the first activation puts the button in a "Confirm cancellation" state, using the same button component, with a cancel-the-cancel option. The second activation sends the request. If product wants no confirmation, delete the extra state. Revisit if the existing UI already has a standard confirm pattern.
- **Proposed copy:** this is not policy.
  - Button: "Cancel reservation"
  - Success: "Your reservation was cancelled."
  - Already cancelled: "This reservation was already cancelled."
  - Uncertain: "We couldn't confirm the cancellation. Checking…"
- **Accessibility:** move focus to the status message after the outcome, and announce results through the inline-error component or a polite live region, whichever the existing UI does.

## 4. Increments

**I-1 (ready): cancellation control and outcome handling on the reservation screen**
- **Requirements:** the behaviors in section 2.
- **Write set:** the reservation screen component, plus a small client call wrapper if the request client's conventions call for one.
  - The source paths are **not supplied**. The implementer must discover them and record them before starting.
  - Do not guess paths.
- **Prerequisites (assumptions with cost if false):**
  - The wire format and exact name of the "already cancelled" and "temporary failure" responses must be read from the existing API client or contract. If the client collapses them, I-1 must adapt.
  - The cached reservation status vocabulary must include a cancelled value. If it doesn't, the cache update would need a contract decision. Stop and flag it rather than invent one.
  - The request client must allow a caller-supplied request ID. If it doesn't, stop and flag it. Do not work around it with a new endpoint.
- **Checks (all unexecuted):**
  1. Confirmed response: cache is updated and the success message is shown.
  2. Already-cancelled response: the same cancelled state is shown with the already-cancelled copy.
  3. Denial and missing reservation: inline error, cache unchanged.
  4. Temporary failure: uncertain state, then the details query reconciles to cancelled or active.
  5. Network drop after the server commit: the reconciling query shows cancelled and the confirmed outcome is displayed, with no second capacity release.
  6. Retry reuses the same request ID.
  7. The button is disabled while a request is pending, so a double click sends one request.
  8. Keyboard-only operation and focus after the outcome.
  9. The control is absent for a cancelled reservation.
  10. No client code sends a member ID or changes capacity.
- **Status:** ready.

## 5. Blockers
None. The three prerequisites in I-1 are verification items for the implementer, not decisions waiting on the user. If any proves false, mark I-1 blocked and report it.

## 6. Handoff notes
- Build only on request. This is design only, and no code was written.
- Self-review only. No independent evaluation was done.
- Update the B-17 registry entry when the roadmap file is available. None was supplied.

## Files changed


## Diff

```diff

```