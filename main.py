import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from stem import Signal
from stem.control import Controller
import asyncio
from httpx import AsyncClient, Limits
from asyncio import Lock
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HTTP proxy settings (Privoxy)
HTTP_PROXY = "http://127.0.0.1:8118"

# Tor control port
TOR_CONTROL_PORT = 9051

# Global AsyncClient for Tor control
tor_client = None

# Rate limiting
RATE_LIMIT = 1  # requests per second
last_request_time = 0
request_lock = Lock()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global tor_client
    logger.info("Ensuring Tor and Privoxy are running...")
    limits = Limits(max_keepalive_connections=5, max_connections=10)
    tor_client = AsyncClient(limits=limits, timeout=30.0)
    yield
    await tor_client.aclose()
    logger.info("Application shutting down...")

app = FastAPI(lifespan=lifespan)

async def switch_tor_identity():
    global last_request_time
    async with request_lock:
        current_time = time.time()
        if current_time - last_request_time < 1 / RATE_LIMIT:
            await asyncio.sleep(1 / RATE_LIMIT - (current_time - last_request_time))
        last_request_time = time.time()

        try:
            async with tor_client.post(f"http://localhost:{TOR_CONTROL_PORT}") as response:
                if response.status_code == 200:
                    await asyncio.sleep(2)  # Wait for the new circuit to be established
                    logger.info("New Tor identity requested successfully")
                else:
                    raise Exception("Failed to switch Tor identity")
        except Exception as e:
            logger.error(f"Error switching Tor identity: {e}")
            raise HTTPException(status_code=500, detail="Failed to switch Tor identity")

@app.get("/new_identity")
async def new_identity():
    await switch_tor_identity()
    return {"message": "New Tor identity requested"}

@app.get("/proxy_info")
async def proxy_info():
    return {
        "http_proxy": HTTP_PROXY,
        "https_proxy": HTTP_PROXY,
        "message": "Use these proxy settings in your anti-detect browser"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)