from __future__ import annotations

import threading

from prometheus_client import Counter, start_http_server

jobs_scraped_total = Counter(
    "jobs_scraped_total",
    "Total de vagas processadas pelo worker",
    ["source"],
)

scrape_errors_total = Counter(
    "scrape_errors_total",
    "Total de erros de scraping observados",
    ["source"],
)

_metrics_started = False
_metrics_lock = threading.Lock()


def start_metrics_server(port: int) -> None:
    global _metrics_started
    with _metrics_lock:
        if _metrics_started:
            return
        start_http_server(port)
        _metrics_started = True
