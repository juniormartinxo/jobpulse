from __future__ import annotations

from datetime import datetime, timezone
import logging
import time

from celery import shared_task

from jobpulse_worker.observability.metrics import jobs_scraped_total
from jobpulse_worker.utils.backoff import BackoffPolicy, backoff_delays
from jobpulse_worker.utils.rate_limit import RateLimiter

logger = logging.getLogger("jobpulse_worker.tasks")
_rate_limiter = RateLimiter(rate_per_second=1000.0)
_backoff_policy = BackoffPolicy(max_attempts=1)


@shared_task(name="jobpulse.ping_task")
def ping_task() -> dict[str, str]:
    wait_time = _rate_limiter.acquire()
    if wait_time > 0:
        time.sleep(wait_time)
    next(backoff_delays(_backoff_policy))
    now = datetime.now(timezone.utc).isoformat()
    jobs_scraped_total.labels(source="ping").inc()
    logger.info("ping_task_executed", extra={"event": "ping", "timestamp": now})
    return {"status": "ok", "timestamp": now}
