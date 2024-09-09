# Tor-based HTTP Proxy with User Agent Rotation

This project implements an HTTP proxy server that routes traffic through the Tor network and rotates user agents for each request. It's designed to enhance anonymity and reduce the likelihood of CAPTCHAs when browsing the web.

## Features

- HTTP proxy using Tor network
- User agent rotation using fake-useragent library
- FastAPI endpoints for programmatic access
- Docker containerization for easy deployment

## Prerequisites

- Docker
- Docker Compose (optional, for easier management)

## Setup

1. Clone this repository:

   ```
   git clone https://github.com/yourusername/tor-http-proxy.git
   cd tor-http-proxy
   ```

2. Build the Docker image:

   ```
   docker build -t tor-http-proxy .
   ```

3. Run the container:

   ```
   docker run -p 8000:8000 -p 8118:8118 tor-http-proxy
   ```

   Or, if you prefer using Docker Compose, create a `docker-compose.yml` file and run:

   ```
   docker-compose up
   ```

## Usage

### As an HTTP Proxy

Use `http://localhost:8118` as your proxy server address in your browser or application settings.

### API Endpoints

- Get proxy information:

  ```
  GET http://localhost:8000/proxy_info
  ```

- Request a new Tor identity:

  ```
  GET http://localhost:8000/new_identity
  ```

- Make a proxied request:
  ```
  GET http://localhost:8000/proxy_request?url=https://example.com
  ```

## File Structure

- `main.py`: The main FastAPI application
- `Dockerfile`: Instructions for building the Docker image
- `requirements.txt`: Python dependencies
- `torrc`: Tor configuration file
- `privoxy_config`: Privoxy configuration file

## Important Notes

- This proxy is intended for legitimate use cases. Always respect websites' terms of service and local laws.
- While this setup includes measures to enhance anonymity, it does not guarantee complete anonymity or prevention of all CAPTCHAs.
- Performance may be slower compared to direct connections due to routing through the Tor network.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)

## Disclaimer

This tool is for educational and research purposes only. Users are responsible for complying with applicable laws and regulations.
