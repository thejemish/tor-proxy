#!/bin/bash
set -e

# Start Tor as the debian-tor user
su debian-tor -s /bin/sh -c "tor -f /etc/tor/torrc" &

# Wait for Tor to start up properly
sleep 5

# Start Privoxy
privoxy --no-daemon /etc/privoxy/config &

# Start the FastAPI application
python main.py