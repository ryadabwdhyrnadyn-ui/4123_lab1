import asyncio
import time
from fastapi import FastAPI, Query

app = FastAPI()
START_TIME = time.time()


@app.get("/info")
def info():
    return {"service": "health-demo", "status": "running"}


@app.get("/health")
async def health(delay: float = Query(default=0.0, ge=0.0)):
    if delay > 0:
        await asyncio.sleep(delay)
    return {
        "status": "ok",
        "uptime_seconds": round(time.time() - START_TIME, 2),
    }
