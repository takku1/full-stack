---
discipline: security
triggers: [internet or trust boundary, multiple users or tenants, personal data, money or irreversible actions, untrusted code or content, secrets or confidential files]
tier2_when: [money, health, safety, regulated data, many users]
---

# Security

## Policy

- Tier 1 when any trigger holds; tier 2 for high consequence.
- Default: deny by default. Authorize at the component that owns the data,
  never only in the client or gateway. Use an established identity provider
  or library before writing authentication.
- Never: secrets in the repository, logs, or client output; trusting input
  that crossed a boundary; marking a control met without an executed check.

## Framework

Shostack's four questions (what are we working on, what can go wrong, what
are we going to do, did we do a good job). STRIDE per trust boundary at
tier 2. OWASP ASVS chapters as the checklist for the boundary types present.
NIST SSDF and SLSA when dependencies or builds are in scope.

## How to

1. **Working on**: list assets, actors, and trust boundaries from the
   design, one line each.
2. **Can go wrong**: per boundary, check identity, object-level
   authorization, input handling, secrets, and abuse (rate, replay,
   enumeration). Tier 2: walk spoofing, tampering, repudiation, information
   disclosure, denial of service, and elevation of privilege per boundary.
3. **Will do**: one control per finding, owned by a named component; add
   each to the assurance table.
4. **Good job**: every control gets a check below; unmet ones are blockers.
   Tier 2 adds dependency audit and lockfile pinning.

## Checks

- Another user's object is refused (404 or 403, never data).
- Unauthenticated and expired-credential requests are rejected.
- Injected input is inert wherever it is parsed (query, shell, template, path).
- No secrets or credentials in the repo, logs, or client bundle (scan).
- Tier 2: rate limit or lockout on authentication; dependency audit clean
  or findings listed.
