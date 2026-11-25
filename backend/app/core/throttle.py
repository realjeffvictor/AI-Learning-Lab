import math
import threading
import time
from collections import deque
from collections.abc import Callable


class LoginThrottle:
    """Sliding-window failure counter. In-process only, so it resets on restart and is per worker.
    Phase 8 replaces it with proper shared rate limiting."""

    def __init__(self, max_failures: int, window_seconds: int, clock: Callable[[], float] = time.monotonic) -> None:
        self._max = max_failures
        self._window = window_seconds
        self._clock = clock
        self._failures: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def _recent(self, key: str) -> deque[float]:
        failures = self._failures.get(key)
        if failures is None:
            return deque()
        cutoff = self._clock() - self._window
        while failures and failures[0] <= cutoff:
            failures.popleft()
        if not failures:
            del self._failures[key]
            return deque()
        return failures

    def retry_after(self, key: str) -> int:
        """Seconds the caller must wait, or 0 when attempts are allowed."""
        with self._lock:
            failures = self._recent(key)
            if len(failures) < self._max:
                return 0
            return max(1, math.ceil(failures[0] + self._window - self._clock()))

    def record_failure(self, key: str) -> None:
        with self._lock:
            self._recent(key)
            self._failures.setdefault(key, deque()).append(self._clock())

    def reset(self, key: str) -> None:
        with self._lock:
            self._failures.pop(key, None)
