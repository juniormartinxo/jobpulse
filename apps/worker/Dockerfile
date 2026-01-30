FROM mcr.microsoft.com/playwright/python:v1.41.2-jammy

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml /app/pyproject.toml

RUN python -m pip install --no-cache-dir tomli

RUN python - <<'PY'
import subprocess
import sys
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

with open("pyproject.toml", "rb") as file:
    data = tomllib.load(file)

deps = data["project"]["dependencies"]
subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
subprocess.check_call([sys.executable, "-m", "pip", "install", *deps])
PY

RUN python -m playwright install chromium

COPY apps/worker /app/apps/worker

ENV PYTHONPATH=/app/apps/worker

EXPOSE 8002

CMD ["celery", "-A", "jobpulse_worker.celery_app", "worker", "--loglevel=INFO"]
