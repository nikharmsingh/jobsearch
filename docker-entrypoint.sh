#!/bin/bash
set -e

# Ensure instance directory exists and has proper permissions
echo "Setting up instance directory..."
mkdir -p /app/instance
chmod 777 /app/instance

# Initialize database if it doesn't exist
if [ ! -f "/app/instance/jobsearch.db" ]; then
    echo "Initializing database..."
    python init_db.py
    python create_tables.py
else
    echo "Database already exists, skipping initialization..."
fi

# Run database migrations
echo "Running database migrations..."
flask db upgrade || echo "No migrations to run"

# Start the application
echo "Starting Flask application..."
exec "$@"
