**SQLite on persistent storage with a web manager — for apps that don't need Postgres.**

This template deploys [SQLite](https://sqlite.org) on a Railway volume and gives you
[sqlite-web](https://github.com/coleifer/sqlite-web), a browser UI for managing it: browse
and edit tables, run queries, change schema, and import/export CSV/JSON. Log in with a
password that Railway generates for you at deploy time (visible in your Variables tab).

**Deploy and Host SQLite with a web manager**

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/sqlite3-railway-template)

## What you get

- **`sqlite3` service** — pinned image (`python:3.12-slim-bookworm`, sqlite-web 0.8.1,
  gevent 26.8.0) serving the manager UI, healthchecked on `/health`.
- **Volume at `/data`** — every `*.db`/`*.sqlite` file on the volume is opened as a
  dataset in the UI; your data survives restarts and redeploys. A default empty
  `sqlite.db` is created on first boot.
- **`SQLITE_WEB_PASSWORD`** — auto-generated (`${{secret(24)}}`), found in the service's
  Variables tab. The service will not start without it.

## Manager vs. libSQL — pick the right shape

This template is a **manager**: a UI over SQLite files on a volume. It's for humans
administering data — no wire protocol, no driver, no second service.

If your **application services need to connect to the database over the network**, SQLite
cannot do that (it's a file format, not a protocol), and Railway volumes cannot be mounted
by more than one service. Deploy the **libSQL Server** template instead — a networked
SQLite fork that speaks a client/server protocol and is built for exactly that case.

Rule of thumb: administering data in a browser → this template; an app backend connecting
over the network → libSQL.

## Working with databases

- **Create** databases by setting `SQLITE_DATABASES` (comma-separated names) and
  redeploying, or by uploading a `.sqlite` file on the UI's *Load database* page.
- **Back up** by exporting tables as CSV/JSON in the UI, downloading the `.db` file from
  the dataset page, and enabling Railway's volume backups for the whole `/data` directory.

## Cost estimate

A single 0.5 GB RAM instance plus a small volume runs around **$5/month** including
storage. SQLite files are small; scale the volume as your data grows.

## Troubleshooting

- **`database is locked` under concurrent writes** — SQLite allows one writer at a time;
  this is inherent to SQLite. Fine for single-instance apps and admin work; for heavy
  multi-writer load, move to libSQL or Postgres.
- **Can't connect from another service** — expected: volumes attach to one service and
  SQLite has no network protocol. Use the libSQL Server template for networked access.
- **Login password** — it's the `SQLITE_WEB_PASSWORD` variable on the service, not your
  Railway account password. Regenerate it by changing the variable and redeploying.
- **Deploy fails healthcheck** — the healthcheck is `GET /health` and needs no login; if it
  fails, check the deploy logs: the service refuses to start if `SQLITE_WEB_PASSWORD` is
  unset or empty.
- **Where did my data go?** — it lives on the volume at `/data`. Deleting the volume
  deletes your databases; take Railway volume backups or download the `.db` files first.

---

# Deploy and Host

## About Hosting

Deploying and hosting SQLite on Railway gives you a lightweight, zero-administration
database whose files live on a persistent Railway volume, administered through the
bundled sqlite-web manager UI. The template provisions one service built from this
repository's pinned Dockerfile (`python:3.12-slim-bookworm`, sqlite-web 0.8.1, gevent
26.8.0) and one volume mounted at `/data`. The manager UI is password-protected with a
secret Railway generates at deploy time (`SQLITE_WEB_PASSWORD`), the service healthchecks
on an unauthenticated `/health` endpoint, and it restarts on failure (10 retries). Set
`SQLITE_DATABASES` to a comma-separated list of names to have additional empty database
files created at boot; all existing `*.db`/`*.sqlite`/`*.sqlite3` files on the volume are
browsable in the UI's dataset selector.

## Why Deploy

SQLite is the most deployed database in the world — a single file, zero configuration,
no server process to run or pay for. On Railway, this template turns that file into a
managed resource: persistent across restarts, healthchecked, restart-on-failure, with a
web manager so you never need a shell session to look at your data. Compared with running
Postgres for a small project, you trade network access and concurrent writers for
simplicity and near-zero overhead — and the template says so plainly rather than hiding
the trade-off. Compared with the hand-rolled images most SQLite templates use, every
dependency here is version-pinned and the base image is maintained, so deploys keep
working.

## Common Use Cases

- **Small app data** for a single-instance API or bot: feature flags, tokens, queues,
  caches, user records that don't justify Postgres.
- **Administering datasets in the browser**: browse/edit rows, tweak schema, run ad-hoc
  SQL, and export CSV/JSON without installing anything.
- **Prototyping and demos**: spin up a data-backed project in one click, then graduate to
  Postgres or libSQL when you outgrow single-writer SQLite.
- **A scratch database for scripts and cron jobs** running elsewhere on Railway (scripts
  run inside this service, since the volume can't be shared across services).

## Dependencies for

### Deployment Dependencies

This template has no external service dependencies — it provisions only the `sqlite3`
service (Docker image built from this repo) and its volume. At deploy time Railway
generates `SQLITE_WEB_PASSWORD` (a 24-character secret) automatically; no user input is
required. The service binds to Railway's injected `PORT` and expects nothing beyond the
attached volume at `/data`. If you later need networked database access from other
services, deploy the libSQL Server template alongside your app instead — it is the
networked-protocol alternative to this file-based manager.
