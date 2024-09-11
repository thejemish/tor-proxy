# Base image: Use the lightweight Alpine Linux
FROM python:3.9-alpine

# Install Tor, Privoxy, and necessary dependencies
RUN apk update && apk add --no-cache \
    tor \
    privoxy \
    curl \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev \
    py3-pip \
    && rm -rf /var/cache/apk/*

# Install FastAPI and Uvicorn
RUN pip install --no-cache-dir fastapi uvicorn requests

# Configure Tor: Run SOCKS5 proxy on port 9050, and enable ControlPort for changing identity
RUN echo "SOCKSPort 0.0.0.0:9050" >> /etc/tor/torrc && \
    echo "ControlPort 9051" >> /etc/tor/torrc && \
    echo "CookieAuthentication 0" >> /etc/tor/torrc && \
    echo "Log notice file /var/log/tor/notices.log" >> /etc/tor/torrc

# Configure Privoxy: Forward all HTTP requests to the Tor SOCKS5 proxy
RUN echo "forward-socks5t / 127.0.0.1:9050 ." >> /etc/privoxy/config && \
    echo "listen-address 0.0.0.0:8118" >> /etc/privoxy/config

# Expose necessary ports for Privoxy (HTTP proxy), Tor (SOCKS5 proxy), and ControlPort
EXPOSE 8118 9050 9051

# Copy FastAPI app code
WORKDIR /app
COPY ./proxy_server.py /app

# Command to start both Tor and Privoxy, then run FastAPI app
CMD tor & privoxy --no-daemon /etc/privoxy/config & uvicorn proxy_server:app --host 0.0.0.0 --port 8000
