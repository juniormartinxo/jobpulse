from __future__ import annotations

import logging
import os

from celery import Celery
from celery.signals import worker_ready

from jobpulse_worker.observability.logging import configure_logging
from jobpulse_worker.observability.metrics import (
    jobs_scraped_total,
    scrape_errors_total,
    start_metrics_server,
)

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
METRICS_PORT = int(os.getenv("METRICS_PORT", "8002"))

celery_app = Celery(
    "jobpulse_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["jobpulse_worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_default_queue="jobpulse",
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_hijack_root_logger=False,
    broker_connection_retry_on_startup=True,
)

configure_logging(LOG_LEVEL)
logger = logging.getLogger("jobpulse_worker.celery")


@worker_ready.connect
def _on_worker_ready(sender, **kwargs) -> None:
    start_metrics_server(METRICS_PORT)
    jobs_scraped_total.labels(source="bootstrap").inc(0)
    scrape_errors_total.labels(source="bootstrap").inc(0)
    from jobpulse_worker.tasks import ping_task

    result = ping_task.delay()
    logger.info(
        "worker_ready",
        extra={
            "event": "worker_ready",
            "metrics_port": METRICS_PORT,
            "ping_task_id": result.id,
        },
    )
