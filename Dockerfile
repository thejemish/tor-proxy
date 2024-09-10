FROM python:3.9-slim

# Install Tor, Privoxy and other necessary system dependencies
RUN apt-get update && apt-get install -y \
    tor \
    privoxy \
    && rm -rf /var/lib/apt/lists/*

# Set working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY . .

# Copy configuration files
COPY torrc /etc/tor/torrc
COPY privoxy_config /etc/privoxy/config

# Copy the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose the ports the app, Privoxy, and Tor control port run on
EXPOSE 8000 8118 9051

# Use the entrypoint script to start services
ENTRYPOINT ["/entrypoint.sh"]