# Product decisions

## Product shape: sqlite-web manager (chosen)

Three viable shapes were considered for a SQLite service on Railway:

**(a) sqlite-web manager — CHOSEN.** A web UI over `.sqlite` files on a volume
(browse/insert/query/schema-edit). This is what the incumbent template
([railway.com/deploy/jOiNFt](https://railway.com/deploy/jOiNFt), 865 deploys, 71%
health) actually ships, and what its installed base expects: a "give me a small
database" service you can administer without a CLI.

**(b) Datasette.** A read-first exploration/publishing tool (write via plugins). A
different product — exploring data, not managing it — and would not serve the demand
that made the incumbent worth replacing.

**(c) libSQL server.** A networked SQLite fork. Rejected as a competitor because it
already has a healthy Railway template (27 deploys at 95% health); it is documented in
the listing as the alternative for the cross-service/networked case instead.

## Why the incumbent degrades

The incumbent's repo ([railwayapp-templates/sqlite](https://github.com/railwayapp-templates/sqlite))
builds on `python:3.7-alpine3.17` (Python 3.7 EOL June 2023, Alpine 3.17 EOL November
2023) with unpinned `pip install gevent sqlite_web`, a custom gevent wrapper, and a
hardcoded single database seeded with sample data. This template rebuilds the same
product on maintained, fully pinned dependencies (`python:3.12-slim-bookworm`,
`sqlite-web 0.8.1`, `gevent 26.8.0`), with the volume — not a hardcoded file — as the
source of truth, no sample data, an auto-generated password enforced at startup
(fail-closed), and a redirect-free `/health` endpoint so Railway's healthcheck doesn't
trip on the login redirect.

## Design notes

- **Serving:** gevent `WSGIServer` (Pool 50) via a small `server.py` that mirrors the
  upstream `sqlite_wsgi` entry-point, adding the public `/health` route. The stock
  sqlite-web auth handler redirects unauthenticated requests to `/login/`; Railway's
  healthcheck cannot follow redirects, so `/health` is exempted from the auth handler.
- **Multiple databases:** every database file on the volume is passed to sqlite-web as a
  dataset; new ones are created via the `SQLITE_DATABASES` variable or UI upload
  (`--enable-load`, uploads land on the volume). Filesystem mode (`-F`) is deliberately
  off — it rejects non-existent paths (can't create new DBs) and exposes on-disk paths
  beyond the volume.
- **Zero-prompt deploys:** `SQLITE_WEB_PASSWORD` uses Railway's `${{secret(24)}}`
  expression so one-click deploys prompt for nothing.
