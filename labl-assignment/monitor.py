import time
import httpx

PORTS = [8001, 8002, 8003]
INTERVAL_SECONDS = 2.0
TIMEOUT_SECONDS = 1.0
SLOW_THRESHOLD_MS = 500.0
FAILURE_THRESHOLD = 3

consecutive_failures = {port: 0 for port in PORTS}
reported_state = {port: "UNKNOWN" for port in PORTS}


def check_port(client: httpx.Client, port: int) -> str:
    url = f"http://127.0.0.1:{port}/health"
    start = time.perf_counter()
    try:
        response = client.get(url, timeout=TIMEOUT_SECONDS)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        if response.status_code >= 500:
            raise httpx.HTTPError(f"HTTP {response.status_code}")
        consecutive_failures[port] = 0
        state = "SLOW" if elapsed_ms > SLOW_THRESHOLD_MS else "UP"
        reported_state[port] = state
        return f"{port}:{state}({elapsed_ms:.0f}ms)"
    except httpx.HTTPError:
        consecutive_failures[port] += 1
        if consecutive_failures[port] >= FAILURE_THRESHOLD:
            reported_state[port] = "DOWN"
            return f"{port}:DOWN(fail={consecutive_failures[port]})"
        pending_label = "DOWN" if reported_state[port] == "DOWN" else reported_state[port]
        return f"{port}:{pending_label}?(fail={consecutive_failures[port]}/{FAILURE_THRESHOLD})"


def run_monitor(duration_seconds: float | None = None):
    deadline = time.time() + duration_seconds if duration_seconds else None
    with httpx.Client() as client:
        while True:
            round_start = time.time()
            parts = [check_port(client, port) for port in PORTS]
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] " + " | ".join(parts), flush=True)
            if deadline and time.time() >= deadline:
                break
            sleep_for = max(0.0, INTERVAL_SECONDS - (time.time() - round_start))
            time.sleep(sleep_for)


if __name__ == "__main__":
    run_monitor()
