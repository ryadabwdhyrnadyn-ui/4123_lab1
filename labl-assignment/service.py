import socket
import time
from datetime import datetime, timezone
from fastapi import FastAPI

app = FastAPI(title="Lab 1 & Assignment 1 Service")
START_TIME = time.monotonic()


@app.get("/info")
def info(delay: float = 0.0):
    if delay > 0:
        time.sleep(delay)
    return {
        "host": socket.gethostname(),
        "server_time": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health")
def health(delay: float = 0.0):
    if delay > 0:
        time.sleep(delay)
    uptime_seconds = round(time.monotonic() - START_TIME, 2)
    return {
        "status": "ok",
        "uptime_seconds": uptime_seconds,
    }
