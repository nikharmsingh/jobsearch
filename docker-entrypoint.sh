#!/bin/bash
set -e

# Initialize database if it doesn't exist
if [ ! -f "/app/instance/jobsearch.db" ]; then
    echo "Initializing database..."
    python init_db.py
    python create_tables.py
fi

# Run database migrations
echo "Running database migrations..."
flask db upgrade || echo "No migrations to run"

# Start the application
echo "Starting Flask application..."
exec "$@"
