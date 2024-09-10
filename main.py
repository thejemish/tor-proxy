import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from stem import Signal
from stem.control import Controller
import random
import httpx
import socket
from asyncio import Semaphore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HTTP proxy settings (Privoxy)
HTTP_PROXY = "http://127.0.0.1:8118"
TOR_CONTROL_PORT = 9051

# Connection pool settings
MAX_CONNECTIONS = 50
connection_semaphore = Semaphore(MAX_CONNECTIONS)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Ensuring Tor and Privoxy are running...")
    if not check_tor_running():
        logger.error("Tor is not running. Please check the Docker setup.")
        raise RuntimeError("Tor is not running")
    yield
    logger.info("Application shutting down...")

app = FastAPI(lifespan=lifespan)

def check_tor_running():
    try:
        with socket.create_connection(("127.0.0.1", TOR_CONTROL_PORT), timeout=5):
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False

async def rotate_tor_circuit():
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            with Controller.from_port(port=TOR_CONTROL_PORT) as controller:
                controller.authenticate()
                controller.signal(Signal.NEWNYM)
                await asyncio.sleep(random.uniform(2, 5))  # Random delay after switching
            logger.info("Tor circuit rotated successfully")
            return True
        except Exception as e:
            logger.warning(f"Error on attempt {attempt + 1}: {e}")
            if attempt == max_attempts - 1:
                logger.error("Failed to rotate Tor circuit after multiple attempts")
                return False
            await asyncio.sleep(1)  # Wait before retrying

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

@app.get("/proxy_info")
async def proxy_info():
    return {
        "http_proxy": HTTP_PROXY,
        "https_proxy": HTTP_PROXY,
        "message": "Use these proxy settings in your anti-detect browser"
    }

@app.get("/check_ip")
async def check_ip():
    async with connection_semaphore:
        try:
            async with httpx.AsyncClient(proxies={"http://": HTTP_PROXY, "https://": HTTP_PROXY}, 
                                         headers=get_headers(),
                                         timeout=30) as client:
                response = await client.get("https://api.ipify.org?format=json")
                return response.json()
        except Exception as e:
            logger.error(f"Error checking IP: {e}")
            raise HTTPException(status_code=500, detail="Failed to check IP")

@app.get("/rotate_ip")
async def rotate_ip():
    async with connection_semaphore:
        success = await rotate_tor_circuit()
        if success:
            # Check the new IP after rotation
            try:
                async with httpx.AsyncClient(proxies={"http://": HTTP_PROXY, "https://": HTTP_PROXY}, 
                                             headers=get_headers(),
                                             timeout=30) as client:
                    response = await client.get("https://api.ipify.org?format=json")
                    new_ip = response.json()["ip"]
                    return {"message": "IP rotated successfully", "new_ip": new_ip}
            except Exception as e:
                logger.error(f"Error checking new IP after rotation: {e}")
                return {"message": "IP rotated successfully, but failed to fetch new IP"}
        else:
            raise HTTPException(status_code=500, detail="Failed to rotate IP")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    async with connection_semaphore:
        start_time = asyncio.get_event_loop().time()
        response = await call_next(request)
        process_time = asyncio.get_event_loop().time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

# Note: We're not including the `if __name__ == "__main__":` block here
# because we're running the app using uvicorn in the entrypoint script