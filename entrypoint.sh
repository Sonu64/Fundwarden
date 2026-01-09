#!/bin/sh

# If migrations folder doesn't exist, create it and generate initial schema
if [ ! -d "migrations" ]; then
    echo "No migrations folder found. Initializing..."
    flask db init
    flask db migrate -m "Auto-generated migration"
fi

echo "Applying database migrations..."
python -m flask db upgrade

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 run:app