# BSWE 4123 - Lab 1 & Assignment 1: Multi-Instance Service Health Monitor

## Overview
REST service built with FastAPI (service.py) exposing /info and /health (with uptime_seconds and optional delay parameter), monitored by monitor.py across ports 8001, 8002, and 8003.

## Health Classification Rules
- UP: Response time <= 500 ms.
- SLOW: Response time > 500 ms.
- DOWN: Timeout, connection error, or HTTP 5xx error.

## How to Run
1. Activate virtual environment: .venv\Scripts\Activate.ps1
2. Start instances in separate terminals:
   - uvicorn service:app --port 8001
   - uvicorn service:app --port 8002
   - uvicorn service:app --port 8003
3. Run monitor: python monitor.py
