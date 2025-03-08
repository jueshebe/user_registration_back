#!/bin/bash

set -e

if [ "$APP_MODE" = "uwsgi" ]; then
    echo "Running with uWSGI..."
    exec uwsgi --ini uwsgi.ini  # Use the ini file
else
    echo "Running with Python..."
    exec python -m app
fi
