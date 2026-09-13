#!/bin/sh
# Prepare the data volume, then hand off to server.py (gevent + sqlite-web).
set -e

DATA_DIR="${DATA_DIR:-/data}"
mkdir -p "$DATA_DIR"

# Refuse to run without a password — never serve the manager unauthenticated.
if [ -z "$SQLITE_WEB_PASSWORD" ]; then
    echo "ERROR: SQLITE_WEB_PASSWORD is not set." >&2
    echo "Set it to a strong secret (the Railway template generates one for you)." >&2
    exit 1
fi

create_db() {
    python -c "import sqlite3, sys; sqlite3.connect(sys.argv[1]).close()" "$1"
    echo "Created empty database $1"
}

# Pre-create any databases requested via SQLITE_DATABASES (comma-separated).
if [ -n "$SQLITE_DATABASES" ]; then
    echo "$SQLITE_DATABASES" | tr ',' '\n' | while IFS= read -r name; do
        name=$(printf '%s' "$name" | tr -d '[:space:]')
        [ -n "$name" ] || continue
        case "$name" in
            *.db|*.sqlite|*.sqlite3) ;;
            *) name="$name.db" ;;
        esac
        [ -f "$DATA_DIR/$name" ] || create_db "$DATA_DIR/$name"
    done
fi

# Always leave the UI with at least one database to open.
if ! ls "$DATA_DIR"/*.db "$DATA_DIR"/*.sqlite "$DATA_DIR"/*.sqlite3 >/dev/null 2>&1; then
    create_db "$DATA_DIR/sqlite.db"
fi

# Collect every database file on the volume as a UI dataset.
set --
for f in "$DATA_DIR"/*.db "$DATA_DIR"/*.sqlite "$DATA_DIR"/*.sqlite3; do
    [ -f "$f" ] && set -- "$@" "$f"
done

echo "Databases found: $#"
exec python server.py "$@"
