#!/bin/sh

DB_FILE="/app/db.sqlite3"

if [ ! -f "$DB_FILE" ]; then
    echo "Database not found. Initializing..."
    python setup_db.py
else
    echo "Database already exists. Starting server..."
fi

exec gunicorn --workers 2 --bind 0.0.0.0:8000 app:app
