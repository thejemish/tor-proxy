import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
import httpx
from stem import Signal
from stem.control import Controller
from http.cookiejar import CookieJar
from fake_useragent import UserAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HTTP proxy settings (Privoxy)
HTTP_PROXY = "http://127.0.0.1:8118"

# Initialize UserAgent
ua = UserAgent()

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

def get_random_user_agent():
    return ua.random

@app.get("/new_identity")
async def new_identity():
    await switch_tor_identity()
    return {"message": "New Tor identity requested"}

@app.get("/proxy_request")
async def proxy_request(url: str):
    if not url.startswith(('http://', 'https://')):
        url = f'https://{url}'
    
    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1"
    }
    
    cookie_jar = CookieJar()
    
    try:
        async with httpx.AsyncClient(proxies={"http://": HTTP_PROXY, "https://": HTTP_PROXY}, 
                                     headers=headers, 
                                     cookies=cookie_jar, 
                                     follow_redirects=True) as client:
            response = await client.get(url)
            return {
                "status_code": response.status_code,
                "content": response.text,
                "headers": dict(response.headers),
                "user_agent": headers["User-Agent"]
            }
    except httpx.RequestError as e:
        logger.error(f"Error making request through proxy: {e}")
        raise HTTPException(status_code=500, detail=f"Error making request: {str(e)}")

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