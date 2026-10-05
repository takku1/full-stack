# Synthetic booking-project context

This file is raw input for E02. The facts below are stipulated by the fixture. No live deployment or code execution is implied.

## Product and stack

The product lets signed-in members reserve and cancel a workshop seat. Existing stack and deployment are fixed for this task. The browser calls a server application; the server owns booking authority and persistence. No replacement framework or storage research is required.

## Roadmap

- B-17: Add a cancellation control for an existing reservation and show the confirmed outcome.
- B-18: Waitlist promotion. Not selected.
- B-19: Cancellation emails. Not selected.
- B-20: Offline booking changes. Not selected.

## Existing contracts

The server's BookingService already provides cancellation through the authenticated API. The caller supplies a reservation ID and request ID. The server verifies access against the authenticated member; client-supplied member IDs cannot authorize cancellation.

For an authorized reservation, the server commits cancellation atomically. Repetition after a successful cancellation returns the already-cancelled outcome without releasing capacity again. Responses distinguish confirmed cancellation, already cancelled, denial, missing reservation, and temporary server failure.

The browser has an existing authenticated request client and an existing reservation-details cache. A successful cancellation response can update that cached reservation; a subsequent details query is available to reconcile uncertain state. Network interruption can occur after the server commits but before the client receives the response.

The reservation screen already displays the reservation ID and status. There is no cancellation control yet. It has a standard inline-error component and a keyboard-accessible button component. The actual source paths are not supplied.

## Constraints

Use existing API semantics, client, cache, and UI controls. Do not implement another cancellation endpoint, release seats on the client, assume a network timeout means rollback, invent source paths, or add waitlist/email/offline behavior. Product copy can be proposed, but changing cancellation policy is outside this task.
