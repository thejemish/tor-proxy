#!/bin/bash
set -e

# Start Tor
service tor start

# Start Privoxy
service privoxy start

# Start the FastAPI application
exec uvicorn main:app --host 0.0.0.0 --port 8000