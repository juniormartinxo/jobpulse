from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.concurrency import run_in_threadpool
import uvicorn

from app.routers.health import router as health_router
from app.settings import configure_logging, get_settings

settings = get_settings()
configure_logging(settings.log_level)

app: FastAPI = FastAPI(title=settings.app_name)
app.include_router(health_router)


@app.get("/metrics", response_class=Response)
async def metrics() -> Response:
    data = await run_in_threadpool(generate_latest)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


def run() -> None:
    uvicorn.run(app, host=settings.api_host, port=settings.api_port, log_config=None)


if __name__ == "__main__":
    run()
