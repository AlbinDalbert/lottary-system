#!/bin/sh

if [ "$(id -u)" = "0" ]; then
    echo "Running as root, fixing volume permissions..."
    chown -R app:app /data
    chmod -R 755 /data
    
    # Switch to app user and re-run this script
    echo "Switching to app user..."
    exec gosu app "$0" "$@"
fi

echo "Running as app user ($(id -u):$(id -g))"

DB_FILE="/data/db.sqlite3"

if [ ! -f "$DB_FILE" ]; then
    echo "Database not found. Initializing..."
    python setup_db.py
fi

echo "Starting application..."
exec gunicorn --workers 2 --bind 0.0.0.0:8000 app:app
