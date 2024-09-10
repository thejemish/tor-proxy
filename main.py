import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from stem import Signal
from stem.control import Controller
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HTTP proxy settings (Privoxy)
HTTP_PROXY = "http://127.0.0.1:8118"

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Ensuring Tor and Privoxy are running...")
    yield
    logger.info("Application shutting down...")

app = FastAPI(lifespan=lifespan)

async def switch_tor_identity():
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
            await asyncio.sleep(2)
        logger.info("New Tor identity requested successfully")
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