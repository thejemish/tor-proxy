from fastapi import FastAPI, HTTPException
import requests
import socket

app = FastAPI()

# Proxy configuration for routing through Tor
proxies = {
    'http': 'http://127.0.0.1:8118',
    'https': 'http://127.0.0.1:8118',
}

# Function to send the "NEWNYM" command to the Tor ControlPort
def new_tor_identity():
    try:
        # Connect to the Tor control port
        tor_control_port = ('127.0.0.1', 9051)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(tor_control_port)
            s.send(b'AUTHENTICATE\r\n')  # No authentication needed (CookieAuthentication 0)
            response = s.recv(1024).decode('utf-8')

            # If authentication was successful, send the NEWNYM signal
            if '250 OK' in response:
                s.send(b'SIGNAL NEWNYM\r\n')
                response = s.recv(1024).decode('utf-8')
                if '250 OK' in response:
                    return True
            return False
    except Exception as e:
        print(f"Error changing Tor identity: {e}")
        return False

@app.get("/proxy")
async def proxy_request(url: str):
    """
    Fetch data from the specified URL and forward the response.
    """
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required")

    try:
        # Send the request through the proxy (Tor)
        response = requests.get(url, proxies=proxies)
        return {
            'status': response.status_code,
            'content': response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/new_identity")
async def new_identity():
    """
    Request a new Tor identity (new IP address).
    """
    success = new_tor_identity()
    if success:
        return {"status": "success", "message": "New Tor identity requested."}
    else:
        raise HTTPException(status_code=500, detail="Failed to request new Tor identity.")
