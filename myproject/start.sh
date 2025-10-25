#!/bin/bash
echo "Starting Django app with Gunicorn..."
gunicorn myproject.wsgi --bind 0.0.0.0:$PORT
