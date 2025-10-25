#!/bin/bash
echo "Starting Django app on Railway..."
gunicorn myproject.wsgi --bind 0.0.0.0:$PORT
