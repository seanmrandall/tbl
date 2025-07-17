#!/bin/bash
set -e

# Use Railway's PORT environment variable, default to 5000
export PORT=${PORT:-5000}

echo "Starting Flask app on port $PORT"
echo "Current directory: $(pwd)"
echo "Files in current directory: $(ls -la)"
echo "Python version: $(python --version)"
echo "Flask app file exists: $(test -f app.py && echo 'YES' || echo 'NO')"

# Start the Flask application
python -m flask run --host=0.0.0.0 --port=$PORT 