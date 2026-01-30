from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache
import json
import logging
import sys
from typing import Mapping

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_STANDARD_LOG_KEYS = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
}


class Settings(BaseSettings):
    app_name: str = Field(default="jobpulse-api")
    environment: str = Field(default="local")
    log_level: str = Field(default="INFO")
    api_port: int = Field(default=8000)

    model_config = SettingsConfigDict(env_prefix="JOBPULSE_", case_sensitive=False)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        extra = _extract_extra(record)
        if extra:
            payload["extra"] = extra
        return json.dumps(payload, ensure_ascii=False, default=str)


def _extract_extra(record: logging.LogRecord) -> Mapping[str, object]:
    return {key: value for key, value in record.__dict__.items() if key not in _STANDARD_LOG_KEYS}


def configure_logging(log_level: str) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
