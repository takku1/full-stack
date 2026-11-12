# STATUS

- **Current Phase**: v1 built and tested
- **Active Focus**: none
- **Architecture Summary**: `app.py` is a single-process stdlib HTTP server (`ThreadingHTTPServer`) with a `Store` class that owns all state in one SQLite file (`--db`). Handler does auth, validation and routing; every list query is scoped by `owner_id`. Tests in `tests/test_api.py` run the real server as a subprocess.
- **Key Decisions**:
  | Decision | Why | Revisit when |
  |---|---|---|
  | SQLite (`sqlite3`, stdlib) | Durable across restart, stdlib-only, transactional | Multiple server processes or heavy write load |
  | Opaque random bearer token (`secrets.token_urlsafe(32)`), only SHA-256 hash stored | Tokens are high-entropy, so a fast hash suffices; DB leak does not reveal tokens | Need token expiry, rotation or revocation |
  | Other user's list returns 404, same as missing | No existence leak | — |
  | Auth checked before body parsing/routing of `/lists*`; unknown paths 404 | Deny by default | — |
  | Bind 127.0.0.1 only; no TLS, no rate limit | Deployment excluded; put a TLS proxy in front if exposed | Exposure beyond localhost |
  | List JSON is `{"id","title"}`; title 1–500 chars, 400 otherwise | Spec fixed only the id; minimal shape | Items/tasks added |
- **Deprecated/Legacy**: none
- **Excluded (by request)**: sharing, editing, deletion, web UI, deployment
- **Known limits**: no token revocation/expiry; `POST /users` is open and unthrottled (anyone can create accounts).
- **Last Updated**: 2026-11-12
