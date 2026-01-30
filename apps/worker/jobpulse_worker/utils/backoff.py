from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class BackoffPolicy:
    base: float = 0.5
    factor: float = 2.0
    max_delay: float = 30.0
    max_attempts: int = 5


def backoff_delays(policy: BackoffPolicy) -> Iterator[float]:
    attempt = 0
    delay = policy.base
    while attempt < policy.max_attempts:
        yield min(delay, policy.max_delay)
        attempt += 1
        delay = delay * policy.factor
