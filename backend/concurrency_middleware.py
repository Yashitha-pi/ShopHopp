"""
concurrency_middleware.py
----------------------------
Drop into ShopHopp's backend (e.g. backend/concurrency_middleware.py) and
wire up in app.py per the instructions below. Tracks two things the
dashboard needs that nothing else in the project currently measures:

  1. Concurrent requests right now (in-flight count) — the closest honest
     proxy for "concurrent users" without adding real session tracking.
  2. Requests/sec and error rate over a rolling 60-second window.

IMPORTANT CAVEAT — read before wiring this up:
Your Dockerfile runs gunicorn with multiple workers
(`--workers 4 --threads 2`). Each worker process gets its OWN copy of the
counters below — they are plain in-process Python objects, not shared
across processes. So GET /api/metrics/concurrency only reflects whichever
worker happens to handle that particular request, not the true total
across all 4 workers. For a local Minikube demo this is good enough to
show real, moving numbers instead of nothing — but if you need an
accurate cluster-wide count later, that requires a shared store (e.g. a
Redis counter, or reading it from resource_observations instead) rather
than in-memory state per worker.
"""

from __future__ import annotations

import threading
import time
from collections import deque

_lock = threading.Lock()
_in_flight = 0
_request_log: deque[tuple[float, bool]] = deque()  # (timestamp, was_error)
_WINDOW_SECONDS = 60


def _prune_old(now: float) -> None:
    while _request_log and now - _request_log[0][0] > _WINDOW_SECONDS:
        _request_log.popleft()


def register(app) -> None:
    """Call once from app.py: `concurrency_middleware.register(app)`"""

    @app.before_request
    def _start_request():  # noqa: ANN202
        global _in_flight
        with _lock:
            _in_flight += 1

    @app.after_request
    def _end_request(response):  # noqa: ANN001, ANN202
        global _in_flight
        now = time.time()
        with _lock:
            _in_flight = max(0, _in_flight - 1)
            _request_log.append((now, response.status_code >= 500))
            _prune_old(now)
        return response

    @app.route("/api/metrics/concurrency")
    def _concurrency_metrics():  # noqa: ANN202
        now = time.time()
        with _lock:
            _prune_old(now)
            total = len(_request_log)
            errors = sum(1 for _, is_err in _request_log if is_err)
            req_per_sec = round(total / _WINDOW_SECONDS, 2)
            error_pct = round((errors / total) * 100, 1) if total else 0.0
            in_flight = _in_flight
        return {
            "concurrent_requests": in_flight,
            "requests_per_sec": req_per_sec,
            "error_rate_pct": error_pct,
            "window_seconds": _WINDOW_SECONDS,
        }