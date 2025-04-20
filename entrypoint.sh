#!/bin/bash

set -e

if [ "$APP_MODE" = "uwsgi" ]; then
    echo "Running with uWSGI..."
    exec uwsgi --ini uwsgi.ini  # Use the ini file
else
    echo "Running with debugpy..."
    exec python -m debugpy --listen :5676  --wait-for-client -m app
fi
