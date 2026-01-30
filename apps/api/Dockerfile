FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml /app/pyproject.toml

RUN python - <<'PY'
import subprocess
import sys
import tomllib

with open("pyproject.toml", "rb") as file:
    data = tomllib.load(file)

deps = data["project"]["dependencies"]
subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
subprocess.check_call([sys.executable, "-m", "pip", "install", *deps])
PY

COPY apps/api /app/apps/api

ENV PYTHONPATH=/app/apps/api

EXPOSE 8000

CMD ["python", "-m", "app.main"]
