import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

DEFAULT_TARGETS = [
    "http://127.0.0.1:8001",
    "http://127.0.0.1:8002",
    "http://127.0.0.1:8003",
]

SLOW_THRESHOLD_MS = 500.0


def classify_response(status_code: int | None, latency_ms: float, timed_out: bool, failed: bool) -> str:
    if timed_out or failed or status_code is None or status_code >= 500:
        return "DOWN"
    if latency_ms > SLOW_THRESHOLD_MS:
        return "SLOW"
    return "UP"


def check_target(base_url: str, timeout_sec: float = 2.0) -> tuple[str, float, str]:
    url = f"{base_url.rstrip('/')}/health"
    start = time.perf_counter()
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            latency_ms = (time.perf_counter() - start) * 1000.0
            status = classify_response(resp.status, latency_ms, timed_out=False, failed=False)
            return status, latency_ms, f"HTTP {resp.status}"
    except TimeoutError:
        latency_ms = (time.perf_counter() - start) * 1000.0
        return "DOWN", latency_ms, "timeout"
    except urllib.error.URLError as exc:
        latency_ms = (time.perf_counter() - start) * 1000.0
        timed_out = isinstance(exc.reason, TimeoutError)
        reason = "timeout" if timed_out else str(exc.reason)
        return "DOWN", latency_ms, reason
    except Exception as exc:
        latency_ms = (time.perf_counter() - start) * 1000.0
        return "DOWN", latency_ms, str(exc)


def main() -> None:
    targets = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_TARGETS
    interval_sec = 2.0
    print(f"Monitoring {len(targets)} target(s) every {interval_sec}s (SLOW > {SLOW_THRESHOLD_MS:.0f}ms). Press Ctrl+C to stop.")
    try:
        while True:
            ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            parts = []
            for t in targets:
                status, latency_ms, detail = check_target(t)
                parts.append(f"{t} -> {status} ({latency_ms:.1f} ms, {detail})")
            print(f"[{ts}] " + " | ".join(parts), flush=True)
            time.sleep(interval_sec)
    except KeyboardInterrupt:
        print("\nMonitor stopped.")


if __name__ == "__main__":
    main()
