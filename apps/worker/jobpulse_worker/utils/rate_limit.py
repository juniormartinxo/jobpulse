from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
import time


@dataclass
class RateLimiter:
    rate_per_second: float
    _lock: Lock = field(default_factory=Lock, init=False)
    _next_allowed: float = field(default_factory=lambda: 0.0, init=False)

    def acquire(self) -> float:
        with self._lock:
            now = time.monotonic()
            interval = 1.0 / self.rate_per_second
            if now < self._next_allowed:
                wait_time = self._next_allowed - now
                self._next_allowed = self._next_allowed + interval
                return wait_time
            self._next_allowed = now + interval
            return 0.0
