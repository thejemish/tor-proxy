#!/bin/bash
set -e

# Start Tor as the debian-tor user
su debian-tor -s /bin/sh -c "tor -f /etc/tor/torrc" &

# Wait for Tor to bootstrap
echo "Waiting for Tor to bootstrap..."
while true; do
    if grep -q "Bootstrapped 100" /var/log/tor/log; then
        echo "Tor has bootstrapped successfully"
        break
    fi
    sleep 5
done

# Start Privoxy
privoxy --no-daemon /etc/privoxy/config &

# Start the FastAPI application
exec python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4