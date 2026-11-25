import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from api.events import router as events_router
from api.stats import router as stats_router
from core.database import Base, engine
from core.consumer import consume_events

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    consumer_task = asyncio.create_task(consume_events())

    yield

    consumer_task.cancel()

    try:
        await consumer_task
    except asyncio.CancelledError:
        pass

    await engine.dispose()


app = FastAPI(
    title="Event Service",
    lifespan=lifespan,
)

app.include_router(events_router)
app.include_router(stats_router)

app.mount(
    "/static",
    StaticFiles(directory="statics"),
    name="static",
)

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
    )